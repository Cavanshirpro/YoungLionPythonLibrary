# 30 — DictDDM keyed service registry

**Complexity:** Advanced  
**Focus:** DictDDM, application keys, owned indexes

## Scenario

Keep stable application keys outside the records while still applying path operations across every DDM value.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
30_dictddm_service_registry/
├── main.py
├── models.py
```

## What to pay attention to

- **DictDDM** — used as part of the actual workflow, not only imported for demonstration.
- **application keys** — used as part of the actual workflow, not only imported for demonstration.
- **owned indexes** — used as part of the actual workflow, not only imported for demonstration.

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

- Use service IDs as stable keys.
- Emit status changes through EventBus.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from YoungLion import DDM
class Service(DDM):
    def __init__(self,data):
        super().__init__(data); self.name=str(data.get("name","")); self.status=str(data.get("status","unknown")); self.latency_ms=float(data.get("latency_ms",0))
```

### `main.py`

```python
from YoungLion import DictDDM
from models import Service

services = DictDDM({
    "auth": Service({"name":"Auth","status":"healthy","latency_ms":18}),
    "search": Service({"name":"Search","status":"healthy","latency_ms":42}),
    "media": Service({"name":"Media","status":"degraded","latency_ms":180}),
})
print("degraded keys:", services.keys_for("status","degraded"))
services.multiply("latency_ms", 1.05)
engine = services.indexed("status","latency_ms")
print("slow:", [s.name for s in engine.find("latency_ms",100,op="gt")])
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

