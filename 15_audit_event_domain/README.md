# 15 — Audit/security event domain

**Complexity:** Intermediate  
**Focus:** typed DDM subclasses, nested DDM composition, ListDDM, DDMSearchEngine

## Scenario

Model immutable-looking audit data with nested actor context while retaining DDM searchability for event type, severity and actor location.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
15_audit_event_domain/
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

- Convert persisted events to `FrozenDDM` when mutation must be impossible.
- Use MultiPatternSearch on free-form audit messages.
- Write daily logs with File + checksums.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class Actor(DDM):
    id: int
    name: str
    ip: str
    country: str

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.name = str(data.get('name', ""))
        self.ip = str(data.get('ip', ""))
        self.country = str(data.get('country', ""))


class AuditEvent(DDM):
    id: int
    event_type: str
    severity: int
    resource: str
    success: bool
    actor: Actor

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.event_type = str(data.get('event_type', ""))
        self.severity = int(data.get('severity', 0))
        self.resource = str(data.get('resource', ""))
        self.success = bool(data.get('success', False))
        self.actor = Actor(data.get('actor', {}))

    def security_relevant(self) -> bool:
        return self.severity >= 4 or not self.success

    def summary(self) -> str:
        return f"{self.event_type} by {self.actor.name} on {self.resource}"
```

### `repository.py`

```python
from __future__ import annotations
from collections.abc import Iterable
from YoungLion import ListDDM, DDMSearchEngine
from models import AuditEvent


class AuditEventRepository:
    def __init__(self, rows: Iterable[dict]):
        self.items = ListDDM(AuditEvent(row) for row in rows)
        self.search = DDMSearchEngine(self.items).create_indexes('id', 'event_type', 'severity', 'success', 'actor.country', 'actor.id')

    def by_id(self, value: int) -> AuditEvent | None:
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
from repository import AuditEventRepository


class AuditEventService:
    def __init__(self, repository: AuditEventRepository):
        self.repository = repository

    def demo(self):
        important = self.repository.where(severity__ge=4)
        return [e.summary() for e in important if e.security_relevant()]
```

### `main.py`

```python
from __future__ import annotations
import json
from pathlib import Path
from repository import AuditEventRepository
from service import AuditEventService

DATA = Path(__file__).with_name("data.json")
rows = json.loads(DATA.read_text(encoding="utf-8"))
repo = AuditEventRepository(rows)
service = AuditEventService(repo)

print("records:", len(repo.items))
print("first:", repo.items[0].to_dict())
print("result:", service.demo())
print("index stats:", repo.search.stats())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

