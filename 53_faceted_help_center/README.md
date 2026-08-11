# 53 — Faceted help-center backend

**Complexity:** Advanced  
**Focus:** ApplicationSearch, facets, help-center search

## Scenario

Combine ranked article search with facet counts so a UI can display categories alongside search results.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
53_faceted_help_center/
├── main.py
```

## What to pay attention to

- **ApplicationSearch** — used as part of the actual workflow, not only imported for demonstration.
- **facets** — used as part of the actual workflow, not only imported for demonstration.
- **help-center search** — used as part of the actual workflow, not only imported for demonstration.

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

- Add tags/language fields.
- Use SearchQuery filters for UI-selected facets.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `main.py`

```python
from YoungLion import ApplicationSearch
articles=[("install","Installing YoungLion","Build from PyPI or source with a C++17 compiler","setup"),("ddm","Modeling data with DDM","Typed subclasses nested models and dynamic fields","data"),("search","Searching DDM collections","Exact range fuzzy and composite indexes","search"),("files","Working with File","Atomic JSON backups checksums and formats","files")]
app=ApplicationSearch()
for id,title,body,cat in articles: app.add(id,title=title,body=body,fields={"category":cat},payload={"id":id,"title":title,"category":cat})
print(app.search("nested model"))
print("all facets:",app.facet("category"))
print("query facets:",app.facet("category",query="search index"))
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

