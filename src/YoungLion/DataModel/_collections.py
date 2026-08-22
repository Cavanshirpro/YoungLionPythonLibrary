"""High-throughput DDM-aware collection types and bulk algorithms.

This module provides ListDDM, SetDDM, DictDDM and DDMTable together with the
shared :class:`DDMCollectionOps` operation surface.  The collection layer is
optimized for workloads containing many DDM-compatible records and supports
native dotted-path extraction, filtering, numeric transforms/reductions,
partitioning, stable sorting, binary-search style algorithms, grouping,
deduplication, chunking and search-index construction.

:class:`BatchPlan` is the preferred tool when several simple mutations must be
applied to every record.  It compiles a sequence of set/add/subtract/multiply/
divide/clamp operations and lets the native extension execute them in one pass,
reducing repeated Python-to-native traversal overhead.

These classes intentionally resemble built-in collections where practical while
adding record-oriented operations that ordinary list/set/dict types do not
provide.  Operations that mutate records invalidate cached search indexes so
callers do not accidentally query stale collection-managed indexes.
"""
from __future__ import annotations

import functools
import heapq
import random
from collections import Counter, defaultdict
from collections.abc import Iterable, Iterator, Mapping, MutableMapping, MutableSequence
from typing import Any, Callable, Dict, Generic, Hashable, List, Optional, Sequence, Tuple, TypeVar, Union, overload

from .. import _native
from ._core import DDM, _MISSING
from ._variants import FrozenDDM, PackedDDM, ViewDDM

D = TypeVar("D")
K = TypeVar("K", bound=Hashable)


def _as_ddm(value: Any) -> Any:
    if isinstance(value, (DDM, PackedDDM, FrozenDDM, ViewDDM)):
        return value
    if isinstance(value, Mapping):
        return DDM(value)
    if hasattr(value, "get_path") and hasattr(value, "to_dict"):
        return value
    raise TypeError("collection values must be DDM-compatible objects or mappings")


def _stable_key(value: Any) -> Any:
    try:
        hash(value)
        return value
    except TypeError:
        if isinstance(value, Mapping):
            return tuple(sorted((str(k), _stable_key(v)) for k, v in value.items()))
        if isinstance(value, (list, tuple)):
            return tuple(_stable_key(v) for v in value)
        if isinstance(value, set):
            return frozenset(_stable_key(v) for v in value)
        return repr(value)


