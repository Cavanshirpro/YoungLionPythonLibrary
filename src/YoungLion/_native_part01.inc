#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cctype>
#include <filesystem>
#include <functional>
#include <ctime>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <limits>
#include <random>
#include <regex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <system_error>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <numeric>
#include <cstring>

namespace fs = std::filesystem;

namespace {

struct PyRef {
    PyObject* p{nullptr};
    PyRef() = default;
    explicit PyRef(PyObject* x): p(x) {}
    ~PyRef(){ Py_XDECREF(p); }
    PyRef(const PyRef&) = delete;
    PyRef& operator=(const PyRef&) = delete;
    PyRef(PyRef&& o) noexcept : p(o.p){ o.p=nullptr; }
    PyRef& operator=(PyRef&& o) noexcept { if(this!=&o){Py_XDECREF(p); p=o.p; o.p=nullptr;} return *this; }
    PyObject* get() const { return p; }
    PyObject* release(){ PyObject* x=p; p=nullptr; return x; }
    explicit operator bool() const { return p!=nullptr; }
};

std::string py_utf8(PyObject* obj) {
    if (!obj) return {};
    if (!PyUnicode_Check(obj)) {
        PyRef s(PyObject_Str(obj));
        if (!s) throw std::runtime_error("failed to convert object to string");
        const char* c = PyUnicode_AsUTF8(s.get());
