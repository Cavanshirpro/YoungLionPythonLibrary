# 23 — DDMBuilder request assembly

**Complexity:** Intermediate  
**Focus:** DDMBuilder, progressive construction, nested data

## Scenario

Construct a nested API/job request progressively, keeping the code readable when values come from several independent subsystems.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
23_ddm_builder_request/
├── main.py
```

## What to pay attention to

- **DDMBuilder** — used as part of the actual workflow, not only imported for demonstration.
- **progressive construction** — used as part of the actual workflow, not only imported for demonstration.
- **nested data** — used as part of the actual workflow, not only imported for demonstration.

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

- Wrap builder creation in an application-specific factory.
- Validate the result before sending it to an external boundary.
- Use a typed DDM subclass after construction.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `main.py`

```python
from YoungLion import DDMBuilder

request = (
    DDMBuilder()
    .set("id", "job-42")
    .nest("profile", lambda b: b.set("name", "Cavan").set("country", "AZ"))
    .nest("options", lambda b: b.set("priority", 5).set("dry_run", True))
    .build()
)
print(request.to_json())
print("country:", request.get_path("profile.country"))
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

