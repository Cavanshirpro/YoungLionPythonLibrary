// Native batch primitives for large DDM collections.
// These functions deliberately keep Python object ownership at the boundary while
// moving traversal/filter/sort/numeric loops into C++.

PyObject* yl_path_get(PyObject* obj, const std::string& path, PyObject* def) {
    PyObject* cur = obj; Py_INCREF(cur);
    size_t start = 0;
    while (true) {
        size_t dot = path.find('.', start);
        std::string part = path.substr(start, dot == std::string::npos ? std::string::npos : dot - start);
        if (part.empty()) { Py_DECREF(cur); Py_INCREF(def); return def; }
        PyObject* nxt = nullptr;
        if (PyDict_Check(cur)) {
            nxt = PyDict_GetItemString(cur, part.c_str()); Py_XINCREF(nxt);
        } else if (PyList_Check(cur) || PyTuple_Check(cur)) {
            char* end = nullptr;
            long index = std::strtol(part.c_str(), &end, 10);
            if (end && *end == '\0') {
                nxt = PySequence_GetItem(cur, index);
                if (!nxt) PyErr_Clear();
            }
        } else {
            PyRef store(PyObject_GetAttrString(cur, "_native_data"));
            if (store && PyDict_Check(store.get())) {
                nxt = PyDict_GetItemString(store.get(), part.c_str()); Py_XINCREF(nxt);
            } else {
                PyErr_Clear();
                nxt = PyObject_GetAttrString(cur, part.c_str());
                if (!nxt) PyErr_Clear();
            }
        }
        Py_DECREF(cur);
        if (!nxt) { Py_INCREF(def); return def; }
        cur = nxt;
        if (dot == std::string::npos) break;
        start = dot + 1;
    }
    return cur;
}

int yl_path_set(PyObject* obj, const std::string& path, PyObject* value) {
    std::vector<std::string> parts;
    size_t start = 0;
    while (true) {
        size_t dot = path.find('.', start);
        std::string part = path.substr(start, dot == std::string::npos ? std::string::npos : dot - start);
        if (part.empty()) { PyErr_SetString(PyExc_ValueError, "path contains an empty segment"); return -1; }
        parts.push_back(part);
        if (dot == std::string::npos) break;
        start = dot + 1;
    }
    PyObject* cur = obj; Py_INCREF(cur);
    for (size_t i = 0; i + 1 < parts.size(); ++i) {
        PyObject* nxt = nullptr;
        if (PyDict_Check(cur)) {
            nxt = PyDict_GetItemString(cur, parts[i].c_str()); Py_XINCREF(nxt);
            if (!nxt) {
                nxt = PyDict_New();
                if (!nxt || PyDict_SetItemString(cur, parts[i].c_str(), nxt) < 0) { Py_XDECREF(nxt); Py_DECREF(cur); return -1; }
            }
        } else {
            PyRef store(PyObject_GetAttrString(cur, "_native_data"));
            if (store && PyDict_Check(store.get())) {
                nxt = PyDict_GetItemString(store.get(), parts[i].c_str()); Py_XINCREF(nxt);
                if (!nxt) {
                    nxt = PyDict_New();
                    if (!nxt || PyDict_SetItemString(store.get(), parts[i].c_str(), nxt) < 0) { Py_XDECREF(nxt); Py_DECREF(cur); return -1; }
                }
            } else {
                PyErr_Clear();
                nxt = PyObject_GetAttrString(cur, parts[i].c_str());
                if (!nxt) {
                    PyErr_Clear();
                    nxt = PyDict_New();
                    if (!nxt || PyObject_SetAttrString(cur, parts[i].c_str(), nxt) < 0) { Py_XDECREF(nxt); Py_DECREF(cur); return -1; }
                }
            }
        }
        Py_DECREF(cur); cur = nxt;
    }
    int rc = 0;
    if (PyDict_Check(cur)) rc = PyDict_SetItemString(cur, parts.back().c_str(), value);
    else {
        PyRef store(PyObject_GetAttrString(cur, "_native_data"));
        if (store && PyDict_Check(store.get())) rc = PyDict_SetItemString(store.get(), parts.back().c_str(), value);
        else { PyErr_Clear(); rc = PyObject_SetAttrString(cur, parts.back().c_str(), value); }
    }
    Py_DECREF(cur);
    return rc;
}

