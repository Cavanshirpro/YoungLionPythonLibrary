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
    """Compile multiple simple mutations and execute them in one C++ collection pass."""

    __slots__ = ("_operations",)

    def __init__(self):
        self._operations: List[tuple] = []

    def set(self, path: str, value: Any) -> "BatchPlan":
        self._operations.append(("set", path, value)); return self

    def add(self, path: str, amount: float = 1.0) -> "BatchPlan":
        self._operations.append(("add", path, float(amount))); return self

    def subtract(self, path: str, amount: float = 1.0) -> "BatchPlan":
        self._operations.append(("sub", path, float(amount))); return self

    sub = subtract

    def multiply(self, path: str, factor: float) -> "BatchPlan":
        self._operations.append(("mul", path, float(factor))); return self

    mul = multiply

    def divide(self, path: str, divisor: float) -> "BatchPlan":
        if divisor == 0: raise ZeroDivisionError("division by zero")
        self._operations.append(("div", path, float(divisor))); return self

    div = divide

    def clamp(self, path: str, minimum: float, maximum: float) -> "BatchPlan":
        if minimum > maximum: raise ValueError("minimum cannot exceed maximum")
        self._operations.append(("clamp", path, float(minimum), float(maximum))); return self

    def clear(self) -> "BatchPlan":
        self._operations.clear(); return self

    def __len__(self) -> int: return len(self._operations)

    def execute(self, collection: Any) -> int:
        items = collection._items_snapshot() if hasattr(collection, "_items_snapshot") else list(collection)
        changed = int(_native.batch_mutate(items, self._operations))
        if hasattr(collection, "_invalidate_indexes"):
            collection._invalidate_indexes([op[1] for op in self._operations])
        return changed


