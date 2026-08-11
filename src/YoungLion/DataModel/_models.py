from __future__ import annotations

import csv
import io
import math
import random
import statistics
from typing import Any, Callable, Dict, Iterable, Iterator, List, Mapping, Optional, Sequence

from .. import _native
from ._core import DDM

class Range(DDM):
    __slots__ = ()
    def __init__(self, min_val: float = 0.0, max_val: float = 1.0, step: float = 1.0):
        if max_val < min_val:
            raise ValueError("max_val must be >= min_val")
        if step == 0:
            raise ValueError("step cannot be zero")
        super().__init__({"min_val": min_val, "max_val": max_val, "step": step})

    def contains(self, value: float) -> bool:
        return self.min_val <= value <= self.max_val

    def clamp(self, value: float) -> float:
        return max(self.min_val, min(self.max_val, value))

    def span(self) -> float:
        return self.max_val - self.min_val

    def midpoint(self) -> float:
        return (self.min_val + self.max_val) / 2

    def normalize(self, value: float) -> float:
        span = self.span()
        return 0.0 if span == 0 else (value - self.min_val) / span

    def denormalize(self, value: float) -> float:
        return self.min_val + value * self.span()

    def random(self) -> float:
        return random.uniform(self.min_val, self.max_val)

    def iterate(self) -> Iterator[float]:
        value = self.min_val
        if self.step > 0:
            while value <= self.max_val + 1e-12:
                yield value
                value += self.step
        else:
            while value >= self.max_val - 1e-12:
                yield value
                value += self.step

    def subdivide(self, parts: int) -> List["Range"]:
        if parts <= 0:
            raise ValueError("parts must be positive")
        width = self.span() / parts
        return [Range(self.min_val + i * width, self.min_val + (i + 1) * width, width) for i in range(parts)]

    def intersect(self, other: "Range") -> Optional["Range"]:
        lo, hi = max(self.min_val, other.min_val), min(self.max_val, other.max_val)
        return None if lo > hi else Range(lo, hi, min(abs(self.step), abs(other.step)))

    def overlaps(self, other: "Range") -> bool:
        return self.intersect(other) is not None


class Vector(DDM):
    __slots__ = ()
    def __init__(self, components: Sequence[float]):
        values = [float(x) for x in components]
        if not values:
            raise ValueError("components cannot be empty")
        super().__init__({"components": values})

    def magnitude(self) -> float:
        return float(_native.vec_magnitude(self.components))

    def normalize(self) -> "Vector":
        mag = self.magnitude()
        return Vector(self.components if mag == 0 else _native.vec_scale(self.components, 1.0 / mag))

    def dot(self, other: "Vector") -> float:
        return float(_native.vec_dot(self.components, other.components))

    def cross(self, other: "Vector") -> "Vector":
        return Vector(_native.vec_cross(self.components, other.components))

    def distance_to(self, other: "Vector") -> float:
        return Vector(_native.vec_sub(self.components, other.components)).magnitude()

    def angle_to(self, other: "Vector") -> float:
        denom = self.magnitude() * other.magnitude()
        if denom == 0:
            raise ValueError("angle is undefined for a zero vector")
        c = max(-1.0, min(1.0, self.dot(other) / denom))
        return math.degrees(math.acos(c))

    def add(self, other: "Vector") -> "Vector":
        return Vector(_native.vec_add(self.components, other.components))

    def subtract(self, other: "Vector") -> "Vector":
        return Vector(_native.vec_sub(self.components, other.components))

    def scale(self, scalar: float) -> "Vector":
        return Vector(_native.vec_scale(self.components, float(scalar)))

    def project_onto(self, other: "Vector") -> "Vector":
        denom = other.dot(other)
        if denom == 0:
            raise ValueError("cannot project onto zero vector")
        return other.scale(self.dot(other) / denom)

    def perpendicular(self) -> "Vector":
        if len(self.components) != 2:
            raise ValueError("perpendicular() requires a 2D vector")
        x, y = self.components
        return Vector([-y, x])

    def lerp(self, other: "Vector", t: float) -> "Vector":
        return self.add(other.subtract(self).scale(float(t)))

    def __add__(self, other: "Vector") -> "Vector":
        return self.add(other)

    def __sub__(self, other: "Vector") -> "Vector":
        return self.subtract(other)

    def __mul__(self, scalar: float) -> "Vector":
        return self.scale(scalar)

    __rmul__ = __mul__

    def __truediv__(self, scalar: float) -> "Vector":
        if scalar == 0:
            raise ZeroDivisionError
        return self.scale(1 / scalar)


