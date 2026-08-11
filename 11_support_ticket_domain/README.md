# 11 — Support ticket domain

**Complexity:** Intermediate  
**Focus:** typed DDM subclasses, nested DDM composition, ListDDM, DDMSearchEngine

## Scenario

Represent tickets with nested requester context and efficiently query open tickets by priority, country or account tier.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
11_support_ticket_domain/
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

- Text-index `subject` for helpdesk search.
- Use EventBus to emit assignment/close events.
- Use Logger.bind(ticket_id=...) for structured logs.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class Requester(DDM):
    id: int
    name: str
    tier: str
    country: str

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.name = str(data.get('name', ""))
        self.tier = str(data.get('tier', "free"))
        self.country = str(data.get('country', "Unknown"))


class Ticket(DDM):
    id: int
    subject: str
    status: str
    priority: int
    assigned: bool
    requester: Requester

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.subject = str(data.get('subject', ""))
        self.status = str(data.get('status', "open"))
        self.priority = int(data.get('priority', 1))
        self.assigned = bool(data.get('assigned', False))
        self.requester = Requester(data.get('requester', {}))

    def assign(self) -> None:
        if self.status == "closed": raise RuntimeError("closed ticket")
        self.assigned = True

    def close(self) -> None:
        self.status = "closed"
```

### `repository.py`

```python
from __future__ import annotations
from collections.abc import Iterable
from YoungLion import ListDDM, DDMSearchEngine
from models import Ticket


class TicketRepository:
    def __init__(self, rows: Iterable[dict]):
        self.items = ListDDM(Ticket(row) for row in rows)
        self.search = DDMSearchEngine(self.items).create_indexes('id', 'status', 'priority', 'assigned', 'requester.tier', 'requester.country')

    def by_id(self, value: int) -> Ticket | None:
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
from repository import TicketRepository


class TicketService:
    def __init__(self, repository: TicketRepository):
        self.repository = repository

    def demo(self):
        urgent = self.repository.where(status="open", priority__ge=4)
        for ticket in urgent:
            if not ticket.assigned: ticket.assign()
        return [(t.id, t.subject, t.assigned, t.requester.tier) for t in urgent]
```

### `main.py`

```python
from __future__ import annotations
import json
from pathlib import Path
from repository import TicketRepository
from service import TicketService

DATA = Path(__file__).with_name("data.json")
rows = json.loads(DATA.read_text(encoding="utf-8"))
repo = TicketRepository(rows)
service = TicketService(repo)

print("records:", len(repo.items))
print("first:", repo.items[0].to_dict())
print("result:", service.demo())
print("index stats:", repo.search.stats())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

