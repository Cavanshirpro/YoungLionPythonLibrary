# 31 — DDMTable analytics/reporting

**Complexity:** Advanced  
**Focus:** DDMTable, query/select, numeric aggregation

## Scenario

Use DDMTable as a lightweight structured reporting layer over typed sale records: select columns, query dimensions, and run numeric aggregations.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
31_ddmtable_sales_analytics/
├── main.py
├── models.py
```

## What to pay attention to

- **DDMTable** — used as part of the actual workflow, not only imported for demonstration.
- **query/select** — used as part of the actual workflow, not only imported for demonstration.
- **numeric aggregation** — used as part of the actual workflow, not only imported for demonstration.

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

- Export selected rows to CSV with File.
- Group by region and create summary DDMs.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from YoungLion import DDM
class Sale(DDM):
    def __init__(self,data):
        super().__init__(data); self.id=int(data.get("id",0)); self.region=str(data.get("region","")); self.amount=float(data.get("amount",0)); self.quantity=int(data.get("quantity",0))
```

### `main.py`

```python
from YoungLion import DDMTable
from models import Sale

rows = DDMTable(Sale({"id":i,"region":"AZ" if i%2 else "EU","amount":20+(i%9)*15,"quantity":1+i%4}) for i in range(200))
print("columns:", rows.columns())
print("AZ revenue:", rows.query(region="AZ").sum("amount"))
print("mean qty:", rows.mean("quantity"))
print("sample report:", rows.select("id","region","amount")[:5])
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

