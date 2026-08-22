"""Specialized Dynamic Data Model variants.

The classes in this module intentionally change one important semantic property
of ordinary :class:`DDM`: mutability, equality/hash behavior, storage layout,
schema enforcement, missing-value behavior, lazy computation or ownership of the
underlying mapping.  They are designed to be selected deliberately rather than
used as interchangeable aliases.

Use FrozenDDM for immutable value objects, IdentityDDM for mutable objects that
must participate in identity-based sets/maps, PackedDDM for dense read-heavy
record pools, SchemaDDM for runtime validation, DefaultDDM for generated missing
values, LazyDDM for cached derived fields and ViewDDM for zero-copy access to an
existing mutable mapping.
"""
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
    """Immutable DDM value object.
    
    Overview
    --------
    ``FrozenDDM`` provides recursive immutability plus value equality/hash semantics.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for configuration snapshots, cache keys and set/dict membership when content must not change.
    
    Inheritance
    -----------
    Base class(es): ``DDM``.
    
    Primary public operations
    -------------------------
    thaw.
    """

    __slots__ = ("_frozen", "_cached_hash")

    def __init__(self, data: Mapping[str, Any]):
        """Initialize a new FrozenDDM instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`FrozenDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        data : Mapping[str, Any]
            Input mapping or record data used to initialize the object.
        """
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
        """Return a mutable DDM copy of the frozen value object.
        
        Details
        -------
        This method belongs to :class:`FrozenDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``DDM`` result described by the method semantics.
        """
        return DDM(self.to_dict())




class IdentityDDM(DDM):
    """Identity-semantic mutable DDM.
    
    Overview
    --------
    ``IdentityDDM`` provides ordinary DDM mutability with object-identity equality and hashing.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use when mutable records must be stored in built-in sets or used as dict keys by identity.
    
    Inheritance
    -----------
    Base class(es): ``DDM``.
    """

    __slots__ = ()
    __hash__ = object.__hash__
    __eq__ = object.__eq__

