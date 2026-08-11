# Complete public API signature index

Generated from the shipped `.pyi` contracts. Use conceptual API/guides for behavior and this page for signature discovery.

## `YoungLion.DataModel._core`

### `class DDM`

- `_data: Dict[str, Any]`
- `_schema: Dict[str, Any] | None`
- `__init__(self, data: Mapping[str, Any]) -> None`
- `to_dict(self) -> Dict[str, Any]`
- `to_json(self, indent: int=2, include_private: bool=False) -> str`
- `from_json(json_str: str) -> DDM`
- `get_path(self, path: str) -> Any | None`
- `get_path(self, path: str, default: T_DDM) -> Any | T_DDM`
- `get_path(self, path: str, default: Any=None) -> Any`
- `set_path(self, path: str, value: Any) -> bool`
- `has_path(self, path: str) -> bool`
- `clone(self: T_DDM) -> T_DDM`
- `copy(self: T_DDM) -> T_DDM`
- `to_flat_dict(self, prefix: str='', separator: str='.') -> Dict[str, Any]`
- `merge(self: T_DDM, other: DDM | Mapping[str, Any]) -> T_DDM`
- `update(self: T_DDM, *args: Mapping[str, Any], **kwargs: Any) -> T_DDM`
- `diff(self, other: DDM) -> Dict[str, Any]`
- `validate_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]`
- `keys(self) -> KeysView[str]`
- `values(self) -> ValuesView[Any]`
- `items(self) -> ItemsView[str, Any]`
- `get(self, key: str) -> Any | None`
- `get(self, key: str, default: T_DDM) -> Any | T_DDM`
- `get(self, key: str, default: Any=None) -> Any`
- `setdefault(self, key: str, default: Any=None) -> Any`
- `pop(self, key: str) -> Any`
- `pop(self, key: str, default: T_DDM) -> Any | T_DDM`
- `pop(self, key: str, default: Any=...) -> Any`
- `popitem(self) -> tuple[str, Any]`
- `clear(self) -> None`
- `filter_keys(self, keys: Iterable[str]) -> DDM`
- `exclude_keys(self, keys: Iterable[str]) -> DDM`
- `pick(self, *keys: str) -> DDM`
- `omit(self, *keys: str) -> DDM`
- `search(self, query: Any, case_sensitive: bool=False) -> Dict[str, Any]`
- `find_by_type(self, value_type: Type[Any]) -> Dict[str, Any]`
- `transform(self, func: Callable[[Any], Any]) -> DDM`
- `map_attributes(self, mapping: Mapping[str, str | Callable[[Any], Any]]) -> DDM`
- `sort_by_key(self, reverse: bool=False) -> DDM`
- `sort_by_value(self, reverse: bool=False) -> DDM`
- `group_by(self, func: Callable[[str, Any], Any]) -> Dict[Any, Dict[str, Any]]`
- `aggregate(self, funcs: Callable[[Iterable[Any]], Any] | Mapping[str, Callable[[Iterable[Any]], Any]]) -> Any`
- `get_types(self) -> Dict[str, Type[Any]]`
- `has_type(self, key: str, value_type: Type[Any]) -> bool`
- `count(self) -> int`
- `is_empty(self) -> bool`
- `memory_info(self, recursive: bool=True) -> Dict[str, int]`
- `compact(self: T_DDM, intern_keys: bool=True) -> T_DDM`
- `to_csv(self) -> str`
- `__getitem__(self, key: str) -> Any`
- `__setitem__(self, key: str, value: Any) -> None`
- `__delitem__(self, key: str) -> None`
- `__contains__(self, key: object) -> bool`
- `__iter__(self) -> Iterator[str]`
- `__len__(self) -> int`
- `__eq__(self, other: object) -> bool`
- `__repr__(self) -> str`

## `YoungLion.DataModel._variants`

### `class FrozenDDM(DDM)`

- `__init__(self, data: Mapping[str, Any]) -> None`
- `__hash__(self) -> int`
- `thaw(self) -> DDM`

### `class IdentityDDM(DDM)`

- `__hash__(self) -> int`

### `class PackedDDM(Mapping[str, Any])`

- `__init__(self, data: Mapping[str, Any], *, intern_keys: bool=True) -> None`
- `_native_data(self) -> Dict[str, Any]`
- `_data(self) -> Dict[str, Any]`
- `__getitem__(self, key: str) -> Any`
- `__setitem__(self, key: str, value: Any) -> None`
- `__delitem__(self, key: str) -> None`
- `__iter__(self) -> Iterator[str]`
- `__len__(self) -> int`
- `to_dict(self) -> Dict[str, Any]`
- `to_json(self, indent: int=2) -> str`
- `get_path(self, path: str) -> Any | None`
- `get_path(self, path: str, default: T) -> Any | T`
- `get_path(self, path: str, default: Any=None) -> Any`
- `set_path(self, path: str, value: Any) -> bool`
- `has_path(self, path: str) -> bool`
- `clone(self) -> PackedDDM`
- `copy(self) -> PackedDDM`
- `to_flat_dict(self, prefix: str='', separator: str='.') -> Dict[str, Any]`
- `memory_info(self, recursive: bool=True) -> Dict[str, int]`
- `freeze(self) -> FrozenDDM`
- `__repr__(self) -> str`

### `class SchemaDDM(DDM)`

- `__init__(self, data: Mapping[str, Any], schema: Mapping[str, Any], *, strict: bool=True) -> None`
- `validate(self) -> Dict[str, Any]`
- `set_validated(self, path: str, value: Any) -> SchemaDDM`

### `class DefaultDDM(DDM)`

- `__init__(self, data: Mapping[str, Any], default_factory: Callable[[], Any]=...) -> None`
- `__getitem__(self, key: str) -> Any`

### `class LazyDDM(DDM)`

- `__init__(self, data: Mapping[str, Any], lazy: Mapping[str, Callable[[LazyDDM], Any]] | None=None) -> None`
- `invalidate(self, *fields: str) -> LazyDDM`

### `class ViewDDM(Mapping[str, Any])`

- `__init__(self, mapping: Dict[str, Any]) -> None`
- `_native_data(self) -> Dict[str, Any]`
- `_data(self) -> Dict[str, Any]`
- `__getitem__(self, key: str) -> Any`
- `__setitem__(self, key: str, value: Any) -> None`
- `__delitem__(self, key: str) -> None`
- `__iter__(self) -> Iterator[str]`
- `__len__(self) -> int`
- `to_dict(self) -> Dict[str, Any]`
- `get_path(self, path: str) -> Any | None`
- `get_path(self, path: str, default: T) -> Any | T`
- `get_path(self, path: str, default: Any=None) -> Any`
- `set_path(self, path: str, value: Any) -> bool`
- `has_path(self, path: str) -> bool`
- `__repr__(self) -> str`

## `YoungLion.DataModel._collections`

### `class BatchPlan`

- `__init__(self) -> None`
- `set(self, path: str, value: Any) -> BatchPlan`
- `add(self, path: str, amount: float=1.0) -> BatchPlan`
- `subtract(self, path: str, amount: float=1.0) -> BatchPlan`
- `multiply(self, path: str, factor: float) -> BatchPlan`
- `divide(self, path: str, divisor: float) -> BatchPlan`
- `clamp(self, path: str, minimum: float, maximum: float) -> BatchPlan`
- `clear(self) -> BatchPlan`
- `execute(self, collection: DDMCollectionOps[Any]) -> int`
- `__len__(self) -> int`

