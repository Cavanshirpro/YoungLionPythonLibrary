# 41 — Indexed typed user directory

**Complexity:** Advanced  
**Focus:** typed nested DDM, DDMSearchEngine, reusable exact/range indexes

## Scenario

Build a repository-like user directory where nested typed `User.profile` fields are exact-indexed and reused across many queries.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
41_indexed_user_directory/
├── models.py
├── directory.py
├── main.py
```

## What to pay attention to

- **typed nested DDM** — used as part of the actual workflow, not only imported for demonstration.
- **DDMSearchEngine** — used as part of the actual workflow, not only imported for demonstration.
- **reusable exact/range indexes** — used as part of the actual workflow, not only imported for demonstration.

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

- Add composite role+country indexes.
- Benchmark index build cost separately from query throughput.

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

### `directory.py`

```python
from YoungLion import ListDDM, DDMSearchEngine
from models import User
class UserDirectory:
    def __init__(self,rows):
        self.users=ListDDM(User(x) for x in rows)
        self.engine=self.users.indexed("id","username","role","profile.country","profile.age")
    def username(self,value): return self.engine.find_one("username",value)
    def country(self,value): return self.engine.find("profile.country",value)
    def adults(self): return self.engine.find("profile.age",18,op="ge")
```

### `main.py`

```python
from directory import UserDirectory
rows=[{"id":i,"username":f"user{i}","role":"admin" if i%50==0 else "member","active":True,"profile":{"name":f"User {i}","age":15+i%50,"country":["AZ","US","DE"][i%3],"city":"Baku" if i%3==0 else ""}} for i in range(10000)]
d=UserDirectory(rows)
print("lookup:",d.username("user7345").profile.to_dict())
print("AZ:",len(d.country("AZ")),"adults:",len(d.adults()))
print(d.engine.stats())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

