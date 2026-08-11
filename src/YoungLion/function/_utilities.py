from __future__ import annotations

import ftplib
import imaplib
import mimetypes
import os
import re
import shutil
import smtplib
import subprocess
import threading
import time
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Union

from .. import _native


@dataclass(slots=True)
class CommandResult:
    args: tuple[str, ...]
    returncode: int
    stdout: str = ""
    stderr: str = ""
    duration: float = 0.0

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def check(self) -> "CommandResult":
        if not self.ok:
            raise subprocess.CalledProcessError(self.returncode, self.args, self.stdout, self.stderr)
        return self


class ScriptRunner:
    """Cross-platform subprocess/script runner with structured results."""

    INTERPRETERS = {
        ".py": lambda: os.environ.get("PYTHON", os.sys.executable),
        ".js": lambda: "node",
        ".mjs": lambda: "node",
        ".sh": lambda: "bash",
        ".ps1": lambda: "powershell" if os.name == "nt" else "pwsh",
        ".bat": lambda: "cmd",
        ".cmd": lambda: "cmd",
    }

    def __init__(self, default_interpreter: str = "node"):
        self.default_interpreter = default_interpreter

    def set_default_interpreter(self, interpreter: str):
        self.default_interpreter = interpreter
        return self

    def _validate_path(self, path: str) -> str:
        p = os.path.abspath(path)
        if not os.path.isfile(p):
            raise FileNotFoundError(path)
        return p

    def detect_interpreter(self, path: str) -> str:
        factory = self.INTERPRETERS.get(Path(path).suffix.lower())
        return factory() if factory else self.default_interpreter

    def run(self, command: Sequence[Union[str, os.PathLike[str]]], *, cwd: Optional[str] = None,
            env: Optional[Mapping[str, str]] = None, timeout: Optional[float] = None,
            input_text: Optional[str] = None, check: bool = False, capture_output: bool = True) -> CommandResult:
        args = tuple(os.fspath(x) for x in command)
        merged_env = os.environ.copy()
        if env: merged_env.update({str(k): str(v) for k, v in env.items()})
        start = time.perf_counter()
        proc = subprocess.run(
            args, cwd=cwd, env=merged_env, input=input_text, text=True,
            capture_output=capture_output, timeout=timeout, check=False,
        )
        result = CommandResult(args, proc.returncode, proc.stdout or "", proc.stderr or "", time.perf_counter() - start)
        return result.check() if check else result

    def run_async(self, command: Sequence[Union[str, os.PathLike[str]]], *, cwd: Optional[str] = None,
                  env: Optional[Mapping[str, str]] = None, stdout: Any = subprocess.PIPE,
                  stderr: Any = subprocess.PIPE) -> subprocess.Popen[str]:
        merged_env = os.environ.copy()
        if env: merged_env.update({str(k): str(v) for k, v in env.items()})
        return subprocess.Popen([os.fspath(x) for x in command], cwd=cwd, env=merged_env, text=True, stdout=stdout, stderr=stderr)

    def run_script(self, path: str, interpreter: Optional[str] = None, terminal: bool = False,
                   inputs: Optional[Union[str, Sequence[str]]] = None, output: bool = True,
                   *, cwd: Optional[str] = None, env: Optional[Mapping[str, str]] = None,
                   timeout: Optional[float] = None, check: bool = True):
        p = self._validate_path(path)
        interp = interpreter or self.detect_interpreter(p)
        values = [inputs] if isinstance(inputs, str) else list(inputs or [])
        if Path(p).suffix.lower() in {".bat", ".cmd"} and interp.lower() == "cmd":
            cmd = [interp, "/c", p, *(str(x) for x in values)]
        else:
            cmd = [interp, p, *(str(x) for x in values)]
        if terminal:
            if os.name == "nt":
                subprocess.Popen(["cmd", "/c", "start", "", *cmd], cwd=cwd, env=dict(os.environ, **dict(env or {})))
                return None
            for terminal_bin, flags in (("x-terminal-emulator", ["-e"]), ("gnome-terminal", ["--"]), ("xterm", ["-e"])):
                if shutil.which(terminal_bin):
                    subprocess.Popen([terminal_bin, *flags, *cmd], cwd=cwd)
                    return None
            raise RuntimeError("No supported terminal emulator found")
        result = self.run(cmd, cwd=cwd, env=env, timeout=timeout, check=check, capture_output=output)
        return result.stdout if output else None


@dataclass(slots=True)
class TaskInfo:
    id: str
    state: str
    created_at: float
    next_run: float
    repeat: Optional[float]
    priority: int
    runs: int = 0
    failures: int = 0
    last_result: Any = None
    last_error: Optional[BaseException] = None


