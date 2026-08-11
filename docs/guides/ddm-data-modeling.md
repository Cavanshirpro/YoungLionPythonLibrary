# Data modeling with DDM

Start with `DDM`. Select variants deliberately:

- huge mostly-read rows → `PackedDDM`;
- immutable value keys → `FrozenDDM`;
- mutable identity membership → `IdentityDDM`;
- boundary validation → `SchemaDDM`;
- derived expensive fields → `LazyDDM`;
- existing dict without copy → `ViewDDM`.

Nested ordinary dictionaries/lists can remain nested; native path operations can traverse them. Convert to plain dictionaries with `to_dict()` at serialization/API boundaries.
