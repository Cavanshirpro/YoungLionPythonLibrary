    explicit JsonParser(const std::string& x):s(x){}
    void ws(){while(i<s.size()&&std::isspace((unsigned char)s[i]))++i;}
    [[noreturn]] void fail(const char* m){throw std::runtime_error(std::string("JSON parse error at ")+std::to_string(i)+": "+m);}
    PyObject* value(){ws(); if(i>=s.size())fail("unexpected end"); char c=s[i]; if(c=='{')return object(); if(c=='[')return array(); if(c=='"')return string(); if(c=='t'&&s.compare(i,4,"true")==0){i+=4;Py_RETURN_TRUE;} if(c=='f'&&s.compare(i,5,"false")==0){i+=5;Py_RETURN_FALSE;} if(c=='n'&&s.compare(i,4,"null")==0){i+=4;Py_RETURN_NONE;} return number();}
    static void append_utf8(std::string& out, unsigned cp){
        if(cp<=0x7f) out+=(char)cp;
        else if(cp<=0x7ff){out+=(char)(0xc0|(cp>>6));out+=(char)(0x80|(cp&63));}
        else if(cp<=0xffff){out+=(char)(0xe0|(cp>>12));out+=(char)(0x80|((cp>>6)&63));out+=(char)(0x80|(cp&63));}
        else if(cp<=0x10ffff){out+=(char)(0xf0|(cp>>18));out+=(char)(0x80|((cp>>12)&63));out+=(char)(0x80|((cp>>6)&63));out+=(char)(0x80|(cp&63));}
        else fail_static("unicode code point out of range");
    }
    [[noreturn]] static void fail_static(const char* m){throw std::runtime_error(std::string("JSON parse error: ")+m);}
    unsigned hex4(){
        if(i+4>s.size()) fail("short unicode escape");
        unsigned cp=0;
        for(int k=0;k<4;++k){char h=s[i++];cp<<=4;if(h>='0'&&h<='9')cp+=h-'0';else if(h>='a'&&h<='f')cp+=h-'a'+10;else if(h>='A'&&h<='F')cp+=h-'A'+10;else fail("bad unicode escape");}
        return cp;
    }
    PyObject* string(){
        if(s[i++]!='"') fail("expected quote");
        std::string out;
        while(i<s.size()){
            unsigned char c=(unsigned char)s[i++];
            if(c=='"') return py_string(out);
            if(c<0x20) fail("unescaped control character in string");
            if(c!='\\'){out+=(char)c;continue;}
            if(i>=s.size()) fail("bad escape");
            char e=s[i++];
            switch(e){
                case '"':out+='"';break; case '\\':out+='\\';break; case '/':out+='/';break;
                case 'b':out+='\b';break; case 'f':out+='\f';break; case 'n':out+='\n';break;
                case 'r':out+='\r';break; case 't':out+='\t';break;
                case 'u':{
                    unsigned cp=hex4();
                    if(cp>=0xd800 && cp<=0xdbff){
                        if(i+2>s.size() || s[i]!='\\' || s[i+1]!='u') fail("high surrogate without low surrogate");
                        i+=2; unsigned low=hex4();
                        if(low<0xdc00 || low>0xdfff) fail("invalid low surrogate");
                        cp=0x10000+((cp-0xd800)<<10)+(low-0xdc00);
                    }else if(cp>=0xdc00 && cp<=0xdfff) fail("isolated low surrogate");
                    append_utf8(out,cp); break;
                }
                default: fail("unknown escape");
            }
        }
        fail("unterminated string");
    }
    PyObject* number(){
        size_t st=i;
        if(s[i]=='-'){++i;if(i>=s.size())fail("incomplete number");}
        if(s[i]=='0'){
            ++i;
            if(i<s.size()&&std::isdigit((unsigned char)s[i])) fail("leading zero in number");
        }else if(s[i]>='1'&&s[i]<='9'){
            while(i<s.size()&&std::isdigit((unsigned char)s[i]))++i;
        }else fail("expected number");
        bool floating=false;
        if(i<s.size()&&s[i]=='.'){
            floating=true;++i;
            if(i>=s.size()||!std::isdigit((unsigned char)s[i])) fail("fraction requires digits");
            while(i<s.size()&&std::isdigit((unsigned char)s[i]))++i;
        }
        if(i<s.size()&&(s[i]=='e'||s[i]=='E')){
            floating=true;++i;
            if(i<s.size()&&(s[i]=='+'||s[i]=='-'))++i;
            if(i>=s.size()||!std::isdigit((unsigned char)s[i])) fail("exponent requires digits");
            while(i<s.size()&&std::isdigit((unsigned char)s[i]))++i;
        }
        std::string n=s.substr(st,i-st);
        if(floating) return PyFloat_FromDouble(std::stod(n));
        char* end=nullptr; PyObject* value=PyLong_FromString(n.data(),&end,10);
        if(!value || !end || *end!='\0'){Py_XDECREF(value);fail("invalid integer");}
        return value;
    }
    PyObject* array(){++i;PyObject* a=PyList_New(0);if(!a)return nullptr;ws();if(i<s.size()&&s[i]==']'){++i;return a;}while(true){PyObject* v=value();if(!v){Py_DECREF(a);return nullptr;}if(PyList_Append(a,v)<0){Py_DECREF(v);Py_DECREF(a);return nullptr;}Py_DECREF(v);ws();if(i>=s.size()){Py_DECREF(a);fail("unterminated array");}char c=s[i++];if(c==']')return a;if(c!=','){Py_DECREF(a);fail("expected comma");}}
    }
    PyObject* object(){++i;PyObject* d=PyDict_New();if(!d)return nullptr;ws();if(i<s.size()&&s[i]=='}'){++i;return d;}while(true){ws();if(i>=s.size()||s[i]!='"'){Py_DECREF(d);fail("expected object key");}PyRef k(string());ws();if(i>=s.size()||s[i++]!=':'){Py_DECREF(d);fail("expected colon");}PyRef v(value());if(!k||!v||PyDict_SetItem(d,k.get(),v.get())<0){Py_DECREF(d);return nullptr;}ws();if(i>=s.size()){Py_DECREF(d);fail("unterminated object");}char c=s[i++];if(c=='}')return d;if(c!=','){Py_DECREF(d);fail("expected comma");}}
    }
};

