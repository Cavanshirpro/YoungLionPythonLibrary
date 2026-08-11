# 10 — Product inventory domain

**Complexity:** Intermediate  
**Focus:** typed DDM subclasses, nested DDM composition, ListDDM, DDMSearchEngine

## Scenario

Model inventory items with nested supplier data and perform stock/value queries using typed subclasses and reusable indexes.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
10_product_inventory_domain/
├── models.py
├── repository.py
├── service.py
├── main.py
├── data.json
```

## What to pay attention to

- **typed DDM subclasses** — used as part of the actual workflow, not only imported for demonstration.
- **nested DDM composition** — used as part of the actual workflow, not only imported for demonstration.
- **ListDDM** — used as part of the actual workflow, not only imported for demonstration.
- **DDMSearchEngine** — used as part of the actual workflow, not only imported for demonstration.

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

This project uses a **domain-model → repository/index → service → entry-point** split. DDM subclasses own normalization and local invariants; the repository owns `ListDDM` and `DDMSearchEngine`; the service coordinates the use case. This is a practical shape when `class User(DDM)` grows beyond a small script.

Nested mappings are deliberately replaced by typed DDM objects during construction. That gives the IDE real attributes such as `user.profile.country`, while `to_dict()`, `get_path("profile.country")`, collection batch operations and nested indexes continue to work. Unknown input keys can remain available for forward compatibility.

## Ways to extend this project

- Add `ApplicationSearch` for typo-friendly product names.
- Use `DDMTable` for inventory reports.
- Use `BatchPlan` for percentage price updates.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class Supplier(DDM):
    id: int
    name: str
    country: str

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.name = str(data.get('name', ""))
        self.country = str(data.get('country', ""))


class Product(DDM):
    id: int
    sku: str
    name: str
    price: float
    stock: int
    supplier: Supplier

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.sku = str(data.get('sku', ""))
        self.name = str(data.get('name', ""))
        self.price = float(data.get('price', 0.0))
        self.stock = int(data.get('stock', 0))
        self.supplier = Supplier(data.get('supplier', {}))

    def restock(self, quantity: int) -> None:
        if quantity <= 0: raise ValueError("quantity must be positive")
        self.stock += quantity

    def stock_value(self) -> float:
        return round(self.price * self.stock, 2)
```

### `repository.py`

```python
from __future__ import annotations
from collections.abc import Iterable
from YoungLion import ListDDM, DDMSearchEngine
from models import Product


class ProductRepository:
    def __init__(self, rows: Iterable[dict]):
        self.items = ListDDM(Product(row) for row in rows)
        self.search = DDMSearchEngine(self.items).create_indexes('id', 'sku', 'stock', 'supplier.id', 'supplier.country')

    def by_id(self, value: int) -> Product | None:
        return self.search.find_one("id", value)

    def where(self, **lookups):
        return self.search.where(**lookups)

    def refresh(self) -> None:
        self.search.refresh()

    def snapshot(self) -> list[dict]:
        return [item.to_dict() for item in self.items]
```

### `service.py`

```python
from __future__ import annotations
from repository import ProductRepository


class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def demo(self):
        empty = self.repository.where(stock=0)
        for product in empty: product.restock(10)
        self.repository.refresh()
        return {p.sku: p.stock_value() for p in self.repository.items}
```

### `main.py`

```python
from __future__ import annotations
import json
from pathlib import Path
from repository import ProductRepository
from service import ProductService

DATA = Path(__file__).with_name("data.json")
rows = json.loads(DATA.read_text(encoding="utf-8"))
repo = ProductRepository(rows)
service = ProductService(repo)

print("records:", len(repo.items))
print("first:", repo.items[0].to_dict())
print("result:", service.demo())
print("index stats:", repo.search.stats())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

