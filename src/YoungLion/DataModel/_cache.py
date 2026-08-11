from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Mapping

from .. import _native
from ._core import DDM

class SmartCache:
    def __init__(self, template: Mapping[str, Any]):
        if not isinstance(template, Mapping):
            raise TypeError("template must be a mapping")
        self.template = dict(template)
        self._completed = 0
        self._filled = 0

    def complete(self, raw_data: Mapping[str, Any]) -> Dict[str, Any]:
        result = _native.cache_complete(self.template, dict(raw_data))
        self._completed += 1
        self._filled += len(_native.cache_missing(self.template, dict(raw_data)))
        return result

    fill = complete

    def complete_batch(self, records: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
        return [self.complete(record) for record in records]

    fill_batch = complete_batch

    def get_missing_keys(self, raw_data: Mapping[str, Any]) -> List[str]:
        return list(_native.cache_missing(self.template, dict(raw_data)))

    def get_extra_keys(self, raw_data: Mapping[str, Any]) -> List[str]:
        return list(_native.cache_extra(self.template, dict(raw_data)))

    def completion_report(self, raw_data: Mapping[str, Any]) -> Dict[str, Any]:
        missing = self.get_missing_keys(raw_data)
        extra = self.get_extra_keys(raw_data)
        return {"missing_keys": missing, "extra_keys": extra, "complete": not missing, "missing_count": len(missing), "extra_count": len(extra)}

    def update_template(self, new_template: Mapping[str, Any]) -> "SmartCache":
        self.template = dict(new_template)
        return self

    def get_stats(self) -> Dict[str, int]:
        return {"completed": self._completed, "filled_keys": self._filled, "template_keys": len(self.template)}

    def reset_stats(self) -> None:
        self._completed = 0
        self._filled = 0


SC = SmartCache


class DDMBuilder:
    def __init__(self):
        self._data: Dict[str, Any] = {}

    def set(self, key: str, value: Any) -> "DDMBuilder":
        self._data[key] = value
        return self

    def set_many(self, **kwargs: Any) -> "DDMBuilder":
        self._data.update(kwargs)
        return self

    def nest(self, key: str, builder_func: Callable[["DDMBuilder"], Any]) -> "DDMBuilder":
        nested = DDMBuilder()
        result = builder_func(nested)
        nested = result if isinstance(result, DDMBuilder) else nested
        self._data[key] = nested.build().to_dict()
        return self

    def add_list(self, key: str, values: Iterable[Any]) -> "DDMBuilder":
        self._data[key] = list(values)
        return self

    def build(self) -> DDM:
        return DDM(_native.ddm_clone_data(DDM(self._data)))


def merge_ddms(*ddms: DDM) -> DDM:
    result = DDM({})
    for item in ddms:
        result.merge(item)
    return result


def compare_ddms(ddm1: DDM, ddm2: DDM) -> Dict[str, Any]:
    diff = ddm1.diff(ddm2)
    return {"equal": not diff, "differences": diff}


def batch_transform(ddms: Iterable[DDM], transformer: Callable[[DDM], Any]) -> List[Any]:
    return [transformer(ddm) for ddm in ddms]


def batch_filter(ddms: Iterable[DDM], predicate: Callable[[DDM], bool]) -> List[DDM]:
    return [ddm for ddm in ddms if predicate(ddm)]


def validate_ddm_batch(ddms: Iterable[DDM], schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [ddm.validate_schema(schema) for ddm in ddms]


def analyze_ddm_structure(ddm: DDM) -> Dict[str, Any]:
    flat = ddm.to_flat_dict()
    return {"keys": len(ddm), "leaf_values": len(flat), "types": {k: type(v).__name__ for k, v in flat.items()}}


def get_ddm_size_info(ddm: DDM) -> Dict[str, int]:
    data = ddm.to_dict()
    encoded = _native.json_dumps(data, indent=-1).encode("utf-8")
    return {"keys": len(data), "json_bytes": len(encoded)}


def create_smart_cache(template: Mapping[str, Any]) -> SmartCache:
    return SmartCache(template)


def fast_complete(template: Mapping[str, Any], raw_data: Mapping[str, Any]) -> Dict[str, Any]:
    return _native.cache_complete(dict(template), dict(raw_data))


def batch_complete_fast(template: Mapping[str, Any], records: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    t = dict(template)
    return [_native.cache_complete(t, dict(record)) for record in records]


