# Choosing a DDM variant

YoungLion intentionally provides several DDM forms because mutability, hashing, memory overhead, validation and zero-copy access are different requirements.

## Decision table

| Need | Recommended type | Reason |
|---|---|---|
| General mutable record | `DDM` | Fast normal attribute semantics and complete API |
| Many mostly-read records | `PackedDDM` | Reduced Python instance overhead |
| Immutable value key | `FrozenDDM` | Stable value hash and immutable semantics |
| Mutable identity key | `IdentityDDM` | Hash/equality follow identity rather than mutable value |
| Enforce runtime shape | `SchemaDDM` | Schema validation during construction/update |
| Missing keys need defaults | `DefaultDDM` | Default factory/value behavior |
| Expensive derived fields | `LazyDDM` | Resolve fields only when requested |
| Existing dict must not be copied | `ViewDDM` | Zero-copy mapping view |

## DDM

Prefer `DDM` unless a concrete requirement points to another variant. It is the compatibility-focused general-purpose model and supports dynamic attributes, dotted paths, serialization, cloning, merging, validation and collection integration.

## PackedDDM

Use packed models for large read-heavy collections where saving per-object Python header/dictionary overhead matters. Packed records trade some of the unrestricted dynamic behavior of normal DDM for a tighter representation. Benchmark with your actual field count and nesting before converting an existing codebase.

## FrozenDDM

Use when a record must be a stable value in a `set`, cache key or dictionary key. Never make a normal mutable value-equality DDM hashable: changing a value after insertion would violate Python's hash-container invariants.

## IdentityDDM

Use when object identity—not current field content—defines uniqueness. This is useful for mutable live sessions, handles or graph nodes whose fields can change while the object remains the same entity.

## SchemaDDM

Use at trust boundaries: parsed input, configuration loading, local persistence, inter-process messages or API payloads. Validation is runtime protection, not a substitute for static typing.

## DefaultDDM and LazyDDM

`DefaultDDM` is appropriate for sparse configuration and counters. `LazyDDM` is better when a value is expensive to compute or may never be requested. Avoid hiding unexpected I/O behind a lazy field unless the calling code is explicitly designed for it.

## ViewDDM

A view reflects the original mapping. That is the purpose. It also means mutations through either side can be visible to the other side; do not use it when isolation is required.

## Collection choice

After choosing a record type, choose the collection separately:

- ordered sequence and bulk transformations: `ListDDM`;
- uniqueness: `SetDDM`;
- application registry/keyed access: `DictDDM`;
- table-like row operations: `DDMTable`.

For indexed nested-field queries, wrap/attach the collection to `DDMSearchEngine` rather than repeatedly scanning it.