std::string read_file(const fs::path& p, bool binary=false){ std::ifstream f(p, binary?std::ios::binary:std::ios::in); if(!f) throw std::runtime_error("cannot open file: "+p.string()); std::ostringstream ss; ss<<f.rdbuf(); return ss.str(); }
void write_file(const fs::path& p,const std::string& s,bool append=false,bool binary=false){ if(p.has_parent_path()) fs::create_directories(p.parent_path()); std::ios::openmode m=std::ios::out; if(append)m|=std::ios::app; if(binary)m|=std::ios::binary; std::ofstream f(p,m); if(!f)throw std::runtime_error("cannot write file: "+p.string()); f.write(s.data(),(std::streamsize)s.size()); if(!f)throw std::runtime_error("write failed: "+p.string()); }

fs::path resolve_path(const std::string& folder,const std::string& path,bool parent=true){ fs::path p(path); if(!p.is_absolute()&&!folder.empty() && !(path.rfind("./",0)==0||path.rfind("../",0)==0)) p=fs::path(folder)/p; p=fs::absolute(p).lexically_normal(); if(parent && p.has_parent_path()) fs::create_directories(p.parent_path()); return p; }

std::vector<std::string> parse_csv_row(const std::string& line,char delim,char quote){std::vector<std::string> out;std::string cur;bool q=false;for(size_t i=0;i<line.size();++i){char c=line[i];if(c==quote){if(q&&i+1<line.size()&&line[i+1]==quote){cur+=quote;++i;}else q=!q;}else if(c==delim&&!q){out.push_back(cur);cur.clear();}else cur+=c;}out.push_back(cur);return out;}
bool csv_record_complete(const std::string& record, char quote){
    bool in_quote=false;
    for(size_t i=0;i<record.size();++i){
        if(record[i]!=quote) continue;
        if(in_quote && i+1<record.size() && record[i+1]==quote){ ++i; continue; }
        in_quote=!in_quote;
    }
    return !in_quote;
}
std::string csv_escape(const std::string& s,char delim,char quote){bool need=s.find(delim)!=std::string::npos||s.find(quote)!=std::string::npos||s.find('\n')!=std::string::npos||s.find('\r')!=std::string::npos;if(!need)return s;std::string o(1,quote);for(char c:s){if(c==quote)o+=quote;o+=c;}o+=quote;return o;}

