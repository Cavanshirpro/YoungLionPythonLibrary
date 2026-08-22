"""Reusable DDM-based mathematical, geometric, temporal and tabular models.

The module contains compact structures that are useful across applications
without requiring NumPy, pandas or geometry packages: Range, Vector, Timeline,
Dataset, Size, Point, Color, Matrix and TreeDDM.  They retain DDM serialization
and inspection behavior while adding domain-specific operations.

These classes favor predictable, dependency-free behavior over exhaustive
scientific-computing functionality.  They are suitable for configuration,
application state, game logic, lightweight analytics and transport objects; use
specialized numerical libraries when very large matrix/dataframe workloads are
the primary requirement.
"""
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
    """Bounded numeric interval model.
    
    Overview
    --------
    ``Range`` provides containment, clamp, normalization, subdivision, intersection and iteration.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for progress scales, game/stat bounds, coordinate intervals and normalization.
    
    Inheritance
    -----------
    Base class(es): ``DDM``.
    
    Primary public operations
    -------------------------
    contains, clamp, span, midpoint, normalize, denormalize, random, iterate, subdivide, intersect, overlaps.
    """
    __slots__ = ()
    def __init__(self, min_val: float = 0.0, max_val: float = 1.0, step: float = 1.0):
        """Initialize a new Range instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`Range` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        min_val : float (default: ``0.0``)
            Lower numeric bound of the range.
        max_val : float (default: ``1.0``)
            Upper numeric bound of the range.
        step : float (default: ``1.0``)
            Iteration step used by Range.
        """
        if max_val < min_val:
            raise ValueError("max_val must be >= min_val")
        if step == 0:
            raise ValueError("step cannot be zero")
        super().__init__({"min_val": min_val, "max_val": max_val, "step": step})

    def contains(self, value: float) -> bool:
        """Return whether a value/substring lies within the represented range or indexed path data.
        
        Details
        -------
        This method belongs to :class:`Range` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        value : float
            Target, new or comparison value.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        """
        return self.min_val <= value <= self.max_val

    def clamp(self, value: float) -> float:
        """Constrain a value or all addressed numeric values to the supplied inclusive bounds.
        
        Details
        -------
        This method belongs to :class:`Range` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        value : float
            Target, new or comparison value.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        return max(self.min_val, min(self.max_val, value))

    def span(self) -> float:
        """Return the numeric width of the range.
        
        Details
        -------
        This method belongs to :class:`Range` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        return self.max_val - self.min_val

    def midpoint(self) -> float:
        """Return the midpoint of this object relative to its range/geometry semantics.
        
        Details
        -------
        This method belongs to :class:`Range` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        return (self.min_val + self.max_val) / 2

    def normalize(self, value: float) -> float:
        """Convert a raw value into normalized range/vector form.
        
        Details
        -------
        This method belongs to :class:`Range` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        value : float
            Target, new or comparison value.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        span = self.span()
        return 0.0 if span == 0 else (value - self.min_val) / span

    def denormalize(self, value: float) -> float:
        """Convert a normalized scalar back into the range's coordinate space.
        
        Details
        -------
        This method belongs to :class:`Range` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        value : float
            Target, new or comparison value.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        return self.min_val + value * self.span()

    def random(self) -> float:
        """Return a random value drawn from the represented range.
        
        Details
        -------
        This method belongs to :class:`Range` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        return random.uniform(self.min_val, self.max_val)

    def iterate(self) -> Iterator[float]:
        """Iterate values from the lower bound toward the upper bound using the configured step.
        
        Details
        -------
        This method belongs to :class:`Range` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``Iterator[float]`` result described by the method semantics.
        """
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
        """Split the range into the requested number of contiguous subranges.
        
        Details
        -------
        This method belongs to :class:`Range` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        parts : int
            Number of subranges requested.
        
        Returns
        -------
        ``List['Range']`` result described by the method semantics.
        """
        if parts <= 0:
            raise ValueError("parts must be positive")
        width = self.span() / parts
        return [Range(self.min_val + i * width, self.min_val + (i + 1) * width, width) for i in range(parts)]

    def intersect(self, other: "Range") -> Optional["Range"]:
        """Return the overlapping portion of two ranges when one exists.
        
        Details
        -------
        This method belongs to :class:`Range` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : 'Range'
            Another compatible object/value used by the operation.
        
        Returns
        -------
        ``Optional['Range']`` result described by the method semantics.
        """
        lo, hi = max(self.min_val, other.min_val), min(self.max_val, other.max_val)
        return None if lo > hi else Range(lo, hi, min(abs(self.step), abs(other.step)))

    def overlaps(self, other: "Range") -> bool:
        """Return whether this range overlaps another range.
        
        Details
        -------
        This method belongs to :class:`Range` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : 'Range'
            Another compatible object/value used by the operation.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        """
        return self.intersect(other) is not None


