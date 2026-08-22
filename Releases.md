# YoungLion Release History

YoungLion follows semantic versioning for the public package line. Patch releases
may improve documentation, type information, packaging, diagnostics and bug fixes
without intentionally changing the established public behavior of the minor line.

## 0.1.1 — Runtime documentation and discoverability patch — 2026-08-22

### Release intent

v0.1.1 is a documentation-first patch over the v0.1 native architecture. The
runtime algorithms, public method signatures and data/search/file semantics are
intentionally preserved. The primary goal is to make YoungLion understandable
*from inside Python itself*: users should be able to discover a class in IDLE,
call ``help()``, inspect a method in a REPL or hover it in an IDE and receive
useful guidance without first opening the external documentation tree.

This is particularly important for YoungLion because the package intentionally
contains several broad tool families—DDM modeling, high-throughput collections,
search, File helpers and application utilities. A short one-line docstring is not
enough to communicate mutation behavior, nested-path semantics, index lifetime,
thread-safety, format limitations or the difference between similar-looking
classes.

### Runtime docstring coverage

The Python implementation now carries comprehensive runtime documentation across
the complete discoverable public surface:

- package and subpackage module overviews;
- all public classes;
- public constructors where they are part of normal interactive discovery;
- public methods and properties;
- public module-level helper functions.

The documentation style is intentionally optimized for ``help()``, IDLE and IDE
introspection. A typical entry starts with a concise summary and then expands into
parameters, return behavior, exceptions where relevant, operational notes and
examples for the APIs where an example materially clarifies usage.

The release audit covers **14 Python implementation modules and 612 discoverable
public class/function/method entries**, with no missing or intentionally tiny
placeholder docstrings in that audited surface.

### DDM and domain-model documentation

DDM documentation now explains both the dynamic mapping use case and the
subclass-oriented domain-model pattern expected in real applications. In
particular, the runtime help demonstrates nested typed models such as:

```python
from YoungLion import DDM


class UserProfile(DDM):
    def __init__(self, data):
        super().__init__(data)
        self.name: str = str(data.get("name", "Unknown"))
        self.country: str = str(data.get("country", "Unknown"))


class User(DDM):
    def __init__(self, data):
        super().__init__(data)
        self.id: int = int(data.get("id", 0))
        self.profile: UserProfile = UserProfile(data.get("profile", {}))
```

The DDM runtime documentation now describes:

- the single-store ``__dict__`` data layout;
- recursive serialization and JSON conversion;
- dotted-path read/write/existence checks;
- subclass-aware cloning and nested typed model reconstruction;
- merge/update/diff behavior;
- schema validation;
- flattening, filtering, mapping, grouping and aggregation;
- memory inspection and compaction;
- when external DDM search indexes must be refreshed after mutation.

Specialized variants—FrozenDDM, IdentityDDM, PackedDDM, SchemaDDM, DefaultDDM,
LazyDDM and ViewDDM—now explain the semantic trade-off each variant introduces
instead of appearing as unexplained alternative constructors.

### High-throughput collection documentation

ListDDM, SetDDM, DictDDM, DDMTable, DDMCollectionOps and BatchPlan now document
their record-oriented behavior in detail. Runtime help covers nested dotted-path
operations, numeric mutation/reduction, filtering, grouping, deduplication,
partitioning, chunking, sorting and binary-search-style algorithms.

BatchPlan explicitly documents its one-pass purpose: multiple simple mutations
can be queued and sent to the native collection implementation together instead
of repeatedly scanning the same record pool.

SetDDM documentation now calls out its uniqueness model and the importance of a
stable ``key_path`` for large mutable datasets, including when ``rehash()`` is
needed after direct external mutations.

### Search documentation

The search stack now has runtime explanations for the relationship between
SearchIndex, BM25Index, AutocompleteIndex, MultiPatternSearch, NumericSearch,
StructuredSearch, FileSearchEngine, ApplicationSearch and DDMSearchEngine.

The DDM search documentation explains:

- dotted paths such as ``profile.name`` and ``economy.balance``;
- exact hash indexes versus sorted range indexes;
- text/fuzzy indexes;
- composite exact indexes;
- scan fallback versus reusable index behavior;
- the shared source/object snapshot used to reduce repeated index memory;
- ``refresh()`` and targeted ``invalidate()`` responsibilities after external
  mutations.

ApplicationSearch documentation describes document CRUD, ranked results, payload
retrieval, autocomplete, facets and the intended command-palette/help-center/
settings/catalog use cases.

### File and format documentation

The File runtime surface now explains core filesystem operations, text/binary and
JSON persistence, checksums, directory sizing, chunked reads, backups and atomic
replacement behavior. Atomic-write documentation calls out the same-filesystem
assumption and the same-directory temporary-file/flush/replace strategy.

Format helpers now state their scope rather than implying unlimited standards
coverage. In particular, the dependency-free PDF and YAML-like helpers are
explicitly documented as practical subsets; applications requiring advanced PDF
layout/OCR or full YAML anchors/tags/custom types should use a dedicated parser.

### Application utility documentation

The utility layer now provides IDLE/help-friendly explanations for:

