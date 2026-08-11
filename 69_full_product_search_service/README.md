# 69. Mini product search service

## Scenario

Combine DDM records, indexed nested fields, general text search and atomic persistence.

## Project structure

```text
69_full_product_search_service/
├── README.md
└── main.py
```

## YoungLion concepts

- `DDMTable`
- `DDMSearchEngine`
- `ApplicationSearch`
- `File`

## Run

```bash
cd 69_full_product_search_service
python main.py
```

## Walkthrough

1. `main.py` creates a small but realistic local data/problem setup.
2. It uses YoungLion through its public API rather than private implementation details.
3. The example prints the important result so behavior is visible immediately.
4. Files created by the example are written under its local `workspace/` directory where applicable.

## Why this pattern matters

Combine DDM records, indexed nested fields, general text search and atomic persistence. The example is intentionally small enough to read in one sitting, but the same API is designed to scale into a larger application module.

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
from YoungLion import DDMTable, DDMSearchEngine, ApplicationSearch, File

products = DDMTable([
    {"id": 1, "name": "Gaming Laptop", "category": "computer", "price": 1299.0},
    {"id": 2, "name": "Office Laptop", "category": "computer", "price": 799.0},
    {"id": 3, "name": "Wireless Mouse", "category": "accessory", "price": 49.0},
])
path_index = DDMSearchEngine(products).create_indexes("category", "price")
print("Computers:", [p.name for p in path_index.find("category", "computer")])

search = ApplicationSearch()
for p in products:
    search.add(p.id, p.name, fields={"category": p.category}, payload=p)
print("Text result:", [p.name for p in search.search("gming laptp")])

File(str(Path(__file__).parent / "workspace")).atomic_write_json("catalog.json", [p.to_dict() for p in products])
```

## Representative output

The following output was captured while validating this mini-project against the v0.1 source tree. Values such as timestamps, temporary paths, ordering, random samples or durations can differ between runs.

```text
Computers: ['Gaming Laptop', 'Office Laptop']
Text result: ['Gaming Laptop', 'Office Laptop']
```

## Adaptation checklist

- Replace the sample records/files with your application's own data model.
- Keep the public YoungLion calls shown above; avoid depending on private `_native` implementation details.
- Add domain validation and application-specific exception handling at trust boundaries.
- For large datasets, benchmark with realistic record counts and field cardinality before choosing indexes or packed representations.
- Add automated tests for the behavior your application depends on.
