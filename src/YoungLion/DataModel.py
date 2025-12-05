"""
DataModel.py

Dynamic Data Model (DDM) - Professional hierarchical data management library.

**Overview:**
This module provides a powerful base class `DDM` for structured, hierarchical data
with comprehensive utilities for serialization, transformation, validation, and analysis.

**Key Features:**
- Recursive serialization to Python dictionaries via `.to_dict()`.
- Dynamic string representation with pretty-printing and ANSI colors.
- Nested DDM objects with automatic indentation levels.
- Cross-platform ANSI color support (Windows, Linux, Mac).
- Path-based access to nested attributes (e.g., "address.city").
- JSON import/export with full control.
- Deep cloning and merging operations.
- Batch processing utilities for lists of DDM objects.
- Advanced filtering, searching, and transformation methods.
- Schema validation and type checking.
- Difference detection (diff) between DDM instances.
- Statistical analysis and structure inspection.
- Builder pattern for fluent, chainable construction.
- CSV, XML-like export formats.
- Dict-like interface (__getitem__, __setitem__, __contains__).

**Core Utilities:**
- `DDMBuilder`: Fluent API for constructing DDM instances.
- `merge_ddms(*ddms)`: Merge multiple DDM objects.
- `compare_ddms(ddm1, ddm2)`: Compare two DDM instances in detail.
- `batch_transform(ddms, transformer)`: Apply transformation to DDM batch.
- `batch_filter(ddms, predicate)`: Filter DDM batch by condition.
- `validate_ddm_batch(ddms, schema)`: Validate multiple DDMs.
- `analyze_ddm_structure(ddm)`: Analyze DDM structure.
- `get_ddm_size_info(ddm)`: Get memory/size metrics.

**Utility Classes:**
- `Size`: 2D dimension management (width, height)
- `Point`: 2D coordinate management (x, y)
- `Color`: Full RGBA color system with conversions

**DDM-Based Specialized Classes:**
- `Range`: Bounded interval management with normalization
- `Vector`: N-dimensional vector with math operations (dot, cross, lerp)
- `Timeline`: Event/milestone management with time interpolation
- `Dataset`: Tabular data with row/column operations and statistics
- `SmartCache` (SC): Ultra-fast template-based data completion with memory optimization
"""

import os,sys,math
from typing import *
from .Colors import Colors


def enable_ansi() -> bool:
    """
    Enable ANSI escape sequences for Windows (if needed).
    Returns True if ANSI sequences can be used, False otherwise.
    """
    try:
        if os.name == "nt":
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            mode = ctypes.c_uint()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
                return True
            return False
        else:
            return sys.stdout.isatty()
    except Exception:
        return False

ANSI_SUPPORTED = enable_ansi()

