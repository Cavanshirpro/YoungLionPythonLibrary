# Build Guide

The canonical build guide is [`docs/building.md`](docs/building.md).

Quick development build:

```bash
python -m pip install -U setuptools wheel pytest
python setup.py build_ext --inplace
PYTHONPATH=src python -m pytest -q
```

Strict compiler build:

```bash
YOUNGLION_STRICT=1 python setup.py build_ext --inplace --force
```

Build local distributions:

```bash
python -m pip install -U build twine
python -m build
python -m twine check dist/*
```

GitHub artifact builds are documented in [`docs/ci.md`](docs/ci.md) and manual PyPI publishing in [`docs/packaging.md`](docs/packaging.md).
