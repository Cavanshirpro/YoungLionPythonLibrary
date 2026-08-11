std::vector<Py_UCS4> unicode_chars(PyObject* obj){
    if(!PyUnicode_Check(obj)) throw std::runtime_error("expected str");
    if(PyUnicode_READY(obj)<0) throw std::runtime_error("invalid unicode string");
    Py_ssize_t n=PyUnicode_GET_LENGTH(obj); std::vector<Py_UCS4> out((size_t)n);
    int kind=PyUnicode_KIND(obj); void* data=PyUnicode_DATA(obj);
    for(Py_ssize_t i=0;i<n;++i) out[(size_t)i]=PyUnicode_READ(kind,data,i);
    return out;
}

size_t levenshtein_distance(const std::vector<Py_UCS4>&a,const std::vector<Py_UCS4>&b){
    if(a.size()>b.size()) return levenshtein_distance(b,a);
    std::vector<size_t> row(a.size()+1); std::iota(row.begin(),row.end(),0);
    for(size_t j=1;j<=b.size();++j){size_t prev=row[0];row[0]=j;for(size_t i=1;i<=a.size();++i){size_t old=row[i];size_t cost=a[i-1]==b[j-1]?0:1;row[i]=std::min({row[i]+1,row[i-1]+1,prev+cost});prev=old;}}
    return row.back();
}
size_t damerau_distance(const std::vector<Py_UCS4>&a,const std::vector<Py_UCS4>&b){
    const size_t n=a.size(),m=b.size(); std::vector<size_t> prev2(n+1),prev(n+1),cur(n+1); std::iota(prev.begin(),prev.end(),0); prev2=prev;
    for(size_t j=1;j<=m;++j){cur[0]=j;for(size_t i=1;i<=n;++i){size_t cost=a[i-1]==b[j-1]?0:1;cur[i]=std::min({prev[i]+1,cur[i-1]+1,prev[i-1]+cost});if(i>1&&j>1&&a[i-1]==b[j-2]&&a[i-2]==b[j-1])cur[i]=std::min(cur[i],prev2[i-2]+1);}prev2.swap(prev);prev.swap(cur);}return prev[n];
}
double jaro_score(const std::vector<Py_UCS4>&s1,const std::vector<Py_UCS4>&s2){
    if(s1==s2) return 1.0;
    if(s1.empty()||s2.empty()) return 0.0;
    size_t range=std::max(s1.size(),s2.size())/2;
    range=range?range-1:0;
    std::vector<char>m1(s1.size()),m2(s2.size());
    size_t matches=0;
    for(size_t i=0;i<s1.size();++i){size_t lo=i>range?i-range:0,hi=std::min(i+range+1,s2.size());for(size_t j=lo;j<hi;++j)if(!m2[j]&&s1[i]==s2[j]){m1[i]=1;m2[j]=1;++matches;break;}}
    if(!matches) return 0.0;
    size_t k=0,t=0;
    for(size_t i=0;i<s1.size();++i) if(m1[i]){while(!m2[k])++k;if(s1[i]!=s2[k])++t;++k;}
    double mt=matches;
    return (mt/s1.size()+mt/s2.size()+(mt-t/2.0)/mt)/3.0;
}
uint64_t trigram_key(Py_UCS4 a,Py_UCS4 b,Py_UCS4 c){return ((uint64_t)a<<42)^((uint64_t)b<<21)^(uint64_t)c;}
double trigram_score(const std::vector<Py_UCS4>&a,const std::vector<Py_UCS4>&b){
    if(a==b) return 1.0;
    if(a.size()<3||b.size()<3) return 0.0;
    std::unordered_set<uint64_t>x,y;
    for(size_t i=0;i+2<a.size();++i)x.insert(trigram_key(a[i],a[i+1],a[i+2]));
    for(size_t i=0;i+2<b.size();++i)y.insert(trigram_key(b[i],b[i+1],b[i+2]));
    size_t inter=0;
    for(auto k:x)if(y.count(k))++inter;
    return x.empty()&&y.empty()?1.0:(2.0*inter)/(x.size()+y.size());
}
PyObject* n_levenshtein(PyObject*,PyObject* args){PyObject*a,*b;if(!PyArg_ParseTuple(args,"OO",&a,&b))return nullptr;try{return PyLong_FromSize_t(levenshtein_distance(unicode_chars(a),unicode_chars(b)));}catch(const std::exception&e){return exception_from_cpp(e);}}
PyObject* n_damerau(PyObject*,PyObject* args){PyObject*a,*b;if(!PyArg_ParseTuple(args,"OO",&a,&b))return nullptr;try{return PyLong_FromSize_t(damerau_distance(unicode_chars(a),unicode_chars(b)));}catch(const std::exception&e){return exception_from_cpp(e);}}
PyObject* n_jaro_winkler(PyObject*,PyObject* args){PyObject*a,*b;double p=0.1;if(!PyArg_ParseTuple(args,"OO|d",&a,&b,&p))return nullptr;try{auto x=unicode_chars(a),y=unicode_chars(b);double j=jaro_score(x,y);size_t prefix=0;while(prefix<std::min<size_t>({4,x.size(),y.size()})&&x[prefix]==y[prefix])++prefix;return PyFloat_FromDouble(j+prefix*p*(1.0-j));}catch(const std::exception&e){return exception_from_cpp(e);}}
PyObject* n_trigram_similarity(PyObject*,PyObject* args){PyObject*a,*b;if(!PyArg_ParseTuple(args,"OO",&a,&b))return nullptr;try{return PyFloat_FromDouble(trigram_score(unicode_chars(a),unicode_chars(b)));}catch(const std::exception&e){return exception_from_cpp(e);}}
PyObject* n_find_all(PyObject*,PyObject* args){PyObject*h,*n;if(!PyArg_ParseTuple(args,"OO",&h,&n))return nullptr;try{auto text=unicode_chars(h),needle=unicode_chars(n);PyObject*out=PyList_New(0);if(needle.empty())return out;if(needle.size()>text.size())return out;std::unordered_map<Py_UCS4,size_t>skip;for(size_t i=0;i+1<needle.size();++i)skip[needle[i]]=needle.size()-1-i;size_t i=0;while(i+needle.size()<=text.size()){size_t j=needle.size();while(j&&needle[j-1]==text[i+j-1])--j;if(!j){PyRef pos(PyLong_FromSize_t(i));PyList_Append(out,pos.get());++i;}else{auto it=skip.find(text[i+needle.size()-1]);i+=it==skip.end()?needle.size():std::max<size_t>(1,it->second);}}return out;}catch(const std::exception&e){return exception_from_cpp(e);}}
PyObject* n_bm25_scores(PyObject*,PyObject* args){PyObject*q,*docs;double k1=1.5,b=0.75;if(!PyArg_ParseTuple(args,"OO|dd",&q,&docs,&k1,&b))return nullptr;try{PyRef qf(PySequence_Fast(q,"query_tokens must be a sequence")),df(PySequence_Fast(docs,"documents must be a sequence"));if(!qf||!df)return nullptr;Py_ssize_t N=PySequence_Fast_GET_SIZE(df.get());std::vector<std::string>qt;for(Py_ssize_t i=0;i<PySequence_Fast_GET_SIZE(qf.get());++i)qt.push_back(py_utf8(PySequence_Fast_GET_ITEM(qf.get(),i)));std::unordered_map<std::string,size_t>docfreq;std::vector<std::unordered_map<std::string,size_t>>freqs((size_t)N);std::vector<size_t>lens((size_t)N);double avg=0;for(Py_ssize_t d=0;d<N;++d){PyRef sf(PySequence_Fast(PySequence_Fast_GET_ITEM(df.get(),d),"document tokens must be sequences"));if(!sf)return nullptr;lens[(size_t)d]=(size_t)PySequence_Fast_GET_SIZE(sf.get());avg+=lens[(size_t)d];std::unordered_set<std::string>seen;for(Py_ssize_t i=0;i<PySequence_Fast_GET_SIZE(sf.get());++i){std::string t=py_utf8(PySequence_Fast_GET_ITEM(sf.get(),i));freqs[(size_t)d][t]++;seen.insert(t);}for(auto&t:seen)docfreq[t]++;}avg=N?avg/N:0;PyObject*out=PyList_New(N);for(Py_ssize_t d=0;d<N;++d){double score=0;for(auto&t:qt){auto tf=freqs[(size_t)d].find(t);if(tf==freqs[(size_t)d].end())continue;double n=(double)docfreq[t];double idf=std::log(1.0+(N-n+0.5)/(n+0.5));double f=(double)tf->second;double denom=f+k1*(1.0-b+b*(avg?lens[(size_t)d]/avg:0));score+=idf*(f*(k1+1.0))/denom;}PyList_SET_ITEM(out,d,PyFloat_FromDouble(score));}return out;}catch(const std::exception&e){return exception_from_cpp(e);}}