class Timeline(DDM):
    __slots__ = ()
    def __init__(self, start_time: float = 0.0, end_time: float = 1.0, events: Optional[List[Dict[str, Any]]] = None):
        if end_time < start_time:
            raise ValueError("end_time must be >= start_time")
        super().__init__({"start_time": start_time, "end_time": end_time, "events": list(events or [])})

    def add_event(self, time: float, name: str, data: Any = None) -> Dict[str, Any]:
        event = {"time": time, "name": name, "data": data}
        self.events.append(event)
        return event

    def remove_event(self, name: str) -> bool:
        for i, event in enumerate(self.events):
            if event.get("name") == name:
                del self.events[i]
                return True
        return False

    def get_event(self, name: str) -> Optional[Dict[str, Any]]:
        return next((e for e in self.events if e.get("name") == name), None)

    def events_at(self, time: float) -> List[Dict[str, Any]]:
        return [e for e in self.events if e.get("time") == time]

    def events_between(self, start: float, end: float) -> List[Dict[str, Any]]:
        return [e for e in self.events if start <= e.get("time", 0) <= end]

    def duration(self) -> float:
        return self.end_time - self.start_time

    def get_progress(self, time: float) -> float:
        d = self.duration()
        return 1.0 if d == 0 and time >= self.end_time else (0.0 if d == 0 else max(0.0, min(1.0, (time - self.start_time) / d)))

    def sort(self, reverse: bool = False) -> "Timeline":
        self.events.sort(key=lambda e: e.get("time", 0), reverse=reverse)
        return self

    def reverse(self) -> "Timeline":
        self.events.reverse()
        return self


class Dataset(DDM):
    __slots__ = ()
    def __init__(self, columns: Optional[Sequence[str]] = None, rows: Optional[Sequence[Mapping[str, Any]]] = None):
        cols = list(columns or [])
        data_rows = [dict(row) for row in (rows or [])]
        if not cols and data_rows:
            cols = list(data_rows[0].keys())
        super().__init__({"columns": cols, "rows": data_rows})

    def add_row(self, row: Mapping[str, Any]) -> "Dataset":
        row = dict(row)
        for key in row:
            if key not in self.columns:
                self.columns.append(key)
        self.rows.append(row)
        return self

    def add_column(self, name: str, default: Any = None) -> "Dataset":
        if name not in self.columns:
            self.columns.append(name)
        for row in self.rows:
            row.setdefault(name, default)
        return self

    def remove_column(self, name: str) -> "Dataset":
        if name in self.columns:
            self.columns.remove(name)
        for row in self.rows:
            row.pop(name, None)
        return self

    def filter_rows(self, predicate: Callable[[Dict[str, Any]], bool]) -> "Dataset":
        return Dataset(self.columns, [row for row in self.rows if predicate(row)])

    def map_column(self, name: str, func: Callable[[Any], Any]) -> "Dataset":
        for row in self.rows:
            if name in row:
                row[name] = func(row[name])
        return self

    def sort_by(self, column: str, reverse: bool = False) -> "Dataset":
        return Dataset(self.columns, sorted(self.rows, key=lambda row: row.get(column), reverse=reverse))

    def group_by(self, column: str) -> Dict[Any, "Dataset"]:
        groups: Dict[Any, List[Dict[str, Any]]] = {}
        for row in self.rows:
            groups.setdefault(row.get(column), []).append(row)
        return {k: Dataset(self.columns, v) for k, v in groups.items()}

    def aggregate(self, column: str, func: Callable[[Iterable[Any]], Any]) -> Any:
        return func(row.get(column) for row in self.rows if column in row)

    def stats(self, column: str) -> Dict[str, float]:
        vals = [float(row[column]) for row in self.rows if column in row and isinstance(row[column], (int, float))]
        if not vals:
            return {"count": 0, "sum": 0.0, "mean": 0.0, "min": 0.0, "max": 0.0, "std": 0.0}
        return {
            "count": len(vals), "sum": sum(vals), "mean": statistics.fmean(vals),
            "min": min(vals), "max": max(vals), "std": statistics.pstdev(vals),
        }

    def to_csv(self) -> str:
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=self.columns)
        writer.writeheader()
        writer.writerows(self.rows)
        return out.getvalue()

    def transpose(self) -> List[List[Any]]:
        return [[row.get(column) for row in self.rows] for column in self.columns]