class DDM:
    """
    **DDM** (Dynamic Data Model) is a professional base class for hierarchical structured data.
    
    **Features:**
    - Stores input dictionary data dynamically as attributes.
    - Supports nested DDM objects, lists, tuples, and dictionaries.
    - `.to_dict()` serializes recursively to JSON-serializable dictionaries.
    - `.to_json()` directly exports to JSON strings.
    - Pretty-printing via `__str__` with optional ANSI colors.
    - Indentation levels represent nested DDM depth.
    - Schema validation and type checking.
    - Diff detection between DDM instances.
    - Clone/copy operations for safe modifications.
    - Path-based access to nested attributes (e.g., "address.city").
    - Merge and update operations.
    - Export/import capabilities (JSON, YAML-like formats).
    
    **Methods:**
    - ``to_dict()``: Serialize to dictionary
    - ``to_json(indent=2)``: Export as JSON string
    - ``to_flat_dict(prefix="")``: Flatten nested structure
    - ``from_json(json_str)``: Parse from JSON string
    - ``clone()``: Deep copy
    - ``get_path(path)``: Get nested value by path
    - ``set_path(path, value)``: Set nested value by path
    - ``has_path(path)``: Check if path exists
    - ``merge(other)``: Merge another DDM
    - ``diff(other)``: Find differences
    - ``update(**kwargs)``: Update attributes
    - ``validate_schema(schema)``: Validate structure
    - ``keys()``, ``values()``, ``items()``: Dict-like iteration
    
    **Usage Example:**
    
        data = {
            "name": "Alice",
            "age": 30,
            "address": {"city": "NY", "zip": "10001"},
            "children": [{"name": "Bob", "age": 5}]
        }
        class Child(DDM): pass
        class Person(DDM):
            def __init__(self, data):
                super().__init__(data)
                self.children: List[Child] = [Child(c) for c in data.get("children", [])]
                
        person = Person(data)
        print(person)  # Pretty-printed, colored string
        print(person.to_dict())  # Serialized dict
        print(person.to_json())  # JSON export
        city = person.get_path("address.city")  # Path access
    """

    def __init__(self, data: Dict[str, Any]):
        """
        Initialize a DDM instance.

        :param data: Dictionary containing the data to wrap. Keys will become attributes.
        """
        self._data: Dict[str, Any] = data  # Store original input
        self._schema: Optional[Dict[str, Any]] = None  # Optional schema for validation
        for key, value in data.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """
        Recursively serialize the DDM instance to a Python dictionary.
        Private attributes (starting with '_') are ignored.
        Nested DDM instances are serialized recursively.

        :return: JSON-serializable dictionary
        """
        result: Dict[str, Any] = {}
        for k, v in self.__dict__.items():
            if k.startswith("_"):
                continue
            result[k] = self._serialize(v)
        return result

    def _serialize(self, value: Any) -> Any:
        """
        Recursive serializer for lists, tuples, dicts, and nested DDMs.

        :param value: Value to serialize
        :return: Serialized value
        """
        if isinstance(value, DDM):
            return value.to_dict()
        if isinstance(value, (list, tuple)):
            return type(value)(self._serialize(i) for i in value)
        if isinstance(value, dict):
            return {kk: self._serialize(vv) for kk, vv in value.items()}
        return value

    def __str__(self) -> str:
        """
        Pretty-print the DDM instance as a hierarchical string.
        Nested DDM objects are indented by levels.
        ANSI colors are applied if supported.
        """
        return self._str(level=0)

    def _str(self, level: int) -> str:
        """
        Internal recursive string representation.

        :param level: Current indentation level
        :return: String representation
        """
        indent = "\t" * level
        parts: List[str] = []
        for k, v in self.__dict__.items():
            if k.startswith("_"):
                continue
            key_str = f"{Colors.BLUE if ANSI_SUPPORTED else ''}{k}{Colors.RESET if ANSI_SUPPORTED else ''}"
            if isinstance(v, DDM):
                parts.append(f"{indent}{key_str}:")
                parts.append(v._str(level + 1))
            elif isinstance(v, list):
                list_strs = []
                for i in v:
                    if isinstance(i, DDM):
                        list_strs.append(i._str(level + 1))
                    else:
                        val_str = f"{Colors.GREEN if ANSI_SUPPORTED else ''}{i}{Colors.RESET if ANSI_SUPPORTED else ''}"
                        list_strs.append(f"{indent}\t- {val_str}")
                parts.append(f"{indent}{key_str}:[\n" + "\n".join(list_strs)+f"\n{indent}]")
            else:
                val_str = f"{Colors.GREEN if ANSI_SUPPORTED else ''}{v}{Colors.RESET if ANSI_SUPPORTED else ''}"
                parts.append(f"{indent}{key_str}: {val_str}")
        return "\n".join(parts)
    
    def to_json(self, indent: int = 2, include_private: bool = False) -> str:
        """Export as JSON string.
        
        :param indent: JSON indentation level
        :param include_private: Include private attributes (starting with _)
        :return: JSON string
        """
        import json
        data = self.to_dict() if not include_private else self._to_dict_full()
        return json.dumps(data, indent=indent, default=str)
    
    @staticmethod
    def from_json(json_str: str) -> "DDM":
        """Parse DDM from JSON string.
        
        :param json_str: JSON string
        :return: New DDM instance
        """
        import json
        data = json.loads(json_str)
        return DDM(data)
    
    def get_path(self, path: str, default: Any = None) -> Any:
        """Get nested value by dot-separated path.
        
        :param path: Path like "address.city" or "items.0.name"
        :param default: Default value if path not found
        :return: Value at path or default
        
        Example:
            person.get_path("address.city")  # → "NY"
            person.get_path("items.0.name")  # → Item name at index 0
        """
        parts = path.split(".")
        current = self
        
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part, default)
            elif isinstance(current, (list, tuple)):
                try:
                    idx = int(part)
                    current = current[idx]
                except (ValueError, IndexError):
                    return default
            elif isinstance(current, DDM):
                current = getattr(current, part, default)
            else:
                return default
            
            if current is default:
                return default
        
        return current
    
    def set_path(self, path: str, value: Any) -> bool:
        """Set nested value by dot-separated path.
        
        :param path: Path like "address.city"
        :param value: Value to set
        :return: True if successful, False if path invalid
        
        Example:
            person.set_path("address.city", "Boston")  # Updates nested value
        """
        parts = path.split(".")
        if not parts:
            return False
        
        current = self
        
        # Navigate to parent
        for part in parts[:-1]:
            if isinstance(current, DDM):
                if not hasattr(current, part):
                    setattr(current, part, {})
                current = getattr(current, part)
            elif isinstance(current, dict):
                if part not in current:
                    current[part] = {}
                current = current[part]
            else:
                return False
        
        # Set final value
        final_key = parts[-1]
        if isinstance(current, DDM):
            setattr(current, final_key, value)
            return True
        elif isinstance(current, dict):
            current[final_key] = value
            return True
        
        return False
    
    def has_path(self, path: str) -> bool:
        """Check if path exists.
        
        :param path: Dot-separated path
        :return: True if path exists
        """
        return self.get_path(path, None) is not None
    
    def clone(self) -> "DDM":
        """Create a deep copy of this DDM.
        
        :return: New independent DDM instance
        """
        import copy
        data_copy = copy.deepcopy(self._data)
        new_ddm = DDM(data_copy)
        
        # Copy all non-private attributes
        for k, v in self.__dict__.items():
            if not k.startswith("_"):
                try:
                    setattr(new_ddm, k, copy.deepcopy(v))
                except:
                    pass
        
        return new_ddm
    
    def copy(self) -> "DDM":
        """Alias for clone()."""
        return self.clone()
    
    def to_flat_dict(self, prefix: str = "", separator: str = ".") -> Dict[str, Any]:
        """Flatten nested structure into single-level dict with path keys.
        
        :param prefix: Prefix for all keys
        :param separator: Separator for path levels
        :return: Flattened dictionary
        
        Example:
            person = Person({"name": "Alice", "address": {"city": "NY"}})
            flat = person.to_flat_dict()
            # → {"name": "Alice", "address.city": "NY"}
        """
        result: Dict[str, Any] = {}
        
        for k, v in self.__dict__.items():
            if k.startswith("_"):
                continue
            
            key = f"{prefix}{separator}{k}" if prefix else k
            
            if isinstance(v, DDM):
                nested = v.to_flat_dict(prefix=key, separator=separator)
                result.update(nested)
            elif isinstance(v, dict):
                for dk, dv in v.items():
                    result[f"{key}{separator}{dk}"] = dv
            elif isinstance(v, (list, tuple)):
                for idx, item in enumerate(v):
                    result[f"{key}{separator}{idx}"] = item
            else:
                result[key] = v
        
        return result
    
    def merge(self, other: Union["DDM", Dict[str, Any]]) -> "DDM":
        """Merge another DDM or dict into this one (recursive).
        
        :param other: DDM or dictionary to merge
        :return: Self (for chaining)
        
        Example:
            person1.merge(person2)  # Merges person2 into person1
        """
        if isinstance(other, DDM):
            other_dict = other.to_dict()
        else:
            other_dict = other
        
        for key, value in other_dict.items():
            if hasattr(self, key):
                existing = getattr(self, key)
                if isinstance(existing, dict) and isinstance(value, dict):
                    existing.update(value)
                elif isinstance(existing, DDM) and isinstance(value, dict):
                    existing.merge(value)
                else:
                    setattr(self, key, value)
            else:
                setattr(self, key, value)
        
        return self
    
    def update(self, **kwargs) -> "DDM":
        """Update attributes from keyword arguments.
        
        :param kwargs: Key-value pairs to update
        :return: Self (for chaining)
        
        Example:
            person.update(name="Bob", age=31)
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self
    
    def diff(self, other: "DDM") -> Dict[str, Any]:
        """Find differences between this and another DDM.
        
        :param other: DDM to compare
        :return: Dictionary with differences
        
        Example:
            diff = person1.diff(person2)
            # → {"name": {"old": "Alice", "new": "Bob"}, ...}
        """
        differences: Dict[str, Any] = {}
        
        my_dict = self.to_dict()
        other_dict = other.to_dict()
        
        all_keys = set(my_dict.keys()) | set(other_dict.keys())
        
        for key in all_keys:
            my_val = my_dict.get(key)
            other_val = other_dict.get(key)
            
            if my_val != other_val:
                differences[key] = {
                    "old": my_val,
                    "new": other_val
                }
        
        return differences
    
    def keys(self) -> List[str]:
        """Return list of public attribute names."""
        return [k for k in self.__dict__.keys() if not k.startswith("_")]
    
    def values(self) -> List[Any]:
        """Return list of public attribute values."""
        return [v for k, v in self.__dict__.items() if not k.startswith("_")]
    
    def items(self) -> List[Tuple[str, Any]]:
        """Return list of (key, value) pairs for public attributes."""
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith("_")]
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get attribute value with default."""
        return getattr(self, key, default)
    
    def validate_schema(self, schema: Dict[str, type]) -> Tuple[bool, List[str]]:
        """Validate structure against schema.
        
        :param schema: Dict mapping attribute names to expected types
        :return: (is_valid, list_of_errors)
        
        Example:
            schema = {"name": str, "age": int, "address": dict}
            valid, errors = person.validate_schema(schema)
        """
        errors: List[str] = []
        
        for key, expected_type in schema.items():
            if not hasattr(self, key):
                errors.append(f"Missing required attribute: {key}")
            else:
                value = getattr(self, key)
                if not isinstance(value, expected_type):
                    errors.append(f"Attribute {key}: expected {expected_type.__name__}, got {type(value).__name__}")
        
        return len(errors) == 0, errors
    
    def __repr__(self) -> str:
        """Detailed representation showing class and key attributes."""
        class_name = self.__class__.__name__
        attrs = ", ".join([f"{k}={repr(v)[:30]}" for k, v in self.items()[:3]])
        return f"{class_name}({attrs}...)" if len(self.items()) > 3 else f"{class_name}({attrs})"
    
    def __len__(self) -> int:
        """Return number of public attributes."""
        return len(self.keys())
    
    def __getitem__(self, key: str) -> Any:
        """Support dict-like access: ddm['key']"""
        return getattr(self, key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Support dict-like assignment: ddm['key'] = value"""
        setattr(self, key, value)
    
    def __contains__(self, key: str) -> bool:
        """Support 'key' in ddm syntax."""
        return hasattr(self, key) and not key.startswith("_")
    
    def _to_dict_full(self) -> Dict[str, Any]:
        """Serialize including private attributes."""
        result: Dict[str, Any] = {}
        for k, v in self.__dict__.items():
            result[k] = self._serialize(v)
        return result
    
    def filter_keys(self, keys: List[str]) -> "DDM":
        """Create new DDM with only specified keys.
        
        :param keys: List of attribute names to keep
        :return: New filtered DDM
        
        Example:
            person_filtered = person.filter_keys(["name", "age"])
        """
        filtered_data = {k: self._data.get(k, getattr(self, k, None)) 
                        for k in keys if hasattr(self, k)}
        return DDM(filtered_data)
    
    def exclude_keys(self, keys: List[str]) -> "DDM":
        """Create new DDM excluding specified keys.
        
        :param keys: List of attribute names to exclude
        :return: New DDM without excluded keys
        """
        exclude_set = set(keys)
        filtered_data = {k: v for k, v in self.to_dict().items() 
                        if k not in exclude_set}
        return DDM(filtered_data)
    
    def search(self, query: str, case_sensitive: bool = False) -> Dict[str, Any]:
        """Search for query string in all attributes.
        
        :param query: String to search for
        :param case_sensitive: Case-sensitive search
        :return: Dictionary of matches with their paths
        
        Example:
            results = person.search("NY")  # Returns all values containing "NY"
        """
        results: Dict[str, Any] = {}
        query_str = query if case_sensitive else query.lower()
        
        for key, value in self.items():
            value_str = str(value) if not isinstance(value, (dict, list)) else str(value)
            check_str = value_str if case_sensitive else value_str.lower()
            
            if query_str in check_str:
                results[key] = value
        
        return results
    
    def find_by_type(self, target_type: type) -> Dict[str, Any]:
        """Find all attributes of specific type.
        
        :param target_type: Type to search for
        :return: Dictionary of matching attributes
        
        Example:
            ints = person.find_by_type(int)  # All integer attributes
        """
        results: Dict[str, Any] = {}
        for key, value in self.items():
            if isinstance(value, target_type):
                results[key] = value
        return results
    
    def transform(self, transformer: callable) -> "DDM":
        """Apply transformation function to all values.
        
        :param transformer: Function to apply to each value
        :return: New DDM with transformed values
        
        Example:
            uppercase = person.transform(lambda v: v.upper() if isinstance(v, str) else v)
        """
        transformed_data = {}
        for k, v in self.to_dict().items():
            try:
                transformed_data[k] = transformer(v)
            except:
                transformed_data[k] = v
        
        return DDM(transformed_data)
    
    def map_attributes(self, mapping: Dict[str, callable]) -> "DDM":
        """Apply specific transformations to selected attributes.
        
        :param mapping: Dict mapping attribute names to transformer functions
        :return: New DDM with applied transformations
        
        Example:
            result = person.map_attributes({
                "name": str.upper,
                "age": lambda x: x + 1
            })
        """
        new_data = self.to_dict().copy()
        for key, transformer in mapping.items():
            if key in new_data:
                try:
                    new_data[key] = transformer(new_data[key])
                except:
                    pass
        
        return DDM(new_data)
    
    def sort_by_key(self, reverse: bool = False) -> "DDM":
        """Create new DDM with keys sorted.
        
        :param reverse: Sort in descending order
        :return: New DDM with sorted keys
        """
        sorted_data = dict(sorted(self.to_dict().items(), reverse=reverse))
        return DDM(sorted_data)
    
    def sort_by_value(self, reverse: bool = False) -> "DDM":
        """Create new DDM sorted by values.
        
        :param reverse: Sort in descending order
        :return: New DDM with entries sorted by value
        """
        try:
            sorted_data = dict(sorted(self.to_dict().items(), 
                                     key=lambda item: item[1], 
                                     reverse=reverse))
            return DDM(sorted_data)
        except:
            # If values not comparable, return copy
            return self.clone()
    
    def group_by(self, key_func: callable) -> Dict[str, List[Tuple[str, Any]]]:
        """Group items by result of key function.
        
        :param key_func: Function to determine group key
        :return: Dictionary of groups
        
        Example:
            by_type = person.group_by(lambda item: type(item[1]).__name__)
        """
        groups: Dict[str, List[Tuple[str, Any]]] = {}
        
        for key, value in self.items():
            try:
                group_key = str(key_func((key, value)))
            except:
                group_key = "other"
            
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append((key, value))
        
        return groups
    
    def aggregate(self, aggregators: Dict[str, callable]) -> Dict[str, Any]:
        """Apply aggregation functions to attributes.
        
        :param aggregators: Dict mapping attribute names to aggregator functions
        :return: Dictionary of aggregation results
        
        Example:
            stats = ddm.aggregate({
                "values": lambda vals: sum(vals) if isinstance(vals, list) else vals,
                "name": len
            })
        """
        results: Dict[str, Any] = {}
        
        for key, aggregator in aggregators.items():
            if hasattr(self, key):
                try:
                    results[key] = aggregator(getattr(self, key))
                except:
                    results[key] = None
        
        return results
    
    def has_type(self, key: str, target_type: type) -> bool:
        """Check if attribute is of specific type.
        
        :param key: Attribute name
        :param target_type: Type to check
        :return: True if attribute exists and is of target type
        """
        if not hasattr(self, key):
            return False
        return isinstance(getattr(self, key), target_type)
    
    def get_types(self) -> Dict[str, str]:
        """Get type names of all attributes.
        
        :return: Dictionary mapping attribute names to type names
        """
        return {k: type(v).__name__ for k, v in self.items()}
    
    def if_exists(self, key: str) -> Optional["DDM"]:
        """Return self if key exists, else None (for chaining).
        
        :param key: Attribute name to check
        :return: Self if exists, None otherwise
        """
        return self if hasattr(self, key) else None
    
    def ensure(self, key: str, default: Any = None) -> "DDM":
        """Ensure attribute exists, set to default if not.
        
        :param key: Attribute name
        :param default: Default value if not present
        :return: Self (for chaining)
        """
        if not hasattr(self, key):
            setattr(self, key, default)
        return self
    
    def to_csv_line(self, sep: str = ",") -> str:
        """Export as CSV line (values only, no headers).
        
        :param sep: Separator character
        :return: CSV line string
        """
        values = [str(v).replace(sep, f"\\{sep}") for v in self.values()]
        return sep.join(values)
    
    @staticmethod
    def from_csv_line(csv_line: str, headers: List[str], sep: str = ",") -> "DDM":
        """Parse from CSV line with headers.
        
        :param csv_line: CSV line string
        :param headers: List of field names
        :param sep: Separator character
        :return: New DDM instance
        """
        values = csv_line.split(sep)
        data = {h: v for h, v in zip(headers, values)}
        return DDM(data)
    
    def to_xml_like(self, tag: str = "item", indent: int = 0) -> str:
        """Export as XML-like string.
        
        :param tag: Tag name
        :param indent: Indentation level
        :return: XML-like string
        """
        indent_str = "  " * indent
        lines = [f"{indent_str}<{tag}>"]
        
        for k, v in self.items():
            v_str = str(v).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            lines.append(f"{indent_str}  <{k}>{v_str}</{k}>")
        
        lines.append(f"{indent_str}</{tag}>")
        return "\n".join(lines)
    
    def only(self, *keys: str) -> "DDM":
        """Shortcut for filter_keys with positional args.
        
        Example:
            person.only("name", "age")
        """
        return self.filter_keys(list(keys))
    
    def without(self, *keys: str) -> "DDM":
        """Shortcut for exclude_keys with positional args.
        
        Example:
            person.without("password", "token")
        """
        return self.exclude_keys(list(keys))
    
    def pick(self, *keys: str) -> Dict[str, Any]:
        """Shortcut to get only specified keys as dict.
        
        Example:
            data = person.pick("name", "age")
        """
        return {k: getattr(self, k, None) for k in keys if hasattr(self, k)}

class ParseError(ValueError):
    """Raised when parsing from a string/list/tuple/dict fails.
    
    Enhanced with context information for debugging.
    """
    def __init__(self, message: str, value: Any = None, expected: str = None):
        """Initialize ParseError with detailed context.
        
        :param message: Error message
        :param value: The value that failed to parse
        :param expected: Description of what was expected
        """
        self.message = message
        self.value = value
        self.expected = expected
        
        full_msg = message
        if value is not None:
            full_msg += f"\n  Got value: {value!r}"
        if expected is not None:
            full_msg += f"\n  Expected: {expected}"
        
        super().__init__(full_msg)

def split_any(string: str, seps=("x", ",", ":", ";", ".")) -> List[str]:
    """
    Split a string using multiple separators.
    
    Tries each separator in order and returns first match.
    Useful for flexible parsing of dimension/coordinate strings.
    
    Example:
        "800x600", "800,600", "800.600" → ["800", "600"]
    
    :param string: String to split
    :param seps: Tuple of separators to try (in order)
    :return: List of parts
    :raises ParseError: If no valid separator found
    """
    for sep in seps:
        if sep in string:
            parts = string.split(sep)
            # Validate that we got meaningful parts
            parts = [p.strip() for p in parts]
            return parts
    
    raise ParseError(
        f"Could not detect a valid separator in string",
        value=string,
        expected=f"String containing one of: {', '.join(seps)}"
    )

def ensure_int_list(values: List[Any], expected_len: int, name: str) -> List[int]:
    """
    Convert list of values to integers with validation.
    
    Ensures correct length and type conversion.
    
    :param values: Values to convert
    :param expected_len: Expected number of values
    :param name: Name for error messages
    :return: List of integers
    :raises ParseError: If length mismatch or conversion fails
    """
    if len(values) != expected_len:
        raise ParseError(
            f"{name} has incorrect number of values",
            value=values,
            expected=f"exactly {expected_len} values"
        )
    
    try:
        int_values = []
        for v in values:
            # Handle string representations
            if isinstance(v, str):
                v = v.strip()
            int_values.append(int(v))
        return int_values
    except (ValueError, TypeError) as e:
        raise ParseError(
            f"{name} values cannot be converted to integers",
            value=values,
            expected="list of convertible-to-int values"
        )


class Size(DDM):
    """
    **Size**: A robust 2D size class for dimensions (width, height).
    
    Supports multiple initialization modes:
    - ``Size(size="800x600")`` — string with separator (x, comma, colon, dot, semicolon)
    - ``Size(size=[800, 600])`` — list or tuple of integers
    - ``Size(size={"width": 800, "height": 600})`` — dictionary
    - ``Size(auto=...)`` — automatic format detection (string, list, tuple, or dict)
    - ``Size(width=800, height=600)`` — explicit keyword arguments
    - ``Size(size="800x600", width=1024)`` — size + override (width takes precedence)
    
    **Attributes:**
    - ``width`` (int): Width dimension (must be > 0)
    - ``height`` (int): Height dimension (must be > 0)
    
    **Methods:**
    - ``area()``: Returns width × height
    - ``aspect_ratio()``: Returns width / height
    - ``scale(factor)``: Return new Size scaled by factor
    - ``scale_width(factor)``: Scale only width
    - ``scale_height(factor)``: Scale only height
    - ``fit_within(max_size)``: Fit this size within another, maintaining aspect ratio
    - ``contains(other_size)``: Check if this size can contain another
    - ``to_tuple()``: Return (width, height) tuple
    - ``to_dict()``: Return {"width": ..., "height": ...} dict
    - ``to_string()``: Return "widthxheight" string
    - ``clamp(min_size, max_size)``: Clamp to min/max bounds
    - ``transpose()``: Swap width and height
    
    **Example:**
    ```python
    s1 = Size("1920x1080")
    s2 = Size(auto=[640, 480])
    s3 = s1.scale(0.5)  # 960x540
    print(s1.aspect_ratio())  # 1.777...
    print(s1.area())  # 2073600
    ```
    """
    def __init__(
        self,
        size: Optional[Union[str, List[int], Tuple[int, int], Dict[str, int]]] = None,
        *,
        auto: Any = None,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> None:
        """Initialize a Size with flexible parsing.
        
        :param size: String ("800x600"), list [w,h], tuple, or dict {width, height}
        :param auto: Auto-detect format from string, list, tuple, or dict
        :param width: Explicit width (overrides parsed value)
        :param height: Explicit height (overrides parsed value)
        :raises ParseError: If size cannot be determined or is invalid
        :raises ValueError: If dimensions are not positive
        """
        super().__init__(data={})
        self.width: int = 0
        self.height: int = 0
        
        if auto is not None:
            size = self._parse_auto(auto)
        
        if size is not None:
            self.width, self.height = self._parse_size(size)
        
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        
        if self.width == 0 or self.height == 0:
            raise ParseError("Size dimensions could not be fully determined.")
        if self.width <= 0 or self.height <= 0:
            raise ValueError(f"Size dimensions must be positive integers: width={self.width}, height={self.height}")

    def _parse_auto(self, value: Any) -> Tuple[int, int]:
        """Auto-detect and parse size from various formats."""
        if isinstance(value, str):
            return self._parse_size(value)
        if isinstance(value, (list, tuple)):
            return self._parse_size(value)
        if isinstance(value, dict):
            if "width" in value and "height" in value:
                return int(value["width"]), int(value["height"])
            raise ParseError(f"Dict auto-format must contain 'width' and 'height' keys: {value}")
        raise ParseError(f"Unrecognized auto format for Size: {value!r}")
    
    def _parse_size(self, value: Any) -> Tuple[int, int]:
        """Parse size from string, list, or tuple."""
        if isinstance(value, str):
            parts = split_any(value)
            w, h = ensure_int_list(parts, 2, "Size")
            return w, h
        if isinstance(value, (list, tuple)):
            w, h = ensure_int_list(list(value), 2, "Size")
            return w, h
        raise ParseError(f"Unsupported size format: {value!r}")
    
    def to_tuple(self) -> Tuple[int, int]:
        """Return size as (width, height) tuple."""
        return (self.width, self.height)

    def to_dict(self) -> Dict[str, int]:
        """Return size as {"width": ..., "height": ...} dict."""
        return {"width": self.width, "height": self.height}
    
    def to_string(self) -> str:
        """Return size as 'widthxheight' string."""
        return f"{self.width}x{self.height}"
    
    def __str__(self) -> str:
        """String representation for printing."""
        return self.to_string()
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"Size(width={self.width}, height={self.height})"
    
    def __eq__(self, other: Any) -> bool:
        """Check equality with another Size."""
        if isinstance(other, Size):
            return self.width == other.width and self.height == other.height
        if isinstance(other, (tuple, list)) and len(other) == 2:
            return self.width == other[0] and self.height == other[1]
        return False

    def area(self) -> int:
        """Return area (width × height)."""
        return self.width * self.height

    def aspect_ratio(self) -> float:
        """Return aspect ratio (width / height)."""
        if self.height == 0:
            return 0.0
        return self.width / self.height
    
    def scale(self, factor: float) -> "Size":
        """Return new Size scaled by factor.
        
        :param factor: Scale factor (e.g., 0.5 for half, 2 for double)
        :return: New Size instance
        :raises ValueError: If factor is not positive
        """
        if factor <= 0:
            raise ValueError(f"Scale factor must be positive: {factor}")
        return Size(width=int(self.width * factor), height=int(self.height * factor))
    
    def scale_width(self, factor: float) -> "Size":
        """Return new Size with scaled width, keeping height."""
        if factor <= 0:
            raise ValueError(f"Scale factor must be positive: {factor}")
        return Size(width=int(self.width * factor), height=self.height)
    
    def scale_height(self, factor: float) -> "Size":
        """Return new Size with scaled height, keeping width."""
        if factor <= 0:
            raise ValueError(f"Scale factor must be positive: {factor}")
        return Size(width=self.width, height=int(self.height * factor))
    
    def fit_within(self, max_size: "Size") -> "Size":
        """Return new Size fitted within max_size, maintaining aspect ratio.
        
        :param max_size: Maximum Size to fit within
        :return: New Size that fits within max_size
        """
        if self.width <= max_size.width and self.height <= max_size.height:
            return Size(width=self.width, height=self.height)
        
        scale_w = max_size.width / self.width
        scale_h = max_size.height / self.height
        scale = min(scale_w, scale_h)
        
        return self.scale(scale)
    
    def contains(self, other: "Size") -> bool:
        """Check if this size can contain another size.
        
        :param other: Size to check
        :return: True if other fits within this size
        """
        return self.width >= other.width and self.height >= other.height
    
    def clamp(self, min_size: "Size", max_size: "Size") -> "Size":
        """Clamp size between min and max bounds.
        
        :param min_size: Minimum Size bounds
        :param max_size: Maximum Size bounds
        :return: New clamped Size
        """
        w = max(min_size.width, min(self.width, max_size.width))
        h = max(min_size.height, min(self.height, max_size.height))
        return Size(width=w, height=h)
    
    def transpose(self) -> "Size":
        """Return new Size with width and height swapped."""
        return Size(width=self.height, height=self.width)
    
    def __mul__(self, factor: float) -> "Size":
        """Support Size * factor syntax."""
        return self.scale(factor)
    
    def __rmul__(self, factor: float) -> "Size":
        """Support factor * Size syntax."""
        return self.scale(factor)

class Point(DDM):
    """
    **Point**: A 2D coordinate class for positions (x, y).
    
    Supports multiple initialization modes:
    - ``Point(auto="10x20")`` — string with separator (x, comma, colon, dot, semicolon)
    - ``Point(auto=[10, 20])`` — list or tuple of integers
    - ``Point(auto={"x": 10, "y": 20})`` — dictionary
    - ``Point(x=10, y=20)`` — explicit keyword arguments
    
    **Attributes:**
    - ``x`` (int): X coordinate
    - ``y`` (int): Y coordinate
    
    **Methods:**
    - ``distance_to(other)``: Euclidean distance to another point
    - ``translate(dx, dy)``: Return new Point moved by (dx, dy)
    - ``rotate_around(center, angle_deg)``: Rotate around a center point
    - ``midpoint(other)``: Return midpoint between two points
    - ``is_within_distance(other, distance)``: Check if within distance
    - ``normalize()``: Return normalized direction vector
    - ``clamp(min_point, max_point)``: Clamp to bounds
    - ``reflect_x(origin_x)``: Reflect across vertical line
    - ``reflect_y(origin_y)``: Reflect across horizontal line
    - ``to_tuple()``, ``to_dict()``, ``to_string()``
    
    **Example:**
    ```python
    p1 = Point(auto="100,200")
    p2 = Point(x=50, y=50)
    dist = p1.distance_to(p2)
    p3 = p1 + p2  # (150, 250)
    ```
    """

    def __init__(
        self,
        *,
        auto: Any = None,
        x: Optional[int] = None,
        y: Optional[int] = None,
        str_cordinate: Optional[str] = None,
        tuple_cordinate: Optional[Tuple[int, int]] = None,
        list_cordinate: Optional[List[int]] = None
    ) -> None:
        """Initialize a Point with flexible parsing."""
        super().__init__(data={})
        self.x: int = 0
        self.y: int = 0

        if auto is not None:
            x_val, y_val = self._parse_auto(auto)
            self.x, self.y = x_val, y_val

        if str_cordinate is not None:
            x_val, y_val = self._parse_str(str_cordinate)
            self.x, self.y = x_val, y_val

        if list_cordinate is not None:
            x_val, y_val = ensure_int_list(list_cordinate, 2, "Point list")
            self.x, self.y = x_val, y_val

        if tuple_cordinate is not None:
            x_val, y_val = ensure_int_list(list(tuple_cordinate), 2, "Point tuple")
            self.x, self.y = x_val, y_val

        if x is not None:
            self.x = x
        if y is not None:
            self.y = y

        if self.x is None or self.y is None:
            raise ParseError("Point could not be fully determined.")

    def _parse_auto(self, value: Any) -> Tuple[int, int]:
        """Auto-detect and parse point from various formats."""
        if isinstance(value, str):
            return self._parse_str(value)
        if isinstance(value, (list, tuple)):
            return ensure_int_list(list(value), 2, "Point auto-sequence")
        if isinstance(value, dict):
            if "x" in value and "y" in value:
                return int(value["x"]), int(value["y"])
            raise ParseError("Point auto-dict must have x/y.")
        raise ParseError(f"Unsupported auto format for Point:{value!r}")

    def _parse_str(self, s: str) -> Tuple[int, int]:
        """Parse point from string (e.g., "10x20", "10,20")."""
        parts = split_any(s)
        x_val, y_val = ensure_int_list(parts, 2, "Point string")
        return x_val, y_val

    def to_tuple(self) -> Tuple[int, int]:
        """Return point as (x, y) tuple."""
        return (self.x, self.y)

    def to_dict(self) -> Dict[str, int]:
        """Return point as {\"x\": ..., \"y\": ...} dict."""
        return {"x": self.x, "y": self.y}
    
    def to_string(self) -> str:
        """Return point as 'x,y' string."""
        return f"{self.x},{self.y}"
    
    def __str__(self) -> str:
        """String representation."""
        return self.to_string()
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"Point(x={self.x}, y={self.y})"
    
    def __eq__(self, other: Any) -> bool:
        """Check equality."""
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        if isinstance(other, (tuple, list)) and len(other) == 2:
            return self.x == other[0] and self.y == other[1]
        return False

    def translate(self, dx: int, dy: int) -> "Point":
        """Return new Point moved by (dx, dy)."""
        return Point(x=self.x + dx, y=self.y + dy)

    def distance_to(self, other: "Point") -> float:
        """Return Euclidean distance to another point."""
        return math.dist((self.x, self.y), (other.x, other.y))
    
    def is_within_distance(self, other: "Point", distance: float) -> bool:
        """Check if another point is within given distance."""
        return self.distance_to(other) <= distance
    
    def midpoint(self, other: "Point") -> "Point":
        """Return midpoint between this and another point."""
        return Point(x=(self.x + other.x) // 2, y=(self.y + other.y) // 2)
    
    def rotate_around(self, center: "Point", angle_deg: float) -> "Point":
        """Rotate this point around a center point by angle_deg degrees."""
        angle_rad = math.radians(angle_deg)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        dx = self.x - center.x
        dy = self.y - center.y
        
        new_x = dx * cos_a - dy * sin_a
        new_y = dx * sin_a + dy * cos_a
        
        return Point(x=int(center.x + new_x), y=int(center.y + new_y))
    
    def normalize(self) -> Tuple[float, float]:
        """Return normalized direction vector (unit vector)."""
        mag = math.sqrt(self.x ** 2 + self.y ** 2)
        if mag == 0:
            return (0.0, 0.0)
        return (self.x / mag, self.y / mag)
    
    def clamp(self, min_point: "Point", max_point: "Point") -> "Point":
        """Clamp coordinates between min and max bounds."""
        x = max(min_point.x, min(self.x, max_point.x))
        y = max(min_point.y, min(self.y, max_point.y))
        return Point(x=x, y=y)
    
    def reflect_x(self, origin_x: int = 0) -> "Point":
        """Reflect across vertical line (x = origin_x)."""
        return Point(x=2 * origin_x - self.x, y=self.y)
    
    def reflect_y(self, origin_y: int = 0) -> "Point":
        """Reflect across horizontal line (y = origin_y)."""
        return Point(x=self.x, y=2 * origin_y - self.y)

    def __add__(self, other: Union["Point", Any]) -> "Point":
        """Add coordinates (support Point + Point, Point + int, Point + tuple)."""
        if isinstance(other, Point):
            return Point(x=self.x + other.x, y=self.y + other.y)
        if isinstance(other, int):
            return Point(x=self.x + other, y=self.y + other)
        if isinstance(other, (list, tuple)) and len(other) >= 2:
            return Point(x=self.x + other[0], y=self.y + other[1])
        return NotImplemented

    def __sub__(self, other: Union["Point", Any]) -> "Point":
        """Subtract coordinates (support Point - Point, Point - int, Point - tuple)."""
        if isinstance(other, Point):
            return Point(x=self.x - other.x, y=self.y - other.y)
        if isinstance(other, int):
            return Point(x=self.x - other, y=self.y - other)
        if isinstance(other, (list, tuple)) and len(other) >= 2:
            return Point(x=self.x - other[0], y=self.y - other[1])
        return NotImplemented
    
    def __mul__(self, factor: float) -> "Point":
        """Support Point * factor syntax."""
        return Point(x=int(self.x * factor), y=int(self.y * factor))
    
    def __rmul__(self, factor: float) -> "Point":
        """Support factor * Point syntax."""
        return self.__mul__(factor)

    
Cordinate=Point

class Color(DDM):
    """
    **Color**: Full professional RGBA color system with comprehensive format support.
    
    Supports multiple initialization modes:
    - ``Color(auto="#FF5733")`` — hex (#RRGGBB or #RRGGBBAA)
    - ``Color(auto="255,87,51")`` — string with separators
    - ``Color(auto=0xFF5733)`` — integer (0xRRGGBB or 0xAARRGGBB)
    - ``Color(auto=[255, 87, 51])`` — list/tuple [R, G, B] or [R, G, B, A]
    - ``Color(auto={"r": 255, "g": 87, "b": 51})`` — dict (case-insensitive)
    - ``Color(r=255, g=87, b=51, a=255)`` — explicit keywords
    
    **Attributes:**
    - ``r``, ``g``, ``b``, ``a`` (int): 0–255 channels
    
    **Conversion Methods:**
    - ``to_hex()``, ``to_hex_lower()``: "#RRGGBB" or "#RRGGBBAA"
    - ``to_rgb()``, ``to_rgba()``: Tuples
    - ``to_int_rgb()``, ``to_int_rgba()``, ``to_int_argb()``: Packed integers
    - ``to_css()``: CSS "rgba(...)" string
    - ``to_tuple()``, ``to_tuple_normalized()``: 0–255 or 0–1 tuples
    - ``to_pillow()``: PIL format
    - ``to_hsl()``, ``to_hsv()``: Color space conversions
    
    **Manipulation Methods:**
    - ``blend(other, ratio)``: Blend colors
    - ``lighten(amount)``, ``darken(amount)``: Adjust brightness
    - ``saturate(amount)``, ``desaturate(amount)``: Adjust saturation
    - ``invert()``, ``grayscale()``: Transforms
    - ``adjust_alpha(amount)``: Modify opacity
    
    **Properties:**
    - ``is_transparent``, ``is_opaque``: Boolean checks
    - ``brightness``: Float 0–1 (perceived brightness)
    
    **Example:**
    ```python
    c1 = Color(auto="#FF5733")
    c2 = Color(r=100, g=200, b=50)
    c3 = c1.darken(50)
    c4 = c1.blend(c2, 0.5)
    ```
    """

    def __init__(
        self,
        *,
        auto=None,
        str_color=None,
        list_color=None,
        tuple_color=None,
        int_color=None,
        r=None,g=None,b=None,a=None
    ):
        super().__init__(data={})
        self.r=self.g=self.b=0
        self.a=255

        if auto is not None:
            R,G,B,A=self._parse_auto(auto)
            self.r,self.g,self.b,self.a=R,G,B,A

        if str_color is not None:
            R,G,B,A=self._parse_str(str_color)
            self.r,self.g,self.b,self.a=R,G,B,A

        if list_color is not None:
            vals=ensure_int_list(list_color,len(list_color),"Color list")
            if len(vals)==3:vals.append(255)
            elif len(vals)!=4:raise ParseError("Color list must have 3 or 4 values.")
            self.r,self.g,self.b,self.a=vals

        if tuple_color is not None:
            vals=ensure_int_list(list(tuple_color),len(tuple_color),"Color tuple")
            if len(vals)==3:vals.append(255)
            elif len(vals)!=4:raise ParseError("Color tuple must have 3 or 4 values.")
            self.r,self.g,self.b,self.a=vals

        if int_color is not None:
            R,G,B,A=self._parse_int(int_color)
            self.r,self.g,self.b,self.a=R,G,B,A

        if r is not None:self.r=int(r)
        if g is not None:self.g=int(g)
        if b is not None:self.b=int(b)
        if a is not None:self.a=int(a)

        self._validate()

    def _validate(self) -> None:
        """Validate all color channels are in range 0-255."""
        for name, v in {"r": self.r, "g": self.g, "b": self.b, "a": self.a}.items():
            if not (0 <= v <= 255):
                raise ValueError(f"Color channel '{name}' out of range: {v} (must be 0-255)")
    def _parse_auto(self,v):
        if isinstance(v,str):
            if v.startswith("#"):return self._parse_hex(v)
            return self._parse_str(v)
        if isinstance(v,(list,tuple)):return self._parse_sequence(v)
        if isinstance(v,dict):return self._parse_dict(v)
        if isinstance(v,int):return self._parse_int(v)

        raise ParseError(f"Unsupported auto-format for Color:{v!r}")

    def _parse_hex(self,s):
        s=s.lstrip("#")
        L=len(s)
        if L==6: # RRGGBB
            r=int(s[0:2],16)
            g=int(s[2:4],16)
            b=int(s[4:6],16)
            return r,g,b,255
        if L==8: # RRGGBBAA
            r=int(s[0:2],16)
            g=int(s[2:4],16)
            b=int(s[4:6],16)
            a=int(s[6:8],16)
            return r,g,b,a
        raise ParseError(f"Invalid hex color length:{s!r}")

    def _parse_str(self,s):
        parts=split_any(s)
        vals=ensure_int_list(parts,len(parts),"Color string")
        if len(vals)==3:vals.append(255)
        elif len(vals)!=4:raise ParseError("Color string must have 3 or 4 values.")
        return tuple(vals)

    def _parse_sequence(self,seq):
        vals=ensure_int_list(seq,len(seq),"Color sequence")
        if len(vals)==3:vals.append(255)
        elif len(vals)!=4:raise ParseError("Color sequence must have 3 or 4 values.")
        return tuple(vals)

    def _parse_dict(self,d):
        r=d.get("r") or d.get("R")
        g=d.get("g") or d.get("G")
        b=d.get("b") or d.get("B")
        a=d.get("a") or d.get("A") or d.get("alpha") or d.get("Alpha") or d.get("ALPHA") or 255
        if r is None or g is None or b is None:raise ParseError(f"Dict color must have r,g,b keys:{d}")
        return int(r),int(g),int(b),int(a)

    def _parse_int(self,value:int):
        """
        Supports:
            0xRRGGBB
            0xAARRGGBB
            decimal ints like 16711680
        """
        if value<0 or value>0xFFFFFFFF:raise ParseError(f"Invalid packed color integer:{value}")
        if value<=0xFFFFFF:
            r=(value>>16)&255
            g=(value>>8)&255
            b=value&255
            return r,g,b,255

        # has alpha → AARRGGBB
        a=(value>>24)&255
        r=(value>>16)&255
        g=(value>>8)&255
        b=value&255
        return r,g,b,a

    def to_hex(self,include_alpha=False):
        if include_alpha:return f"#{self.r:02X}{self.g:02X}{self.b:02X}{self.a:02X}"
        return f"#{self.r:02X}{self.g:02X}{self.b:02X}"

    def to_hex_lower(self,include_alpha=False):return self.to_hex(include_alpha).lower()

    def to_rgb(self):return (self.r,self.g,self.b)

    def to_rgba(self):return (self.r,self.g,self.b,self.a)

    def to_int_rgb(self):
        """RRGGBB as integer."""
        return ((self.r&255) << 16)|((self.g&255) << 8)|(self.b&255)

    def to_int_rgba(self):
        """RRGGBBAA packed."""
        return ((self.r&255) << 24)|((self.g&255) << 16)|((self.b&255) << 8)|(self.a&255)

    def to_int_argb(self):
        """AARRGGBB packed."""
        return ((self.a&255) << 24)|((self.r&255) << 16)|((self.g&255) << 8)|(self.b&255)

    def to_css(self):
        """CSS rgba format."""
        return f"rgba({self.r},{self.g},{self.b},{self.a/255:.3f})"

    def to_tuple(self):
        return (self.r,self.g,self.b,self.a)

    def to_tuple_normalized(self):
        return (self.r/255,self.g/255,self.b/255,self.a/255)
    
    def to_dict(self):
        return {'r':self.r,'g':self.g,'b':self.b,"alpha":self.a}

    def to_pillow(self):
        """PIL RGBA tuple."""
        return (self.r,self.g,self.b,self.a)

    def to_string(self) -> str:
        """Return color as 'R,G,B,A' string."""
        return f"{self.r},{self.g},{self.b},{self.a}"
    
    def __str__(self) -> str:
        """String representation for printing."""
        return self.to_hex(include_alpha=(self.a != 255))
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"Color(r={self.r}, g={self.g}, b={self.b}, a={self.a})"
    
    def __eq__(self, other: Any) -> bool:
        """Check equality with another Color."""
        if isinstance(other, Color):
            return self.r == other.r and self.g == other.g and self.b == other.b and self.a == other.a
        if isinstance(other, (tuple, list)) and len(other) >= 3:
            alpha = other[3] if len(other) >= 4 else 255
            return self.r == other[0] and self.g == other[1] and self.b == other[2] and self.a == alpha
        return False
    
    @property
    def is_transparent(self) -> bool:
        """True if alpha is less than 128 (semi-transparent or transparent)."""
        return self.a < 128
    
    @property
    def is_opaque(self) -> bool:
        """True if alpha equals 255 (fully opaque)."""
        return self.a == 255
    
    @property
    def brightness(self) -> float:
        """Return perceived brightness (0–1).
        
        Uses standard luminance formula: 0.299*R + 0.587*G + 0.114*B
        """
        return (0.299 * self.r + 0.587 * self.g + 0.114 * self.b) / 255.0
    
    def blend(self, other: "Color", ratio: float = 0.5) -> "Color":
        """Blend this color with another color.
        
        :param other: Target Color to blend with
        :param ratio: Blend ratio (0.0 = 100% self, 1.0 = 100% other)
        :return: New blended Color
        :raises ValueError: If ratio is not in [0, 1]
        """
        if not (0.0 <= ratio <= 1.0):
            raise ValueError(f"Blend ratio must be in [0, 1]: {ratio}")
        
        inv_ratio = 1.0 - ratio
        return Color(
            r=int(self.r * inv_ratio + other.r * ratio),
            g=int(self.g * inv_ratio + other.g * ratio),
            b=int(self.b * inv_ratio + other.b * ratio),
            a=int(self.a * inv_ratio + other.a * ratio)
        )
    
    def lighten(self, amount: int = 30) -> "Color":
        """Return lighter color by increasing RGB values.
        
        :param amount: Amount to increase each channel (0-255)
        :return: New lighter Color
        """
        return Color(
            r=min(255, self.r + amount),
            g=min(255, self.g + amount),
            b=min(255, self.b + amount),
            a=self.a
        )
    
    def darken(self, amount: int = 30) -> "Color":
        """Return darker color by decreasing RGB values.
        
        :param amount: Amount to decrease each channel (0-255)
        :return: New darker Color
        """
        return Color(
            r=max(0, self.r - amount),
            g=max(0, self.g - amount),
            b=max(0, self.b - amount),
            a=self.a
        )
    
    def invert(self) -> "Color":
        """Return color with inverted RGB (255-R, 255-G, 255-B).
        
        Alpha channel is preserved.
        """
        return Color(r=255 - self.r, g=255 - self.g, b=255 - self.b, a=self.a)
    
    def grayscale(self) -> "Color":
        """Return grayscale version using luminance formula."""
        gray = int(0.299 * self.r + 0.587 * self.g + 0.114 * self.b)
        return Color(r=gray, g=gray, b=gray, a=self.a)
    
    def adjust_alpha(self, amount: int) -> "Color":
        """Return new Color with adjusted alpha.
        
        :param amount: Amount to adjust (positive increases opacity, negative decreases)
        :return: New Color with clamped alpha
        """
        return Color(r=self.r, g=self.g, b=self.b, a=max(0, min(255, self.a + amount)))
    
    def saturate(self, amount: float = 0.1) -> "Color":
        """Increase color saturation (make more vibrant).
        
        :param amount: Saturation adjustment (0.0–1.0 recommended)
        :return: New Color with adjusted saturation
        """
        h, s, l = self.to_hsl()
        s = min(1.0, s + amount)
        return self._hsl_to_color(h, s, l)
    
    def desaturate(self, amount: float = 0.1) -> "Color":
        """Decrease color saturation (make less vibrant).
        
        :param amount: Saturation adjustment (0.0–1.0 recommended)
        :return: New Color with adjusted saturation
        """
        h, s, l = self.to_hsl()
        s = max(0.0, s - amount)
        return self._hsl_to_color(h, s, l)
    
    @staticmethod
    def _hsl_to_color(h: float, s: float, l: float) -> "Color":
        """Convert HSL to RGB Color (internal helper)."""
        def hue_to_rgb(p: float, q: float, t: float) -> int:
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1 / 6:
                return int(255 * (p + (q - p) * 6 * t))
            if t < 1 / 2:
                return int(255 * q)
            if t < 2 / 3:
                return int(255 * (p + (q - p) * (2 / 3 - t) * 6))
            return int(255 * p)
        
        if s == 0:
            gray = int(255 * l)
            return Color(r=gray, g=gray, b=gray)
        
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        
        r_val = hue_to_rgb(p, q, h + 1 / 3)
        g_val = hue_to_rgb(p, q, h)
        b_val = hue_to_rgb(p, q, h - 1 / 3)
        
        return Color(r=r_val, g=g_val, b=b_val)


    def to_hsl(self) -> Tuple[float, float, float]:
        """Return HSL color space as (H, S, L) floats 0–1.
        
        - H (Hue): 0.0–1.0 (0°–360°)
        - S (Saturation): 0.0–1.0 (0%–100%)
        - L (Lightness): 0.0–1.0 (0%–100%)
        """
        r, g, b = self.r / 255, self.g / 255, self.b / 255
        mx, mn = max(r, g, b), min(r, g, b)
        d = mx - mn

        # lightness
        l = (mx + mn) / 2
        if d == 0:
            h = s = 0
        else:
            s = d / (1 - abs(2 * l - 1))
            if mx == r:
                h = ((g - b) / d) % 6
            elif mx == g:
                h = ((b - r) / d) + 2
            else:
                h = ((r - g) / d) + 4
            h /= 6

        return (h, s, l)

    def to_hsv(self) -> Tuple[float, float, float]:
        """Return HSV color space as (H, S, V) floats 0–1.
        
        - H (Hue): 0.0–1.0 (0°–360°)
        - S (Saturation): 0.0–1.0 (0%–100%)
        - V (Value): 0.0–1.0 (0%–100%, also called brightness)
        """
        r, g, b = self.r / 255, self.g / 255, self.b / 255
        mx, mn = max(r, g, b), min(r, g, b)
        d = mx - mn

        # hue
        if d == 0:
            h = 0
        elif mx == r:
            h = ((g - b) / d) % 6
        elif mx == g:
            h = ((b - r) / d) + 2
        else:
            h = ((r - g) / d) + 4
        h /= 6
        s = 0 if mx == 0 else d / mx
        v = mx

        return (h, s, v)

class DDMBuilder:
    """Builder pattern for constructing complex DDM instances.
    
    Allows fluent, chainable API for building hierarchical data structures.
    
    Example:
        builder = DDMBuilder()
        person = (builder
            .set("name", "Alice")
            .set("age", 30)
            .nest("address", lambda b: b.set("city", "NY").set("zip", "10001"))
            .build()
        )
    """
    
    def __init__(self):
        """Initialize empty builder."""
        self._data: Dict[str, Any] = {}
    
    def set(self, key: str, value: Any) -> "DDMBuilder":
        """Set a key-value pair.
        
        :param key: Attribute name
        :param value: Attribute value
        :return: Self for chaining
        """
        self._data[key] = value
        return self
    
    def set_many(self, **kwargs) -> "DDMBuilder":
        """Set multiple key-value pairs at once.
        
        :param kwargs: Key-value pairs to set
        :return: Self for chaining
        """
        self._data.update(kwargs)
        return self
    
    def nest(self, key: str, builder_func: callable) -> "DDMBuilder":
        """Create nested DDM using builder function.
        
        :param key: Parent key
        :param builder_func: Function that takes builder and returns it
        :return: Self for chaining
        
        Example:
            .nest("address", lambda b: b.set("city", "NY"))
        """
        nested_builder = DDMBuilder()
        builder_func(nested_builder)
        self._data[key] = DDM(nested_builder._data)
        return self
    
    def add_list(self, key: str, items: List[Any]) -> "DDMBuilder":
        """Add a list of items.
        
        :param key: List key
        :param items: List items
        :return: Self for chaining
        """
        self._data[key] = items
        return self
    
    def build(self) -> DDM:
        """Build final DDM instance.
        
        :return: Constructed DDM
        """
        return DDM(self._data)


def merge_ddms(*ddms: DDM) -> DDM:
    """Merge multiple DDM instances into one.
    
    Later DDMs override earlier ones in case of key conflicts.
    
    :param ddms: Variable number of DDM instances
    :return: New merged DDM
    
    Example:
        combined = merge_ddms(person1, person2, person3)
    """
    result_data: Dict[str, Any] = {}
    
    for ddm in ddms:
        if isinstance(ddm, DDM):
            result_data.update(ddm.to_dict())
    
    return DDM(result_data)


def compare_ddms(ddm1: DDM, ddm2: DDM, show_only_diff: bool = True) -> Dict[str, Any]:
    """Compare two DDM instances in detail.
    
    :param ddm1: First DDM
    :param ddm2: Second DDM
    :param show_only_diff: Only show different values
    :return: Comparison dictionary
    """
    d1 = ddm1.to_dict()
    d2 = ddm2.to_dict()
    
    comparison: Dict[str, Any] = {}
    all_keys = set(d1.keys()) | set(d2.keys())
    
    for key in all_keys:
        v1 = d1.get(key)
        v2 = d2.get(key)
        
        if show_only_diff and v1 == v2:
            continue
        
        comparison[key] = {
            "ddm1": v1,
            "ddm2": v2,
            "equal": v1 == v2,
            "type1": type(v1).__name__,
            "type2": type(v2).__name__
        }
    
    return comparison


def flatten_to_single_dict(*ddms: DDM) -> Dict[str, Any]:
    """Flatten multiple DDMs into single flat dictionary with path keys.
    
    :param ddms: Variable number of DDM instances
    :return: Flattened dictionary with path keys
    """
    result: Dict[str, Any] = {}
    
    for i, ddm in enumerate(ddms):
        flat = ddm.to_flat_dict()
        # Prefix with ddm index to avoid conflicts
        prefixed = {f"ddm{i}_{k}": v for k, v in flat.items()}
        result.update(prefixed)
    
    return result


def batch_transform(ddms: List[DDM], transformer: callable) -> List[DDM]:
    """Apply same transformation to batch of DDM instances.
    
    :param ddms: List of DDM instances
    :param transformer: Transformation function
    :return: List of transformed DDMs
    
    Example:
        uppercase_all = batch_transform(people, 
            lambda ddm: ddm.transform(lambda v: v.upper() if isinstance(v, str) else v)
        )
    """
    return [transformer(ddm) for ddm in ddms]


def batch_filter(ddms: List[DDM], predicate: callable) -> List[DDM]:
    """Filter batch of DDM instances by predicate.
    
    :param ddms: List of DDM instances
    :param predicate: Function returning True/False
    :return: Filtered list of DDMs
    
    Example:
        adults = batch_filter(people, lambda p: p.get("age", 0) >= 18)
    """
    return [ddm for ddm in ddms if predicate(ddm)]


def validate_ddm_batch(ddms: List[DDM], schema: Dict[str, type]) -> Dict[int, Tuple[bool, List[str]]]:
    """Validate batch of DDMs against schema.
    
    :param ddms: List of DDM instances
    :param schema: Validation schema
    :return: Dictionary mapping DDM index to (is_valid, errors)
    """
    results: Dict[int, Tuple[bool, List[str]]] = {}
    
    for i, ddm in enumerate(ddms):
        valid, errors = ddm.validate_schema(schema)
        results[i] = (valid, errors)
    
    return results

def analyze_ddm_structure(ddm: DDM) -> Dict[str, Any]:
    """Analyze structural properties of a DDM.
    
    :param ddm: DDM instance to analyze
    :return: Dictionary with structural info
    """
    flat = ddm.to_flat_dict()
    types = ddm.get_types()
    
    analysis: Dict[str, Any] = {
        "total_attributes": len(ddm),
        "attribute_names": ddm.keys(),
        "attribute_types": types,
        "nested_depth": max([len(k.split(".")) for k in flat.keys()]) if flat else 1,
        "contains_nested_ddm": any(isinstance(v, DDM) for v in ddm.values()),
        "contains_lists": any(isinstance(v, (list, tuple)) for v in ddm.values()),
        "type_distribution": {}
    }
    
    # Calculate type distribution
    for type_name in types.values():
        analysis["type_distribution"][type_name] = analysis["type_distribution"].get(type_name, 0) + 1
    
    return analysis


def get_ddm_size_info(ddm: DDM) -> Dict[str, int]:
    """Get size information about DDM data.
    
    :param ddm: DDM instance
    :return: Dictionary with size metrics
    """
    import sys
    
    data_dict = ddm.to_dict()
    
    return {
        "total_keys": len(data_dict),
        "approximate_memory_bytes": sys.getsizeof(data_dict),
        "string_attributes": sum(1 for v in data_dict.values() if isinstance(v, str)),
        "numeric_attributes": sum(1 for v in data_dict.values() if isinstance(v, (int, float))),
        "list_attributes": sum(1 for v in data_dict.values() if isinstance(v, list)),
        "dict_attributes": sum(1 for v in data_dict.values() if isinstance(v, dict)),
    }

class Range(DDM):
    """
    **Range**: DDM-based range/interval management for continuous values.
    
    Represents a bounded numerical interval with optional step/granularity.
    Useful for value validation, iteration, and constraint management.
    
    **Attributes:**
    - `min_val` (float): Minimum value
    - `max_val` (float): Maximum value
    - `step` (float): Step size (default 1.0)
    - `inclusive_end` (bool): Include max_val in iteration
    
    **Methods:**
    - `contains(value)`: Check if value in range
    - `clamp(value)`: Clamp value to range
    - `normalize(value)`: Map value to [0, 1]
    - `denormalize(normalized)`: Map from [0, 1] to range
    - `span()`: Get range width
    - `midpoint()`: Get center value
    - `random()`: Get random value in range
    - `iterate()`: Generator for stepped values
    - `subdivide(n)`: Split into n sub-ranges
    - `intersect(other)`: Find intersection with another range
    - `overlaps(other)`: Check overlap
    
    **Example:**
    ```python
    r = Range(min_val=0, max_val=100, step=10)
    assert r.contains(50)  # True
    assert r.clamp(150)    # 100
    for val in r.iterate():
        print(val)  # 0, 10, 20, ..., 100
    ```
    """
    
    def __init__(self, *, min_val: float, max_val: float, step: float = 1.0, inclusive_end: bool = True):
        """Initialize a Range.
        
        :param min_val: Minimum value
        :param max_val: Maximum value
        :param step: Step size for iteration
        :param inclusive_end: Include max_val in range
        :raises ValueError: If min_val >= max_val or step <= 0
        """
        if min_val >= max_val:
            raise ValueError(f"min_val ({min_val}) must be less than max_val ({max_val})")
        if step <= 0:
            raise ValueError(f"step ({step}) must be positive")
        
        super().__init__({
            "min_val": float(min_val),
            "max_val": float(max_val),
            "step": float(step),
            "inclusive_end": bool(inclusive_end)
        })
        
        self.min_val = float(min_val)
        self.max_val = float(max_val)
        self.step = float(step)
        self.inclusive_end = bool(inclusive_end)
    
    def contains(self, value: float) -> bool:
        """Check if value is within range (inclusive)."""
        return self.min_val <= value <= self.max_val
    
    def clamp(self, value: float) -> float:
        """Clamp value to range bounds."""
        return max(self.min_val, min(value, self.max_val))
    
    def span(self) -> float:
        """Get the width of range."""
        return self.max_val - self.min_val
    
    def midpoint(self) -> float:
        """Get center/midpoint value."""
        return (self.min_val + self.max_val) / 2.0
    
    def normalize(self, value: float) -> float:
        """Map value to [0, 1] range.
        
        :param value: Value to normalize
        :return: Normalized value in [0, 1]
        """
        span = self.span()
        if span == 0:
            return 0.0
        return (self.clamp(value) - self.min_val) / span
    
    def denormalize(self, normalized: float) -> float:
        """Map from [0, 1] to this range.
        
        :param normalized: Value in [0, 1]
        :return: Mapped value in this range
        """
        return self.min_val + normalized * self.span()
    
    def random(self) -> float:
        """Get random value within range."""
        import random
        return random.uniform(self.min_val, self.max_val)
    
    def iterate(self):
        """Generate values from min to max with step size."""
        current = self.min_val
        while current < self.max_val or (self.inclusive_end and current == self.max_val):
            yield current
            current += self.step
            if current > self.max_val and not self.inclusive_end:
                break
    
    def subdivide(self, n: int) -> List["Range"]:
        """Divide range into n equal sub-ranges.
        
        :param n: Number of subdivisions
        :return: List of Range objects
        """
        if n < 1:
            raise ValueError(f"n must be >= 1: {n}")
        
        span = self.span()
        sub_span = span / n
        ranges = []
        
        for i in range(n):
            sub_min = self.min_val + i * sub_span
            sub_max = sub_min + sub_span if i < n - 1 else self.max_val
            ranges.append(Range(min_val=sub_min, max_val=sub_max, step=self.step))
        
        return ranges
    
    def intersect(self, other: "Range") -> Optional["Range"]:
        """Find intersection with another range.
        
        :param other: Another Range object
        :return: New Range if intersection exists, None otherwise
        """
        inter_min = max(self.min_val, other.min_val)
        inter_max = min(self.max_val, other.max_val)
        
        if inter_min >= inter_max:
            return None
        
        return Range(min_val=inter_min, max_val=inter_max, 
                    step=min(self.step, other.step))
    
    def overlaps(self, other: "Range") -> bool:
        """Check if ranges overlap.
        
        :param other: Another Range object
        :return: True if ranges overlap
        """
        return self.intersect(other) is not None
    
    def __str__(self) -> str:
        return f"Range({self.min_val}..{self.max_val}, step={self.step})"
    
    def __repr__(self) -> str:
        return f"Range(min_val={self.min_val}, max_val={self.max_val}, step={self.step})"


class Vector(DDM):
    """
    **Vector**: DDM-based n-dimensional vector with mathematical operations.
    
    Supports arbitrary dimensions, mathematical operations, and linear algebra.
    
    **Attributes:**
    - `components` (List[float]): Vector components
    - `dimension` (int): Number of dimensions
    
    **Methods:**
    - `magnitude()`: Get vector length (norm)
    - `normalize()`: Return unit vector
    - `dot(other)`: Dot product
    - `cross(other)`: Cross product (3D only)
    - `distance_to(other)`: Distance to another vector
    - `angle_to(other)`: Angle to another vector (degrees)
    - `add(other)`: Vector addition
    - `subtract(other)`: Vector subtraction
    - `scale(factor)`: Scalar multiplication
    - `project_onto(other)`: Project onto another vector
    - `perpendicular()`: Get perpendicular vector
    - `lerp(other, t)`: Linear interpolation
    
    **Example:**
    ```python
    v1 = Vector(components=[1, 2, 3])
    v2 = Vector(components=[4, 5, 6])
    dot = v1.dot(v2)           # 32
    dist = v1.distance_to(v2)  # ~5.196
    v3 = v1.lerp(v2, 0.5)      # Midpoint
    ```
    """
    
    def __init__(self, *, components: List[float]):
        """Initialize a Vector.
        
        :param components: List of numerical components
        :raises ValueError: If components is empty
        """
        if not components:
            raise ValueError("Vector must have at least one component")
        
        components = [float(c) for c in components]
        
        super().__init__({
            "components": components,
            "dimension": len(components)
        })
        
        self.components = components
        self.dimension = len(components)
    
    def magnitude(self) -> float:
        """Get vector length (Euclidean norm)."""
        return math.sqrt(sum(c ** 2 for c in self.components))
    
    def normalize(self) -> "Vector":
        """Return normalized unit vector."""
        mag = self.magnitude()
        if mag == 0:
            return Vector(components=self.components.copy())
        return Vector(components=[c / mag for c in self.components])
    
    def dot(self, other: "Vector") -> float:
        """Calculate dot product with another vector.
        
        :param other: Another Vector
        :return: Dot product
        :raises ValueError: If dimensions don't match
        """
        if self.dimension != other.dimension:
            raise ValueError(f"Dimension mismatch: {self.dimension} vs {other.dimension}")
        
        return sum(a * b for a, b in zip(self.components, other.components))
    
    def cross(self, other: "Vector") -> "Vector":
        """Calculate cross product (3D vectors only).
        
        :param other: Another 3D Vector
        :return: New Vector (cross product)
        :raises ValueError: If not 3D or dimension mismatch
        """
        if self.dimension != 3 or other.dimension != 3:
            raise ValueError(f"Cross product requires 3D vectors, got {self.dimension}D and {other.dimension}D")
        
        a = self.components
        b = other.components
        
        return Vector(components=[
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]
        ])
    
    def distance_to(self, other: "Vector") -> float:
        """Calculate Euclidean distance to another vector."""
        if self.dimension != other.dimension:
            raise ValueError(f"Dimension mismatch: {self.dimension} vs {other.dimension}")
        
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(self.components, other.components)))
    
    def angle_to(self, other: "Vector") -> float:
        """Calculate angle to another vector in degrees.
        
        :param other: Another Vector
        :return: Angle in degrees [0, 180]
        """
        mag_product = self.magnitude() * other.magnitude()
        if mag_product == 0:
            return 0.0
        
        cos_angle = self.dot(other) / mag_product
        cos_angle = max(-1.0, min(1.0, cos_angle))  # Clamp to [-1, 1]
        
        return math.degrees(math.acos(cos_angle))
    
    def add(self, other: "Vector") -> "Vector":
        """Add another vector."""
        if self.dimension != other.dimension:
            raise ValueError(f"Dimension mismatch: {self.dimension} vs {other.dimension}")
        
        return Vector(components=[a + b for a, b in zip(self.components, other.components)])
    
    def subtract(self, other: "Vector") -> "Vector":
        """Subtract another vector."""
        if self.dimension != other.dimension:
            raise ValueError(f"Dimension mismatch: {self.dimension} vs {other.dimension}")
        
        return Vector(components=[a - b for a, b in zip(self.components, other.components)])
    
    def scale(self, factor: float) -> "Vector":
        """Scale vector by scalar factor."""
        return Vector(components=[c * factor for c in self.components])
    
    def project_onto(self, other: "Vector") -> "Vector":
        """Project this vector onto another.
        
        :param other: Vector to project onto
        :return: Projected vector
        """
        other_mag_sq = other.dot(other)
        if other_mag_sq == 0:
            raise ValueError("Cannot project onto zero vector")
        
        scalar = self.dot(other) / other_mag_sq
        return other.scale(scalar)
    
    def perpendicular(self) -> "Vector":
        """Get perpendicular vector (2D only)."""
        if self.dimension != 2:
            raise ValueError(f"Perpendicular only for 2D vectors, got {self.dimension}D")
        
        return Vector(components=[-self.components[1], self.components[0]])
    
    def lerp(self, other: "Vector", t: float) -> "Vector":
        """Linear interpolation to another vector.
        
        :param other: Target vector
        :param t: Interpolation factor [0, 1]
        :return: Interpolated vector
        """
        if t < 0 or t > 1:
            raise ValueError(f"t must be in [0, 1]: {t}")
        
        inv_t = 1.0 - t
        return Vector(components=[
            a * inv_t + b * t 
            for a, b in zip(self.components, other.components)
        ])
    
    def __str__(self) -> str:
        vals = ", ".join(f"{c:.2f}" for c in self.components)
        return f"Vector[{vals}]"
    
    def __repr__(self) -> str:
        return f"Vector(components={self.components})"
    
    def __add__(self, other: "Vector") -> "Vector":
        """Support v1 + v2 syntax."""
        return self.add(other)
    
    def __sub__(self, other: "Vector") -> "Vector":
        """Support v1 - v2 syntax."""
        return self.subtract(other)
    
    def __mul__(self, factor: float) -> "Vector":
        """Support v * factor syntax."""
        return self.scale(factor)
    
    def __rmul__(self, factor: float) -> "Vector":
        """Support factor * v syntax."""
        return self.scale(factor)


