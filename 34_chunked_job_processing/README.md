# 34 — Chunked batch job processing

**Complexity:** Advanced  
**Focus:** chunks, batch operations, bounded processing

## Scenario

Process a large collection in bounded chunks so downstream persistence or APIs can control memory/transaction size while the in-memory model remains typed.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
34_chunked_job_processing/
├── main.py
├── models.py
```

## What to pay attention to

- **chunks** — used as part of the actual workflow, not only imported for demonstration.
- **batch operations** — used as part of the actual workflow, not only imported for demonstration.
- **bounded processing** — used as part of the actual workflow, not only imported for demonstration.

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

- Write each chunk in one database transaction.
- Pair with RateLimiter when chunks feed an API.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from YoungLion import DDM
class Job(DDM):
    def __init__(self,data):
        super().__init__(data); self.id=int(data.get("id",0)); self.state=str(data.get("state","queued")); self.attempts=int(data.get("attempts",0))
```

### `main.py`

```python
from YoungLion import ListDDM
from models import Job

jobs = ListDDM(Job({"id":i,"state":"queued","attempts":0}) for i in range(10000))
processed=0
for chunk in jobs.chunks(750):
    batch = ListDDM(chunk)
    batch.set_all("state","processed")
    batch.increment("attempts",1)
    processed += len(batch)
print("processed:", processed, "states:", jobs.count_by("state"), "attempts:", jobs.sum("attempts"))
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

