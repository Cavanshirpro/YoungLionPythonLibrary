# 46 — Product catalog search backend

**Complexity:** Advanced  
**Focus:** typed product DDM, ApplicationSearch, structured DDM indexes

## Scenario

Combine typed DDM product records with ApplicationSearch for user-facing text search and DDMSearchEngine for structured price/category queries.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
46_product_catalog_backend/
├── models.py
├── service.py
├── main.py
```

## What to pay attention to

- **typed product DDM** — used as part of the actual workflow, not only imported for demonstration.
- **ApplicationSearch** — used as part of the actual workflow, not only imported for demonstration.
- **structured DDM indexes** — used as part of the actual workflow, not only imported for demonstration.

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

- Add facet counts to the product search UI.
- Persist the catalog with File and rebuild indexes at startup.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from YoungLion import DDM
class Product(DDM):
    def __init__(self,d): super().__init__(d); self.id=int(d.get("id",0)); self.name=str(d.get("name","")); self.description=str(d.get("description","")); self.category=str(d.get("category","")); self.price=float(d.get("price",0)); self.stock=int(d.get("stock",0))
```

### `service.py`

```python
from YoungLion import ListDDM, DDMSearchEngine, ApplicationSearch
from models import Product
class Catalog:
    def __init__(self,rows):
        self.items=ListDDM(Product(x) for x in rows); self.structured=self.items.indexed("category","price","stock"); self.text=ApplicationSearch()
        for p in self.items: self.text.add(p.id,title=p.name,body=p.description,fields={"category":p.category},payload=p)
    def search(self,q): return self.text.search(q,limit=5)
    def available_under(self,category,price): return [p for p in self.structured.find("category",category) if p.price<=price and p.stock>0]
```

### `main.py`

```python
from service import Catalog
rows=[{"id":1,"name":"Gaming Laptop","description":"RTX graphics fast gaming notebook","category":"computer","price":1299,"stock":4},{"id":2,"name":"Office Laptop","description":"quiet productivity notebook","category":"computer","price":799,"stock":10},{"id":3,"name":"Wireless Mouse","description":"ergonomic bluetooth mouse","category":"accessory","price":49,"stock":0}]
c=Catalog(rows)
print([p.name for p in c.search("gming laptp")])
print([p.name for p in c.available_under("computer",1000)])
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

