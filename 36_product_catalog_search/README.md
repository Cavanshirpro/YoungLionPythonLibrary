# 36. Product catalog search

## Scenario

Rank product text and filter with structured fields.

## Project structure

```text
36_product_catalog_search/
├── README.md
└── main.py
```

## YoungLion concepts

- `ApplicationSearch`
- `fields`
- `facet`

## Run

```bash
cd 36_product_catalog_search
python main.py
```

## Walkthrough

1. `main.py` creates a small but realistic local data/problem setup.
2. It uses YoungLion through its public API rather than private implementation details.
3. The example prints the important result so behavior is visible immediately.
4. Files created by the example are written under its local `workspace/` directory where applicable.

## Why this pattern matters

Rank product text and filter with structured fields. The example is intentionally small enough to read in one sitting, but the same API is designed to scale into a larger application module.

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
from YoungLion import ApplicationSearch

search = ApplicationSearch()
for pid, title, category in [(1, "Gaming Laptop", "computer"), (2, "Office Laptop", "computer"), (3, "Wireless Mouse", "accessory")]:
    search.add(pid, title, fields={"category": category}, payload={"id": pid, "title": title})
print(search.search("laptpo"))
print("Facets:", search.facet("category"))
```

## Representative output

The following output was captured while validating this mini-project against the v0.1 source tree. Values such as timestamps, temporary paths, ordering, random samples or durations can differ between runs.

```text
[{'id': 1, 'title': 'Gaming Laptop'}, {'id': 2, 'title': 'Office Laptop'}]
Facets: [('computer', 2), ('accessory', 1)]
```

## Adaptation checklist

- Replace the sample records/files with your application's own data model.
- Keep the public YoungLion calls shown above; avoid depending on private `_native` implementation details.
- Add domain validation and application-specific exception handling at trust boundaries.
- For large datasets, benchmark with realistic record counts and field cardinality before choosing indexes or packed representations.
- Add automated tests for the behavior your application depends on.
