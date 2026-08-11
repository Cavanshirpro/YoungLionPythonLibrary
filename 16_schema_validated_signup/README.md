# 16 — Schema-validated signup pipeline

**Complexity:** Intermediate  
**Focus:** SchemaDDM, typed DDM subclasses, validation boundary

## Scenario

Validate incoming registration dictionaries with `SchemaDDM`, then convert accepted data into a typed `User(DDM)` domain object. This shows how schema-driven validation and subclass-driven behavior can coexist.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
16_schema_validated_signup/
├── models.py
├── main.py
```

## What to pay attention to

- **SchemaDDM** — used as part of the actual workflow, not only imported for demonstration.
- **typed DDM subclasses** — used as part of the actual workflow, not only imported for demonstration.
- **validation boundary** — used as part of the actual workflow, not only imported for demonstration.

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

- Add stricter email/domain rules in the service layer.
- Store schema definitions in versioned configuration.
- Batch-validate imports before constructing domain models.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `models.py`

```python
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM, SchemaDDM

SIGNUP_SCHEMA = {
    "username": {"type": str, "required": True},
    "age": {"type": int, "required": True},
    "email": {"type": str, "required": True},
}

class User(DDM):
    username: str
    age: int
    email: str
    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.username = str(data.get("username", "")).strip()
        self.age = int(data.get("age", 0))
        self.email = str(data.get("email", "")).strip().casefold()
        if len(self.username) < 3: raise ValueError("username too short")

def validate_signup(data: dict) -> dict:
    result = SchemaDDM(data, SIGNUP_SCHEMA)
    return result.to_dict()
```

### `main.py`

```python
from models import User, validate_signup

raw = {"username": " Cavan ", "age": 18, "email": "CAVAN@example.test"}
validated = validate_signup(raw)
user = User(validated)
print(user.to_dict())
print(user.username, user.email)
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

