# 03 — E-commerce order domain

**Complexity:** Intermediate  
**Focus:** typed DDM subclasses, nested DDM composition, ListDDM, DDMSearchEngine

## Scenario

Parse orders with nested shipping information, calculate local business rules, and query orders by region/status using reusable nested indexes.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
03_ecommerce_order_domain/
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

- Add a `ListDDM` of line-item DDM subclasses.
- Create a country+status composite index.
- Persist transitions as an audit log with `Logger`.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class Shipping(DDM):
    country: str
    city: str
    method: str

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.country = str(data.get('country', ""))
        self.city = str(data.get('city', ""))
        self.method = str(data.get('method', "standard"))


class Order(DDM):
    id: int
    status: str
    subtotal: float
    shipping_cost: float
    paid: bool
    shipping: Shipping

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.status = str(data.get('status', "pending"))
        self.subtotal = float(data.get('subtotal', 0.0))
        self.shipping_cost = float(data.get('shipping_cost', 0.0))
        self.paid = bool(data.get('paid', False))
        self.shipping = Shipping(data.get('shipping', {}))

    @property
    def total(self) -> float:
        return round(self.subtotal + self.shipping_cost, 2)

    def mark_paid(self) -> None:
        self.paid = True
        if self.status == "pending":
            self.status = "processing"
```

### `repository.py`

```python
from __future__ import annotations
from collections.abc import Iterable
from YoungLion import ListDDM, DDMSearchEngine
from models import Order


class OrderRepository:
    def __init__(self, rows: Iterable[dict]):
        self.items = ListDDM(Order(row) for row in rows)
        self.search = DDMSearchEngine(self.items).create_indexes('id', 'status', 'paid', 'shipping.country')

    def by_id(self, value: int) -> Order | None:
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
from repository import OrderRepository


class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def demo(self):
        az_orders = self.repository.where(shipping__country="AZ", paid=True)
        pending = self.repository.where(status="pending")
        if pending:
            pending[0].mark_paid()
        return {"azerbaijan_revenue": sum(o.total for o in az_orders), "updated_status": pending[0].status if pending else None}
```

### `main.py`

```python
from __future__ import annotations
import json
from pathlib import Path
from repository import OrderRepository
from service import OrderService

DATA = Path(__file__).with_name("data.json")
rows = json.loads(DATA.read_text(encoding="utf-8"))
repo = OrderRepository(rows)
service = OrderService(repo)

print("records:", len(repo.items))
print("first:", repo.items[0].to_dict())
print("result:", service.demo())
print("index stats:", repo.search.stats())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