class BatchPlan:
    """Compiled bulk mutation plan.
    
    Overview
    --------
    ``BatchPlan`` provides multiple simple dotted-path mutations executed in a single native collection pass.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use when applying several arithmetic/set operations to every record in a large collection.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    set, add, subtract, multiply, divide, clamp, clear, execute.
    """

    __slots__ = ("_operations",)

    def __init__(self):
        """Initialize a new BatchPlan instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`BatchPlan` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        """
        self._operations: List[tuple] = []

    def set(self, path: str, value: Any) -> "BatchPlan":
        """Add a field assignment to the builder/plan and return self for fluent chaining.
        
        Details
        -------
        This method belongs to :class:`BatchPlan` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any
            Target, new or comparison value.
        
        Returns
        -------
        ``'BatchPlan'`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        self._operations.append(("set", path, value)); return self

    def add(self, path: str, amount: float = 1.0) -> "BatchPlan":
        """Add a value/record/operation to the current object according to its collection or numeric semantics.
        
        Details
        -------
        This method belongs to :class:`BatchPlan` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        amount : float (default: ``1.0``)
            Numeric amount to add or subtract.
        
        Returns
        -------
        ``'BatchPlan'`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        self._operations.append(("add", path, float(amount))); return self

    def subtract(self, path: str, amount: float = 1.0) -> "BatchPlan":
        """Subtract another value or queue a subtraction operation.
        
        Details
        -------
        This method belongs to :class:`BatchPlan` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        amount : float (default: ``1.0``)
            Numeric amount to add or subtract.
        
        Returns
        -------
        ``'BatchPlan'`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        self._operations.append(("sub", path, float(amount))); return self

    sub = subtract

    def multiply(self, path: str, factor: float) -> "BatchPlan":
        """Multiply the addressed numeric values by a factor.
        
        Details
        -------
        This method belongs to :class:`BatchPlan` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        factor : float
            Numeric scaling/multiplication factor.
        
        Returns
        -------
        ``'BatchPlan'`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        self._operations.append(("mul", path, float(factor))); return self

    mul = multiply

    def divide(self, path: str, divisor: float) -> "BatchPlan":
        """Divide the addressed numeric values by a divisor.
        
        Details
        -------
        This method belongs to :class:`BatchPlan` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        divisor : float
            Numeric divisor; zero is invalid.
        
        Returns
        -------
        ``'BatchPlan'`` result described by the method semantics.
        
        Raises
        ------
        ZeroDivisionError/ValueError
            If the supplied divisor is zero, according to the native/Python operation path.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        if divisor == 0: raise ZeroDivisionError("division by zero")
        self._operations.append(("div", path, float(divisor))); return self

    div = divide

    def clamp(self, path: str, minimum: float, maximum: float) -> "BatchPlan":
        """Constrain a value or all addressed numeric values to the supplied inclusive bounds.
        
        Details
        -------
        This method belongs to :class:`BatchPlan` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        minimum : float
            Lower bound or minimum accepted value.
        maximum : float
            Upper bound or maximum accepted value.
        
        Returns
        -------
        ``'BatchPlan'`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        if minimum > maximum: raise ValueError("minimum cannot exceed maximum")
        self._operations.append(("clamp", path, float(minimum), float(maximum))); return self

    def clear(self) -> "BatchPlan":
        """Remove all currently stored entries or queued operations, depending on the owning class.
        
        Details
        -------
        This method belongs to :class:`BatchPlan` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``'BatchPlan'`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        self._operations.clear(); return self

    def __len__(self) -> int: return len(self._operations)

    def execute(self, collection: Any) -> int:
        """Execute the queued batch plan against a DDM-aware collection.
        
        Details
        -------
        This method belongs to :class:`BatchPlan` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        collection : Any
            Value supplied for ``collection`` according to the BatchPlan contract.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        Queued operations are passed to the native collection routine together so each record can be visited once. This is most beneficial when several simple path mutations would otherwise require repeated full scans.
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        items = collection._items_snapshot() if hasattr(collection, "_items_snapshot") else list(collection)
        changed = int(_native.batch_mutate(items, self._operations))
        if hasattr(collection, "_invalidate_indexes"):
            collection._invalidate_indexes([op[1] for op in self._operations])
        return changed


class DDMCollectionOps:
    """Shared DDM collection operation surface.
    
    Overview
    --------
    ``DDMCollectionOps`` provides bulk path access, transforms, reductions, algorithms and search integration.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Inherited by ListDDM/SetDDM/DictDDM/DDMTable; normally use those concrete containers.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    batch, path_values, set_all, apply_path, map, for_each, reduce, filter, filter_path, first, first_path, any, all, exists_path, count_path, partition_path ....
    """

    def _items_snapshot(self) -> List[Any]:
        raise NotImplementedError

    def _replace_items(self, items: Sequence[Any]) -> None:
        raise NotImplementedError

    def _invalidate_indexes(self, paths: Optional[Iterable[str]] = None) -> None:
        pass

    def batch(self) -> BatchPlan:
        """Return a new BatchPlan for composing several one-pass mutations.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``BatchPlan`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        return BatchPlan()

    def path_values(self, path: str, default: Any = None) -> List[Any]:
        """Extract the value at the same dotted path from every collection record.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.
        
        Returns
        -------
        ``List[Any]`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        return _native.batch_get_path(self._items_snapshot(), path, default)

    pluck = path_values

    def set_all(self, path: str, value: Any) -> int:
        """Set one dotted path to the same value across every collection record.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any
            Target, new or comparison value.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        items = self._items_snapshot()
        changed = int(_native.batch_set_path(items, path, value))
        self._invalidate_indexes([path])
        return changed

    def apply_path(self, path: str, func: Callable[[Any], Any], *, write_back: bool = True) -> List[Any]:
        """Apply a callable to a dotted-path value for each record, optionally writing transformed values back.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        func : Callable[[Any], Any]
            Callable applied by the operation.
        write_back : bool (default: ``True``)
            When True, store transformed values back into records; otherwise only return results.
        
        Returns
        -------
        ``List[Any]`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        items = self._items_snapshot()
        result = _native.batch_apply_path(items, path, func, write_back=write_back)
        if write_back:
            self._invalidate_indexes([path])
        return result

    def map(self, func: Callable[[Any], Any]) -> List[Any]:
        """Apply a callable to every record and return the mapped results.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        func : Callable[[Any], Any]
            Callable applied by the operation.
        
        Returns
        -------
        ``List[Any]`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        return [func(item) for item in self._items_snapshot()]

    def for_each(self, func: Callable[[Any], Any]) -> "DDMCollectionOps":
        """Invoke a callable for every record for side effects.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        func : Callable[[Any], Any]
            Callable applied by the operation.
        
        Returns
        -------
        ``'DDMCollectionOps'`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        for item in self._items_snapshot():
            func(item)
        self._invalidate_indexes()
        return self

    def reduce(self, func: Callable[[Any, Any], Any], initial: Any = _MISSING) -> Any:
        """Fold the collection into one accumulated value.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        func : Callable[[Any, Any], Any]
            Callable applied by the operation.
        initial : Any (default: ``_MISSING``)
            Initial accumulator value for reduction.
        
        Returns
        -------
        ``Any`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        items = self._items_snapshot()
        if initial is _MISSING:
            return functools.reduce(func, items)
        return functools.reduce(func, items, initial)

    def filter(self, predicate: Callable[[Any], bool]) -> List[Any]:
        """Return records for which the supplied predicate evaluates truthfully.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        predicate : Callable[[Any], bool]
            Callable returning truthy for records that should match/be selected.
        
        Returns
        -------
        Collection/list of matching records without modifying non-inplace source state.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        return [item for item in self._items_snapshot() if predicate(item)]

    def filter_path(self, path: str, value: Any = None, *, op: str = "eq") -> List[Any]:
        """Filter records by comparing a dotted-path value with a target using the selected operator.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any (default: ``None``)
            Target, new or comparison value.
        op : str (default: ``'eq'``)
            Comparison operator name such as eq/ne/lt/lte/gt/gte/prefix/contains where supported.
        
        Returns
        -------
        ``List[Any]`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        
        Example::
        
            adults = users.filter_path("profile.age", 18, op="gte")
        """
        return _native.batch_filter_path(self._items_snapshot(), path, op, value)

    where = filter_path

    def first(self, predicate: Optional[Callable[[Any], bool]] = None, default: Any = None) -> Any:
        """Return the first record satisfying a predicate or a caller-provided default.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        predicate : Optional[Callable[[Any], bool]] (default: ``None``)
            Callable returning truthy for records that should match/be selected.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.
        
        Returns
        -------
        ``Any`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        for item in self._items_snapshot():
            if predicate is None or predicate(item):
                return item
        return default

    def first_path(self, path: str, value: Any = None, *, op: str = "eq", default: Any = None) -> Any:
        """Return the first record whose dotted-path value satisfies the requested comparison.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any (default: ``None``)
            Target, new or comparison value.
        op : str (default: ``'eq'``)
            Comparison operator name such as eq/ne/lt/lte/gt/gte/prefix/contains where supported.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.
        
        Returns
        -------
        ``Any`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        matches = self.filter_path(path, value, op=op)
        return matches[0] if matches else default

    def any(self, predicate: Callable[[Any], bool]) -> bool:
        """Return whether at least one record satisfies the predicate.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        predicate : Callable[[Any], bool]
            Callable returning truthy for records that should match/be selected.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        return any(predicate(item) for item in self._items_snapshot())

    def all(self, predicate: Callable[[Any], bool]) -> bool:
        """Return whether every record satisfies the predicate.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        predicate : Callable[[Any], bool]
            Callable returning truthy for records that should match/be selected.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        return all(predicate(item) for item in self._items_snapshot())

    def exists_path(self, path: str, value: Any = None, *, op: str = "eq") -> bool:
        """Return whether any record satisfies a dotted-path comparison.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any (default: ``None``)
            Target, new or comparison value.
        op : str (default: ``'eq'``)
            Comparison operator name such as eq/ne/lt/lte/gt/gte/prefix/contains where supported.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        return self.first_path(path, value, op=op, default=None) is not None

    def count_path(self, path: str, value: Any = None, *, op: str = "eq") -> int:
        """Count records satisfying a dotted-path comparison without allocating a result list.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any (default: ``None``)
            Target, new or comparison value.
        op : str (default: ``'eq'``)
            Comparison operator name such as eq/ne/lt/lte/gt/gte/prefix/contains where supported.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        return int(_native.batch_count_path(self._items_snapshot(), path, op, value))

    def partition_path(self, path: str, value: Any = None, *, op: str = "eq") -> Tuple[List[Any], List[Any]]:
        """Split records into matching and non-matching groups using a dotted-path comparison.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any (default: ``None``)
            Target, new or comparison value.
        op : str (default: ``'eq'``)
            Comparison operator name such as eq/ne/lt/lte/gt/gte/prefix/contains where supported.
        
        Returns
        -------
        ``Tuple[List[Any], List[Any]]`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        matched, rest = _native.batch_partition_path(self._items_snapshot(), path, op, value)
        return matched, rest

    def update_all(self, **values: Any) -> int:
        """Apply the supplied top-level assignments to every collection record.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        **values : Any
            Input iterable, mapping values or composite lookup values.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        count = 0
        for path, value in values.items():
            count = max(count, self.set_all(path, value))
        return count

    def update_where(self, predicate: Callable[[Any], bool], **values: Any) -> int:
        """Update only records satisfying the supplied Python predicate.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        predicate : Callable[[Any], bool]
            Callable returning truthy for records that should match/be selected.
        **values : Any
            Input iterable, mapping values or composite lookup values.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        selected = [item for item in self._items_snapshot() if predicate(item)]
        for path, value in values.items():
            _native.batch_set_path(selected, path, value)
        self._invalidate_indexes(values.keys())
        return len(selected)

    def apply_where(self, predicate: Callable[[Any], bool], path: str, func: Callable[[Any], Any]) -> int:
        """Transform one dotted-path value only on records satisfying a predicate.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        predicate : Callable[[Any], bool]
            Callable returning truthy for records that should match/be selected.
        path : str
            Filesystem path or dotted data path, according to the owning API.
        func : Callable[[Any], Any]
            Callable applied by the operation.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        selected = [item for item in self._items_snapshot() if predicate(item)]
        _native.batch_apply_path(selected, path, func, write_back=True)
        self._invalidate_indexes([path])
        return len(selected)

    def increment(self, path: str, amount: float = 1.0) -> int:
        """Add an amount to the addressed numeric value in every record.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        amount : float (default: ``1.0``)
            Numeric amount to add or subtract.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        
        Example::
        
            users.increment("economy.balance", 25)
        """
        changed = int(_native.batch_numeric_op(self._items_snapshot(), path, "add", float(amount)))
        self._invalidate_indexes([path]); return changed

    def decrement(self, path: str, amount: float = 1.0) -> int:
        """Subtract an amount from the addressed numeric value in every record.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        amount : float (default: ``1.0``)
            Numeric amount to add or subtract.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        changed = int(_native.batch_numeric_op(self._items_snapshot(), path, "sub", float(amount)))
        self._invalidate_indexes([path]); return changed

    def multiply(self, path: str, factor: float) -> int:
        """Multiply the addressed numeric values by a factor.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        factor : float
            Numeric scaling/multiplication factor.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        changed = int(_native.batch_numeric_op(self._items_snapshot(), path, "mul", float(factor)))
        self._invalidate_indexes([path]); return changed

    def divide(self, path: str, divisor: float) -> int:
        """Divide the addressed numeric values by a divisor.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        divisor : float
            Numeric divisor; zero is invalid.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Raises
        ------
        ZeroDivisionError/ValueError
            If the supplied divisor is zero, according to the native/Python operation path.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        changed = int(_native.batch_numeric_op(self._items_snapshot(), path, "div", float(divisor)))
        self._invalidate_indexes([path]); return changed

    def clamp(self, path: str, minimum: float, maximum: float) -> int:
        """Constrain a value or all addressed numeric values to the supplied inclusive bounds.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        minimum : float
            Lower bound or minimum accepted value.
        maximum : float
            Upper bound or maximum accepted value.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        if maximum < minimum:
            raise ValueError("maximum must be >= minimum")
        changed = int(_native.batch_numeric_op(self._items_snapshot(), path, "clamp", float(minimum), float(maximum)))
        self._invalidate_indexes([path]); return changed

    def sum(self, path: str) -> float:
        """Return the numeric sum of values found at the requested dotted path.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        value = _native.batch_numeric_reduce(self._items_snapshot(), path, "sum")
        return 0.0 if value is None else float(value)

    def mean(self, path: str) -> Optional[float]:
        """Return the arithmetic mean of numeric values found at the requested dotted path.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        ``Optional[float]`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        value = _native.batch_numeric_reduce(self._items_snapshot(), path, "mean")
        return None if value is None else float(value)

    def min(self, path: str) -> Optional[float]:
        """Return the minimum numeric value found at the requested dotted path.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        ``Optional[float]`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        value = _native.batch_numeric_reduce(self._items_snapshot(), path, "min")
        return None if value is None else float(value)

    def max(self, path: str) -> Optional[float]:
        """Return the maximum numeric value found at the requested dotted path.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        ``Optional[float]`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        value = _native.batch_numeric_reduce(self._items_snapshot(), path, "max")
        return None if value is None else float(value)

    def numeric_count(self, path: str) -> int:
        """Count records containing numeric data at the requested dotted path.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        return int(_native.batch_numeric_reduce(self._items_snapshot(), path, "count"))

    def sort_by(self, path: str, *, reverse: bool = False, missing_last: bool = True, inplace: bool = False):
        """Sort records by a column/dotted path with explicit missing-value and in-place behavior.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.
        missing_last : bool (default: ``True``)
            Whether records lacking the sort path should be placed after records with values.
        inplace : bool (default: ``False``)
            When True, mutate/reorder the collection itself where supported.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        ordered = _native.batch_sort_path(self._items_snapshot(), path, reverse=reverse, missing_last=missing_last)
        if inplace:
            self._replace_items(ordered)
            self._invalidate_indexes()
            return self
        return ordered

    def is_sorted(self, path: str, *, reverse: bool = False) -> bool:
        """Check whether records are already ordered by the requested dotted path.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        return bool(_native.batch_is_sorted_path(self._items_snapshot(), path, reverse))

    def lower_bound(self, path: str, value: Any, *, reverse: bool = False, verify_sorted: bool = True) -> int:
        """Return the insertion boundary for a value in records sorted by the requested path.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any
            Target, new or comparison value.
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.
        verify_sorted : bool (default: ``True``)
            Whether to validate sorted-order preconditions before a binary-search style operation.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        items = self._items_snapshot()
        if verify_sorted and not _native.batch_is_sorted_path(items, path, reverse):
            raise ValueError("collection must be sorted by the requested path")
        return int(_native.batch_lower_bound_path(items, path, value, reverse))

    def equal_range(self, path: str, value: Any, *, reverse: bool = False, verify_sorted: bool = True) -> Tuple[int, int]:
        """Return the half-open range of positions containing values equal to the target in sorted records.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any
            Target, new or comparison value.
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.
        verify_sorted : bool (default: ``True``)
            Whether to validate sorted-order preconditions before a binary-search style operation.
        
        Returns
        -------
        ``Tuple[int, int]`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        items = self._items_snapshot()
        if verify_sorted and not _native.batch_is_sorted_path(items, path, reverse):
            raise ValueError("collection must be sorted by path before equal_range")
        start, end = _native.batch_equal_range_path(items, path, value, reverse)
        return int(start), int(end)

    def binary_search(self, path: str, value: Any, *, reverse: bool = False, verify_sorted: bool = True) -> int:
        """Locate a target value in records sorted by the requested dotted path.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any
            Target, new or comparison value.
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.
        verify_sorted : bool (default: ``True``)
            Whether to validate sorted-order preconditions before a binary-search style operation.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        items = self._items_snapshot()
        if verify_sorted and not _native.batch_is_sorted_path(items, path, reverse):
            raise ValueError("collection must be sorted by path before binary_search")
        return int(_native.batch_binary_search_path(items, path, value, reverse))

    def nth(self, path: str, n: int, *, largest: bool = False) -> Any:
        """Select the record at an order-statistic position without requiring a full Python-side sort.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        n : int
            Requested count, rank or n-gram width depending on the API.
        largest : bool (default: ``False``)
            Whether order-statistic selection counts from the largest side.
        
        Returns
        -------
        ``Any`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        return _native.batch_nth_path(self._items_snapshot(), path, n, largest=largest)

    def top(self, path: str, n: int = 10, *, largest: bool = True) -> List[Any]:
        """Return the highest-ranked records for a dotted-path value.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        n : int (default: ``10``)
            Requested count, rank or n-gram width depending on the API.
        largest : bool (default: ``True``)
            Whether order-statistic selection counts from the largest side.
        
        Returns
        -------
        ``List[Any]`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        if n <= 0:
            return []
        items = self._items_snapshot()
        sentinel = object()
        key = lambda item: _native.ddm_get_path(item, path, sentinel)
        usable = [item for item in items if key(item) is not sentinel]
        fn = heapq.nlargest if largest else heapq.nsmallest
        return fn(n, usable, key=key)

    def bottom(self, path: str, n: int = 10) -> List[Any]:
        """Return the lowest-ranked records for a dotted-path value.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        n : int (default: ``10``)
            Requested count, rank or n-gram width depending on the API.
        
        Returns
        -------
        ``List[Any]`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        return self.top(path, n, largest=False)

    def group_by(self, path: str, default: Any = None) -> Dict[Any, List[Any]]:
        """Group records or values by the requested field/callback and return the resulting buckets.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.
        
        Returns
        -------
        ``Dict[Any, List[Any]]`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        groups: Dict[Any, List[Any]] = defaultdict(list)
        items = self._items_snapshot()
        for item, value in zip(items, _native.batch_get_path(items, path, default)):
            groups[_stable_key(value)].append(item)
        return dict(groups)

    def count_by(self, path: str, default: Any = None) -> Counter:
        """Count records per distinct dotted-path value.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.
        
        Returns
        -------
        ``Counter`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        return Counter(_stable_key(v) for v in self.path_values(path, default))

    def distinct(self, path: str, default: Any = None) -> List[Any]:
        """Return distinct values observed at a dotted path while preserving supported collection semantics.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.
        
        Returns
        -------
        ``List[Any]`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        seen = set(); out = []
        for value in self.path_values(path, default):
            key = _stable_key(value)
            if key not in seen:
                seen.add(key); out.append(value)
        return out

    def deduplicate(self, path: Optional[str] = None, *, inplace: bool = False):
        """Remove duplicate records/keys according to a dotted path.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : Optional[str] (default: ``None``)
            Filesystem path or dotted data path, according to the owning API.
        inplace : bool (default: ``False``)
            When True, mutate/reorder the collection itself where supported.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        seen = set(); out = []
        sentinel = object()
        for item in self._items_snapshot():
            value = item.to_dict() if path is None else _native.ddm_get_path(item, path, sentinel)
            key = _stable_key(value)
            if key in seen: continue
            seen.add(key); out.append(item)
        if inplace:
            self._replace_items(out); self._invalidate_indexes(); return self
        return out

    def partition(self, predicate: Callable[[Any], bool]) -> Tuple[List[Any], List[Any]]:
        """Split the collection into records that do and do not satisfy a predicate.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        predicate : Callable[[Any], bool]
            Callable returning truthy for records that should match/be selected.
        
        Returns
        -------
        ``Tuple[List[Any], List[Any]]`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        yes, no = [], []
        for item in self._items_snapshot():
            (yes if predicate(item) else no).append(item)
        return yes, no

    def chunks(self, size: int) -> Iterator[List[Any]]:
        """Yield or return bounded-size chunks of the collection for incremental processing.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        size : int
            Requested size/dimension/chunk width.
        
        Returns
        -------
        ``Iterator[List[Any]]`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        if size <= 0: raise ValueError("size must be positive")
        items = self._items_snapshot()
        for i in range(0, len(items), size): yield items[i:i+size]

    def take(self, count: int) -> List[Any]:
        """Return the first requested number of records.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        count : int
            Requested number of records/items.
        
        Returns
        -------
        ``List[Any]`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        return self._items_snapshot()[:max(0, count)]
    def skip(self, count: int) -> List[Any]:
        """Return records after skipping the requested leading count.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        count : int
            Requested number of records/items.
        
        Returns
        -------
        ``List[Any]`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        return self._items_snapshot()[max(0, count):]
    def sample(self, count: int) -> List[Any]:
        """Return a random sample without requiring callers to manipulate backing storage directly.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        count : int
            Requested number of records/items.
        
        Returns
        -------
        ``List[Any]`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        items = self._items_snapshot(); return random.sample(items, min(max(0, count), len(items)))

    def shuffle(self, *, inplace: bool = True):
        """Randomize record order, optionally mutating the collection.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        inplace : bool (default: ``True``)
            When True, mutate/reorder the collection itself where supported.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        items = self._items_snapshot(); random.shuffle(items)
        if inplace: self._replace_items(items); self._invalidate_indexes(); return self
        return items

    def reverse(self, *, inplace: bool = True):
        """Reverse record/event order, optionally mutating according to the class contract.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        inplace : bool (default: ``True``)
            When True, mutate/reorder the collection itself where supported.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        items = list(reversed(self._items_snapshot()))
        if inplace: self._replace_items(items); self._invalidate_indexes(); return self
        return items

    def rename_path(self, old_path: str, new_path: str, *, missing: Any = _MISSING) -> int:
        """Move a value from one dotted path to another name/path across records.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        old_path : str
            Existing filesystem or dotted-data path to move/rename from.
        new_path : str
            Destination filesystem or dotted-data path to move/rename to.
        missing : Any (default: ``_MISSING``)
            Fallback/behavior used when the source dotted path does not exist.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        count = 0
        for item in self._items_snapshot():
            value = _native.ddm_get_path(item, old_path, missing)
            if value is missing: continue
            _native.ddm_set_path(item, new_path, value)
            self._delete_path(item, old_path)
            count += 1
        self._invalidate_indexes([old_path, new_path]); return count

    def copy_path(self, source: str, destination: str, *, missing: Any = _MISSING) -> int:
        """Copy a value from one dotted path to another across records.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        source : str
            Source path, collection or transfer identifier.
        destination : str
            Destination path or location.
        missing : Any (default: ``_MISSING``)
            Fallback/behavior used when the source dotted path does not exist.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        count = 0
        for item in self._items_snapshot():
            value = _native.ddm_get_path(item, source, missing)
            if value is missing: continue
            _native.ddm_set_path(item, destination, value); count += 1
        self._invalidate_indexes([destination]); return count

    def move_path(self, source: str, destination: str, *, missing: Any = _MISSING) -> int:
        """Move a value from one dotted path to another across records and remove the source.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        source : str
            Source path, collection or transfer identifier.
        destination : str
            Destination path or location.
        missing : Any (default: ``_MISSING``)
            Fallback/behavior used when the source dotted path does not exist.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        count = self.copy_path(source, destination, missing=missing)
        for item in self._items_snapshot(): self._delete_path(item, source)
        self._invalidate_indexes([source, destination]); return count

    def fill_missing(self, path: str, value: Any) -> int:
        """Populate a dotted path only when that path is missing.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any
            Target, new or comparison value.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        missing = object(); count = 0
        for item in self._items_snapshot():
            if _native.ddm_get_path(item, path, missing) is missing:
                _native.ddm_set_path(item, path, value); count += 1
        self._invalidate_indexes([path]); return count

    @staticmethod
    def _delete_path(item: Any, path: str) -> bool:
        parts = path.split(".")
        if not parts: return False
        parent = item
        for part in parts[:-1]:
            parent = _native.ddm_get_path(parent, part, _MISSING)
            if parent is _MISSING: return False
        key = parts[-1]
        if isinstance(parent, dict): return parent.pop(key, _MISSING) is not _MISSING
        store = getattr(parent, "_native_data", None)
        if isinstance(store, dict): return store.pop(key, _MISSING) is not _MISSING
        if hasattr(parent, key): delattr(parent, key); return True
        return False

    def delete_path(self, path: str) -> int:
        """Delete a dotted path from every record where it exists.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        count = sum(1 for item in self._items_snapshot() if self._delete_path(item, path))
        self._invalidate_indexes([path]); return count

    def search(self, *args: Any, **kwargs: Any):
        """Search the current data/index using the query and options supported by this class.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        *args : Any
            Arguments passed to a script/callable/subprocess.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        
        Returns
        -------
        Result collection/value produced by the operation.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        from ..search import DDMSearchEngine
        engine = getattr(self, "_search_engine", None) or DDMSearchEngine(self)
        return engine.find(*args, **kwargs)

    def build_search_index(self, *paths: str, **kwargs: Any):
        """Build and return a reusable DDMSearchEngine over this collection.
        
        Details
        -------
        This method belongs to :class:`DDMCollectionOps` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        *paths : str
            Dotted paths participating in an index/composite operation.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        from ..search import DDMSearchEngine
        engine = DDMSearchEngine(self)
        for path in paths: engine.create_index(path, **kwargs)
        return engine


class ListDDM(DDMCollectionOps, MutableSequence[Any]):
    """Sequence-oriented DDM collection.
    
    Overview
    --------
    ``ListDDM`` provides mutable list semantics plus high-throughput DDM bulk/path operations.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use when record order and duplicate records are meaningful.
    
    Inheritance
    -----------
    Base class(es): ``DDMCollectionOps, MutableSequence[Any]``.
    
    Primary public operations
    -------------------------
    insert, indexed.
    
    Example::
    
        users = ListDDM([
            DDM({"profile": {"age": 20}, "score": 10}),
            DDM({"profile": {"age": 17}, "score": 8}),
        ])
        adults = users.filter_path("profile.age", 18, op="gte")
        users.batch().add("score", 2).clamp("score", 0, 100).execute(users)
    """

    __slots__ = ("_items", "_search_engine")

    def __init__(self, values: Iterable[Any] = ()):
        """Initialize a new ListDDM instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`ListDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        values : Iterable[Any] (default: ``()``)
            Input iterable, mapping values or composite lookup values.
        """
        self._items = [_as_ddm(v) for v in values]
        self._search_engine = None

    def _items_snapshot(self) -> List[Any]: return self._items
    def _replace_items(self, items: Sequence[Any]) -> None: self._items[:] = [_as_ddm(v) for v in items]
    def _invalidate_indexes(self, paths: Optional[Iterable[str]] = None) -> None:
        if self._search_engine is not None: self._search_engine.invalidate(paths)
    def __len__(self) -> int: return len(self._items)
    def __getitem__(self, index): return self._items[index]
    def __setitem__(self, index, value): self._items[index] = _as_ddm(value); self._invalidate_indexes()
    def __delitem__(self, index): del self._items[index]; self._invalidate_indexes()
    def insert(self, index: int, value: Any) -> None:
        """Insert a record at the requested sequence position.
        
        Details
        -------
        This method belongs to :class:`ListDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        index : int
            Value supplied for ``index`` according to the ListDDM contract.
        value : Any
            Target, new or comparison value.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        self._items.insert(index, _as_ddm(value)); self._invalidate_indexes()
    def __iter__(self): return iter(self._items)
    def __repr__(self): return f"ListDDM({self._items!r})"

    def indexed(self, *paths: str, **kwargs: Any):
        """Build or reuse a DDMSearchEngine with indexes for the requested paths.
        
        Details
        -------
        This method belongs to :class:`ListDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        *paths : str
            Dotted paths participating in an index/composite operation.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        from ..search import DDMSearchEngine
        if self._search_engine is None: self._search_engine = DDMSearchEngine(self)
        for path in paths: self._search_engine.create_index(path, **kwargs)
        return self._search_engine


class SetDDM(DDMCollectionOps):
    """Uniqueness-oriented DDM collection.
    
    Overview
    --------
    ``SetDDM`` provides ordered record storage with configurable stable uniqueness keys.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Prefer key_path for large mutable datasets with a stable primary key; call rehash after external key mutations.
    
    Inheritance
    -----------
    Base class(es): ``DDMCollectionOps``.
    
    Primary public operations
    -------------------------
    add, discard, remove, rehash.
    
    Uniqueness semantics
    --------------------
    Ordinary mutable DDM uses value equality and is intentionally unhashable. SetDDM therefore maintains its own stable uniqueness keys. For large datasets prefer ``key_path`` pointing to an immutable primary-key field; use ``rehash()`` after direct external mutations that change the uniqueness key.
    """

    __slots__ = ("_items", "_keys", "_keyfunc", "_key_path", "_search_engine")

    def __init__(self, values: Iterable[Any] = (), *, key: Optional[Callable[[Any], Hashable]] = None,
                 key_path: Optional[str] = None):
        """Initialize a new SetDDM instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`SetDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        values : Iterable[Any] (default: ``()``)
            Input iterable, mapping values or composite lookup values.
        key : Optional[Callable[[Any], Hashable]] (default: ``None``)
            Mapping key or uniqueness key.
        key_path : Optional[str] (default: ``None``)
            Dotted path used as a stable uniqueness key for SetDDM.
        """
        if key is not None and key_path is not None:
            raise ValueError("use either key= or key_path=, not both")
        self._items: List[Any] = []
        self._keys: Dict[Any, Any] = {}
        self._key_path = str(key_path) if key_path is not None else None
        if key is not None:
            self._keyfunc = key
        elif self._key_path is not None:
            path = self._key_path
            missing = object()
            def by_path(item: Any):
                value = _native.ddm_get_path(item, path, missing)
                if value is missing:
                    raise KeyError(f"SetDDM key path missing: {path}")
                return _stable_key(value)
            self._keyfunc = by_path
        else:
            self._keyfunc = lambda item: _stable_key(item.to_dict())
        self._search_engine = None
        for value in values: self.add(value)

    def _key(self, item: Any): return self._keyfunc(item)

    def _invalidate_search_indexes(self, paths: Optional[Iterable[str]] = None) -> None:
        if self._search_engine is not None:
            self._search_engine.invalidate(paths)

    def _mutation_can_change_key(self, paths: Optional[Iterable[str]]) -> bool:
        if self._key_path is None:
            return True
        if paths is None:
            return True
        key_path = self._key_path
        return any(key_path == path or key_path.startswith(path + ".") or path.startswith(key_path + ".") for path in paths)

    def _rebuild_keys(self) -> None:
        rebuilt: Dict[Any, Any] = {}
        for item in self._items:
            key = self._key(item)
            if key in rebuilt and rebuilt[key] is not item:
                raise ValueError(f"SetDDM mutation produced duplicate key: {key!r}")
            rebuilt[key] = item
        self._keys = rebuilt

    def add(self, value: Any) -> bool:
        """Add a value/record/operation to the current object according to its collection or numeric semantics.
        
        Details
        -------
        This method belongs to :class:`SetDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        value : Any
            Target, new or comparison value.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        item = _as_ddm(value); key = self._key(item)
        if key in self._keys: return False
        self._keys[key] = item; self._items.append(item); self._invalidate_search_indexes(); return True
    def discard(self, value: Any) -> bool:
        """Remove a set-like record if present without raising for absence.
        
        Details
        -------
        This method belongs to :class:`SetDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        value : Any
            Target, new or comparison value.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        item = _as_ddm(value); key = self._key(item); existing = self._keys.pop(key, None)
        if existing is None: return False
        self._items.remove(existing); self._invalidate_search_indexes(); return True
    def remove(self, value: Any) -> None:
        """Remove an existing record/document/event and raise or report according to the class contract when absent.
        
        Details
        -------
        This method belongs to :class:`SetDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        value : Any
            Target, new or comparison value.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        if not self.discard(value): raise KeyError(value)
    def __contains__(self, value: Any) -> bool:
        try: return self._key(_as_ddm(value)) in self._keys
        except Exception: return False
    def __iter__(self): return iter(self._items)
    def __len__(self): return len(self._items)
    def _items_snapshot(self) -> List[Any]: return self._items
    def _replace_items(self, items: Sequence[Any]) -> None:
        self._items = [_as_ddm(item) for item in items]
        self._rebuild_keys()
        self._invalidate_search_indexes()
    def _invalidate_indexes(self, paths: Optional[Iterable[str]] = None) -> None:
        paths_tuple = None if paths is None else tuple(paths)
        if self._mutation_can_change_key(paths_tuple):
            self._rebuild_keys()
        self._invalidate_search_indexes(paths_tuple)
    def rehash(self) -> "SetDDM":
        """Rebuild SetDDM uniqueness keys after external mutation of stored records.
        
        Details
        -------
        This method belongs to :class:`SetDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``'SetDDM'`` result described by the method semantics.
        
        Notes
        -----
        Call this after directly mutating values that participate in SetDDM uniqueness. Collection-provided mutation methods already refresh internal uniqueness/search state where applicable.
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        self._rebuild_keys(); self._invalidate_search_indexes(); return self
    def __repr__(self): return f"SetDDM({self._items!r})"


