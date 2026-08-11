# Bulk processing and BatchPlan

Prefer collection methods over manual loops when the operation maps to a native path/numeric primitive.

```python
rows.increment("account.balance", 10)
rows.clamp("risk.score", 0, 100)
```

Python callbacks are supported with `apply_path`, but the callback itself still executes in Python.

Several simple operations can be compiled into one collection traversal:

```python
plan = rows.batch().add("score", 5).multiply("score", 1.05).clamp("score", 0, 100).set("active", True)
plan.execute(rows)
```

Collection mutation invalidates reusable search indexes. SetDDM also re-evaluates uniqueness keys when needed.