class Vector(DDM):
    """N-dimensional vector model.
    
    Overview
    --------
    ``Vector`` provides magnitude, normalization, dot/cross products, projection, interpolation and arithmetic.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for dependency-free geometry/game/application calculations.
    
    Inheritance
    -----------
    Base class(es): ``DDM``.
    
    Primary public operations
    -------------------------
    magnitude, normalize, dot, cross, distance_to, angle_to, add, subtract, scale, project_onto, perpendicular, lerp.
    """
    __slots__ = ()
    def __init__(self, components: Sequence[float]):
        """Initialize a new Vector instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`Vector` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        components : Sequence[float]
            Numeric components used to initialize the vector.
        """
        values = [float(x) for x in components]
        if not values:
            raise ValueError("components cannot be empty")
        super().__init__({"components": values})

    def magnitude(self) -> float:
        """Return the Euclidean magnitude of the vector.
        
        Details
        -------
        This method belongs to :class:`Vector` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        return float(_native.vec_magnitude(self.components))

    def normalize(self) -> "Vector":
        """Convert a raw value into normalized range/vector form.
        
        Details
        -------
        This method belongs to :class:`Vector` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``'Vector'`` result described by the method semantics.
        """
        mag = self.magnitude()
        return Vector(self.components if mag == 0 else _native.vec_scale(self.components, 1.0 / mag))

    def dot(self, other: "Vector") -> float:
        """Return the dot product with another vector.
        
        Details
        -------
        This method belongs to :class:`Vector` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : 'Vector'
            Another compatible object/value used by the operation.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        return float(_native.vec_dot(self.components, other.components))

    def cross(self, other: "Vector") -> "Vector":
        """Return the cross product for supported vector dimensions.
        
        Details
        -------
        This method belongs to :class:`Vector` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : 'Vector'
            Another compatible object/value used by the operation.
        
        Returns
        -------
        ``'Vector'`` result described by the method semantics.
        """
        return Vector(_native.vec_cross(self.components, other.components))

    def distance_to(self, other: "Vector") -> float:
        """Return Euclidean distance to another compatible point/vector.
        
        Details
        -------
        This method belongs to :class:`Vector` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : 'Vector'
            Another compatible object/value used by the operation.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        return Vector(_native.vec_sub(self.components, other.components)).magnitude()

    def angle_to(self, other: "Vector") -> float:
        """Return the angle between this vector and another vector.
        
        Details
        -------
        This method belongs to :class:`Vector` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : 'Vector'
            Another compatible object/value used by the operation.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        denom = self.magnitude() * other.magnitude()
        if denom == 0:
            raise ValueError("angle is undefined for a zero vector")
        c = max(-1.0, min(1.0, self.dot(other) / denom))
        return math.degrees(math.acos(c))

    def add(self, other: "Vector") -> "Vector":
        """Add a value/record/operation to the current object according to its collection or numeric semantics.
        
        Details
        -------
        This method belongs to :class:`Vector` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : 'Vector'
            Another compatible object/value used by the operation.
        
        Returns
        -------
        ``'Vector'`` result described by the method semantics.
        """
        return Vector(_native.vec_add(self.components, other.components))

    def subtract(self, other: "Vector") -> "Vector":
        """Subtract another value or queue a subtraction operation.
        
        Details
        -------
        This method belongs to :class:`Vector` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : 'Vector'
            Another compatible object/value used by the operation.
        
        Returns
        -------
        ``'Vector'`` result described by the method semantics.
        """
        return Vector(_native.vec_sub(self.components, other.components))

    def scale(self, scalar: float) -> "Vector":
        """Return a scaled version of the represented numeric/geometry object.
        
        Details
        -------
        This method belongs to :class:`Vector` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        scalar : float
            Numeric scalar multiplier.
        
        Returns
        -------
        ``'Vector'`` result described by the method semantics.
        """
        return Vector(_native.vec_scale(self.components, float(scalar)))

    def project_onto(self, other: "Vector") -> "Vector":
        """Project this vector onto another vector.
        
        Details
        -------
        This method belongs to :class:`Vector` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : 'Vector'
            Another compatible object/value used by the operation.
        
        Returns
        -------
        ``'Vector'`` result described by the method semantics.
        """
        denom = other.dot(other)
        if denom == 0:
            raise ValueError("cannot project onto zero vector")
        return other.scale(self.dot(other) / denom)

    def perpendicular(self) -> "Vector":
        """Return a perpendicular vector where the operation is defined.
        
        Details
        -------
        This method belongs to :class:`Vector` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``'Vector'`` result described by the method semantics.
        """
        if len(self.components) != 2:
            raise ValueError("perpendicular() requires a 2D vector")
        x, y = self.components
        return Vector([-y, x])

    def lerp(self, other: "Vector", t: float) -> "Vector":
        """Linearly interpolate between this value and another compatible value.
        
        Details
        -------
        This method belongs to :class:`Vector` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : 'Vector'
            Another compatible object/value used by the operation.
        t : float
            Interpolation parameter, normally between 0 and 1.
        
        Returns
        -------
        ``'Vector'`` result described by the method semantics.
        """
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
    """Event timeline model.
    
    Overview
    --------
    ``Timeline`` provides bounded time range plus named event management, filtering and progress calculation.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for schedules, animation/event progress and milestone collections.
    
    Inheritance
    -----------
    Base class(es): ``DDM``.
    
    Primary public operations
    -------------------------
    add_event, remove_event, get_event, events_at, events_between, duration, get_progress, sort, reverse.
    """
    __slots__ = ()
    def __init__(self, start_time: float = 0.0, end_time: float = 1.0, events: Optional[List[Dict[str, Any]]] = None):
        """Initialize a new Timeline instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`Timeline` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        start_time : float (default: ``0.0``)
            Lower/start position of the timeline.
        end_time : float (default: ``1.0``)
            Upper/end position of the timeline.
        events : Optional[List[Dict[str, Any]]] (default: ``None``)
            Optional initial event records.
        """
        if end_time < start_time:
            raise ValueError("end_time must be >= start_time")
        super().__init__({"start_time": start_time, "end_time": end_time, "events": list(events or [])})

    def add_event(self, time: float, name: str, data: Any = None) -> Dict[str, Any]:
        """Add a named event at a timeline position.
        
        Details
        -------
        This method belongs to :class:`Timeline` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        time : float
            Timeline position for the operation.
        name : str
            Name/label used by the object or event.
        data : Any (default: ``None``)
            Input mapping or record data used to initialize the object.
        
        Returns
        -------
        ``Dict[str, Any]`` result described by the method semantics.
        """
        event = {"time": time, "name": name, "data": data}
        self.events.append(event)
        return event

    def remove_event(self, name: str) -> bool:
        """Remove timeline events matching the supplied name.
        
        Details
        -------
        This method belongs to :class:`Timeline` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        name : str
            Name/label used by the object or event.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        """
        for i, event in enumerate(self.events):
            if event.get("name") == name:
                del self.events[i]
                return True
        return False

    def get_event(self, name: str) -> Optional[Dict[str, Any]]:
        """Return the first timeline event matching the supplied name.
        
        Details
        -------
        This method belongs to :class:`Timeline` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        name : str
            Name/label used by the object or event.
        
        Returns
        -------
        ``Optional[Dict[str, Any]]`` result described by the method semantics.
        """
        return next((e for e in self.events if e.get("name") == name), None)

    def events_at(self, time: float) -> List[Dict[str, Any]]:
        """Return events occurring at the requested timeline position.
        
        Details
        -------
        This method belongs to :class:`Timeline` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        time : float
            Timeline position for the operation.
        
        Returns
        -------
        ``List[Dict[str, Any]]`` result described by the method semantics.
        """
        return [e for e in self.events if e.get("time") == time]

    def events_between(self, start: float, end: float) -> List[Dict[str, Any]]:
        """Return events whose times lie within the requested interval.
        
        Details
        -------
        This method belongs to :class:`Timeline` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        start : float
            Whether the stopwatch starts immediately or remains stopped initially.
        end : float
            Value supplied for ``end`` according to the Timeline contract.
        
        Returns
        -------
        ``List[Dict[str, Any]]`` result described by the method semantics.
        """
        return [e for e in self.events if start <= e.get("time", 0) <= end]

    def duration(self) -> float:
        """Return the timeline's total span.
        
        Details
        -------
        This method belongs to :class:`Timeline` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        return self.end_time - self.start_time

    def get_progress(self, time: float) -> float:
        """Return the last known integer percentage for a transfer ID.
        
        Details
        -------
        This method belongs to :class:`Timeline` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        time : float
            Timeline position for the operation.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        d = self.duration()
        return 1.0 if d == 0 and time >= self.end_time else (0.0 if d == 0 else max(0.0, min(1.0, (time - self.start_time) / d)))

    def sort(self, reverse: bool = False) -> "Timeline":
        """Perform the ``sort`` operation for Timeline.
        
        Details
        -------
        This method belongs to :class:`Timeline` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.
        
        Returns
        -------
        ``'Timeline'`` result described by the method semantics.
        """
        self.events.sort(key=lambda e: e.get("time", 0), reverse=reverse)
        return self

    def reverse(self) -> "Timeline":
        """Reverse record/event order, optionally mutating according to the class contract.
        
        Details
        -------
        This method belongs to :class:`Timeline` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``'Timeline'`` result described by the method semantics.
        """
        self.events.reverse()
        return self


