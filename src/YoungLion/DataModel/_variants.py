from __future__ import annotations

import sys
from collections.abc import Mapping
from typing import Any, Callable, Dict, Iterable, Iterator, Optional

from .. import _native
from ._core import DDM, _MISSING


def _freeze_value(value: Any) -> Any:
    if isinstance(value, FrozenDDM):
        return value
    if isinstance(value, DDM):
        return FrozenDDM(value.to_dict())
    if isinstance(value, Mapping):
        return FrozenDDM(value)
    if isinstance(value, list):
        return tuple(_freeze_value(v) for v in value)
    if isinstance(value, tuple):
        return tuple(_freeze_value(v) for v in value)
    if isinstance(value, set):
        return frozenset(_freeze_value(v) for v in value)
    return value


def _hashable(value: Any) -> Any:
    if isinstance(value, FrozenDDM):
        return value._hash_tuple
    if isinstance(value, Mapping):
        return tuple(sorted((str(k), _hashable(v)) for k, v in value.items()))
    if isinstance(value, (list, tuple)):
        return tuple(_hashable(v) for v in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(_hashable(v) for v in value)
    try:
        hash(value)
        return value
    except TypeError:
        return repr(value)


class FrozenDDM(DDM):
    """Recursively immutable, hashable DDM.

    Use this variant when DDM values need to be set members, dictionary keys, cache
    keys, or safely shared between threads without mutation.
    """

    __slots__ = ("_frozen", "_cached_hash")

    def __init__(self, data: Mapping[str, Any]):
        object.__setattr__(self, "_frozen", False)
        object.__setattr__(self, "_cached_hash", None)
        super().__init__({sys.intern(str(k)): _freeze_value(v) for k, v in data.items()})
        object.__setattr__(self, "_frozen", True)

    @property
    def _hash_tuple(self):
        return tuple(sorted((k, _hashable(v)) for k, v in self.__dict__.items()))

    def __hash__(self) -> int:
        cached = self._cached_hash
        if cached is None:
            cached = hash(self._hash_tuple)
            object.__setattr__(self, "_cached_hash", cached)
        return cached

    def _immutable(self, *args: Any, **kwargs: Any):
        raise TypeError("FrozenDDM is immutable")

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_frozen", False) and not name.startswith("_"):
            self._immutable()
        object.__setattr__(self, name, value)

    __setitem__ = _immutable
    __delitem__ = _immutable
    set_path = _immutable
    merge = _immutable
    update = _immutable
    setdefault = _immutable
    pop = _immutable
    popitem = _immutable
    clear = _immutable
    compact = _immutable

    def _clone_construct(self, data: Mapping[str, Any]) -> "FrozenDDM":
        return FrozenDDM(data)

    def thaw(self) -> DDM:
        return DDM(self.to_dict())




class IdentityDDM(DDM):
    """Mutable DDM with identity equality/hash for built-in set/dict-key use.

    Standard :class:`DDM` intentionally keeps value equality and is therefore
    unhashable while mutable. IdentityDDM trades value equality for object
    identity, making mutation safe after insertion into a Python set or dict.
    """

    __slots__ = ()
    __hash__ = object.__hash__
    __eq__ = object.__eq__

class PackedDDM(Mapping[str, Any]):
    """Memory-oriented DDM-compatible mapping with no per-instance ``__dict__``.

    ``PackedDDM`` trades a little attribute-access speed for a smaller object header.
    It is useful for very large mostly-read datasets. The C++ path/search functions
    access ``_native_data`` directly, so batch operations stay efficient.
    """

    __slots__ = ("_store", "_schema")

    def __init__(self, data: Mapping[str, Any], *, intern_keys: bool = True):
        if not isinstance(data, Mapping):
            raise TypeError("data must be a mapping")
        self._schema = None
        self._store = {
            sys.intern(str(k)) if intern_keys else str(k): v
            for k, v in data.items()
        }

    @property
    def _native_data(self) -> Dict[str, Any]:
        return self._store

    @property
    def _data(self) -> Dict[str, Any]:
        return self._store

    def __getattr__(self, name: str) -> Any:
        try:
            return self._store[name]
        except KeyError:
            raise AttributeError(name) from None

    def __setattr__(self, name: str, value: Any) -> None:
        if name in {"_store", "_schema"}:
            object.__setattr__(self, name, value)
        else:
            self._store[name] = value

    def __getitem__(self, key: str) -> Any:
        return self._store[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._store[key] = value

    def __delitem__(self, key: str) -> None:
        del self._store[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._store)

    def __len__(self) -> int:
        return len(self._store)

    def to_dict(self) -> Dict[str, Any]:
        return _native.ddm_to_dict(self)

    def to_json(self, indent: int = 2) -> str:
        return _native.json_dumps(self, indent=indent)

    def get_path(self, path: str, default: Any = None) -> Any:
        return _native.ddm_get_path(self, path, default)

    def set_path(self, path: str, value: Any) -> bool:
        return bool(_native.ddm_set_path(self, path, value))

    def has_path(self, path: str) -> bool:
        return bool(_native.ddm_has_path(self, path))

    def clone(self) -> "PackedDDM":
        return PackedDDM(_native.ddm_clone_data(self))

    copy = clone

    def to_flat_dict(self, prefix: str = "", separator: str = ".") -> Dict[str, Any]:
        return _native.ddm_flatten(self, prefix=prefix, separator=separator)

    def memory_info(self, recursive: bool = True) -> Dict[str, int]:
        return _native.ddm_memory_info(self, recursive)

    def freeze(self) -> FrozenDDM:
        return FrozenDDM(self.to_dict())

    def __repr__(self) -> str:
        return f"PackedDDM({self._store!r})"


class SchemaDDM(DDM):
    """DDM that validates a schema on construction and selected updates."""

    __slots__ = ("_strict_schema",)

    def __init__(self, data: Mapping[str, Any], schema: Mapping[str, Any], *, strict: bool = True):
        super().__init__(data)
        object.__setattr__(self, "_strict_schema", bool(strict))
        result = self.validate_schema(dict(schema))
        if strict and not bool(result.get("valid", not result)):
            raise ValueError(f"schema validation failed: {result}")

    def _clone_construct(self, data: Mapping[str, Any]) -> "SchemaDDM":
        return SchemaDDM(data, self._schema or {}, strict=self._strict_schema)

    def validate(self) -> Dict[str, Any]:
        return self.validate_schema(self._schema or {})

    def set_validated(self, path: str, value: Any) -> "SchemaDDM":
        old = self.get_path(path, _MISSING)
        self.set_path(path, value)
        result = self.validate()
        if self._strict_schema and not bool(result.get("valid", not result)):
            if old is _MISSING:
                # Best effort rollback for new top-level paths.
                top = path.split(".", 1)[0]
                self.__dict__.pop(top, None)
            else:
                self.set_path(path, old)
            raise ValueError(f"schema validation failed: {result}")
        return self


class DefaultDDM(DDM):
    """DDM with a default factory for absent top-level attributes/keys."""

    __slots__ = ("_default_factory",)

    def __init__(self, data: Mapping[str, Any], default_factory: Callable[[], Any] = lambda: None):
        super().__init__(data)
        object.__setattr__(self, "_default_factory", default_factory)

    def _clone_construct(self, data: Mapping[str, Any]) -> "DefaultDDM":
        return DefaultDDM(data, default_factory=self._default_factory)

    def __getattr__(self, name: str) -> Any:
        value = self._default_factory()
        self.__dict__[name] = value
        return value

    def __missing__(self, key: str) -> Any:
        value = self._default_factory()
        self.__dict__[key] = value
        return value

    def __getitem__(self, key: str) -> Any:
        try:
            return self.__dict__[key]
        except KeyError:
            return self.__missing__(key)


class LazyDDM(DDM):
    """DDM with lazily computed fields cached after the first access."""

    __slots__ = ("_lazy",)

    def __init__(self, data: Mapping[str, Any], lazy: Optional[Mapping[str, Callable[["LazyDDM"], Any]]] = None):
        super().__init__(data)
        object.__setattr__(self, "_lazy", dict(lazy or {}))

    def _clone_construct(self, data: Mapping[str, Any]) -> "LazyDDM":
        # Keep lazy definitions but do not copy already materialized derived
        # values as authoritative cache entries. They are present in data for
        # round-trip compatibility and can be explicitly invalidated by callers.
        return LazyDDM(data, lazy=self._lazy)

    def __getattr__(self, name: str) -> Any:
        lazy = self._lazy
        if name not in lazy:
            raise AttributeError(name)
        value = lazy[name](self)
        self.__dict__[name] = value
        return value

    def invalidate(self, *fields: str) -> "LazyDDM":
        targets = fields or tuple(self._lazy)
        for field in targets:
            self.__dict__.pop(field, None)
        return self


class ViewDDM(Mapping[str, Any]):
    """Zero-copy DDM-compatible view over an existing mutable mapping."""

    __slots__ = ("_store",)

    def __init__(self, mapping: Dict[str, Any]):
        if not isinstance(mapping, dict):
            raise TypeError("ViewDDM currently requires a dict for zero-copy semantics")
        self._store = mapping

    @property
    def _native_data(self):
        return self._store

    @property
    def _data(self):
        return self._store

    def __getitem__(self, key: str) -> Any: return self._store[key]
    def __setitem__(self, key: str, value: Any) -> None: self._store[key] = value
    def __delitem__(self, key: str) -> None: del self._store[key]
    def __iter__(self) -> Iterator[str]: return iter(self._store)
    def __len__(self) -> int: return len(self._store)
    def __getattr__(self, name: str) -> Any:
        try: return self._store[name]
        except KeyError: raise AttributeError(name) from None
    def to_dict(self) -> Dict[str, Any]: return _native.ddm_to_dict(self)
    def get_path(self, path: str, default: Any = None) -> Any: return _native.ddm_get_path(self, path, default)
    def set_path(self, path: str, value: Any) -> bool: return bool(_native.ddm_set_path(self, path, value))
    def has_path(self, path: str) -> bool: return bool(_native.ddm_has_path(self, path))
    def __repr__(self) -> str: return f"ViewDDM({self._store!r})"