### `class DDMCollectionOps(Generic[TItem])`

- `batch(self) -> BatchPlan`
- `path_values(self, path: str, default: Any=None) -> list[Any]`
- `set_all(self, path: str, value: Any) -> int`
- `apply_path(self, path: str, func: Callable[[Any], Any], *, write_back: bool=True) -> list[Any]`
- `map(self, func: Callable[[TItem], Any]) -> list[Any]`
- `for_each(self, func: Callable[[TItem], Any]) -> DDMCollectionOps[TItem]`
- `reduce(self, func: Callable[[Any, TItem], Any], initial: Any=...) -> Any`
- `filter(self, predicate: Callable[[TItem], bool]) -> list[TItem]`
- `filter_path(self, path: str, value: Any=None, *, op: str='eq') -> list[TItem]`
- `first(self, predicate: Callable[[TItem], bool] | None=None, default: Any=None) -> TItem | Any`
- `first_path(self, path: str, value: Any=None, *, op: str='eq', default: Any=None) -> TItem | Any`
- `any(self, predicate: Callable[[TItem], bool]) -> bool`
- `all(self, predicate: Callable[[TItem], bool]) -> bool`
- `exists_path(self, path: str, value: Any=None, *, op: str='eq') -> bool`
- `count_path(self, path: str, value: Any=None, *, op: str='eq') -> int`
- `partition_path(self, path: str, value: Any=None, *, op: str='eq') -> tuple[list[TItem], list[TItem]]`
- `update_all(self, **values: Any) -> int`
- `update_where(self, predicate: Callable[[TItem], bool], **values: Any) -> int`
- `apply_where(self, predicate: Callable[[TItem], bool], path: str, func: Callable[[Any], Any]) -> int`
- `increment(self, path: str, amount: float=1.0) -> int`
- `decrement(self, path: str, amount: float=1.0) -> int`
- `multiply(self, path: str, factor: float) -> int`
- `divide(self, path: str, divisor: float) -> int`
- `clamp(self, path: str, minimum: float, maximum: float) -> int`
- `sum(self, path: str) -> float`
- `mean(self, path: str) -> float | None`
- `min(self, path: str) -> float | None`
- `max(self, path: str) -> float | None`
- `numeric_count(self, path: str) -> int`
- `sort_by(self, path: str, *, reverse: bool=False, missing_last: bool=True, inplace: bool=False) -> list[TItem]`
- `sort_by(self, path: str, *, reverse: bool=False, missing_last: bool=True, inplace: bool=True) -> DDMCollectionOps[TItem]`
- `is_sorted(self, path: str, *, reverse: bool=False) -> bool`
- `lower_bound(self, path: str, value: Any, *, reverse: bool=False, verify_sorted: bool=True) -> int`
- `equal_range(self, path: str, value: Any, *, reverse: bool=False, verify_sorted: bool=True) -> tuple[int, int]`
- `binary_search(self, path: str, value: Any, *, reverse: bool=False, verify_sorted: bool=True) -> int`
- `nth(self, path: str, n: int, *, largest: bool=False) -> TItem`
- `top(self, path: str, n: int=10, *, largest: bool=True) -> list[TItem]`
- `bottom(self, path: str, n: int=10) -> list[TItem]`
- `group_by(self, path: str, default: Any=None) -> dict[Any, list[TItem]]`
- `count_by(self, path: str, default: Any=None) -> Counter[Any]`
- `distinct(self, path: str, default: Any=None) -> list[Any]`
- `deduplicate(self, path: str | None=None, *, inplace: bool=False) -> list[TItem]`
- `deduplicate(self, path: str | None=None, *, inplace: bool=True) -> DDMCollectionOps[TItem]`
- `partition(self, predicate: Callable[[TItem], bool]) -> tuple[list[TItem], list[TItem]]`
- `chunks(self, size: int) -> Iterator[list[TItem]]`
- `take(self, count: int) -> list[TItem]`
- `skip(self, count: int) -> list[TItem]`
- `sample(self, count: int) -> list[TItem]`
- `shuffle(self, *, inplace: bool=True) -> DDMCollectionOps[TItem]`
- `shuffle(self, *, inplace: bool=False) -> list[TItem]`
- `reverse(self, *, inplace: bool=True) -> DDMCollectionOps[TItem]`
- `reverse(self, *, inplace: bool=False) -> list[TItem]`
- `rename_path(self, old_path: str, new_path: str, *, missing: Any=...) -> int`
- `copy_path(self, source: str, destination: str, *, missing: Any=...) -> int`
- `move_path(self, source: str, destination: str, *, missing: Any=...) -> int`
- `fill_missing(self, path: str, value: Any) -> int`
- `delete_path(self, path: str) -> int`
- `search(self, *args: Any, **kwargs: Any) -> Any`
- `build_search_index(self, *paths: str, **kwargs: Any) -> Any`

### `class ListDDM(DDMCollectionOps[DDM], MutableSequence[DDM])`

- `__init__(self, values: Iterable[DDM | Mapping[str, Any]]=()) -> None`
- `__len__(self) -> int`
- `__getitem__(self, index: int) -> DDM`
- `__getitem__(self, index: slice) -> list[DDM]`
- `__setitem__(self, index: int | slice, value: DDM | Mapping[str, Any] | Iterable[DDM | Mapping[str, Any]]) -> None`
- `__delitem__(self, index: int | slice) -> None`
- `insert(self, index: int, value: DDM | Mapping[str, Any]) -> None`
- `__iter__(self) -> Iterator[DDM]`
- `indexed(self, *paths: str, **kwargs: Any) -> Any`
- `__repr__(self) -> str`

### `class SetDDM(DDMCollectionOps[DDM])`

- `__init__(self, values: Iterable[DDM | Mapping[str, Any]]=(), *, key: Callable[[DDM], Hashable] | None=None, key_path: str | None=None) -> None`
- `add(self, value: DDM | Mapping[str, Any]) -> bool`
- `discard(self, value: DDM | Mapping[str, Any]) -> bool`
- `remove(self, value: DDM | Mapping[str, Any]) -> None`
- `__contains__(self, value: object) -> bool`
- `__iter__(self) -> Iterator[DDM]`
- `__len__(self) -> int`
- `rehash(self) -> SetDDM`
- `__repr__(self) -> str`

### `class DictDDM(DDMCollectionOps[DDM], MutableMapping[K, DDM], Generic[K])`

- `__init__(self, values: Mapping[K, DDM | Mapping[str, Any]] | None=None, **kwargs: Any) -> None`
- `__getitem__(self, key: K) -> DDM`
- `__setitem__(self, key: K, value: DDM | Mapping[str, Any]) -> None`
- `__delitem__(self, key: K) -> None`
- `__iter__(self) -> Iterator[K]`
- `__len__(self) -> int`
- `values(self) -> Any`
- `items(self) -> Any`
- `keys_for(self, path: str, value: Any=None, *, op: str='eq') -> list[K]`
- `indexed(self, *paths: str, **kwargs: Any) -> Any`
- `__repr__(self) -> str`

### `class DDMTable(ListDDM)`

- `columns(self) -> list[str]`
- `select(self, *paths: str) -> list[dict[str, Any]]`
- `assign(self, **path_values: Any) -> DDMTable`
- `query(self, **criteria: Any) -> DDMTable`

## `YoungLion.DataModel._models`

### `class Range(DDM)`

