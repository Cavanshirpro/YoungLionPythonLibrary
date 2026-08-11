# 52. Backup with integrity check

## Scenario

Create a backup and compare checksums.

## Project structure

```text
52_backup_and_checksum/
├── README.md
└── main.py
```

## YoungLion concepts

- `backup`
- `checksum`
- `compare_files`

## Run

```bash
cd 52_backup_and_checksum
python main.py
```

## Walkthrough

1. `main.py` creates a small but realistic local data/problem setup.
2. It uses YoungLion through its public API rather than private implementation details.
3. The example prints the important result so behavior is visible immediately.
4. Files created by the example are written under its local `workspace/` directory where applicable.

## Why this pattern matters

Create a backup and compare checksums. The example is intentionally small enough to read in one sitting, but the same API is designed to scale into a larger application module.

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
f.txt_write_str("important.txt", "critical local state\n")
backup = f.backup("important.txt")
print("Backup:", backup)
print("Original SHA:", f.checksum("important.txt"))
print("Same bytes:", f.compare_files("important.txt", backup))
```

## Representative output

The following output was captured while validating this mini-project against the v0.1 source tree. Values such as timestamps, temporary paths, ordering, random samples or durations can differ between runs.

```text
Backup: <example>/52_backup_and_checksum/workspace/important.txt.20260810-221519.bak
Original SHA: 2de000ffd8ff0544a31f44db1a3cc1fcb8ee32f60386f953affcb4a59994d826
Same bytes: True
```

## Adaptation checklist

- Replace the sample records/files with your application's own data model.
- Keep the public YoungLion calls shown above; avoid depending on private `_native` implementation details.
- Add domain validation and application-specific exception handling at trust boundaries.
- For large datasets, benchmark with realistic record counts and field cardinality before choosing indexes or packed representations.
- Add automated tests for the behavior your application depends on.