class TaskScheduler:
    """Lightweight in-process scheduler with pause/resume/repeat/retry support."""

    def __init__(self):
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._counter = 0
        self._lock = threading.RLock()
        self._closed = False

    def schedule_task(self, func: Callable[..., Any], delay: float = 0.0, repeat: Optional[float] = None,
                      priority: int = 0, args: Sequence[Any] = (), kwargs: Optional[Dict[str, Any]] = None,
                      *, retries: int = 0, retry_delay: float = 0.0, task_id: Optional[str] = None) -> str:
        if self._closed: raise RuntimeError("scheduler is shut down")
        if repeat is not None and repeat <= 0: raise ValueError("repeat must be positive")
        with self._lock:
            self._counter += 1
            ident = task_id or f"task-{self._counter}"
            if ident in self._tasks: raise KeyError(f"task id already exists: {ident}")
            now = time.time()
            task = {
                "id": ident, "func": func, "args": tuple(args), "kwargs": dict(kwargs or {}),
                "repeat": repeat, "priority": int(priority), "state": "queued", "timer": None,
                "created_at": now, "next_run": now + max(0.0, float(delay)), "runs": 0,
                "failures": 0, "last_result": None, "last_error": None,
                "retries": max(0, int(retries)), "retry_delay": max(0.0, float(retry_delay)),
                "remaining_retries": max(0, int(retries)),
            }
            self._tasks[ident] = task
            self._arm(task, max(0.0, float(delay)))
            return ident

    def schedule_at(self, when: datetime, func: Callable[..., Any], **kwargs: Any) -> str:
        return self.schedule_task(func, delay=max(0.0, (when - datetime.now(tz=when.tzinfo)).total_seconds()), **kwargs)

    def _arm(self, task: Dict[str, Any], delay: float) -> None:
        task["next_run"] = time.time() + delay
        timer = threading.Timer(delay, self._execute, args=(task["id"],))
        timer.daemon = True; task["timer"] = timer; timer.start()

    def _execute(self, task_id: str) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task or task["state"] in {"cancelled", "paused"} or self._closed: return
            task["state"] = "running"
        try:
            result = task["func"](*task["args"], **task["kwargs"])
        except BaseException as exc:
            with self._lock:
                task["failures"] += 1; task["last_error"] = exc
                if task["remaining_retries"] > 0 and task["state"] != "cancelled":
                    task["remaining_retries"] -= 1; task["state"] = "queued"; self._arm(task, task["retry_delay"]); return
                task["state"] = "failed"
                task["remaining_retries"] = task["retries"]
            return
        with self._lock:
            task["runs"] += 1; task["last_result"] = result; task["last_error"] = None; task["remaining_retries"] = task["retries"]
            if task["repeat"] and task["state"] != "cancelled" and not self._closed:
                task["state"] = "queued"; self._arm(task, float(task["repeat"]))
            elif task["state"] != "cancelled": task["state"] = "completed"

    def run_now(self, task_id: str) -> bool:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task or task["state"] == "cancelled": return False
            timer = task.get("timer")
            if timer: timer.cancel()
            task["state"] = "queued"
        thread = threading.Thread(target=self._execute, args=(task_id,), daemon=True); thread.start(); return True

    def cancel_task(self, task_id: str) -> bool:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task: return False
            task["state"] = "cancelled"; timer = task.get("timer")
            if timer: timer.cancel()
            return True

    def pause_task(self, task_id: str) -> bool:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task or task["state"] in {"completed", "cancelled", "failed"}: return False
            task["remaining_delay"] = max(0.0, task.get("next_run", time.time()) - time.time())
            task["state"] = "paused"; timer = task.get("timer")
            if timer: timer.cancel()
            return True

    def resume_task(self, task_id: str) -> bool:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task or task["state"] != "paused": return False
            task["state"] = "queued"; self._arm(task, float(task.pop("remaining_delay", 0.0))); return True

    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task: return None
            return TaskInfo(task["id"], task["state"], task["created_at"], task["next_run"], task["repeat"], task["priority"], task["runs"], task["failures"], task["last_result"], task["last_error"])

    def list_tasks(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [{k: v for k, v in task.items() if k not in {"timer", "func"}} for task in self._tasks.values()]

    def wait(self, task_id: str, timeout: Optional[float] = None, poll_interval: float = 0.01) -> Optional[TaskInfo]:
        deadline = None if timeout is None else time.monotonic() + timeout
        while deadline is None or time.monotonic() < deadline:
            info = self.get_task(task_id)
            if info is None or info.state in {"completed", "failed", "cancelled"}: return info
            time.sleep(poll_interval)
        return self.get_task(task_id)

    def shutdown(self, cancel_pending: bool = True) -> None:
        with self._lock:
            self._closed = True
            if cancel_pending:
                for task in self._tasks.values():
                    timer = task.get("timer")
                    if timer: timer.cancel()
                    if task["state"] not in {"completed", "failed"}: task["state"] = "cancelled"


class Logger:
    LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}

    def __init__(self, log_file: str = "app.log", log_level: str = "INFO", *, console: bool = True,
                 max_bytes: int = 0, backup_count: int = 5):
        self.log_file = os.path.abspath(log_file); self.console = bool(console)
        self.max_bytes = max(0, int(max_bytes)); self.backup_count = max(0, int(backup_count))
        self._lock = threading.RLock(); self._context: Dict[str, Any] = {}; self.set_log_level(log_level)

    def set_log_level(self, level: str):
        level = level.upper()
        if level not in self.LEVELS: raise ValueError(f"invalid log level: {level}")
        self.log_level = level; return self

    def bind(self, **context: Any) -> "Logger":
        child = Logger(self.log_file, self.log_level, console=self.console, max_bytes=self.max_bytes, backup_count=self.backup_count)
        child._context = {**self._context, **context}; return child

    def _rotate(self, incoming: int) -> None:
        if not self.max_bytes or not os.path.exists(self.log_file): return
        try: size = os.path.getsize(self.log_file)
        except OSError: return
        if size + incoming <= self.max_bytes: return
        if self.backup_count <= 0:
            Path(self.log_file).write_text("", encoding="utf-8"); return
        oldest = f"{self.log_file}.{self.backup_count}"
        if os.path.exists(oldest): os.remove(oldest)
        for i in range(self.backup_count - 1, 0, -1):
            src, dst = f"{self.log_file}.{i}", f"{self.log_file}.{i+1}"
            if os.path.exists(src): os.replace(src, dst)
        if os.path.exists(self.log_file): os.replace(self.log_file, f"{self.log_file}.1")

    def _log(self, level: str, message: str, **fields: Any):
        if self.LEVELS[level] < self.LEVELS[self.log_level]: return
        merged = {**self._context, **fields}
        suffix = "" if not merged else " " + _native.json_dumps(merged, indent=-1)
        line = f"[{datetime.now().astimezone().isoformat(timespec='seconds')}] [{level}] {message}{suffix}"
        encoded = (line + "\n").encode("utf-8")
        with self._lock:
            self._rotate(len(encoded))
            if self.console: print(line)
            _native.write_text(self.log_file, line + "\n", True)

    def log_debug(self, message: str, **fields: Any): self._log("DEBUG", message, **fields)
    def log_info(self, message: str, **fields: Any): self._log("INFO", message, **fields)
    def log_warning(self, message: str, **fields: Any): self._log("WARNING", message, **fields)
    def log_error(self, message: str, **fields: Any): self._log("ERROR", message, **fields)
    def log_critical(self, message: str, **fields: Any): self._log("CRITICAL", message, **fields)
    debug = log_debug; info = log_info; warning = log_warning; error = log_error; critical = log_critical


