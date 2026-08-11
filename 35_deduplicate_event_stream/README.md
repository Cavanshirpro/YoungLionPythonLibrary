# 35 — Event stream deduplication

**Complexity:** Advanced  
**Focus:** deduplicate, stable path keys, ListDDM

## Scenario

Deduplicate records by a nested or explicit path while preserving the first full DDM object for each key.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
35_deduplicate_event_stream/
├── main.py
├── models.py
```

## What to pay attention to

- **deduplicate** — used as part of the actual workflow, not only imported for demonstration.
- **stable path keys** — used as part of the actual workflow, not only imported for demonstration.
- **ListDDM** — used as part of the actual workflow, not only imported for demonstration.

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

- Use SetDDM(key_path="event_id") for streaming insertion uniqueness.
- Persist duplicate counts for observability.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from YoungLion import DDM
class Event(DDM):
    def __init__(self,data):
        super().__init__(data); self.id=int(data.get("id",0)); self.event_id=str(data.get("event_id","")); self.type=str(data.get("type",""))
```

### `main.py`

```python
from YoungLion import ListDDM
from models import Event

rows = ListDDM(Event({"id":i,"event_id":f"evt-{i//2}","type":"click" if i%3 else "view"}) for i in range(100))
unique = rows.deduplicate("event_id")
print("before:", len(rows), "after:", len(unique))
print([e.event_id for e in unique[:8]])
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

