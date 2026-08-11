# 38 — Inventory restock bulk pipeline

**Complexity:** Advanced  
**Focus:** partition_path, selected bulk mutation, reductions

## Scenario

Partition products by stock state, apply restock only to selected rows, and compute post-operation inventory value.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
38_inventory_restock_pipeline/
├── main.py
```

## What to pay attention to

- **partition_path** — used as part of the actual workflow, not only imported for demonstration.
- **selected bulk mutation** — used as part of the actual workflow, not only imported for demonstration.
- **reductions** — used as part of the actual workflow, not only imported for demonstration.

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

- Use apply_where for reorder quantities based on product category.
- Index low-stock paths for an interactive admin UI.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `main.py`

```python
from YoungLion import ListDDM, DDM

products = ListDDM(DDM({"id":i,"stock":i%8,"price":10+(i%25)}) for i in range(1000))
empty,available = products.partition_path("stock",0,op="eq")
restock = ListDDM(empty)
restock.set_all("stock",25)
print("restocked:", len(restock), "available before:",len(available))
print("stock total:", products.sum("stock"))
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

