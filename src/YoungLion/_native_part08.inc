PyModuleDef module={
    PyModuleDef_HEAD_INIT,
    "_native",
    "YoungLion native C++ core.",
    -1,
    methods,
    nullptr,
    nullptr,
    nullptr,
    nullptr
};

} // namespace

PyMODINIT_FUNC PyInit__native(void){return PyModule_Create(&module);}
