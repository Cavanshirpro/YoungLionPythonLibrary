# 51 — Aho-Corasick multi-pattern moderation

**Complexity:** Advanced  
**Focus:** MultiPatternSearch, Aho-Corasick, single-pass multi-keyword scan

## Scenario

Scan each message once against many phrases using MultiPatternSearch. This is useful for filters, keyword routing and rule engines.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
51_aho_corasick_moderation/
├── main.py
```

## What to pay attention to

- **MultiPatternSearch** — used as part of the actual workflow, not only imported for demonstration.
- **Aho-Corasick** — used as part of the actual workflow, not only imported for demonstration.
- **single-pass multi-keyword scan** — used as part of the actual workflow, not only imported for demonstration.

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

- Associate patterns with rule metadata.
- Normalize/segment input before matching based on your moderation policy.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `main.py`

```python
from YoungLion import MultiPatternSearch
patterns=["free money","credential leak","spam link","api key","secret token"]
matcher=MultiPatternSearch(patterns)
messages=["normal conversation","possible API key was pasted here","free money spam link now"]
for text in messages:
    matches=matcher.find(text)
    print(text,[(m.pattern,m.start,m.end) for m in matches])
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

