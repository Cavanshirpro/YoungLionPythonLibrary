# YoungLion 0.1.1

**YoungLion** is a dependency-light Python toolkit backed by a C++17 native extension. Version 0.1 focuses on four practical problems that appear repeatedly in desktop applications, bots, developer tools, local services, automation programs, and data-heavy Python applications:

1. **Dynamic structured data** through DDM and its specialized variants.
2. **Fast bulk operations and indexed search** over large collections of DDM records.
3. **File and structured-format workflows** without a large tree of Python runtime dependencies.
4. **Reusable application utilities** for scripts, scheduling, logging, caching, resilience, terminal output, text processing, e-mail construction, and file transfer.

The package keeps a Python-friendly API while moving performance-sensitive traversal, serialization, searching, file primitives, and batch operations into C++ where that provides a real benefit.

> **Development status:** `0.1.1` is still the active v0.1 development line. The repository is prepared for reproducible source/wheel builds, but this README does not imply that a particular commit has already been published to PyPI.

---

## Highlights

- C++17 native extension built directly against the CPython C API.
- **Zero required third-party Python runtime dependencies** in the core package.
- Typed package with `py.typed` and detailed `.pyi` files.
- CPython **3.10–3.14** stable target line.
- DDM core plus `PackedDDM`, `FrozenDDM`, `IdentityDDM`, `SchemaDDM`, `DefaultDDM`, `LazyDDM`, and `ViewDDM`.
- `ListDDM`, `SetDDM`, `DictDDM`, and `DDMTable` for collection-scale work.
- Native batch arithmetic, aggregation, sorting, selection, filtering helpers, and `BatchPlan` single-pass mutation plans.
- Nested path indexes such as `profile.name`, numeric range indexes, composite indexes, and fuzzy/text search over DDM collections.
- General application search using inverted indexes, BM25, autocomplete, fuzzy metrics, structured filters, and multi-pattern matching.
- Native/standard-library file operations for JSON, text, binary data, CSV, INI, properties, XML, practical YAML, backups, checksums, atomic writes, and directory workflows.
- Application helpers: scheduler, script runner, logger, event bus, TTL cache, rate limiter, retry policy, circuit breaker, stopwatch, terminal renderer, text processor, e-mail manager, and transfer manager.
- Multi-platform GitHub Actions build configuration that produces one downloadable release bundle instead of publishing to PyPI automatically.

---

## Installation

### From PyPI after a release

```bash
python -m pip install YoungLion
```

### From a local source checkout

A C++17 compiler is required when building the native extension from source.

```bash
git clone https://github.com/Cavanshirpro/YoungLionPythonLibrary.git
cd YoungLionPythonLibrary
python -m pip install .
```

For editable development:

```bash
python -m pip install -e .
```

For a strict local native build:

```bash
YOUNGLION_STRICT=1 python setup.py build_ext --inplace --force
```

On Windows PowerShell, set the variable first:

```powershell
$env:YOUNGLION_STRICT = "1"
python setup.py build_ext --inplace --force
```

See [docs/installation.md](docs/installation.md), [docs/development/building.md](docs/development/building.md), and [docs/development/compatibility.md](docs/development/compatibility.md) for platform details.

---

# Quick start

## DDM: dynamic structured data

```python
from YoungLion import DDM

user = DDM({
    "id": 42,
    "profile": {
        "name": "Alice",
        "age": 28,
    },
    "active": True,
})

print(user.id)
print(user.get_path("profile.name"))

user.set_path("profile.age", 29)
print(user.to_dict())
print(user.to_json(indent=2))
```

DDM is deliberately dynamic: it is useful when your structure is known at runtime, evolves over time, comes from JSON-like data, or must remain easy to inspect and serialize.

## Typed DDM subclasses: model your own domain classes

`DDM` is intentionally subclass-friendly. For application code, a useful pattern is to keep the native/dynamic storage and serialization behavior from `DDM`, while normalizing the fields that your domain actually understands into typed attributes and nested DDM subclasses.

