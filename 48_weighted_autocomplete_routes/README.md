# 48 — Weighted autocomplete for routes/actions

**Complexity:** Advanced  
**Focus:** AutocompleteIndex, weighted prefix search, fuzzy fallback

## Scenario

Create a reusable prefix index for a UI where frequently used actions should rank above less important but lexically similar terms.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
48_weighted_autocomplete_routes/
├── main.py
```

## What to pay attention to

- **AutocompleteIndex** — used as part of the actual workflow, not only imported for demonstration.
- **weighted prefix search** — used as part of the actual workflow, not only imported for demonstration.
- **fuzzy fallback** — used as part of the actual workflow, not only imported for demonstration.

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

- Feed usage counts into weights.
- Store command IDs as payloads instead of executing from the index.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `main.py`

```python
from YoungLion import AutocompleteIndex, AutocompleteEntry
index=AutocompleteIndex([
    AutocompleteEntry("Open Project", {"route":"/open"}, 10),
    AutocompleteEntry("Open Recent", {"route":"/recent"}, 8),
    AutocompleteEntry("Open Settings", {"route":"/settings"}, 4),
    AutocompleteEntry("Optimize Database", {"route":"/db/optimize"}, 3),
])
for prefix in ["op","open p","optmize"]:
    print(prefix,[(x.term,x.weight,x.payload) for x in index.suggest(prefix,limit=4,min_score=0.5)])
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

