# 46. Crash-resistant JSON configuration

## Scenario

Persist settings with an atomic replacement workflow.

## Project structure

```text
46_atomic_json_configuration/
├── README.md
└── main.py
```

## YoungLion concepts

- `File`
- `atomic_write_json`
- `json_read`

## Run

```bash
cd 46_atomic_json_configuration
python main.py
```

## Walkthrough

1. `main.py` creates a small but realistic local data/problem setup.
2. It uses YoungLion through its public API rather than private implementation details.
3. The example prints the important result so behavior is visible immediately.
4. Files created by the example are written under its local `workspace/` directory where applicable.

## Why this pattern matters

Persist settings with an atomic replacement workflow. The example is intentionally small enough to read in one sitting, but the same API is designed to scale into a larger application module.

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
f.atomic_write_json("config.json", {"theme": "dark", "workers": 4})
print(f.json_read("config.json"))
print("SHA256:", f.checksum("config.json"))
```

## Representative output

The following output was captured while validating this mini-project against the v0.1 source tree. Values such as timestamps, temporary paths, ordering, random samples or durations can differ between runs.

```text
{'theme': 'dark', 'workers': 4}
SHA256: 4727955abf8124f4dcdf354e52ac4ebdf34fe2a5c05d6f86efe7fe29453eb8e3
```

## Adaptation checklist

- Replace the sample records/files with your application's own data model.
- Keep the public YoungLion calls shown above; avoid depending on private `_native` implementation details.
- Add domain validation and application-specific exception handling at trust boundaries.
- For large datasets, benchmark with realistic record counts and field cardinality before choosing indexes or packed representations.
- Add automated tests for the behavior your application depends on.
