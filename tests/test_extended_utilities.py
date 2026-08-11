from __future__ import annotations

import time
import pytest

import sys
from pathlib import Path

from YoungLion.function import FileTransferManager, Logger, ScriptRunner, TaskScheduler, TextProcessor


def test_script_runner_structured_result(tmp_path: Path):
    script = tmp_path / "hello.py"
    script.write_text("print('ok')", encoding="utf-8")
    runner = ScriptRunner()
    result = runner.run([sys.executable, str(script)], check=True)
    assert result.ok and result.stdout.strip() == "ok" and result.duration >= 0
    assert runner.run_script(str(script)).strip() == "ok"


def test_scheduler_resume_and_result():
    output = []
    scheduler = TaskScheduler()
    task = scheduler.schedule_task(lambda: output.append(1) or 42, delay=0.03)
    assert scheduler.pause_task(task)
    assert scheduler.resume_task(task)
    info = scheduler.wait(task, timeout=2)
    assert info and info.state == "completed" and info.last_result == 42 and output == [1]
    scheduler.shutdown()


def test_logger_rotation(tmp_path: Path):
    log = Logger(str(tmp_path / "app.log"), console=False, max_bytes=80, backup_count=2)
    for i in range(10): log.info("message", i=i)
    assert (tmp_path / "app.log").exists()
    assert (tmp_path / "app.log.1").exists()


def test_local_transfer(tmp_path: Path):
    src = tmp_path / "a.bin"; dst = tmp_path / "b.bin"; src.write_bytes(b"abc" * 100)
    manager = FileTransferManager(); tid = manager.upload(str(src), str(dst), protocol="local")
    assert dst.read_bytes() == src.read_bytes() and manager.get_status(tid) == "completed" and manager.get_progress(tid) == 100


def test_text_processor():
    text = TextProcessor("Hello world. Email me@example.com and visit https://example.com")
    assert text.word_count() >= 7
    assert text.sentence_count() == 2
    assert text.extract_emails() == ["me@example.com"]
    assert text.extract_urls() == ["https://example.com"]
    assert text.similarity("Hello world", "Hello world") == 1.0
    assert text.stats()["words"] == text.word_count()


def test_event_bus_ttl_cache_and_rate_limiter():
    from YoungLion import EventBus, TTLCache, RateLimiter
    bus = EventBus(); seen = []
    bus.subscribe("event", lambda value: seen.append(("normal", value)), priority=1)
    bus.once("event", lambda value: seen.append(("once", value)), priority=10)
    bus.emit("event", 1); bus.emit("event", 2)
    assert seen == [("once", 1), ("normal", 1), ("normal", 2)]

    cache = TTLCache(max_size=2, default_ttl=None)
    cache.set("a", 1); cache.set("b", 2); assert cache.get("a") == 1
    cache.set("c", 3)
    assert "b" not in cache and cache.get("c") == 3

    limiter = RateLimiter(rate=1000, capacity=2)
    assert limiter.try_acquire(2)
    assert not limiter.try_acquire(1)
    assert limiter.acquire(1, timeout=0.02)


def test_retry_circuit_breaker_and_stopwatch():
    from YoungLion import RetryPolicy, CircuitBreaker, Stopwatch
    state = {"n": 0}
    def flaky():
        state["n"] += 1
        if state["n"] < 3:
            raise ValueError("retry")
        return "ok"
    assert RetryPolicy(attempts=3).call(flaky) == "ok"

    breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=0.01)
    try:
        breaker.call(lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    except RuntimeError:
        pass
    assert breaker.state == breaker.OPEN
    deadline = time.monotonic() + 1.0
    while breaker.state != breaker.HALF_OPEN and time.monotonic() < deadline:
        time.sleep(0.01)
    assert breaker.state == breaker.HALF_OPEN
    assert breaker.call(lambda: 42) == 42
    assert breaker.state == breaker.CLOSED

    sw = Stopwatch(); time.sleep(0.002); assert sw.elapsed > 0; assert sw.stop() > 0


def test_terminal_and_colors_helpers():
    from YoungLion import Colors, Terminal
    colored = Colors.wrap("hello", Colors.rgb(10, 20, 30), Colors.BRIGHT)
    assert Colors.strip(colored) == "hello"
    assert Terminal.visible_width(colored) == 5
    table = Terminal.table([["Alice", 30], ["Bob", 20]], headers=["Name", "Age"])
    assert "Alice" in table and "Name" in table
    assert "50.00%" in Terminal.progress(5, 10, width=10)
    assert Colors.ansi256(255).startswith("\x1b[")
    with pytest.raises(ValueError): Colors.rgb(256, 0, 0)
