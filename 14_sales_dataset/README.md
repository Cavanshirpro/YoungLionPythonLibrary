# 14. Small sales dataset report

## Scenario

Use Dataset for lightweight rows, grouping and statistics.

## Project structure

```text
14_sales_dataset/
├── README.md
└── main.py
```

## YoungLion concepts

- `Dataset`
- `group_by`
- `stats`

## Run

```bash
cd 14_sales_dataset
python main.py
```

## Walkthrough

1. `main.py` creates a small but realistic local data/problem setup.
2. It uses YoungLion through its public API rather than private implementation details.
3. The example prints the important result so behavior is visible immediately.
4. Files created by the example are written under its local `workspace/` directory where applicable.

## Why this pattern matters

Use Dataset for lightweight rows, grouping and statistics. The example is intentionally small enough to read in one sitting, but the same API is designed to scale into a larger application module.

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
from YoungLion import Dataset

data = Dataset(rows=[
    {"region": "AZ", "revenue": 120.0},
    {"region": "TR", "revenue": 180.0},
    {"region": "AZ", "revenue": 90.0},
])
print("Revenue stats:", data.stats("revenue"))
print("Regions:", {k: len(v.rows) for k, v in data.group_by("region").items()})
```

## Representative output

The following output was captured while validating this mini-project against the v0.1 source tree. Values such as timestamps, temporary paths, ordering, random samples or durations can differ between runs.

```text
Revenue stats: {'count': 3, 'sum': 390.0, 'mean': 130.0, 'min': 90.0, 'max': 180.0, 'std': 37.416573867739416}
Regions: {'AZ': 2, 'TR': 1}
```

## Adaptation checklist

- Replace the sample records/files with your application's own data model.
- Keep the public YoungLion calls shown above; avoid depending on private `_native` implementation details.
- Add domain validation and application-specific exception handling at trust boundaries.
- For large datasets, benchmark with realistic record counts and field cardinality before choosing indexes or packed representations.
- Add automated tests for the behavior your application depends on.