class DDMCollectionOps:
    """Shared batch engine for large DDM collections.

    Hot loops that only need path traversal, comparisons, numeric transforms or
    reductions are delegated to the C++ extension. Python callbacks remain possible
    for arbitrary transformations.
    """

    def _items_snapshot(self) -> List[Any]:
        raise NotImplementedError

    def _replace_items(self, items: Sequence[Any]) -> None:
        raise NotImplementedError

    def _invalidate_indexes(self, paths: Optional[Iterable[str]] = None) -> None:
        pass

    def batch(self) -> BatchPlan:
        return BatchPlan()

    def path_values(self, path: str, default: Any = None) -> List[Any]:
        return _native.batch_get_path(self._items_snapshot(), path, default)

    pluck = path_values

    def set_all(self, path: str, value: Any) -> int:
        items = self._items_snapshot()
        changed = int(_native.batch_set_path(items, path, value))
        self._invalidate_indexes([path])
        return changed

    def apply_path(self, path: str, func: Callable[[Any], Any], *, write_back: bool = True) -> List[Any]:
        items = self._items_snapshot()
        result = _native.batch_apply_path(items, path, func, write_back=write_back)
        if write_back:
            self._invalidate_indexes([path])
        return result

    def map(self, func: Callable[[Any], Any]) -> List[Any]:
        return [func(item) for item in self._items_snapshot()]

    def for_each(self, func: Callable[[Any], Any]) -> "DDMCollectionOps":
        for item in self._items_snapshot():
            func(item)
        self._invalidate_indexes()
        return self

    def reduce(self, func: Callable[[Any, Any], Any], initial: Any = _MISSING) -> Any:
        items = self._items_snapshot()
        if initial is _MISSING:
            return functools.reduce(func, items)
        return functools.reduce(func, items, initial)

    def filter(self, predicate: Callable[[Any], bool]) -> List[Any]:
        return [item for item in self._items_snapshot() if predicate(item)]

    def filter_path(self, path: str, value: Any = None, *, op: str = "eq") -> List[Any]:
        return _native.batch_filter_path(self._items_snapshot(), path, op, value)

    where = filter_path

    def first(self, predicate: Optional[Callable[[Any], bool]] = None, default: Any = None) -> Any:
        for item in self._items_snapshot():
            if predicate is None or predicate(item):
                return item
        return default

    def first_path(self, path: str, value: Any = None, *, op: str = "eq", default: Any = None) -> Any:
        matches = self.filter_path(path, value, op=op)
        return matches[0] if matches else default

    def any(self, predicate: Callable[[Any], bool]) -> bool:
        return any(predicate(item) for item in self._items_snapshot())

    def all(self, predicate: Callable[[Any], bool]) -> bool:
        return all(predicate(item) for item in self._items_snapshot())

    def exists_path(self, path: str, value: Any = None, *, op: str = "eq") -> bool:
        return self.first_path(path, value, op=op, default=None) is not None

    def count_path(self, path: str, value: Any = None, *, op: str = "eq") -> int:
        return int(_native.batch_count_path(self._items_snapshot(), path, op, value))

    def partition_path(self, path: str, value: Any = None, *, op: str = "eq") -> Tuple[List[Any], List[Any]]:
        matched, rest = _native.batch_partition_path(self._items_snapshot(), path, op, value)
        return matched, rest

    def update_all(self, **values: Any) -> int:
        count = 0
        for path, value in values.items():
            count = max(count, self.set_all(path, value))
        return count

    def update_where(self, predicate: Callable[[Any], bool], **values: Any) -> int:
        selected = [item for item in self._items_snapshot() if predicate(item)]
        for path, value in values.items():
            _native.batch_set_path(selected, path, value)
        self._invalidate_indexes(values.keys())
        return len(selected)

    def apply_where(self, predicate: Callable[[Any], bool], path: str, func: Callable[[Any], Any]) -> int:
        selected = [item for item in self._items_snapshot() if predicate(item)]
        _native.batch_apply_path(selected, path, func, write_back=True)
        self._invalidate_indexes([path])
        return len(selected)

    def increment(self, path: str, amount: float = 1.0) -> int:
        changed = int(_native.batch_numeric_op(self._items_snapshot(), path, "add", float(amount)))
        self._invalidate_indexes([path]); return changed

    def decrement(self, path: str, amount: float = 1.0) -> int:
        changed = int(_native.batch_numeric_op(self._items_snapshot(), path, "sub", float(amount)))
        self._invalidate_indexes([path]); return changed

    def multiply(self, path: str, factor: float) -> int:
        changed = int(_native.batch_numeric_op(self._items_snapshot(), path, "mul", float(factor)))
        self._invalidate_indexes([path]); return changed

    def divide(self, path: str, divisor: float) -> int:
        changed = int(_native.batch_numeric_op(self._items_snapshot(), path, "div", float(divisor)))
        self._invalidate_indexes([path]); return changed

    def clamp(self, path: str, minimum: float, maximum: float) -> int:
        if maximum < minimum:
            raise ValueError("maximum must be >= minimum")
        changed = int(_native.batch_numeric_op(self._items_snapshot(), path, "clamp", float(minimum), float(maximum)))
        self._invalidate_indexes([path]); return changed

    def sum(self, path: str) -> float:
        value = _native.batch_numeric_reduce(self._items_snapshot(), path, "sum")
        return 0.0 if value is None else float(value)

    def mean(self, path: str) -> Optional[float]:
        value = _native.batch_numeric_reduce(self._items_snapshot(), path, "mean")
        return None if value is None else float(value)

    def min(self, path: str) -> Optional[float]:
        value = _native.batch_numeric_reduce(self._items_snapshot(), path, "min")
        return None if value is None else float(value)

    def max(self, path: str) -> Optional[float]:
        value = _native.batch_numeric_reduce(self._items_snapshot(), path, "max")
        return None if value is None else float(value)

    def numeric_count(self, path: str) -> int:
        return int(_native.batch_numeric_reduce(self._items_snapshot(), path, "count"))

    def sort_by(self, path: str, *, reverse: bool = False, missing_last: bool = True, inplace: bool = False):
        ordered = _native.batch_sort_path(self._items_snapshot(), path, reverse=reverse, missing_last=missing_last)
        if inplace:
            self._replace_items(ordered)
            self._invalidate_indexes()
            return self
        return ordered

    def is_sorted(self, path: str, *, reverse: bool = False) -> bool:
        return bool(_native.batch_is_sorted_path(self._items_snapshot(), path, reverse))

    def lower_bound(self, path: str, value: Any, *, reverse: bool = False, verify_sorted: bool = True) -> int:
        items = self._items_snapshot()
        if verify_sorted and not _native.batch_is_sorted_path(items, path, reverse):
            raise ValueError("collection must be sorted by the requested path")
        return int(_native.batch_lower_bound_path(items, path, value, reverse))

    def equal_range(self, path: str, value: Any, *, reverse: bool = False, verify_sorted: bool = True) -> Tuple[int, int]:
        items = self._items_snapshot()
        if verify_sorted and not _native.batch_is_sorted_path(items, path, reverse):
            raise ValueError("collection must be sorted by path before equal_range")
        start, end = _native.batch_equal_range_path(items, path, value, reverse)
        return int(start), int(end)

    def binary_search(self, path: str, value: Any, *, reverse: bool = False, verify_sorted: bool = True) -> int:
        items = self._items_snapshot()
        if verify_sorted and not _native.batch_is_sorted_path(items, path, reverse):
            raise ValueError("collection must be sorted by path before binary_search")
        return int(_native.batch_binary_search_path(items, path, value, reverse))

    def nth(self, path: str, n: int, *, largest: bool = False) -> Any:
        return _native.batch_nth_path(self._items_snapshot(), path, n, largest=largest)

    def top(self, path: str, n: int = 10, *, largest: bool = True) -> List[Any]:
        if n <= 0:
            return []
        items = self._items_snapshot()
        sentinel = object()
        key = lambda item: _native.ddm_get_path(item, path, sentinel)
        usable = [item for item in items if key(item) is not sentinel]
        fn = heapq.nlargest if largest else heapq.nsmallest
        return fn(n, usable, key=key)

    def bottom(self, path: str, n: int = 10) -> List[Any]:
        return self.top(path, n, largest=False)

    def group_by(self, path: str, default: Any = None) -> Dict[Any, List[Any]]:
        groups: Dict[Any, List[Any]] = defaultdict(list)
        items = self._items_snapshot()
        for item, value in zip(items, _native.batch_get_path(items, path, default)):
            groups[_stable_key(value)].append(item)
        return dict(groups)

    def count_by(self, path: str, default: Any = None) -> Counter:
        return Counter(_stable_key(v) for v in self.path_values(path, default))

    def distinct(self, path: str, default: Any = None) -> List[Any]:
        seen = set(); out = []
        for value in self.path_values(path, default):
            key = _stable_key(value)
            if key not in seen:
                seen.add(key); out.append(value)
        return out

    def deduplicate(self, path: Optional[str] = None, *, inplace: bool = False):
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
        yes, no = [], []
        for item in self._items_snapshot():
            (yes if predicate(item) else no).append(item)
        return yes, no

    def chunks(self, size: int) -> Iterator[List[Any]]:
        if size <= 0: raise ValueError("size must be positive")
        items = self._items_snapshot()
        for i in range(0, len(items), size): yield items[i:i+size]

    def take(self, count: int) -> List[Any]: return self._items_snapshot()[:max(0, count)]
    def skip(self, count: int) -> List[Any]: return self._items_snapshot()[max(0, count):]
    def sample(self, count: int) -> List[Any]:
        items = self._items_snapshot(); return random.sample(items, min(max(0, count), len(items)))

    def shuffle(self, *, inplace: bool = True):
        items = self._items_snapshot(); random.shuffle(items)
        if inplace: self._replace_items(items); self._invalidate_indexes(); return self
        return items

    def reverse(self, *, inplace: bool = True):
        items = list(reversed(self._items_snapshot()))
        if inplace: self._replace_items(items); self._invalidate_indexes(); return self
        return items

    def rename_path(self, old_path: str, new_path: str, *, missing: Any = _MISSING) -> int:
        count = 0
        for item in self._items_snapshot():
            value = _native.ddm_get_path(item, old_path, missing)
            if value is missing: continue
            _native.ddm_set_path(item, new_path, value)
            self._delete_path(item, old_path)
            count += 1
        self._invalidate_indexes([old_path, new_path]); return count

    def copy_path(self, source: str, destination: str, *, missing: Any = _MISSING) -> int:
        count = 0
        for item in self._items_snapshot():
            value = _native.ddm_get_path(item, source, missing)
            if value is missing: continue
            _native.ddm_set_path(item, destination, value); count += 1
        self._invalidate_indexes([destination]); return count

    def move_path(self, source: str, destination: str, *, missing: Any = _MISSING) -> int:
        count = self.copy_path(source, destination, missing=missing)
        for item in self._items_snapshot(): self._delete_path(item, source)
        self._invalidate_indexes([source, destination]); return count

    def fill_missing(self, path: str, value: Any) -> int:
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
        count = sum(1 for item in self._items_snapshot() if self._delete_path(item, path))
        self._invalidate_indexes([path]); return count

    def search(self, *args: Any, **kwargs: Any):
        from ..search import DDMSearchEngine
        engine = getattr(self, "_search_engine", None) or DDMSearchEngine(self)
        return engine.find(*args, **kwargs)

    def build_search_index(self, *paths: str, **kwargs: Any):
        from ..search import DDMSearchEngine
        engine = DDMSearchEngine(self)
        for path in paths: engine.create_index(path, **kwargs)
        return engine


