"""Dependency-free application utilities used across YoungLion projects.

This module collects focused building blocks that are useful in command-line,
desktop and service applications without introducing third-party runtime
requirements: structured subprocess results, script execution, in-process task
scheduling, rotating logging, SMTP/IMAP e-mail, local/FTP transfer tracking, text
analysis, priority event dispatch, TTL/LRU caching, token-bucket rate limiting,
retry policies, circuit breakers, stopwatches and terminal rendering.

Concurrency-sensitive classes document their thread-safety guarantees.  Network
helpers expose standard protocol behavior and allow connection/authentication
errors to propagate so callers can implement application-specific recovery.
"""
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
    """Structured subprocess result.
    
    Overview
    --------
    ``CommandResult`` provides command arguments, return code, captured streams, duration and success/check helpers.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Returned by ScriptRunner.run for inspectable process execution.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    ok, check.
    """
    args: tuple[str, ...]
    returncode: int
    stdout: str = ""
    stderr: str = ""
    duration: float = 0.0

    @property
    def ok(self) -> bool:
        """Return True when the subprocess return code indicates success.
        
        Details
        -------
        This method belongs to :class:`CommandResult` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        """
        return self.returncode == 0

    def check(self) -> "CommandResult":
        """Return this result when successful or raise CalledProcessError for a non-zero return code.
        
        Details
        -------
        This method belongs to :class:`CommandResult` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``'CommandResult'`` result described by the method semantics.
        """
        if not self.ok:
            raise subprocess.CalledProcessError(self.returncode, self.args, self.stdout, self.stderr)
        return self


