    os << '"';
    static const char hex[]="0123456789abcdef";
    for (unsigned char c: in) {
        switch(c){
            case '"': os<<"\\\""; break; case '\\': os<<"\\\\"; break; case '\b': os<<"\\b"; break;
            case '\f': os<<"\\f"; break; case '\n': os<<"\\n"; break; case '\r': os<<"\\r"; break; case '\t': os<<"\\t"; break;
            default: if(c<0x20){os<<"\\u00"<<hex[(c>>4)&15]<<hex[c&15];} else os<<static_cast<char>(c);
        }
    }
    os << '"';
}

bool json_dump_obj(PyObject* obj, std::ostringstream& os, int indent, int level) {
    if (obj == Py_None) { os<<"null"; return true; }
    if (obj == Py_True) { os<<"true"; return true; }
    if (obj == Py_False) { os<<"false"; return true; }
    if (PyLong_Check(obj) || PyFloat_Check(obj)) { PyRef r(PyObject_Repr(obj)); if(!r)return false; os<<py_utf8(r.get()); return true; }
    if (PyUnicode_Check(obj)) { json_escape(py_utf8(obj), os); return true; }
    if (PyBytes_Check(obj)) { char* b=nullptr; Py_ssize_t n=0; if(PyBytes_AsStringAndSize(obj,&b,&n)<0)return false; json_escape(std::string(b,n),os); return true; }
    PyRef plain;
    if (!(PyDict_Check(obj)||PyList_Check(obj)||PyTuple_Check(obj))) { plain=PyRef(to_plain(obj)); if(!plain) return false; if(plain.get()!=obj) return json_dump_obj(plain.get(),os,indent,level); }
    auto newline=[&](){ if(indent>=0) os<<'\n'<<std::string((level+1)*indent,' '); };
    auto endline=[&](){ if(indent>=0) os<<'\n'<<std::string(level*indent,' '); };
    if (PyDict_Check(obj)) {
        os<<'{'; PyObject *k,*v; Py_ssize_t pos=0; bool first=true;
        while(PyDict_Next(obj,&pos,&k,&v)){
            if(!first) os<<',';
            first=false;
            newline();
            json_escape(py_utf8(k),os);
            os<<((indent>=0)?": ":":");
            if(!json_dump_obj(v,os,indent,level+1)) return false;
        }
        if(!first) endline();
        os<<'}';
        return true;
    }
    if(PyList_Check(obj)||PyTuple_Check(obj)){
        os<<'['; Py_ssize_t n=PySequence_Size(obj); for(Py_ssize_t i=0;i<n;++i){ if(i)os<<','; newline(); PyRef it(PySequence_GetItem(obj,i)); if(!it||!json_dump_obj(it.get(),os,indent,level+1))return false;} if(n)endline(); os<<']'; return true;
    }
    PyRef r(PyObject_Str(obj)); if(!r)return false; json_escape(py_utf8(r.get()),os); return true;
}

struct JsonParser {
    const std::string& s; size_t i{0};