class Dataset(DDM):
    """Lightweight tabular dataset.
    
    Overview
    --------
    ``Dataset`` provides rows/columns, filtering, mapping, grouping, aggregation, statistics and CSV export.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for modest in-memory analytics when a dataframe dependency would be excessive.
    
    Inheritance
    -----------
    Base class(es): ``DDM``.
    
    Primary public operations
    -------------------------
    add_row, add_column, remove_column, filter_rows, map_column, sort_by, group_by, aggregate, stats, to_csv, transpose.
    """
    __slots__ = ()
    def __init__(self, columns: Optional[Sequence[str]] = None, rows: Optional[Sequence[Mapping[str, Any]]] = None):
        """Initialize a new Dataset instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`Dataset` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        columns : Optional[Sequence[str]] (default: ``None``)
            Dataset column names.
        rows : Optional[Sequence[Mapping[str, Any]]] (default: ``None``)
            Dataset/matrix row data.
        """
        cols = list(columns or [])
        data_rows = [dict(row) for row in (rows or [])]
        if not cols and data_rows:
            cols = list(data_rows[0].keys())
        super().__init__({"columns": cols, "rows": data_rows})

    def add_row(self, row: Mapping[str, Any]) -> "Dataset":
        """Append a row to the dataset after applying dataset shape rules.
        
        Details
        -------
        This method belongs to :class:`Dataset` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        row : Mapping[str, Any]
            One dataset record to append.
        
        Returns
        -------
        ``'Dataset'`` result described by the method semantics.
        """
        row = dict(row)
        for key in row:
            if key not in self.columns:
                self.columns.append(key)
        self.rows.append(row)
        return self

    def add_column(self, name: str, default: Any = None) -> "Dataset":
        """Add a column to the dataset and populate existing rows with a default value.
        
        Details
        -------
        This method belongs to :class:`Dataset` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        name : str
            Name/label used by the object or event.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.
        
        Returns
        -------
        ``'Dataset'`` result described by the method semantics.
        """
        if name not in self.columns:
            self.columns.append(name)
        for row in self.rows:
            row.setdefault(name, default)
        return self

    def remove_column(self, name: str) -> "Dataset":
        """Remove a named dataset column from schema and rows.
        
        Details
        -------
        This method belongs to :class:`Dataset` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        name : str
            Name/label used by the object or event.
        
        Returns
        -------
        ``'Dataset'`` result described by the method semantics.
        """
        if name in self.columns:
            self.columns.remove(name)
        for row in self.rows:
            row.pop(name, None)
        return self

    def filter_rows(self, predicate: Callable[[Dict[str, Any]], bool]) -> "Dataset":
        """Return a dataset containing only rows accepted by the predicate.
        
        Details
        -------
        This method belongs to :class:`Dataset` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        predicate : Callable[[Dict[str, Any]], bool]
            Callable returning truthy for records that should match/be selected.
        
        Returns
        -------
        ``'Dataset'`` result described by the method semantics.
        """
        return Dataset(self.columns, [row for row in self.rows if predicate(row)])

    def map_column(self, name: str, func: Callable[[Any], Any]) -> "Dataset":
        """Transform one dataset column using a callable.
        
        Details
        -------
        This method belongs to :class:`Dataset` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        name : str
            Name/label used by the object or event.
        func : Callable[[Any], Any]
            Callable applied by the operation.
        
        Returns
        -------
        ``'Dataset'`` result described by the method semantics.
        """
        for row in self.rows:
            if name in row:
                row[name] = func(row[name])
        return self

    def sort_by(self, column: str, reverse: bool = False) -> "Dataset":
        """Sort records by a column/dotted path with explicit missing-value and in-place behavior.
        
        Details
        -------
        This method belongs to :class:`Dataset` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        column : str
            Dataset column selected for aggregation/statistics.
        reverse : bool (default: ``False``)
            When True, reverse the natural ordering.
        
        Returns
        -------
        ``'Dataset'`` result described by the method semantics.
        """
        return Dataset(self.columns, sorted(self.rows, key=lambda row: row.get(column), reverse=reverse))

    def group_by(self, column: str) -> Dict[Any, "Dataset"]:
        """Group records or values by the requested field/callback and return the resulting buckets.
        
        Details
        -------
        This method belongs to :class:`Dataset` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        column : str
            Dataset column selected for aggregation/statistics.
        
        Returns
        -------
        ``Dict[Any, 'Dataset']`` result described by the method semantics.
        """
        groups: Dict[Any, List[Dict[str, Any]]] = {}
        for row in self.rows:
            groups.setdefault(row.get(column), []).append(row)
        return {k: Dataset(self.columns, v) for k, v in groups.items()}

    def aggregate(self, column: str, func: Callable[[Iterable[Any]], Any]) -> Any:
        """Apply one or more aggregation callables to the selected data.
        
        Details
        -------
        This method belongs to :class:`Dataset` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        column : str
            Dataset column selected for aggregation/statistics.
        func : Callable[[Iterable[Any]], Any]
            Callable applied by the operation.
        
        Returns
        -------
        ``Any`` result described by the method semantics.
        """
        return func(row.get(column) for row in self.rows if column in row)

    def stats(self, column: str) -> Dict[str, float]:
        """Return diagnostic counts describing the current cache/index/processor state.
        
        Details
        -------
        This method belongs to :class:`Dataset` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        column : str
            Dataset column selected for aggregation/statistics.
        
        Returns
        -------
        Dictionary/dataclass containing diagnostic statistics for the current object.
        """
        vals = [float(row[column]) for row in self.rows if column in row and isinstance(row[column], (int, float))]
        if not vals:
            return {"count": 0, "sum": 0.0, "mean": 0.0, "min": 0.0, "max": 0.0, "std": 0.0}
        return {
            "count": len(vals), "sum": sum(vals), "mean": statistics.fmean(vals),
            "min": min(vals), "max": max(vals), "std": statistics.pstdev(vals),
        }

    def to_csv(self) -> str:
        """Serialize the represented data to CSV text.
        
        Details
        -------
        This method belongs to :class:`Dataset` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=self.columns)
        writer.writeheader()
        writer.writerows(self.rows)
        return out.getvalue()

    def transpose(self) -> List[List[Any]]:
        """Swap dataset/matrix row and column orientation.
        
        Details
        -------
        This method belongs to :class:`Dataset` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``List[List[Any]]`` result described by the method semantics.
        """
        return [[row.get(column) for row in self.rows] for column in self.columns]



class Size(DDM):
    """2D dimension model.
    
    Overview
    --------
    ``Size`` provides area, perimeter, aspect ratio, scaling and fit calculations.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for UI/media/layout dimensions and simple geometry.
    
    Inheritance
    -----------
    Base class(es): ``DDM``.
    
    Primary public operations
    -------------------------
    area, perimeter, aspect_ratio, scale, fit_inside, contains.
    """
    __slots__ = ()
    def __init__(self, width: float = 0.0, height: float = 0.0):
        """Initialize a new Size instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`Size` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        width : float (default: ``0.0``)
            Width in characters/pixels/units according to the API.
        height : float (default: ``0.0``)
            Height in pixels/units.
        """
        if width < 0 or height < 0: raise ValueError("width and height must be non-negative")
        super().__init__({"width": float(width), "height": float(height)})
    @property
    def area(self) -> float:
        """Return two-dimensional area.
        
        Details
        -------
        This method belongs to :class:`Size` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        return self.width * self.height
    @property
    def perimeter(self) -> float:
        """Return the perimeter of the 2D size.
        
        Details
        -------
        This method belongs to :class:`Size` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        return 2.0 * (self.width + self.height)
    @property
    def aspect_ratio(self) -> float:
        """Return width divided by height using the class's zero-height behavior.
        
        Details
        -------
        This method belongs to :class:`Size` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        return math.inf if self.height == 0 else self.width / self.height
    def scale(self, factor: float) -> "Size":
        """Return a scaled version of the represented numeric/geometry object.
        
        Details
        -------
        This method belongs to :class:`Size` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        factor : float
            Numeric scaling/multiplication factor.
        
        Returns
        -------
        ``'Size'`` result described by the method semantics.
        """
        return Size(self.width * factor, self.height * factor)
    def fit_inside(self, other: "Size", *, upscale: bool = False) -> "Size":
        """Return a size scaled to fit within another size while preserving aspect ratio.
        
        Details
        -------
        This method belongs to :class:`Size` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : 'Size'
            Another compatible object/value used by the operation.
        upscale : bool (default: ``False``)
            Whether fit calculations may enlarge a smaller source size.
        
        Returns
        -------
        ``'Size'`` result described by the method semantics.
        """
        if self.width == 0 or self.height == 0: return Size(0, 0)
        factor = min(other.width / self.width, other.height / self.height)
        if not upscale: factor = min(1.0, factor)
        return self.scale(factor)
    def contains(self, other: "Size") -> bool:
        """Return whether a value/substring lies within the represented range or indexed path data.
        
        Details
        -------
        This method belongs to :class:`Size` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : 'Size'
            Another compatible object/value used by the operation.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        """
        return self.width >= other.width and self.height >= other.height


