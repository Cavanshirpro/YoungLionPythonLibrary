# 01 — Typed user account domain

**Complexity:** Intermediate  
**Focus:** typed DDM subclasses, nested DDM composition, ListDDM, DDMSearchEngine

## Scenario

Model users received from JSON/API data with a nested profile, domain behavior, a repository-owned nested index, and a service layer that performs a real account operation.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
01_typed_user_account/
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

- Add an `Address(DDM)` nested inside `UserProfile`.
- Persist `repository.snapshot()` with `File.atomic_write_json`.
- Add a composite index for country + role.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class UserProfile(DDM):
    display_name: str
    country: str
    age: int

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.display_name = str(data.get('display_name', "Unknown"))
        self.country = str(data.get('country', "Unknown"))
        self.age = int(data.get('age', 0))


class User(DDM):
    id: int
    username: str
    role: str
    active: bool
    profile: UserProfile

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.username = str(data.get('username', "unknown"))
        self.role = str(data.get('role', "member"))
        self.active = bool(data.get('active', True))
        self.profile = UserProfile(data.get('profile', {}))

    def can_access_admin(self) -> bool:
        return self.active and self.role == "admin"

    def rename(self, username: str) -> None:
        username = username.strip()
        if len(username) < 3:
            raise ValueError("username is too short")
        self.username = username
```

### `repository.py`

```python
from __future__ import annotations
from collections.abc import Iterable
from YoungLion import ListDDM, DDMSearchEngine
from models import User


class UserRepository:
    def __init__(self, rows: Iterable[dict]):
        self.items = ListDDM(User(row) for row in rows)
        self.search = DDMSearchEngine(self.items).create_indexes('id', 'username', 'profile.country', 'profile.age')

    def by_id(self, value: int) -> User | None:
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
from repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def demo(self):
        user = self.repository.by_id(2)
        assert user is not None
        user.rename("cavanshir")
        adults = self.repository.where(profile__age__ge=18, active=True)
        self.repository.refresh()
        return {"renamed": user.username, "adult_active_ids": [u.id for u in adults]}
```

### `main.py`

```python
from __future__ import annotations
import json
from pathlib import Path
from repository import UserRepository
from service import UserService

DATA = Path(__file__).with_name("data.json")
rows = json.loads(DATA.read_text(encoding="utf-8"))
repo = UserRepository(rows)
service = UserService(repo)

print("records:", len(repo.items))
print("first:", repo.items[0].to_dict())
print("result:", service.demo())
print("index stats:", repo.search.stats())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