PyObject* n_batch_get_path(PyObject*, PyObject* args) {
    PyObject* iterable; const char* path; PyObject* def = Py_None;
    if (!PyArg_ParseTuple(args, "Os|O", &iterable, &path, &def)) return nullptr;
    PyRef seq(PySequence_Fast(iterable, "items must be iterable")); if (!seq) return nullptr;
    Py_ssize_t n = PySequence_Fast_GET_SIZE(seq.get());
    PyObject* out = PyList_New(n); if (!out) return nullptr;
    PyObject** items = PySequence_Fast_ITEMS(seq.get());
    for (Py_ssize_t i = 0; i < n; ++i) {
        PyObject* value = yl_path_get(items[i], path, def);
        if (!value) { Py_DECREF(out); return nullptr; }
        PyList_SET_ITEM(out, i, value);
    }
    return out;
}

PyObject* n_batch_set_path(PyObject*, PyObject* args) {
    PyObject* iterable; const char* path; PyObject* value;
    if (!PyArg_ParseTuple(args, "OsO", &iterable, &path, &value)) return nullptr;
    PyRef seq(PySequence_Fast(iterable, "items must be iterable")); if (!seq) return nullptr;
    Py_ssize_t n = PySequence_Fast_GET_SIZE(seq.get()); PyObject** items = PySequence_Fast_ITEMS(seq.get());
    for (Py_ssize_t i = 0; i < n; ++i) if (yl_path_set(items[i], path, value) < 0) return nullptr;
    return PyLong_FromSsize_t(n);
}

PyObject* n_batch_apply_path(PyObject*, PyObject* args, PyObject* kwargs) {
    PyObject* iterable; const char* path; PyObject* func; int write_back = 1;
    static const char* kw[] = {"items", "path", "func", "write_back", nullptr};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OsO|p", (char**)kw, &iterable, &path, &func, &write_back)) return nullptr;
    if (!PyCallable_Check(func)) { PyErr_SetString(PyExc_TypeError, "func must be callable"); return nullptr; }
    PyRef seq(PySequence_Fast(iterable, "items must be iterable")); if (!seq) return nullptr;
    Py_ssize_t n = PySequence_Fast_GET_SIZE(seq.get()); PyObject** items = PySequence_Fast_ITEMS(seq.get());
    PyObject* out = PyList_New(n); if (!out) return nullptr;
    for (Py_ssize_t i = 0; i < n; ++i) {
        PyRef value(yl_path_get(items[i], path, Py_None)); if (!value) { Py_DECREF(out); return nullptr; }
        PyObject* result = PyObject_CallOneArg(func, value.get());
        if (!result) { Py_DECREF(out); return nullptr; }
        if (write_back && yl_path_set(items[i], path, result) < 0) { Py_DECREF(result); Py_DECREF(out); return nullptr; }
        PyList_SET_ITEM(out, i, result);
    }
    return out;
}

bool yl_compare(PyObject* actual, const std::string& op, PyObject* expected, bool& ok) {
    ok = true;
    int rc = 0;
    if (op == "eq" || op == "==") rc = PyObject_RichCompareBool(actual, expected, Py_EQ);
    else if (op == "ne" || op == "!=") rc = PyObject_RichCompareBool(actual, expected, Py_NE);
    else if (op == "lt" || op == "<") rc = PyObject_RichCompareBool(actual, expected, Py_LT);
    else if (op == "le" || op == "<=") rc = PyObject_RichCompareBool(actual, expected, Py_LE);
    else if (op == "gt" || op == ">") rc = PyObject_RichCompareBool(actual, expected, Py_GT);
    else if (op == "ge" || op == ">=") rc = PyObject_RichCompareBool(actual, expected, Py_GE);
    else if (op == "contains") rc = PySequence_Contains(actual, expected);
    else if (op == "in") rc = PySequence_Contains(expected, actual);
    else if (op == "is_none") return actual == Py_None;
    else if (op == "not_none") return actual != Py_None;
    else if (op == "startswith" || op == "endswith") {
        const char* method = op == "startswith" ? "startswith" : "endswith";
        PyRef fn(PyObject_GetAttrString(actual, method));
        if (!fn || !PyCallable_Check(fn.get())) { PyErr_Clear(); return false; }
        PyRef result(PyObject_CallOneArg(fn.get(), expected)); if (!result) { ok = false; return false; }
        rc = PyObject_IsTrue(result.get());
    } else { PyErr_SetString(PyExc_ValueError, "unsupported comparison operator"); ok = false; return false; }
    if (rc < 0) { ok = false; return false; }
    return rc != 0;
}

