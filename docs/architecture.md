# Architecture

YoungLion is hybrid: Python provides dynamic ergonomic APIs; C++17 implements selected hot paths through the CPython C API.

```text
YoungLion/
├── _native.*
├── DataModel/  # core, variants, collections, models, cache
├── function/   # File mixins + application utilities
├── search.py
├── Colors.py
└── *.pyi / py.typed
```

Native work includes path traversal, serialization, vector math, file primitives, fuzzy metrics, BM25 primitives, and batch loops. Arbitrary Python callbacks still execute Python code under the GIL; native orchestration cannot turn them into pure C++.

The runtime dependency policy is intentionally strict: use the C++ standard library or Python standard library when practical instead of silently installing large third-party packages.