class PackedDDM(Mapping[str, Any]):
    """Packed read-heavy DDM.
    
    Overview
    --------
    ``PackedDDM`` provides slot-backed mapping storage intended to reduce per-instance overhead in large record pools.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use when many similarly shaped records are mostly read rather than dynamically extended.
    
    Inheritance
    -----------
    Base class(es): ``Mapping[str, Any]``.
    
    Primary public operations
    -------------------------
    to_dict, to_json, get_path, set_path, has_path, clone, to_flat_dict, memory_info, freeze.
    
    Trade-off
    ---------
    PackedDDM avoids a normal per-instance ``__dict__`` and is intended for large, read-heavy record pools. It deliberately gives up some of ordinary DDM's dynamic attribute-storage flexibility in exchange for lower overhead.
    """

    __slots__ = ("_store", "_schema")

    def __init__(self, data: Mapping[str, Any], *, intern_keys: bool = True):
        """Initialize a new PackedDDM instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`PackedDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        data : Mapping[str, Any]
            Input mapping or record data used to initialize the object.
        intern_keys : bool (default: ``True``)
            Whether repeated string keys should be interned to reduce memory overhead.
        """
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
        """Recursively serialize the object into ordinary Python containers suitable for JSON-compatible processing.
        
        Details
        -------
        This method belongs to :class:`PackedDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Recursively converted ordinary Python dictionary.
        
        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
        """
        return _native.ddm_to_dict(self)

    def to_json(self, indent: int = 2) -> str:
        """Serialize the object to a JSON string using YoungLion's native JSON encoder.
        
        Details
        -------
        This method belongs to :class:`PackedDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        indent : int (default: ``2``)
            JSON indentation level; use the supported compact value for minimal output.
        
        Returns
        -------
        JSON text representation.
        
        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
        """
        return _native.json_dumps(self, indent=indent)

    def get_path(self, path: str, default: Any = None) -> Any:
        """Read a nested value using a dotted path without manually traversing every intermediate object.
        
        Details
        -------
        This method belongs to :class:`PackedDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.
        
        Returns
        -------
        Resolved nested value or ``default`` when the path cannot be resolved.
        
        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
        """
        return _native.ddm_get_path(self, path, default)

    def set_path(self, path: str, value: Any) -> bool:
        """Assign a nested value using a dotted path, creating or updating the addressed field according to DDM path semantics.
        
        Details
        -------
        This method belongs to :class:`PackedDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any
            Target, new or comparison value.
        
        Returns
        -------
        ``True`` when the native path assignment succeeds.
        
        Raises
        ------
        TypeError/ValueError
            If the operation violates PackedDDM mutability/path constraints.
        
        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
        """
        return bool(_native.ddm_set_path(self, path, value))

    def has_path(self, path: str) -> bool:
        """Return whether a dotted path can be resolved in the current object.
        
        Details
        -------
        This method belongs to :class:`PackedDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        Boolean indicating whether the full dotted path exists.
        
        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
        """
        return bool(_native.ddm_has_path(self, path))

    def clone(self) -> "PackedDDM":
        """Create an independent deep clone while preserving supported DDM subclass semantics.
        
        Details
        -------
        This method belongs to :class:`PackedDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Independent object of the same supported DDM/subclass type.
        
        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
        """
        return PackedDDM(_native.ddm_clone_data(self))

    copy = clone

    def to_flat_dict(self, prefix: str = "", separator: str = ".") -> Dict[str, Any]:
        """Flatten nested structured data into a single mapping whose keys encode paths.
        
        Details
        -------
        This method belongs to :class:`PackedDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        prefix : str (default: ``''``)
            Optional path/text prefix applied by the operation.
        separator : str (default: ``'.'``)
            Delimiter inserted between flattened path components.
        
        Returns
        -------
        ``Dict[str, Any]`` result described by the method semantics.
        
        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
        """
        return _native.ddm_flatten(self, prefix=prefix, separator=separator)

    def memory_info(self, recursive: bool = True) -> Dict[str, int]:
        """Return approximate storage metrics useful for comparing data representations.
        
        Details
        -------
        This method belongs to :class:`PackedDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        recursive : bool (default: ``True``)
            Value supplied for ``recursive`` according to the PackedDDM contract.
        
        Returns
        -------
        ``Dict[str, int]`` result described by the method semantics.
        """
        return _native.ddm_memory_info(self, recursive)

    def freeze(self) -> FrozenDDM:
        """Return an immutable FrozenDDM representation of the current packed data.
        
        Details
        -------
        This method belongs to :class:`PackedDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``FrozenDDM`` result described by the method semantics.
        """
        return FrozenDDM(self.to_dict())

    def __repr__(self) -> str:
        return f"PackedDDM({self._store!r})"