PyObject* n_batch_filter_path(PyObject*, PyObject* args) {
    PyObject* iterable; const char* path; const char* op; PyObject* expected = Py_None;
    if (!PyArg_ParseTuple(args, "Oss|O", &iterable, &path, &op, &expected)) return nullptr;
    PyRef seq(PySequence_Fast(iterable, "items must be iterable")); if (!seq) return nullptr;
    PyObject* out = PyList_New(0); if (!out) return nullptr;
    Py_ssize_t n = PySequence_Fast_GET_SIZE(seq.get()); PyObject** items = PySequence_Fast_ITEMS(seq.get());
    PyRef missing(PyCapsule_New((void*)iterable, "yl.missing", nullptr)); if (!missing) { Py_DECREF(out); return nullptr; }
    for (Py_ssize_t i = 0; i < n; ++i) {
        PyRef value(yl_path_get(items[i], path, missing.get())); if (!value) { Py_DECREF(out); return nullptr; }
        if (value.get() == missing.get()) continue;
        bool ok = true; bool match = yl_compare(value.get(), op, expected, ok);
        if (!ok) { Py_DECREF(out); return nullptr; }
        if (match && PyList_Append(out, items[i]) < 0) { Py_DECREF(out); return nullptr; }
    }
    return out;
}


PyObject* n_batch_count_path(PyObject*, PyObject* args) {
    PyObject* iterable; const char* path; const char* op; PyObject* expected = Py_None;
    if (!PyArg_ParseTuple(args, "Oss|O", &iterable, &path, &op, &expected)) return nullptr;
    PyRef seq(PySequence_Fast(iterable, "items must be iterable")); if (!seq) return nullptr;
    Py_ssize_t n = PySequence_Fast_GET_SIZE(seq.get()); PyObject** items = PySequence_Fast_ITEMS(seq.get());
    PyRef missing(PyCapsule_New((void*)iterable, "yl.count.missing", nullptr)); if (!missing) return nullptr;
    Py_ssize_t count = 0;
    for (Py_ssize_t i = 0; i < n; ++i) {
        PyRef value(yl_path_get(items[i], path, missing.get())); if (!value) return nullptr;
        if (value.get() == missing.get()) continue;
        bool ok = true; bool match = yl_compare(value.get(), op, expected, ok);
        if (!ok) return nullptr;
        if (match) ++count;
    }
    return PyLong_FromSsize_t(count);
}

PyObject* n_batch_partition_path(PyObject*, PyObject* args) {
    PyObject* iterable; const char* path; const char* op; PyObject* expected = Py_None;
    if (!PyArg_ParseTuple(args, "Oss|O", &iterable, &path, &op, &expected)) return nullptr;
    PyRef seq(PySequence_Fast(iterable, "items must be iterable")); if (!seq) return nullptr;
    PyObject* yes = PyList_New(0); if (!yes) return nullptr;
    PyObject* no = PyList_New(0); if (!no) { Py_DECREF(yes); return nullptr; }
    Py_ssize_t n = PySequence_Fast_GET_SIZE(seq.get()); PyObject** items = PySequence_Fast_ITEMS(seq.get());
    PyRef missing(PyCapsule_New((void*)iterable, "yl.partition.missing", nullptr));
    if (!missing) { Py_DECREF(yes); Py_DECREF(no); return nullptr; }
    for (Py_ssize_t i = 0; i < n; ++i) {
        PyRef value(yl_path_get(items[i], path, missing.get()));
        if (!value) { Py_DECREF(yes); Py_DECREF(no); return nullptr; }
        bool match = false;
        if (value.get() != missing.get()) {
            bool ok = true; match = yl_compare(value.get(), op, expected, ok);
            if (!ok) { Py_DECREF(yes); Py_DECREF(no); return nullptr; }
        }
        if (PyList_Append(match ? yes : no, items[i]) < 0) { Py_DECREF(yes); Py_DECREF(no); return nullptr; }
    }
    PyObject* result = PyTuple_New(2); if (!result) { Py_DECREF(yes); Py_DECREF(no); return nullptr; }
    PyTuple_SET_ITEM(result, 0, yes); PyTuple_SET_ITEM(result, 1, no); return result;
}

