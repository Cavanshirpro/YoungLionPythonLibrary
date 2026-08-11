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
    """Dynamic Data Model with a compact single-store layout and C++ hot paths.

    Public fields are stored once in the normal instance ``__dict__``. Attribute
    access therefore stays on CPython's fast native attribute path, while ``_data``
    is a zero-copy compatibility view instead of a second duplicate dictionary.
    """

    __slots__ = ("_schema", "__dict__")

    def __init__(self, data: Mapping[str, Any]):
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
        return _native.ddm_to_dict(self)

    def _to_dict_full(self) -> Dict[str, Any]:
        # Serialize public data once; include_private is an uncommon diagnostic
        # path and should not pay for two complete native recursive walks.
        data = self.to_dict()
        return {"_data": data, "_schema": self._schema, **data}

    def to_json(self, indent: int = 2, include_private: bool = False) -> str:
        return _native.json_dumps(self._to_dict_full() if include_private else self, indent=indent)

    @staticmethod
    def from_json(json_str: str) -> "DDM":
        value = _native.json_loads(json_str)
        if not isinstance(value, dict):
            raise ValueError("DDM JSON root must be an object")
        return DDM(value)

    def get_path(self, path: str, default: Any = None) -> Any:
        return _native.ddm_get_path(self, path, default)

    def set_path(self, path: str, value: Any) -> bool:
        return bool(_native.ddm_set_path(self, path, value))

    def has_path(self, path: str) -> bool:
        return bool(_native.ddm_has_path(self, path))

    def clone(self: T) -> T:
        data = _native.ddm_clone_data(self)
        if self.__class__ is DDM:
            obj = DDM(data)
        else:
            obj = self.__class__.__new__(self.__class__)
            DDM.__init__(obj, data)
        if isinstance(self._schema, dict):
            object.__setattr__(obj, "_schema", _native.ddm_clone_data(DDM(self._schema)))
        else:
            object.__setattr__(obj, "_schema", self._schema)
        return obj

    copy = clone

    def to_flat_dict(self, prefix: str = "", separator: str = ".") -> Dict[str, Any]:
        return _native.ddm_flatten(self, prefix=prefix, separator=separator)

    def merge(self: T, other: Union["DDM", Mapping[str, Any]]) -> T:
        merged = _native.ddm_merge_data(self, other)
        self.__dict__.clear()
        self.__dict__.update(merged)
        return self

    def update(self: T, *args: Mapping[str, Any], **kwargs: Any) -> T:
        store = self.__dict__
        for mapping in args:
            if not isinstance(mapping, Mapping):
                raise TypeError("positional update arguments must be mappings")
            store.update(mapping)
        store.update(kwargs)
        return self

    def diff(self, other: "DDM") -> Dict[str, Any]:
        return _native.ddm_diff(self, other)

    def validate_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        object.__setattr__(self, "_schema", schema)
        return _native.ddm_validate_schema(self, schema)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def get(self, key: str, default: Any = None) -> Any:
        return self.__dict__.get(key, default)

    def setdefault(self, key: str, default: Any = None) -> Any:
        return self.__dict__.setdefault(key, default)

    def pop(self, key: str, default: Any = _MISSING):
        store = self.__dict__
        if default is _MISSING:
            return store.pop(key)
        return store.pop(key, default)

    def popitem(self):
        return self.__dict__.popitem()

    def clear(self) -> None:
        self.__dict__.clear()

    def filter_keys(self, keys: Iterable[str]) -> "DDM":
        wanted = set(keys)
        return DDM({k: v for k, v in self.items() if k in wanted})

    def exclude_keys(self, keys: Iterable[str]) -> "DDM":
        excluded = set(keys)
        return DDM({k: v for k, v in self.items() if k not in excluded})

    def pick(self, *keys: str) -> "DDM":
        return self.filter_keys(keys)

    def omit(self, *keys: str) -> "DDM":
        return self.exclude_keys(keys)

    def search(self, query: Any, case_sensitive: bool = False) -> Dict[str, Any]:
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
        return {k: v for k, v in self.to_flat_dict().items() if isinstance(v, value_type)}

    def transform(self, func: Callable[[Any], Any]) -> "DDM":
        return DDM({k: func(v) for k, v in self.items()})

    def map_attributes(self, mapping: Mapping[str, Union[str, Callable[[Any], Any]]]) -> "DDM":
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
        return DDM(dict(sorted(self.items(), key=lambda kv: kv[0], reverse=reverse)))

    def sort_by_value(self, reverse: bool = False) -> "DDM":
        return DDM(dict(sorted(self.items(), key=lambda kv: kv[1], reverse=reverse)))

    def group_by(self, func: Callable[[str, Any], Any]) -> Dict[Any, Dict[str, Any]]:
        result: Dict[Any, Dict[str, Any]] = {}
        for k, v in self.items():
            result.setdefault(func(k, v), {})[k] = v
        return result

    def aggregate(self, funcs: Union[Callable[[Iterable[Any]], Any], Mapping[str, Callable[[Iterable[Any]], Any]]]) -> Any:
        vals = self.values()
        if callable(funcs):
            return funcs(vals)
        snapshot = tuple(vals)
        return {name: fn(snapshot) for name, fn in funcs.items()}

    def get_types(self) -> Dict[str, Type[Any]]:
        return {k: type(v) for k, v in self.items()}

    def has_type(self, key: str, value_type: Type[Any]) -> bool:
        value = self.get(key, _MISSING)
        return value is not _MISSING and isinstance(value, value_type)

    def count(self) -> int:
        return len(self)

    def is_empty(self) -> bool:
        return not self.__dict__

    def memory_info(self, recursive: bool = True) -> Dict[str, int]:
        """Return storage estimates without serializing to JSON."""
        return _native.ddm_memory_info(self, recursive)

    def compact(self, intern_keys: bool = True) -> "DDM":
        """Compact key storage in-place. Values are not copied."""
        if intern_keys:
            store = self.__dict__
            compacted = {sys.intern(k) if isinstance(k, str) else k: v for k, v in store.items()}
            store.clear()
            store.update(compacted)
        return self

    def to_csv(self) -> str:
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