class Timeline(DDM):
    """
    **Timeline**: DDM-based sequential event/milestone management.
    
    Manages a sequence of time-indexed events with various operations.
    Useful for animations, schedules, and event logging.
    
    **Attributes:**
    - `events` (List[Dict]): List of {time, label, data}
    - `start_time` (float): Timeline start
    - `end_time` (float): Timeline end
    - `duration` (float): Total duration
    
    **Methods:**
    - `add_event(time, label, data)`: Add event at time
    - `remove_event(label)`: Remove event by label
    - `get_event(label)`: Get event data
    - `events_at(time)`: Get events at specific time
    - `events_between(t1, t2)`: Get events in time range
    - `get_progress(current_time)`: Get 0-1 progress
    - `interpolate(current_time)`: Interpolate between events
    - `sort()`: Sort events by time
    - `duration()`: Get total duration
    - `reverse()`: Reverse event order
    
    **Example:**
    ```python
    tl = Timeline(start_time=0, end_time=10)
    tl.add_event(0, "start", {"value": 0})
    tl.add_event(5, "middle", {"value": 50})
    tl.add_event(10, "end", {"value": 100})
    progress = tl.get_progress(5)  # 0.5
    ```
    """
    
    def __init__(self, *, start_time: float = 0, end_time: float = 1):
        """Initialize Timeline.
        
        :param start_time: Timeline start time
        :param end_time: Timeline end time
        """
        if start_time >= end_time:
            raise ValueError(f"start_time ({start_time}) must be < end_time ({end_time})")
        
        super().__init__({
            "start_time": float(start_time),
            "end_time": float(end_time),
            "events": []
        })
        
        self.start_time = float(start_time)
        self.end_time = float(end_time)
        self.events: List[Dict[str, Any]] = []
    
    def add_event(self, time: float, label: str, data: Any = None) -> "Timeline":
        """Add event at specific time.
        
        :param time: Event time
        :param label: Event identifier
        :param data: Event data (optional)
        :return: Self (for chaining)
        """
        if not (self.start_time <= time <= self.end_time):
            raise ValueError(f"time ({time}) out of range [{self.start_time}, {self.end_time}]")
        
        self.events.append({
            "time": float(time),
            "label": str(label),
            "data": data
        })
        
        return self
    
    def remove_event(self, label: str) -> "Timeline":
        """Remove event by label.
        
        :param label: Event label
        :return: Self (for chaining)
        """
        self.events = [e for e in self.events if e["label"] != label]
        return self
    
    def get_event(self, label: str) -> Optional[Dict[str, Any]]:
        """Get event by label.
        
        :param label: Event label
        :return: Event dict or None
        """
        for e in self.events:
            if e["label"] == label:
                return e
        return None
    
    def events_at(self, time: float, tolerance: float = 0.001) -> List[Dict[str, Any]]:
        """Get events at specific time.
        
        :param time: Time to check
        :param tolerance: Time tolerance
        :return: List of matching events
        """
        return [e for e in self.events if abs(e["time"] - time) < tolerance]
    
    def events_between(self, t1: float, t2: float) -> List[Dict[str, Any]]:
        """Get events within time range.
        
        :param t1: Start time
        :param t2: End time
        :return: List of events
        """
        return [e for e in self.events if t1 <= e["time"] <= t2]
    
    def duration(self) -> float:
        """Get total duration."""
        return self.end_time - self.start_time
    
    def get_progress(self, current_time: float) -> float:
        """Get normalized progress [0, 1] at current time."""
        dur = self.duration()
        if dur == 0:
            return 0.0
        return (current_time - self.start_time) / dur
    
    def sort(self) -> "Timeline":
        """Sort events by time.
        
        :return: Self (for chaining)
        """
        self.events.sort(key=lambda e: e["time"])
        return self
    
    def reverse(self) -> "Timeline":
        """Reverse event order.
        
        :return: Self (for chaining)
        """
        self.events.reverse()
        return self
    
    def __str__(self) -> str:
        return f"Timeline({self.start_time}..{self.end_time}, {len(self.events)} events)"
    
    def __repr__(self) -> str:
        return f"Timeline(start_time={self.start_time}, end_time={self.end_time})"


