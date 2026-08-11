# 49 — Numeric range and nearest price search

**Complexity:** Advanced  
**Focus:** NumericSearch, range lookup, nearest lookup

## Scenario

Use NumericSearch as a compact standalone numeric index when you do not need a full DDM path engine.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
49_numeric_price_index/
├── main.py
```

## What to pay attention to

- **NumericSearch** — used as part of the actual workflow, not only imported for demonstration.
- **range lookup** — used as part of the actual workflow, not only imported for demonstration.
- **nearest lookup** — used as part of the actual workflow, not only imported for demonstration.

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

Search is treated as a **long-lived service/index**, not a helper that performs a fresh full scan for every query. Index build cost is paid when data is loaded or changed; repeated queries reuse exact/range/text/composite structures. User-facing text ranking and structured DDM path lookups are separate tools and can be combined when a UI needs both.

Do not index every field automatically. Index hot paths that are queried repeatedly, monitor memory, and refresh/invalidate indexes when source records change outside collection-owned mutation APIs.

## Ways to extend this project

- Use DDMSearchEngine when the numeric value is only one field of a richer record.
- Maintain a new index after mutating source values.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `main.py`

```python
from YoungLion import NumericSearch
products=[(1299,{"id":1,"name":"Laptop"}),(49,{"id":2,"name":"Mouse"}),(99,{"id":3,"name":"Keyboard"}),(799,{"id":4,"name":"Office Laptop"})]
idx=NumericSearch(products)
print("range:",idx.range(50,900))
print("nearest:",idx.nearest(750,k=2))
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

