# 21 — ViewDDM over shared mutable settings

**Complexity:** Intermediate  
**Focus:** ViewDDM, zero-copy view, shared state

## Scenario

Expose DDM-style access to an existing dictionary without duplicating ownership. Changes made through the view are visible to the original settings mapping.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
21_view_backed_settings/
├── main.py
```

## What to pay attention to

- **ViewDDM** — used as part of the actual workflow, not only imported for demonstration.
- **zero-copy view** — used as part of the actual workflow, not only imported for demonstration.
- **shared state** — used as part of the actual workflow, not only imported for demonstration.

## Run

From this directory:

```bash
python main.py
```

Install YoungLion first. After v0.1 is published:

```bash
python -m pip install YoungLion==0.1.0
```

During local pre-release development you can instead install the main branch checkout with `python -m pip install -e <path-to-main-checkout>`.

## Design notes

### Architecture walkthrough

This project isolates one specialized DDM/model capability and demonstrates the tradeoff that justifies it. Variants are not intended to replace normal `DDM` everywhere: choose them when immutability, identity hashing, lazy computation, defaults, validation, zero-copy views or memory density materially change the problem.

Keep the specialized boundary explicit. Convert to a richer typed domain subclass when domain behavior becomes more important than the storage/semantic specialization.

## Ways to extend this project

- Use a view only when shared mutation is intentional.
- Wrap the view in a service that validates writes.
- Snapshot to a normal DDM before long-lived asynchronous work.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `main.py`

```python
from YoungLion import ViewDDM

raw = {"theme": "dark", "window": {"width": 1280, "height": 720}}
view = ViewDDM(raw)
view["theme"] = "light"
view.set_path("window.width", 1440)
print("view:", view.to_dict())
print("same backing mapping:", raw)
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