- `min_val: float`
- `max_val: float`
- `step: float`
- `__init__(self, min_val: float=0.0, max_val: float=1.0, step: float=1.0) -> None`
- `contains(self, value: float) -> bool`
- `clamp(self, value: float) -> float`
- `span(self) -> float`
- `midpoint(self) -> float`
- `normalize(self, value: float) -> float`
- `denormalize(self, value: float) -> float`
- `random(self) -> float`
- `iterate(self) -> Iterator[float]`
- `subdivide(self, parts: int) -> List[Range]`
- `intersect(self, other: Range) -> Range | None`
- `overlaps(self, other: Range) -> bool`

### `class Vector(DDM)`

- `components: List[float]`
- `__init__(self, components: Sequence[float]) -> None`
- `magnitude(self) -> float`
- `normalize(self) -> Vector`
- `dot(self, other: Vector) -> float`
- `cross(self, other: Vector) -> Vector`
- `distance_to(self, other: Vector) -> float`
- `angle_to(self, other: Vector) -> float`
- `add(self, other: Vector) -> Vector`
- `subtract(self, other: Vector) -> Vector`
- `scale(self, scalar: float) -> Vector`
- `project_onto(self, other: Vector) -> Vector`
- `perpendicular(self) -> Vector`
- `lerp(self, other: Vector, t: float) -> Vector`

### `class Timeline(DDM)`

- `start_time: float`
- `end_time: float`
- `events: List[Dict[str, Any]]`
- `__init__(self, start_time: float=0.0, end_time: float=1.0, events: List[Dict[str, Any]] | None=None) -> None`
- `add_event(self, time: float, name: str, data: Any=None) -> Dict[str, Any]`
- `remove_event(self, name: str) -> bool`
- `get_event(self, name: str) -> Dict[str, Any] | None`
- `events_at(self, time: float) -> List[Dict[str, Any]]`
- `events_between(self, start: float, end: float) -> List[Dict[str, Any]]`
- `duration(self) -> float`
- `get_progress(self, time: float) -> float`
- `sort(self, reverse: bool=False) -> Timeline`
- `reverse(self) -> Timeline`

### `class Dataset(DDM)`

- `columns: List[str]`
- `rows: List[Dict[str, Any]]`
- `__init__(self, columns: Sequence[str] | None=None, rows: Sequence[Mapping[str, Any]] | None=None) -> None`
- `add_row(self, row: Mapping[str, Any]) -> Dataset`
- `add_column(self, name: str, default: Any=None) -> Dataset`
- `remove_column(self, name: str) -> Dataset`
- `filter_rows(self, predicate: Callable[[Dict[str, Any]], bool]) -> Dataset`
- `map_column(self, name: str, func: Callable[[Any], Any]) -> Dataset`
- `sort_by(self, column: str, reverse: bool=False) -> Dataset`
- `group_by(self, column: str) -> Dict[Any, Dataset]`
- `aggregate(self, column: str, func: Callable[[Iterable[Any]], Any]) -> Any`
- `stats(self, column: str) -> Dict[str, float]`
- `to_csv(self) -> str`
- `transpose(self) -> List[List[Any]]`

### `class Size(DDM)`

- `width: float`
- `height: float`
- `__init__(self, width: float=0.0, height: float=0.0) -> None`
- `area(self) -> float`
- `perimeter(self) -> float`
- `aspect_ratio(self) -> float`
- `scale(self, factor: float) -> Size`
- `fit_inside(self, other: Size, *, upscale: bool=False) -> Size`
- `contains(self, other: Size) -> bool`

### `class Point(DDM)`

- `x: float`
- `y: float`
- `__init__(self, x: float=0.0, y: float=0.0) -> None`
- `distance_to(self, other: Point) -> float`
- `midpoint(self, other: Point) -> Point`
- `translate(self, dx: float=0.0, dy: float=0.0) -> Point`
- `scale(self, factor: float, origin: Point | None=None) -> Point`
- `to_vector(self) -> Vector`

### `class Color(DDM)`

- `r: int`
- `g: int`
- `b: int`
- `a: int`
- `__init__(self, r: int=0, g: int=0, b: int=0, a: int=255) -> None`
- `from_hex(cls, value: str) -> Color`
- `to_hex(self, include_alpha: bool=False) -> str`
- `normalized(self) -> tuple[float, float, float, float]`
- `blend(self, other: Color, t: float=0.5) -> Color`
- `luminance(self) -> float`
- `contrast_ratio(self, other: Color) -> float`

### `class Matrix(DDM)`

- `rows: List[List[float]]`
- `shape(self) -> tuple[int, int]`
- `__init__(self, rows: Sequence[Sequence[float]]) -> None`
- `identity(cls, size: int) -> Matrix`
- `transpose(self) -> Matrix`
- `add(self, other: Matrix) -> Matrix`
- `subtract(self, other: Matrix) -> Matrix`
- `scale(self, scalar: float) -> Matrix`
- `matmul(self, other: Matrix) -> Matrix`
- `vector_mul(self, vector: Vector) -> Vector`

### `class TreeDDM(DDM)`

- `value: Any`
- `children: List[TreeDDM]`
- `__init__(self, value: Any=None, children: Iterable[TreeDDM] | None=None, **data: Any) -> None`
- `add_child(self, child: Any, **data: Any) -> TreeDDM`
- `walk(self, order: str='dfs') -> Iterator[TreeDDM]`
- `find(self, predicate: Callable[[TreeDDM], bool]) -> TreeDDM | None`
- `depth(self) -> int`
- `size(self) -> int`

## `YoungLion.DataModel._cache`

### `class SmartCache`

- `template: Dict[str, Any]`
- `__init__(self, template: Mapping[str, Any]) -> None`
- `complete(self, raw_data: Mapping[str, Any]) -> Dict[str, Any]`
- `complete_batch(self, records: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]`
- `fill: Callable[[Mapping[str, Any]], Dict[str, Any]]`
- `fill_batch: Callable[[Iterable[Mapping[str, Any]]], List[Dict[str, Any]]]`
- `get_missing_keys(self, raw_data: Mapping[str, Any]) -> List[str]`
- `get_extra_keys(self, raw_data: Mapping[str, Any]) -> List[str]`
- `completion_report(self, raw_data: Mapping[str, Any]) -> Dict[str, Any]`
- `update_template(self, new_template: Mapping[str, Any]) -> SmartCache`
- `get_stats(self) -> Dict[str, int]`
- `reset_stats(self) -> None`

### `class DDMBuilder`

- `__init__(self) -> None`
- `set(self, key: str, value: Any) -> DDMBuilder`
- `set_many(self, **kwargs: Any) -> DDMBuilder`
- `nest(self, key: str, builder_func: Callable[[DDMBuilder], Any]) -> DDMBuilder`
- `add_list(self, key: str, values: Iterable[Any]) -> DDMBuilder`
- `build(self) -> DDM`

- `merge_ddms(*ddms: DDM) -> DDM`
- `compare_ddms(ddm1: DDM, ddm2: DDM) -> Dict[str, Any]`
- `batch_transform(ddms: Iterable[DDM], transformer: Callable[[DDM], Any]) -> List[Any]`
- `batch_filter(ddms: Iterable[DDM], predicate: Callable[[DDM], bool]) -> List[DDM]`
- `validate_ddm_batch(ddms: Iterable[DDM], schema: Dict[str, Any]) -> List[Dict[str, Any]]`
- `analyze_ddm_structure(ddm: DDM) -> Dict[str, Any]`
- `get_ddm_size_info(ddm: DDM) -> Dict[str, int]`
- `create_smart_cache(template: Mapping[str, Any]) -> SmartCache`
- `fast_complete(template: Mapping[str, Any], raw_data: Mapping[str, Any]) -> Dict[str, Any]`
- `batch_complete_fast(template: Mapping[str, Any], records: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]`
## `YoungLion.search`

