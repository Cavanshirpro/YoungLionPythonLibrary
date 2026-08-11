# 05 — Bank account domain model

**Complexity:** Intermediate  
**Focus:** typed DDM subclasses, nested DDM composition, ListDDM, DDMSearchEngine

## Scenario

Keep account identity and nested owner/KYC data in DDM subclasses while enforcing balance operations through domain methods.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
05_bank_account_domain/
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

- Replace currency strings with an Enum.
- Build a transaction service that owns transfer atomicity.
- Use `FrozenDDM` for immutable transaction IDs/keys.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class Owner(DDM):
    name: str
    country: str
    verified: bool

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.name = str(data.get('name', ""))
        self.country = str(data.get('country', ""))
        self.verified = bool(data.get('verified', False))


class BankAccount(DDM):
    id: int
    currency: str
    balance: float
    locked: bool
    owner: Owner

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.currency = str(data.get('currency', "USD"))
        self.balance = float(data.get('balance', 0.0))
        self.locked = bool(data.get('locked', False))
        self.owner = Owner(data.get('owner', {}))

    def deposit(self, amount: float) -> None:
        if amount <= 0: raise ValueError("amount must be positive")
        if self.locked: raise RuntimeError("account is locked")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0: raise ValueError("amount must be positive")
        if self.locked or amount > self.balance: raise RuntimeError("withdrawal denied")
        self.balance -= amount
```

### `repository.py`

```python
from __future__ import annotations
from collections.abc import Iterable
from YoungLion import ListDDM, DDMSearchEngine
from models import BankAccount


class BankAccountRepository:
    def __init__(self, rows: Iterable[dict]):
        self.items = ListDDM(BankAccount(row) for row in rows)
        self.search = DDMSearchEngine(self.items).create_indexes('id', 'currency', 'locked', 'owner.country', 'owner.verified')

    def by_id(self, value: int) -> BankAccount | None:
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
from repository import BankAccountRepository


class BankAccountService:
    def __init__(self, repository: BankAccountRepository):
        self.repository = repository

    def demo(self):
        verified = self.repository.where(owner__verified=True, locked=False)
        verified[0].deposit(125)
        return {a.id: a.balance for a in verified}
```

### `main.py`

```python
from __future__ import annotations
import json
from pathlib import Path
from repository import BankAccountRepository
from service import BankAccountService

DATA = Path(__file__).with_name("data.json")
rows = json.loads(DATA.read_text(encoding="utf-8"))
repo = BankAccountRepository(rows)
service = BankAccountService(repo)

print("records:", len(repo.items))
print("first:", repo.items[0].to_dict())
print("result:", service.demo())
print("index stats:", repo.search.stats())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

