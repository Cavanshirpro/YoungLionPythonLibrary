# Thread safety

Mutable DDMs and mutable collections should be synchronized like ordinary mutable Python containers. `FrozenDDM` is appropriate for read-only sharing. Utility classes use locks where their implementation requires them, but native code does not make arbitrary concurrent Python-object mutation safe.

Atomic file replacement protects one file-update boundary, not multi-file transactions.
