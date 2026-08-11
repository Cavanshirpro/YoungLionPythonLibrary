# Native extension reference

YoungLion's `_native` module is an implementation layer for performance-sensitive operations. Most applications should import higher-level names from `YoungLion`, `YoungLion.DataModel`, `YoungLion.function`, or `YoungLion.search` instead of calling `_native` directly.

## Why it exists

The extension reduces Python-level overhead in operations such as recursive DDM conversion, dotted-path traversal, JSON primitives, file operations, fuzzy metrics, repeated collection traversal, numeric reductions and C++ algorithm-backed selection/sorting helpers.

## ABI and builds

The extension uses the CPython C API and is therefore built per supported CPython/platform ABI. A source distribution contains the C++ source; wheels contain the compiled extension but intentionally omit the `.cpp`/`.inc` source implementation files.

## Source layout

- `_native.cpp` — module entry/compilation unit.
- `_native_part*.inc` — implementation sections.
- `_native_collection.inc` — collection/batch helpers.
- `_native_search.inc` — search primitives.
- `_native_file_extra.inc` — additional file primitives.
- `_native_ddm_extra.inc` — additional DDM primitives.
- `_native.pyi` — public typing surface for the extension.

## Stability

The native function names are typed because internal Python modules consume them, but the highest compatibility guarantee belongs to the normal public Python API. Prefer that API unless you deliberately accept lower-level coupling.

## GIL

Calling C++ does not automatically make an operation parallel. Functions manipulating Python objects must obey CPython reference-count/GIL rules. Python callbacks invoked during native collection traversal execute as Python callbacks and therefore remain subject to the GIL.

## Error handling

Native failures are translated into Python exceptions or documented sentinel/boolean results. C++ exceptions must not escape across the CPython ABI boundary unhandled.
