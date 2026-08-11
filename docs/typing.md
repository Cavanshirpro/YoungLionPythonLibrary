# Typing and `.pyi` support

YoungLion is a PEP 561 typed package (`py.typed`). Public APIs and `_native` are described by modular stubs.

```text
YoungLion/
├── __init__.pyi
├── _native.pyi
├── search.pyi
├── Colors.pyi
├── DataModel/{__init__,_core,_variants,_collections,_models,_cache}.pyi
└── function/{__init__,_base,_formats,_extra,_utilities}.pyi
```

The stubs model generics such as `DictDDM[str]`, DDM defaults/overloads, collection slices, aliases (`pluck`, `where`, `sub`, `mul`), dataclass fields, inherited `File` mixins and native functions.

An AST coverage check compares source/stub public classes, functions and methods so missing public signatures are caught during release preparation.