PyObject* n_batch_numeric_op(PyObject*, PyObject* args) {
    PyObject* iterable; const char* path; const char* op; double a; double b = 0.0;
    if (!PyArg_ParseTuple(args, "Ossd|d", &iterable, &path, &op, &a, &b)) return nullptr;
    PyRef seq(PySequence_Fast(iterable, "items must be iterable")); if (!seq) return nullptr;
    Py_ssize_t n = PySequence_Fast_GET_SIZE(seq.get()); PyObject** items = PySequence_Fast_ITEMS(seq.get());
    Py_ssize_t changed = 0;
    for (Py_ssize_t i = 0; i < n; ++i) {
        PyRef value(yl_path_get(items[i], path, Py_None)); if (!value) return nullptr;
        if (!(PyLong_Check(value.get()) || PyFloat_Check(value.get()))) continue;
        double x = PyFloat_AsDouble(value.get()); if (PyErr_Occurred()) return nullptr;
        double y;
        std::string operation(op);
        if (operation == "add") y = x + a;
        else if (operation == "sub") y = x - a;
        else if (operation == "mul") y = x * a;
        else if (operation == "div") { if (a == 0.0) { PyErr_SetString(PyExc_ZeroDivisionError, "division by zero"); return nullptr; } y = x / a; }
        else if (operation == "clamp") y = std::max(a, std::min(b, x));
        else { PyErr_SetString(PyExc_ValueError, "unsupported numeric operation"); return nullptr; }
        PyRef py(PyFloat_FromDouble(y)); if (!py || yl_path_set(items[i], path, py.get()) < 0) return nullptr;
        ++changed;
    }
    return PyLong_FromSsize_t(changed);
}

PyObject* n_batch_numeric_reduce(PyObject*, PyObject* args) {
    PyObject* iterable; const char* path; const char* op;
    if (!PyArg_ParseTuple(args, "Oss", &iterable, &path, &op)) return nullptr;
    PyRef seq(PySequence_Fast(iterable, "items must be iterable")); if (!seq) return nullptr;
    Py_ssize_t n = PySequence_Fast_GET_SIZE(seq.get()); PyObject** items = PySequence_Fast_ITEMS(seq.get());
    double sum = 0.0, lo = std::numeric_limits<double>::infinity(), hi = -std::numeric_limits<double>::infinity(); Py_ssize_t count = 0;
    for (Py_ssize_t i = 0; i < n; ++i) {
        PyRef value(yl_path_get(items[i], path, Py_None)); if (!value) return nullptr;
        if (!(PyLong_Check(value.get()) || PyFloat_Check(value.get()))) continue;
        double x = PyFloat_AsDouble(value.get()); if (PyErr_Occurred()) return nullptr;
        sum += x; lo = std::min(lo, x); hi = std::max(hi, x); ++count;
    }
    std::string operation(op);
    if (operation == "count") return PyLong_FromSsize_t(count);
    if (!count) Py_RETURN_NONE;
    if (operation == "sum") return PyFloat_FromDouble(sum);
    if (operation == "mean") return PyFloat_FromDouble(sum / count);
    if (operation == "min") return PyFloat_FromDouble(lo);
    if (operation == "max") return PyFloat_FromDouble(hi);
    PyErr_SetString(PyExc_ValueError, "unsupported reduce operation"); return nullptr;
}

