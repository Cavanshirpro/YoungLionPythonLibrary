# 42 — Nested numeric range search

**Complexity:** Advanced  
**Focus:** numeric path index, range query, typed nested DDM

## Scenario

Use the sorted numeric side of a DDM path index for repeated age-band and threshold queries over typed nested profiles.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
42_nested_age_range_search/
├── models.py
├── main.py
```

## What to pay attention to

- **numeric path index** — used as part of the actual workflow, not only imported for demonstration.
- **range query** — used as part of the actual workflow, not only imported for demonstration.
- **typed nested DDM** — used as part of the actual workflow, not only imported for demonstration.

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

Search is treated as a **long-lived service/index**, not a helper that performs a fresh full scan for every query. Index build cost is paid when data is loaded or changed; repeated queries reuse exact/range/text/composite structures. User-facing text ranking and structured DDM path lookups are separate tools and can be combined when a UI needs both.

Do not index every field automatically. Index hot paths that are queried repeatedly, monitor memory, and refresh/invalidate indexes when source records change outside collection-owned mutation APIs.

## Ways to extend this project

- Index other numeric paths such as reputation/balance.
- Use engine.where() to combine range results with categorical indexes.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from YoungLion import DDM
class Profile(DDM):
    def __init__(self,data):
        super().__init__(data); self.name=str(data.get("name","Unknown")); self.age=int(data.get("age",0)); self.country=str(data.get("country","Unknown")); self.city=str(data.get("city",""))
class User(DDM):
    def __init__(self,data):
        super().__init__(data); self.id=int(data.get("id",0)); self.username=str(data.get("username","")); self.role=str(data.get("role","member")); self.active=bool(data.get("active",True)); self.profile=Profile(data.get("profile",{}))
```

### `main.py`

```python
from YoungLion import ListDDM, DDMSearchEngine
from models import User
users=ListDDM(User({"id":i,"username":f"u{i}","profile":{"name":f"N{i}","age":10+i%70,"country":"AZ","city":"Baku"}}) for i in range(20000))
engine=DDMSearchEngine(users).create_indexes("profile.age")
for low,high in [(18,25),(26,40),(41,65)]:
    rows=engine.between("profile.age",low,high)
    print((low,high),len(rows),rows[0].profile.age if rows else None)
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

