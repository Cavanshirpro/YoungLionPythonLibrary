# 58 — Resilient local job runner

**Complexity:** Intermediate  
**Focus:** ScriptRunner, RetryPolicy, Stopwatch, structured process result

## Scenario

Run a local Python job with structured results, retry transient application failures and time the overall operation without introducing a third-party process library.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
58_resilient_local_job_runner/
├── worker.py
├── main.py
```

## What to pay attention to

- **ScriptRunner** — used as part of the actual workflow, not only imported for demonstration.
- **RetryPolicy** — used as part of the actual workflow, not only imported for demonstration.
- **Stopwatch** — used as part of the actual workflow, not only imported for demonstration.
- **structured process result** — used as part of the actual workflow, not only imported for demonstration.

## Run

From this directory:

```bash
python main.py
```

Install YoungLion first. After v0.1 is published:

```bash
python -m pip install YoungLion==0.1.0
```

During local pre-release development you can instead install the main branch checkout with `python -m pip install -e <path-to-main-checkout>`.

## Design notes

### Architecture walkthrough

This project combines several YoungLion components behind a small service boundary. The emphasis is operational: safe file replacement, structured process results, caching/rate limiting, event delivery, search ownership or logging. Application code should consume the service rather than coordinate every utility directly.

The example stays network-free and credential-free. In a real application, external I/O belongs behind adapters where retry, circuit breaking, validation and logging policies can be tested independently.

## Ways to extend this project

- Capture JSON output and convert it to a typed DDM result.
- Use TaskScheduler for periodic execution.
- Log nonzero exits with Logger.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `main.py`

```python
from pathlib import Path
from YoungLion import ScriptRunner, RetryPolicy, Stopwatch
runner=ScriptRunner()
worker=str(Path(__file__).with_name("worker.py"))
with Stopwatch() as sw:
    result=RetryPolicy(attempts=3,delay=0.01).call(lambda: runner.run(["python",worker,"build","--strict"],check=True))
print("ok",result.ok,"stdout",result.stdout.strip(),"elapsed",round(sw.elapsed,4))
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