class DictDDM(DDMCollectionOps, MutableMapping[K, Any], Generic[K]):
    """Keyed DDM collection.
    
    Overview
    --------
    ``DictDDM`` provides application-defined mapping keys whose values participate in DDM bulk/search operations.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for registries, entity maps and caches where external keys must be retained.
    
    Inheritance
    -----------
    Base class(es): ``DDMCollectionOps, MutableMapping[K, Any], Generic[K]``.
    
    Primary public operations
    -------------------------
    values, items, keys_for, indexed.
    """

    __slots__ = ("_items", "_search_engine")

    def __init__(self, values: Optional[Mapping[K, Any]] = None, **kwargs: Any):
        """Initialize a new DictDDM instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`DictDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        values : Optional[Mapping[K, Any]] (default: ``None``)
            Input iterable, mapping values or composite lookup values.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        """
        self._items: Dict[K, Any] = {k: _as_ddm(v) for k, v in (values or {}).items()}
        self._items.update({k: _as_ddm(v) for k, v in kwargs.items()})
        self._search_engine = None
    def __getitem__(self, key: K): return self._items[key]
    def __setitem__(self, key: K, value: Any): self._items[key] = _as_ddm(value); self._invalidate_indexes()
    def __delitem__(self, key: K): del self._items[key]; self._invalidate_indexes()
    def __iter__(self): return iter(self._items)
    def __len__(self): return len(self._items)
    def values(self):
        """Return a dynamic view or collection of stored values.
        
        Details
        -------
        This method belongs to :class:`DictDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Result collection/value produced by the operation.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        return self._items.values()
    def items(self):
        """Return key/value pairs for the current mapping-like object.
        
        Details
        -------
        This method belongs to :class:`DictDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Result collection/value produced by the operation.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        return self._items.items()
    def _items_snapshot(self) -> List[Any]: return list(self._items.values())
    def _replace_items(self, items: Sequence[Any]) -> None:
        if len(items) != len(self._items):
            raise TypeError("DictDDM cannot replace ordered values when cardinality changes; use filter/search result instead")
        self._items = {k: _as_ddm(v) for k, v in zip(self._items.keys(), items)}
    def _invalidate_indexes(self, paths: Optional[Iterable[str]] = None) -> None:
        if self._search_engine is not None: self._search_engine.invalidate(paths)
    def keys_for(self, path: str, value: Any = None, *, op: str = "eq") -> List[K]:
        """Return DictDDM mapping keys whose values satisfy a dotted-path comparison.
        
        Details
        -------
        This method belongs to :class:`DictDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any (default: ``None``)
            Target, new or comparison value.
        op : str (default: ``'eq'``)
            Comparison operator name such as eq/ne/lt/lte/gt/gte/prefix/contains where supported.
        
        Returns
        -------
        ``List[K]`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        matches = set(map(id, self.filter_path(path, value, op=op)))
        return [k for k, v in self._items.items() if id(v) in matches]
    def indexed(self, *paths: str, **kwargs: Any):
        """Build or reuse a DDMSearchEngine with indexes for the requested paths.
        
        Details
        -------
        This method belongs to :class:`DictDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        *paths : str
            Dotted paths participating in an index/composite operation.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        from ..search import DDMSearchEngine
        if self._search_engine is None: self._search_engine = DDMSearchEngine(self)
        for path in paths: self._search_engine.create_index(path, **kwargs)
        return self._search_engine
    def __repr__(self): return f"DictDDM({self._items!r})"


