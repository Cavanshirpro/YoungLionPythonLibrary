# Indexed DDM search

For repeated queries on large data, create indexes on nested paths.

```python
engine = DDMSearchEngine(users)
engine.create_indexes("profile.name", "profile.age", "account.id")
```

Use `find` for exact/comparison operations, `between` for ranges, `text` for ranked/fuzzy string search and composite indexes for repeated multi-field equality queries.

Path indexes share one record store rather than copying a full key→object table per path. If records are mutated outside collection APIs, call `invalidate` or `refresh` before trusting indexes.