PyObject* n_batch_sort_path(PyObject*, PyObject* args, PyObject* kwargs) {
    PyObject* iterable; const char* path; int reverse = 0; int missing_last = 1;
    static const char* kw[] = {"items", "path", "reverse", "missing_last", nullptr};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "Os|pp", (char**)kw, &iterable, &path, &reverse, &missing_last)) return nullptr;
    PyRef seq(PySequence_Fast(iterable, "items must be iterable")); if (!seq) return nullptr;
    Py_ssize_t n = PySequence_Fast_GET_SIZE(seq.get()); PyObject** items = PySequence_Fast_ITEMS(seq.get());
    struct Entry { PyObject* item; PyObject* value; bool missing; Py_ssize_t order; };
    std::vector<Entry> entries; entries.reserve((size_t)n);
    PyRef missing(PyCapsule_New((void*)iterable, "yl.sort.missing", nullptr)); if (!missing) return nullptr;
    for (Py_ssize_t i = 0; i < n; ++i) {
        PyObject* value = yl_path_get(items[i], path, missing.get()); if (!value) { for(auto&e:entries)Py_DECREF(e.value); return nullptr; }
        Py_INCREF(items[i]); entries.push_back({items[i], value, value == missing.get(), i});
    }
    bool failed = false;
    std::stable_sort(entries.begin(), entries.end(), [&](const Entry& lhs, const Entry& rhs) {
        if (lhs.missing || rhs.missing) {
            if (lhs.missing && rhs.missing) return lhs.order < rhs.order;
            return missing_last ? !lhs.missing : lhs.missing;
        }
        int rc = PyObject_RichCompareBool(lhs.value, rhs.value, reverse ? Py_GT : Py_LT);
        if (rc < 0) { PyErr_Clear(); failed = true; return lhs.order < rhs.order; }
        return rc != 0;
    });
    if (failed) {
        for (auto& e : entries) { Py_DECREF(e.item); Py_DECREF(e.value); }
        PyErr_SetString(PyExc_TypeError, "path values are not mutually orderable"); return nullptr;
    }
    PyObject* out = PyList_New(n); if (!out) { for (auto& e : entries) { Py_DECREF(e.item); Py_DECREF(e.value); } return nullptr; }
    for (Py_ssize_t i = 0; i < n; ++i) { PyList_SET_ITEM(out, i, entries[(size_t)i].item); Py_DECREF(entries[(size_t)i].value); }
    return out;
}

PyObject* n_batch_is_sorted_path(PyObject*, PyObject* args) {
    PyObject* iterable; const char* path; int reverse = 0;
    if (!PyArg_ParseTuple(args, "Os|p", &iterable, &path, &reverse)) return nullptr;
    PyRef seq(PySequence_Fast(iterable, "items must be iterable")); if (!seq) return nullptr;
    Py_ssize_t n = PySequence_Fast_GET_SIZE(seq.get()); PyObject** items = PySequence_Fast_ITEMS(seq.get());
    if (n < 2) Py_RETURN_TRUE;
    PyRef prev(yl_path_get(items[0], path, Py_None)); if (!prev) return nullptr;
    for (Py_ssize_t i = 1; i < n; ++i) {
        PyRef cur(yl_path_get(items[i], path, Py_None)); if (!cur) return nullptr;
        int rc = PyObject_RichCompareBool(prev.get(), cur.get(), reverse ? Py_LT : Py_GT);
        if (rc < 0) return nullptr;
        if (rc) Py_RETURN_FALSE;
        prev = std::move(cur);
    }
    Py_RETURN_TRUE;
}

PyObject* n_batch_lower_bound_path(PyObject*, PyObject* args) {
    PyObject* iterable; const char* path; PyObject* target; int reverse = 0;
    if (!PyArg_ParseTuple(args, "OsO|p", &iterable, &path, &target, &reverse)) return nullptr;
    PyRef seq(PySequence_Fast(iterable, "items must be iterable")); if (!seq) return nullptr;
    Py_ssize_t lo = 0, hi = PySequence_Fast_GET_SIZE(seq.get()); PyObject** items = PySequence_Fast_ITEMS(seq.get());
    while (lo < hi) {
        Py_ssize_t mid = lo + (hi - lo) / 2;
        PyRef value(yl_path_get(items[mid], path, Py_None)); if (!value) return nullptr;
        int before = PyObject_RichCompareBool(value.get(), target, reverse ? Py_GT : Py_LT);
        if (before < 0) return nullptr;
        if (before) lo = mid + 1; else hi = mid;
    }
    return PyLong_FromSsize_t(lo);
}


PyObject* n_batch_equal_range_path(PyObject*, PyObject* args) {
    PyObject* iterable; const char* path; PyObject* target; int reverse = 0;
    if (!PyArg_ParseTuple(args, "OsO|p", &iterable, &path, &target, &reverse)) return nullptr;
    PyRef seq(PySequence_Fast(iterable, "items must be iterable")); if (!seq) return nullptr;
    Py_ssize_t size = PySequence_Fast_GET_SIZE(seq.get()); PyObject** items = PySequence_Fast_ITEMS(seq.get());
    Py_ssize_t lo = 0, hi = size;
    while (lo < hi) {
        Py_ssize_t mid = lo + (hi - lo) / 2;
        PyRef value(yl_path_get(items[mid], path, Py_None)); if (!value) return nullptr;
        int before = PyObject_RichCompareBool(value.get(), target, reverse ? Py_GT : Py_LT);
        if (before < 0) return nullptr;
        if (before) lo = mid + 1; else hi = mid;
    }
    Py_ssize_t first = lo; hi = size;
    while (lo < hi) {
        Py_ssize_t mid = lo + (hi - lo) / 2;
        PyRef value(yl_path_get(items[mid], path, Py_None)); if (!value) return nullptr;
        int after = PyObject_RichCompareBool(target, value.get(), reverse ? Py_GT : Py_LT);
        if (after < 0) return nullptr;
        if (after) hi = mid; else lo = mid + 1;
    }
    return Py_BuildValue("(nn)", first, lo);
}

