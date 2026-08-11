# DDM variants

- **FrozenDDM:** recursively immutable/hashable; `thaw()` returns mutable DDM.
- **IdentityDDM:** mutable with identity equality/hash.
- **PackedDDM:** slots-based, no per-instance `__dict__`; designed for huge mostly-read datasets.
- **SchemaDDM:** construction and validated updates against a schema.
- **DefaultDDM:** fills missing top-level values with a factory.
- **LazyDDM:** computes configured fields on first access and caches until invalidated.
- **ViewDDM:** zero-copy view over an existing `dict`; mutations are shared with the original dictionary.

Choose a variant for a semantic or measured performance reason; start with normal `DDM` otherwise.
