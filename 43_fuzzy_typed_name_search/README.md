# 43 — Fuzzy search over typed nested names

**Complexity:** Advanced  
**Focus:** DDM text index, fuzzy ranking, SearchResult scores

## Scenario

Keep exact/range indexes for structured fields but use the text side of a nested DDM path index when user-entered names contain typos.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
43_fuzzy_typed_name_search/
├── models.py
├── main.py
```

## What to pay attention to

- **DDM text index** — used as part of the actual workflow, not only imported for demonstration.
- **fuzzy ranking** — used as part of the actual workflow, not only imported for demonstration.
- **SearchResult scores** — used as part of the actual workflow, not only imported for demonstration.

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

- Tune min_score for your UI.
- Combine fuzzy name results with exact tenant/country filtering.

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
names=["Cavanshir Qurbanzade","Alice Johnson","Robert Stone","Alicia Keys","Catherine Green"]
users=ListDDM(User({"id":i,"username":n.split()[0].lower(),"profile":{"name":n,"age":20+i,"country":"AZ" if i==0 else "US","city":""}}) for i,n in enumerate(names))
engine=DDMSearchEngine(users).create_indexes("profile.name")
for q in ["Cavansir","Alcie","Robrt"]:
    hits=engine.text("profile.name",q,hits=True,limit=3)
    print(q,[(h.item.profile.name,round(h.score,3),h.algorithm) for h in hits])
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