class Point(DDM):
    """2D coordinate model.
    
    Overview
    --------
    ``Point`` provides distance, midpoint, translation, scaling and vector conversion.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for geometry, canvas/UI and game coordinates.
    
    Inheritance
    -----------
    Base class(es): ``DDM``.
    
    Primary public operations
    -------------------------
    distance_to, midpoint, translate, scale, to_vector.
    """
    __slots__ = ()
    def __init__(self, x: float = 0.0, y: float = 0.0):
        """Initialize a new Point instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`Point` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        x : float (default: ``0.0``)
            X coordinate.
        y : float (default: ``0.0``)
            Y coordinate.
        """
        super().__init__({"x": float(x), "y": float(y)})
    def distance_to(self, other: "Point") -> float:
        """Return Euclidean distance to another compatible point/vector.
        
        Details
        -------
        This method belongs to :class:`Point` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : 'Point'
            Another compatible object/value used by the operation.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        return math.hypot(self.x - other.x, self.y - other.y)
    def midpoint(self, other: "Point") -> "Point":
        """Return the midpoint of this object relative to its range/geometry semantics.
        
        Details
        -------
        This method belongs to :class:`Point` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : 'Point'
            Another compatible object/value used by the operation.
        
        Returns
        -------
        ``'Point'`` result described by the method semantics.
        """
        return Point((self.x + other.x) / 2.0, (self.y + other.y) / 2.0)
    def translate(self, dx: float = 0.0, dy: float = 0.0) -> "Point":
        """Perform the ``translate`` operation for Point.
        
        Details
        -------
        This method belongs to :class:`Point` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        dx : float (default: ``0.0``)
            Horizontal translation.
        dy : float (default: ``0.0``)
            Vertical translation.
        
        Returns
        -------
        ``'Point'`` result described by the method semantics.
        """
        return Point(self.x + dx, self.y + dy)
    def scale(self, factor: float, origin: Optional["Point"] = None) -> "Point":
        """Return a scaled version of the represented numeric/geometry object.
        
        Details
        -------
        This method belongs to :class:`Point` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        factor : float
            Numeric scaling/multiplication factor.
        origin : Optional['Point'] (default: ``None``)
            Origin point used for scaling.
        
        Returns
        -------
        ``'Point'`` result described by the method semantics.
        """
        origin = origin or Point()
        return Point(origin.x + (self.x - origin.x) * factor, origin.y + (self.y - origin.y) * factor)
    def to_vector(self) -> Vector:
        """Perform the ``to_vector`` operation for Point.
        
        Details
        -------
        This method belongs to :class:`Point` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``Vector`` result described by the method semantics.
        """
        return Vector([self.x, self.y])


class Color(DDM):
    """RGBA color model.
    
    Overview
    --------
    ``Color`` provides hex conversion, normalized channels, blending, luminance and contrast ratio.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for theme, UI and accessibility calculations independent of terminal ANSI colors.
    
    Inheritance
    -----------
    Base class(es): ``DDM``.
    
    Primary public operations
    -------------------------
    from_hex, to_hex, normalized, blend, luminance, contrast_ratio.
    """
    __slots__ = ()
    def __init__(self, r: int = 0, g: int = 0, b: int = 0, a: int = 255):
        """Initialize a new Color instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`Color` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        r : int (default: ``0``)
            Red channel 0..255.
        g : int (default: ``0``)
            Green channel 0..255.
        b : int (default: ``0``)
            Second string/value.
        a : int (default: ``255``)
            First string/value.
        """
        vals = [int(r), int(g), int(b), int(a)]
        if any(v < 0 or v > 255 for v in vals): raise ValueError("RGBA components must be between 0 and 255")
        super().__init__({"r": vals[0], "g": vals[1], "b": vals[2], "a": vals[3]})
    @classmethod
    def from_hex(cls, value: str) -> "Color":
        """Construct a color from hexadecimal RGB/RGBA notation.
        
        Details
        -------
        This method belongs to :class:`Color` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        value : str
            Target, new or comparison value.
        
        Returns
        -------
        ``'Color'`` result described by the method semantics.
        """
        text = value.strip().lstrip("#")
        if len(text) not in {6, 8}: raise ValueError("hex color must be RRGGBB or RRGGBBAA")
        values = [int(text[i:i+2], 16) for i in range(0, len(text), 2)]
        return cls(*values) if len(values) == 4 else cls(*values, 255)
    def to_hex(self, include_alpha: bool = False) -> str:
        """Return the color as a hexadecimal string.
        
        Details
        -------
        This method belongs to :class:`Color` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        include_alpha : bool (default: ``False``)
            Whether hexadecimal output includes the alpha channel.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}" + (f"{self.a:02X}" if include_alpha else "")
    def normalized(self) -> tuple[float, float, float, float]:
        """Return RGBA channels normalized to floating-point 0..1 values.
        
        Details
        -------
        This method belongs to :class:`Color` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``tuple[float, float, float, float]`` result described by the method semantics.
        """
        return tuple(v / 255.0 for v in (self.r, self.g, self.b, self.a))
    def blend(self, other: "Color", t: float = 0.5) -> "Color":
        """Interpolate between this color and another color.
        
        Details
        -------
        This method belongs to :class:`Color` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : 'Color'
            Another compatible object/value used by the operation.
        t : float (default: ``0.5``)
            Interpolation parameter, normally between 0 and 1.
        
        Returns
        -------
        ``'Color'`` result described by the method semantics.
        """
        t = max(0.0, min(1.0, float(t)))
        vals = [round(a + (b-a)*t) for a, b in zip((self.r,self.g,self.b,self.a), (other.r,other.g,other.b,other.a))]
        return Color(*vals)
    def luminance(self) -> float:
        """Return relative luminance for accessibility/contrast calculations.
        
        Details
        -------
        This method belongs to :class:`Color` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        channels = []
        for c in (self.r, self.g, self.b):
            x = c / 255.0; channels.append(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4)
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]
    def contrast_ratio(self, other: "Color") -> float:
        """Return the WCAG-style contrast ratio between this color and another color.
        
        Details
        -------
        This method belongs to :class:`Color` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : 'Color'
            Another compatible object/value used by the operation.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        a, b = self.luminance(), other.luminance(); hi, lo = max(a,b), min(a,b); return (hi + 0.05) / (lo + 0.05)