### `class SearchAlgorithm(str, Enum)`

- `AUTO: SearchAlgorithm`
- `HYBRID: SearchAlgorithm`
- `EXACT: SearchAlgorithm`
- `PREFIX: SearchAlgorithm`
- `SUBSTRING: SearchAlgorithm`
- `REGEX: SearchAlgorithm`
- `LEVENSHTEIN: SearchAlgorithm`
- `DAMERAU: SearchAlgorithm`
- `JARO_WINKLER: SearchAlgorithm`
- `TRIGRAM: SearchAlgorithm`
- `BM25: SearchAlgorithm`

### `class SearchDocument`

- `id: Hashable`
- `text: str`
- `metadata: dict[str, Any]`
- `tags: tuple[str, ...]`
- `fields: dict[str, Any]`
- `__init__(self, id: Hashable, text: str, metadata: dict[str, Any]=..., tags: tuple[str, ...]=(), fields: dict[str, Any]=...) -> None`
- `searchable_text(self) -> str`

### `class SearchResult`

- `sort_index: float`
- `score: float`
- `document: SearchDocument`
- `algorithm: str`
- `positions: tuple[int, ...]`
- `matched_terms: tuple[str, ...]`
- `details: dict[str, float]`
- `__init__(self, score: float, document: SearchDocument, algorithm: str='hybrid', positions: tuple[int, ...]=(), matched_terms: tuple[str, ...]=(), details: dict[str, float]=...) -> None`
- `value(self) -> Any`

### `class SearchStats`

- `documents: int`
- `tokens: int`
- `unique_tokens: int`
- `average_document_length: float`
- `__init__(self, documents: int, tokens: int, unique_tokens: int, average_document_length: float) -> None`

### `class SearchQuery`

- `text: str`
- `algorithm: SearchAlgorithm | str`
- `limit: int | None`
- `min_score: float`
- `filters: Mapping[str, Any] | None`
- `regex_flags: int`
- `__init__(self, text: str, algorithm: SearchAlgorithm | str=SearchAlgorithm.HYBRID, limit: int | None=10, min_score: float=0.0, filters: Mapping[str, Any] | None=None, regex_flags: int=0) -> None`

### `class Posting`

- `doc_id: Hashable`
- `term_frequency: int`
- `__init__(self, doc_id: Hashable, term_frequency: int) -> None`

### `class AutocompleteEntry`

- `term: str`
- `payload: Any`
- `weight: float`
- `__init__(self, term: str, payload: Any=None, weight: float=1.0) -> None`

### `class PatternMatch`

- `pattern: str`
- `start: int`
- `end: int`
- `pattern_index: int`
- `__init__(self, pattern: str, start: int, end: int, pattern_index: int) -> None`

### `class FuzzyMatcher`

- `levenshtein(a: str, b: str, *, case_sensitive: bool=False) -> int`
- `damerau_levenshtein(a: str, b: str, *, case_sensitive: bool=False) -> int`
- `levenshtein_ratio(a: str, b: str, *, damerau: bool=False, case_sensitive: bool=False) -> float`
- `jaro_winkler(a: str, b: str, *, case_sensitive: bool=False) -> float`
- `trigram(a: str, b: str, *, case_sensitive: bool=False) -> float`
- `hybrid(a: str, b: str, *, case_sensitive: bool=False) -> float`

### `class InvertedIndex`

- `__init__(self) -> None`
- `add(self, doc_id: Hashable, tokens: Iterable[str]) -> None`
- `remove(self, doc_id: Hashable) -> bool`
- `clear(self) -> None`
- `tokens(self, doc_id: Hashable) -> tuple[str, ...]`
- `postings(self, term: str) -> tuple[Posting, ...]`
- `terms(self) -> Iterator[str]`
- `prefix_terms(self, prefix: str, *, limit: int | None=None) -> list[str]`
- `fuzzy_terms(self, query: str, *, algorithm: SearchAlgorithm | str=SearchAlgorithm.HYBRID, threshold: float=0.6, limit: int=8) -> list[tuple[str, float]]`
- `candidate_ids(self, terms: Iterable[str]) -> set[Hashable]`
- `bm25(self, query_tokens: Iterable[str], *, candidates: set[Hashable] | None=None, k1: float=1.5, b: float=0.75) -> dict[Hashable, float]`
- `document_count(self) -> int`
- `token_count(self) -> int`
- `unique_token_count(self) -> int`

### `class SearchIndex`

- `__init__(self, documents: Iterable[SearchDocument | Mapping[str, Any] | str] | None=None, *, case_sensitive: bool=False) -> None`
- `add(self, document: SearchDocument | Mapping[str, Any] | str, *, doc_id: Hashable | None=None) -> SearchDocument`
- `extend(self, documents: Iterable[SearchDocument | Mapping[str, Any] | str]) -> SearchIndex`
- `remove(self, doc_id: Hashable) -> bool`
- `update(self, doc_id: Hashable, **changes: Any) -> SearchDocument`
- `clear(self) -> None`
- `__len__(self) -> int`
- `__iter__(self) -> Iterator[SearchDocument]`
- `stats(self) -> SearchStats`
- `inverted_index(self) -> InvertedIndex`
- `search(self, query: str | SearchQuery, *, algorithm: SearchAlgorithm | str=SearchAlgorithm.HYBRID, limit: int | None=10, min_score: float=0.0, filters: Mapping[str, Any] | None=None, regex_flags: int=0) -> list[SearchResult]`

### `class BM25Index(SearchIndex)`

- `search(self, query: str | SearchQuery, **kwargs: Any) -> list[SearchResult]`

### `class AutocompleteIndex`

- `__init__(self, entries: Iterable[str | AutocompleteEntry | tuple[str, Any] | tuple[str, Any, float]]=(), *, case_sensitive: bool=False) -> None`
- `add(self, entry: str | AutocompleteEntry | tuple[str, Any] | tuple[str, Any, float], payload: Any=None, weight: float=1.0) -> AutocompleteEntry`
- `suggest(self, prefix: str, *, limit: int=10, fuzzy_fallback: bool=True, min_score: float=0.62) -> list[AutocompleteEntry]`
- `__len__(self) -> int`

### `class MultiPatternSearch`

- `__init__(self, patterns: Iterable[str], *, case_sensitive: bool=False) -> None`
- `find(self, text: str) -> list[PatternMatch]`
- `contains_any(self, text: str) -> bool`

### `class NumericSearch`

- `__init__(self, values: Iterable[tuple[float, Any]]=()) -> None`
- `add(self, value: float, payload: Any=None) -> None`
- `range(self, minimum: float, maximum: float) -> list[tuple[float, Any]]`
- `nearest(self, value: float, k: int=1) -> list[tuple[float, Any]]`
- `__len__(self) -> int`

### `class StructuredSearch`

- `__init__(self, records: Iterable[Mapping[str, Any]]=(), *, id_field: str='id', field_weights: Mapping[str, float] | None=None, case_sensitive: bool=False) -> None`
- `add(self, record: Mapping[str, Any]) -> SearchDocument`
- `search(self, query: str | SearchQuery, **kwargs: Any) -> list[SearchResult]`

### `class FileSearchEngine`

