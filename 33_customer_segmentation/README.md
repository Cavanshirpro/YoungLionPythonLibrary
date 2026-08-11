# 33 — Customer segmentation with group/count/distinct

**Complexity:** Advanced  
**Focus:** group_by, count_by, distinct, reductions

## Scenario

Create reporting segments from a large customer collection using reusable path-oriented collection operations.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
33_customer_segmentation/
├── main.py
├── models.py
```

## What to pay attention to

- **group_by** — used as part of the actual workflow, not only imported for demonstration.
- **count_by** — used as part of the actual workflow, not only imported for demonstration.
- **distinct** — used as part of the actual workflow, not only imported for demonstration.
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

- Create segment DDM summary records.
- Use search indexes for interactive drill-down after grouping.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from YoungLion import DDM
class Customer(DDM):
    def __init__(self,data):
        super().__init__(data); self.id=int(data.get("id",0)); self.country=str(data.get("country","")); self.tier=str(data.get("tier","free")); self.spend=float(data.get("spend",0))
```

### `main.py`

```python
from YoungLion import ListDDM
from models import Customer

customers = ListDDM(Customer({"id":i,"country":["AZ","US","DE"][i%3],"tier":["free","pro","team"][i%3],"spend":(i*17)%5000}) for i in range(5000))
print("countries:", customers.distinct("country"))
print("tier counts:", customers.count_by("tier"))
for country, rows in customers.group_by("country").items():
    group = ListDDM(rows)
    print(country, "users", len(group), "mean spend", round(group.mean("spend") or 0,2))
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

