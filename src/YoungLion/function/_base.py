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
    COLORS = {"RESET": "\033[0m", "INFO": "\033[1;94m", "DEBUG": "\033[1;36m", "SUCCESS": "\033[1;92m", "WARNING": "\033[1;93m", "ERROR": "\033[1;91m", "CRITICAL": "\033[1;41m", "CUSTOM": "\033[1;95m"}
    SYMBOLS = {"INFO": "ℹ", "DEBUG": "🐞", "SUCCESS": "✔", "WARNING": "⚠", "ERROR": "✖", "CRITICAL": "‼", "CUSTOM": "*"}

    def __init__(self, level: int = 0, DefaultSymbol: bool = False):
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

    def info(self, message: str): self._print("INFO", message)
    def debug(self, message: str): self._print("DEBUG", message)
    def success(self, message: str): self._print("SUCCESS", message)
    def warning(self, message: str): self._print("WARNING", message)
    def error(self, message: str): self._print("ERROR", message)
    def critical(self, message: str): self._print("CRITICAL", message)
    def custom(self, message: str, color_code: str = "\033[1;95m", symbol: str = "*"): self._print("CUSTOM", message, color_code, symbol)
    def set_level(self, level: int): self.level = int(level)




class FileBase:
    SUPPORTED_FORMATS = [".json", ".txt", ".log", ".pdf", ".xml", ".csv", ".yml", ".yaml", ".ini", ".properties", ".md", ".rtf", ".html", ".css", ".js", ".tex", ".py"]

    def __init__(self, filefolder: Optional[str] = None, debug: bool = False, debugger: Optional[Debugger] = None):
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
        return _native.get_info(self._validate_and_prepare_path(path))

    def rename_file(self, old_path: str, new_name: str) -> bool:
        old = Path(self._validate_and_prepare_path(old_path))
        if not old.is_file(): return False
        return bool(_native.rename_path(str(old), str(old.with_name(new_name))))

    def rename_folder(self, old_path: str, new_name: str) -> bool:
        old = Path(self._validate_and_prepare_path(old_path))
        if not old.is_dir(): return False
        return bool(_native.rename_path(str(old), str(old.with_name(new_name))))

    def create_shortcut(self, target_path: str, shortcut_path: str, description: str = "") -> bool:
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
        directory = path or self.filefolder
        if not directory:
            raise ValueError("Path or default filefolder must be specified.")
        return list(_native.list_dir(self._validate_and_prepare_path(directory)))

    def create_folder(self, folder_path: str) -> bool:
        return bool(_native.create_dir(self._validate_and_prepare_path(folder_path)))

    def copy_file(self, source: str, destination: str) -> bool:
        try: return bool(_native.copy_path(self._validate_and_prepare_path(source), self._validate_and_prepare_path(destination), False))
        except Exception: return False

    def copy_folder(self, source: str, destination: str) -> bool:
        try: return bool(_native.copy_path(self._validate_and_prepare_path(source), self._validate_and_prepare_path(destination), True))
        except Exception: return False

    def move_file(self, source: str, destination: str) -> bool:
        try: return bool(_native.move_path(self._validate_and_prepare_path(source), self._validate_and_prepare_path(destination)))
        except Exception: return False

    def move_folder(self, source: str, destination: str) -> bool:
        return self.move_file(source, destination)

    def delete_file(self, path: str) -> bool:
        try: return bool(_native.remove_path(self._validate_and_prepare_path(path), False))
        except Exception: return False

    def delete_folder(self, path: str) -> bool:
        try: return bool(_native.remove_path(self._validate_and_prepare_path(path), True))
        except Exception: return False

    def json_read(self, path: str, default: Optional[Union[dict, list]] = None) -> Union[dict, list]:
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
        if not isinstance(data, (dict, list)):
            raise TypeError("Data to be written must be a dictionary or list.")
        _native.json_write_file(self._validate_and_prepare_path(path), data, 4)

    def txt_read_str(self, path: str) -> str:
        fp = self._validate_and_prepare_path(path)
        if not os.path.exists(fp): _native.write_text(fp, "", False)
        return _native.read_text(fp)

    def txt_read_linear(self, path: str) -> Dict[str, str]:
        return {str(i): line.rstrip("\r\n") for i, line in enumerate(self.txt_read_str(path).splitlines(), 1)}

    def txt_write_str(self, path: str, content: str):
        _native.write_text(self._validate_and_prepare_path(path), str(content), False)

    def txt_write_linear(self, path: str, data: Mapping[int, str]):
        if not data:
            self.txt_write_str(path, "")
            return
        end = max(int(k) for k in data)
        self.txt_write_str(path, "\n".join(str(data.get(i, "")) for i in range(1, end + 1)) + "\n")

    def exists(self, path: str) -> bool:
        return os.path.exists(self._validate_and_prepare_path(path))

    def is_file(self, path: str) -> bool:
        return os.path.isfile(self._validate_and_prepare_path(path))

    def is_folder(self, path: str) -> bool:
        return os.path.isdir(self._validate_and_prepare_path(path))

    def file_size(self, path: str) -> int:
        info = self.get_info(path)
        if not info or not info.get("is_file"):
            raise FileNotFoundError(path)
        return int(info.get("size") or 0)

    def directory_size(self, path: Optional[str] = None, recursive: bool = True) -> int:
        target = path or self.filefolder
        if not target:
            raise ValueError("Path or default filefolder must be specified.")
        return int(_native.directory_size(self._validate_and_prepare_path(target), bool(recursive)))

    def read_bytes(self, path: str) -> bytes:
        return bytes(_native.read_bytes(self._validate_and_prepare_path(path)))

    def write_bytes(self, path: str, data: Union[bytes, bytearray, memoryview], append: bool = False) -> None:
        _native.write_bytes(self._validate_and_prepare_path(path), bytes(data), bool(append))

    def append_bytes(self, path: str, data: Union[bytes, bytearray, memoryview]) -> None:
        self.write_bytes(path, data, append=True)

    def touch(self, path: str) -> bool:
        return bool(_native.touch(self._validate_and_prepare_path(path)))

    def line_count(self, path: str) -> int:
        return int(_native.line_count(self._validate_and_prepare_path(path)))

    def compare_files(self, first: str, second: str) -> bool:
        return bool(_native.compare_files(self._validate_and_prepare_path(first), self._validate_and_prepare_path(second)))

    def checksum(self, path: str, algorithm: str = "sha256") -> str:
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
        target = Path(self._validate_and_prepare_path(path))
        self._atomic_replace_bytes(target, str(content).encode("utf-8"))

    def atomic_write_bytes(self, path: str, data: Union[bytes, bytearray, memoryview]) -> None:
        target = Path(self._validate_and_prepare_path(path))
        self._atomic_replace_bytes(target, bytes(data))

    def atomic_write_json(self, path: str, data: Union[dict, list], indent: int = 4) -> None:
        # Native JSON serialization preserves the same semantics as json_write;
        # the temporary file is then fsync'ed and atomically replaced.
        serialized = _native.json_dumps(data, indent=int(indent))
        self.atomic_write_text(path, serialized)

    def find_files(self, pattern: str = "*", path: Optional[str] = None, *, recursive: bool = True,
                   extensions: Optional[list[str]] = None, min_size: Optional[int] = None,
                   max_size: Optional[int] = None) -> list[str]:
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
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")
        with open(self._validate_and_prepare_path(path), "rb") as stream:
            while True:
                chunk = stream.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    def backup(self, path: str, destination: Optional[str] = None) -> str:
        source = Path(self._validate_and_prepare_path(path))
        if not source.exists():
            raise FileNotFoundError(path)
        if destination is None:
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            destination = str(source.with_name(f"{source.name}.{stamp}.bak"))
        dest = Path(self._validate_and_prepare_path(destination))
        _native.copy_path(str(source), str(dest), source.is_dir())
        return str(dest)

    def log_read(self, path: str) -> Dict[str, str]: return self.txt_read_linear(path)
    def log_write(self, path: str, content: str): _native.write_text(self._validate_and_prepare_path(path), str(content) + "\n", True)
    def log_write_entry(self, path: str, entry: str): self.log_write(path, f"{datetime.now():%Y-%m-%d %H:%M:%S} - {entry}")