class Dataset(DDM):
    """
    **Dataset**: DDM-based tabular data management with row/column operations.
    
    Manages structured data with rows and columns, supporting filtering,
    aggregation, and statistical analysis.
    
    **Attributes:**
    - `rows` (List[Dict]): Data rows
    - `columns` (List[str]): Column names
    
    **Methods:**
    - `add_row(data)`: Add row
    - `add_column(name, default)`: Add column
    - `remove_column(name)`: Remove column
    - `filter_rows(predicate)`: Filter rows
    - `map_column(name, transformer)`: Transform column
    - `sort_by(column, reverse)`: Sort by column
    - `group_by(column)`: Group by column value
    - `aggregate(column, func)`: Aggregate column values
    - `stats(column)`: Get column statistics
    - `to_csv()`: Export as CSV
    - `transpose()`: Transpose table
    
    **Example:**
    ```python
    ds = Dataset(columns=["name", "age", "city"])
    ds.add_row({"name": "Alice", "age": 30, "city": "NY"})
    ds.add_row({"name": "Bob", "age": 25, "city": "LA"})
    
    adults = ds.filter_rows(lambda row: row["age"] >= 25)
    avg_age = ds.aggregate("age", lambda vals: sum(vals) / len(vals))
    ```
    """
    
    def __init__(self, *, columns: List[str]):
        """Initialize Dataset.
        
        :param columns: Column names
        """
        super().__init__({"rows": [], "columns": list(columns)})
        
        self.rows: List[Dict[str, Any]] = []
        self.columns = list(columns)
    
    def add_row(self, data: Dict[str, Any]) -> "Dataset":
        """Add row of data.
        
        :param data: Dictionary with column names as keys
        :return: Self (for chaining)
        """
        row = {col: data.get(col) for col in self.columns}
        self.rows.append(row)
        return self
    
    def add_column(self, name: str, default: Any = None) -> "Dataset":
        """Add new column.
        
        :param name: Column name
        :param default: Default value for existing rows
        :return: Self (for chaining)
        """
        if name in self.columns:
            raise ValueError(f"Column '{name}' already exists")
        
        self.columns.append(name)
        for row in self.rows:
            row[name] = default
        
        return self
    
    def remove_column(self, name: str) -> "Dataset":
        """Remove column.
        
        :param name: Column name
        :return: Self (for chaining)
        """
        if name not in self.columns:
            raise ValueError(f"Column '{name}' not found")
        
        self.columns.remove(name)
        for row in self.rows:
            if name in row:
                del row[name]
        
        return self
    
    def filter_rows(self, predicate: callable) -> "Dataset":
        """Create new Dataset with filtered rows.
        
        :param predicate: Function returning True for rows to keep
        :return: New Dataset
        """
        filtered = Dataset(columns=self.columns)
        for row in self.rows:
            if predicate(row):
                filtered.add_row(row)
        return filtered
    
    def map_column(self, name: str, transformer: callable) -> "Dataset":
        """Apply transformation to column values.
        
        :param name: Column name
        :param transformer: Transformation function
        :return: New Dataset
        """
        if name not in self.columns:
            raise ValueError(f"Column '{name}' not found")
        
        new_ds = Dataset(columns=self.columns)
        for row in self.rows:
            new_row = row.copy()
            try:
                new_row[name] = transformer(row[name])
            except:
                pass
            new_ds.add_row(new_row)
        
        return new_ds
    
    def sort_by(self, column: str, reverse: bool = False) -> "Dataset":
        """Sort by column.
        
        :param column: Column name
        :param reverse: Descending order
        :return: New sorted Dataset
        """
        if column not in self.columns:
            raise ValueError(f"Column '{column}' not found")
        
        sorted_ds = Dataset(columns=self.columns)
        sorted_rows = sorted(self.rows, key=lambda r: r.get(column), reverse=reverse)
        
        for row in sorted_rows:
            sorted_ds.add_row(row)
        
        return sorted_ds
    
    def group_by(self, column: str) -> Dict[Any, "Dataset"]:
        """Group rows by column value.
        
        :param column: Column name
        :return: Dictionary mapping column value to Dataset
        """
        if column not in self.columns:
            raise ValueError(f"Column '{column}' not found")
        
        groups: Dict[Any, "Dataset"] = {}
        
        for row in self.rows:
            key = row.get(column)
            
            if key not in groups:
                groups[key] = Dataset(columns=self.columns)
            
            groups[key].add_row(row)
        
        return groups
    
    def aggregate(self, column: str, func: callable) -> Any:
        """Aggregate column values.
        
        :param column: Column name
        :param func: Aggregation function
        :return: Aggregation result
        
        Example:
            avg = ds.aggregate("age", lambda vals: sum(vals) / len(vals))
        """
        if column not in self.columns:
            raise ValueError(f"Column '{column}' not found")
        
        values = [row.get(column) for row in self.rows]
        return func(values)
    
    def stats(self, column: str) -> Dict[str, float]:
        """Get statistical summary of column.
        
        :param column: Column name
        :return: Dict with count, sum, mean, min, max, std
        """
        if column not in self.columns:
            raise ValueError(f"Column '{column}' not found")
        
        values = [v for v in [row.get(column) for row in self.rows] 
                 if v is not None and isinstance(v, (int, float))]
        
        if not values:
            return {"count": 0}
        
        count = len(values)
        total = sum(values)
        mean = total / count
        variance = sum((v - mean) ** 2 for v in values) / count if count > 0 else 0
        
        return {
            "count": count,
            "sum": total,
            "mean": mean,
            "min": min(values),
            "max": max(values),
            "variance": variance,
            "std": math.sqrt(variance)
        }
    
    def to_csv(self, sep: str = ",") -> str:
        """Export as CSV string.
        
        :param sep: Separator character
        :return: CSV string
        """
        lines = [sep.join(self.columns)]
        
        for row in self.rows:
            values = [str(row.get(col, "")) for col in self.columns]
            lines.append(sep.join(values))
        
        return "\n".join(lines)
    
    def transpose(self) -> "Dataset":
        """Transpose rows/columns.
        
        :return: New transposed Dataset
        """
        if not self.rows:
            return Dataset(columns=[])
        
        transposed = Dataset(columns=[f"row_{i}" for i in range(len(self.rows))])
        
        for col in self.columns:
            row_data = {}
            for i, row in enumerate(self.rows):
                row_data[f"row_{i}"] = row.get(col)
            transposed.add_row({**{"column": col}, **row_data})
        
        return transposed
    
    def __len__(self) -> int:
        """Get number of rows."""
        return len(self.rows)
    
    def __str__(self) -> str:
        return f"Dataset({len(self.rows)} rows × {len(self.columns)} columns)"
    
    def __repr__(self) -> str:
        return f"Dataset(columns={self.columns}, rows={len(self.rows)})"

