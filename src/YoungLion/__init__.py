"""YoungLion — native-accelerated, dependency-free Python developer toolkit.

Overview
--------
YoungLion combines dynamic data modeling, high-throughput DDM collections,
ranked/fuzzy/application search, filesystem and structured-format helpers, and a
set of focused application utilities behind one import surface. Performance-
sensitive DDM, file and search operations are backed by the bundled C++17 CPython
extension while the public API remains ordinary Python.

Major areas
-----------
Data modeling
    ``DDM`` and its specialized variants provide hierarchical JSON-like data,
    dotted-path access, recursive serialization, schema validation, cloning,
    transformation and subclass-friendly typed domain models.

Collections and algorithms
    ``ListDDM``, ``SetDDM``, ``DictDDM``, ``DDMTable`` and ``BatchPlan`` provide
    record-oriented bulk operations, native path transforms/reductions and
    selected C++-style algorithms for large DDM-compatible datasets.

Search
    ``SearchIndex``, ``BM25Index``, ``ApplicationSearch`` and
    ``DDMSearchEngine`` cover ranked text retrieval, fuzzy matching,
    autocomplete, structured queries and reusable nested-path indexes.

Files and formats
    ``File`` exposes core filesystem operations, atomic persistence, JSON/text/
    binary helpers and lightweight CSV/XML/YAML-like/INI/properties/PDF/script
    workflows without mandatory runtime dependencies.

Application utilities
    Script execution, scheduling, logging, e-mail, transfer tracking, text
    processing, events, TTL caching, rate limiting, retries, circuit breaking,
    timing, ANSI colors and terminal rendering are available from the package
    root for interactive discoverability.

Interactive discovery
---------------------
The runtime implementation intentionally carries detailed module, class and
method docstrings.  ``help(YoungLion)``, ``help(DDM)``, IDLE call tips and IDE
hover/introspection can therefore explain the public API even when the external
``docs/`` tree is not open.

Example
-------
    from YoungLion import DDM, ListDDM, DDMSearchEngine, File, Logger

    class UserProfile(DDM):
        def __init__(self, data):
            super().__init__(data)
            self.name: str = str(data.get("name", "Unknown"))

    class User(DDM):
        def __init__(self, data):
            super().__init__(data)
            self.id: int = int(data.get("id", 0))
            self.profile: UserProfile = UserProfile(data.get("profile", {}))

    users = ListDDM([User({"id": 1, "profile": {"name": "Alice"}})])
    search = DDMSearchEngine(users).create_index("profile.name")
    assert search.find_one("profile.name", "Alice").id == 1

Notes
-----
YoungLion targets CPython and ships native code.  Platform/interpreter support is
therefore determined by the wheels produced for a release or by the availability
of a compatible C++17 toolchain when installing from source.
"""

__version__ = "0.1.1"
__author__ = "Cavanşir Qurbanzadə"
__author_email__ = "cavanshirpro@gmail.com"
__url__ = "https://github.com/Cavanshirpro/YoungLionPythonLibrary"

author = {
    "name": "Cavanşir",
    "surname": "Qurbanzadə",
    "username": "cavanshirpro",
    "email": "cavanshirpro@gmail.com",
}

# Keep the historical import surface. DataModel/function resolve to the new
# packages, whose hot paths are backed by YoungLion._native (C++17).
from .function import *
try:
    from .search import *
except ImportError:
    pass
from .DataModel import *
try:
    from .Colors import *
except ImportError:
    pass