class ListDDM(DDMCollectionOps, MutableSequence[Any]):
    """List-like DDM collection with native batch operations and reusable indexes."""

    __slots__ = ("_items", "_search_engine")

    def __init__(self, values: Iterable[Any] = ()):
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
    def insert(self, index: int, value: Any) -> None: self._items.insert(index, _as_ddm(value)); self._invalidate_indexes()
    def __iter__(self): return iter(self._items)
    def __repr__(self): return f"ListDDM({self._items!r})"

    def indexed(self, *paths: str, **kwargs: Any):
        from ..search import DDMSearchEngine
        if self._search_engine is None: self._search_engine = DDMSearchEngine(self)
        for path in paths: self._search_engine.create_index(path, **kwargs)
        return self._search_engine


class SetDDM(DDMCollectionOps):
    """Set-like mutable collection for DDM values without violating Python hashing rules.

    Uniqueness defaults to value content. A ``key`` callable can provide identity,
    primary-key or application-specific uniqueness for very large collections.
    """

    __slots__ = ("_items", "_keys", "_keyfunc", "_key_path", "_search_engine")

    def __init__(self, values: Iterable[Any] = (), *, key: Optional[Callable[[Any], Hashable]] = None,
                 key_path: Optional[str] = None):
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
        item = _as_ddm(value); key = self._key(item)
        if key in self._keys: return False
        self._keys[key] = item; self._items.append(item); self._invalidate_search_indexes(); return True
    def discard(self, value: Any) -> bool:
        item = _as_ddm(value); key = self._key(item); existing = self._keys.pop(key, None)
        if existing is None: return False
        self._items.remove(existing); self._invalidate_search_indexes(); return True
    def remove(self, value: Any) -> None:
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
        self._rebuild_keys(); self._invalidate_search_indexes(); return self
    def __repr__(self): return f"SetDDM({self._items!r})"