- `__init__(self, root: str | Path='.', *, content: bool=False, max_content_bytes: int=2000000, extensions: Iterable[str] | None=None, case_sensitive: bool=False) -> None`
- `refresh(self) -> FileSearchEngine`
- `search_results(self, query: str | SearchQuery, *, extension: str | Sequence[str] | None=None, min_size: int | None=None, max_size: int | None=None, **kwargs: Any) -> list[SearchResult]`
- `search(self, query: str | SearchQuery, **kwargs: Any) -> list[str]`

### `class GenerateTags`

- `__init__(self, terms: str | list[str], lowercase: bool=True, clean_special_chars: bool=True, min_words: int=1, max_words: int | None=None, replacements: dict[str, str] | None=None, stop_words: list[str] | None=None, max_tags: int=10000) -> None`
- `get_tags(self) -> list[str]`

### `class SearchData`

- `__init__(self, data: list[dict[str, Any]]) -> None`
- `get_tags(self) -> list[str]`
- `get(self, tag: str) -> list[Any]`
- `__getitem__(self, tag: str) -> list[Any]`
- `__contains__(self, tag: object) -> bool`
- `__repr__(self) -> str`

### `class Search`

- `__init__(self, sdata: SearchData, only_tag: bool=False) -> None`
- `search(self, query: str) -> list[Any]`
- `ranked(self, query: str, **kwargs: Any) -> list[SearchResult]`

### `class SearchFile`

- `__init__(self, root: str | Path='.') -> None`
- `search(self, query: str, content: bool=False, case_sensitive: bool=False) -> list[str]`

### `class DDMSearchHit`

- `item: Any`
- `key: Any`
- `path: str`
- `value: Any`
- `score: float`
- `algorithm: str`
- `__init__(self, item: Any, key: Any, path: str, value: Any, score: float=1.0, algorithm: str='exact') -> None`

### `class DDMPathIndex`

- `path: str`
- `case_sensitive: bool`
- `__init__(self, path: str, entries: Sequence[tuple[Any, Any]], *, text: bool=True, case_sensitive: bool=False, objects: Mapping[Any, Any] | None=None) -> None`
- `exact(self, value: Any) -> list[DDMSearchHit]`
- `range(self, minimum: Any=None, maximum: Any=None, *, include_min: bool=True, include_max: bool=True) -> list[DDMSearchHit]`
- `prefix(self, prefix: str, *, limit: int | None=None) -> list[DDMSearchHit]`
- `text(self, query: str, *, algorithm: SearchAlgorithm | str=SearchAlgorithm.HYBRID, limit: int | None=10, min_score: float=0.0) -> list[DDMSearchHit]`
- `contains(self, needle: Any, *, case_sensitive: bool | None=None) -> list[DDMSearchHit]`
- `stats(self) -> dict[str, int]`

### `class DDMCompositeIndex`

- `__init__(self, paths: Sequence[str], entries: Sequence[tuple[Any, Any]], *, objects: Mapping[Any, Any] | None=None) -> None`
- `find(self, *values: Any) -> list[Any]`

### `class DDMSearchEngine`

- `__init__(self, source: Any, *, case_sensitive: bool=False) -> None`
- `refresh(self) -> DDMSearchEngine`
- `invalidate(self, paths: Iterable[str] | None=None) -> None`
- `create_index(self, path: str, *, text: bool=True) -> DDMPathIndex`
- `create_indexes(self, *paths: str, text: bool=True) -> DDMSearchEngine`
- `create_composite_index(self, *paths: str) -> DDMCompositeIndex`
- `find(self, path: str, value: Any=None, *, op: str='eq', limit: int | None=None, use_index: bool=True) -> list[Any]`
- `find_one(self, path: str, value: Any=None, *, op: str='eq', default: Any=None, use_index: bool=True) -> Any`
- `exists(self, path: str, value: Any=None, *, op: str='eq') -> bool`
- `count(self, path: str, value: Any=None, *, op: str='eq') -> int`
- `between(self, path: str, minimum: Any, maximum: Any, *, include_min: bool=True, include_max: bool=True) -> list[Any]`
- `text(self, path: str, query: str, *, algorithm: SearchAlgorithm | str=SearchAlgorithm.HYBRID, limit: int | None=10, min_score: float=0.0, hits: bool=False) -> Any`
- `composite(self, paths: Sequence[str], values: Sequence[Any]) -> list[Any]`
- `where(self, **lookups: Any) -> list[Any]`
- `order_by(self, path: str, *, reverse: bool=False, missing_last: bool=True) -> list[Any]`
- `values(self, path: str, default: Any=None) -> list[Any]`
- `stats(self) -> dict[str, Any]`

### `class ApplicationSearch`

- `__init__(self, *, case_sensitive: bool=False) -> None`
- `add(self, doc_id: Hashable, title: str, body: str='', *, tags: Iterable[str]=(), fields: Mapping[str, Any] | None=None, payload: Any=None, autocomplete_weight: float=1.0) -> SearchDocument`
- `update(self, doc_id: Hashable, *, title: str | None=None, body: str | None=None, tags: Iterable[str] | None=None, fields: Mapping[str, Any] | None=None, payload: Any=..., autocomplete_weight: float | None=None) -> SearchDocument`
- `remove(self, doc_id: Hashable) -> bool`
- `search_results(self, query: str | SearchQuery, **kwargs: Any) -> list[SearchResult]`
- `search(self, query: str | SearchQuery, **kwargs: Any) -> list[Any]`
- `suggest(self, prefix: str, *, limit: int=10, fuzzy: bool=True) -> list[AutocompleteEntry]`
- `facet(self, field: str, *, query: str | None=None, limit: int | None=None) -> list[tuple[Any, int]]`
- `stats(self) -> SearchStats`

- `tokenize(text: Any, *, case_sensitive: bool=False, min_length: int=1) -> list[str]`
## `YoungLion.function._base`

### `class Debugger`

- `COLORS: dict[str, str]`
- `SYMBOLS: dict[str, str]`
- `level: int`
- `DefaultSymbol: bool`
- `ansi: bool`
- `__init__(self, level: int=0, DefaultSymbol: bool=False) -> None`
- `info(self, message: str) -> None`
- `debug(self, message: str) -> None`
- `success(self, message: str) -> None`
- `warning(self, message: str) -> None`
- `error(self, message: str) -> None`
- `critical(self, message: str) -> None`
- `custom(self, message: str, color_code: str='\x1b[1;95m', symbol: str='*') -> None`
- `set_level(self, level: int) -> None`

### `class FileBase`

