# 04. Frozen permission cache key

## Scenario

Use immutable DDM values as stable cache keys.

## Project structure

```text
04_frozen_permission_key/
├── README.md
└── main.py
```

## YoungLion concepts

- `FrozenDDM`
- `hashing`
- `thaw`

## Run

```bash
cd 04_frozen_permission_key
python main.py
```

## Walkthrough

1. `main.py` creates a small but realistic local data/problem setup.
2. It uses YoungLion through its public API rather than private implementation details.
3. The example prints the important result so behavior is visible immediately.
4. Files created by the example are written under its local `workspace/` directory where applicable.

## Why this pattern matters

Use immutable DDM values as stable cache keys. The example is intentionally small enough to read in one sitting, but the same API is designed to scale into a larger application module.

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
from YoungLion import FrozenDDM

permission = FrozenDDM({"user_id": 7, "roles": ["admin", "editor"]})
cache = {permission: "ALLOW"}
print(cache[permission])
print("Mutable copy:", permission.thaw())
```

## Representative output

The following output was captured while validating this mini-project against the v0.1 source tree. Values such as timestamps, temporary paths, ordering, random samples or durations can differ between runs.

```text
ALLOW
Mutable copy: {
  "user_id": 7,
  "roles": [
    "admin",
    "editor"
  ]
}
```

## Adaptation checklist

- Replace the sample records/files with your application's own data model.
- Keep the public YoungLion calls shown above; avoid depending on private `_native` implementation details.
- Add domain validation and application-specific exception handling at trust boundaries.
- For large datasets, benchmark with realistic record counts and field cardinality before choosing indexes or packed representations.
- Add automated tests for the behavior your application depends on.