class Matrix(DDM):
    """Dense numeric matrix model.
    
    Overview
    --------
    ``Matrix`` provides shape, identity, transpose, scalar/arithmetic multiplication and vector multiplication.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for lightweight matrix workflows without a numerical dependency.
    
    Inheritance
    -----------
    Base class(es): ``DDM``.
    
    Primary public operations
    -------------------------
    shape, identity, transpose, add, subtract, scale, matmul, vector_mul.
    """
    __slots__ = ()
    def __init__(self, rows: Sequence[Sequence[float]]):
        """Initialize a new Matrix instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`Matrix` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        rows : Sequence[Sequence[float]]
            Dataset/matrix row data.
        """
        values = [[float(v) for v in row] for row in rows]
        if not values or not values[0]: raise ValueError("matrix cannot be empty")
        width = len(values[0])
        if any(len(row) != width for row in values): raise ValueError("matrix rows must have equal length")
        super().__init__({"rows": values})
    @property
    def shape(self) -> tuple[int, int]:
        """Return matrix dimensions as a rows/columns pair.
        
        Details
        -------
        This method belongs to :class:`Matrix` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``tuple[int, int]`` result described by the method semantics.
        """
        return len(self.rows), len(self.rows[0])
    @classmethod
    def identity(cls, size: int) -> "Matrix":
        """Construct an identity matrix of the requested square size.
        
        Details
        -------
        This method belongs to :class:`Matrix` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        size : int
            Requested size/dimension/chunk width.
        
        Returns
        -------
        ``'Matrix'`` result described by the method semantics.
        """
        if size <= 0: raise ValueError("size must be positive")
        return cls([[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)])
    def transpose(self) -> "Matrix":
        """Swap dataset/matrix row and column orientation.
        
        Details
        -------
        This method belongs to :class:`Matrix` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``'Matrix'`` result described by the method semantics.
        """
        return Matrix(list(map(list, zip(*self.rows))))
    T = property(transpose)
    def add(self, other: "Matrix") -> "Matrix":
        """Add a value/record/operation to the current object according to its collection or numeric semantics.
        
        Details
        -------
        This method belongs to :class:`Matrix` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : 'Matrix'
            Another compatible object/value used by the operation.
        
        Returns
        -------
        ``'Matrix'`` result described by the method semantics.
        """
        if self.shape != other.shape: raise ValueError("matrix shapes differ")
        return Matrix([[a+b for a,b in zip(ra,rb)] for ra,rb in zip(self.rows,other.rows)])
    def subtract(self, other: "Matrix") -> "Matrix":
        """Subtract another value or queue a subtraction operation.
        
        Details
        -------
        This method belongs to :class:`Matrix` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : 'Matrix'
            Another compatible object/value used by the operation.
        
        Returns
        -------
        ``'Matrix'`` result described by the method semantics.
        """
        if self.shape != other.shape: raise ValueError("matrix shapes differ")
        return Matrix([[a-b for a,b in zip(ra,rb)] for ra,rb in zip(self.rows,other.rows)])
    def scale(self, scalar: float) -> "Matrix":
        """Return a scaled version of the represented numeric/geometry object.
        
        Details
        -------
        This method belongs to :class:`Matrix` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        scalar : float
            Numeric scalar multiplier.
        
        Returns
        -------
        ``'Matrix'`` result described by the method semantics.
        """
        return Matrix([[v*scalar for v in row] for row in self.rows])
    def matmul(self, other: "Matrix") -> "Matrix":
        """Return matrix multiplication with another compatible matrix.
        
        Details
        -------
        This method belongs to :class:`Matrix` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : 'Matrix'
            Another compatible object/value used by the operation.
        
        Returns
        -------
        ``'Matrix'`` result described by the method semantics.
        """
        r1,c1=self.shape; r2,c2=other.shape
        if c1 != r2: raise ValueError("incompatible matrix shapes")
        bt = other.transpose().rows
        return Matrix([[sum(a*b for a,b in zip(row,col)) for col in bt] for row in self.rows])
    def vector_mul(self, vector: Vector) -> Vector:
        """Multiply the matrix by a compatible vector.
        
        Details
        -------
        This method belongs to :class:`Matrix` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        vector : Vector
            Value supplied for ``vector`` according to the Matrix contract.
        
        Returns
        -------
        ``Vector`` result described by the method semantics.
        """
        if self.shape[1] != len(vector.components): raise ValueError("incompatible dimensions")
        return Vector([sum(a*b for a,b in zip(row,vector.components)) for row in self.rows])
    def __add__(self, other: "Matrix") -> "Matrix": return self.add(other)
    def __sub__(self, other: "Matrix") -> "Matrix": return self.subtract(other)
    def __matmul__(self, other: "Matrix") -> "Matrix": return self.matmul(other)
    def __mul__(self, scalar: float) -> "Matrix": return self.scale(scalar)
    __rmul__ = __mul__