PyObject* n_batch_binary_search_path(PyObject*, PyObject* args) {
    PyObject* iterable; const char* path; PyObject* target; int reverse = 0;
    if (!PyArg_ParseTuple(args, "OsO|p", &iterable, &path, &target, &reverse)) return nullptr;
    PyRef seq(PySequence_Fast(iterable, "items must be iterable")); if (!seq) return nullptr;
    Py_ssize_t lo = 0, hi = PySequence_Fast_GET_SIZE(seq.get()); PyObject** items = PySequence_Fast_ITEMS(seq.get());
    while (lo < hi) {
        Py_ssize_t mid = lo + (hi - lo) / 2;
        PyRef value(yl_path_get(items[mid], path, Py_None)); if (!value) return nullptr;
        int before = PyObject_RichCompareBool(value.get(), target, reverse ? Py_GT : Py_LT);
        if (before < 0) return nullptr;
        if (before) lo = mid + 1; else hi = mid;
    }
    Py_ssize_t size = PySequence_Fast_GET_SIZE(seq.get());
    if (lo >= size) return PyLong_FromLong(-1);
    PyRef value(yl_path_get(items[lo], path, Py_None)); if (!value) return nullptr;
    int equal = PyObject_RichCompareBool(value.get(), target, Py_EQ); if (equal < 0) return nullptr;
    return PyLong_FromSsize_t(equal ? lo : -1);
}

PyObject* n_batch_nth_path(PyObject*, PyObject* args, PyObject* kwargs) {
    PyObject* iterable; const char* path; Py_ssize_t nth; int largest = 0;
    static const char* kw[] = {"items", "path", "n", "largest", nullptr};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "Osn|p", (char**)kw, &iterable, &path, &nth, &largest)) return nullptr;
    PyRef seq(PySequence_Fast(iterable, "items must be iterable")); if (!seq) return nullptr;
    Py_ssize_t size = PySequence_Fast_GET_SIZE(seq.get());
    if (nth < 0) nth += size;
    if (nth < 0 || nth >= size) { PyErr_SetString(PyExc_IndexError, "n is out of range"); return nullptr; }
    PyObject** items = PySequence_Fast_ITEMS(seq.get());
    struct Entry { PyObject* item; PyObject* value; };
    std::vector<Entry> entries; entries.reserve((size_t)size);
    for (Py_ssize_t i = 0; i < size; ++i) {
        PyObject* value = yl_path_get(items[i], path, Py_None); if (!value) { for(auto&e:entries){Py_DECREF(e.item);Py_DECREF(e.value);} return nullptr; }
        Py_INCREF(items[i]); entries.push_back({items[i], value});
    }
    bool failed = false;
    auto comp = [&](const Entry& a, const Entry& b) {
        int rc = PyObject_RichCompareBool(a.value, b.value, largest ? Py_GT : Py_LT);
        if (rc < 0) { PyErr_Clear(); failed = true; return false; }
        return rc != 0;
    };
    std::nth_element(entries.begin(), entries.begin() + nth, entries.end(), comp);
    if (failed) {
        for(auto&e:entries){Py_DECREF(e.item);Py_DECREF(e.value);} PyErr_SetString(PyExc_TypeError,"path values are not mutually orderable"); return nullptr;
    }
    PyObject* result = entries[(size_t)nth].item; Py_INCREF(result);
    for(auto&e:entries){Py_DECREF(e.item);Py_DECREF(e.value);} return result;
}