```python
from collections.abc import Mapping
from typing import Any
from YoungLion import DDM


class UserProfile(DDM):
    name: str
    country: str
    age: int

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.name = str(data.get("name", "Unknown"))
        self.country = str(data.get("country", "Unknown"))
        self.age = max(0, int(data.get("age", 0)))

    @property
    def is_adult(self) -> bool:
        return self.age >= 18


class User(DDM):
    id: int
    username: str
    profile: UserProfile

    def __init__(self, data: Mapping[str, Any]):
        super().__init__(data)
        self.id = int(data.get("id", 0))
        self.username = str(data.get("username", "unknown"))
        self.profile = UserProfile(data.get("profile", {}))

    def rename(self, value: str) -> None:
        value = value.strip()
        if not value:
            raise ValueError("username cannot be empty")
        self.username = value


user = User({
    "id": 42,
    "username": "cavan",
    "profile": {"name": "Cavan", "country": "AZ", "age": 18},
})

print(user.profile.name)
print(user.profile.is_adult)
print(user.get_path("profile.country"))
print(user.to_dict())
```

This pattern is useful because it does **not** replace DDM with a conventional dataclass. The object still participates in native DDM serialization, nested-path search, `ListDDM` batch operations and `DDMSearchEngine`; your subclass simply adds domain validation, methods, type annotations and nested models.

For larger projects, keep models, repositories/search indexes and services in separate modules instead of putting every rule in `__init__`. See [Typed DDM subclass modeling](docs/guides/typed-ddm-subclasses.md). The separate `examples` branch contains complete multi-file projects built around this style.

### Choosing a DDM variant

| Type | Best fit |
|---|---|
| `DDM` | General mutable dynamic records |
| `PackedDDM` | Read-heavy records where per-object Python overhead matters |
| `FrozenDDM` | Immutable, value-hashable records and cache/set keys |
| `IdentityDDM` | Mutable objects that need identity-based hashing |
| `SchemaDDM` | Runtime schema validation |
| `DefaultDDM` | Missing-value/default-factory workflows |
| `LazyDDM` | Derived or expensive fields evaluated on demand |
| `ViewDDM` | Zero-copy view over an existing mapping |

See [Choosing a DDM variant](docs/guides/choosing-ddm-variant.md) and the [DDM variants API](docs/api/datamodel-variants.md).

---

## Large DDM collections

`ListDDM`, `SetDDM`, and `DictDDM` are not just aliases around Python containers. They provide a shared collection API designed for repeated path operations and bulk data manipulation.

```python
from YoungLion import ListDDM

users = ListDDM([
    {"id": 1, "profile": {"name": "Alice", "age": 24}, "score": 70},
    {"id": 2, "profile": {"name": "Bob", "age": 31}, "score": 85},
    {"id": 3, "profile": {"name": "Carol", "age": 27}, "score": 91},
])

users.increment("score", 5)
users.clamp("score", 0, 100)

adults = users.filter_path("profile.age", ">=", 25)
average = users.mean("score")
leaderboard = users.top("score", 2)
```

### Single-pass batch plans

When several mutations target the same collection, `BatchPlan` can group them so the outer record traversal happens once.

```python
plan = (
    users.batch()
    .add("score", 3)
    .multiply("score", 1.05)
    .clamp("score", 0, 100)
    .set("active", True)
)

plan.execute(users)
```

Other collection operations cover grouping, distinct values, partitioning, chunking, deduplication, path moves/renames, numeric reductions, nth/top/bottom selection, stable sorting, binary-search helpers, and bulk callback application.

Read [DDM collections](docs/api/datamodel-collections.md), [Batch processing](docs/guides/batch-processing.md), and [Large datasets](docs/guides/large-datasets.md).

---

# Indexed DDM search

A common application pattern is repeatedly searching thousands or millions of structured records by a nested field. Re-running a Python loop for every query is wasteful when the searched path is stable.

