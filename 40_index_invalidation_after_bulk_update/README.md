# 40 — Search index invalidation after bulk mutation

**Complexity:** Advanced  
**Focus:** DDMSearchEngine, index invalidation, ListDDM mutation

## Scenario

Demonstrate why collection-owned mutation is important: indexed paths are invalidated/rebuilt automatically after a ListDDM bulk update.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
40_index_invalidation_after_bulk_update/
├── main.py
```

## What to pay attention to

- **DDMSearchEngine** — used as part of the actual workflow, not only imported for demonstration.
- **index invalidation** — used as part of the actual workflow, not only imported for demonstration.
- **ListDDM mutation** — used as part of the actual workflow, not only imported for demonstration.

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

The important unit here is the **collection**, not one record. Records stay DDM-compatible while transformations happen through `ListDDM`, `SetDDM`, `DictDDM`, `DDMTable` or `BatchPlan`. Path/numeric primitives avoid repeated Python-level traversal; arbitrary business logic can still be injected through callback operations when necessary.

For production migrations, separate transformation from persistence: validate the transformed collection, checkpoint it, then commit it to your database or file store in bounded chunks.

## Ways to extend this project

- Prefer `collection.indexed(...)` so engine ownership is automatic.
- Call refresh() after mutating records directly outside the collection.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `main.py`

```python
from YoungLion import ListDDM, DDM, DDMSearchEngine

users = ListDDM(DDM({"id":i,"profile":{"country":"AZ" if i%2 else "US"}}) for i in range(1000))
engine = DDMSearchEngine(users).create_indexes("profile.country")
users._search_engine = engine
print("AZ before:", engine.count("profile.country","AZ"))
users.set_all("profile.country","AZ")
print("AZ after:", engine.count("profile.country","AZ"))
print("stats:", engine.stats())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

