# Errors and behavior

YoungLion preserves a mix of exception and status-return APIs.

- Programmer/validation errors normally raise `TypeError`, `ValueError`, `KeyError`, etc.
- Many filesystem convenience methods return `bool` for expected operational failures.
- Search returns empty lists for no matches.
- `find_one` supports a default.
- `CommandResult.check()` raises for non-zero process exit.
- Scheduler/transfer APIs expose IDs and state/status inspection.

Applications should translate these into domain-specific errors at their boundaries.
