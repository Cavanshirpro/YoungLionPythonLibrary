# 45 — Application command palette backend

**Complexity:** Advanced  
**Focus:** ApplicationSearch, autocomplete, facets, payload routing

## Scenario

Build a command palette that supports typo-tolerant search, weighted autocomplete payloads, categories and routes.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
45_application_command_palette/
├── commands.py
├── main.py
```

## What to pay attention to

- **ApplicationSearch** — used as part of the actual workflow, not only imported for demonstration.
- **autocomplete** — used as part of the actual workflow, not only imported for demonstration.
- **facets** — used as part of the actual workflow, not only imported for demonstration.
- **payload routing** — used as part of the actual workflow, not only imported for demonstration.

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

- Add usage-frequency weights to suggestions.
- Filter commands by permissions before returning payloads.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `commands.py`

```python
COMMANDS=[
    {"id":"settings.general","title":"General Settings","body":"Language startup theme interface preferences","category":"settings","route":"/settings/general"},
    {"id":"settings.account","title":"Account & Profile","body":"Username avatar privacy account","category":"settings","route":"/settings/account"},
    {"id":"project.open","title":"Open Project","body":"Open a recent project or workspace","category":"project","route":"/open"},
    {"id":"search.files","title":"Search Files","body":"Find files by name and content","category":"search","route":"/search/files"},
]
```

### `main.py`

```python
from YoungLion import ApplicationSearch
from commands import COMMANDS
engine=ApplicationSearch()
for c in COMMANDS:
    engine.add(c["id"],title=c["title"],body=c["body"],fields={"category":c["category"]},payload=c)
for q in ["setings","profil","find file"]:
    print(q,[r["title"] for r in engine.search(q,limit=3)])
print("suggest:",[x.term for x in engine.suggest("gen")])
print("facets:",engine.facet("category"))
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