class ScriptRunner:
    """Cross-platform subprocess/script runner.
    
    Overview
    --------
    ``ScriptRunner`` provides interpreter detection, synchronous structured execution, asynchronous processes and script launching.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for explicit commands or script files while retaining cwd/env/timeout control.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    set_default_interpreter, detect_interpreter, run, run_async, run_script.
    
    Example::
    
        runner = ScriptRunner()
        result = runner.run(["python", "--version"])
        if result.ok:
            print(result.stdout or result.stderr)
    """

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
        """Initialize a new ScriptRunner instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`ScriptRunner` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        default_interpreter : str (default: ``'node'``)
            Fallback executable used when a script extension has no registered interpreter.
        """
        self.default_interpreter = default_interpreter

    def set_default_interpreter(self, interpreter: str):
        """Change the fallback interpreter used for script extensions that are not recognized explicitly.
        
        Details
        -------
        This method belongs to :class:`ScriptRunner` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        interpreter : str
            Explicit interpreter executable; when omitted automatic detection is used.
        """
        self.default_interpreter = interpreter
        return self

    def _validate_path(self, path: str) -> str:
        p = os.path.abspath(path)
        if not os.path.isfile(p):
            raise FileNotFoundError(path)
        return p

    def detect_interpreter(self, path: str) -> str:
        """Choose an interpreter from a script filename extension or fall back to the configured default.
        
        Details
        -------
        This method belongs to :class:`ScriptRunner` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
        factory = self.INTERPRETERS.get(Path(path).suffix.lower())
        return factory() if factory else self.default_interpreter

    def run(self, command: Sequence[Union[str, os.PathLike[str]]], *, cwd: Optional[str] = None,
            env: Optional[Mapping[str, str]] = None, timeout: Optional[float] = None,
            input_text: Optional[str] = None, check: bool = False, capture_output: bool = True) -> CommandResult:
        """Execute a command synchronously and return a structured CommandResult.
        
        Details
        -------
        This method belongs to :class:`ScriptRunner` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        command : Sequence[Union[str, os.PathLike[str]]]
            Sequence containing executable and command arguments.
        cwd : Optional[str] (default: ``None``)
            Optional working directory for the child process.
        env : Optional[Mapping[str, str]] (default: ``None``)
            Environment values merged with the current process environment.
        timeout : Optional[float] (default: ``None``)
            Maximum seconds to wait before giving up; None means no explicit timeout.
        input_text : Optional[str] (default: ``None``)
            Optional standard-input text supplied to the subprocess.
        check : bool (default: ``False``)
            Whether non-zero process exit status should raise CalledProcessError.
        capture_output : bool (default: ``True``)
            Whether stdout/stderr are captured into CommandResult.
        
        Returns
        -------
        CommandResult containing exit code, streams and duration.
        
        Example::
        
            result = runner.run(["python", "--version"], timeout=10)
            result.check()
        """
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
        """Start a subprocess asynchronously and return the live Popen object.
        
        Details
        -------
        This method belongs to :class:`ScriptRunner` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        command : Sequence[Union[str, os.PathLike[str]]]
            Sequence containing executable and command arguments.
        cwd : Optional[str] (default: ``None``)
            Optional working directory for the child process.
        env : Optional[Mapping[str, str]] (default: ``None``)
            Environment values merged with the current process environment.
        stdout : Any (default: ``subprocess.PIPE``)
            stdout target passed to subprocess.Popen.
        stderr : Any (default: ``subprocess.PIPE``)
            stderr target passed to subprocess.Popen.
        
        Returns
        -------
        Live ``subprocess.Popen`` process handle.
        """
        merged_env = os.environ.copy()
        if env: merged_env.update({str(k): str(v) for k, v in env.items()})
        return subprocess.Popen([os.fspath(x) for x in command], cwd=cwd, env=merged_env, text=True, stdout=stdout, stderr=stderr)

    def run_script(self, path: str, interpreter: Optional[str] = None, terminal: bool = False,
                   inputs: Optional[Union[str, Sequence[str]]] = None, output: bool = True,
                   *, cwd: Optional[str] = None, env: Optional[Mapping[str, str]] = None,
                   timeout: Optional[float] = None, check: bool = True):
        """Resolve a script interpreter and execute/open the script according to the requested mode.
        
        Details
        -------
        This method belongs to :class:`ScriptRunner` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        path : str
            Filesystem path or dotted data path, according to the owning API.
        interpreter : Optional[str] (default: ``None``)
            Explicit interpreter executable; when omitted automatic detection is used.
        terminal : bool (default: ``False``)
            Whether to open the script in a separate terminal where supported.
        inputs : Optional[Union[str, Sequence[str]]] (default: ``None``)
            Additional script arguments/input values.
        output : bool (default: ``True``)
            Whether captured output is returned by the convenience method.
        cwd : Optional[str] (default: ``None``)
            Optional working directory for the child process.
        env : Optional[Mapping[str, str]] (default: ``None``)
            Environment values merged with the current process environment.
        timeout : Optional[float] (default: ``None``)
            Maximum seconds to wait before giving up; None means no explicit timeout.
        check : bool (default: ``True``)
            Whether non-zero process exit status should raise CalledProcessError.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        """
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
    """Immutable-style scheduler task snapshot.
    
    Overview
    --------
    ``TaskInfo`` provides task identity, state, timing, repeat configuration, run/failure counters and latest result/error.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Returned by TaskScheduler inspection methods.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    """
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
    """In-process task scheduler.
    
    Overview
    --------
    ``TaskScheduler`` provides delayed, absolute-time and repeating tasks with pause/resume/cancel/retry state.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for lightweight application scheduling; it is not a durable distributed job queue.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    schedule_task, schedule_at, run_now, cancel_task, pause_task, resume_task, get_task, list_tasks, wait, shutdown.
    
    Concurrency model
    -----------------
    Tasks execute in daemon timer/worker threads inside the current process. Scheduler state is synchronized, but scheduled callables are normal application code and must coordinate their own shared data. Pending tasks do not survive process restart.
    
    Example::
    
        scheduler = TaskScheduler()
        task_id = scheduler.schedule_task(lambda: "done", delay=0.1)
        info = scheduler.wait(task_id, timeout=2.0)
        scheduler.shutdown()
    """

    def __init__(self):
        """Initialize a new TaskScheduler instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`TaskScheduler` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._counter = 0
        self._lock = threading.RLock()
        self._closed = False

    def schedule_task(self, func: Callable[..., Any], delay: float = 0.0, repeat: Optional[float] = None,
                      priority: int = 0, args: Sequence[Any] = (), kwargs: Optional[Dict[str, Any]] = None,
                      *, retries: int = 0, retry_delay: float = 0.0, task_id: Optional[str] = None) -> str:
        """Schedule a callable after a delay with optional repetition, priority metadata and retry behavior.
        
        Details
        -------
        This method belongs to :class:`TaskScheduler` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        func : Callable[..., Any]
            Callable applied by the operation.
        delay : float (default: ``0.0``)
            Initial delay in seconds.
        repeat : Optional[float] (default: ``None``)
            Repeat interval in seconds; None schedules only one execution.
        priority : int (default: ``0``)
            Priority metadata/order; larger values are handled first where the API supports priority.
        args : Sequence[Any] (default: ``()``)
            Arguments passed to a script/callable/subprocess.
        kwargs : Optional[Dict[str, Any]] (default: ``None``)
            Keyword arguments forwarded to the target callable/helper.
        retries : int (default: ``0``)
            Number of retry attempts after task execution failures.
        retry_delay : float (default: ``0.0``)
            Delay in seconds between scheduler retry attempts.
        task_id : Optional[str] (default: ``None``)
            Optional caller-defined task identifier.
        
        Returns
        -------
        Task identifier string.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
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
        """Schedule a callable for an absolute datetime by converting it to an appropriate delay.
        
        Details
        -------
        This method belongs to :class:`TaskScheduler` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        when : datetime
            Absolute datetime at which the task should become eligible to run.
        func : Callable[..., Any]
            Callable applied by the operation.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        
        Returns
        -------
        Task identifier string.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
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
        """Trigger a queued task immediately in a daemon worker thread.
        
        Details
        -------
        This method belongs to :class:`TaskScheduler` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        task_id : str
            Optional caller-defined task identifier.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task or task["state"] == "cancelled": return False
            timer = task.get("timer")
            if timer: timer.cancel()
            task["state"] = "queued"
        thread = threading.Thread(target=self._execute, args=(task_id,), daemon=True); thread.start(); return True

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a known task and its pending timer.
        
        Details
        -------
        This method belongs to :class:`TaskScheduler` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        task_id : str
            Optional caller-defined task identifier.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task: return False
            task["state"] = "cancelled"; timer = task.get("timer")
            if timer: timer.cancel()
            return True

    def pause_task(self, task_id: str) -> bool:
        """Pause a pending task while retaining its remaining delay.
        
        Details
        -------
        This method belongs to :class:`TaskScheduler` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        task_id : str
            Optional caller-defined task identifier.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task or task["state"] in {"completed", "cancelled", "failed"}: return False
            task["remaining_delay"] = max(0.0, task.get("next_run", time.time()) - time.time())
            task["state"] = "paused"; timer = task.get("timer")
            if timer: timer.cancel()
            return True

    def resume_task(self, task_id: str) -> bool:
        """Resume a previously paused task using its recorded remaining delay.
        
        Details
        -------
        This method belongs to :class:`TaskScheduler` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        task_id : str
            Optional caller-defined task identifier.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task or task["state"] != "paused": return False
            task["state"] = "queued"; self._arm(task, float(task.pop("remaining_delay", 0.0))); return True

    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """Return a TaskInfo snapshot for one task ID or None when unknown.
        
        Details
        -------
        This method belongs to :class:`TaskScheduler` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        task_id : str
            Optional caller-defined task identifier.
        
        Returns
        -------
        ``Optional[TaskInfo]`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if not task: return None
            return TaskInfo(task["id"], task["state"], task["created_at"], task["next_run"], task["repeat"], task["priority"], task["runs"], task["failures"], task["last_result"], task["last_error"])

    def list_tasks(self) -> List[Dict[str, Any]]:
        """Return serializable-style snapshots of all scheduler tasks without internal timer/callable objects.
        
        Details
        -------
        This method belongs to :class:`TaskScheduler` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``List[Dict[str, Any]]`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        with self._lock:
            return [{k: v for k, v in task.items() if k not in {"timer", "func"}} for task in self._tasks.values()]

    def wait(self, task_id: str, timeout: Optional[float] = None, poll_interval: float = 0.01) -> Optional[TaskInfo]:
        """Poll task state until completion/failure/cancellation or timeout.
        
        Details
        -------
        This method belongs to :class:`TaskScheduler` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        task_id : str
            Optional caller-defined task identifier.
        timeout : Optional[float] (default: ``None``)
            Maximum seconds to wait before giving up; None means no explicit timeout.
        poll_interval : float (default: ``0.01``)
            Seconds between state checks while waiting.
        
        Returns
        -------
        ``Optional[TaskInfo]`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        deadline = None if timeout is None else time.monotonic() + timeout
        while deadline is None or time.monotonic() < deadline:
            info = self.get_task(task_id)
            if info is None or info.state in {"completed", "failed", "cancelled"}: return info
            time.sleep(poll_interval)
        return self.get_task(task_id)

    def shutdown(self, cancel_pending: bool = True) -> None:
        """Stop the scheduler and optionally cancel all unfinished tasks.
        
        Details
        -------
        This method belongs to :class:`TaskScheduler` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        cancel_pending : bool (default: ``True``)
            Whether shutdown marks/cancels unfinished tasks.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        with self._lock:
            self._closed = True
            if cancel_pending:
                for task in self._tasks.values():
                    timer = task.get("timer")
                    if timer: timer.cancel()
                    if task["state"] not in {"completed", "failed"}: task["state"] = "cancelled"


