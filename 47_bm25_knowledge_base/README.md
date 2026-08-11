# 47 — BM25 knowledge base

**Complexity:** Advanced  
**Focus:** BM25Index, SearchDocument, ranked retrieval

## Scenario

Create a local article index where document-length-aware ranking matters more than simple substring matching.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
47_bm25_knowledge_base/
├── main.py
```

## What to pay attention to

- **BM25Index** — used as part of the actual workflow, not only imported for demonstration.
- **SearchDocument** — used as part of the actual workflow, not only imported for demonstration.
- **ranked retrieval** — used as part of the actual workflow, not only imported for demonstration.

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

- Load Markdown documents from disk.
- Store metadata fields for filters/facets.
- Compare BM25 and hybrid ranking on real queries.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `main.py`

```python
from YoungLion import BM25Index, SearchDocument
articles=[
    SearchDocument("ddm","DDM collections use native path operations for bulk structured data",fields={"topic":"data"}),
    SearchDocument("search","DDMSearchEngine builds reusable nested indexes and supports exact range and fuzzy text queries",fields={"topic":"search"}),
    SearchDocument("file","File provides atomic JSON text binary checksum backup and structured format helpers",fields={"topic":"file"}),
]
index=BM25Index(articles)
for result in index.search("nested DDM search index",limit=3):
    print(result.document.id, round(result.score,3), result.document.text)
print(index.stats())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

