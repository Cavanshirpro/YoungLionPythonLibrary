# 26 — Bulk nested account migration

**Complexity:** Advanced  
**Focus:** ListDDM, rename/copy/fill path, typed subclasses

## Scenario

Migrate thousands of typed user models from legacy nested field names to the v0.1 layout, using path operations rather than hand-written Python loops for every field.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
26_bulk_account_migration/
├── main.py
├── models.py
```

## What to pay attention to

- **ListDDM** — used as part of the actual workflow, not only imported for demonstration.
- **rename/copy/fill path** — used as part of the actual workflow, not only imported for demonstration.
- **typed subclasses** — used as part of the actual workflow, not only imported for demonstration.

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

The important unit here is the **collection**, not one record. Records stay DDM-compatible while transformations happen through `ListDDM`, `SetDDM`, `DictDDM`, `DDMTable` or `BatchPlan`. Path/numeric primitives avoid repeated Python-level traversal; arbitrary business logic can still be injected through callback operations when necessary.

For production migrations, separate transformation from persistence: validate the transformed collection, checkpoint it, then commit it to your database or file store in bounded chunks.

## Ways to extend this project

- Add a rollback snapshot using File.atomic_write_json.
- Use chunks() to hand batches to a database writer.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from YoungLion import DDM

class Profile(DDM):
    name: str
    country: str
    age: int
    def __init__(self, data):
        super().__init__(data)
        self.name = str(data.get("name", "Unknown"))
        self.country = str(data.get("country", "Unknown"))
        self.age = int(data.get("age", 0))

class User(DDM):
    id: int
    score: float
    active: bool
    profile: Profile
    def __init__(self, data):
        super().__init__(data)
        self.id = int(data.get("id", 0))
        self.score = float(data.get("score", 0))
        self.active = bool(data.get("active", True))
        self.profile = Profile(data.get("profile", {}))
```

### `main.py`

```python
from YoungLion import ListDDM
from models import User

users = ListDDM(User({"id": i, "score": i % 100, "active": True, "profile": {"name": f"User {i}", "country": "AZ" if i%2 else "US", "age": 18+i%40}, "legacy_rank": "member"}) for i in range(5000))
print("before columns:", users[0].to_dict())
users.rename_path("legacy_rank", "account.rank")
users.fill_missing("account.migrated", True)
users.copy_path("profile.country", "account.region")
print("after:", users[0].to_dict())
print("migrated:", users.count_path("account.migrated", True))
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

