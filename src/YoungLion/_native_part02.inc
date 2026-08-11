        if (!c) throw std::runtime_error("failed to encode string as UTF-8");
        return c;
    }
    const char* c = PyUnicode_AsUTF8(obj);
    if (!c) throw std::runtime_error("failed to encode string as UTF-8");
    return c;
}

PyObject* py_string(const std::string& s) {
    return PyUnicode_DecodeUTF8(s.data(), static_cast<Py_ssize_t>(s.size()), "strict");
}

bool starts_private(PyObject* key) {
    if (!PyUnicode_Check(key)) return false;
    const char* s = PyUnicode_AsUTF8(key);
    return s && s[0] == '_';
}

PyObject* deep_copy(PyObject* obj);
PyObject* to_plain(PyObject* obj);

PyObject* get_public_dict(PyObject* obj) {
    PyRef native_data(PyObject_GetAttrString(obj, "_native_data"));
    if (native_data && PyDict_Check(native_data.get())) {
        // Fast path for the very common flat DDM case. PyDict_Copy gives us a
        // new public dictionary while safely sharing immutable leaf objects.
        // If a nested/container value exists we fall back to recursive
        // conversion. Private keys keep the historical to_dict() behavior.
        bool flat_leaf_only = true;
        bool has_private = false;
        PyObject *k, *v; Py_ssize_t scan=0;
        while (PyDict_Next(native_data.get(), &scan, &k, &v)) {
            if (starts_private(k)) { has_private = true; flat_leaf_only = false; break; }
            if (!(v == Py_None || PyBool_Check(v) || PyLong_Check(v) || PyFloat_Check(v) || PyUnicode_Check(v) || PyBytes_Check(v))) {
                flat_leaf_only = false;
                break;
            }
        }
        if (flat_leaf_only && !has_private) return PyDict_Copy(native_data.get());

        PyObject* out = PyDict_New();
        if (!out) return nullptr;
        Py_ssize_t pos=0;
        while (PyDict_Next(native_data.get(), &pos, &k, &v)) {
            if (starts_private(k)) continue;
            PyRef cv(to_plain(v));
            if (!cv || PyDict_SetItem(out, k, cv.get()) < 0) { Py_DECREF(out); return nullptr; }
        }
        return out;
    }
    PyErr_Clear();
    PyRef dict(PyObject_GetAttrString(obj, "__dict__"));
    if (!dict || !PyDict_Check(dict.get())) {
        PyErr_Clear();
        if (PyDict_Check(obj)) { Py_INCREF(obj); return obj; }
        return PyDict_New();
    }
    PyObject* out = PyDict_New();
    if (!out) return nullptr;
    PyObject *k, *v; Py_ssize_t pos=0;
    while (PyDict_Next(dict.get(), &pos, &k, &v)) {
        if (starts_private(k)) continue;
        PyRef cv(to_plain(v));
        if (!cv || PyDict_SetItem(out, k, cv.get()) < 0) { Py_DECREF(out); return nullptr; }
    }
    return out;
}

PyObject* to_plain(PyObject* obj) {
    if (obj == Py_None || PyBool_Check(obj) || PyLong_Check(obj) || PyFloat_Check(obj) || PyUnicode_Check(obj) || PyBytes_Check(obj)) {
        Py_INCREF(obj); return obj;
    }
    if (PyDict_Check(obj)) {
        PyObject* out=PyDict_New(); if(!out) return nullptr;
