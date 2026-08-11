# 32 — Bulk nested DDM callback normalization

**Complexity:** Advanced  
**Focus:** apply_path, typed nested DDM, callback batch

## Scenario

Apply a real Python domain function to `profile` across a typed DDM collection while YoungLion owns the nested-path traversal/write-back loop.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
32_bulk_nested_profile_normalization/
├── main.py
├── models.py
```

## What to pay attention to

- **apply_path** — used as part of the actual workflow, not only imported for demonstration.
- **typed nested DDM** — used as part of the actual workflow, not only imported for demonstration.
- **callback batch** — used as part of the actual workflow, not only imported for demonstration.

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

- Return a replacement Profile when immutable normalization is desired.
- Prefer native set/numeric operations when no Python callback is necessary.

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
from models import User, Profile

users = ListDDM(User({"id":i,"score":i,"active":True,"profile":{"name":f"  User {i}  ","country":"az" if i%2 else "US","age":18+i%10}}) for i in range(1000))
def normalize(profile: Profile) -> Profile:
    profile.name = profile.name.strip()
    profile.country = profile.country.upper()
    return profile

updated = users.apply_path("profile", normalize)
print("updated:", len(updated))
print(users[1].profile.to_dict())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

