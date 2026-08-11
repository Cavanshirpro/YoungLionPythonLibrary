# 09 — Subscription and billing domain

**Complexity:** Intermediate  
**Focus:** typed DDM subclasses, nested DDM composition, ListDDM, DDMSearchEngine

## Scenario

Model a subscription with nested billing preferences and query renewals/plan state without flattening the domain into unrelated dictionaries.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
09_subscription_billing_domain/
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

- Add invoice/history models as nested lists.
- Build a composite index for country + plan.
- Persist billing snapshots atomically before applying migrations.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class BillingProfile(DDM):
    method: str
    country: str
    auto_renew: bool

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.method = str(data.get('method', "card"))
        self.country = str(data.get('country', "AZ"))
        self.auto_renew = bool(data.get('auto_renew', True))


class Subscription(DDM):
    id: int
    plan: str
    monthly_price: float
    renewal_day: int
    active: bool
    billing: BillingProfile

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.plan = str(data.get('plan', "free"))
        self.monthly_price = float(data.get('monthly_price', 0.0))
        self.renewal_day = int(data.get('renewal_day', 1))
        self.active = bool(data.get('active', True))
        self.billing = BillingProfile(data.get('billing', {}))

    def cancel(self) -> None:
        self.active = False
        self.billing.auto_renew = False

    def annual_cost(self) -> float:
        return round(self.monthly_price * 12, 2)
```

### `repository.py`

```python
from __future__ import annotations
from collections.abc import Iterable
from YoungLion import ListDDM, DDMSearchEngine
from models import Subscription


class SubscriptionRepository:
    def __init__(self, rows: Iterable[dict]):
        self.items = ListDDM(Subscription(row) for row in rows)
        self.search = DDMSearchEngine(self.items).create_indexes('id', 'plan', 'renewal_day', 'active', 'billing.country')

    def by_id(self, value: int) -> Subscription | None:
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
from repository import SubscriptionRepository


class SubscriptionService:
    def __init__(self, repository: SubscriptionRepository):
        self.repository = repository

    def demo(self):
        renew_today = self.repository.where(renewal_day=12, active=True)
        return [(s.id, s.plan, s.annual_cost(), s.billing.auto_renew) for s in renew_today]
```

### `main.py`

```python
from __future__ import annotations
import json
from pathlib import Path
from repository import SubscriptionRepository
from service import SubscriptionService

DATA = Path(__file__).with_name("data.json")
rows = json.loads(DATA.read_text(encoding="utf-8"))
repo = SubscriptionRepository(rows)
service = SubscriptionService(repo)

print("records:", len(repo.items))
print("first:", repo.items[0].to_dict())
print("result:", service.demo())
print("index stats:", repo.search.stats())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

