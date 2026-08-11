# DDM memory model

0.1 avoids keeping a second independent full user-data mapping alongside normal DDM attributes. `PackedDDM` reduces instance header overhead further with slots and an internal store.

Memory depends on nested values/key sharing/intering, so measure representative records with `memory_info(recursive=True)` instead of relying only on shallow `sys.getsizeof`.
