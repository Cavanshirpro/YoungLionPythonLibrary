# File API

`File` combines `FileBase`, `FileFormatsMixin` and `FileExtraMixin`.

Core capabilities: filesystem metadata/list/create/copy/move/rename/delete, text/binary I/O, JSON, checksums, directory size, line count, binary compare, `head`, efficient `tail`, chunked reads, backup and atomic text/binary/JSON replacement.

Structured helpers cover CSV, INI, properties, XML, dependency-free YAML subset and basic PDF text I/O, plus Markdown/HTML/CSS/JS/RTF/TEX/Python, ZIP and SQLite helpers.

Use atomic writes for important state/config files. Use `read_chunks` for very large files.