PyObject* n_batch_mutate(PyObject*, PyObject* args) {
    PyObject* iterable; PyObject* operations;
    if (!PyArg_ParseTuple(args, "OO", &iterable, &operations)) return nullptr;
    PyRef seq(PySequence_Fast(iterable, "items must be iterable")); if (!seq) return nullptr;
    PyRef opseq(PySequence_Fast(operations, "operations must be iterable")); if (!opseq) return nullptr;

    struct Mutation {
        std::string op;
        std::string path;
        PyObject* value{nullptr};
        double a{0.0};
        double b{0.0};
    };
    std::vector<Mutation> plan;
    Py_ssize_t op_count = PySequence_Fast_GET_SIZE(opseq.get());
    PyObject** op_items = PySequence_Fast_ITEMS(opseq.get());
    plan.reserve((size_t)op_count);
    for (Py_ssize_t i = 0; i < op_count; ++i) {
        PyRef row(PySequence_Fast(op_items[i], "each mutation must be a tuple/list"));
        if (!row) return nullptr;
        Py_ssize_t fields = PySequence_Fast_GET_SIZE(row.get());
        if (fields < 3) { PyErr_SetString(PyExc_ValueError, "mutation requires at least (op, path, value)"); return nullptr; }
        PyObject** parts = PySequence_Fast_ITEMS(row.get());
        std::string op = py_utf8(parts[0]);
        std::string path = py_utf8(parts[1]);
        Mutation m; m.op = op; m.path = path;
        if (op == "set") {
            m.value = parts[2]; Py_INCREF(m.value);
        } else if (op == "add" || op == "sub" || op == "mul" || op == "div") {
            m.a = PyFloat_AsDouble(parts[2]);
            if (PyErr_Occurred()) { for (auto& x: plan) Py_XDECREF(x.value); return nullptr; }
            if (op == "div" && m.a == 0.0) { for (auto& x: plan) Py_XDECREF(x.value); PyErr_SetString(PyExc_ZeroDivisionError, "division by zero in batch plan"); return nullptr; }
        } else if (op == "clamp") {
            if (fields < 4) { for (auto& x: plan) Py_XDECREF(x.value); PyErr_SetString(PyExc_ValueError, "clamp requires minimum and maximum"); return nullptr; }
            m.a = PyFloat_AsDouble(parts[2]); if (PyErr_Occurred()) { for (auto& x: plan) Py_XDECREF(x.value); return nullptr; }
            m.b = PyFloat_AsDouble(parts[3]); if (PyErr_Occurred()) { for (auto& x: plan) Py_XDECREF(x.value); return nullptr; }
            if (m.a > m.b) { for (auto& x: plan) Py_XDECREF(x.value); PyErr_SetString(PyExc_ValueError, "clamp minimum cannot exceed maximum"); return nullptr; }
        } else {
            for (auto& x: plan) Py_XDECREF(x.value);
            PyErr_SetString(PyExc_ValueError, "unsupported batch mutation operation"); return nullptr;
        }
        plan.push_back(std::move(m));
    }

    Py_ssize_t changed = 0;
    Py_ssize_t n = PySequence_Fast_GET_SIZE(seq.get()); PyObject** items = PySequence_Fast_ITEMS(seq.get());
    for (Py_ssize_t i = 0; i < n; ++i) {
        for (const auto& m : plan) {
            if (m.op == "set") {
                if (yl_path_set(items[i], m.path, m.value) < 0) { for (auto& x: plan) Py_XDECREF(x.value); return nullptr; }
                ++changed; continue;
            }
            PyRef current(yl_path_get(items[i], m.path, Py_None));
            if (!current) { for (auto& x: plan) Py_XDECREF(x.value); return nullptr; }
            if (!(PyLong_Check(current.get()) || PyFloat_Check(current.get()))) continue;
            double x = PyFloat_AsDouble(current.get());
            if (PyErr_Occurred()) { for (auto& y: plan) Py_XDECREF(y.value); return nullptr; }
            double result = x;
            if (m.op == "add") result = x + m.a;
            else if (m.op == "sub") result = x - m.a;
            else if (m.op == "mul") result = x * m.a;
            else if (m.op == "div") result = x / m.a;
            else if (m.op == "clamp") result = std::max(m.a, std::min(m.b, x));
            PyRef value(PyFloat_FromDouble(result));
            if (!value || yl_path_set(items[i], m.path, value.get()) < 0) { for (auto& y: plan) Py_XDECREF(y.value); return nullptr; }
            ++changed;
        }
    }
    for (auto& x: plan) Py_XDECREF(x.value);
    return PyLong_FromSsize_t(changed);
}
