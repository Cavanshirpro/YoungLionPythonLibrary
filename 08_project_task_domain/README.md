# 08 — Project and task domain

**Complexity:** Intermediate  
**Focus:** typed DDM subclasses, nested DDM composition, ListDDM, DDMSearchEngine

## Scenario

Use DDM subclasses for project work items with nested assignment metadata and query work by owner, priority and completion state.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
08_project_task_domain/
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

- Add due dates and a numeric timestamp index.
- Use `TaskScheduler` to trigger periodic checks.
- Use `DDMTable.select()` for a reporting view.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class Assignment(DDM):
    owner: str
    team: str
    blocked: bool

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.owner = str(data.get('owner', ""))
        self.team = str(data.get('team', ""))
        self.blocked = bool(data.get('blocked', False))


class Task(DDM):
    id: int
    title: str
    priority: int
    progress: float
    done: bool
    assignment: Assignment

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.title = str(data.get('title', ""))
        self.priority = int(data.get('priority', 1))
        self.progress = float(data.get('progress', 0.0))
        self.done = bool(data.get('done', False))
        self.assignment = Assignment(data.get('assignment', {}))

    def advance(self, delta: float) -> None:
        self.progress = min(1.0, max(0.0, self.progress + delta))
        self.done = self.progress >= 1.0

    def actionable(self) -> bool:
        return not self.done and not self.assignment.blocked
```

### `repository.py`

```python
from __future__ import annotations
from collections.abc import Iterable
from YoungLion import ListDDM, DDMSearchEngine
from models import Task


class TaskRepository:
    def __init__(self, rows: Iterable[dict]):
        self.items = ListDDM(Task(row) for row in rows)
        self.search = DDMSearchEngine(self.items).create_indexes('id', 'priority', 'done', 'assignment.owner', 'assignment.team')

    def by_id(self, value: int) -> Task | None:
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
from repository import TaskRepository


class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def demo(self):
        mine = self.repository.where(assignment__owner="cavan", done=False)
        for task in mine: task.advance(0.25)
        return [(t.title, t.progress, t.done) for t in mine]
```

### `main.py`

```python
from __future__ import annotations
import json
from pathlib import Path
from repository import TaskRepository
from service import TaskService

DATA = Path(__file__).with_name("data.json")
rows = json.loads(DATA.read_text(encoding="utf-8"))
repo = TaskRepository(rows)
service = TaskService(repo)

print("records:", len(repo.items))
print("first:", repo.items[0].to_dict())
print("result:", service.demo())
print("index stats:", repo.search.stats())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