- `SUPPORTED_FORMATS: list[str]`
- `filefolder: str | None`
- `debug: bool`
- `debugger: Debugger`
- `__init__(self, filefolder: str | None=None, debug: bool=False, debugger: Debugger | None=None) -> None`
- `get_info(self, path: str) -> dict[str, Any]`
- `rename_file(self, old_path: str, new_name: str) -> bool`
- `rename_folder(self, old_path: str, new_name: str) -> bool`
- `create_shortcut(self, target_path: str, shortcut_path: str, description: str='') -> bool`
- `list_files_and_folders(self, path: str | None=None) -> list[str]`
- `create_folder(self, folder_path: str) -> bool`
- `copy_file(self, source: str, destination: str) -> bool`
- `copy_folder(self, source: str, destination: str) -> bool`
- `move_file(self, source: str, destination: str) -> bool`
- `move_folder(self, source: str, destination: str) -> bool`
- `delete_file(self, path: str) -> bool`
- `delete_folder(self, path: str) -> bool`
- `json_read(self, path: str, default: dict[str, Any] | list[Any] | None=None) -> dict[str, Any] | list[Any]`
- `json_write(self, path: str, data: dict[str, Any] | list[Any]) -> None`
- `txt_read_str(self, path: str) -> str`
- `txt_read_linear(self, path: str) -> dict[str, str]`
- `txt_write_str(self, path: str, content: str) -> None`
- `txt_write_linear(self, path: str, data: Mapping[int, str]) -> None`
- `exists(self, path: str) -> bool`
- `is_file(self, path: str) -> bool`
- `is_folder(self, path: str) -> bool`
- `file_size(self, path: str) -> int`
- `directory_size(self, path: str | None=None, recursive: bool=True) -> int`
- `read_bytes(self, path: str) -> bytes`
- `write_bytes(self, path: str, data: bytes | bytearray | memoryview, append: bool=False) -> None`
- `append_bytes(self, path: str, data: bytes | bytearray | memoryview) -> None`
- `touch(self, path: str) -> bool`
- `line_count(self, path: str) -> int`
- `compare_files(self, first: str, second: str) -> bool`
- `checksum(self, path: str, algorithm: str='sha256') -> str`
- `head(self, path: str, lines: int=10) -> list[str]`
- `tail(self, path: str, lines: int=10, block_size: int=8192) -> list[str]`
- `atomic_write_text(self, path: str, content: str) -> None`
- `atomic_write_bytes(self, path: str, data: bytes | bytearray | memoryview) -> None`
- `atomic_write_json(self, path: str, data: dict[str, Any] | list[Any], indent: int=4) -> None`
- `find_files(self, pattern: str='*', path: str | None=None, *, recursive: bool=True, extensions: list[str] | None=None, min_size: int | None=None, max_size: int | None=None) -> list[str]`
- `read_chunks(self, path: str, chunk_size: int=1024 * 1024) -> Iterator[bytes]`
- `backup(self, path: str, destination: str | None=None) -> str`
- `log_read(self, path: str) -> dict[str, str]`
- `log_write(self, path: str, content: str) -> None`
- `log_write_entry(self, path: str, entry: str) -> None`

## `YoungLion.function._formats`

### `class FileFormatsMixin`

- `pdf_read(self, path: str) -> str`
- `pdf_write(self, path: str, content: str) -> None`
- `xml_read(self, path: str) -> dict[str, Any] | None`
- `xml_write(self, path: str, data: dict[str, Any], root_element: str='root') -> None`
- `xml_append(self, path: str, data: dict[str, Any], root_element: str='root') -> None`
- `xml_find(self, path: str, query: str) -> dict[str, Any] | None`
- `csv_read(self, path: str, delimiter: str=',', quotechar: str='"') -> list[dict[str, str]]`
- `csv_write(self, path: str, data: list[dict[str, str]], fieldnames: list[str] | None=None, delimiter: str=',', quotechar: str='"') -> None`
- `csv_append(self, path: str, data: list[dict[str, str]], fieldnames: list[str] | None=None, delimiter: str=',', quotechar: str='"') -> None`
- `csv_update(self, path: str, data: list[dict[str, str]], identifier: str, delimiter: str=',', quotechar: str='"') -> None`
- `yaml_read(self, path: str, default: dict[str, Any] | None=None) -> dict[str, Any]`
- `yaml_write(self, path: str, data: dict[str, Any]) -> None`
- `ini_read(self, path: str, default: dict[str, dict[str, str]] | None=None) -> dict[str, dict[str, str]]`
- `ini_write(self, path: str, data: dict[str, dict[str, str]], append: bool=False) -> None`
- `properties_read(self, path: str) -> dict[str, str]`
- `properties_write(self, path: str, data: dict[str, str], append: bool=False) -> None`

## `YoungLion.function._extra`

### `class FileExtraMixin`

- `md_write(self, path: str, content: str, append: bool=False) -> None`
- `rtf_write(self, path: str, content: str, append: bool=False) -> None`
- `html_write(self, path: str, content: str, append: bool=False) -> None`
- `css_write(self, path: str, content: str, append: bool=False) -> None`
- `js_write(self, path: str, content: str, append: bool=False) -> None`
- `tex_write(self, path: str, content: str) -> None`
- `tex_append(self, path: str, content: str) -> None`
- `py_write(self, path: str, content: str, append: bool=False) -> None`
- `handle_compressed(self, path: str, action: str, target: str | None=None) -> Any`
- `sql_execute(self, path: str, query: str, params: Sequence[Any]=()) -> Any`
- `markdown_to_latex(markdown: str) -> str`
- `latex_compile(content: str) -> str`
- `tex_to_markdown(content: str) -> str`
- `latex_to_html(self, content: str, output_path: str | None=None) -> str`
- `latex_to_image(self, content: str, output_path: str) -> str`
- `py_run(self, path: str, args: Sequence[str] | None=None, terminal: bool=False) -> str | None`
- `py_add_code(self, path: str, code: str, position: str | int='end') -> None`
- `js_run(self, path: str, args: Sequence[str] | None=None, terminal: bool=False) -> str | None`

## `YoungLion.function._utilities`

### `class CommandResult`

- `args: tuple[str, ...]`
- `returncode: int`
- `stdout: str`
- `stderr: str`
- `duration: float`
- `ok(self) -> bool`
- `check(self) -> CommandResult`

### `class ScriptRunner`

- `INTERPRETERS: dict[str, Callable[[], str]]`
- `default_interpreter: str`
- `__init__(self, default_interpreter: str='node') -> None`
- `set_default_interpreter(self, interpreter: str) -> ScriptRunner`
- `detect_interpreter(self, path: str) -> str`
- `run(self, command: Sequence[Any], *, cwd: str | None=None, env: Mapping[str, str] | None=None, timeout: float | None=None, input_text: str | None=None, check: bool=False, capture_output: bool=True) -> CommandResult`
- `run_async(self, command: Sequence[Any], *, cwd: str | None=None, env: Mapping[str, str] | None=None, stdout: Any=..., stderr: Any=...) -> Any`
- `run_script(self, path: str, interpreter: str | None=None, terminal: bool=False, inputs: str | Sequence[str] | None=None, output: bool=True, *, cwd: str | None=None, env: Mapping[str, str] | None=None, timeout: float | None=None, check: bool=True) -> str | None`

### `class TaskInfo`

- `id: str`
- `state: str`
- `created_at: float`
- `next_run: float`
- `repeat: float | None`
- `priority: int`
- `runs: int`
- `failures: int`
- `last_result: Any`
- `last_error: BaseException | None`

### `class TaskScheduler`

- `__init__(self) -> None`
- `schedule_task(self, func: Callable[..., Any], delay: float=0.0, repeat: float | None=None, priority: int=0, args: Sequence[Any]=(), kwargs: dict[str, Any] | None=None, *, retries: int=0, retry_delay: float=0.0, task_id: str | None=None) -> str`
- `schedule_at(self, when: datetime, func: Callable[..., Any], **kwargs: Any) -> str`
- `run_now(self, task_id: str) -> bool`
- `cancel_task(self, task_id: str) -> bool`
- `pause_task(self, task_id: str) -> bool`
- `resume_task(self, task_id: str) -> bool`
- `get_task(self, task_id: str) -> TaskInfo | None`
- `list_tasks(self) -> list[dict[str, Any]]`
- `wait(self, task_id: str, timeout: float | None=None, poll_interval: float=0.01) -> TaskInfo | None`
- `shutdown(self, cancel_pending: bool=True) -> None`

