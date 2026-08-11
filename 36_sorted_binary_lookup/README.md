# 36 — Sorted collection binary lookup

**Complexity:** Advanced  
**Focus:** stable native sort, lower_bound, equal_range, binary_search

## Scenario

Prepare a sorted DDM collection once and use lower_bound/equal_range/binary_search style operations for repeated exact/range-oriented access.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
36_sorted_binary_lookup/
├── main.py
```

## What to pay attention to

- **stable native sort** — used as part of the actual workflow, not only imported for demonstration.
- **lower_bound** — used as part of the actual workflow, not only imported for demonstration.
- **equal_range** — used as part of the actual workflow, not only imported for demonstration.
- **binary_search** — used as part of the actual workflow, not only imported for demonstration.

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

- Compare this approach with DDMSearchEngine when data is mutable or multiple paths are indexed.
- Keep the collection sorted after mutations or re-sort before binary operations.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `main.py`

```python
from YoungLion import ListDDM, DDM

rows = ListDDM(DDM({"id":i,"score":(i//3)*10}) for i in range(1000))
rows.sort_by("score", inplace=True)
start,end = rows.equal_range("score", 500)
print("score=500 slice:", [(r.id,r.score) for r in rows._items_snapshot()[start:end]])
print("lower bound 777:", rows.lower_bound("score",777))
print("binary 500:", rows.binary_search("score",500))
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

