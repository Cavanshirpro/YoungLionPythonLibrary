# 39 — Large numeric transform and constraints

**Complexity:** Advanced  
**Focus:** native numeric operations, nested paths, large data

## Scenario

Apply native arithmetic to a large nested metric path and calculate summary statistics without serializing records.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
39_large_score_transform/
├── main.py
```

## What to pay attention to

- **native numeric operations** — used as part of the actual workflow, not only imported for demonstration.
- **nested paths** — used as part of the actual workflow, not only imported for demonstration.
- **large data** — used as part of the actual workflow, not only imported for demonstration.

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

- Replace three passes with BatchPlan when operations can be fused.
- Benchmark against a normal Python loop for your record shape.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `main.py`

```python
from YoungLion import ListDDM, DDM

rows = ListDDM(DDM({"id":i,"metrics":{"score":float((i*13)%120),"bonus":1.0}}) for i in range(20000))
rows.multiply("metrics.score",1.075)
rows.increment("metrics.score",3)
rows.clamp("metrics.score",0,100)
print({"count":rows.numeric_count("metrics.score"),"mean":rows.mean("metrics.score"),"min":rows.min("metrics.score"),"max":rows.max("metrics.score")})
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