class SmartCache(DDM):
    """
    **SmartCache (SC)**: Ultra-fast, memory-optimized template-based data completion system.
    
    **Purpose:**
    - Stores a default template dictionary
    - Quickly fills missing keys from raw data without modifying template values
    - Designed for high-frequency data processing with minimal overhead
    - Perfect for standardizing incoming data against a schema
    
    **Key Features:**
    - ⚡ O(n) completion - only processes missing keys
    - 🔒 Template protection - never modifies default values
    - 🧠 Memory-efficient - key hashing for fast lookups
    - 🔄 Batch processing - handle multiple records efficiently
    - 🎯 Smart merging - recursive nested dictionary support
    - 📊 Statistics tracking - monitor cache hits/misses
    
    **Attributes:**
    - `template` (Dict): Default template with all required keys
    - `key_set` (Set): Cached set of template keys (for O(1) lookup)
    - `stats` (Dict): Hit/miss statistics
    
    **Methods:**
    - `complete(raw_data)`: Fill missing keys from raw data
    - `complete_batch(records)`: Process multiple records
    - `update_template(new_template)`: Update template dynamically
    - `get_stats()`: Get cache statistics
    - `reset_stats()`: Reset statistics
    
    **Example:**
    ```python
    # Setup template
    default = {"name": "Unknown", "age": 0, "city": "Unknown"}
    sc = SmartCache(template=default)
    
    # Complete raw data (very fast!)
    raw1 = {"name": "Alice", "age": 30}
    completed1 = sc.complete(raw1)
    # → {"name": "Alice", "age": 30, "city": "Unknown"}
    
    # Batch processing
    records = [
        {"name": "Bob"},
        {"age": 25},
        {"name": "Charlie", "city": "NYC"}
    ]
    completed = sc.complete_batch(records)
    ```
    """
    
    def __init__(self, *, template: Dict[str, Any]):
        """Initialize SmartCache with template.
        
        :param template: Default template dictionary (frozen as default)
        :raises ValueError: If template is empty or not a dict
        """
        if not isinstance(template, dict):
            raise ValueError("Template must be a dictionary")
        if not template:
            raise ValueError("Template cannot be empty")
        
        # Deep copy template to protect original
        import copy
        template_copy = copy.deepcopy(template)
        
        super().__init__({
            "template": template_copy,
            "key_set": set(template_copy.keys()),
            "stats": {
                "completed": 0,
                "batches": 0,
                "total_keys_filled": 0,
                "total_records_processed": 0
            }
        })
        
        self.template = template_copy
        self.key_set = set(template_copy.keys())
        self.stats = {
            "completed": 0,
            "batches": 0,
            "total_keys_filled": 0,
            "total_records_processed": 0
        }
    
    def complete(self, raw_data: Dict[str, Any], recursive: bool = True) -> Dict[str, Any]:
        """Complete raw data with template defaults (ultra-fast).
        
        **Algorithm:**
        1. Start with template copy (guarantees all defaults present)
        2. Iterate only keys in raw_data
        3. Update only if key exists in template
        4. For dicts: recursively complete if recursive=True
        
        This ensures:
        - Template values are NEVER overwritten
        - Only missing keys from raw_data are added
        - No unnecessary iterations
        
        :param raw_data: Incomplete data dictionary
        :param recursive: Recursively handle nested dicts
        :return: Completed dictionary with all template keys
        
        Time Complexity: O(k) where k = number of raw_data keys
        Space Complexity: O(n) where n = template size
        """
        import copy
        
        # Start with template copy (fastest baseline)
        result = copy.copy(self.template)
        
        # Update only keys that exist in template
        # This ensures template values are preserved
        keys_filled = 0
        for key, value in raw_data.items():
            if key in self.key_set:
                # For nested dicts with recursive mode, complete recursively
                if recursive and isinstance(value, dict) and isinstance(self.template[key], dict):
                    result[key] = self.complete(value, recursive=True)
                else:
                    result[key] = value
                
                keys_filled += 1
        
        # Update statistics
        self.stats["completed"] += 1
        self.stats["total_keys_filled"] += keys_filled
        
        return result
    
    def complete_batch(self, records: List[Dict[str, Any]], recursive: bool = True) -> List[Dict[str, Any]]:
        """Process multiple records efficiently (batch mode).
        
        Optimized for processing many records at once.
        
        :param records: List of incomplete dictionaries
        :param recursive: Recursively handle nested structures
        :return: List of completed dictionaries
        
        Example:
            sc = SmartCache(template={"x": 0, "y": 0})
            completed = sc.complete_batch([{"x": 10}, {"y": 20}])
        """
        results = []
        
        for record in records:
            results.append(self.complete(record, recursive=recursive))
        
        self.stats["batches"] += 1
        self.stats["total_records_processed"] += len(records)
        
        return results
    
    def update_template(self, new_template: Dict[str, Any]) -> "SmartCache":
        """Update template dynamically.
        
        Useful for schema changes. Statistics are preserved.
        
        :param new_template: New template dictionary
        :return: Self (for chaining)
        """
        import copy
        
        if not isinstance(new_template, dict) or not new_template:
            raise ValueError("New template must be non-empty dict")
        
        self.template = copy.deepcopy(new_template)
        self.key_set = set(self.template.keys())
        
        return self
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        :return: Statistics dictionary
        
        Example:
            stats = sc.get_stats()
            # → {
            #    "completed": 100,
            #    "batches": 2,
            #    "total_keys_filled": 250,
            #    "total_records_processed": 50,
            #    "template_size": 5,
            #    "efficiency_percent": 83.33
            # }
        """
        total_possible = self.stats["total_records_processed"] * len(self.key_set)
        efficiency = 0.0
        
        if total_possible > 0:
            efficiency = (self.stats["total_keys_filled"] / total_possible) * 100
        
        return {
            **self.stats,
            "template_size": len(self.template),
            "template_keys": list(self.template.keys()),
            "efficiency_percent": efficiency
        }
    
    def reset_stats(self) -> "SmartCache":
        """Reset statistics counters.
        
        :return: Self (for chaining)
        """
        self.stats = {
            "completed": 0,
            "batches": 0,
            "total_keys_filled": 0,
            "total_records_processed": 0
        }
        return self
    
    def clone_with_template(self, new_template: Dict[str, Any]) -> "SmartCache":
        """Create new SmartCache with different template.
        
        Useful for template variations while keeping statistics separate.
        
        :param new_template: New template
        :return: New SmartCache instance
        """
        return SmartCache(template=new_template)
    
    def get_template(self) -> Dict[str, Any]:
        """Get current template (copy).
        
        :return: Copy of template
        """
        import copy
        return copy.deepcopy(self.template)
    
    def get_missing_keys(self, raw_data: Dict[str, Any]) -> List[str]:
        """Get list of missing keys in raw_data compared to template.
        
        :param raw_data: Data to check
        :return: List of keys that would be filled
        
        Example:
            missing = sc.get_missing_keys({"name": "Alice"})
            # → ["age", "city"]
        """
        return [key for key in self.key_set if key not in raw_data]
    
    def get_extra_keys(self, raw_data: Dict[str, Any]) -> List[str]:
        """Get list of extra keys in raw_data not in template.
        
        These keys will be preserved in output but not added to result.
        
        :param raw_data: Data to check
        :return: List of extra keys
        """
        return [key for key in raw_data.keys() if key not in self.key_set]
    
    def completion_report(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed report about what would be completed.
        
        :param raw_data: Data to analyze
        :return: Detailed report
        
        Example:
            report = sc.completion_report({"name": "Bob", "extra": 123})
            # → {
            #    "missing_keys": ["age", "city"],
            #    "extra_keys": ["extra"],
            #    "coverage_percent": 66.67,
            #    "will_be_completed": True
            # }
        """
        missing = self.get_missing_keys(raw_data)
        extra = self.get_extra_keys(raw_data)
        coverage = (len(self.key_set) - len(missing)) / len(self.key_set) * 100 if self.key_set else 0
        
        return {
            "missing_keys": missing,
            "extra_keys": extra,
            "missing_count": len(missing),
            "extra_count": len(extra),
            "coverage_percent": coverage,
            "will_be_completed": len(missing) > 0 or len(extra) > 0
        }
    
    def __str__(self) -> str:
        return f"SmartCache(template_keys={len(self.template)}, completed={self.stats['completed']})"
    
    def __repr__(self) -> str:
        keys_str = ", ".join(list(self.template.keys())[:3])
        if len(self.template) > 3:
            keys_str += f", +{len(self.template) - 3}"
        return f"SmartCache(template=[{keys_str}])"
    
    # Fast shortcuts for common operations
    
    def fill(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Alias for complete() - shorter name for frequent use."""
        return self.complete(raw_data)
    
    def fill_batch(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Alias for complete_batch() - shorter name."""
        return self.complete_batch(records)
    
    def report(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Alias for completion_report() - shorter name."""
        return self.completion_report(raw_data)

def create_smart_cache(template: Dict[str, Any]) -> SmartCache:
    """Create SmartCache instance with template.
    
    Convenience function for SmartCache instantiation.
    
    :param template: Template dictionary
    :return: New SmartCache instance
    """
    return SmartCache(template=template)


def fast_complete(template: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """One-shot fast completion (no cache overhead).
    
    Use when you only need to complete data once.
    For repeated use, use SmartCache directly.
    
    :param template: Template dictionary
    :param raw_data: Data to complete
    :return: Completed dictionary
    """
    import copy
    result = copy.copy(template)
    
    for key, value in raw_data.items():
        if key in template:
            result[key] = value
    
    return result


def batch_complete_fast(template: Dict[str, Any], records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Fast batch completion without cache.
    
    :param template: Template dictionary
    :param records: List of records to complete
    :return: List of completed dictionaries
    """
    return [fast_complete(template, record) for record in records]