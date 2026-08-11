# Packaging

`pyproject.toml` is canonical metadata. Setuptools builds the C++ extension.

- `dependencies = []` keeps runtime dependency-free.
- `requires-python >= 3.10` matches source syntax/features.
- `py.typed` and all `.pyi` files ship in wheels.
- native `.cpp/.inc` ships in sdist for source builds.
- native source is excluded from wheels; the compiled extension remains.