class EmailManager:
    def __init__(self, smtp_server: str, smtp_port: int, email_address: str, email_password: str,
                 imap_server: Optional[str] = None, *, use_ssl: bool = False, starttls: bool = True):
        self.smtp_server = smtp_server; self.smtp_port = int(smtp_port); self.email_address = email_address
        self.email_password = email_password; self.imap_server = imap_server; self.use_ssl = bool(use_ssl); self.starttls = bool(starttls)

    def build_email(self, to: Union[str, Sequence[str]], subject: str, body: str, *, html: Optional[str] = None,
                    cc: Union[str, Sequence[str], None] = None, bcc: Union[str, Sequence[str], None] = None,
                    attachments: Iterable[Union[str, os.PathLike[str]]] = ()) -> EmailMessage:
        def addresses(value): return [value] if isinstance(value, str) else list(value or [])
        msg = EmailMessage(); msg["From"] = self.email_address; msg["To"] = ", ".join(addresses(to)); msg["Subject"] = subject
        if cc: msg["Cc"] = ", ".join(addresses(cc))
        msg.set_content(body)
        if html is not None: msg.add_alternative(html, subtype="html")
        for attachment in attachments:
            path = Path(attachment); mime, _ = mimetypes.guess_type(path.name); maintype, subtype = (mime or "application/octet-stream").split("/", 1)
            msg.add_attachment(path.read_bytes(), maintype=maintype, subtype=subtype, filename=path.name)
        # BCC intentionally does not become a visible header.
        msg._younglion_bcc = addresses(bcc)  # type: ignore[attr-defined]
        return msg

    def send_message(self, message: EmailMessage) -> bool:
        recipients = []
        for header in ("To", "Cc"):
            if message.get(header): recipients.extend(x.strip() for x in message[header].split(",") if x.strip())
        recipients.extend(getattr(message, "_younglion_bcc", []))
        smtp_cls = smtplib.SMTP_SSL if self.use_ssl else smtplib.SMTP
        with smtp_cls(self.smtp_server, self.smtp_port, timeout=30) as smtp:
            if not self.use_ssl and self.starttls: smtp.starttls()
            if self.email_address: smtp.login(self.email_address, self.email_password)
            smtp.send_message(message, to_addrs=recipients or None)
        return True

    def send_email(self, to: Union[str, Sequence[str]], subject: str, body: str, **kwargs: Any) -> bool:
        return self.send_message(self.build_email(to, subject, body, **kwargs))

    def schedule_email(self, to: Union[str, Sequence[str]], subject: str, body: str, send_time: datetime, **kwargs: Any):
        delay = max(0.0, (send_time - datetime.now(tz=send_time.tzinfo)).total_seconds())
        timer = threading.Timer(delay, self.send_email, args=(to, subject, body), kwargs=kwargs); timer.daemon = True; timer.start(); return timer

    def check_inbox(self, user: Optional[str] = None, limit: int = 10, mailbox: str = "INBOX"):
        server = self.imap_server or re.sub(r"^smtp\.", "imap.", self.smtp_server)
        with imaplib.IMAP4_SSL(server) as imap:
            imap.login(user or self.email_address, self.email_password); imap.select(mailbox); _, data = imap.search(None, "ALL")
            ids = data[0].split()[-max(0, limit):]; result = []
            for msg_id in reversed(ids):
                _, parts = imap.fetch(msg_id, "(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE MESSAGE-ID)])")
                raw = parts[0][1].decode("utf-8", "replace") if parts and isinstance(parts[0], tuple) else ""
                def field(name: str):
                    match = re.search(rf"^{re.escape(name)}:\s*(.*)$", raw, re.M | re.I); return match.group(1).strip() if match else ""
                result.append({"id": msg_id.decode(), "subject": field("Subject"), "from": field("From"), "date": field("Date"), "message_id": field("Message-ID")})
            return result


