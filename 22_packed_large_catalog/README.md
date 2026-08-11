# 22 — PackedDDM read-heavy catalog

**Complexity:** Advanced  
**Focus:** PackedDDM, memory-oriented records, read-heavy datasets

## Scenario

Load many compact read-heavy records and compare the modeling tradeoff with regular DDM objects. The example focuses on lower object overhead rather than rich per-record behavior.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
22_packed_large_catalog/
├── main.py
```

## What to pay attention to

- **PackedDDM** — used as part of the actual workflow, not only imported for demonstration.
- **memory-oriented records** — used as part of the actual workflow, not only imported for demonstration.
- **read-heavy datasets** — used as part of the actual workflow, not only imported for demonstration.

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

- Benchmark a representative dataset against DDM.
- Convert selected records to richer domain subclasses when behavior is needed.
- Index the packed records with DDMSearchEngine.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `main.py`

```python
from YoungLion import PackedDDM

rows = [PackedDDM({"id": i, "sku": f"SKU-{i:06d}", "price": (i % 200) + 0.99}) for i in range(10000)]
print("records:", len(rows))
print("sample:", rows[4321].to_dict())
print("sample memory:", rows[4321].memory_info())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

