# Type stub reference

YoungLion ships PEP 561 metadata and `.pyi` files so IDEs and static type checkers can understand APIs implemented partly in C++ or dynamically in Python.

## Files

- `YoungLion/__init__.pyi` — top-level package metadata/re-exports.
- `YoungLion/_native.pyi` — C++ extension signatures.
- `YoungLion/search.pyi` — search stack.
- `YoungLion/Colors.pyi` — color helpers.
- `YoungLion/DataModel/*.pyi` — DDM core, variants, collections, models and cache/builder.
- `YoungLion/function/*.pyi` — File mixins and application utilities.
- `YoungLion/py.typed` — PEP 561 marker.

## Generics

Collection stubs use type parameters where a caller benefits from preserving item/key type information. Dynamic dotted paths necessarily return `Any` in cases where Python's static type system cannot infer a runtime path string.

## Overloads

Overloads are used for common distinctions such as defaults, slicing, and collection access. They are intended to improve editor inference without pretending dynamic runtime paths are statically knowable.

## Maintenance audit

Run:

```bash
python tools/check_stub_coverage.py
```

The audit parses every stub and structurally compares maintained Python source modules with paired stubs. It catches a missing public class, function or direct public method. It is intentionally dependency-free so CI can run it before installing mypy/Pyright.

A structural pass does not prove that every parameter annotation is semantically perfect. Review changed signatures manually and use a real type checker in applications that depend on strict typing.
