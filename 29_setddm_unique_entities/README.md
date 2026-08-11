# 29 — SetDDM domain-key uniqueness

**Complexity:** Advanced  
**Focus:** SetDDM, key_path uniqueness, bulk mutation

## Scenario

Deduplicate mutable user-like objects by a stable domain key without making mutable DDM objects hashable by value.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
29_setddm_unique_entities/
├── main.py
├── models.py
```

## What to pay attention to

- **SetDDM** — used as part of the actual workflow, not only imported for demonstration.
- **key_path uniqueness** — used as part of the actual workflow, not only imported for demonstration.
- **bulk mutation** — used as part of the actual workflow, not only imported for demonstration.

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

- Use a compound callable key such as `(tenant_id, user_id)`.
- Handle key-field mutation deliberately and test duplicate detection.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from YoungLion import DDM
class Account(DDM):
    def __init__(self,data):
        super().__init__(data); self.id=int(data.get("id",0)); self.email=str(data.get("email","")); self.score=float(data.get("score",0))
```

### `main.py`

```python
from YoungLion import SetDDM
from models import Account

accounts = SetDDM(key_path="id")
for row in [{"id":1,"email":"a@test","score":10},{"id":2,"email":"b@test","score":20},{"id":1,"email":"duplicate@test","score":99}]:
    print("added", row["id"], accounts.add(Account(row)))
print("count:", len(accounts))
accounts.increment("score", 5)
print([a.to_dict() for a in accounts])
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

