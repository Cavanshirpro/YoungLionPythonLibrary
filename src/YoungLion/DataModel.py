"""
DataModel.py

Dynamic Data Model (DDM) library module.

This module provides a base class `DDM` for structured hierarchical data.
Features:
- Recursive serialization to Python dictionaries via `.to_dict()`.
- Dynamic __str__ with pretty-printing and ANSI colors.
- Handles nested DDM objects with automatic indentation levels.
- Cross-platform ANSI color support (Windows, Linux, Mac).
- Easy to extend for application-specific data models.
"""

import os,sys
from typing import Any, Dict, List
from .Colors import Colors

# -------------------- ANSI Color Utilities --------------------

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
    DDM (Dynamic Data Model) is a base class for hierarchical structured data.
    
    Features:
    - Stores input dictionary data dynamically as attributes.
    - Supports nested DDM objects, lists, tuples, and dictionaries.
    - `.to_dict()` serializes recursively to a JSON-serializable dictionary.
    - Pretty-printing via `__str__`, with optional ANSI colors.
    - Indentation levels represent nested DDM depth.
    
    Usage Example:
    
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
    """

    def __init__(self, data: Dict[str, Any]):
        """
        Initialize a DDM instance.

        :param data: Dictionary containing the data to wrap. Keys will become attributes.
        """
        self._data: Dict[str, Any] = data  # Store original input
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
