"""Core filesystem and debugging primitives used by YoungLion.function.

:class:`FileBase` provides normalized path handling plus dependency-free file and
directory operations, structured JSON/text helpers, binary I/O, checksums,
atomic writes, chunked reads, backups and simple log persistence.  :class:`Debugger`
is the lightweight console diagnostic helper retained for compatibility.

Methods generally raise the underlying Python/OSError family exception when the
requested operation cannot be completed; they do not silently hide filesystem
failures.  Atomic-write helpers are the preferred choice when replacing important
configuration or state files.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import fnmatch
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Union

from .. import _native

class Debugger:
    """Lightweight console debugger.
    
    Overview
    --------
    ``Debugger`` provides severity-filtered colored diagnostic messages and custom symbols.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for compatibility/simple scripts; Logger is preferred when persistent structured logging is needed.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    info, debug, success, warning, error, critical, custom, set_level.
    """
    COLORS = {"RESET": "\033[0m", "INFO": "\033[1;94m", "DEBUG": "\033[1;36m", "SUCCESS": "\033[1;92m", "WARNING": "\033[1;93m", "ERROR": "\033[1;91m", "CRITICAL": "\033[1;41m", "CUSTOM": "\033[1;95m"}
    SYMBOLS = {"INFO": "ℹ", "DEBUG": "🐞", "SUCCESS": "✔", "WARNING": "⚠", "ERROR": "✖", "CRITICAL": "‼", "CUSTOM": "*"}

    def __init__(self, level: int = 0, DefaultSymbol: bool = False):
        """Initialize a new Debugger instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`Debugger` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        level : int (default: ``0``)
            Minimum severity level name.
        DefaultSymbol : bool (default: ``False``)
            Whether the compatibility debugger uses its default status symbols.
        """
        self.level = int(level)
        self.DefaultSymbol = bool(DefaultSymbol)
        self.ansi = bool(getattr(sys.stdout, "isatty", lambda: False)())

    def _print(self, message_type: str, message: str, color: Optional[str] = None, symbol: Optional[str] = None) -> None:
        t = message_type.upper()
        prefix = "\t" * self.level
        sym = symbol if symbol is not None else (self.SYMBOLS.get(t, "") if self.DefaultSymbol else "")
        if self.ansi:
            c = color or self.COLORS.get(t, "")
            print(f"{prefix}[{c}{sym}{t}{self.COLORS['RESET']}]\t{message}")
        else:
            print(f"{prefix}[{t}]\t{message}")

    def info(self, message: str):
        """Emit an informational diagnostic message if enabled by the configured level.
        
        Details
        -------
        This method belongs to :class:`Debugger` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        message : str
            Human-readable message text.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        """
        self._print("INFO", message)
    def debug(self, message: str):
        """Emit a debug diagnostic message if enabled by the configured level.
        
        Details
        -------
        This method belongs to :class:`Debugger` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        message : str
            Human-readable message text.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        """
        self._print("DEBUG", message)
    def success(self, message: str):
        """Emit a success diagnostic message if enabled by the configured level.
        
        Details
        -------
        This method belongs to :class:`Debugger` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        message : str
            Human-readable message text.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        """
        self._print("SUCCESS", message)
    def warning(self, message: str):
        """Emit a warning diagnostic message if enabled by the configured level.
        
        Details
        -------
        This method belongs to :class:`Debugger` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        message : str
            Human-readable message text.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        """
        self._print("WARNING", message)
    def error(self, message: str):
        """Emit an error diagnostic message if enabled by the configured level.
        
        Details
        -------
        This method belongs to :class:`Debugger` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        message : str
            Human-readable message text.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        """
        self._print("ERROR", message)
    def critical(self, message: str):
        """Emit a critical diagnostic message if enabled by the configured level.
        
        Details
        -------
        This method belongs to :class:`Debugger` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        message : str
            Human-readable message text.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        """
        self._print("CRITICAL", message)
    def custom(self, message: str, color_code: str = "\033[1;95m", symbol: str = "*"):
        """Emit a diagnostic message with caller-provided color/symbol styling.
        
        Details
        -------
        This method belongs to :class:`Debugger` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        message : str
            Human-readable message text.
        color_code : str (default: ``'\x1b[1;95m'``)
            Value supplied for ``color_code`` according to the Debugger contract.
        symbol : str (default: ``'*'``)
            Value supplied for ``symbol`` according to the Debugger contract.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        """
        self._print("CUSTOM", message, color_code, symbol)
    def set_level(self, level: int):
        """Change the minimum severity level used by future diagnostic/logging calls.
        
        Details
        -------
        This method belongs to :class:`Debugger` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        level : int
            Minimum severity level name.
        """
        self.level = int(level)




class FileBase:
    """Core filesystem facade.
    
    Overview
    --------
    ``FileBase`` provides safe path resolution, file/directory management, text/binary/JSON I/O, checksums and atomic persistence.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use directly only for core behavior; the public File facade adds format and extra mixins.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    get_info, rename_file, rename_folder, create_shortcut, list_files_and_folders, create_folder, copy_file, copy_folder, move_file, move_folder, delete_file, delete_folder, json_read, json_write, txt_read_str, txt_read_linear ....
    """
    SUPPORTED_FORMATS = [".json", ".txt", ".log", ".pdf", ".xml", ".csv", ".yml", ".yaml", ".ini", ".properties", ".md", ".rtf", ".html", ".css", ".js", ".tex", ".py"]

    def __init__(self, filefolder: Optional[str] = None, debug: bool = False, debugger: Optional[Debugger] = None):
        """Initialize a new FileBase instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        filefolder : Optional[str] (default: ``None``)
            Optional base folder used for resolving relative paths.
        debug : bool (default: ``False``)
            Whether compatibility debug behavior is enabled.
        debugger : Optional[Debugger] (default: ``None``)
            Optional Debugger instance used by file operations.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        self.filefolder = filefolder
        self.debug = bool(debug)
        self.debugger = debugger or Debugger()

    def _validate_and_prepare_path(self, path: str) -> str:
        return _native.resolve_path(self.filefolder or "", os.fspath(path), True)

    @staticmethod
    def _recursive_update(target: Dict[str, Any], default: Mapping[str, Any]) -> Dict[str, Any]:
        for key, value in default.items():
            if isinstance(value, Mapping):
                current = target.get(key)
                if not isinstance(current, dict):
                    current = {}
                target[key] = FileBase._recursive_update(current, value)
            else:
                target.setdefault(key, value)
        return target

    def get_info(self, path: str) -> dict:
        """Return filesystem metadata for a resolved path.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        ``dict`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        return _native.get_info(self._validate_and_prepare_path(path))

    def rename_file(self, old_path: str, new_name: str) -> bool:
        """Rename a file while preserving its parent directory.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        old_path : str
            Existing filesystem or dotted-data path to move/rename from.
        new_name : str
            Value supplied for ``new_name`` according to the FileBase contract.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        old = Path(self._validate_and_prepare_path(old_path))
        if not old.is_file(): return False
        return bool(_native.rename_path(str(old), str(old.with_name(new_name))))

    def rename_folder(self, old_path: str, new_name: str) -> bool:
        """Rename a directory while preserving its parent directory.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        old_path : str
            Existing filesystem or dotted-data path to move/rename from.
        new_name : str
            Value supplied for ``new_name`` according to the FileBase contract.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        old = Path(self._validate_and_prepare_path(old_path))
        if not old.is_dir(): return False
        return bool(_native.rename_path(str(old), str(old.with_name(new_name))))

    def create_shortcut(self, target_path: str, shortcut_path: str, description: str = "") -> bool:
        """Create a platform-appropriate shortcut/link to a target path where supported.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        target_path : str
            Filesystem or dotted-data path used by this operation.
        shortcut_path : str
            Filesystem or dotted-data path used by this operation.
        description : str (default: ``''``)
            Value supplied for ``description`` according to the FileBase contract.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        target = os.path.abspath(target_path)
        shortcut = self._validate_and_prepare_path(shortcut_path)
        try:
            if os.name == "nt":
                safe_target = target.replace("'", "''")
                safe_shortcut = shortcut.replace("'", "''")
                safe_desc = description.replace("'", "''")
                ps = f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{safe_shortcut}');$s.TargetPath='{safe_target}';$s.Description='{safe_desc}';$s.Save()"
                subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                if os.path.lexists(shortcut): os.remove(shortcut)
                os.symlink(target, shortcut)
            return True
        except Exception as exc:
            if self.debug: self.debugger.error(str(exc))
            return False

    def list_files_and_folders(self, path: Optional[str] = None) -> list:
        """List immediate directory entries grouped or represented by the File API.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : Optional[str] (default: ``None``)
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        ``list`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        directory = path or self.filefolder
        if not directory:
            raise ValueError("Path or default filefolder must be specified.")
        return list(_native.list_dir(self._validate_and_prepare_path(directory)))

    def create_folder(self, folder_path: str) -> bool:
        """Create a directory path, including required parents.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        folder_path : str
            Filesystem or dotted-data path used by this operation.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        return bool(_native.create_dir(self._validate_and_prepare_path(folder_path)))

    def copy_file(self, source: str, destination: str) -> bool:
        """Copy a file to the requested destination.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        source : str
            Source path, collection or transfer identifier.
        destination : str
            Destination path or location.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        try: return bool(_native.copy_path(self._validate_and_prepare_path(source), self._validate_and_prepare_path(destination), False))
        except Exception: return False

    def copy_folder(self, source: str, destination: str) -> bool:
        """Recursively copy a directory tree to the requested destination.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        source : str
            Source path, collection or transfer identifier.
        destination : str
            Destination path or location.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        try: return bool(_native.copy_path(self._validate_and_prepare_path(source), self._validate_and_prepare_path(destination), True))
        except Exception: return False

    def move_file(self, source: str, destination: str) -> bool:
        """Move a file to the requested destination.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        source : str
            Source path, collection or transfer identifier.
        destination : str
            Destination path or location.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        try: return bool(_native.move_path(self._validate_and_prepare_path(source), self._validate_and_prepare_path(destination)))
        except Exception: return False

    def move_folder(self, source: str, destination: str) -> bool:
        """Move a directory tree to the requested destination.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        source : str
            Source path, collection or transfer identifier.
        destination : str
            Destination path or location.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        return self.move_file(source, destination)

    def delete_file(self, path: str) -> bool:
        """Delete the requested file.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        try: return bool(_native.remove_path(self._validate_and_prepare_path(path), False))
        except Exception: return False

    def delete_folder(self, path: str) -> bool:
        """Recursively delete the requested directory.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        try: return bool(_native.remove_path(self._validate_and_prepare_path(path), True))
        except Exception: return False

    def json_read(self, path: str, default: Optional[Union[dict, list]] = None) -> Union[dict, list]:
        """Read and decode a JSON file, returning a default according to the method contract when appropriate.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        default : Optional[Union[dict, list]] (default: ``None``)
            Fallback returned/used when the requested value or path is absent.
        
        Returns
        -------
        ``Union[dict, list]`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        fp = self._validate_and_prepare_path(path)
        if not os.path.exists(fp) or os.path.getsize(fp) == 0:
            data = default if default is not None else {}
            _native.json_write_file(fp, data, 4)
            return self._recursive_update(dict(data), default) if isinstance(data, dict) and isinstance(default, dict) else data
        try:
            data = _native.json_read_file(fp)
        except ValueError:
            data = default if default is not None else {}
        if isinstance(default, dict):
            if not isinstance(data, dict): data = {}
            return self._recursive_update(data, default)
        if isinstance(default, list) and not isinstance(data, list):
            return []
        return data

    def json_write(self, path: str, data: Union[dict, list]):
        """Serialize data as JSON and write it to the resolved path.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        data : Union[dict, list]
            Input mapping or record data used to initialize the object.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        if not isinstance(data, (dict, list)):
            raise TypeError("Data to be written must be a dictionary or list.")
        _native.json_write_file(self._validate_and_prepare_path(path), data, 4)

    def txt_read_str(self, path: str) -> str:
        """Read an entire text file as one string.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        fp = self._validate_and_prepare_path(path)
        if not os.path.exists(fp): _native.write_text(fp, "", False)
        return _native.read_text(fp)

    def txt_read_linear(self, path: str) -> Dict[str, str]:
        """Read a text file into a line-oriented representation.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        ``Dict[str, str]`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        return {str(i): line.rstrip("\r\n") for i, line in enumerate(self.txt_read_str(path).splitlines(), 1)}

    def txt_write_str(self, path: str, content: str):
        """Write one string to a text file.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        content : str
            Text/bytes/content payload to write, search or convert.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        _native.write_text(self._validate_and_prepare_path(path), str(content), False)

    def txt_write_linear(self, path: str, data: Mapping[int, str]):
        """Write an iterable of line values to a text file.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        data : Mapping[int, str]
            Input mapping or record data used to initialize the object.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        if not data:
            self.txt_write_str(path, "")
            return
        end = max(int(k) for k in data)
        self.txt_write_str(path, "\n".join(str(data.get(i, "")) for i in range(1, end + 1)) + "\n")

    def exists(self, path: str) -> bool:
        """Return whether any record satisfies the dotted-path comparison.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        ``True`` if at least one matching record exists.
        """
        return os.path.exists(self._validate_and_prepare_path(path))

    def is_file(self, path: str) -> bool:
        """Return whether the resolved path exists and is a regular file.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        """
        return os.path.isfile(self._validate_and_prepare_path(path))

    def is_folder(self, path: str) -> bool:
        """Return whether the resolved path exists and is a directory.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        """
        return os.path.isdir(self._validate_and_prepare_path(path))

    def file_size(self, path: str) -> int:
        """Return a file's size in bytes.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        info = self.get_info(path)
        if not info or not info.get("is_file"):
            raise FileNotFoundError(path)
        return int(info.get("size") or 0)

    def directory_size(self, path: Optional[str] = None, recursive: bool = True) -> int:
        """Calculate directory size, optionally recursing into descendants.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : Optional[str] (default: ``None``)
            Filesystem path or dotted data path, according to the owning API.
        recursive : bool (default: ``True``)
            Value supplied for ``recursive`` according to the FileBase contract.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        target = path or self.filefolder
        if not target:
            raise ValueError("Path or default filefolder must be specified.")
        return int(_native.directory_size(self._validate_and_prepare_path(target), bool(recursive)))

    def read_bytes(self, path: str) -> bytes:
        """Read a file as raw bytes.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        ``bytes`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        return bytes(_native.read_bytes(self._validate_and_prepare_path(path)))

    def write_bytes(self, path: str, data: Union[bytes, bytearray, memoryview], append: bool = False) -> None:
        """Write raw bytes, optionally appending instead of replacing.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        data : Union[bytes, bytearray, memoryview]
            Input mapping or record data used to initialize the object.
        append : bool (default: ``False``)
            Whether to append instead of replacing existing content.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        _native.write_bytes(self._validate_and_prepare_path(path), bytes(data), bool(append))

    def append_bytes(self, path: str, data: Union[bytes, bytearray, memoryview]) -> None:
        """Append raw bytes to an existing/new file.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        data : Union[bytes, bytearray, memoryview]
            Input mapping or record data used to initialize the object.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        self.write_bytes(path, data, append=True)

    def touch(self, path: str) -> bool:
        """Create the file if absent and/or update its modification time.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        return bool(_native.touch(self._validate_and_prepare_path(path)))

    def line_count(self, path: str) -> int:
        """Count logical lines in a text file.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        return int(_native.line_count(self._validate_and_prepare_path(path)))

    def compare_files(self, first: str, second: str) -> bool:
        """Compare two files for content equality using the implementation's efficient path.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        first : str
            Value supplied for ``first`` according to the FileBase contract.
        second : str
            Value supplied for ``second`` according to the FileBase contract.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        return bool(_native.compare_files(self._validate_and_prepare_path(first), self._validate_and_prepare_path(second)))

    def checksum(self, path: str, algorithm: str = "sha256") -> str:
        """Calculate a cryptographic/content digest using the requested hashlib algorithm.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        algorithm : str (default: ``'sha256'``)
            Algorithm name used for hashing, fuzzy matching or search ranking.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        algorithm = algorithm.lower().replace("-", "")
        fp = self._validate_and_prepare_path(path)
        if algorithm == "crc32":
            return str(_native.file_crc32(fp))
        import hashlib
        try:
            h = hashlib.new(algorithm)
        except ValueError as exc:
            raise ValueError(f"unsupported checksum algorithm: {algorithm}") from exc
        with open(fp, "rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    def head(self, path: str, lines: int = 10) -> list[str]:
        """Return the first requested number of lines from a text file.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        lines : int (default: ``10``)
            Value supplied for ``lines`` according to the FileBase contract.
        
        Returns
        -------
        ``list[str]`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        if lines <= 0:
            return []
        out = []
        with open(self._validate_and_prepare_path(path), "r", encoding="utf-8", errors="replace") as stream:
            for _ in range(lines):
                line = stream.readline()
                if not line:
                    break
                out.append(line.rstrip("\r\n"))
        return out

    def tail(self, path: str, lines: int = 10, block_size: int = 8192) -> list[str]:
        """Return the final requested number of lines from a text file.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        lines : int (default: ``10``)
            Value supplied for ``lines`` according to the FileBase contract.
        block_size : int (default: ``8192``)
            Value supplied for ``block_size`` according to the FileBase contract.
        
        Returns
        -------
        ``list[str]`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        if lines <= 0:
            return []
        fp = self._validate_and_prepare_path(path)
        with open(fp, "rb") as stream:
            stream.seek(0, os.SEEK_END); pos = stream.tell(); buf = bytearray()
            while pos > 0 and buf.count(b"\n") <= lines:
                step = min(block_size, pos); pos -= step; stream.seek(pos); buf[:0] = stream.read(step)
        return bytes(buf).decode("utf-8", "replace").splitlines()[-lines:]

    @staticmethod
    def _atomic_replace_bytes(target: Path, data: bytes) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        temp_name: Optional[str] = None
        try:
            with tempfile.NamedTemporaryFile(prefix=f".{target.name}.", suffix=".younglion.tmp", dir=target.parent, delete=False) as stream:
                temp_name = stream.name
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, target)
            temp_name = None
            # POSIX durability: persist the directory entry as well as the
            # file contents. This is best-effort because Windows and some
            # filesystems do not allow opening directories this way.
            if os.name != "nt":
                directory_fd = None
                try:
                    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                    directory_fd = os.open(str(target.parent), flags)
                    os.fsync(directory_fd)
                except OSError:
                    pass
                finally:
                    if directory_fd is not None:
                        os.close(directory_fd)
        finally:
            if temp_name is not None:
                try:
                    os.unlink(temp_name)
                except FileNotFoundError:
                    pass

    def atomic_write_text(self, path: str, content: str) -> None:
        """Replace a text file atomically using a same-directory temporary file and fsync/replace sequence where supported.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        content : str
            Text/bytes/content payload to write, search or convert.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        
        Notes
        -----
        Atomic replacement is strongest when source/temp/destination reside on the same filesystem. The implementation writes a unique same-directory temporary file, flushes/fsyncs where supported and then replaces the destination.
        """
        target = Path(self._validate_and_prepare_path(path))
        self._atomic_replace_bytes(target, str(content).encode("utf-8"))

    def atomic_write_bytes(self, path: str, data: Union[bytes, bytearray, memoryview]) -> None:
        """Replace a binary file atomically using a same-directory temporary file.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        data : Union[bytes, bytearray, memoryview]
            Input mapping or record data used to initialize the object.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        
        Notes
        -----
        Atomic replacement is strongest when source/temp/destination reside on the same filesystem.
        """
        target = Path(self._validate_and_prepare_path(path))
        self._atomic_replace_bytes(target, bytes(data))

    def atomic_write_json(self, path: str, data: Union[dict, list], indent: int = 4) -> None:
        # Native JSON serialization preserves the same semantics as json_write;
        # the temporary file is then fsync'ed and atomically replaced.
        """Serialize JSON and atomically replace the destination file.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        data : Union[dict, list]
            Input mapping or record data used to initialize the object.
        indent : int (default: ``4``)
            JSON indentation level; use the supported compact value for minimal output.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        
        Notes
        -----
        Serialization happens before replacement, reducing the chance that a partially written JSON document becomes the final destination.
        
        Example::
        
            File().atomic_write_json("settings.json", {"theme": "dark"})
        """
        serialized = _native.json_dumps(data, indent=int(indent))
        self.atomic_write_text(path, serialized)

    def find_files(self, pattern: str = "*", path: Optional[str] = None, *, recursive: bool = True,
                   extensions: Optional[list[str]] = None, min_size: Optional[int] = None,
                   max_size: Optional[int] = None) -> list[str]:
        """Discover files below a directory using name/extension/size filters.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        pattern : str (default: ``'*'``)
            Filename/pattern filter.
        path : Optional[str] (default: ``None``)
            Filesystem path or dotted data path, according to the owning API.
        recursive : bool (default: ``True``)
            Value supplied for ``recursive`` according to the FileBase contract.
        extensions : Optional[list[str]] (default: ``None``)
            Allowed file extensions, typically including leading dots.
        min_size : Optional[int] (default: ``None``)
            Optional minimum file/content size filter.
        max_size : Optional[int] (default: ``None``)
            Maximum number of cache entries retained.
        
        Returns
        -------
        ``list[str]`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        root_value = path or self.filefolder
        if not root_value:
            raise ValueError("Path or default filefolder must be specified.")
        root = Path(self._validate_and_prepare_path(root_value))
        normalized_extensions = None
        if extensions is not None:
            normalized_extensions = {ext.lower() if ext.startswith(".") else f".{ext.lower()}" for ext in extensions}
        iterator = root.rglob("*") if recursive else root.glob("*")
        results: list[str] = []
        for item in iterator:
            try:
                if not item.is_file() or not fnmatch.fnmatch(item.name, pattern):
                    continue
                if normalized_extensions is not None and item.suffix.lower() not in normalized_extensions:
                    continue
                size = item.stat().st_size
                if min_size is not None and size < min_size:
                    continue
                if max_size is not None and size > max_size:
                    continue
                results.append(str(item))
            except OSError:
                continue
        return results

    def read_chunks(self, path: str, chunk_size: int = 1024 * 1024):
        """Iterate a binary file in bounded chunks to avoid loading the entire file into memory.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        chunk_size : int (default: ``1024 * 1024``)
            Maximum number of bytes read per yielded chunk.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")
        with open(self._validate_and_prepare_path(path), "rb") as stream:
            while True:
                chunk = stream.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    def backup(self, path: str, destination: Optional[str] = None) -> str:
        """Create a backup copy of a file or directory at the requested destination.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        destination : Optional[str] (default: ``None``)
            Destination path or location.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        source = Path(self._validate_and_prepare_path(path))
        if not source.exists():
            raise FileNotFoundError(path)
        if destination is None:
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            destination = str(source.with_name(f"{source.name}.{stamp}.bak"))
        dest = Path(self._validate_and_prepare_path(destination))
        _native.copy_path(str(source), str(dest), source.is_dir())
        return str(dest)

    def log_read(self, path: str) -> Dict[str, str]:
        """Read a simple YoungLion log file representation.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        ``Dict[str, str]`` result described by the method semantics.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        return self.txt_read_linear(path)
    def log_write(self, path: str, content: str):
        """Append/write log text through the File facade.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        content : str
            Text/bytes/content payload to write, search or convert.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        _native.write_text(self._validate_and_prepare_path(path), str(content) + "\n", True)
    def log_write_entry(self, path: str, entry: str):
        """Persist one structured log entry in the File helper format.
        
        Details
        -------
        This method belongs to :class:`FileBase` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        entry : str
            Structured or textual log entry to persist.
        
        Raises
        ------
        OSError
            When the underlying filesystem operation fails; format/parse operations may additionally raise their normal decoding/value errors.
        """
        self.log_write(path, f"{datetime.now():%Y-%m-%d %H:%M:%S} - {entry}")

