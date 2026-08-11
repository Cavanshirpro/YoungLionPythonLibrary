# DDM collections

`ListDDM`, `SetDDM`, `DictDDM` and `DDMTable` share `DDMCollectionOps`.

Native-assisted operations include path reads/writes, filtering/counting/partitioning, numeric mutation/reductions, stable sort, lower-bound/binary-search/equal-range, nth-element selection, grouping, deduplication, chunking and path refactors.

`SetDDM` avoids unsafe mutable value hashing. Define uniqueness with content, `key=`, or `key_path=`. Mutations that can affect uniqueness rebuild the key map and detect collisions.

`DDMTable` adds columns/select/assign/query convenience methods.
