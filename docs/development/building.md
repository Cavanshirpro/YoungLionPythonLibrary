# Building from source

```bash
python setup.py build_ext --inplace
```

Strict diagnostics:
```bash
YOUNGLION_STRICT=1 python setup.py build_ext --inplace --force
```

PEP 517 distributions:
```bash
python -m pip install build
python -m build
```

Release verification should unpack the sdist into a clean directory, rebuild there, run tests, build/install a wheel in a fresh venv with `--no-deps`, and run smoke imports.
