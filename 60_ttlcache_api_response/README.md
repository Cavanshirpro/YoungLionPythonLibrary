# 60. TTL API response cache

## Scenario

Cache computed responses locally with expiry and bounded size.

## Project structure

```text
60_ttlcache_api_response/
├── README.md
└── main.py
```

## YoungLion concepts

- `TTLCache`
- `TTL`
- `stats`

## Run

```bash
cd 60_ttlcache_api_response
python main.py
```

## Walkthrough

1. `main.py` creates a small but realistic local data/problem setup.
2. It uses YoungLion through its public API rather than private implementation details.
3. The example prints the important result so behavior is visible immediately.
4. Files created by the example are written under its local `workspace/` directory where applicable.

## Why this pattern matters

Cache computed responses locally with expiry and bounded size. The example is intentionally small enough to read in one sitting, but the same API is designed to scale into a larger application module.

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
from YoungLion import TTLCache

cache = TTLCache(max_size=3, default_ttl=10)
cache.set("user:1", {"name": "Alice"})
cache.set("user:2", {"name": "Bob"})
print(cache.get("user:1"))
print(cache.stats())
```

## Representative output

The following output was captured while validating this mini-project against the v0.1 source tree. Values such as timestamps, temporary paths, ordering, random samples or durations can differ between runs.

```text
{'name': 'Alice'}
{'size': 2, 'hits': 1, 'misses': 0, 'evictions': 0}
```

## Adaptation checklist

- Replace the sample records/files with your application's own data model.
- Keep the public YoungLion calls shown above; avoid depending on private `_native` implementation details.
- Add domain validation and application-specific exception handling at trust boundaries.
- For large datasets, benchmark with realistic record counts and field cardinality before choosing indexes or packed representations.
- Add automated tests for the behavior your application depends on.
