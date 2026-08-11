# 06 — Typed API response models

**Complexity:** Intermediate  
**Focus:** typed DDM subclasses, nested DDM composition, ListDDM, DDMSearchEngine

## Scenario

Normalize partially trusted API response dictionaries into typed nested DDM subclasses while preserving unknown fields for forward compatibility.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
06_api_response_models/
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

- Add response-version migration methods.
- Use `DefaultDDM` for optional server flags.
- Index nested API metadata only when it is queried frequently.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class ApiMeta(DDM):
    request_id: str
    page: int
    cached: bool

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.request_id = str(data.get('request_id', ""))
        self.page = int(data.get('page', 1))
        self.cached = bool(data.get('cached', False))


class ApiUser(DDM):
    id: int
    email: str
    status: str
    verified: bool
    meta: ApiMeta

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.email = str(data.get('email', ""))
        self.status = str(data.get('status', "unknown"))
        self.verified = bool(data.get('verified', False))
        self.meta = ApiMeta(data.get('meta', {}))

    def public_view(self) -> dict[str, object]:
        return {"id": self.id, "email": self.email, "status": self.status, "verified": self.verified}

    def activate(self) -> None:
        if not self.verified: raise RuntimeError("verification required")
        self.status = "active"
```

### `repository.py`

```python
from __future__ import annotations
from collections.abc import Iterable
from YoungLion import ListDDM, DDMSearchEngine
from models import ApiUser


class ApiUserRepository:
    def __init__(self, rows: Iterable[dict]):
        self.items = ListDDM(ApiUser(row) for row in rows)
        self.search = DDMSearchEngine(self.items).create_indexes('id', 'status', 'verified', 'meta.cached')

    def by_id(self, value: int) -> ApiUser | None:
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
from repository import ApiUserRepository


class ApiUserService:
    def __init__(self, repository: ApiUserRepository):
        self.repository = repository

    def demo(self):
        active = self.repository.where(status="active")
        return {"active": [u.public_view() for u in active], "unknown_field_preserved": self.repository.items[0].get("new_server_field")}
```

### `main.py`

```python
from __future__ import annotations
import json
from pathlib import Path
from repository import ApiUserRepository
from service import ApiUserService

DATA = Path(__file__).with_name("data.json")
rows = json.loads(DATA.read_text(encoding="utf-8"))
repo = ApiUserRepository(rows)
service = ApiUserService(repo)

print("records:", len(repo.items))
print("first:", repo.items[0].to_dict())
print("result:", service.demo())
print("index stats:", repo.search.stats())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

