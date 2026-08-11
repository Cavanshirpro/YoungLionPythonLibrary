# 48. INI desktop settings

## Scenario

Read and update classic INI configuration.

## Project structure

```text
48_ini_desktop_settings/
├── README.md
└── main.py
```

## YoungLion concepts

- `INI`
- `configuration`
- `append/update`

## Run

```bash
cd 48_ini_desktop_settings
python main.py
```

## Walkthrough

1. `main.py` creates a small but realistic local data/problem setup.
2. It uses YoungLion through its public API rather than private implementation details.
3. The example prints the important result so behavior is visible immediately.
4. Files created by the example are written under its local `workspace/` directory where applicable.

## Why this pattern matters

Read and update classic INI configuration. The example is intentionally small enough to read in one sitting, but the same API is designed to scale into a larger application module.

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
f.ini_write("app.ini", {"ui": {"theme": "dark", "scale": "1.25"}, "network": {"timeout": "20"}})
print(f.ini_read("app.ini"))
```

## Representative output

The following output was captured while validating this mini-project against the v0.1 source tree. Values such as timestamps, temporary paths, ordering, random samples or durations can differ between runs.

```text
{'ui': {'theme': 'dark', 'scale': '1.25'}, 'network': {'timeout': '20'}}
```

## Adaptation checklist

- Replace the sample records/files with your application's own data model.
- Keep the public YoungLion calls shown above; avoid depending on private `_native` implementation details.
- Add domain validation and application-specific exception handling at trust boundaries.
- For large datasets, benchmark with realistic record counts and field cardinality before choosing indexes or packed representations.
- Add automated tests for the behavior your application depends on.