### `class Logger`

- `__init__(self, log_file: str='app.log', log_level: str='INFO', *, console: bool=True, max_bytes: int=0, backup_count: int=5) -> None`
- `set_log_level(self, level: str) -> Logger`
- `bind(self, **context: Any) -> Logger`
- `log_debug(self, message: str, **fields: Any) -> None`
- `log_info(self, message: str, **fields: Any) -> None`
- `log_warning(self, message: str, **fields: Any) -> None`
- `log_error(self, message: str, **fields: Any) -> None`
- `log_critical(self, message: str, **fields: Any) -> None`

### `class EmailManager`

- `__init__(self, smtp_server: str, smtp_port: int, email_address: str, email_password: str, imap_server: str | None=None, *, use_ssl: bool=False, starttls: bool=True) -> None`
- `build_email(self, to: str | Sequence[str], subject: str, body: str, *, html: str | None=None, cc: str | Sequence[str] | None=None, bcc: str | Sequence[str] | None=None, attachments: Sequence[Any]=()) -> Any`
- `send_message(self, message: Any) -> bool`
- `send_email(self, to: str | Sequence[str], subject: str, body: str, **kwargs: Any) -> bool`
- `schedule_email(self, to: str | Sequence[str], subject: str, body: str, send_time: datetime, **kwargs: Any) -> Any`
- `check_inbox(self, user: str | None=None, limit: int=10, mailbox: str='INBOX') -> list[dict[str, Any]]`

### `class FileTransferManager`

- `__init__(self) -> None`
- `upload(self, file_path: str, destination: str, protocol: str='ftp', host: str='', username: str='', password: str='', port: int | None=None, *, progress: Callable[[int, int], Any] | None=None) -> str`
- `download(self, source: str, destination: str, protocol: str='ftp', host: str='', username: str='', password: str='', port: int | None=None, *, progress: Callable[[int, int], Any] | None=None) -> str`
- `get_status(self, transfer_id: str) -> str | None`
- `get_progress(self, transfer_id: str) -> int | None`

### `class TextProcessor`

- `__init__(self, text: str='') -> None`
- `set_text(self, text: str) -> TextProcessor`
- `words(self, text: str | None=None) -> list[str]`
- `sentences(self, text: str | None=None) -> list[str]`
- `word_count(self, text: str | None=None) -> int`
- `sentence_count(self, text: str | None=None) -> int`
- `line_count(self, text: str | None=None) -> int`
- `character_count(self, text: str | None=None, include_spaces: bool=True) -> int`
- `keyword_search(self, keyword: str, text: str | None=None, case_sensitive: bool=False) -> list[int]`
- `replace(self, old: str, new: str, text: str | None=None) -> str`
- `normalize_whitespace(self, text: str | None=None) -> str`
- `most_frequent_words(self, n: int=10, text: str | None=None) -> list[tuple[str, int]]`
- `ngrams(self, n: int=2, text: str | None=None) -> list[tuple[str, ...]]`
- `extract_emails(self, text: str | None=None) -> list[str]`
- `extract_urls(self, text: str | None=None) -> list[str]`
- `summarize(self, sentences: int=3, text: str | None=None) -> str`
- `similarity(self, other: str, text: str | None=None, algorithm: str='hybrid') -> float`
- `readability_score(self, text: str | None=None) -> float`
- `stats(self, text: str | None=None) -> dict[str, Any]`

### `class EventBus`

- `__init__(self) -> None`
- `subscribe(self, event: str, callback: Callable[..., Any], *, once: bool=False, priority: int=0) -> str`
- `once(self, event: str, callback: Callable[..., Any], *, priority: int=0) -> str`
- `unsubscribe(self, token: str) -> bool`
- `emit(self, event: str, *args: Any, **kwargs: Any) -> list[Any]`
- `listener_count(self, event: str | None=None) -> int`
- `clear(self, event: str | None=None) -> None`

### `class TTLCache`

- `__init__(self, max_size: int=1024, default_ttl: float | None=300.0) -> None`
- `set(self, key: Any, value: Any, ttl: Any=...) -> None`
- `get(self, key: Any, default: Any=None) -> Any`
- `pop(self, key: Any, default: Any=...) -> Any`
- `delete(self, key: Any) -> bool`
- `purge(self) -> int`
- `clear(self) -> None`
- `items(self) -> list[tuple[Any, Any]]`
- `stats(self) -> dict[str, int]`
- `__contains__(self, key: object) -> bool`
- `__len__(self) -> int`

### `class RateLimiter`

- `__init__(self, rate: float, capacity: float | None=None) -> None`
- `available(self) -> float`
- `try_acquire(self, tokens: float=1.0) -> bool`
- `acquire(self, tokens: float=1.0, timeout: float | None=None) -> bool`

### `class RetryPolicy`

- `__init__(self, attempts: int=3, delay: float=0.0, backoff: float=2.0, max_delay: float | None=None, exceptions: tuple[type[BaseException], ...]=(Exception,)) -> None`
- `call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any`

### `class CircuitBreaker`

- `CLOSED: str`
- `OPEN: str`
- `HALF_OPEN: str`
- `__init__(self, failure_threshold: int=5, recovery_timeout: float=30.0, success_threshold: int=1) -> None`
- `state(self) -> str`
- `allow(self) -> bool`
- `reset(self) -> None`
- `call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any`

### `class Stopwatch`

- `__init__(self, start: bool=True) -> None`
- `running(self) -> bool`
- `elapsed(self) -> float`
- `start(self) -> Stopwatch`
- `stop(self) -> float`
- `reset(self, *, start: bool=True) -> Stopwatch`
- `lap(self) -> float`

### `class Terminal`

- `supports_color(stream: Any=None) -> bool`
- `size(fallback: tuple[int, int]=(80, 24)) -> tuple[int, int]`
- `strip_ansi(cls, text: object) -> str`
- `visible_width(cls, text: object) -> int`
- `truncate(cls, text: object, width: int, suffix: str='…') -> str`
- `pad(cls, text: object, width: int, align: str='left') -> str`
- `table(cls, rows: Iterable[Sequence[Any]], headers: Sequence[Any] | None=None, *, padding: int=1, max_width: int | None=None) -> str`
- `clear(stream: Any=None) -> None`
- `progress(current: float, total: float, *, width: int=30, label: str='', fill: str='#', empty: str='-') -> str`

## `YoungLion.Colors`

### `class Colors`