class FileTransferManager:
    """Dependency-free local/FTP transfer manager with status/progress tracking."""

    def __init__(self):
        self.transfer_status: Dict[str, str] = {}; self.transfer_progress: Dict[str, int] = {}; self._counter = 0; self._lock = threading.RLock()

    def _id(self) -> str:
        with self._lock: self._counter += 1; return f"transfer-{self._counter}"

    def _set_progress(self, tid: str, transferred: int, total: int, callback: Optional[Callable[[int, int], Any]]) -> None:
        percent = 100 if total <= 0 else min(100, int(transferred * 100 / total)); self.transfer_progress[tid] = percent
        if callback: callback(transferred, total)

    def upload(self, file_path: str, destination: str, protocol: str = "ftp", host: str = "", username: str = "",
               password: str = "", port: Optional[int] = None, *, progress: Optional[Callable[[int, int], Any]] = None) -> str:
        tid = self._id(); self.transfer_status[tid] = "running"; self.transfer_progress[tid] = 0
        try:
            if protocol.lower() in {"local", "file"}:
                shutil.copy2(file_path, destination); self._set_progress(tid, os.path.getsize(file_path), os.path.getsize(file_path), progress)
            elif protocol.lower() == "ftp":
                total = os.path.getsize(file_path); sent = 0
                with ftplib.FTP() as ftp, open(file_path, "rb") as f:
                    ftp.connect(host, port or 21, timeout=30); ftp.login(username, password)
                    def cb(chunk: bytes):
                        nonlocal sent; sent += len(chunk); self._set_progress(tid, sent, total, progress)
                    ftp.storbinary(f"STOR {destination}", f, callback=cb)
            else:
                raise RuntimeError("SFTP intentionally has no hidden Python dependency; use system OpenSSH/libssh2 integration in a future native backend.")
            self.transfer_status[tid] = "completed"; self.transfer_progress[tid] = 100
        except Exception:
            self.transfer_status[tid] = "failed"; raise
        return tid

    def download(self, source: str, destination: str, protocol: str = "ftp", host: str = "", username: str = "",
                 password: str = "", port: Optional[int] = None, *, progress: Optional[Callable[[int, int], Any]] = None) -> str:
        tid = self._id(); self.transfer_status[tid] = "running"; self.transfer_progress[tid] = 0
        try:
            if protocol.lower() in {"local", "file"}:
                shutil.copy2(source, destination); size = os.path.getsize(destination); self._set_progress(tid, size, size, progress)
            elif protocol.lower() == "ftp":
                received = 0
                with ftplib.FTP() as ftp, open(destination, "wb") as f:
                    ftp.connect(host, port or 21, timeout=30); ftp.login(username, password)
                    try: total = int(ftp.size(source) or 0)
                    except Exception: total = 0
                    def cb(chunk: bytes):
                        nonlocal received; f.write(chunk); received += len(chunk); self._set_progress(tid, received, total, progress)
                    ftp.retrbinary(f"RETR {source}", cb)
            else:
                raise RuntimeError("SFTP intentionally has no hidden Python dependency; use system OpenSSH/libssh2 integration in a future native backend.")
            self.transfer_status[tid] = "completed"; self.transfer_progress[tid] = 100
        except Exception:
            self.transfer_status[tid] = "failed"; raise
        return tid

    def get_status(self, transfer_id: str) -> Optional[str]: return self.transfer_status.get(transfer_id)
    def get_progress(self, transfer_id: str) -> Optional[int]: return self.transfer_progress.get(transfer_id)


