# 32. Indexed age range search

## Scenario

Use a numeric nested-path index for range lookup.

## Project structure

```text
32_ddm_age_range_search/
├── README.md
└── main.py
```

## YoungLion concepts

- `DDMSearchEngine`
- `between`
- `numeric index`

## Run

```bash
cd 32_ddm_age_range_search
python main.py
```

## Walkthrough

1. `main.py` creates a small but realistic local data/problem setup.
2. It uses YoungLion through its public API rather than private implementation details.
3. The example prints the important result so behavior is visible immediately.
4. Files created by the example are written under its local `workspace/` directory where applicable.

## Why this pattern matters

Use a numeric nested-path index for range lookup. The example is intentionally small enough to read in one sitting, but the same API is designed to scale into a larger application module.

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
from YoungLion import ListDDM, DDMSearchEngine

users = ListDDM({"id": i, "profile": {"age": 15 + i}} for i in range(30))
engine = DDMSearchEngine(users).create_indexes("profile.age")
print([u.id for u in engine.between("profile.age", 18, 21)])
```

## Representative output

The following output was captured while validating this mini-project against the v0.1 source tree. Values such as timestamps, temporary paths, ordering, random samples or durations can differ between runs.

```text
[3, 4, 5, 6]
```

## Adaptation checklist

- Replace the sample records/files with your application's own data model.
- Keep the public YoungLion calls shown above; avoid depending on private `_native` implementation details.
- Add domain validation and application-specific exception handling at trust boundaries.
- For large datasets, benchmark with realistic record counts and field cardinality before choosing indexes or packed representations.
- Add automated tests for the behavior your application depends on.
