# 24 — TreeDDM category navigation

**Complexity:** Intermediate  
**Focus:** TreeDDM, hierarchical data, model helpers

## Scenario

Represent a hierarchy of categories and traverse it without flattening parent/child relationships into ad-hoc dictionaries.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
24_tree_category_navigation/
├── main.py
```

## What to pay attention to

- **TreeDDM** — used as part of the actual workflow, not only imported for demonstration.
- **hierarchical data** — used as part of the actual workflow, not only imported for demonstration.
- **model helpers** — used as part of the actual workflow, not only imported for demonstration.

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

- Attach DDM metadata to tree nodes.
- Build breadcrumbs/search paths.
- Persist the hierarchy with a custom serializer.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `main.py`

```python
from YoungLion import TreeDDM

root = TreeDDM("products")
electronics = root.add_child(TreeDDM("electronics"))
electronics.add_child(TreeDDM("laptops"))
electronics.add_child(TreeDDM("keyboards"))
root.add_child(TreeDDM("books"))
print(root)
print("children:", [child.value for child in root.children])
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

