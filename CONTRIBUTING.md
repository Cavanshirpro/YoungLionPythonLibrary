# Contributing

1. Keep third-party runtime Python dependencies at zero.
2. Put performance-sensitive primitive operations in `YoungLion._native` rather than adding Python packages.
3. Preserve existing public import paths and method signatures whenever practical.
4. Add a regression test for every bug fix.
5. Run `python setup.py build_ext --inplace` and `python -m pytest -q` before opening a PR.
6. Avoid `-march=native` and build-machine-specific assumptions in release artifacts.
7. Update `.pyi` files whenever a public API changes.
