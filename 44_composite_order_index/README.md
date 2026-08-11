# 44 — Composite order index

**Complexity:** Advanced  
**Focus:** composite index, nested paths, typed order model

## Scenario

Create a composite index for high-frequency multi-field lookups such as tenant/status/country rather than intersecting full scans every time.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
44_composite_order_index/
├── models.py
├── main.py
```

## What to pay attention to

- **composite index** — used as part of the actual workflow, not only imported for demonstration.
- **nested paths** — used as part of the actual workflow, not only imported for demonstration.
- **typed order model** — used as part of the actual workflow, not only imported for demonstration.

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

Search is treated as a **long-lived service/index**, not a helper that performs a fresh full scan for every query. Index build cost is paid when data is loaded or changed; repeated queries reuse exact/range/text/composite structures. User-facing text ranking and structured DDM path lookups are separate tools and can be combined when a UI needs both.

Do not index every field automatically. Index hot paths that are queried repeatedly, monitor memory, and refresh/invalidate indexes when source records change outside collection-owned mutation APIs.

## Ways to extend this project

- Use a composite only for combinations queried frequently.
- Compare memory cost with intersecting separate indexes.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from YoungLion import DDM
class Customer(DDM):
    def __init__(self,d): super().__init__(d); self.country=str(d.get("country","")); self.tier=str(d.get("tier","free"))
class Order(DDM):
    def __init__(self,d): super().__init__(d); self.id=int(d.get("id",0)); self.tenant=str(d.get("tenant","default")); self.status=str(d.get("status","pending")); self.total=float(d.get("total",0)); self.customer=Customer(d.get("customer",{}))
```

### `main.py`

```python
from YoungLion import ListDDM, DDMSearchEngine
from models import Order
orders=ListDDM(Order({"id":i,"tenant":f"t{i%5}","status":["pending","paid","shipped"][i%3],"total":10+i%500,"customer":{"country":["AZ","US","DE"][i%3],"tier":"pro" if i%4==0 else "free"}}) for i in range(30000))
engine=DDMSearchEngine(orders)
engine.create_composite_index("tenant","status","customer.country")
rows=engine.composite(("tenant","status","customer.country"),("t2","shipped","DE"))
print("matches:",len(rows),"sample:",rows[0].to_dict() if rows else None)
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

