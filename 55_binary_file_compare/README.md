# 55. Binary artifact comparison

## Scenario

Write binary blobs and compare exact contents.

## Project structure

```text
55_binary_file_compare/
├── README.md
└── main.py
```

## YoungLion concepts

- `binary I/O`
- `compare_files`
- `CRC/checksum`

## Run

```bash
cd 55_binary_file_compare
python main.py
```

## Walkthrough

1. `main.py` creates a small but realistic local data/problem setup.
2. It uses YoungLion through its public API rather than private implementation details.
3. The example prints the important result so behavior is visible immediately.
4. Files created by the example are written under its local `workspace/` directory where applicable.

## Why this pattern matters

Write binary blobs and compare exact contents. The example is intentionally small enough to read in one sitting, but the same API is designed to scale into a larger application module.

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

f = File(str(Path(__file__).parent / "workspace"))
payload = bytes([0, 1]) + b"YoungLion" + bytes([255])
f.write_bytes("a.bin", payload)
f.write_bytes("b.bin", payload)
print("Equal:", f.compare_files("a.bin", "b.bin"))
print("SHA256:", f.checksum("a.bin"))
```

## Representative output

The following output was captured while validating this mini-project against the v0.1 source tree. Values such as timestamps, temporary paths, ordering, random samples or durations can differ between runs.

```text
Equal: True
SHA256: 39343426f8a81230c304e13a6536f69fe4c4745ab9d083922d2a7abd2e5dc23a
```

## Adaptation checklist

- Replace the sample records/files with your application's own data model.
- Keep the public YoungLion calls shown above; avoid depending on private `_native` implementation details.
- Add domain validation and application-specific exception handling at trust boundaries.
- For large datasets, benchmark with realistic record counts and field cardinality before choosing indexes or packed representations.
- Add automated tests for the behavior your application depends on.