- `RESET: ClassVar[str]`
- `BRIGHT: ClassVar[str]`
- `DIM: ClassVar[str]`
- `ITALIC: ClassVar[str]`
- `UNDERLINE: ClassVar[str]`
- `BLINK: ClassVar[str]`
- `REVERSE: ClassVar[str]`
- `HIDDEN: ClassVar[str]`
- `STRIKETHROUGH: ClassVar[str]`
- `BLACK: ClassVar[str]`
- `RED: ClassVar[str]`
- `GREEN: ClassVar[str]`
- `YELLOW: ClassVar[str]`
- `BLUE: ClassVar[str]`
- `MAGENTA: ClassVar[str]`
- `CYAN: ClassVar[str]`
- `WHITE: ClassVar[str]`
- `BRIGHT_BLACK: ClassVar[str]`
- `BRIGHT_RED: ClassVar[str]`
- `BRIGHT_GREEN: ClassVar[str]`
- `BRIGHT_YELLOW: ClassVar[str]`
- `BRIGHT_BLUE: ClassVar[str]`
- `BRIGHT_MAGENTA: ClassVar[str]`
- `BRIGHT_CYAN: ClassVar[str]`
- `BRIGHT_WHITE: ClassVar[str]`
- `BG_BLACK: ClassVar[str]`
- `BG_RED: ClassVar[str]`
- `BG_GREEN: ClassVar[str]`
- `BG_YELLOW: ClassVar[str]`
- `BG_BLUE: ClassVar[str]`
- `BG_MAGENTA: ClassVar[str]`
- `BG_CYAN: ClassVar[str]`
- `BG_WHITE: ClassVar[str]`
- `BG_BRIGHT_BLACK: ClassVar[str]`
- `BG_BRIGHT_RED: ClassVar[str]`
- `BG_BRIGHT_GREEN: ClassVar[str]`
- `BG_BRIGHT_YELLOW: ClassVar[str]`
- `BG_BRIGHT_BLUE: ClassVar[str]`
- `BG_BRIGHT_MAGENTA: ClassVar[str]`
- `BG_BRIGHT_CYAN: ClassVar[str]`
- `BG_BRIGHT_WHITE: ClassVar[str]`
- `rgb(cls, r: int, g: int, b: int) -> str`
- `bg_rgb(cls, r: int, g: int, b: int) -> str`
- `ansi256(index: int) -> str`
- `bg_ansi256(index: int) -> str`
- `strip(text: object) -> str`
- `wrap(cls, text: object, *styles: str, reset: bool=True) -> str`
- `foreground(cls, rgb: tuple[int, int, int], text: object) -> str`
- `background(cls, rgb: tuple[int, int, int], text: object) -> str`
- `gradient(cls, text: str, start: tuple[int, int, int], end: tuple[int, int, int]) -> str`

## `YoungLion._native`

- `json_dumps(data: Any, indent: int=2) -> str`
- `json_loads(data: str) -> Any`
- `ddm_to_dict(obj: Any) -> dict[str, Any]`
- `ddm_clone_data(obj: Any) -> dict[str, Any]`
- `ddm_get_path(obj: Any, path: str, default: Any=None) -> Any`
- `ddm_set_path(obj: Any, path: str, value: Any) -> bool`
- `ddm_has_path(obj: Any, path: str) -> bool`
- `ddm_merge_data(obj: Any, other: Any) -> dict[str, Any]`
- `ddm_diff(a: Any, b: Any) -> dict[str, Any]`
- `ddm_flatten(obj: Any, prefix: str='', separator: str='.') -> dict[str, Any]`
- `ddm_validate_schema(obj: Any, schema: Mapping[str, Any]) -> dict[str, Any]`
- `ddm_memory_info(obj: Any, recursive: bool=True) -> dict[str, int]`
- `cache_complete(template: Mapping[str, Any], data: Mapping[str, Any]) -> dict[str, Any]`
- `cache_missing(template: Mapping[str, Any], data: Mapping[str, Any]) -> list[str]`
- `cache_extra(template: Mapping[str, Any], data: Mapping[str, Any]) -> list[str]`
- `vec_magnitude(values: Sequence[float]) -> float`
- `vec_dot(a: Sequence[float], b: Sequence[float]) -> float`
- `vec_add(a: Sequence[float], b: Sequence[float]) -> list[float]`
- `vec_sub(a: Sequence[float], b: Sequence[float]) -> list[float]`
- `vec_scale(a: Sequence[float], scalar: float) -> list[float]`
- `vec_cross(a: Sequence[float], b: Sequence[float]) -> list[float]`
- `resolve_path(root: str, path: str, create_parent: bool=True) -> str`
- `get_info(path: str) -> dict[str, Any]`
- `list_dir(path: str) -> list[str]`
- `create_dir(path: str) -> bool`
- `remove_path(path: str, recursive: bool=False) -> bool`
- `rename_path(source: str, destination: str) -> bool`
- `copy_path(source: str, destination: str, recursive: bool=False) -> bool`
- `move_path(source: str, destination: str) -> bool`
- `read_text(path: str) -> str`
- `write_text(path: str, content: str, append: bool=False) -> None`
- `read_bytes(path: str) -> bytes`
- `write_bytes(path: str, data: bytes, append: bool=False) -> None`
- `json_read_file(path: str) -> Any`
- `json_write_file(path: str, data: Any, indent: int=4) -> None`
- `csv_read(path: str, delimiter: str=',', quotechar: str='"') -> list[dict[str, str]]`
- `csv_write(path: str, data: list[dict[str, str]], fieldnames: list[str] | None=None, delimiter: str=',', quotechar: str='"', append: bool=False) -> None`
- `properties_read(path: str) -> dict[str, str]`
- `properties_write(path: str, data: Mapping[str, str], append: bool=False) -> None`
- `ini_read(path: str) -> dict[str, dict[str, str]]`
- `ini_write(path: str, data: Mapping[str, Mapping[str, str]], append: bool=False) -> None`
- `pdf_write(path: str, content: str) -> None`
- `pdf_read(path: str) -> str`
- `file_crc32(path: str) -> str`
- `directory_size(path: str, recursive: bool=True) -> int`
- `touch(path: str) -> bool`
- `line_count(path: str) -> int`
- `compare_files(a: str, b: str) -> bool`
- `levenshtein(a: str, b: str) -> int`
- `damerau_levenshtein(a: str, b: str) -> int`
- `jaro_winkler(a: str, b: str, prefix_scale: float=0.1) -> float`
- `trigram_similarity(a: str, b: str) -> float`
- `find_all(haystack: str, needle: str) -> list[int]`
- `bm25_scores(query_tokens: Sequence[str], documents: Sequence[Sequence[str]], k1: float=1.5, b: float=0.75) -> list[float]`
- `batch_get_path(items: Sequence[Any], path: str, default: Any=None) -> list[Any]`
- `batch_set_path(items: Sequence[Any], path: str, value: Any) -> int`
- `batch_apply_path(items: Sequence[Any], path: str, func: Callable[[Any], Any], write_back: bool=True) -> list[Any]`
- `batch_filter_path(items: Sequence[Any], path: str, op: str, expected: Any=None) -> list[Any]`
- `batch_count_path(items: Sequence[Any], path: str, op: str, expected: Any=None) -> int`
- `batch_partition_path(items: Sequence[Any], path: str, op: str, expected: Any=None) -> tuple[list[Any], list[Any]]`
- `batch_numeric_op(items: Sequence[Any], path: str, op: str, a: float, b: float=0.0) -> int`
- `batch_numeric_reduce(items: Sequence[Any], path: str, op: str) -> float | None`
- `batch_sort_path(items: Sequence[Any], path: str, reverse: bool=False, missing_last: bool=True) -> list[Any]`
- `batch_is_sorted_path(items: Sequence[Any], path: str, reverse: bool=False) -> bool`
- `batch_lower_bound_path(items: Sequence[Any], path: str, target: Any, reverse: bool=False) -> int`
- `batch_equal_range_path(items: Sequence[Any], path: str, target: Any, reverse: bool=False) -> tuple[int, int]`
- `batch_binary_search_path(items: Sequence[Any], path: str, target: Any, reverse: bool=False) -> int`
- `batch_nth_path(items: Sequence[Any], path: str, n: int, largest: bool=False) -> Any`
- `batch_mutate(items: Sequence[Any], operations: Sequence[Sequence[Any]]) -> int`
