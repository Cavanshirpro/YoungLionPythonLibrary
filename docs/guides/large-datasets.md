# Working with large datasets

This guide explains how to structure YoungLion workloads when records number in the tens of thousands or more.

## 1. Avoid repeated full scans

A one-off filter can be cheaper than constructing an index. Repeated queries against the same path are different: build a `DDMSearchEngine` path index once and reuse it.

```python
engine = DDMSearchEngine(records)
engine.create_indexes("profile.name", "profile.age", "account.id")
```

Use exact indexes for equality-heavy fields, sorted/range structures for numeric comparisons, text indexes for fuzzy/ranked search and composite indexes for combinations that recur as a unit.

## 2. Batch mutations

A chain of independent bulk operations can traverse the collection repeatedly. Group compatible mutations in a `BatchPlan` so the outer collection is visited once.

```python
plan = records.batch().add("score", 5).clamp("score", 0, 100).set("active", True)
plan.execute(records)
```

## 3. Choose the right representation

- Use `PackedDDM` for many mostly-read records if profiling shows object overhead matters.
- Use normal `DDM` where unrestricted mutable attributes are more important.
- Avoid storing several redundant copies of the same dataset solely to support different indexes.

`DDMSearchEngine` is designed to share the underlying record store across path indexes where practical.

## 4. Keep callbacks cheap

`apply_path()` can move traversal into native code, but a Python callback still executes under the GIL. If the callback performs heavy Python work for every record, the callback becomes the bottleneck. Prefer built-in numeric/path batch operations when they express the transformation.

## 5. Avoid needless serialization

Do not call `to_dict()` or `to_json()` inside a tight query loop unless serialization is actually required. Keep records as DDM objects during computation and serialize at boundaries such as persistence, IPC or network output.

## 6. Stream files

Use chunked reads and line-oriented helpers for large files. Do not read a multi-gigabyte file into one Python string simply because the API permits whole-file reads.

## 7. Measure index construction separately

An indexed search benchmark should distinguish:

1. index build time;
2. first query latency;
3. repeated query throughput;
4. memory used by indexes;
5. mutation/invalidation cost.

A scan can win for one query; an index can dominate for thousands of repeated queries. The workload decides.

## 8. Mutation and invalidation

An index only remains correct if mutations are reflected or invalidated. Prefer collection APIs that know when indexed data changes. If external code mutates nested mappings behind the collection/search layer, refresh or invalidate the relevant index explicitly.

## 9. Memory measurement

Use realistic nested shapes, strings and field cardinality. Shallow `sys.getsizeof()` values do not capture the full object graph. See `docs/performance/ddm-memory.md` and `docs/performance/benchmark-methodology.md`.