std::string pdf_escape(const std::string& s){std::string o;for(char c:s){if(c=='('||c==')'||c=='\\')o+='\\'; if(c=='\r'||c=='\n')continue; o+=c;}return o;}
void write_simple_pdf(const fs::path& p,const std::string& text){
    std::vector<std::string> lines; std::stringstream ss(text); std::string line; while(std::getline(ss,line))lines.push_back(line); if(lines.empty())lines.push_back("");
    std::ostringstream content; content<<"BT\n/F1 12 Tf\n40 800 Td\n14 TL\n"; for(size_t i=0;i<lines.size();++i){ if(i)content<<"T*\n"; content<<"("<<pdf_escape(lines[i])<<") Tj\n";} content<<"ET\n"; std::string cs=content.str();
    std::vector<std::string> obj(6); obj[1]="<< /Type /Catalog /Pages 2 0 R >>"; obj[2]="<< /Type /Pages /Kids [3 0 R] /Count 1 >>"; obj[3]="<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"; obj[4]="<< /Length "+std::to_string(cs.size())+" >>\nstream\n"+cs+"endstream"; obj[5]="<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>";
    std::ostringstream out; out<<"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n"; std::vector<long> off(6); for(int i=1;i<=5;++i){off[i]=(long)out.tellp();out<<i<<" 0 obj\n"<<obj[i]<<"\nendobj\n";} long xref=(long)out.tellp();out<<"xref\n0 6\n0000000000 65535 f \n"; for(int i=1;i<=5;++i)out<<std::setw(10)<<std::setfill('0')<<off[i]<<" 00000 n \n"; out<<"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n"<<xref<<"\n%%EOF\n"; write_file(p,out.str(),false,true);
}
std::string read_simple_pdf(const fs::path& p){std::string b=read_file(p,true);std::string out;std::regex tj(R"(\((([^\\)]|\\.)*)\)\s*Tj)");auto begin=std::sregex_iterator(b.begin(),b.end(),tj),end=std::sregex_iterator();for(auto it=begin;it!=end;++it){std::string s=(*it)[1].str();std::string u;for(size_t i=0;i<s.size();++i){if(s[i]=='\\'&&i+1<s.size())u+=s[++i];else u+=s[i];}if(!out.empty())out+='\n';out+=u;}return out;}

PyObject* exception_from_cpp(const std::exception& e){PyErr_SetString(PyExc_RuntimeError,e.what());return nullptr;}

// JSON
PyObject* n_json_dumps(PyObject*,PyObject* args,PyObject* kwargs){PyObject* obj;int indent=2;static const char* kw[]={"obj","indent",nullptr};if(!PyArg_ParseTupleAndKeywords(args,kwargs,"O|i",(char**)kw,&obj,&indent))return nullptr;try{std::ostringstream os;if(!json_dump_obj(obj,os,indent,0))return nullptr;return py_string(os.str());}catch(const std::exception&e){return exception_from_cpp(e);}}
PyObject* n_json_loads(PyObject*,PyObject* arg){try{std::string s=py_utf8(arg);JsonParser p(s);PyObject* v=p.value();p.ws();if(p.i!=s.size()){Py_XDECREF(v);throw std::runtime_error("JSON parse error: trailing data");}return v;}catch(const std::exception&e){PyErr_SetString(PyExc_ValueError,e.what());return nullptr;}}