class Size(DDM):
    __slots__ = ()
    def __init__(self, width: float = 0.0, height: float = 0.0):
        if width < 0 or height < 0: raise ValueError("width and height must be non-negative")
        super().__init__({"width": float(width), "height": float(height)})
    @property
    def area(self) -> float: return self.width * self.height
    @property
    def perimeter(self) -> float: return 2.0 * (self.width + self.height)
    @property
    def aspect_ratio(self) -> float: return math.inf if self.height == 0 else self.width / self.height
    def scale(self, factor: float) -> "Size": return Size(self.width * factor, self.height * factor)
    def fit_inside(self, other: "Size", *, upscale: bool = False) -> "Size":
        if self.width == 0 or self.height == 0: return Size(0, 0)
        factor = min(other.width / self.width, other.height / self.height)
        if not upscale: factor = min(1.0, factor)
        return self.scale(factor)
    def contains(self, other: "Size") -> bool: return self.width >= other.width and self.height >= other.height


class Point(DDM):
    __slots__ = ()
    def __init__(self, x: float = 0.0, y: float = 0.0): super().__init__({"x": float(x), "y": float(y)})
    def distance_to(self, other: "Point") -> float: return math.hypot(self.x - other.x, self.y - other.y)
    def midpoint(self, other: "Point") -> "Point": return Point((self.x + other.x) / 2.0, (self.y + other.y) / 2.0)
    def translate(self, dx: float = 0.0, dy: float = 0.0) -> "Point": return Point(self.x + dx, self.y + dy)
    def scale(self, factor: float, origin: Optional["Point"] = None) -> "Point":
        origin = origin or Point()
        return Point(origin.x + (self.x - origin.x) * factor, origin.y + (self.y - origin.y) * factor)
    def to_vector(self) -> Vector: return Vector([self.x, self.y])


class Color(DDM):
    __slots__ = ()
    def __init__(self, r: int = 0, g: int = 0, b: int = 0, a: int = 255):
        vals = [int(r), int(g), int(b), int(a)]
        if any(v < 0 or v > 255 for v in vals): raise ValueError("RGBA components must be between 0 and 255")
        super().__init__({"r": vals[0], "g": vals[1], "b": vals[2], "a": vals[3]})
    @classmethod
    def from_hex(cls, value: str) -> "Color":
        text = value.strip().lstrip("#")
        if len(text) not in {6, 8}: raise ValueError("hex color must be RRGGBB or RRGGBBAA")
        values = [int(text[i:i+2], 16) for i in range(0, len(text), 2)]
        return cls(*values) if len(values) == 4 else cls(*values, 255)
    def to_hex(self, include_alpha: bool = False) -> str:
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}" + (f"{self.a:02X}" if include_alpha else "")
    def normalized(self) -> tuple[float, float, float, float]: return tuple(v / 255.0 for v in (self.r, self.g, self.b, self.a))
    def blend(self, other: "Color", t: float = 0.5) -> "Color":
        t = max(0.0, min(1.0, float(t)))
        vals = [round(a + (b-a)*t) for a, b in zip((self.r,self.g,self.b,self.a), (other.r,other.g,other.b,other.a))]
        return Color(*vals)
    def luminance(self) -> float:
        channels = []
        for c in (self.r, self.g, self.b):
            x = c / 255.0; channels.append(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4)
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]
    def contrast_ratio(self, other: "Color") -> float:
        a, b = self.luminance(), other.luminance(); hi, lo = max(a,b), min(a,b); return (hi + 0.05) / (lo + 0.05)


