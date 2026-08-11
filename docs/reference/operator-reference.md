# DDM collection operator reference

Frequently used path/algorithm operations: `filter_path`, `count_path`, `partition_path`, `sort_by`, `is_sorted`, `lower_bound`, `binary_search`, `equal_range`, `nth`, `top`, `bottom`, numeric `sum/mean/min/max` and bulk numeric mutations.

Binary-search helpers require the same sort path/order. Keep `verify_sorted=True` unless the caller already guarantees the invariant.
