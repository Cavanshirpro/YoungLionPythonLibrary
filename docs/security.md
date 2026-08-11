# Security considerations

YoungLion is not a sandbox. Validate inputs to `ScriptRunner`, Python/JS execution, SQL, archive extraction and file deletion/overwrite helpers. Use SQL parameters; do not interpolate untrusted shell/SQL text. Keep mail/FTP credentials in secrets/environment configuration. Scope File roots to application directories where practical.

Checksums detect changes but are not digital signatures. Search indexes can retain searchable data; do not index secrets without appropriate process/access controls.
