# 70. Local knowledge-base mini app

## Scenario

Combine file content indexing, text analysis, cache and application search into a local knowledge tool.

## Project structure

```text
70_local_knowledge_base/
├── README.md
└── main.py
```

## YoungLion concepts

- `FileSearchEngine`
- `ApplicationSearch`
- `TTLCache`
- `TextProcessor`

## Run

```bash
cd 70_local_knowledge_base
python main.py
```

## Walkthrough

1. `main.py` creates a small but realistic local data/problem setup.
2. It uses YoungLion through its public API rather than private implementation details.
3. The example prints the important result so behavior is visible immediately.
4. Files created by the example are written under its local `workspace/` directory where applicable.

## Why this pattern matters

Combine file content indexing, text analysis, cache and application search into a local knowledge tool. The example is intentionally small enough to read in one sitting, but the same API is designed to scale into a larger application module.

## Production extensions

- Replace the small in-memory sample with application data.
- Add tests around the public API used by this example.
- Add domain-specific validation/error handling before production use.

## Notes

- No real credentials are embedded.
- The example is designed for YoungLion 0.1.0 / CPython 3.10+.
- For performance-sensitive code, benchmark with data shaped like your actual workload.

## Full example code

```python
from pathlib import Path
from YoungLion import FileSearchEngine, ApplicationSearch, TTLCache, TextProcessor

root = Path(__file__).parent / "workspace" / "notes"
root.mkdir(parents=True, exist_ok=True)
(root / "native.md").write_text("YoungLion uses a C++ native extension for hot paths.", encoding="utf-8")
(root / "search.md").write_text("DDMSearchEngine indexes nested paths such as profile.name.", encoding="utf-8")

file_index = FileSearchEngine(root, content=True)
paths = file_index.search("nested path")
print("Matching files:", paths)

app = ApplicationSearch()
for i, path in enumerate(root.glob("*.md"), 1):
    text = path.read_text(encoding="utf-8")
    app.add(i, path.stem, text, payload=str(path))
print("Ranked:", app.search("native hot path"))

cache = TTLCache(default_ttl=60)
summary = TextProcessor((root / "native.md").read_text()).summarize(1)
cache.set("native-summary", summary)
print("Cached summary:", cache.get("native-summary"))
```

## Representative output

The following output was captured while validating this mini-project against the v0.1 source tree. Values such as timestamps, temporary paths, ordering, random samples or durations can differ between runs.

```text
Matching files: ['<example>/70_local_knowledge_base/workspace/notes/search.md', '<example>/70_local_knowledge_base/workspace/notes/native.md']
Ranked: ['<example>/70_local_knowledge_base/workspace/notes/native.md', '<example>/70_local_knowledge_base/workspace/notes/search.md']
Cached summary: YoungLion uses a C++ native extension for hot paths.
```

## Adaptation checklist

- Replace the sample records/files with your application's own data model.
- Keep the public YoungLion calls shown above; avoid depending on private `_native` implementation details.
- Add domain validation and application-specific exception handling at trust boundaries.
- For large datasets, benchmark with realistic record counts and field cardinality before choosing indexes or packed representations.
- Add automated tests for the behavior your application depends on.