```python
from YoungLion import DDMSearchEngine, ListDDM

users = ListDDM([
    {"id": 1, "profile": {"name": "Alice", "age": 24}},
    {"id": 2, "profile": {"name": "Bob", "age": 31}},
    {"id": 3, "profile": {"name": "Alicia", "age": 27}},
])

engine = DDMSearchEngine(users)
engine.create_indexes("profile.name", "profile.age")

exact = engine.find("profile.name", "Alice")
age_band = engine.between("profile.age", 25, 35)
fuzzy = engine.text("profile.name", "Alcie")
```

Indexes are reusable. Depending on the path/query type, the search layer can maintain exact lookup structures, sorted/range information, text indexes, and composite indexes.

```python
engine.create_composite_index("country", "status")
matches = engine.composite(("country", "status"), ("AZ", "active"))
```

The engine can consume YoungLion DDM collections and ordinary iterable/mapping collections of DDM-like records.

See [DDM search indexing](docs/guides/ddm-search-indexing.md), [Search API](docs/api/search.md), and [Search indexing performance](docs/performance/search-indexing.md).

---

# General application search

`ApplicationSearch` is intended for search bars, command palettes, help centers, settings pages, local catalogs, knowledge tools, and similar application-facing search.

```python
from YoungLion import ApplicationSearch

search = ApplicationSearch()
search.add(
    "settings.general",
    title="General settings",
    body="Change language, startup behavior and interface preferences",
    tags=["preferences", "configuration"],
    fields={"category": "settings"},
    payload={"route": "/settings/general"},
)

search.add(
    "settings.account",
    title="Account settings",
    body="Manage profile and account information",
    fields={"category": "settings"},
    payload={"route": "/settings/account"},
)

results = search.search("setings")       # typo-friendly search
suggestions = search.suggest("acc")      # autocomplete
facets = search.facet("category")
```

The search module includes:

- inverted indexes;
- BM25 ranking;
- Levenshtein distance;
- Damerau-Levenshtein distance;
- Jaro-Winkler similarity;
- trigram/Dice similarity;
- prefix/autocomplete indexes;
- numeric range/nearest search;
- structured mapping search;
- Aho-Corasick multi-pattern matching;
- file name/content search;
- DDM path-aware indexes.

The algorithms are exposed as building blocks as well as through higher-level search classes. See [Search algorithms](docs/reference/search-algorithms.md) for when each one is appropriate.

---

# Real-life example projects

The main branch intentionally stays focused on the library itself. A separate **`examples` branch in this same repository** is intended for large, runnable mini-projects rather than tiny snippets:

- typed `class User(DDM)` / nested-model designs;
- large `ListDDM`/`SetDDM`/`DictDDM` batch pipelines;
- reusable nested-path indexes;
- application search backends;
- File/configuration/ETL workflows;
- integrated scheduler/cache/logger/resilience examples.

After the branch is pushed, browse it at [`tree/examples`](../../tree/examples).

# File workflows

`File` combines the core file/path primitives with structured-format helpers.

```python
from YoungLion import File

files = File("workspace")

files.atomic_json_write("settings.json", {
    "theme": "dark",
    "autosave": True,
})

settings = files.json_read("settings.json")
checksum = files.checksum("settings.json", "sha256")
backup = files.backup("settings.json")

print(settings)
print(checksum)
print(backup)
```

Common capabilities include:

- text and binary read/write;
- atomic text/binary/JSON replacement;
- JSON;
- CSV read/write/append/update;
- INI;
- Java-style properties;
- XML;
- practical dependency-free YAML for normal configuration files;
- Markdown/HTML/CSS/JS/RTF/LaTeX-oriented helpers;
- file/folder copy, move, rename, delete, list and discovery;
- backup and checksums;
- CRC32;
- directory size and line counts;
- head/tail/chunked reads;
- binary comparison;
- metadata inspection.

Some complex file ecosystems are intentionally scoped. For example, a small dependency-free PDF helper is not intended to replace a full professional PDF engine, and the practical YAML helper does not claim support for every advanced YAML feature. Exact format boundaries are documented in [Format support](docs/reference/format-support.md).