class TreeDDM(DDM):
    """Hierarchical DDM tree node.
    
    Overview
    --------
    ``TreeDDM`` provides children, traversal orders, predicate search, depth and size.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for menus, categories, ownership trees and other recursive domain structures.
    
    Inheritance
    -----------
    Base class(es): ``DDM``.
    
    Primary public operations
    -------------------------
    add_child, walk, find, depth, size.
    """
    __slots__ = ()
    def __init__(self, value: Any = None, children: Optional[Iterable["TreeDDM"]] = None, **data: Any):
        """Initialize a new TreeDDM instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`TreeDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        value : Any (default: ``None``)
            Target, new or comparison value.
        children : Optional[Iterable['TreeDDM']] (default: ``None``)
            Optional initial child nodes/values.
        **data : Any
            Input mapping or record data used to initialize the object.
        """
        super().__init__({"value": value, "children": list(children or []), **data})
    def add_child(self, child: Any, **data: Any) -> "TreeDDM":
        """Append a child node/value and return the resulting child node.
        
        Details
        -------
        This method belongs to :class:`TreeDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        child : Any
            Value supplied for ``child`` according to the TreeDDM contract.
        **data : Any
            Input mapping or record data used to initialize the object.
        
        Returns
        -------
        ``'TreeDDM'`` result described by the method semantics.
        """
        node = child if isinstance(child, TreeDDM) else TreeDDM(child, **data); self.children.append(node); return node
    def walk(self, order: str = "dfs") -> Iterator["TreeDDM"]:
        """Traverse the tree in the requested supported order.
        
        Details
        -------
        This method belongs to :class:`TreeDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        order : str (default: ``'dfs'``)
            Traversal order name supported by TreeDDM.
        
        Returns
        -------
        ``Iterator['TreeDDM']`` result described by the method semantics.
        """
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
        """Return tree/search records that satisfy a predicate or query.
        
        Details
        -------
        This method belongs to :class:`TreeDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        predicate : Callable[['TreeDDM'], bool]
            Callable returning truthy for records that should match/be selected.
        
        Returns
        -------
        ``Optional['TreeDDM']`` result described by the method semantics.
        """
        return next((node for node in self.walk() if predicate(node)), None)
    def depth(self) -> int:
        """Return the maximum depth of the tree rooted at this node.
        
        Details
        -------
        This method belongs to :class:`TreeDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        """
        return 1 + max((child.depth() for child in self.children), default=-1)
    def size(self) -> int:
        """Return the number of nodes/items or terminal dimensions, depending on the class.
        
        Details
        -------
        This method belongs to :class:`TreeDDM` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        """
        return sum(1 for _ in self.walk())
