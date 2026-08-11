        PyObject *k,*v; Py_ssize_t pos=0;
        while(PyDict_Next(obj,&pos,&k,&v)) {
            PyRef cv(to_plain(v)); if(!cv || PyDict_SetItem(out,k,cv.get())<0){Py_DECREF(out);return nullptr;}
        }
        return out;
    }
    if (PyList_Check(obj) || PyTuple_Check(obj)) {
        Py_ssize_t n=PySequence_Size(obj);
        PyObject* out=PyList_New(n); if(!out) return nullptr;
        for(Py_ssize_t i=0;i<n;++i){ PyObject* it=PySequence_GetItem(obj,i); if(!it){Py_DECREF(out);return nullptr;} PyRef r(it); PyObject* cv=to_plain(it); if(!cv){Py_DECREF(out);return nullptr;} PyList_SET_ITEM(out,i,cv); }
        return out;
    }
    if (PySet_Check(obj) || PyFrozenSet_Check(obj)) {
        PyRef seq(PySequence_List(obj)); if(!seq) return nullptr; return to_plain(seq.get());
    }
    PyRef m(PyObject_GetAttrString(obj,"to_dict"));
    if (m && PyCallable_Check(m.get())) {
        PyRef r(PyObject_CallNoArgs(m.get())); if(!r) return nullptr; return to_plain(r.get());
    }
    PyErr_Clear();
    Py_INCREF(obj); return obj;
}

PyObject* deep_copy(PyObject* obj) {
    if (obj == Py_None || PyBool_Check(obj) || PyLong_Check(obj) || PyFloat_Check(obj) || PyUnicode_Check(obj) || PyBytes_Check(obj)) { Py_INCREF(obj); return obj; }
    if (PyDict_Check(obj)) {
        PyObject* out=PyDict_New(); if(!out) return nullptr;
        PyObject *k,*v; Py_ssize_t pos=0;
        while(PyDict_Next(obj,&pos,&k,&v)) { PyRef ck(deep_copy(k)); PyRef cv(deep_copy(v)); if(!ck||!cv||PyDict_SetItem(out,ck.get(),cv.get())<0){Py_DECREF(out);return nullptr;} }
        return out;
    }
    if (PyList_Check(obj)) {
        Py_ssize_t n=PyList_GET_SIZE(obj); PyObject* out=PyList_New(n); if(!out) return nullptr;
        for(Py_ssize_t i=0;i<n;++i){ PyObject* cv=deep_copy(PyList_GET_ITEM(obj,i)); if(!cv){Py_DECREF(out);return nullptr;} PyList_SET_ITEM(out,i,cv);} return out;
    }
    if (PyTuple_Check(obj)) {
        Py_ssize_t n=PyTuple_GET_SIZE(obj); PyObject* out=PyTuple_New(n); if(!out) return nullptr;
        for(Py_ssize_t i=0;i<n;++i){ PyObject* cv=deep_copy(PyTuple_GET_ITEM(obj,i)); if(!cv){Py_DECREF(out);return nullptr;} PyTuple_SET_ITEM(out,i,cv);} return out;
    }
    PyRef plain(to_plain(obj));
    if (plain && plain.get()!=obj) return deep_copy(plain.get());
    PyErr_Clear(); Py_INCREF(obj); return obj;
}

void json_escape(const std::string& in, std::ostringstream& os) {
