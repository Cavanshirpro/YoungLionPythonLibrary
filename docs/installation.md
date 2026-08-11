# Installation

YoungLion targets CPython 3.10–3.14 and has no required third-party Python runtime dependencies.

## PyPI
```bash
python -m pip install YoungLion
```
A compatible wheel needs no local compiler. Source fallback requires a C++17 compiler and Python development headers.

## Development
```bash
git clone https://github.com/Cavanshirpro/YoungLionPythonLibrary.git
cd YoungLionPythonLibrary
python -m pip install -e .
python setup.py build_ext --inplace
python -m pytest
```

## Verify
```python
from YoungLion import DDM, SearchIndex
assert DDM({"x": 1}).x == 1
assert SearchIndex(["hello world"]).search("hello")
```

The sdist contains native `.cpp/.inc` files; wheels contain the compiled extension and type information but exclude native sources to reduce installed size.
