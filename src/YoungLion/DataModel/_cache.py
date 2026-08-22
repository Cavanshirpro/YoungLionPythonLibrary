"""DataModel cache, builder and batch utility helpers.

This module complements DDM with :class:`SmartCache`, a template-driven completion
helper; :class:`DDMBuilder`, a fluent constructor; and convenience functions for
merging, comparing, transforming, filtering, validating and inspecting DDM
objects.  The functions are intentionally small orchestration utilities built on
top of the public DDM contract so they remain easy to compose in scripts and
services.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Mapping

from .. import _native
from ._core import DDM

class SmartCache:
    """Template-driven record completion cache.
    
    Overview
    --------
    ``SmartCache`` provides fast completion of sparse mappings against a reusable template plus completion statistics.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use when many records should be normalized to a known key structure.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    complete, complete_batch, get_missing_keys, get_extra_keys, completion_report, update_template, get_stats, reset_stats.
    """
    def __init__(self, template: Mapping[str, Any]):
        """Initialize a new SmartCache instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`SmartCache` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        template : Mapping[str, Any]
            Reference mapping whose keys/default values define the completion shape.
        """
        if not isinstance(template, Mapping):
            raise TypeError("template must be a mapping")
        self.template = dict(template)
        self._completed = 0
        self._filled = 0

    def complete(self, raw_data: Mapping[str, Any]) -> Dict[str, Any]:
        """Complete one sparse record from the cache template without mutating the caller's input.
        
        Details
        -------
        This method belongs to :class:`SmartCache` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        raw_data : Mapping[str, Any]
            Sparse/source mapping to inspect or complete.
        
        Returns
        -------
        ``Dict[str, Any]`` result described by the method semantics.
        """
        result = _native.cache_complete(self.template, dict(raw_data))
        self._completed += 1
        self._filled += len(_native.cache_missing(self.template, dict(raw_data)))
        return result

    fill = complete

    def complete_batch(self, records: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
        """Complete many sparse records using the same reusable template.
        
        Details
        -------
        This method belongs to :class:`SmartCache` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        records : Iterable[Mapping[str, Any]]
            Input records for structured/DDM collection indexing.
        
        Returns
        -------
        ``List[Dict[str, Any]]`` result described by the method semantics.
        """
        return [self.complete(record) for record in records]

    fill_batch = complete_batch

    def get_missing_keys(self, raw_data: Mapping[str, Any]) -> List[str]:
        """Return template keys that are absent from the supplied record.
        
        Details
        -------
        This method belongs to :class:`SmartCache` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        raw_data : Mapping[str, Any]
            Sparse/source mapping to inspect or complete.
        
        Returns
        -------
        ``List[str]`` result described by the method semantics.
        """
        return list(_native.cache_missing(self.template, dict(raw_data)))

    def get_extra_keys(self, raw_data: Mapping[str, Any]) -> List[str]:
        """Return input keys that are not present in the current template.
        
        Details
        -------
        This method belongs to :class:`SmartCache` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        raw_data : Mapping[str, Any]
            Sparse/source mapping to inspect or complete.
        
        Returns
        -------
        ``List[str]`` result described by the method semantics.
        """
        return list(_native.cache_extra(self.template, dict(raw_data)))

    def completion_report(self, raw_data: Mapping[str, Any]) -> Dict[str, Any]:
        """Describe how a record differs from the template before completion.
        
        Details
        -------
        This method belongs to :class:`SmartCache` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        raw_data : Mapping[str, Any]
            Sparse/source mapping to inspect or complete.
        
        Returns
        -------
        ``Dict[str, Any]`` result described by the method semantics.
        """
        missing = self.get_missing_keys(raw_data)
        extra = self.get_extra_keys(raw_data)
        return {"missing_keys": missing, "extra_keys": extra, "complete": not missing, "missing_count": len(missing), "extra_count": len(extra)}

    def update_template(self, new_template: Mapping[str, Any]) -> "SmartCache":
        """Replace the reusable completion template and refresh internal cache state.
        
        Details
        -------
        This method belongs to :class:`SmartCache` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        new_template : Mapping[str, Any]
            Value supplied for ``new_template`` according to the SmartCache contract.
        
        Returns
        -------
        ``'SmartCache'`` result described by the method semantics.
        """
        self.template = dict(new_template)
        return self

    def get_stats(self) -> Dict[str, int]:
        """Return current counters/statistics collected by this object.
        
        Details
        -------
        This method belongs to :class:`SmartCache` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``Dict[str, int]`` result described by the method semantics.
        """
        return {"completed": self._completed, "filled_keys": self._filled, "template_keys": len(self.template)}

    def reset_stats(self) -> None:
        """Reset accumulated statistics without changing the primary configured data.
        
        Details
        -------
        This method belongs to :class:`SmartCache` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        """
        self._completed = 0
        self._filled = 0


SC = SmartCache


class DDMBuilder:
    """Fluent DDM construction helper.
    
    Overview
    --------
    ``DDMBuilder`` provides chainable setting, nested construction and list assignment.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use when programmatic construction is clearer as a fluent pipeline than as nested dict literals.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    set, set_many, nest, add_list, build.
    """
    def __init__(self):
        """Initialize a new DDMBuilder instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`DDMBuilder` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        """
        self._data: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> "DDMBuilder":
        """Add a field assignment to the builder/plan and return self for fluent chaining.
        
        Details
        -------
        This method belongs to :class:`DDMBuilder` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        key : str
            Mapping key or uniqueness key.
        value : Any
            Target, new or comparison value.
        
        Returns
        -------
        ``'DDMBuilder'`` result described by the method semantics.
        """
        self._data[key] = value
        return self

    def set_many(self, **kwargs: Any) -> "DDMBuilder":
        """Add several top-level field assignments in one fluent builder call.
        
        Details
        -------
        This method belongs to :class:`DDMBuilder` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        
        Returns
        -------
        ``'DDMBuilder'`` result described by the method semantics.
        """
        self._data.update(kwargs)
        return self

    def nest(self, key: str, builder_func: Callable[["DDMBuilder"], Any]) -> "DDMBuilder":
        """Create and assign a nested DDM through a child builder callback.
        
        Details
        -------
        This method belongs to :class:`DDMBuilder` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        key : str
            Mapping key or uniqueness key.
        builder_func : Callable[['DDMBuilder'], Any]
            Value supplied for ``builder_func`` according to the DDMBuilder contract.
        
        Returns
        -------
        ``'DDMBuilder'`` result described by the method semantics.
        """
        nested = DDMBuilder()
        result = builder_func(nested)
        nested = result if isinstance(result, DDMBuilder) else nested
        self._data[key] = nested.build().to_dict()
        return self

    def add_list(self, key: str, values: Iterable[Any]) -> "DDMBuilder":
        """Assign a list value through the fluent DDM builder.
        
        Details
        -------
        This method belongs to :class:`DDMBuilder` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        key : str
            Mapping key or uniqueness key.
        values : Iterable[Any]
            Input iterable, mapping values or composite lookup values.
        
        Returns
        -------
        ``'DDMBuilder'`` result described by the method semantics.
        """
        self._data[key] = list(values)
        return self

    def build(self) -> DDM:
        """Materialize and return the DDM represented by the builder state.
        
        Details
        -------
        This method belongs to :class:`DDMBuilder` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``DDM`` result described by the method semantics.
        """
        return DDM(_native.ddm_clone_data(DDM(self._data)))


def merge_ddms(*ddms: DDM) -> DDM:
    """Merge multiple DDM objects into one new DDM using DDM merge semantics in argument order.
    
    Parameters
    ----------
    *ddms : DDM
        Value supplied for ``ddms`` according to the function contract.
    
    Returns
    -------
    ``DDM`` result described by the method semantics.
    """
    result = DDM({})
    for item in ddms:
        result.merge(item)
    return result


def compare_ddms(ddm1: DDM, ddm2: DDM) -> Dict[str, Any]:
    """Compare two DDM objects and return a structured summary of equality/differences.
    
    Parameters
    ----------
    ddm1 : DDM
        Value supplied for ``ddm1`` according to the function contract.
    ddm2 : DDM
        Value supplied for ``ddm2`` according to the function contract.
    
    Returns
    -------
    ``Dict[str, Any]`` result described by the method semantics.
    """
    diff = ddm1.diff(ddm2)
    return {"equal": not diff, "differences": diff}


def batch_transform(ddms: Iterable[DDM], transformer: Callable[[DDM], Any]) -> List[Any]:
    """Apply a transformer callable to every DDM in an iterable and return the transformed batch.
    
    Parameters
    ----------
    ddms : Iterable[DDM]
        Value supplied for ``ddms`` according to the function contract.
    transformer : Callable[[DDM], Any]
        Value supplied for ``transformer`` according to the function contract.
    
    Returns
    -------
    ``List[Any]`` result described by the method semantics.
    """
    return [transformer(ddm) for ddm in ddms]


def batch_filter(ddms: Iterable[DDM], predicate: Callable[[DDM], bool]) -> List[DDM]:
    """Return only DDM objects for which the predicate evaluates truthfully.
    
    Parameters
    ----------
    ddms : Iterable[DDM]
        Value supplied for ``ddms`` according to the function contract.
    predicate : Callable[[DDM], bool]
        Callable returning truthy for records that should match/be selected.
    
    Returns
    -------
    ``List[DDM]`` result described by the method semantics.
    """
    return [ddm for ddm in ddms if predicate(ddm)]


def validate_ddm_batch(ddms: Iterable[DDM], schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Validate every DDM in a batch against the same schema and return per-item results.
    
    Parameters
    ----------
    ddms : Iterable[DDM]
        Value supplied for ``ddms`` according to the function contract.
    schema : Dict[str, Any]
        Schema mapping describing expected fields/types/constraints.
    
    Returns
    -------
    ``List[Dict[str, Any]]`` result described by the method semantics.
    """
    return [ddm.validate_schema(schema) for ddm in ddms]


