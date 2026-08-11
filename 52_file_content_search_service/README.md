# 52 — File name/content search service

**Complexity:** Advanced  
**Focus:** FileSearchEngine, local content search, ranked results

## Scenario

Create temporary local documents and use FileSearchEngine as the backend for a small developer-document finder.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
52_file_content_search_service/
├── main.py
```

## What to pay attention to

- **FileSearchEngine** — used as part of the actual workflow, not only imported for demonstration.
- **local content search** — used as part of the actual workflow, not only imported for demonstration.
- **ranked results** — used as part of the actual workflow, not only imported for demonstration.

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

- Restrict indexed extensions.
- Rebuild or incrementally update after file changes.
- Store path metadata for UI previews.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `main.py`

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from YoungLion import FileSearchEngine
with TemporaryDirectory() as tmp:
    root=Path(tmp)
    (root/"ddm.md").write_text("DDM nested path indexes and batch operations",encoding="utf-8")
    (root/"release.txt").write_text("wheel build artifact release bundle",encoding="utf-8")
    (root/"notes.log").write_text("ordinary log entry",encoding="utf-8")
    engine=FileSearchEngine(root,content=True,extensions=[".md",".txt",".log"])
    for result in engine.search_results("nested index",limit=10):
        print(result.document.metadata["path"],round(result.score,3))
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

