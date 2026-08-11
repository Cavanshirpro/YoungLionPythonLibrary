# Changelog

## 0.1.0 — in development

0.1.0 is the first native-architecture release line and has **not been declared final in this repository yet**.

### Native core

- Added a C++17 CPython extension with no pybind11 runtime requirement.
- Added optimized release builds with optional LTO, strict warning mode and portable CPU settings.
- Added native JSON, filesystem, binary/file, vector/cache and search primitives.

### DDM

- Removed duplicate `_data` + public-field dictionary storage; `_data` is now a zero-copy compatibility view of `__dict__`.
- Added native recursive serialization, clone data, dotted paths, deep merge, diff, flattening and schema checks.
- Added native-driven recursive memory inspection and optional key interning.
- Hardened native JSON parsing for surrogate pairs, control characters and invalid number grammar.
- Added a fast flat-model `to_dict` path using `PyDict_Copy` when all public values are immutable leaves.
- Removed an unnecessary second recursive copy from native clone data.

### File

- Removed mandatory third-party runtime dependencies from normal File operation.
- Added native binary read/write, CRC32, directory size, line count, file comparison and touch.
- Added SHA/standard-library checksums, atomic text/JSON/binary replacement, backups, chunked reads and filtered file discovery.
- Hardened CSV quoted-newline handling.
- Atomic replacement now uses unique same-directory temporary files, file `fsync`, and best-effort POSIX parent-directory `fsync`.

### Search

- Rebuilt Search around typed documents, results and query objects.
- Added native Unicode Levenshtein, Damerau-Levenshtein, Jaro-Winkler, trigram and substring-position primitives.
- Added persistent inverted indexes and posting-list BM25 scoring for repeated queries.
- Added hybrid ranking, autocomplete, Aho-Corasick multi-pattern matching, structured, numeric and file search.
- Preserved historical `SearchData`, `Search`, `SearchFile` and `GenerateTags` APIs.
- Added a maximum generated-tag limit to prevent factorial memory explosions.
- Added lazily sorted prefix-vocabulary caching and full-recall pure-prefix candidate expansion.

### Packaging and CI

- Runtime `dependencies = []`.
- Added typed package metadata and richer PyPI project metadata.
- Corrected the stable interpreter boundary to CPython 3.10–3.14; CPython 3.15 stays in a separate manually triggered prerelease artifact job.
- Kept C++ sources in the sdist while excluding them from prebuilt wheels, reducing wheel size significantly.
- Added Windows/Linux/macOS native CI plus clean Debian/Arch/Fedora/Rocky/openSUSE/Alpine source builds.
- Added manylinux/musllinux, Windows, macOS and source artifact workflow.
- PyPI publishing is intentionally **not** automated; artifacts are downloaded and published manually by the maintainer.
