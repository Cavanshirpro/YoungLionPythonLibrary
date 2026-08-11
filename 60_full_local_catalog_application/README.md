# 60 — Full local catalog mini-application

**Complexity:** Advanced  
**Focus:** typed DDM subclasses, ListDDM, DDMSearchEngine, ApplicationSearch, File, Logger

## Scenario

Combine typed DDM domain models, ListDDM, structured nested indexes, typo-friendly application search, atomic persistence and structured logging in one small but complete local application.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
60_full_local_catalog_application/
├── models.py
├── catalog.py
├── main.py
```

## What to pay attention to

- **typed DDM subclasses** — used as part of the actual workflow, not only imported for demonstration.
- **ListDDM** — used as part of the actual workflow, not only imported for demonstration.
- **DDMSearchEngine** — used as part of the actual workflow, not only imported for demonstration.
- **ApplicationSearch** — used as part of the actual workflow, not only imported for demonstration.
- **File** — used as part of the actual workflow, not only imported for demonstration.
- **Logger** — used as part of the actual workflow, not only imported for demonstration.

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

This project combines several YoungLion components behind a small service boundary. The emphasis is operational: safe file replacement, structured process results, caching/rate limiting, event delivery, search ownership or logging. Application code should consume the service rather than coordinate every utility directly.

The example stays network-free and credential-free. In a real application, external I/O belongs behind adapters where retry, circuit breaking, validation and logging policies can be tested independently.

## Ways to extend this project

- Split persistence into a repository when moving beyond local JSON.
- Add facets/autocomplete to the UI.
- Use BatchPlan for mass price/stock transformations.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from YoungLion import DDM
class Supplier(DDM):
    def __init__(self,d): super().__init__(d); self.name=str(d.get("name","Unknown")); self.country=str(d.get("country","Unknown"))
class Product(DDM):
    def __init__(self,d):
        super().__init__(d); self.id=int(d.get("id",0)); self.name=str(d.get("name","")); self.description=str(d.get("description","")); self.category=str(d.get("category","")); self.price=float(d.get("price",0)); self.stock=int(d.get("stock",0)); self.supplier=Supplier(d.get("supplier",{}))
    def restock(self,n):
        if n<=0: raise ValueError("positive restock required")
        self.stock += int(n)
```

### `catalog.py`

```python
from pathlib import Path

from YoungLion import ListDDM, DDMSearchEngine, ApplicationSearch, File, Logger
from models import Product
class CatalogApp:
    def __init__(self,root,rows):
        self.files=File(root); self.log=Logger(str(Path(root) / "catalog.log"),console=False,max_bytes=100000,backup_count=2); self.products=ListDDM(Product(x) for x in rows); self.paths=self.products.indexed("id","category","price","stock","supplier.country"); self.text=ApplicationSearch(); self._rebuild_text()
    def _rebuild_text(self):
        self.text=ApplicationSearch()
        for p in self.products: self.text.add(p.id,title=p.name,body=p.description,tags=[p.category,p.supplier.name],fields={"category":p.category,"country":p.supplier.country},payload=p)
    def query(self,text,category=None,max_price=None):
        candidates=self.text.search(text,limit=50); allowed={id(p) for p in candidates}
        if category: allowed &= {id(p) for p in self.paths.find("category",category)}
        if max_price is not None: allowed &= {id(p) for p in self.paths.find("price",max_price,op="le")}
        return [p for p in candidates if id(p) in allowed]
    def restock_empty(self,amount=10):
        empty=self.paths.find("stock",0); [p.restock(amount) for p in empty]; self.paths.refresh(); self._rebuild_text(); self.log.info("restocked",count=len(empty),amount=amount); return len(empty)
    def save(self): self.files.atomic_write_json("catalog.json",[p.to_dict() for p in self.products]); return self.files.checksum("catalog.json")
```

### `main.py`

```python
from tempfile import TemporaryDirectory
from catalog import CatalogApp
rows=[
 {"id":1,"name":"Gaming Laptop","description":"high performance RTX gaming notebook","category":"computer","price":1299,"stock":3,"supplier":{"name":"TechCo","country":"US"}},
 {"id":2,"name":"Office Laptop","description":"quiet efficient work notebook","category":"computer","price":799,"stock":0,"supplier":{"name":"TechCo","country":"US"}},
 {"id":3,"name":"Mechanical Keyboard","description":"hot swap tactile keyboard","category":"accessory","price":119,"stock":8,"supplier":{"name":"InputLab","country":"DE"}},
]
with TemporaryDirectory() as tmp:
    app=CatalogApp(tmp,rows)
    print("search",[(p.name,p.price) for p in app.query("ofice laptp",category="computer",max_price=1000)])
    print("restocked",app.restock_empty())
    print("digest",app.save())
    print("stats",app.paths.stats())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

