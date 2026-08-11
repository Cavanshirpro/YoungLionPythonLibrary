from ._base import Debugger, FileBase
from ._formats import FileFormatsMixin
from ._extra import FileExtraMixin
from ._utilities import (
    CommandResult, TaskInfo, ScriptRunner, TaskScheduler, Logger, EmailManager,
    FileTransferManager, TextProcessor, EventBus, TTLCache, RateLimiter, RetryPolicy,
    CircuitBreaker, Stopwatch, Terminal,
)

class File(FileExtraMixin, FileFormatsMixin, FileBase):
    """Compatibility-preserving File API backed by native C++ hot paths."""
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
