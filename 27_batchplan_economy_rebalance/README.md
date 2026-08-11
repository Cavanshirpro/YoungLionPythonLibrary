# 27 — Single-pass economy rebalance with BatchPlan

**Complexity:** Advanced  
**Focus:** BatchPlan, numeric reductions, large ListDDM

## Scenario

Apply several numeric changes to a large player economy in one outer native traversal, then compute aggregate checks before accepting the rebalance.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
27_batchplan_economy_rebalance/
├── main.py
├── models.py
```

## What to pay attention to

- **BatchPlan** — used as part of the actual workflow, not only imported for demonstration.
- **numeric reductions** — used as part of the actual workflow, not only imported for demonstration.
- **large ListDDM** — used as part of the actual workflow, not only imported for demonstration.

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

- Compare separate passes vs BatchPlan in your own workload.
- Add invariants before committing the transformed dataset.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from YoungLion import DDM
class Player(DDM):
    def __init__(self,data):
        super().__init__(data); self.id=int(data.get("id",0)); self.wallet=float(data.get("wallet",0)); self.reputation=int(data.get("reputation",0)); self.active=bool(data.get("active",True))
```

### `main.py`

```python
from YoungLion import ListDDM
from models import Player

players = ListDDM(Player({"id": i, "wallet": 100 + i%500, "reputation": i%120, "active": i%7 != 0}) for i in range(10000))
before = players.sum("wallet")
plan = players.batch().multiply("wallet", 1.03).add("wallet", 15).clamp("wallet", 0, 2000).set("economy_version", 2)
changed = plan.execute(players)
after = players.sum("wallet")
print({"changed": changed, "before": round(before,2), "after": round(after,2), "mean": round(players.mean("wallet") or 0,2)})
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

