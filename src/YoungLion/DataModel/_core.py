"""Core Dynamic Data Model implementation.

This module defines :class:`DDM`, YoungLion's general-purpose hierarchical data
container.  DDM stores public fields directly in the instance ``__dict__`` to
avoid duplicate mapping storage while exposing mapping-like operations,
serialization, dotted-path traversal, schema validation, clone/merge/diff tools,
structure analysis and transformations.  Performance-sensitive recursive and
path operations delegate to the native ``YoungLion._native`` extension.

Subclassing is a first-class use case.  A domain model may call ``super().__init__``
with raw mapping data and then normalize selected attributes into richer types or
nested DDM subclasses.  Serialization continues to recurse through those nested
objects, and cloning re-runs conventional subclass constructors so domain types
are preserved whenever possible.

Example
-------
    class UserProfile(DDM):
        def __init__(self, data):
            super().__init__(data)
            self.country: str = str(data.get("country", "Unknown"))

    class User(DDM):
        def __init__(self, data):
            super().__init__(data)
            self.name: str = str(data.get("name", "Unknown"))
            self.profile: UserProfile = UserProfile(data.get("profile", {}))

    user = User({"name": "Alice", "profile": {"country": "AZ"}})
    assert user.get_path("profile.country") == "AZ"

DDM is dynamic rather than a validation framework: use SchemaDDM or explicit
subclass normalization when strict input contracts are required.
"""
from __future__ import annotations

import csv
import io
import sys
from collections.abc import Mapping, MutableMapping
from typing import Any, Callable, Dict, Iterable, Iterator, Optional, Type, TypeVar, Union

from .. import _native

T = TypeVar("T", bound="DDM")
_MISSING = object()