class SchemaDDM(DDM):
    """Schema-validating DDM.
    
    Overview
    --------
    ``SchemaDDM`` provides runtime schema validation during construction and validated path assignment.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use at trust boundaries where malformed structured input must be rejected early.
    
    Inheritance
    -----------
    Base class(es): ``DDM``.
    
    Primary public operations
    -------------------------
    validate, set_validated.
    """

    __slots__ = ("_strict_schema",)

    def __init__(self, data: Mapping[str, Any], schema: Mapping[str, Any], *, strict: bool = True):
        """Initialize a new SchemaDDM instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`SchemaDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        data : Mapping[str, Any]
            Input mapping or record data used to initialize the object.
        schema : Mapping[str, Any]
            Schema mapping describing expected fields/types/constraints.
        strict : bool (default: ``True``)
            Whether validation rejects fields/conditions beyond the schema contract.
        """
        super().__init__(data)
        object.__setattr__(self, "_strict_schema", bool(strict))
        result = self.validate_schema(dict(schema))
        if strict and not bool(result.get("valid", not result)):
            raise ValueError(f"schema validation failed: {result}")

    def _clone_construct(self, data: Mapping[str, Any]) -> "SchemaDDM":
        return SchemaDDM(data, self._schema or {}, strict=self._strict_schema)

    def validate(self) -> Dict[str, Any]:
        """Validate current state against the configured schema.
        
        Details
        -------
        This method belongs to :class:`SchemaDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``Dict[str, Any]`` result described by the method semantics.
        """
        return self.validate_schema(self._schema or {})

    def set_validated(self, path: str, value: Any) -> "SchemaDDM":
        """Assign a dotted-path value only if the resulting SchemaDDM remains valid.
        
        Details
        -------
        This method belongs to :class:`SchemaDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any
            Target, new or comparison value.
        
        Returns
        -------
        ``'SchemaDDM'`` result described by the method semantics.
        """
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
    """Default-producing DDM.
    
    Overview
    --------
    ``DefaultDDM`` provides top-level missing keys and attributes resolved through a default factory.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for sparse settings/state objects where a consistent fallback policy is preferred.
    
    Inheritance
    -----------
    Base class(es): ``DDM``.
    """

    __slots__ = ("_default_factory",)

    def __init__(self, data: Mapping[str, Any], default_factory: Callable[[], Any] = lambda: None):
        """Initialize a new DefaultDDM instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`DefaultDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        data : Mapping[str, Any]
            Input mapping or record data used to initialize the object.
        default_factory : Callable[[], Any] (default: ``lambda: None``)
            Callable producing fallback values for missing top-level keys/attributes.
        """
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
    """Lazy-field DDM.
    
    Overview
    --------
    ``LazyDDM`` provides on-demand field computation with per-field caching and invalidation.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for derived values that are expensive or unnecessary for every record.
    
    Inheritance
    -----------
    Base class(es): ``DDM``.
    
    Primary public operations
    -------------------------
    invalidate.
    """

    __slots__ = ("_lazy",)

    def __init__(self, data: Mapping[str, Any], lazy: Optional[Mapping[str, Callable[["LazyDDM"], Any]]] = None):
        """Initialize a new LazyDDM instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`LazyDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        data : Mapping[str, Any]
            Input mapping or record data used to initialize the object.
        lazy : Optional[Mapping[str, Callable[['LazyDDM'], Any]]] (default: ``None``)
            Mapping of field names to callables used for on-demand LazyDDM values.
        """
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
        """Invalidate cached lazy fields so they will be recomputed on next access.
        
        Details
        -------
        This method belongs to :class:`LazyDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        *fields : str
            Field names or field mapping used for structured document data.
        
        Returns
        -------
        ``'LazyDDM'`` result described by the method semantics.
        """
        targets = fields or tuple(self._lazy)
        for field in targets:
            self.__dict__.pop(field, None)
        return self


class ViewDDM(Mapping[str, Any]):
    """Zero-copy mapping view.
    
    Overview
    --------
    ``ViewDDM`` provides DDM-style path operations directly over an externally owned mutable mapping.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use when copying would be wasteful and shared mutation is explicitly desired.
    
    Inheritance
    -----------
    Base class(es): ``Mapping[str, Any]``.
    
    Primary public operations
    -------------------------
    to_dict, get_path, set_path, has_path.
    """

    __slots__ = ("_store",)

    def __init__(self, mapping: Dict[str, Any]):
        """Initialize a new ViewDDM instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`ViewDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        mapping : Dict[str, Any]
            Mapping that supplies source values, rename rules or transformation instructions.
        """
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
    def to_dict(self) -> Dict[str, Any]:
        """Recursively serialize the object into ordinary Python containers suitable for JSON-compatible processing.
        
        Details
        -------
        This method belongs to :class:`ViewDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Recursively converted ordinary Python dictionary.
        
        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
        """
        return _native.ddm_to_dict(self)
    def get_path(self, path: str, default: Any = None) -> Any:
        """Read a nested value using a dotted path without manually traversing every intermediate object.
        
        Details
        -------
        This method belongs to :class:`ViewDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.
        
        Returns
        -------
        Resolved nested value or ``default`` when the path cannot be resolved.
        
        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
        """
        return _native.ddm_get_path(self, path, default)
    def set_path(self, path: str, value: Any) -> bool:
        """Assign a nested value using a dotted path, creating or updating the addressed field according to DDM path semantics.
        
        Details
        -------
        This method belongs to :class:`ViewDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        value : Any
            Target, new or comparison value.
        
        Returns
        -------
        ``True`` when the native path assignment succeeds.
        
        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
        """
        return bool(_native.ddm_set_path(self, path, value))
    def has_path(self, path: str) -> bool:
        """Return whether a dotted path can be resolved in the current object.
        
        Details
        -------
        This method belongs to :class:`ViewDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        Boolean indicating whether the full dotted path exists.
        
        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
        """
        return bool(_native.ddm_has_path(self, path))
    def __repr__(self) -> str: return f"ViewDDM({self._store!r})"