class DDMTable(ListDDM):
    """Lightweight structured table.
    
    Overview
    --------
    ``DDMTable`` provides ListDDM operations plus column selection, assignment and criteria queries.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for small/medium zero-dependency tabular workflows; it is not a pandas replacement.
    
    Inheritance
    -----------
    Base class(es): ``ListDDM``.
    
    Primary public operations
    -------------------------
    columns, select, assign, query.
    """

    def columns(self) -> List[str]:
        """Return the column names observed in the table records.
        
        Details
        -------
        This method belongs to :class:`DDMTable` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``List[str]`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        names = set()
        for item in self._items: names.update(item.to_dict())
        return sorted(names)

    def select(self, *paths: str) -> List[Dict[str, Any]]:
        """Project table rows to the requested dotted-path columns.
        
        Details
        -------
        This method belongs to :class:`DDMTable` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        *paths : str
            Dotted paths participating in an index/composite operation.
        
        Returns
        -------
        ``List[Dict[str, Any]]`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        rows = []
        for item in self._items:
            rows.append({path: _native.ddm_get_path(item, path, None) for path in paths})
        return rows

    def assign(self, **path_values: Any) -> "DDMTable":
        """Assign one or more columns/dotted paths across the table.
        
        Details
        -------
        This method belongs to :class:`DDMTable` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        **path_values : Any
            Value supplied for ``path_values`` according to the DDMTable contract.
        
        Returns
        -------
        ``'DDMTable'`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        self.update_all(**path_values); return self

    def query(self, **criteria: Any) -> "DDMTable":
        """Execute a class-specific query and return matching values/results.
        
        Details
        -------
        This method belongs to :class:`DDMTable` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        **criteria : Any
            Value supplied for ``criteria`` according to the DDMTable contract.
        
        Returns
        -------
        ``'DDMTable'`` result described by the method semantics.
        
        Notes
        -----
        Collection operations accept DDM-compatible nested records. Dotted paths such as ``profile.name`` traverse DDM instances and mapping-like nested values.
        """
        items = self._items_snapshot()
        for path, expected in criteria.items():
            items = _native.batch_filter_path(items, path, "eq", expected)
        return DDMTable(items)
