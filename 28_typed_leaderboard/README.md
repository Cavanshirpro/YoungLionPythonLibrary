# 28 — Typed player leaderboard and nth selection

**Complexity:** Advanced  
**Focus:** ListDDM, stable sort, nth/top selection

## Scenario

Build a leaderboard from typed player models, use native path sorting/nth selection, and keep full domain objects in the results.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
28_typed_leaderboard/
├── main.py
├── models.py
```

## What to pay attention to

- **ListDDM** — used as part of the actual workflow, not only imported for demonstration.
- **stable sort** — used as part of the actual workflow, not only imported for demonstration.
- **nth/top selection** — used as part of the actual workflow, not only imported for demonstration.

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

- Add composite ranking rules.
- Persist only the top-N leaderboard snapshot.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from YoungLion import DDM
class Player(DDM):
    def __init__(self,data):
        super().__init__(data); self.id=int(data.get("id",0)); self.name=str(data.get("name","")); self.score=float(data.get("score",0)); self.team=str(data.get("team","solo"))
```

### `main.py`

```python
from YoungLion import ListDDM
from models import Player

players = ListDDM(Player({"id":i,"name":f"P{i}","score":(i*37)%1000,"team":"lion" if i%3==0 else "wolf"}) for i in range(1000))
players.sort_by("score", reverse=True, inplace=True)
print("top 5:", [(p.name,p.score) for p in players.take(5)])
median_score = players.nth("score", len(players)//2)
print("median candidate:", median_score)
print("lion top:", [(p.name,p.score) for p in ListDDM(players.filter_path("team","lion")).top("score",5)])
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