class DictDDM(DDMCollectionOps, MutableMapping[K, Any], Generic[K]):
    """Mapping of application keys to DDM values with bulk/path operations."""

    __slots__ = ("_items", "_search_engine")

    def __init__(self, values: Optional[Mapping[K, Any]] = None, **kwargs: Any):
        self._items: Dict[K, Any] = {k: _as_ddm(v) for k, v in (values or {}).items()}
        self._items.update({k: _as_ddm(v) for k, v in kwargs.items()})
        self._search_engine = None
    def __getitem__(self, key: K): return self._items[key]
    def __setitem__(self, key: K, value: Any): self._items[key] = _as_ddm(value); self._invalidate_indexes()
    def __delitem__(self, key: K): del self._items[key]; self._invalidate_indexes()
    def __iter__(self): return iter(self._items)
    def __len__(self): return len(self._items)
    def values(self): return self._items.values()
    def items(self): return self._items.items()
    def _items_snapshot(self) -> List[Any]: return list(self._items.values())
    def _replace_items(self, items: Sequence[Any]) -> None:
        if len(items) != len(self._items):
            raise TypeError("DictDDM cannot replace ordered values when cardinality changes; use filter/search result instead")
        self._items = {k: _as_ddm(v) for k, v in zip(self._items.keys(), items)}
    def _invalidate_indexes(self, paths: Optional[Iterable[str]] = None) -> None:
        if self._search_engine is not None: self._search_engine.invalidate(paths)
    def keys_for(self, path: str, value: Any = None, *, op: str = "eq") -> List[K]:
        matches = set(map(id, self.filter_path(path, value, op=op)))
        return [k for k, v in self._items.items() if id(v) in matches]
    def indexed(self, *paths: str, **kwargs: Any):
        from ..search import DDMSearchEngine
        if self._search_engine is None: self._search_engine = DDMSearchEngine(self)
        for path in paths: self._search_engine.create_index(path, **kwargs)
        return self._search_engine
    def __repr__(self): return f"DictDDM({self._items!r})"


class DDMTable(ListDDM):
    """Column-oriented convenience layer over ListDDM for analytics/batch editing."""

    def columns(self) -> List[str]:
        names = set()
        for item in self._items: names.update(item.to_dict())
        return sorted(names)

    def select(self, *paths: str) -> List[Dict[str, Any]]:
        rows = []
        for item in self._items:
            rows.append({path: _native.ddm_get_path(item, path, None) for path in paths})
        return rows

    def assign(self, **path_values: Any) -> "DDMTable":
        self.update_all(**path_values); return self

    def query(self, **criteria: Any) -> "DDMTable":
        items = self._items_snapshot()
        for path, expected in criteria.items():
            items = _native.batch_filter_path(items, path, "eq", expected)
        return DDMTable(items)
