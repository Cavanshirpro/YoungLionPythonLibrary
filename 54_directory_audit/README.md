# 54. Directory audit report

## Scenario

Discover files and calculate metadata/checksums.

## Project structure

```text
54_directory_audit/
├── README.md
└── main.py
```

## YoungLion concepts

- `find_files`
- `get_info`
- `directory_size`

## Run

```bash
cd 54_directory_audit
python main.py
```

## Walkthrough

1. `main.py` creates a small but realistic local data/problem setup.
2. It uses YoungLion through its public API rather than private implementation details.
3. The example prints the important result so behavior is visible immediately.
4. Files created by the example are written under its local `workspace/` directory where applicable.

## Why this pattern matters

Discover files and calculate metadata/checksums. The example is intentionally small enough to read in one sitting, but the same API is designed to scale into a larger application module.

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
from YoungLion import File

root = Path(__file__).parent / "workspace"
f = File(str(root))
f.txt_write_str("logs/a.log", "hello")
f.txt_write_str("logs/b.log", "world")
for path in f.find_files("*.log", recursive=True):
    print(path, f.get_info(path).get("size"), f.checksum(path)[:12])
print("Directory bytes:", f.directory_size())
```

## Representative output

The following output was captured while validating this mini-project against the v0.1 source tree. Values such as timestamps, temporary paths, ordering, random samples or durations can differ between runs.

```text
<example>/54_directory_audit/workspace/logs/b.log 5 486ea46224d1
<example>/54_directory_audit/workspace/logs/a.log 5 2cf24dba5fb0
Directory bytes: 10
```

## Adaptation checklist

- Replace the sample records/files with your application's own data model.
- Keep the public YoungLion calls shown above; avoid depending on private `_native` implementation details.
- Add domain validation and application-specific exception handling at trust boundaries.
- For large datasets, benchmark with realistic record counts and field cardinality before choosing indexes or packed representations.
- Add automated tests for the behavior your application depends on.
