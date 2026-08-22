"""YoungLion.DataModel — dynamic, typed-friendly and high-throughput data modeling.

Overview
--------
The DataModel package is the structured-data core of YoungLion.  Its central
abstraction, :class:`DDM` (Dynamic Data Model), keeps JSON-like mappings easy to
inspect and mutate while providing recursive serialization, dotted-path access,
schema validation, cloning, transformations and native C++ accelerated hot paths.

DDM is intentionally subclass-friendly.  Applications can keep the flexibility
of dynamic input while exposing domain-specific attributes such as ``User``,
``UserProfile`` or ``Order`` with normal Python type annotations and methods.
Specialized variants cover immutable values, identity semantics, packed storage,
schema enforcement, default values, lazy fields and zero-copy views.

The package also provides DDM-aware collections for large datasets, builder/cache
utilities and reusable mathematical/data structures such as Range, Vector,
Timeline, Dataset, Size, Point, Color, Matrix and TreeDDM.

Recommended discovery path
--------------------------
1. Start with :class:`DDM` for ordinary hierarchical application data.
2. Subclass DDM for domain models when IDE-visible typed attributes are useful.
3. Use ListDDM/DictDDM/SetDDM and BatchPlan for high-volume operations.
4. Choose a specialized DDM variant only when its semantic trade-off is needed.
5. Pair large collections with :class:`YoungLion.DDMSearchEngine` for reusable
   dotted-path indexes.

All public APIs are documented in their runtime docstrings so ``help()``, IDLE,
interactive shells and IDE hovers remain useful without opening external docs.
"""
from ._core import DDM
from ._models import Range, Vector, Timeline, Dataset, Size, Point, Color, Matrix, TreeDDM
from ._variants import FrozenDDM, IdentityDDM, PackedDDM, SchemaDDM, DefaultDDM, LazyDDM, ViewDDM
from ._collections import ListDDM, SetDDM, DictDDM, DDMTable, DDMCollectionOps, BatchPlan
from ._cache import (
    SmartCache, SC, DDMBuilder, merge_ddms, compare_ddms, batch_transform,
    batch_filter, validate_ddm_batch, analyze_ddm_structure, get_ddm_size_info,
    create_smart_cache, fast_complete, batch_complete_fast,
)

__all__ = [
    "DDM", "FrozenDDM", "IdentityDDM", "PackedDDM", "SchemaDDM", "DefaultDDM", "LazyDDM", "ViewDDM",
    "ListDDM", "SetDDM", "DictDDM", "DDMTable", "DDMCollectionOps", "BatchPlan",
    "Range", "Vector", "Timeline", "Dataset", "Size", "Point", "Color", "Matrix", "TreeDDM", "SmartCache", "SC", "DDMBuilder",
    "merge_ddms", "compare_ddms", "batch_transform", "batch_filter", "validate_ddm_batch",
    "analyze_ddm_structure", "get_ddm_size_info", "create_smart_cache", "fast_complete", "batch_complete_fast",
]

# Preserve less-used legacy public names without overriding native replacements.
try:
    import importlib.util as _importlib_util
    from pathlib import Path as _Path
    _legacy_path = _Path(__file__).resolve().parent.parent / "DataModel.py"
    if _legacy_path.exists():
        _spec = _importlib_util.spec_from_file_location("YoungLion._legacy_datamodel", _legacy_path)
        if _spec and _spec.loader:
            _legacy = _importlib_util.module_from_spec(_spec)
            _spec.loader.exec_module(_legacy)
            for _name, _value in vars(_legacy).items():
                if not _name.startswith("_") and _name not in globals():
                    globals()[_name] = _value
                    __all__.append(_name)
except Exception:
    pass
