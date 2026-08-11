PyObject* n_ddm_memory_info(PyObject*, PyObject* args){
    PyObject* obj; int recursive=1;
    if(!PyArg_ParseTuple(args,"O|p",&obj,&recursive)) return nullptr;
    try{
        PyRef sys(PyImport_ImportModule("sys")); if(!sys) return nullptr;
        PyRef getsizeof(PyObject_GetAttrString(sys.get(),"getsizeof")); if(!getsizeof) return nullptr;
        auto size_of=[&](PyObject* x)->long long{
            PyRef r(PyObject_CallOneArg(getsizeof.get(),x));
            if(!r) throw std::runtime_error("sys.getsizeof failed");
            long long n=PyLong_AsLongLong(r.get()); if(PyErr_Occurred()) throw std::runtime_error("invalid object size");
            return n;
        };
        PyRef store(PyObject_GetAttrString(obj,"_native_data"));
        if(!store || !PyDict_Check(store.get())){PyErr_Clear();store=PyRef(get_public_dict(obj));if(!store)return nullptr;}
        long long object_bytes=size_of(obj), storage_bytes=size_of(store.get()), recursive_bytes=object_bytes;
        long long nodes=1, keys=PyDict_Size(store.get());
        if(recursive){
            std::unordered_set<PyObject*> seen; seen.insert(obj);
            std::function<void(PyObject*)> walk=[&](PyObject* x){
                if(!x || seen.count(x)) return;
                seen.insert(x);
                recursive_bytes += size_of(x);
                ++nodes;
                if(PyDict_Check(x)){PyObject*k,*v;Py_ssize_t pos=0;while(PyDict_Next(x,&pos,&k,&v)){walk(k);walk(v);}}
                else if(PyList_Check(x)||PyTuple_Check(x)){Py_ssize_t n=PySequence_Size(x);for(Py_ssize_t i=0;i<n;++i){PyObject* it=PySequence_Fast_GET_ITEM(x,i);walk(it);}}
                else if(PySet_Check(x)||PyFrozenSet_Check(x)){PyRef it(PyObject_GetIter(x));if(it){while(PyObject* item=PyIter_Next(it.get())){walk(item);Py_DECREF(item);}}else PyErr_Clear();}
            };
            walk(store.get());
        }else recursive_bytes=object_bytes+storage_bytes;
        PyObject*out=PyDict_New();
        PyDict_SetItemString(out,"object_bytes",PyRef(PyLong_FromLongLong(object_bytes)).get());
        PyDict_SetItemString(out,"storage_bytes",PyRef(PyLong_FromLongLong(storage_bytes)).get());
        PyDict_SetItemString(out,"recursive_bytes",PyRef(PyLong_FromLongLong(recursive_bytes)).get());
        PyDict_SetItemString(out,"nodes",PyRef(PyLong_FromLongLong(nodes)).get());
        PyDict_SetItemString(out,"keys",PyRef(PyLong_FromLongLong(keys)).get());
        return out;
    }catch(const std::exception&e){return exception_from_cpp(e);}
}