class TextProcessor:
    """Zero-dependency text analysis and normalization helper."""

    def __init__(self, text: str = ""): self.text = text
    def set_text(self, text: str) -> "TextProcessor": self.text = str(text); return self
    def _value(self, text: Optional[str]) -> str: return text if text is not None else self.text
    def words(self, text: Optional[str] = None) -> List[str]: return re.findall(r"\b\w+(?:['-]\w+)*\b", self._value(text), re.UNICODE)
    def sentences(self, text: Optional[str] = None) -> List[str]: return [x.strip() for x in re.split(r"(?<=[.!?])\s+", self._value(text)) if x.strip()]
    def word_count(self, text: Optional[str] = None) -> int: return len(self.words(text))
    def sentence_count(self, text: Optional[str] = None) -> int: return len(self.sentences(text))
    def line_count(self, text: Optional[str] = None) -> int: return len(self._value(text).splitlines())
    def character_count(self, text: Optional[str] = None, include_spaces: bool = True) -> int:
        value = self._value(text); return len(value) if include_spaces else len(re.sub(r"\s", "", value))
    def keyword_search(self, keyword: str, text: Optional[str] = None, case_sensitive: bool = False) -> List[int]:
        value = self._value(text); return list(_native.find_all(value if case_sensitive else value.casefold(), keyword if case_sensitive else keyword.casefold()))
    def replace(self, old: str, new: str, text: Optional[str] = None) -> str: return self._value(text).replace(old, new)
    def normalize_whitespace(self, text: Optional[str] = None) -> str: return re.sub(r"\s+", " ", self._value(text)).strip()
    def most_frequent_words(self, n: int = 10, text: Optional[str] = None): return Counter(word.casefold() for word in self.words(text)).most_common(n)
    def ngrams(self, n: int = 2, text: Optional[str] = None) -> List[tuple[str, ...]]:
        if n <= 0: raise ValueError("n must be positive")
        words = self.words(text); return [tuple(words[i:i+n]) for i in range(max(0, len(words)-n+1))]
    def extract_emails(self, text: Optional[str] = None) -> List[str]: return re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", self._value(text))
    def extract_urls(self, text: Optional[str] = None) -> List[str]: return re.findall(r"https?://[^\s<>'\"]+", self._value(text))
    def summarize(self, sentences: int = 3, text: Optional[str] = None) -> str: return " ".join(self.sentences(text)[:max(0, sentences)])
    def similarity(self, other: str, text: Optional[str] = None, algorithm: str = "hybrid") -> float:
        a, b = self._value(text), str(other); algo = algorithm.lower()
        if algo in {"jaro", "jaro_winkler"}: return float(_native.jaro_winkler(a.casefold(), b.casefold()))
        if algo in {"trigram", "dice"}: return float(_native.trigram_similarity(a.casefold(), b.casefold()))
        distance = _native.damerau_levenshtein(a.casefold(), b.casefold()) if algo in {"damerau", "hybrid"} else _native.levenshtein(a.casefold(), b.casefold())
        lev = max(0.0, 1.0 - distance / max(len(a), len(b), 1))
        if algo == "hybrid": return 0.4 * lev + 0.35 * float(_native.jaro_winkler(a.casefold(), b.casefold())) + 0.25 * float(_native.trigram_similarity(a.casefold(), b.casefold()))
        return lev
    def readability_score(self, text: Optional[str] = None) -> float:
        value = self._value(text); words = self.words(value); sents = max(1, self.sentence_count(value)); vowels = re.compile(r"[aeiouyAEIOUY]+")
        syllables = max(1, sum(max(1, len(vowels.findall(w))) for w in words)); wc = max(1, len(words)); return 206.835 - 1.015 * (wc / sents) - 84.6 * (syllables / wc)
    def stats(self, text: Optional[str] = None) -> Dict[str, Any]:
        value = self._value(text); words = self.words(value)
        return {"characters": len(value), "characters_no_spaces": len(re.sub(r"\s", "", value)), "words": len(words), "unique_words": len({w.casefold() for w in words}), "sentences": self.sentence_count(value), "lines": self.line_count(value), "readability": self.readability_score(value)}

# ---------------------------------------------------------------------------
# General application infrastructure (zero third-party runtime dependencies)
# ---------------------------------------------------------------------------

_UTIL_MISSING = object()