- ``ScriptRunner`` and ``CommandResult``;
- ``TaskScheduler`` and ``TaskInfo``;
- ``Logger`` with context binding and size-based rotation;
- ``EmailManager``;
- ``FileTransferManager``;
- ``TextProcessor``;
- ``EventBus``;
- ``TTLCache``;
- ``RateLimiter``;
- ``RetryPolicy``;
- ``CircuitBreaker``;
- ``Stopwatch``;
- ``Terminal`` and ``Colors``.

Thread-sensitive classes document what YoungLion protects internally and what
remains the caller's synchronization responsibility. EventBus notes that emission
is synchronous; TaskScheduler notes that work runs in in-process daemon threads;
TTLCache documents lazy expiry/LRU-style recency; RateLimiter notes that its token
bucket is process-local; RetryPolicy warns that retries are appropriate only when
repeating the operation is safe.

### API and behavior compatibility

No intentional runtime feature or algorithm change is part of v0.1.1. Public
Python method signatures remain unchanged. The documentation pass was verified by
comparing the original and updated Python ASTs after removing docstring expression
nodes; the resulting runtime structure is identical.

A small formatting consequence exists for methods that previously placed their
entire body on the same physical source line: those definitions are expanded to a
normal indented suite so Python can expose a real function docstring. The executed
statements and AST semantics remain unchanged.

The package version metadata and ``YoungLion.__version__`` are updated to
``0.1.1`` as required for the patch release.

### Packaging and release expectations

YoungLion remains dependency-free at runtime. Native C++ sources remain source-
distribution material and are not intended to be bundled as source files inside
prebuilt wheels. ``py.typed`` and the public ``.pyi`` stubs remain part of the
wheel so static typing and runtime introspection complement one another.

The v0.1 release workflow continues to build distribution artifacts rather than
publishing directly to PyPI. Maintainers should validate the generated ``pypi/``
folder with Twine before manual upload.

### Upgrade notes

There are no intended application-code migrations from v0.1.0 to v0.1.1. Normal
upgrade:

```bash
python -m pip install --upgrade YoungLion==0.1.1
```

Interactive users are encouraged to try:

```python
import YoungLion
from YoungLion import DDM, ListDDM, DDMSearchEngine, File, Logger

help(YoungLion)
help(DDM)
help(DDM.get_path)
help(ListDDM.filter_path)
help(DDMSearchEngine.create_index)
help(File.atomic_write_json)
help(Logger.bind)
```

These runtime help pages are now a supported part of YoungLion's developer
experience rather than an afterthought.

---

## 0.1.0 — Native architecture foundation

v0.1.0 established the native-accelerated architecture on which the 0.1 line is
built.

### Native core

- Added a C++17 CPython extension with no pybind11 runtime requirement.
- Added optimized release builds with optional LTO, strict warning mode and
  portable CPU settings.
- Added native JSON, filesystem, binary/file, DDM collection and search
  primitives.

### Dynamic Data Model

- Removed duplicate ``_data`` plus public-field dictionary storage; ``_data`` is
  a zero-copy compatibility view of ``__dict__``.
- Added native recursive serialization, clone data, dotted paths, deep merge,
  diff, flattening and schema checks.
- Added native-driven recursive memory inspection and optional key interning.
- Added typed-subclass-aware clone reconstruction and specialized clone state for
  built-in DDM variants.
- Added FrozenDDM, IdentityDDM, PackedDDM, SchemaDDM, DefaultDDM, LazyDDM and
  ViewDDM.
- Added ListDDM, SetDDM, DictDDM, DDMTable and one-pass BatchPlan operations.

### File

- Removed mandatory third-party runtime dependencies from normal File operation.
- Added native binary read/write, CRC32, directory size, line count, file
  comparison and touch.
- Added standard-library checksums, atomic text/JSON/binary replacement, backups,
  chunked reads and filtered file discovery.
- Hardened CSV quoted-newline handling.
- Atomic replacement uses unique same-directory temporary files, file ``fsync``
  and best-effort POSIX parent-directory ``fsync``.

### Search

- Rebuilt Search around typed documents, results and query objects.
- Added native Unicode Levenshtein, Damerau-Levenshtein, Jaro-Winkler, trigram
  and substring-position primitives.
- Added persistent inverted indexes and posting-list BM25 scoring for repeated
  queries.
- Added hybrid ranking, autocomplete, multi-pattern matching, structured,
  numeric and file search.
- Added DDMSearchEngine for exact/range/text/composite nested-path queries and
  shared multi-index record storage.
- Added ApplicationSearch for application-facing document CRUD, ranked search,
  autocomplete and facets.
- Preserved historical SearchData, Search, SearchFile and GenerateTags APIs.

### Utilities

- Added/expanded ScriptRunner, TaskScheduler, Logger, EmailManager,
  FileTransferManager and TextProcessor.
- Added EventBus, TTLCache, RateLimiter, RetryPolicy, CircuitBreaker, Stopwatch
  and Terminal.
- Expanded ANSI/RGB/ANSI-256 handling in Colors.

### Typing, packaging and CI

- Runtime ``dependencies = []``.
- Added ``py.typed`` and modular public ``.pyi`` stubs.
- Added cross-platform native CI and source-install validation.
- Added wheel/sdist artifact assembly for manual PyPI publishing.
- Kept native sources in the sdist while excluding them from prebuilt wheels.