class Matrix(DDM):
    """Small/medium dependency-free numeric matrix utility."""
    __slots__ = ()
    def __init__(self, rows: Sequence[Sequence[float]]):
        values = [[float(v) for v in row] for row in rows]
        if not values or not values[0]: raise ValueError("matrix cannot be empty")
        width = len(values[0])
        if any(len(row) != width for row in values): raise ValueError("matrix rows must have equal length")
        super().__init__({"rows": values})
    @property
    def shape(self) -> tuple[int, int]: return len(self.rows), len(self.rows[0])
    @classmethod
    def identity(cls, size: int) -> "Matrix":
        if size <= 0: raise ValueError("size must be positive")
        return cls([[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)])
    def transpose(self) -> "Matrix": return Matrix(list(map(list, zip(*self.rows))))
    T = property(transpose)
    def add(self, other: "Matrix") -> "Matrix":
        if self.shape != other.shape: raise ValueError("matrix shapes differ")
        return Matrix([[a+b for a,b in zip(ra,rb)] for ra,rb in zip(self.rows,other.rows)])
    def subtract(self, other: "Matrix") -> "Matrix":
        if self.shape != other.shape: raise ValueError("matrix shapes differ")
        return Matrix([[a-b for a,b in zip(ra,rb)] for ra,rb in zip(self.rows,other.rows)])
    def scale(self, scalar: float) -> "Matrix": return Matrix([[v*scalar for v in row] for row in self.rows])
    def matmul(self, other: "Matrix") -> "Matrix":
        r1,c1=self.shape; r2,c2=other.shape
        if c1 != r2: raise ValueError("incompatible matrix shapes")
        bt = other.transpose().rows
        return Matrix([[sum(a*b for a,b in zip(row,col)) for col in bt] for row in self.rows])
    def vector_mul(self, vector: Vector) -> Vector:
        if self.shape[1] != len(vector.components): raise ValueError("incompatible dimensions")
        return Vector([sum(a*b for a,b in zip(row,vector.components)) for row in self.rows])
    def __add__(self, other: "Matrix") -> "Matrix": return self.add(other)
    def __sub__(self, other: "Matrix") -> "Matrix": return self.subtract(other)
    def __matmul__(self, other: "Matrix") -> "Matrix": return self.matmul(other)
    def __mul__(self, scalar: float) -> "Matrix": return self.scale(scalar)
    __rmul__ = __mul__


class TreeDDM(DDM):
    """Hierarchical DDM node with iterative traversal helpers."""
    __slots__ = ()
    def __init__(self, value: Any = None, children: Optional[Iterable["TreeDDM"]] = None, **data: Any):
        super().__init__({"value": value, "children": list(children or []), **data})
    def add_child(self, child: Any, **data: Any) -> "TreeDDM":
        node = child if isinstance(child, TreeDDM) else TreeDDM(child, **data); self.children.append(node); return node
    def walk(self, order: str = "dfs") -> Iterator["TreeDDM"]:
        if order == "bfs":
            queue = [self]
            while queue:
                node = queue.pop(0); yield node; queue.extend(node.children)
        elif order == "dfs":
            stack = [self]
            while stack:
                node = stack.pop(); yield node; stack.extend(reversed(node.children))
        else: raise ValueError("order must be 'dfs' or 'bfs'")
    def find(self, predicate: Callable[["TreeDDM"], bool]) -> Optional["TreeDDM"]:
        return next((node for node in self.walk() if predicate(node)), None)
    def depth(self) -> int:
        return 1 + max((child.depth() for child in self.children), default=-1)
    def size(self) -> int: return sum(1 for _ in self.walk())