class EventBus:
    """Thread-safe in-process event dispatcher with priority and one-shot listeners."""

    def __init__(self):
        self._listeners: Dict[str, List[tuple[int, str, Callable[..., Any], bool]]] = {}
        self._lock = threading.RLock()

    def subscribe(self, event: str, callback: Callable[..., Any], *, once: bool = False, priority: int = 0) -> str:
        if not callable(callback):
            raise TypeError("callback must be callable")
        token = uuid.uuid4().hex
        with self._lock:
            bucket = self._listeners.setdefault(str(event), [])
            bucket.append((int(priority), token, callback, bool(once)))
            bucket.sort(key=lambda row: row[0], reverse=True)
        return token

    on = subscribe

    def once(self, event: str, callback: Callable[..., Any], *, priority: int = 0) -> str:
        return self.subscribe(event, callback, once=True, priority=priority)

    def unsubscribe(self, token: str) -> bool:
        with self._lock:
            for event, bucket in list(self._listeners.items()):
                for idx, row in enumerate(bucket):
                    if row[1] == token:
                        del bucket[idx]
                        if not bucket:
                            self._listeners.pop(event, None)
                        return True
        return False

    off = unsubscribe

    def emit(self, event: str, *args: Any, **kwargs: Any) -> List[Any]:
        with self._lock:
            listeners = list(self._listeners.get(str(event), ()))
        results = []
        once_tokens = []
        for _, token, callback, one_shot in listeners:
            results.append(callback(*args, **kwargs))
            if one_shot:
                once_tokens.append(token)
        for token in once_tokens:
            self.unsubscribe(token)
        return results

    def listener_count(self, event: Optional[str] = None) -> int:
        with self._lock:
            if event is None:
                return sum(len(v) for v in self._listeners.values())
            return len(self._listeners.get(str(event), ()))

    def clear(self, event: Optional[str] = None) -> None:
        with self._lock:
            if event is None:
                self._listeners.clear()
            else:
                self._listeners.pop(str(event), None)


class TTLCache:
    """Small thread-safe TTL + LRU cache for application-level memoization."""

    def __init__(self, max_size: int = 1024, default_ttl: Optional[float] = 300.0):
        from collections import OrderedDict
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        self.max_size = int(max_size)
        self.default_ttl = default_ttl
        self._items = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    @staticmethod
    def _deadline(ttl: Optional[float]) -> Optional[float]:
        if ttl is None:
            return None
        if ttl < 0:
            return time.monotonic() - 1
        return time.monotonic() + float(ttl)

    def set(self, key: Any, value: Any, ttl: Any = _UTIL_MISSING) -> None:
        actual_ttl = self.default_ttl if ttl is _UTIL_MISSING else ttl
        with self._lock:
            self._items.pop(key, None)
            self._items[key] = (self._deadline(actual_ttl), value)
            self._items.move_to_end(key)
            self._purge_expired_locked()
            while len(self._items) > self.max_size:
                self._items.popitem(last=False)
                self._evictions += 1

    def _purge_expired_locked(self) -> int:
        now = time.monotonic()
        expired = [key for key, (deadline, _) in self._items.items() if deadline is not None and deadline <= now]
        for key in expired:
            self._items.pop(key, None)
        return len(expired)

    def purge(self) -> int:
        with self._lock:
            return self._purge_expired_locked()

    def get(self, key: Any, default: Any = None) -> Any:
        with self._lock:
            row = self._items.get(key)
            if row is None:
                self._misses += 1
                return default
            deadline, value = row
            if deadline is not None and deadline <= time.monotonic():
                self._items.pop(key, None)
                self._misses += 1
                return default
            self._items.move_to_end(key)
            self._hits += 1
            return value

    def pop(self, key: Any, default: Any = _UTIL_MISSING) -> Any:
        with self._lock:
            row = self._items.pop(key, _UTIL_MISSING)
            if row is _UTIL_MISSING:
                if default is _UTIL_MISSING:
                    raise KeyError(key)
                return default
            deadline, value = row
            if deadline is not None and deadline <= time.monotonic():
                if default is _UTIL_MISSING:
                    raise KeyError(key)
                return default
            return value

    def delete(self, key: Any) -> bool:
        with self._lock:
            return self._items.pop(key, None) is not None

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def __contains__(self, key: Any) -> bool:
        return self.get(key, _UTIL_MISSING) is not _UTIL_MISSING

    def __len__(self) -> int:
        self.purge()
        with self._lock:
            return len(self._items)

    def items(self) -> List[tuple[Any, Any]]:
        self.purge()
        with self._lock:
            return [(k, row[1]) for k, row in self._items.items()]

    def stats(self) -> Dict[str, int]:
        with self._lock:
            return {"size": len(self._items), "hits": self._hits, "misses": self._misses, "evictions": self._evictions}


