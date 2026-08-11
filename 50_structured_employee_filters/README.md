# 50 — Structured employee filters

**Complexity:** Advanced  
**Focus:** StructuredSearch, mapping filters, non-text search

## Scenario

Filter records by several exact/numeric criteria without building a user-facing text index.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
50_structured_employee_filters/
├── main.py
```

## What to pay attention to

- **StructuredSearch** — used as part of the actual workflow, not only imported for demonstration.
- **mapping filters** — used as part of the actual workflow, not only imported for demonstration.
- **non-text search** — used as part of the actual workflow, not only imported for demonstration.

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

- For repeated large-data queries, graduate to DDMSearchEngine indexes.
- Normalize enums/casing at ingestion.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `main.py`

```python
from YoungLion import StructuredSearch
rows=[
 {"id":1,"name":"Alice","department":"engineering","age":30,"active":True},
 {"id":2,"name":"Cavan","department":"engineering","age":18,"active":True},
 {"id":3,"name":"Bob","department":"sales","age":44,"active":False},
]
search=StructuredSearch(rows, field_weights={"name":2.0,"department":1.5})
results=search.search("engineering", filters={"department":"engineering","active":True}, limit=10)
print([r.document.metadata["record"] for r in results])
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