class Logger:
    """Thread-safe rotating application logger.
    
    Overview
    --------
    ``Logger`` provides level filtering, contextual fields, console output, file persistence and size-based rotation.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for dependency-free application logging with bindable context.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    set_log_level, bind, log_debug, log_info, log_warning, log_error, log_critical.
    
    Logging behavior
    ----------------
    Messages below ``log_level`` are ignored. Accepted messages are rendered with an ISO local timestamp and level label, optional bound context fields are serialized as compact JSON, and file output is protected by a re-entrant lock. ``max_bytes=0`` disables rotation; otherwise numbered backups up to ``backup_count`` are maintained.
    
    Example::
    
        log = Logger("app.log", "INFO", max_bytes=1_000_000, backup_count=3)
        request_log = log.bind(component="api", request_id="req-42")
        request_log.info("request completed", status=200)
    """
    LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}

    def __init__(self, log_file: str = "app.log", log_level: str = "INFO", *, console: bool = True,
                 max_bytes: int = 0, backup_count: int = 5):
        """Initialize a new Logger instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`Logger` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        log_file : str (default: ``'app.log'``)
            Path of the plain UTF-8 log file.
        log_level : str (default: ``'INFO'``)
            Minimum accepted log severity name.
        console : bool (default: ``True``)
            Whether accepted log lines are also printed to stdout.
        max_bytes : int (default: ``0``)
            Maximum active log size before rotation; 0 disables rotation.
        backup_count : int (default: ``5``)
            Number of rotated backup files retained.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        self.log_file = os.path.abspath(log_file); self.console = bool(console)
        self.max_bytes = max(0, int(max_bytes)); self.backup_count = max(0, int(backup_count))
        self._lock = threading.RLock(); self._context: Dict[str, Any] = {}; self.set_log_level(log_level)

    def set_log_level(self, level: str):
        """Change the minimum severity accepted by future log calls.
        
        Details
        -------
        This method belongs to :class:`Logger` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        level : str
            Minimum severity level name.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        level = level.upper()
        if level not in self.LEVELS: raise ValueError(f"invalid log level: {level}")
        self.log_level = level; return self

    def bind(self, **context: Any) -> "Logger":
        """Create a logger sharing configuration but pre-populated with additional contextual fields.
        
        Details
        -------
        This method belongs to :class:`Logger` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        **context : Any
            Value supplied for ``context`` according to the Logger contract.
        
        Returns
        -------
        ``'Logger'`` result described by the method semantics.
        
        Notes
        -----
        The returned Logger has its own context mapping but writes to the same configured file path and uses the same severity/rotation settings. It is useful for request/module/entity context without modifying the parent logger.
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
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

    def log_debug(self, message: str, **fields: Any):
        """Write a DEBUG message with optional structured context fields.
        
        Details
        -------
        This method belongs to :class:`Logger` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        message : str
            Human-readable message text.
        **fields : Any
            Field names or field mapping used for structured document data.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        self._log("DEBUG", message, **fields)
    def log_info(self, message: str, **fields: Any):
        """Write an INFO message with optional structured context fields.
        
        Details
        -------
        This method belongs to :class:`Logger` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        message : str
            Human-readable message text.
        **fields : Any
            Field names or field mapping used for structured document data.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        
        Example::
        
            logger.info("user authenticated", user_id=42, method="token")
        """
        self._log("INFO", message, **fields)
    def log_warning(self, message: str, **fields: Any):
        """Write a WARNING message with optional structured context fields.
        
        Details
        -------
        This method belongs to :class:`Logger` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        message : str
            Human-readable message text.
        **fields : Any
            Field names or field mapping used for structured document data.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        self._log("WARNING", message, **fields)
    def log_error(self, message: str, **fields: Any):
        """Write an ERROR message with optional structured context fields.
        
        Details
        -------
        This method belongs to :class:`Logger` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        message : str
            Human-readable message text.
        **fields : Any
            Field names or field mapping used for structured document data.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        self._log("ERROR", message, **fields)
    def log_critical(self, message: str, **fields: Any):
        """Write a CRITICAL message with optional structured context fields.
        
        Details
        -------
        This method belongs to :class:`Logger` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        message : str
            Human-readable message text.
        **fields : Any
            Field names or field mapping used for structured document data.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        self._log("CRITICAL", message, **fields)
    debug = log_debug; info = log_info; warning = log_warning; error = log_error; critical = log_critical


class EmailManager:
    """SMTP/IMAP e-mail helper.
    
    Overview
    --------
    ``EmailManager`` provides plain/HTML message construction, CC/BCC, attachments, sending, delayed sends and inbox header inspection.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use with provider credentials supplied by the application; protocol errors are not silently swallowed.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    build_email, send_message, send_email, schedule_email, check_inbox.
    """
    def __init__(self, smtp_server: str, smtp_port: int, email_address: str, email_password: str,
                 imap_server: Optional[str] = None, *, use_ssl: bool = False, starttls: bool = True):
        """Initialize a new EmailManager instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`EmailManager` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        smtp_server : str
            SMTP server hostname.
        smtp_port : int
            SMTP server port.
        email_address : str
            Account/from address used for SMTP authentication and message From.
        email_password : str
            Password/app-password supplied to SMTP/IMAP authentication.
        imap_server : Optional[str] (default: ``None``)
            Optional IMAP hostname; when omitted a hostname is derived from SMTP server.
        use_ssl : bool (default: ``False``)
            Use SMTP-over-SSL from connection start.
        starttls : bool (default: ``True``)
            Upgrade a non-SSL SMTP connection with STARTTLS before authentication.
        """
        self.smtp_server = smtp_server; self.smtp_port = int(smtp_port); self.email_address = email_address
        self.email_password = email_password; self.imap_server = imap_server; self.use_ssl = bool(use_ssl); self.starttls = bool(starttls)

    def build_email(self, to: Union[str, Sequence[str]], subject: str, body: str, *, html: Optional[str] = None,
                    cc: Union[str, Sequence[str], None] = None, bcc: Union[str, Sequence[str], None] = None,
                    attachments: Iterable[Union[str, os.PathLike[str]]] = ()) -> EmailMessage:
        """Construct an EmailMessage with plain text, optional HTML, CC/BCC and attachments.
        
        Details
        -------
        This method belongs to :class:`EmailManager` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        to : Union[str, Sequence[str]]
            Recipient address or sequence of addresses.
        subject : str
            Message subject line.
        body : str
            Plain-text message body.
        html : Optional[str] (default: ``None``)
            Optional HTML alternative body.
        cc : Union[str, Sequence[str], None] (default: ``None``)
            Optional visible carbon-copy recipients.
        bcc : Union[str, Sequence[str], None] (default: ``None``)
            Optional blind-carbon-copy recipients, intentionally omitted from visible headers.
        attachments : Iterable[Union[str, os.PathLike[str]]] (default: ``()``)
            Iterable of filesystem paths to attach.
        
        Returns
        -------
        Prepared ``email.message.EmailMessage``.
        """
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
        """Send a prepared EmailMessage through the configured SMTP server.
        
        Details
        -------
        This method belongs to :class:`EmailManager` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        message : EmailMessage
            Human-readable message text.
        
        Returns
        -------
        ``True`` after SMTP send completes without raising.
        """
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
        """Build and send one e-mail in a convenience call.
        
        Details
        -------
        This method belongs to :class:`EmailManager` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        to : Union[str, Sequence[str]]
            Recipient address or sequence of addresses.
        subject : str
            Message subject line.
        body : str
            Plain-text message body.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        
        Returns
        -------
        ``True`` after message construction and SMTP send complete.
        """
        return self.send_message(self.build_email(to, subject, body, **kwargs))

    def schedule_email(self, to: Union[str, Sequence[str]], subject: str, body: str, send_time: datetime, **kwargs: Any):
        """Schedule an e-mail send using an in-process daemon timer.
        
        Details
        -------
        This method belongs to :class:`EmailManager` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        to : Union[str, Sequence[str]]
            Recipient address or sequence of addresses.
        subject : str
            Message subject line.
        body : str
            Plain-text message body.
        send_time : datetime
            Datetime at which an in-process timer should send the message.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        """
        delay = max(0.0, (send_time - datetime.now(tz=send_time.tzinfo)).total_seconds())
        timer = threading.Timer(delay, self.send_email, args=(to, subject, body), kwargs=kwargs); timer.daemon = True; timer.start(); return timer

    def check_inbox(self, user: Optional[str] = None, limit: int = 10, mailbox: str = "INBOX"):
        """Fetch recent IMAP message headers from the selected mailbox.
        
        Details
        -------
        This method belongs to :class:`EmailManager` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        user : Optional[str] (default: ``None``)
            Optional IMAP username overriding the configured e-mail address.
        limit : int (default: ``10``)
            Maximum number of results/messages/suggestions to return.
        mailbox : str (default: ``'INBOX'``)
            IMAP mailbox name.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        """
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
    """Tracked local/FTP transfer manager.
    
    Overview
    --------
    ``FileTransferManager`` provides upload/download operations with IDs, progress callbacks and queryable status.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for simple file movement; SFTP is intentionally not emulated without an explicit dependency.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    upload, download, get_status, get_progress.
    """

    def __init__(self):
        """Initialize a new FileTransferManager instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`FileTransferManager` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        self.transfer_status: Dict[str, str] = {}; self.transfer_progress: Dict[str, int] = {}; self._counter = 0; self._lock = threading.RLock()

    def _id(self) -> str:
        with self._lock: self._counter += 1; return f"transfer-{self._counter}"

    def _set_progress(self, tid: str, transferred: int, total: int, callback: Optional[Callable[[int, int], Any]]) -> None:
        percent = 100 if total <= 0 else min(100, int(transferred * 100 / total)); self.transfer_progress[tid] = percent
        if callback: callback(transferred, total)

    def upload(self, file_path: str, destination: str, protocol: str = "ftp", host: str = "", username: str = "",
               password: str = "", port: Optional[int] = None, *, progress: Optional[Callable[[int, int], Any]] = None) -> str:
        """Upload/copy a local file using the selected local/FTP protocol and track progress.
        
        Details
        -------
        This method belongs to :class:`FileTransferManager` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        file_path : str
            Local file path participating in transfer/log operations.
        destination : str
            Destination path or location.
        protocol : str (default: ``'ftp'``)
            Transfer protocol name (local/FTP where supported).
        host : str (default: ``''``)
            Remote host for network transfer.
        username : str (default: ``''``)
            Remote authentication username.
        password : str (default: ``''``)
            Remote authentication password.
        port : Optional[int] (default: ``None``)
            Optional remote port; protocol default is used when omitted.
        progress : Optional[Callable[[int, int], Any]] (default: ``None``)
            Optional callback receiving transferred and total byte counts.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
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
        """Download/copy a file using the selected local/FTP protocol and track progress.
        
        Details
        -------
        This method belongs to :class:`FileTransferManager` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        source : str
            Source path, collection or transfer identifier.
        destination : str
            Destination path or location.
        protocol : str (default: ``'ftp'``)
            Transfer protocol name (local/FTP where supported).
        host : str (default: ``''``)
            Remote host for network transfer.
        username : str (default: ``''``)
            Remote authentication username.
        password : str (default: ``''``)
            Remote authentication password.
        port : Optional[int] (default: ``None``)
            Optional remote port; protocol default is used when omitted.
        progress : Optional[Callable[[int, int], Any]] (default: ``None``)
            Optional callback receiving transferred and total byte counts.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
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

    def get_status(self, transfer_id: str) -> Optional[str]:
        """Return the last known status string for a transfer ID.
        
        Details
        -------
        This method belongs to :class:`FileTransferManager` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        transfer_id : str
            Identifier returned when a transfer was started.
        
        Returns
        -------
        ``Optional[str]`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        return self.transfer_status.get(transfer_id)
    def get_progress(self, transfer_id: str) -> Optional[int]:
        """Return the last known integer percentage for a transfer ID.
        
        Details
        -------
        This method belongs to :class:`FileTransferManager` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        transfer_id : str
            Identifier returned when a transfer was started.
        
        Returns
        -------
        ``Optional[int]`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        return self.transfer_progress.get(transfer_id)


class TextProcessor:
    """Text analysis and transformation helper.
    
    Overview
    --------
    ``TextProcessor`` provides token/sentence counts, search/replace, normalization, n-grams, extraction, summary, similarity and readability.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for lightweight text workflows without NLP dependencies.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    set_text, words, sentences, word_count, sentence_count, line_count, character_count, keyword_search, replace, normalize_whitespace, most_frequent_words, ngrams, extract_emails, extract_urls, summarize, similarity ....
    
    Example::
    
        text = TextProcessor("YoungLion makes repeated data work easier.")
        print(text.word_count())
        print(text.ngrams(2))
    """

    def __init__(self, text: str = ""):
        """Initialize a new TextProcessor instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`TextProcessor` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : str (default: ``''``)
            Text/content input.
        """
        self.text = text
    def set_text(self, text: str) -> "TextProcessor":
        """Replace the processor's default text and return the processor for fluent reuse.
        
        Details
        -------
        This method belongs to :class:`TextProcessor` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : str
            Text/content input.
        
        Returns
        -------
        ``'TextProcessor'`` result described by the method semantics.
        """
        self.text = str(text); return self
    def _value(self, text: Optional[str]) -> str: return text if text is not None else self.text
    def words(self, text: Optional[str] = None) -> List[str]:
        """Tokenize text into the processor's word representation.
        
        Details
        -------
        This method belongs to :class:`TextProcessor` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.
        
        Returns
        -------
        ``List[str]`` result described by the method semantics.
        """
        return re.findall(r"\b\w+(?:['-]\w+)*\b", self._value(text), re.UNICODE)
    def sentences(self, text: Optional[str] = None) -> List[str]:
        """Split text into sentence-like units using the dependency-free rules.
        
        Details
        -------
        This method belongs to :class:`TextProcessor` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.
        
        Returns
        -------
        ``List[str]`` result described by the method semantics.
        """
        return [x.strip() for x in re.split(r"(?<=[.!?])\s+", self._value(text)) if x.strip()]
    def word_count(self, text: Optional[str] = None) -> int:
        """Return the number of words in the selected/default text.
        
        Details
        -------
        This method belongs to :class:`TextProcessor` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        """
        return len(self.words(text))
    def sentence_count(self, text: Optional[str] = None) -> int:
        """Return the number of sentence-like units in the selected/default text.
        
        Details
        -------
        This method belongs to :class:`TextProcessor` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        """
        return len(self.sentences(text))
    def line_count(self, text: Optional[str] = None) -> int:
        """Count logical lines in a text file.
        
        Details
        -------
        This method belongs to :class:`TextProcessor` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        """
        return len(self._value(text).splitlines())
    def character_count(self, text: Optional[str] = None, include_spaces: bool = True) -> int:
        """Count characters, optionally excluding whitespace.
        
        Details
        -------
        This method belongs to :class:`TextProcessor` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.
        include_spaces : bool (default: ``True``)
            Whether whitespace contributes to character count.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        """
        value = self._value(text); return len(value) if include_spaces else len(re.sub(r"\s", "", value))
    def keyword_search(self, keyword: str, text: Optional[str] = None, case_sensitive: bool = False) -> List[int]:
        """Return positions/matches for a keyword with optional case sensitivity.
        
        Details
        -------
        This method belongs to :class:`TextProcessor` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        keyword : str
            Keyword/substring to locate.
        text : Optional[str] (default: ``None``)
            Text/content input.
        case_sensitive : bool (default: ``False``)
            Whether string matching preserves case instead of using case-folded comparison.
        
        Returns
        -------
        ``List[int]`` result described by the method semantics.
        """
        value = self._value(text); return list(_native.find_all(value if case_sensitive else value.casefold(), keyword if case_sensitive else keyword.casefold()))
    def replace(self, old: str, new: str, text: Optional[str] = None) -> str:
        """Replace occurrences of one substring with another in selected/default text.
        
        Details
        -------
        This method belongs to :class:`TextProcessor` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        old : str
            Substring to replace.
        new : str
            Replacement substring.
        text : Optional[str] (default: ``None``)
            Text/content input.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
        return self._value(text).replace(old, new)
    def normalize_whitespace(self, text: Optional[str] = None) -> str:
        """Collapse/normalize whitespace while preserving text content semantics as defined by the helper.
        
        Details
        -------
        This method belongs to :class:`TextProcessor` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
        return re.sub(r"\s+", " ", self._value(text)).strip()
    def most_frequent_words(self, n: int = 10, text: Optional[str] = None):
        """Return the most frequent normalized words and their counts.
        
        Details
        -------
        This method belongs to :class:`TextProcessor` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        n : int (default: ``10``)
            Requested count, rank or n-gram width depending on the API.
        text : Optional[str] (default: ``None``)
            Text/content input.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        """
        return Counter(word.casefold() for word in self.words(text)).most_common(n)
    def ngrams(self, n: int = 2, text: Optional[str] = None) -> List[tuple[str, ...]]:
        """Return contiguous n-word groups from the selected/default text.
        
        Details
        -------
        This method belongs to :class:`TextProcessor` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        n : int (default: ``2``)
            Requested count, rank or n-gram width depending on the API.
        text : Optional[str] (default: ``None``)
            Text/content input.
        
        Returns
        -------
        ``List[tuple[str, ...]]`` result described by the method semantics.
        """
        if n <= 0: raise ValueError("n must be positive")
        words = self.words(text); return [tuple(words[i:i+n]) for i in range(max(0, len(words)-n+1))]
    def extract_emails(self, text: Optional[str] = None) -> List[str]:
        """Extract e-mail-address-like substrings using the helper's regular expression.
        
        Details
        -------
        This method belongs to :class:`TextProcessor` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.
        
        Returns
        -------
        ``List[str]`` result described by the method semantics.
        """
        return re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", self._value(text))
    def extract_urls(self, text: Optional[str] = None) -> List[str]:
        """Extract URL-like substrings using the helper's regular expression.
        
        Details
        -------
        This method belongs to :class:`TextProcessor` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.
        
        Returns
        -------
        ``List[str]`` result described by the method semantics.
        """
        return re.findall(r"https?://[^\s<>'\"]+", self._value(text))
    def summarize(self, sentences: int = 3, text: Optional[str] = None) -> str:
        """Create a simple extractive summary containing the requested number of sentences.
        
        Details
        -------
        This method belongs to :class:`TextProcessor` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        sentences : int (default: ``3``)
            Number of sentences requested in an extractive summary.
        text : Optional[str] (default: ``None``)
            Text/content input.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
        return " ".join(self.sentences(text)[:max(0, sentences)])
    def similarity(self, other: str, text: Optional[str] = None, algorithm: str = "hybrid") -> float:
        """Compare text with another string using the selected YoungLion fuzzy similarity algorithm.
        
        Details
        -------
        This method belongs to :class:`TextProcessor` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        other : str
            Another compatible object/value used by the operation.
        text : Optional[str] (default: ``None``)
            Text/content input.
        algorithm : str (default: ``'hybrid'``)
            Algorithm name used for hashing, fuzzy matching or search ranking.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        a, b = self._value(text), str(other); algo = algorithm.lower()
        if algo in {"jaro", "jaro_winkler"}: return float(_native.jaro_winkler(a.casefold(), b.casefold()))
        if algo in {"trigram", "dice"}: return float(_native.trigram_similarity(a.casefold(), b.casefold()))
        distance = _native.damerau_levenshtein(a.casefold(), b.casefold()) if algo in {"damerau", "hybrid"} else _native.levenshtein(a.casefold(), b.casefold())
        lev = max(0.0, 1.0 - distance / max(len(a), len(b), 1))
        if algo == "hybrid": return 0.4 * lev + 0.35 * float(_native.jaro_winkler(a.casefold(), b.casefold())) + 0.25 * float(_native.trigram_similarity(a.casefold(), b.casefold()))
        return lev
    def readability_score(self, text: Optional[str] = None) -> float:
        """Return a lightweight readability metric derived from words/sentences/characteristics.
        
        Details
        -------
        This method belongs to :class:`TextProcessor` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        """
        value = self._value(text); words = self.words(value); sents = max(1, self.sentence_count(value)); vowels = re.compile(r"[aeiouyAEIOUY]+")
        syllables = max(1, sum(max(1, len(vowels.findall(w))) for w in words)); wc = max(1, len(words)); return 206.835 - 1.015 * (wc / sents) - 84.6 * (syllables / wc)
    def stats(self, text: Optional[str] = None) -> Dict[str, Any]:
        """Return diagnostic counts describing the current cache/index/processor state.
        
        Details
        -------
        This method belongs to :class:`TextProcessor` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : Optional[str] (default: ``None``)
            Text/content input.
        
        Returns
        -------
        Dictionary/dataclass containing diagnostic statistics for the current object.
        """
        value = self._value(text); words = self.words(value)
        return {"characters": len(value), "characters_no_spaces": len(re.sub(r"\s", "", value)), "words": len(words), "unique_words": len({w.casefold() for w in words}), "sentences": self.sentence_count(value), "lines": self.line_count(value), "readability": self.readability_score(value)}

# ---------------------------------------------------------------------------
# General application infrastructure (zero third-party runtime dependencies)
# ---------------------------------------------------------------------------

_UTIL_MISSING = object()


class EventBus:
    """Thread-safe in-process event bus.
    
    Overview
    --------
    ``EventBus`` provides priority listeners, one-shot subscriptions, unsubscribe tokens and synchronous emission.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for decoupled application components where callbacks run in the emitting thread.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    subscribe, once, unsubscribe, emit, listener_count, clear.
    
    Example::
    
        bus = EventBus()
        token = bus.subscribe("user.created", lambda user: print(user.id))
        bus.emit("user.created", user)
        bus.unsubscribe(token)
    """

    def __init__(self):
        """Initialize a new EventBus instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`EventBus` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        self._listeners: Dict[str, List[tuple[int, str, Callable[..., Any], bool]]] = {}
        self._lock = threading.RLock()

    def subscribe(self, event: str, callback: Callable[..., Any], *, once: bool = False, priority: int = 0) -> str:
        """Register an event callback with priority and optional one-shot behavior; return its unsubscribe token.
        
        Details
        -------
        This method belongs to :class:`EventBus` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        event : str
            Event name.
        callback : Callable[..., Any]
            Listener/progress/callback function invoked by the operation.
        once : bool (default: ``False``)
            Whether an event listener automatically unregisters after one emission.
        priority : int (default: ``0``)
            Priority metadata/order; larger values are handled first where the API supports priority.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
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
        """Register a callback that automatically unsubscribes after its first successful emission.
        
        Details
        -------
        This method belongs to :class:`EventBus` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        event : str
            Event name.
        callback : Callable[..., Any]
            Listener/progress/callback function invoked by the operation.
        priority : int (default: ``0``)
            Priority metadata/order; larger values are handled first where the API supports priority.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        return self.subscribe(event, callback, once=True, priority=priority)

    def unsubscribe(self, token: str) -> bool:
        """Remove a listener by subscription token and report whether it existed.
        
        Details
        -------
        This method belongs to :class:`EventBus` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        token : str
            Subscription token returned by EventBus.subscribe/once.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
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
        """Synchronously invoke listeners for an event in priority order and return callback results.
        
        Details
        -------
        This method belongs to :class:`EventBus` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        event : str
            Event name.
        *args : Any
            Arguments passed to a script/callable/subprocess.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        
        Returns
        -------
        ``List[Any]`` result described by the method semantics.
        
        Notes
        -----
        Listeners are invoked synchronously in the emitting thread. A slow listener therefore delays emit(); use your own worker/executor when asynchronous dispatch is required.
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
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
        """Return the number of listeners for one event or across the entire bus.
        
        Details
        -------
        This method belongs to :class:`EventBus` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        event : Optional[str] (default: ``None``)
            Event name.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        with self._lock:
            if event is None:
                return sum(len(v) for v in self._listeners.values())
            return len(self._listeners.get(str(event), ()))

    def clear(self, event: Optional[str] = None) -> None:
        """Remove all currently stored entries or queued operations, depending on the owning class.
        
        Details
        -------
        This method belongs to :class:`EventBus` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        event : Optional[str] (default: ``None``)
            Event name.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        with self._lock:
            if event is None:
                self._listeners.clear()
            else:
                self._listeners.pop(str(event), None)


class TTLCache:
    """Thread-safe TTL/LRU-style cache.
    
    Overview
    --------
    ``TTLCache`` provides per-entry expiry, bounded size, recency updates, purge operations and hit/miss/eviction stats.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for small application memoization; values are held in-process only.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    set, purge, get, pop, delete, clear, items, stats.
    
    Example::
    
        cache = TTLCache(max_size=1000, default_ttl=60)
        cache.set("user:42", {"name": "Alice"})
        user = cache.get("user:42")
    """

    def __init__(self, max_size: int = 1024, default_ttl: Optional[float] = 300.0):
        """Initialize a new TTLCache instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`TTLCache` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        max_size : int (default: ``1024``)
            Maximum number of cache entries retained.
        default_ttl : Optional[float] (default: ``300.0``)
            Default time-to-live in seconds; None means no expiry.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
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
        """Add a field assignment to the builder/plan and return self for fluent chaining.
        
        Details
        -------
        This method belongs to :class:`TTLCache` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        key : Any
            Mapping key or uniqueness key.
        value : Any
            Target, new or comparison value.
        ttl : Any (default: ``_UTIL_MISSING``)
            Per-entry time-to-live override.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
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
        """Remove expired cache entries and return how many were discarded.
        
        Details
        -------
        This method belongs to :class:`TTLCache` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        with self._lock:
            return self._purge_expired_locked()

    def get(self, key: Any, default: Any = None) -> Any:
        """Return a value for a key, falling back to a default when the key is absent.
        
        Details
        -------
        This method belongs to :class:`TTLCache` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        key : Any
            Mapping key or uniqueness key.
        default : Any (default: ``None``)
            Fallback returned/used when the requested value or path is absent.
        
        Returns
        -------
        ``Any`` result described by the method semantics.
        
        Notes
        -----
        A successful get updates recency for LRU-style eviction. Expired entries are treated as misses and removed lazily.
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
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
        """Remove a key and return its value, optionally using a default when absent.
        
        Details
        -------
        This method belongs to :class:`TTLCache` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        key : Any
            Mapping key or uniqueness key.
        default : Any (default: ``_UTIL_MISSING``)
            Fallback returned/used when the requested value or path is absent.
        
        Returns
        -------
        ``Any`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
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
        """Remove one cache entry and report whether it existed.
        
        Details
        -------
        This method belongs to :class:`TTLCache` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        key : Any
            Mapping key or uniqueness key.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        with self._lock:
            return self._items.pop(key, None) is not None

    def clear(self) -> None:
        """Remove all currently stored entries or queued operations, depending on the owning class.
        
        Details
        -------
        This method belongs to :class:`TTLCache` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        with self._lock:
            self._items.clear()

    def __contains__(self, key: Any) -> bool:
        return self.get(key, _UTIL_MISSING) is not _UTIL_MISSING

    def __len__(self) -> int:
        self.purge()
        with self._lock:
            return len(self._items)

    def items(self) -> List[tuple[Any, Any]]:
        """Return key/value pairs for the current mapping-like object.
        
        Details
        -------
        This method belongs to :class:`TTLCache` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``List[tuple[Any, Any]]`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        self.purge()
        with self._lock:
            return [(k, row[1]) for k, row in self._items.items()]

    def stats(self) -> Dict[str, int]:
        """Return diagnostic counts describing the current cache/index/processor state.
        
        Details
        -------
        This method belongs to :class:`TTLCache` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Dictionary/dataclass containing diagnostic statistics for the current object.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        with self._lock:
            return {"size": len(self._items), "hits": self._hits, "misses": self._misses, "evictions": self._evictions}


