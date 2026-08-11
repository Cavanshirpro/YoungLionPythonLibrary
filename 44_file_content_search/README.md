# 44. Search local notes by content

## Scenario

Index text content inside files.

## Project structure

```text
44_file_content_search/
├── README.md
└── main.py
```

## YoungLion concepts

- `FileSearchEngine`
- `content=True`
- `extension filter`

## Run

```bash
cd 44_file_content_search
python main.py
```

## Walkthrough

1. `main.py` creates a small but realistic local data/problem setup.
2. It uses YoungLion through its public API rather than private implementation details.
3. The example prints the important result so behavior is visible immediately.
4. Files created by the example are written under its local `workspace/` directory where applicable.

## Why this pattern matters

Index text content inside files. The example is intentionally small enough to read in one sitting, but the same API is designed to scale into a larger application module.

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
from YoungLion import FileSearchEngine

root = Path(__file__).parent / "workspace"
root.mkdir(exist_ok=True)
(root / "network.md").write_text("Reverse proxy and TLS configuration guide", encoding="utf-8")
(root / "python.md").write_text("Python native extension build notes", encoding="utf-8")
engine = FileSearchEngine(root, content=True, extensions=[".md"])
print(engine.search("native extension"))
```

## Representative output

The following output was captured while validating this mini-project against the v0.1 source tree. Values such as timestamps, temporary paths, ordering, random samples or durations can differ between runs.

```text
['<example>/44_file_content_search/workspace/python.md']
```

## Adaptation checklist

- Replace the sample records/files with your application's own data model.
- Keep the public YoungLion calls shown above; avoid depending on private `_native` implementation details.
- Add domain validation and application-specific exception handling at trust boundaries.
- For large datasets, benchmark with realistic record counts and field cardinality before choosing indexes or packed representations.
- Add automated tests for the behavior your application depends on.
