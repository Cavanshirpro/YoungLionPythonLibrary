# File workflows

- Application config/state → `atomic_write_json`.
- Integrity → `checksum`, `compare_files`.
- Backups/audits → `find_files`, `get_info`, `directory_size`, `backup`.
- Huge files → `read_chunks`.
- Recent log lines → `tail`.

Complex PDF/YAML/RTF/LaTeX requirements may exceed the intentional dependency-free subset; integrate a dedicated application dependency when standards-complete behavior is required.
