# 25. Keyed user registry

## Scenario

Use DictDDM as an application registry plus bulk operations.

## Project structure

```text
25_dictddm_registry/
├── README.md
└── main.py
```

## YoungLion concepts

- `DictDDM`
- `mapping semantics`
- `bulk values`

## Run

```bash
cd 25_dictddm_registry
python main.py
```

## Walkthrough

1. `main.py` creates a small but realistic local data/problem setup.
2. It uses YoungLion through its public API rather than private implementation details.
3. The example prints the important result so behavior is visible immediately.
4. Files created by the example are written under its local `workspace/` directory where applicable.

## Why this pattern matters

Use DictDDM as an application registry plus bulk operations. The example is intentionally small enough to read in one sitting, but the same API is designed to scale into a larger application module.

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
from YoungLion import DictDDM

users = DictDDM({
    "alice": {"score": 10, "active": True},
    "bob": {"score": 20, "active": False},
})
users.increment("score", 5)
print(users["alice"].score)
print(users.keys_for("active", True))
```

## Representative output

The following output was captured while validating this mini-project against the v0.1 source tree. Values such as timestamps, temporary paths, ordering, random samples or durations can differ between runs.

```text
15.0
['alice']
```

## Adaptation checklist

- Replace the sample records/files with your application's own data model.
- Keep the public YoungLion calls shown above; avoid depending on private `_native` implementation details.
- Add domain validation and application-specific exception handling at trust boundaries.
- For large datasets, benchmark with realistic record counts and field cardinality before choosing indexes or packed representations.
- Add automated tests for the behavior your application depends on.