// DDM hot paths
PyObject* n_ddm_to_dict(PyObject*,PyObject* obj){return get_public_dict(obj);}
PyObject* n_ddm_clone_data(PyObject*,PyObject* obj){return get_public_dict(obj);}
PyObject* n_ddm_get_path(PyObject*,PyObject* args){
    PyObject* obj; const char* path; PyObject* def=Py_None;
    if(!PyArg_ParseTuple(args,"Os|O",&obj,&path,&def)) return nullptr;
    PyObject* cur=obj; Py_INCREF(cur);
    const char* seg=path;
    for(const char* p=path;;++p){
        if(*p!='.' && *p!='\0') continue;
        if(p==seg){Py_DECREF(cur);Py_INCREF(def);return def;}
        std::string part(seg,(size_t)(p-seg));
        PyObject* nxt=nullptr;
        if(PyDict_Check(cur)){
            nxt=PyDict_GetItemString(cur,part.c_str()); Py_XINCREF(nxt);
        }else if(PyList_Check(cur)||PyTuple_Check(cur)){
            char* e=nullptr; long idx=strtol(part.c_str(),&e,10);
            if(e && *e=='\0'){nxt=PySequence_GetItem(cur,idx);if(!nxt)PyErr_Clear();}
        }else{
            PyRef store(PyObject_GetAttrString(cur,"_native_data"));
            if(store && PyDict_Check(store.get())){nxt=PyDict_GetItemString(store.get(),part.c_str());Py_XINCREF(nxt);}
            else{PyErr_Clear();nxt=PyObject_GetAttrString(cur,part.c_str());if(!nxt)PyErr_Clear();}
        }
        Py_DECREF(cur);
        if(!nxt){Py_INCREF(def);return def;}
        cur=nxt;
        if(*p=='\0') break;
        seg=p+1;
    }
    return cur;
}
PyObject* n_ddm_has_path(PyObject* self,PyObject* args){PyObject* obj;const char* path;if(!PyArg_ParseTuple(args,"Os",&obj,&path))return nullptr;PyRef sentinel(PyCapsule_New((void*)self,nullptr,nullptr));if(!sentinel)return nullptr;PyRef tuple(Py_BuildValue("OsO",obj,path,sentinel.get()));PyRef r(n_ddm_get_path(nullptr,tuple.get()));if(!r)return nullptr;return PyBool_FromLong(r.get()!=sentinel.get());}
PyObject* n_ddm_set_path(PyObject*,PyObject* args){
    PyObject* obj; const char* path; PyObject* val;
    if(!PyArg_ParseTuple(args,"OsO",&obj,&path,&val)) return nullptr;
    std::vector<std::string> ps; const char* seg=path;
    for(const char* p=path;;++p){if(*p=='.'||*p=='\0'){if(p==seg)Py_RETURN_FALSE;ps.emplace_back(seg,(size_t)(p-seg));if(*p=='\0')break;seg=p+1;}}
    PyObject* cur=obj; Py_INCREF(cur);
    for(size_t i=0;i+1<ps.size();++i){
        PyObject* nxt=nullptr;
        if(PyDict_Check(cur)){
            nxt=PyDict_GetItemString(cur,ps[i].c_str()); if(nxt)Py_INCREF(nxt);
            else{nxt=PyDict_New();if(PyDict_SetItemString(cur,ps[i].c_str(),nxt)<0){Py_DECREF(nxt);Py_DECREF(cur);return nullptr;}}
        }else{
            PyRef store(PyObject_GetAttrString(cur,"_native_data"));
            if(store && PyDict_Check(store.get())){
                nxt=PyDict_GetItemString(store.get(),ps[i].c_str());if(nxt)Py_INCREF(nxt);
                else{nxt=PyDict_New();if(PyDict_SetItemString(store.get(),ps[i].c_str(),nxt)<0){Py_DECREF(nxt);Py_DECREF(cur);return nullptr;}}
            }else{
                PyErr_Clear();nxt=PyObject_GetAttrString(cur,ps[i].c_str());
                if(!nxt){PyErr_Clear();nxt=PyDict_New();if(PyObject_SetAttrString(cur,ps[i].c_str(),nxt)<0){Py_DECREF(nxt);Py_DECREF(cur);return nullptr;}}
            }
        }
        Py_DECREF(cur);cur=nxt;
    }
    int rc;
    if(PyDict_Check(cur)) rc=PyDict_SetItemString(cur,ps.back().c_str(),val);
    else{
        PyRef store(PyObject_GetAttrString(cur,"_native_data"));
        if(store && PyDict_Check(store.get())) rc=PyDict_SetItemString(store.get(),ps.back().c_str(),val);
        else{PyErr_Clear();rc=PyObject_SetAttrString(cur,ps.back().c_str(),val);}
    }
    Py_DECREF(cur);if(rc<0)return nullptr;Py_RETURN_TRUE;
}
void merge_dicts(PyObject* target, PyObject* source){
    PyObject *k,*v; Py_ssize_t pos=0;
    while(PyDict_Next(source,&pos,&k,&v)){
        PyObject* existing=PyDict_GetItem(target,k);
        if(existing && PyDict_Check(existing) && PyDict_Check(v)){
            merge_dicts(existing,v);
        }else{
            PyRef copy(deep_copy(v));
            if(!copy || PyDict_SetItem(target,k,copy.get())<0) throw std::runtime_error("merge failed");
        }
    }
}
PyObject* n_ddm_merge_data(PyObject*,PyObject* args){PyObject* a;PyObject* b;if(!PyArg_ParseTuple(args,"OO",&a,&b))return nullptr;PyRef db(to_plain(b));if(!db||!PyDict_Check(db.get())){PyErr_SetString(PyExc_TypeError,"merge expects mapping-like DDM/dict values");return nullptr;}PyRef out(PyDict_Check(a)?deep_copy(a):get_public_dict(a));if(!out||!PyDict_Check(out.get())){PyErr_SetString(PyExc_TypeError,"merge expects mapping-like DDM/dict values");return nullptr;}try{merge_dicts(out.get(),db.get());return out.release();}catch(const std::exception&e){return exception_from_cpp(e);}}
PyObject* n_ddm_diff(PyObject*,PyObject* args){PyObject*a,*b;if(!PyArg_ParseTuple(args,"OO",&a,&b))return nullptr;PyRef da(to_plain(a)),db(to_plain(b));if(!da||!db||!PyDict_Check(da.get())||!PyDict_Check(db.get())){PyErr_SetString(PyExc_TypeError,"diff expects mappings");return nullptr;}PyObject*out=PyDict_New();if(!out)return nullptr;PyRef keys(PySet_New(nullptr));if(!keys){Py_DECREF(out);return nullptr;}PyRef ka(PyDict_Keys(da.get())),kb(PyDict_Keys(db.get()));if(!ka||!kb){Py_DECREF(out);return nullptr;}for(Py_ssize_t i=0;i<PyList_GET_SIZE(ka.get());++i)PySet_Add(keys.get(),PyList_GET_ITEM(ka.get(),i));for(Py_ssize_t i=0;i<PyList_GET_SIZE(kb.get());++i)PySet_Add(keys.get(),PyList_GET_ITEM(kb.get(),i));PyRef it(PyObject_GetIter(keys.get()));PyObject*k;while((k=PyIter_Next(it.get()))){PyRef rk(k);PyObject*av=PyDict_GetItem(da.get(),k),*bv=PyDict_GetItem(db.get(),k);int eq=(av&&bv)?PyObject_RichCompareBool(av,bv,Py_EQ):0;if(eq<0){Py_DECREF(out);return nullptr;}if(!eq){PyObject* d=PyDict_New();if(!d){Py_DECREF(out);return nullptr;}PyDict_SetItemString(d,"old",av?av:Py_None);PyDict_SetItemString(d,"new",bv?bv:Py_None);PyDict_SetItem(out,k,d);Py_DECREF(d);}}return out;}
