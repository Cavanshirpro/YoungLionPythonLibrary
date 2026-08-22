"""YoungLion.function — file operations and application utilities.

The package combines YoungLion's dependency-free File facade with developer
utilities for subprocess execution, scheduling, logging, e-mail, transfers, text
processing, events, caching, rate limiting, retry/circuit-breaker resilience,
timing and terminal formatting.  File is assembled from a core filesystem class
and format/extra mixins so one object exposes common text, binary, JSON, CSV,
XML, YAML-like, INI, properties, script and archive workflows.

Public classes are also re-exported from ``YoungLion`` for convenient discovery.
"""
from ._base import Debugger, FileBase
from ._formats import FileFormatsMixin
from ._extra import FileExtraMixin
from ._utilities import (
    CommandResult, TaskInfo, ScriptRunner, TaskScheduler, Logger, EmailManager,
    FileTransferManager, TextProcessor, EventBus, TTLCache, RateLimiter, RetryPolicy,
    CircuitBreaker, Stopwatch, Terminal,
)

class File(FileExtraMixin, FileFormatsMixin, FileBase):
    """Unified YoungLion file facade.
    
    Overview
    --------
    ``File`` provides FileBase plus structured-format and extended file/script helpers in one dependency-free interface.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use this as the normal entry point for filesystem and file-format workflows.
    
    Inheritance
    -----------
    Base class(es): ``FileExtraMixin, FileFormatsMixin, FileBase``.
    
    Example::
    
        from YoungLion import File
    
        files = File()
        files.atomic_write_json("config.json", {"theme": "dark"})
        config = files.json_read("config.json", default={})
        digest = files.checksum("config.json", "sha256")
    """
    pass

__all__ = [
    "Debugger", "File", "CommandResult", "TaskInfo", "ScriptRunner", "TaskScheduler", "Logger",
    "EmailManager", "FileTransferManager", "TextProcessor", "EventBus", "TTLCache",
    "RateLimiter", "RetryPolicy", "CircuitBreaker", "Stopwatch", "Terminal",
]

# Preserve less-used legacy public names without overriding native replacements.
try:
    import importlib.util as _importlib_util
    from pathlib import Path as _Path
    _legacy_path = _Path(__file__).resolve().parent.parent / "function.py"
    if _legacy_path.exists():
        _spec = _importlib_util.spec_from_file_location("YoungLion._legacy_function", _legacy_path)
        if _spec and _spec.loader:
            _legacy = _importlib_util.module_from_spec(_spec)
            _spec.loader.exec_module(_legacy)
            for _name, _value in vars(_legacy).items():
                if not _name.startswith("_") and _name not in globals():
                    globals()[_name] = _value
                    __all__.append(_name)
except Exception:
    pass