---

# Application utilities

## Scripts

```python
from YoungLion import ScriptRunner

runner = ScriptRunner(default_interpreter="python")
result = runner.run("tools/example.py", args=["--check"], timeout=30)

print(result.returncode)
print(result.stdout)
```

## Scheduling

```python
from YoungLion import TaskScheduler

scheduler = TaskScheduler()
task_id = scheduler.schedule_task(lambda: print("cleanup"), repeat=False)
scheduler.wait(task_id)
```

## Cache and resilience

```python
from YoungLion import TTLCache, RetryPolicy, CircuitBreaker, RateLimiter

cache = TTLCache(max_size=1000, default_ttl=60)
cache.set("user:42", {"name": "Alice"})

retry = RetryPolicy(attempts=3, base_delay=0.1)
breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)
limiter = RateLimiter(rate=10, capacity=20)
```

## Events, logging, terminal and text

YoungLion also includes `EventBus`, rotating/contextual `Logger`, `Terminal`, `Colors`, `TextProcessor`, and `Stopwatch`. These are standard-library-first utilities intended to cover frequently repeated infrastructure without forcing a separate package for every small task.

See [Utilities API](docs/api/utilities.md), [Colors and Terminal](docs/api/colors-terminal.md), [Caching and resilience](docs/guides/caching-resilience.md), [Scheduler and automation](docs/guides/scheduler-automation.md), and [Logging](docs/guides/logging.md).

---

# Model helpers

The DataModel package also includes specialized helpers that remain DDM-friendly:

- `Range` — bounds, clamping, normalization and subdivision.
- `Vector` — vector math, distance, dot/cross operations and interpolation.
- `Timeline` — time-positioned events and progress.
- `Dataset` — lightweight row-oriented data utilities.
- `Size` and `Point` — common geometry primitives.
- `Color` — RGBA-oriented color helpers.
- `Matrix` — small matrix transformations.
- `TreeDDM` — hierarchical tree structures.
- `SmartCache` / `SC` — fast reusable completion/default templates.
- `DDMBuilder` — fluent construction of nested structures.

See [Model helpers](docs/api/models.md) and [SmartCache and Builder](docs/api/cache-builder.md).

---

# Typing and IDE support

YoungLion ships as a PEP 561 typed package:

- `src/YoungLion/py.typed` marks inline typing support;
- public Python modules have `.pyi` interfaces;
- the native C++ extension has `_native.pyi`;
- collection classes expose generic type parameters where useful;
- overloads describe path defaults, slicing, dictionary access, and common collection operations;
- `tools/check_stub_coverage.py` structurally checks that public source classes/functions/methods remain represented in the corresponding stubs.

Run the audit with:

```bash
python tools/check_stub_coverage.py
```

The structural audit complements—not replaces—mypy, Pyright, an IDE type engine, and real runtime tests. Read [docs/typing.md](docs/typing.md) and [Stub maintenance](docs/development/stub-maintenance.md).

---

# Performance philosophy

YoungLion does **not** assume that rewriting everything in C++ is automatically better. Native code is used where it can reduce Python-level loop overhead, repeated parsing/traversal, or expensive index work. Python remains the control layer where flexibility is more valuable.

Important design choices include:

- a single-storage DDM design rather than duplicating record fields in two Python dictionaries;
- packed/frozen/view variants for different memory or mutability requirements;
- native recursive serialization and path helpers;
- persistent search indexes for repeated queries;
- shared record stores across DDM path indexes where practical;
- single-pass `BatchPlan` execution for groups of bulk mutations;
- C++ algorithms for stable sort, lower/equal range, binary search, nth selection, partitioning and reductions;
- source distributions containing native source while prebuilt wheels omit C++ source files.

Any benchmark number is workload-dependent. Use the included scripts under `benchmarks/` and follow [Benchmark methodology](docs/performance/benchmark-methodology.md) before making architectural decisions.