class DDM:
    """Dynamic Data Model.
    
    Overview
    --------
    ``DDM`` provides hierarchical JSON-like application data with native path/serialization hot paths.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Subclass DDM when domain-specific typed attributes and methods should coexist with dynamic input.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    to_dict, to_json, from_json, get_path, set_path, has_path, clone, to_flat_dict, merge, update, diff, validate_schema, keys, values, items, get ....
    
    Data model semantics
    --------------------
    Public fields are stored once in the normal instance ``__dict__``. ``_data`` and ``_native_data`` are compatibility/native views of that same store rather than duplicate dictionaries. Nested DDM objects are recursively serialized, and ordinary mapping/list/tuple values remain valid inputs.
    
    Subclassing pattern
    -------------------
    Call ``super().__init__(data)`` first, then normalize the domain fields you care about into annotated attributes or nested DDM subclasses. This keeps raw JSON flexibility while making application code self-documenting and IDE-friendly.
    
    Example::
    
        class UserProfile(DDM):
            def __init__(self, data):
                super().__init__(data)
                self.name: str = str(data.get("name", "Unknown"))
    
        class User(DDM):
            def __init__(self, data):
                super().__init__(data)
                self.profile: UserProfile = UserProfile(data.get("profile", {}))
    
        user = User({"profile": {"name": "Alice"}})
        print(user.get_path("profile.name"))
        print(user.to_json())
    """

    __slots__ = ("_schema", "__dict__")

    def __init__(self, data: Mapping[str, Any]):
        """Initialize a new DDM instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        data : Mapping[str, Any]
            Input mapping or record data used to initialize the object.
        
        Raises
        ------
        TypeError
            If ``data`` is not a mapping.
        """
        if not isinstance(data, Mapping):
            raise TypeError("data must be a mapping")
        object.__setattr__(self, "_schema", None)
        self.__dict__.update(data)

    @property
    def _native_data(self) -> Dict[str, Any]:
        """Internal zero-copy storage hook used by the C++ extension."""
        return self.__dict__

    @property
    def _data(self) -> Dict[str, Any]:
        """Backward-compatible view of the historical internal data dictionary."""
        return self.__dict__

    @_data.setter
    def _data(self, value: Mapping[str, Any]) -> None:
        if not isinstance(value, Mapping):
            raise TypeError("_data must be a mapping")
        self.__dict__.clear()
        self.__dict__.update(value)

    def to_dict(self) -> Dict[str, Any]:
        """Recursively serialize the object into ordinary Python containers suitable for JSON-compatible processing.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Recursively converted ordinary Python dictionary.
        
        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
        """
        return _native.ddm_to_dict(self)

    def _to_dict_full(self) -> Dict[str, Any]:
        # Serialize public data once; include_private is an uncommon diagnostic
        # path and should not pay for two complete native recursive walks.
        data = self.to_dict()
        return {"_data": data, "_schema": self._schema, **data}

    def to_json(self, indent: int = 2, include_private: bool = False) -> str:
        """Serialize the object to a JSON string using YoungLion's native JSON encoder.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        indent : int (default: ``2``)
            JSON indentation level; use the supported compact value for minimal output.
        include_private : bool (default: ``False``)
            Whether diagnostic/private DDM state should also be serialized.
        
        Returns
        -------
        JSON text representation.
        
        Notes
        -----
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
        """
        return _native.json_dumps(self._to_dict_full() if include_private else self, indent=indent)

    @staticmethod
    def from_json(json_str: str) -> "DDM":
        """Create a DDM instance from a JSON object string.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        json_str : str
            Value supplied for ``json_str`` according to the DDM contract.
        
        Returns
        -------
        New DDM containing the decoded JSON object.
        
        Raises
        ------
        ValueError
            If the JSON root is not an object or input cannot be decoded according to the JSON contract.
        """
        value = _native.json_loads(json_str)
        if not isinstance(value, dict):
            raise ValueError("DDM JSON root must be an object")
        return DDM(value)

    def get_path(self, path: str, default: Any = None) -> Any:
        """Read a nested value using a dotted path without manually traversing every intermediate object.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
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
        
        Example::
        
            user.get_path("profile.address.city", "Unknown")
        """
        return _native.ddm_get_path(self, path, default)

    def set_path(self, path: str, value: Any) -> bool:
        """Assign a nested value using a dotted path, creating or updating the addressed field according to DDM path semantics.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
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
        This is a mutation. If the DDM belongs to an externally managed search index, refresh or invalidate that index unless the owning YoungLion collection performed the mutation and handled invalidation.
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
        
        Example::
        
            user.set_path("profile.locale", "en-US")
        """
        return bool(_native.ddm_set_path(self, path, value))

    def has_path(self, path: str) -> bool:
        """Return whether a dotted path can be resolved in the current object.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
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

    def clone(self: T) -> T:
        """Create an independent deep clone while preserving supported DDM subclass semantics.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Independent object of the same supported DDM/subclass type.
        
        Notes
        -----
        For conventional subclasses whose constructor accepts one mapping, the constructor is re-run so nested typed DDM models can be reconstructed. Built-in variants use specialized clone hooks where required. The clone does not share mutable nested data with the source.
        Path/serialization hot paths are implemented by the YoungLion native extension where supported; callers use the same Python API regardless of the underlying implementation.
        """
        data = _native.ddm_clone_data(self)
        if self.__class__ is DDM:
            obj = DDM(data)
        else:
            # Typed application subclasses conventionally accept one mapping in
            # __init__. Re-running that constructor preserves nested model types
            # such as User.profile -> UserProfile instead of degrading them to
            # plain dictionaries. Built-in variants with additional constructor
            # state provide a private _clone_construct hook.
            construct = getattr(self, "_clone_construct", None)
            if construct is not None:
                obj = construct(data)
            else:
                try:
                    obj = self.__class__(data)
                except TypeError:
                    # Compatibility fallback for legacy DDM subclasses whose
                    # constructor requires a non-standard signature.
                    obj = self.__class__.__new__(self.__class__)
                    DDM.__init__(obj, data)
        if isinstance(self._schema, dict):
            object.__setattr__(obj, "_schema", _native.ddm_clone_data(DDM(self._schema)))
        else:
            object.__setattr__(obj, "_schema", self._schema)
        return obj

    copy = clone

    def to_flat_dict(self, prefix: str = "", separator: str = ".") -> Dict[str, Any]:
        """Flatten nested structured data into a single mapping whose keys encode paths.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
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
        
        Example::
        
            DDM({"profile": {"name": "Alice"}}).to_flat_dict()
            # {"profile.name": "Alice"}
        """
        return _native.ddm_flatten(self, prefix=prefix, separator=separator)

    def merge(self: T, other: Union["DDM", Mapping[str, Any]]) -> T:
        """Deep-merge another DDM or mapping into this object and return the mutated instance.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : Union['DDM', Mapping[str, Any]]
            Another compatible object/value used by the operation.
        
        Returns
        -------
        ``T`` result described by the method semantics.
        """
        merged = _native.ddm_merge_data(self, other)
        self.__dict__.clear()
        self.__dict__.update(merged)
        return self

    def update(self: T, *args: Mapping[str, Any], **kwargs: Any) -> T:
        """Update top-level fields from mapping arguments and keyword values.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        *args : Mapping[str, Any]
            Arguments passed to a script/callable/subprocess.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        
        Returns
        -------
        ``T`` result described by the method semantics.
        """
        store = self.__dict__
        for mapping in args:
            if not isinstance(mapping, Mapping):
                raise TypeError("positional update arguments must be mappings")
            store.update(mapping)
        store.update(kwargs)
        return self

    def diff(self, other: "DDM") -> Dict[str, Any]:
        """Compute structural/value differences between this DDM and another DDM.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : 'DDM'
            Another compatible object/value used by the operation.
        
        Returns
        -------
        ``Dict[str, Any]`` result described by the method semantics.
        """
        return _native.ddm_diff(self, other)

    def validate_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the current data against a schema and remember that schema on the object.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        schema : Dict[str, Any]
            Schema mapping describing expected fields/types/constraints.
        
        Returns
        -------
        ``Dict[str, Any]`` result described by the method semantics.
        
        Notes
        -----
        The returned mapping reports validation status/errors according to the native schema contract. Validation records the schema on the object for diagnostic/variant use; ordinary DDM remains mutable.
        """
        object.__setattr__(self, "_schema", schema)
        return _native.ddm_validate_schema(self, schema)

    def keys(self):
        """Return a dynamic view of top-level field names.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Result collection/value produced by the operation.
        """
        return self.__dict__.keys()

    def values(self):
        """Return a dynamic view or collection of stored values.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Result collection/value produced by the operation.
        """
        return self.__dict__.values()

    def items(self):
        """Return key/value pairs for the current mapping-like object.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Result collection/value produced by the operation.
        """
        return self.__dict__.items()

    def get(self, key: str, default: Any = None) -> Any:
        """Return a value for a key, falling back to a default when the key is absent.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        key : str
            Mapping key or uniqueness key.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.
        
        Returns
        -------
        ``Any`` result described by the method semantics.
        """
        return self.__dict__.get(key, default)

    def setdefault(self, key: str, default: Any = None) -> Any:
        """Return the existing value for a key or insert and return the supplied default.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        key : str
            Mapping key or uniqueness key.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.
        
        Returns
        -------
        ``Any`` result described by the method semantics.
        """
        return self.__dict__.setdefault(key, default)

    def pop(self, key: str, default: Any = _MISSING):
        """Remove a key and return its value, optionally using a default when absent.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        key : str
            Mapping key or uniqueness key.
        default : Any (default: ``_MISSING``)
            Fallback returned/used when the requested value or path is absent.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        """
        store = self.__dict__
        if default is _MISSING:
            return store.pop(key)
        return store.pop(key, default)

    def popitem(self):
        """Remove and return one key/value pair using normal dictionary popitem semantics.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        """
        return self.__dict__.popitem()

    def clear(self) -> None:
        """Remove all currently stored entries or queued operations, depending on the owning class.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        """
        self.__dict__.clear()

    def filter_keys(self, keys: Iterable[str]) -> "DDM":
        """Create a new DDM containing only the requested top-level keys.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        keys : Iterable[str]
            Iterable of mapping field names.
        
        Returns
        -------
        ``'DDM'`` result described by the method semantics.
        """
        wanted = set(keys)
        return DDM({k: v for k, v in self.items() if k in wanted})

    def exclude_keys(self, keys: Iterable[str]) -> "DDM":
        """Create a new DDM excluding the requested top-level keys.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        keys : Iterable[str]
            Iterable of mapping field names.
        
        Returns
        -------
        ``'DDM'`` result described by the method semantics.
        """
        excluded = set(keys)
        return DDM({k: v for k, v in self.items() if k not in excluded})

    def pick(self, *keys: str) -> "DDM":
        """Convenience wrapper that returns a DDM containing only the named keys.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        *keys : str
            Iterable of mapping field names.
        
        Returns
        -------
        ``'DDM'`` result described by the method semantics.
        """
        return self.filter_keys(keys)

    def omit(self, *keys: str) -> "DDM":
        """Convenience wrapper that returns a DDM without the named keys.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        *keys : str
            Iterable of mapping field names.
        
        Returns
        -------
        ``'DDM'`` result described by the method semantics.
        """
        return self.exclude_keys(keys)

    def search(self, query: Any, case_sensitive: bool = False) -> Dict[str, Any]:
        """Search the current data/index using the query and options supported by this class.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        query : Any
            Search text, structured query or SQL/XML expression according to the method.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        
        Returns
        -------
        ``Dict[str, Any]`` result described by the method semantics.
        """
        q = str(query) if case_sensitive else str(query).casefold()
        found: Dict[str, Any] = {}

        def walk(value: Any, path: str = "") -> None:
            if isinstance(value, DDM):
                value = value._native_data
            if isinstance(value, Mapping):
                for k, v in value.items():
                    p = f"{path}.{k}" if path else str(k)
                    key = str(k) if case_sensitive else str(k).casefold()
                    val = str(v) if case_sensitive else str(v).casefold()
                    if q in key or (not isinstance(v, (Mapping, list, tuple)) and q in val):
                        found[p] = v
                    walk(v, p)
            elif isinstance(value, (list, tuple)):
                for i, v in enumerate(value):
                    walk(v, f"{path}.{i}" if path else str(i))

        walk(self)
        return found

    def find_by_type(self, value_type: Type[Any]) -> Dict[str, Any]:
        """Return flattened values whose runtime type matches the requested type.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        value_type : Type[Any]
            Runtime Python type used for filtering/type checks.
        
        Returns
        -------
        ``Dict[str, Any]`` result described by the method semantics.
        """
        return {k: v for k, v in self.to_flat_dict().items() if isinstance(v, value_type)}

    def transform(self, func: Callable[[Any], Any]) -> "DDM":
        """Apply a callable to values and return a transformed DDM rather than mutating the original.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        func : Callable[[Any], Any]
            Callable applied by the operation.
        
        Returns
        -------
        ``'DDM'`` result described by the method semantics.
        """
        return DDM({k: func(v) for k, v in self.items()})

    def map_attributes(self, mapping: Mapping[str, Union[str, Callable[[Any], Any]]]) -> "DDM":
        """Rename or transform selected attributes according to a declarative mapping.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        mapping : Mapping[str, Union[str, Callable[[Any], Any]]]
            Mapping that supplies source values, rename rules or transformation instructions.
        
        Returns
        -------
        ``'DDM'`` result described by the method semantics.
        """
        out = self.to_dict()
        for key, op in mapping.items():
            if key not in out:
                continue
            if callable(op):
                out[key] = op(out[key])
            elif isinstance(op, str):
                out[op] = out.pop(key)
        return DDM(out)

    def sort_by_key(self, reverse: bool = False) -> "DDM":
        """Return a DDM whose top-level items are ordered by key.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.
        
        Returns
        -------
        ``'DDM'`` result described by the method semantics.
        """
        return DDM(dict(sorted(self.items(), key=lambda kv: kv[0], reverse=reverse)))

    def sort_by_value(self, reverse: bool = False) -> "DDM":
        """Return a DDM whose top-level items are ordered by value.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.
        
        Returns
        -------
        ``'DDM'`` result described by the method semantics.
        """
        return DDM(dict(sorted(self.items(), key=lambda kv: kv[1], reverse=reverse)))

    def group_by(self, func: Callable[[str, Any], Any]) -> Dict[Any, Dict[str, Any]]:
        """Group records or values by the requested field/callback and return the resulting buckets.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        func : Callable[[str, Any], Any]
            Callable applied by the operation.
        
        Returns
        -------
        ``Dict[Any, Dict[str, Any]]`` result described by the method semantics.
        """
        result: Dict[Any, Dict[str, Any]] = {}
        for k, v in self.items():
            result.setdefault(func(k, v), {})[k] = v
        return result

    def aggregate(self, funcs: Union[Callable[[Iterable[Any]], Any], Mapping[str, Callable[[Iterable[Any]], Any]]]) -> Any:
        """Apply one or more aggregation callables to the selected data.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        funcs : Union[Callable[[Iterable[Any]], Any], Mapping[str, Callable[[Iterable[Any]], Any]]]
            Value supplied for ``funcs`` according to the DDM contract.
        
        Returns
        -------
        ``Any`` result described by the method semantics.
        """
        vals = self.values()
        if callable(funcs):
            return funcs(vals)
        snapshot = tuple(vals)
        return {name: fn(snapshot) for name, fn in funcs.items()}

    def get_types(self) -> Dict[str, Type[Any]]:
        """Return runtime type information for the object's top-level fields.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``Dict[str, Type[Any]]`` result described by the method semantics.
        """
        return {k: type(v) for k, v in self.items()}

    def has_type(self, key: str, value_type: Type[Any]) -> bool:
        """Check whether a named field currently contains a value of the requested type.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        key : str
            Mapping key or uniqueness key.
        value_type : Type[Any]
            Runtime Python type used for filtering/type checks.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        """
        value = self.get(key, _MISSING)
        return value is not _MISSING and isinstance(value, value_type)

    def count(self) -> int:
        """Return the number of stored values or matching records, depending on the class.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Number of records/fields matching the method semantics.
        """
        return len(self)

    def is_empty(self) -> bool:
        """Return True when the object has no public data fields.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        """
        return not self.__dict__

    def memory_info(self, recursive: bool = True) -> Dict[str, int]:
        """Return approximate storage metrics useful for comparing data representations.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        recursive : bool (default: ``True``)
            Value supplied for ``recursive`` according to the DDM contract.
        
        Returns
        -------
        ``Dict[str, int]`` result described by the method semantics.
        """
        return _native.ddm_memory_info(self, recursive)

    def compact(self, intern_keys: bool = True) -> "DDM":
        """Apply optional key interning/compaction steps intended to reduce repeated-memory overhead.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        intern_keys : bool (default: ``True``)
            Whether repeated string keys should be interned to reduce memory overhead.
        
        Returns
        -------
        ``'DDM'`` result described by the method semantics.
        """
        if intern_keys:
            store = self.__dict__
            compacted = {sys.intern(k) if isinstance(k, str) else k: v for k, v in store.items()}
            store.clear()
            store.update(compacted)
        return self

    def to_csv(self) -> str:
        """Serialize the represented data to CSV text.
        
        Details
        -------
        This method belongs to :class:`DDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(self.keys())
        writer.writerow(self.values())
        return out.getvalue()

    def __getitem__(self, key: str) -> Any:
        try:
            return self.__dict__[key]
        except KeyError:
            raise KeyError(key) from None

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value

    def __delitem__(self, key: str) -> None:
        del self.__dict__[key]

    def __contains__(self, key: str) -> bool:
        return key in self.__dict__

    def __iter__(self) -> Iterator[str]:
        return iter(self.__dict__)

    def __len__(self) -> int:
        return len(self.__dict__)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DDM):
            return self.to_dict() == other.to_dict()
        if isinstance(other, dict):
            return self.to_dict() == other
        return False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.to_dict()!r})"

    def __str__(self) -> str:
        return _native.json_dumps(self, indent=2)
