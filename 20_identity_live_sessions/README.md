# 20 — IdentityDDM live session registry

**Complexity:** Intermediate  
**Focus:** IdentityDDM, identity hashing, mutable session state

## Scenario

Model mutable live sessions that may have equal values but still represent distinct in-memory identities. This is a case where value hashing would be incorrect.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
20_identity_live_sessions/
├── models.py
├── main.py
```

## What to pay attention to

- **IdentityDDM** — used as part of the actual workflow, not only imported for demonstration.
- **identity hashing** — used as part of the actual workflow, not only imported for demonstration.
- **mutable session state** — used as part of the actual workflow, not only imported for demonstration.

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

This project isolates one specialized DDM/model capability and demonstrates the tradeoff that justifies it. Variants are not intended to replace normal `DDM` everywhere: choose them when immutability, identity hashing, lazy computation, defaults, validation, zero-copy views or memory density materially change the problem.

Keep the specialized boundary explicit. Convert to a richer typed domain subclass when domain behavior becomes more important than the storage/semantic specialization.

## Ways to extend this project

- Store sessions by explicit token in DictDDM.
- Use SetDDM(key_path=...) when uniqueness is domain-key based.
- Emit close events through EventBus.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from YoungLion import IdentityDDM

class Session(IdentityDDM):
    def __init__(self, data):
        super().__init__(data)
        self.user_id = int(data.get("user_id", 0))
        self.state = str(data.get("state", "active"))
    def close(self): self.state = "closed"
```

### `main.py`

```python
from models import Session

a = Session({"user_id": 1, "state": "active"})
b = Session({"user_id": 1, "state": "active"})
sessions = {a, b}
print("distinct live objects:", len(sessions))
a.close()
print(a.state, b.state)
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

