# DDM core API

`DDM` is a mutable dynamic record. Top-level keys become attributes while mapping-like operations remain available.

```python
user = DDM({"name": "Alice", "profile": {"age": 30}})
print(user.name, user["name"])
user.set_path("profile.age", 31)
```

Key areas: serialization (`to_dict`, `to_json`, `to_flat_dict`), nested paths, clone/copy, merge/update, diff/schema validation, pick/omit/filter, transforms, grouping/aggregation, type/memory introspection and dict-style mutation.

Standard mutable DDM is not the recommended Python set/dict-key type. Use `FrozenDDM` for immutable value hashing or `IdentityDDM` for mutable identity semantics.
