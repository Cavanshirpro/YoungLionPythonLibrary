# 14 — Student/course profile domain

**Complexity:** Intermediate  
**Focus:** typed DDM subclasses, nested DDM composition, ListDDM, DDMSearchEngine

## Scenario

Represent student enrollment and nested academic statistics, then query students by program, year and GPA.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
14_student_course_domain/
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

- Add `Course(DDM)` and `Enrollment(DDM)` models.
- Index numeric GPA for range queries.
- Use DDMTable to export grade summaries.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from __future__ import annotations
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class AcademicProfile(DDM):
    program: str
    year: int
    gpa: float

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.program = str(data.get('program', ""))
        self.year = int(data.get('year', 1))
        self.gpa = float(data.get('gpa', 0.0))


class Student(DDM):
    id: int
    name: str
    active: bool
    credits: int
    academic: AcademicProfile

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get('id', 0))
        self.name = str(data.get('name', ""))
        self.active = bool(data.get('active', True))
        self.credits = int(data.get('credits', 0))
        self.academic = AcademicProfile(data.get('academic', {}))

    def honor_candidate(self) -> bool:
        return self.active and self.academic.gpa >= 3.7

    def add_credits(self, amount: int) -> None:
        self.credits += max(0, amount)
```

### `repository.py`

```python
from __future__ import annotations
from collections.abc import Iterable
from YoungLion import ListDDM, DDMSearchEngine
from models import Student


class StudentRepository:
    def __init__(self, rows: Iterable[dict]):
        self.items = ListDDM(Student(row) for row in rows)
        self.search = DDMSearchEngine(self.items).create_indexes('id', 'active', 'credits', 'academic.program', 'academic.year', 'academic.gpa')

    def by_id(self, value: int) -> Student | None:
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
from repository import StudentRepository


class StudentService:
    def __init__(self, repository: StudentRepository):
        self.repository = repository

    def demo(self):
        cs = self.repository.where(academic__program="CS", active=True)
        honors = [s.name for s in self.repository.items if s.honor_candidate()]
        return {"active_cs": [s.name for s in cs], "honors": honors}
```

### `main.py`

```python
from __future__ import annotations
import json
from pathlib import Path
from repository import StudentRepository
from service import StudentService

DATA = Path(__file__).with_name("data.json")
rows = json.loads(DATA.read_text(encoding="utf-8"))
repo = StudentRepository(rows)
service = StudentService(repo)

print("records:", len(repo.items))
print("first:", repo.items[0].to_dict())
print("result:", service.demo())
print("index stats:", repo.search.stats())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