def analyze_ddm_structure(ddm: DDM) -> Dict[str, Any]:
    """Inspect a DDM and return structural information useful for diagnostics and schema understanding.
    
    Parameters
    ----------
    ddm : DDM
        Value supplied for ``ddm`` according to the function contract.
    
    Returns
    -------
    ``Dict[str, Any]`` result described by the method semantics.
    """
    flat = ddm.to_flat_dict()
    return {"keys": len(ddm), "leaf_values": len(flat), "types": {k: type(v).__name__ for k, v in flat.items()}}


def get_ddm_size_info(ddm: DDM) -> Dict[str, int]:
    """Return approximate size/memory metrics for a DDM.
    
    Parameters
    ----------
    ddm : DDM
        Value supplied for ``ddm`` according to the function contract.
    
    Returns
    -------
    ``Dict[str, int]`` result described by the method semantics.
    """
    data = ddm.to_dict()
    encoded = _native.json_dumps(data, indent=-1).encode("utf-8")
    return {"keys": len(data), "json_bytes": len(encoded)}


def create_smart_cache(template: Mapping[str, Any]) -> SmartCache:
    """Construct and return a SmartCache from a completion template.
    
    Parameters
    ----------
    template : Mapping[str, Any]
        Reference mapping whose keys/default values define the completion shape.
    
    Returns
    -------
    ``SmartCache`` result described by the method semantics.
    """
    return SmartCache(template)


def fast_complete(template: Mapping[str, Any], raw_data: Mapping[str, Any]) -> Dict[str, Any]:
    """Complete one sparse mapping against a template using a short-lived SmartCache convenience path.
    
    Parameters
    ----------
    template : Mapping[str, Any]
        Reference mapping whose keys/default values define the completion shape.
    raw_data : Mapping[str, Any]
        Sparse/source mapping to inspect or complete.
    
    Returns
    -------
    ``Dict[str, Any]`` result described by the method semantics.
    """
    return _native.cache_complete(dict(template), dict(raw_data))


def batch_complete_fast(template: Mapping[str, Any], records: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """Complete many sparse mappings against one template using a shared SmartCache.
    
    Parameters
    ----------
    template : Mapping[str, Any]
        Reference mapping whose keys/default values define the completion shape.
    records : Iterable[Mapping[str, Any]]
        Input records for structured/DDM collection indexing.
    
    Returns
    -------
    ``List[Dict[str, Any]]`` result described by the method semantics.
    """
    t = dict(template)
    return [_native.cache_complete(t, dict(record)) for record in records]


