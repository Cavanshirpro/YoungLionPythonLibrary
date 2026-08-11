# 55 — Hybrid admin search service

**Complexity:** Advanced  
**Focus:** ApplicationSearch, DDMSearchEngine, result intersection, typed models

## Scenario

Combine application-facing text search with structured DDM indexes to implement an admin UI that can search text then constrain results by status/country.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
55_hybrid_admin_search/
├── models.py
├── service.py
├── main.py
```

## What to pay attention to

- **ApplicationSearch** — used as part of the actual workflow, not only imported for demonstration.
- **DDMSearchEngine** — used as part of the actual workflow, not only imported for demonstration.
- **result intersection** — used as part of the actual workflow, not only imported for demonstration.
- **typed models** — used as part of the actual workflow, not only imported for demonstration.

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

- Move candidate intersection into a reusable service abstraction.
- Expose facets from the text index.

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

### `service.py`

```python
from YoungLion import ListDDM, DDMSearchEngine, ApplicationSearch
from models import User
class AdminSearch:
    def __init__(self,rows):
        self.users=ListDDM(User(r) for r in rows); self.paths=DDMSearchEngine(self.users).create_indexes("id","active","role","profile.country"); self.text=ApplicationSearch()
        for u in self.users: self.text.add(u.id,title=f"{u.profile.name} @{u.username}",body=f"{u.role} {u.profile.country}",fields={"role":u.role,"country":u.profile.country},payload=u)
    def query(self,text,country=None,active=None):
        candidates=self.text.search(text,limit=50); allowed={id(x) for x in candidates}
        if country is not None: allowed &= {id(x) for x in self.paths.find("profile.country",country)}
        if active is not None: allowed &= {id(x) for x in self.paths.find("active",active)}
        return [u for u in candidates if id(u) in allowed]
```

### `main.py`

```python
from service import AdminSearch
rows=[{"id":i,"username":f"user{i}","role":"admin" if i%100==0 else "member","active":i%7!=0,"profile":{"name":f"Cavan {i}" if i%50==0 else f"Person {i}","age":18+i%40,"country":"AZ" if i%3==0 else "US","city":""}} for i in range(5000)]
s=AdminSearch(rows)
print([(u.id,u.username,u.profile.country) for u in s.query("cavn",country="AZ",active=True)[:10]])
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