---

# Building release artifacts on GitHub

The repository workflow is designed to **build, test, and collect artifacts only**. It does not publish to PyPI and does not need a PyPI token.

A release build ultimately assembles one downloadable artifact:

```text
YoungLion-0.1.1-release-bundle/
├── pypi/
│   ├── younglion-0.1.1.tar.gz
│   └── *.whl
├── experimental/
├── checksums/
│   ├── MANIFEST.json
│   └── SHA256SUMS.txt
└── UPLOAD_TO_PYPI.md
```

Only the stable files under `pypi/` are intended for the normal manual upload flow. Preview/interpreter/platform builds stay separated under `experimental/`.

Typical manual release check:

```bash
cd pypi
python -m twine check *
python -m twine upload *
```

See [CI](docs/development/ci.md), [Release bundle](docs/development/release-bundle.md), [Packaging](docs/development/packaging.md), and [Manual PyPI publishing](docs/development/manual-pypi-publish.md).

---

# Real-life examples

A separate archive—not part of the main repository tree—contains **70 standalone real-life mini projects**. They cover DDM modeling, collection-scale batch operations, nested-path search, application search, file formats, automation, resilience, terminal/text tools, and combined local applications.

Each numbered example has its own `README.md` and executable `main.py`, for example:

```text
31_ddm_exact_user_search/
├── README.md
└── main.py
```

The examples are intentionally kept outside `tree/main` so the core repository remains focused. They are validated against the v0.1 source during release preparation.

---

# Documentation

Start at **[docs/index.md](docs/index.md)**. The documentation includes:

- installation and quick start;
- architecture;
- complete API references;
- DDM and every DDM variant;
- collection/batch operations;
- DDM indexes and application search;
- search algorithm reference;
- file format support and file workflows;
- utilities and thread-safety notes;
- typing/stub maintenance;
- memory/performance guides;
- build, CI and packaging;
- release bundle and manual PyPI upload;
- security notes;
- troubleshooting, FAQ and migration guidance;
- generated public API signatures.

---

# Development checks

Useful local checks:

```bash
# Native extension
YOUNGLION_STRICT=1 python setup.py build_ext --inplace --force

# Tests
PYTHONPATH=src python -m pytest -q

# Stub/source structural coverage
python tools/check_stub_coverage.py

# Build distributions
python -m build
```

The GitHub CI matrix additionally tests supported operating-system/distribution targets and wheel construction.

---

# Project layout

```text
YoungLionPythonLibrary/
├── .github/workflows/        # CI and artifact builds
├── benchmarks/               # performance experiments
├── docs/                     # full documentation
├── src/YoungLion/
│   ├── DataModel/            # DDM core, variants, collections and models
│   ├── function/             # File and application utilities
│   ├── _native.cpp           # native extension entry point
│   ├── _native_*.inc         # native implementation units
│   ├── _native.pyi           # native type interface
│   ├── search.py             # search stack
│   ├── search.pyi
│   ├── Colors.py
│   └── py.typed
├── tests/
├── tools/
├── pyproject.toml
├── setup.py
└── README.md
```

---

# Compatibility and dependency policy

- Stable Python target: **CPython 3.10–3.14**.
- Native language level: **C++17**.
- Core runtime third-party Python dependencies: **none required**.
- Developer/build dependencies are separate from runtime dependencies.
- Complex optional protocols/formats are not silently emulated through undeclared packages.

Read [Compatibility](docs/development/compatibility.md) for the exact support policy.

---

# Contributing

Before proposing changes:

1. keep existing public compatibility unless a change is deliberately documented;
2. update `.pyi` files with public API changes;
3. add tests for behavior and regression cases;
4. update the canonical docs, not only a compatibility redirect page;
5. run the stub audit and normal test suite;
6. avoid adding required runtime dependencies without a strong architectural reason.

See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/development/contributing.md](docs/development/contributing.md).

---

# License

YoungLion is distributed under the **MIT License**. See [LICENSE](LICENSE).