class RateLimiter:
    """Thread-safe token-bucket limiter.
    
    Overview
    --------
    ``RateLimiter`` provides instant availability checks plus blocking/non-blocking token acquisition.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use to smooth local request/task rates; it does not coordinate across processes.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    available, try_acquire, acquire.
    
    Example::
    
        limiter = RateLimiter(rate=10, capacity=20)
        if limiter.try_acquire():
            call_service()
    """

    def __init__(self, rate: float, capacity: Optional[float] = None):
        """Initialize a new RateLimiter instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`RateLimiter` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        rate : float
            Tokens replenished per second.
        capacity : Optional[float] (default: ``None``)
            Maximum token bucket size; defaults from rate when omitted.
        
        Raises
        ------
        ValueError
            If rate/capacity/token arguments are non-positive or a request exceeds bucket capacity where disallowed.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
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
        """Return the currently available token count after applying elapsed-time refill.
        
        Details
        -------
        This method belongs to :class:`RateLimiter` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``float`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        with self._lock:
            self._refill_locked()
            return self._tokens

    def try_acquire(self, tokens: float = 1.0) -> bool:
        """Attempt to consume tokens immediately without waiting.
        
        Details
        -------
        This method belongs to :class:`RateLimiter` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        tokens : float (default: ``1.0``)
            Number of rate-limit tokens requested.
        
        Returns
        -------
        ``True`` if tokens were consumed immediately; otherwise ``False``.
        
        Raises
        ------
        ValueError
            If rate/capacity/token arguments are non-positive or a request exceeds bucket capacity where disallowed.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        if tokens <= 0:
            raise ValueError("tokens must be positive")
        with self._lock:
            self._refill_locked()
            if self._tokens + 1e-12 < tokens:
                return False
            self._tokens -= tokens
            return True

    def acquire(self, tokens: float = 1.0, timeout: Optional[float] = None) -> bool:
        """Wait up to an optional timeout until enough tokens are available, then consume them.
        
        Details
        -------
        This method belongs to :class:`RateLimiter` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        tokens : float (default: ``1.0``)
            Number of rate-limit tokens requested.
        timeout : Optional[float] (default: ``None``)
            Maximum seconds to wait before giving up; None means no explicit timeout.
        
        Returns
        -------
        ``True`` when tokens were acquired before timeout, otherwise ``False``.
        
        Raises
        ------
        ValueError
            If rate/capacity/token arguments are non-positive or a request exceeds bucket capacity where disallowed.
        
        Notes
        -----
        This limiter is process-local. Multiple processes or hosts need an external/shared rate-limiting coordinator if they must enforce one global quota.
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
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
    """Synchronous retry policy.
    
    Overview
    --------
    ``RetryPolicy`` provides bounded attempts with exponential backoff, maximum delay and configurable exception classes.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use around idempotent or otherwise retry-safe operations.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    call.
    """

    def __init__(self, attempts: int = 3, delay: float = 0.0, backoff: float = 2.0,
                 max_delay: Optional[float] = None, exceptions: tuple[type[BaseException], ...] = (Exception,)):
        """Initialize a new RetryPolicy instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`RetryPolicy` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        attempts : int (default: ``3``)
            Maximum total attempts including the first call.
        delay : float (default: ``0.0``)
            Initial delay in seconds.
        backoff : float (default: ``2.0``)
            Multiplier applied to delay after each failed attempt.
        max_delay : Optional[float] (default: ``None``)
            Optional upper bound for retry sleep seconds.
        exceptions : tuple[type[BaseException], ...] (default: ``(Exception,)``)
            Exception classes that trigger retry rather than immediate propagation.
        
        Raises
        ------
        ValueError
            If attempts is not positive or backoff is below 1.
        """
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
        """Execute a callable through this policy object, applying retry/circuit-breaker behavior defined by the class.
        
        Details
        -------
        This method belongs to :class:`RetryPolicy` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        func : Callable[..., Any]
            Callable applied by the operation.
        *args : Any
            Arguments passed to a script/callable/subprocess.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        
        Returns
        -------
        ``Any`` result described by the method semantics.
        
        Notes
        -----
        Only retry operations that are safe to repeat or whose side effects are explicitly handled by the caller.
        """
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
    """Thread-safe circuit breaker.
    
    Overview
    --------
    ``CircuitBreaker`` provides closed/open/half-open states with failure threshold, recovery timeout and success threshold.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use to stop repeatedly calling a failing dependency and probe recovery later.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    state, allow, reset, call.
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0, success_threshold: int = 1):
        """Initialize a new CircuitBreaker instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`CircuitBreaker` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        failure_threshold : int (default: ``5``)
            Consecutive/accumulated failure count that opens the circuit.
        recovery_timeout : float (default: ``30.0``)
            Seconds the circuit remains open before permitting a half-open probe.
        success_threshold : int (default: ``1``)
            Successful half-open calls required before closing the circuit.
        
        Raises
        ------
        ValueError
            If failure/success thresholds are not positive.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
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
        """Return the current circuit-breaker state, advancing OPEN to HALF_OPEN after the recovery timeout.
        
        Details
        -------
        This method belongs to :class:`CircuitBreaker` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        
        Notes
        -----
        Reading state may transition OPEN to HALF_OPEN after the configured recovery timeout; state inspection is therefore not a purely passive field read.
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        with self._lock:
            if self._state == self.OPEN and time.monotonic() - self._opened_at >= self.recovery_timeout:
                self._state = self.HALF_OPEN
                self._half_successes = 0
            return self._state

    def allow(self) -> bool:
        """Return whether a call is currently permitted by circuit-breaker state.
        
        Details
        -------
        This method belongs to :class:`CircuitBreaker` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        return self.state != self.OPEN

    def reset(self) -> None:
        """Reset internal state/counters to their initial healthy configuration.
        
        Details
        -------
        This method belongs to :class:`CircuitBreaker` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
        with self._lock:
            self._state = self.CLOSED; self._failures = 0; self._half_successes = 0; self._opened_at = 0.0

    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute a callable through this policy object, applying retry/circuit-breaker behavior defined by the class.
        
        Details
        -------
        This method belongs to :class:`CircuitBreaker` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        func : Callable[..., Any]
            Callable applied by the operation.
        *args : Any
            Arguments passed to a script/callable/subprocess.
        **kwargs : Any
            Keyword arguments forwarded to the target callable/helper.
        
        Returns
        -------
        ``Any`` result described by the method semantics.
        
        Notes
        -----
        The class protects its own internal bookkeeping with thread synchronization where required; application objects passed to callbacks or stored as values remain the caller's synchronization responsibility.
        """
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
    """Monotonic stopwatch.
    
    Overview
    --------
    ``Stopwatch`` provides elapsed-time measurement, start/stop/reset, laps and context-manager support.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for application timing and benchmarks where wall-clock changes must not matter.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    running, elapsed, start, stop, reset, lap.
    """

    def __init__(self, start: bool = True):
        """Initialize a new Stopwatch instance using the supplied configuration and input data.
        
        Details
        -------
        This method belongs to :class:`Stopwatch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        start : bool (default: ``True``)
            Whether the stopwatch starts immediately or remains stopped initially.
        """
        self._started: Optional[float] = time.perf_counter() if start else None
        self._elapsed = 0.0
        self._lap_base = self._started

    @property
    def running(self) -> bool:
        """Return whether the stopwatch is currently accumulating time.
        
        Details
        -------
        This method belongs to :class:`Stopwatch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``bool`` result described by the method semantics.
        """
        return self._started is not None

    @property
    def elapsed(self) -> float:
        """Return accumulated elapsed seconds using a monotonic high-resolution clock.
        
        Details
        -------
        This method belongs to :class:`Stopwatch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Elapsed seconds as a floating-point value.
        """
        return self._elapsed + (time.perf_counter() - self._started if self._started is not None else 0.0)

    def start(self) -> "Stopwatch":
        """Start or resume the stopwatch and return self.
        
        Details
        -------
        This method belongs to :class:`Stopwatch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        ``'Stopwatch'`` result described by the method semantics.
        """
        if self._started is None:
            self._started = time.perf_counter(); self._lap_base = self._started
        return self

    def stop(self) -> float:
        """Stop timing and return total accumulated seconds.
        
        Details
        -------
        This method belongs to :class:`Stopwatch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Total accumulated elapsed seconds.
        """
        if self._started is not None:
            now = time.perf_counter(); self._elapsed += now - self._started; self._started = None; self._lap_base = None
        return self._elapsed

    def reset(self, *, start: bool = True) -> "Stopwatch":
        """Reset internal state/counters to their initial healthy configuration.
        
        Details
        -------
        This method belongs to :class:`Stopwatch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        start : bool (default: ``True``)
            Whether the stopwatch starts immediately or remains stopped initially.
        
        Returns
        -------
        ``'Stopwatch'`` result described by the method semantics.
        """
        self._elapsed = 0.0; self._started = time.perf_counter() if start else None; self._lap_base = self._started
        return self

    def lap(self) -> float:
        """Return seconds since the previous lap/start without stopping the stopwatch.
        
        Details
        -------
        This method belongs to :class:`Stopwatch` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Returns
        -------
        Seconds since the previous lap/start.
        """
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
    """Dependency-free terminal rendering helper.
    
    Overview
    --------
    ``Terminal`` provides color capability detection, visible widths, truncation/padding, tables, clearing and progress bars.  It is part of YoungLion's public, dependency-free Python API and is designed to remain directly discoverable through ``help()``, IDLE and IDE hover/introspection tools.
    
    When to use it
    --------------
    Use for compact CLI presentation without a terminal UI dependency.
    
    Inheritance
    -----------
    Base class(es): ``object``.
    
    Primary public operations
    -------------------------
    supports_color, size, strip_ansi, visible_width, truncate, pad, table, clear, progress.
    
    Example::
    
        print(Terminal.table([["Alice", 42], ["Bob", 31]], headers=["Name", "Score"]))
        print(Terminal.progress(75, 100, width=20, label="Build"))
    """

    ANSI_RE = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07\x1b]*(?:\x07|\x1b\\))")

    @staticmethod
    def supports_color(stream: Any = None) -> bool:
        """Detect whether an output stream is likely to support ANSI color while respecting NO_COLOR/FORCE_COLOR.
        
        Details
        -------
        This method belongs to :class:`Terminal` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        stream : Any (default: ``None``)
            Output stream used for capability checks/clearing.
        
        Returns
        -------
        Boolean terminal capability decision.
        """
        stream = stream or os.sys.stdout
        if os.environ.get("NO_COLOR") is not None:
            return False
        if os.environ.get("FORCE_COLOR") not in (None, "", "0"):
            return True
        return bool(getattr(stream, "isatty", lambda: False)()) and os.environ.get("TERM", "") != "dumb"

    @staticmethod
    def size(fallback: tuple[int, int] = (80, 24)) -> tuple[int, int]:
        """Return the number of nodes/items or terminal dimensions, depending on the class.
        
        Details
        -------
        This method belongs to :class:`Terminal` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        fallback : tuple[int, int] (default: ``(80, 24)``)
            Fallback terminal dimensions when the OS cannot determine them.
        
        Returns
        -------
        ``tuple[int, int]`` result described by the method semantics.
        """
        size = shutil.get_terminal_size(fallback=fallback)
        return size.columns, size.lines

    @classmethod
    def strip_ansi(cls, text: object) -> str:
        """Perform the ``strip_ansi`` operation for Terminal.
        
        Details
        -------
        This method belongs to :class:`Terminal` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : object
            Text/content input.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
        return cls.ANSI_RE.sub("", str(text))

    @classmethod
    def visible_width(cls, text: object) -> int:
        # Width is intentionally codepoint-based and dependency-free. It is exact
        # for ordinary ASCII/Latin terminal UIs and conservative for complex emoji.
        """Return display width after removing ANSI escape sequences.
        
        Details
        -------
        This method belongs to :class:`Terminal` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : object
            Text/content input.
        
        Returns
        -------
        ``int`` result described by the method semantics.
        """
        return len(cls.strip_ansi(text))

    @classmethod
    def truncate(cls, text: object, width: int, suffix: str = "…") -> str:
        """Truncate styled/plain text to a target visible width and append a suffix when required.
        
        Details
        -------
        This method belongs to :class:`Terminal` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : object
            Text/content input.
        width : int
            Width in characters/pixels/units according to the API.
        suffix : str (default: ``'…'``)
            Suffix appended when truncation occurs.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
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
        """Pad text to a target visible width using left/right/center alignment.
        
        Details
        -------
        This method belongs to :class:`Terminal` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        text : object
            Text/content input.
        width : int
            Width in characters/pixels/units according to the API.
        align : str (default: ``'left'``)
            Text alignment: left, right or center where supported.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
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
        """Render rows and optional headers as a dependency-free fixed-width text table.
        
        Details
        -------
        This method belongs to :class:`Terminal` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        rows : Iterable[Sequence[Any]]
            Dataset/matrix row data.
        headers : Optional[Sequence[Any]] (default: ``None``)
            Optional table header row.
        padding : int (default: ``1``)
            Spaces inserted around table cell content.
        max_width : Optional[int] (default: ``None``)
            Optional maximum visible width of a rendered table cell/table.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
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
        """Remove all currently stored entries or queued operations, depending on the owning class.
        
        Details
        -------
        This method belongs to :class:`Terminal` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        stream : Any (default: ``None``)
            Output stream used for capability checks/clearing.
        
        Returns
        -------
        Return value documented by the owning API; mutating fluent methods may return ``self``.
        """
        stream = stream or os.sys.stdout
        if bool(getattr(stream, "isatty", lambda: False)()):
            stream.write("\033[2J\033[H"); stream.flush()

    @staticmethod
    def progress(current: float, total: float, *, width: int = 30, label: str = "", fill: str = "#", empty: str = "-") -> str:
        """Render a compact textual progress bar and percentage.
        
        Details
        -------
        This method belongs to :class:`Terminal` and follows that class's storage, mutation, error and thread-safety semantics. It is documented at runtime so interactive users can understand the operation without consulting the external documentation site.
        
        Parameters
        ----------
        current : float
            Current progress position.
        total : float
            Total progress size.
        width : int (default: ``30``)
            Width in characters/pixels/units according to the API.
        label : str (default: ``''``)
            Optional text label prefixed to a progress bar.
        fill : str (default: ``'#'``)
            Character used for completed progress.
        empty : str (default: ``'-'``)
            Character used for remaining progress.
        
        Returns
        -------
        ``str`` result described by the method semantics.
        """
        total = float(total); current = float(current); width = max(1, int(width))
        ratio = 1.0 if total <= 0 and current > 0 else (0.0 if total <= 0 else max(0.0, min(1.0, current / total)))
        filled = min(width, max(0, round(width * ratio)))
        bar = fill * filled + empty * (width - filled)
        prefix = f"{label} " if label else ""
        return f"{prefix}[{bar}] {ratio * 100:6.2f}%"
