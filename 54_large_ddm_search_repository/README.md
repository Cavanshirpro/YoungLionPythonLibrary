# 54 — Large DDM search repository

**Complexity:** Advanced  
**Focus:** repository abstraction, large indexed DDM data, exact+range+text search

## Scenario

Wrap DDMSearchEngine behind a repository API so the rest of an application does not know how indexes are built or refreshed.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
54_large_ddm_search_repository/
├── models.py
├── repository.py
├── main.py
```

## What to pay attention to

- **repository abstraction** — used as part of the actual workflow, not only imported for demonstration.
- **large indexed DDM data** — used as part of the actual workflow, not only imported for demonstration.
- **exact+range+text search** — used as part of the actual workflow, not only imported for demonstration.

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

- Persist a serialized dataset and rebuild indexes on startup.
- Measure memory per path index before indexing every possible field.

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

### `repository.py`

```python
from YoungLion import ListDDM, DDMSearchEngine
from models import User
class Repository:
    def __init__(self,rows):
        self.rows=ListDDM(User(r) for r in rows); self.engine=DDMSearchEngine(self.rows); self.engine.create_indexes("id","role","active","profile.name","profile.age","profile.country")
    def find_user(self,id): return self.engine.find_one("id",id)
    def admin_candidates(self,country): return self.engine.where(role="member",active=True,profile__country=country,profile__age__ge=18)
    def name_search(self,q): return self.engine.text("profile.name",q,limit=10)
```

### `main.py`

```python
from repository import Repository
rows=[{"id":i,"username":f"u{i}","role":"member","active":i%9!=0,"profile":{"name":f"Person {i}","age":15+i%50,"country":["AZ","US","DE"][i%3],"city":""}} for i in range(30000)]
r=Repository(rows)
print(r.find_user(27654).username)
print("candidates:",len(r.admin_candidates("AZ")))
print("fuzzy:",[u.id for u in r.name_search("Persn 321")[:3]])
print(r.engine.stats())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