class RateLimiter:
    """Thread-safe token-bucket rate limiter."""

    def __init__(self, rate: float, capacity: Optional[float] = None):
        if rate <= 0:
            raise ValueError("rate must be positive")
        self.rate = float(rate)
        self.capacity = float(capacity if capacity is not None else max(1.0, rate))
        if self.capacity <= 0:
            raise ValueError("capacity must be positive")
        self._tokens = self.capacity
        self._updated = time.monotonic()
        self._lock = threading.Lock()

    def _refill_locked(self) -> None:
        now = time.monotonic()
        self._tokens = min(self.capacity, self._tokens + (now - self._updated) * self.rate)
        self._updated = now

    def available(self) -> float:
        with self._lock:
            self._refill_locked()
            return self._tokens

    def try_acquire(self, tokens: float = 1.0) -> bool:
        if tokens <= 0:
            raise ValueError("tokens must be positive")
        with self._lock:
            self._refill_locked()
            if self._tokens + 1e-12 < tokens:
                return False
            self._tokens -= tokens
            return True

    def acquire(self, tokens: float = 1.0, timeout: Optional[float] = None) -> bool:
        if tokens > self.capacity:
            raise ValueError("requested tokens exceed bucket capacity")
        deadline = None if timeout is None else time.monotonic() + max(0.0, timeout)
        while True:
            if self.try_acquire(tokens):
                return True
            if deadline is not None and time.monotonic() >= deadline:
                return False
            with self._lock:
                self._refill_locked()
                missing = max(0.0, tokens - self._tokens)
            wait = missing / self.rate if missing else 0.001
            if deadline is not None:
                wait = min(wait, max(0.0, deadline - time.monotonic()))
            time.sleep(max(0.0005, wait))


class RetryPolicy:
    """Configurable synchronous retry helper with exponential backoff."""

    def __init__(self, attempts: int = 3, delay: float = 0.0, backoff: float = 2.0,
                 max_delay: Optional[float] = None, exceptions: tuple[type[BaseException], ...] = (Exception,)):
        if attempts <= 0:
            raise ValueError("attempts must be positive")
        if backoff < 1:
            raise ValueError("backoff must be >= 1")
        self.attempts = int(attempts)
        self.delay = max(0.0, float(delay))
        self.backoff = float(backoff)
        self.max_delay = max_delay
        self.exceptions = exceptions

    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        wait = self.delay
        last: Optional[BaseException] = None
        for attempt in range(self.attempts):
            try:
                return func(*args, **kwargs)
            except self.exceptions as exc:
                last = exc
                if attempt + 1 >= self.attempts:
                    raise
                if wait:
                    time.sleep(wait)
                wait *= self.backoff
                if self.max_delay is not None:
                    wait = min(wait, float(self.max_delay))
        if last is not None:
            raise last
        raise RuntimeError("retry policy reached an impossible state")

    __call__ = call


