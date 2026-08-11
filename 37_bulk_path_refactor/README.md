# 37 — Schema/path refactor across records

**Complexity:** Advanced  
**Focus:** rename_path, move_path, delete_path, migration

## Scenario

Refactor nested field names across a large dataset using copy/move/rename/delete primitives and verify the migration with path counts.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
37_bulk_path_refactor/
├── main.py
```

## What to pay attention to

- **rename_path** — used as part of the actual workflow, not only imported for demonstration.
- **move_path** — used as part of the actual workflow, not only imported for demonstration.
- **delete_path** — used as part of the actual workflow, not only imported for demonstration.
- **migration** — used as part of the actual workflow, not only imported for demonstration.

## Run

From this directory:

```bash
python main.py
```

Install YoungLion first. After v0.1 is published:

```bash
python -m pip install YoungLion==0.1.0
```

During local pre-release development you can instead install the main branch checkout with `python -m pip install -e <path-to-main-checkout>`.

## Design notes

### Architecture walkthrough

The important unit here is the **collection**, not one record. Records stay DDM-compatible while transformations happen through `ListDDM`, `SetDDM`, `DictDDM`, `DDMTable` or `BatchPlan`. Path/numeric primitives avoid repeated Python-level traversal; arbitrary business logic can still be injected through callback operations when necessary.

For production migrations, separate transformation from persistence: validate the transformed collection, checkpoint it, then commit it to your database or file store in bounded chunks.

## Ways to extend this project

- Snapshot before migration.
- Write migration invariants and run them before persistence.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `main.py`

```python
from YoungLion import ListDDM, DDM

rows = ListDDM(DDM({"id":i,"profile":{"full_name":f"User {i}","old_country":"AZ"},"legacy":{"enabled":True}}) for i in range(2500))
rows.rename_path("profile.full_name","profile.display_name")
rows.move_path("profile.old_country","profile.country")
rows.delete_path("legacy")
rows.fill_missing("schema_version",2)
print(rows[0].to_dict())
print("v2:", rows.count_path("schema_version",2))
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