class CircuitBreaker:
    """Simple thread-safe CLOSED/OPEN/HALF_OPEN circuit breaker."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0, success_threshold: int = 1):
        if failure_threshold <= 0 or success_threshold <= 0:
            raise ValueError("thresholds must be positive")
        self.failure_threshold = int(failure_threshold)
        self.recovery_timeout = max(0.0, float(recovery_timeout))
        self.success_threshold = int(success_threshold)
        self._state = self.CLOSED
        self._failures = 0
        self._half_successes = 0
        self._opened_at = 0.0
        self._lock = threading.Lock()

    @property
    def state(self) -> str:
        with self._lock:
            if self._state == self.OPEN and time.monotonic() - self._opened_at >= self.recovery_timeout:
                self._state = self.HALF_OPEN
                self._half_successes = 0
            return self._state

    def allow(self) -> bool:
        return self.state != self.OPEN

    def reset(self) -> None:
        with self._lock:
            self._state = self.CLOSED; self._failures = 0; self._half_successes = 0; self._opened_at = 0.0

    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        if not self.allow():
            raise RuntimeError("circuit breaker is open")
        try:
            result = func(*args, **kwargs)
        except BaseException:
            with self._lock:
                self._failures += 1
                self._half_successes = 0
                if self._state == self.HALF_OPEN or self._failures >= self.failure_threshold:
                    self._state = self.OPEN
                    self._opened_at = time.monotonic()
            raise
        with self._lock:
            if self._state == self.HALF_OPEN:
                self._half_successes += 1
                if self._half_successes >= self.success_threshold:
                    self._state = self.CLOSED; self._failures = 0; self._half_successes = 0
            else:
                self._failures = 0
        return result

    __call__ = call


class Stopwatch:
    """Monotonic stopwatch with laps and context-manager support."""

    def __init__(self, start: bool = True):
        self._started: Optional[float] = time.perf_counter() if start else None
        self._elapsed = 0.0
        self._lap_base = self._started

    @property
    def running(self) -> bool:
        return self._started is not None

    @property
    def elapsed(self) -> float:
        return self._elapsed + (time.perf_counter() - self._started if self._started is not None else 0.0)

    def start(self) -> "Stopwatch":
        if self._started is None:
            self._started = time.perf_counter(); self._lap_base = self._started
        return self

    def stop(self) -> float:
        if self._started is not None:
            now = time.perf_counter(); self._elapsed += now - self._started; self._started = None; self._lap_base = None
        return self._elapsed

    def reset(self, *, start: bool = True) -> "Stopwatch":
        self._elapsed = 0.0; self._started = time.perf_counter() if start else None; self._lap_base = self._started
        return self

    def lap(self) -> float:
        if self._started is None:
            raise RuntimeError("stopwatch is not running")
        now = time.perf_counter(); base = self._lap_base if self._lap_base is not None else self._started
        self._lap_base = now
        return now - base

    def __enter__(self) -> "Stopwatch":
        return self.start()

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.stop()

class Terminal:
    """Cross-platform dependency-free terminal formatting helper."""

    ANSI_RE = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07\x1b]*(?:\x07|\x1b\\))")

    @staticmethod
    def supports_color(stream: Any = None) -> bool:
        stream = stream or os.sys.stdout
        if os.environ.get("NO_COLOR") is not None:
            return False
        if os.environ.get("FORCE_COLOR") not in (None, "", "0"):
            return True
        return bool(getattr(stream, "isatty", lambda: False)()) and os.environ.get("TERM", "") != "dumb"

    @staticmethod
    def size(fallback: tuple[int, int] = (80, 24)) -> tuple[int, int]:
        size = shutil.get_terminal_size(fallback=fallback)
        return size.columns, size.lines

    @classmethod
    def strip_ansi(cls, text: object) -> str:
        return cls.ANSI_RE.sub("", str(text))

    @classmethod
    def visible_width(cls, text: object) -> int:
        # Width is intentionally codepoint-based and dependency-free. It is exact
        # for ordinary ASCII/Latin terminal UIs and conservative for complex emoji.
        return len(cls.strip_ansi(text))

    @classmethod
    def truncate(cls, text: object, width: int, suffix: str = "…") -> str:
        value = str(text)
        width = max(0, int(width))
        plain = cls.strip_ansi(value)
        if len(plain) <= width:
            return value
        if width == 0:
            return ""
        if len(suffix) >= width:
            return suffix[:width]
        # ANSI-preserving truncation is deliberately avoided here: returning a
        # clean string prevents leaking an unterminated style into later output.
        return plain[: width - len(suffix)] + suffix

    @classmethod
    def pad(cls, text: object, width: int, align: str = "left") -> str:
        value = str(text); missing = max(0, int(width) - cls.visible_width(value))
        align = align.lower()
        if align == "right": return " " * missing + value
        if align == "center":
            left = missing // 2; return " " * left + value + " " * (missing - left)
        if align != "left": raise ValueError("align must be left, center or right")
        return value + " " * missing

    @classmethod
    def table(cls, rows: Iterable[Sequence[Any]], headers: Optional[Sequence[Any]] = None,
              *, padding: int = 1, max_width: Optional[int] = None) -> str:
        materialized = [[str(cell) for cell in row] for row in rows]
        if headers is not None:
            materialized.insert(0, [str(cell) for cell in headers])
        if not materialized:
            return ""
        columns = max(len(row) for row in materialized)
        normalized = [row + [""] * (columns - len(row)) for row in materialized]
        widths = [max(cls.visible_width(row[col]) for row in normalized) for col in range(columns)]
        if max_width is not None and columns:
            available = max(columns, int(max_width) - (columns + 1) - 2 * padding * columns)
            cap = max(1, available // columns)
            widths = [min(width, cap) for width in widths]
        def border(char: str = "-") -> str:
            return "+" + "+".join(char * (w + padding * 2) for w in widths) + "+"
        lines = [border()]
        for index, row in enumerate(normalized):
            cells = []
            for col, value in enumerate(row):
                value = cls.truncate(value, widths[col])
                cells.append(" " * padding + cls.pad(value, widths[col]) + " " * padding)
            lines.append("|" + "|".join(cells) + "|")
            if headers is not None and index == 0:
                lines.append(border("="))
        lines.append(border())
        return "\n".join(lines)

    @staticmethod
    def clear(stream: Any = None) -> None:
        stream = stream or os.sys.stdout
        if bool(getattr(stream, "isatty", lambda: False)()):
            stream.write("\033[2J\033[H"); stream.flush()

    @staticmethod
    def progress(current: float, total: float, *, width: int = 30, label: str = "", fill: str = "#", empty: str = "-") -> str:
        total = float(total); current = float(current); width = max(1, int(width))
        ratio = 1.0 if total <= 0 and current > 0 else (0.0 if total <= 0 else max(0.0, min(1.0, current / total)))
        filled = min(width, max(0, round(width * ratio)))
        bar = fill * filled + empty * (width - filled)
        prefix = f"{label} " if label else ""
        return f"{prefix}[{bar}] {ratio * 100:6.2f}%"
