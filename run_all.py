from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).parent
FOLDERS = sorted(p for p in ROOT.iterdir() if p.is_dir() and p.name[:2].isdigit())
WORKERS = max(1, min(4, os.cpu_count() or 1))


def run_one(folder: Path) -> tuple[str, int, str, str]:
    main = folder / "main.py"
    if not main.exists():
        return folder.name, 0, "(no main.py; skipped)", ""
    try:
        proc = subprocess.run(
            [sys.executable, str(main)],
            cwd=folder,
            text=True,
            capture_output=True,
            timeout=60,
        )
        return folder.name, proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        return folder.name, 124, exc.stdout or "", "timed out after 60 seconds"


failures: list[tuple[str, int]] = []
results = {}
with ThreadPoolExecutor(max_workers=WORKERS) as pool:
    futures = {pool.submit(run_one, folder): folder for folder in FOLDERS}
    for future in as_completed(futures):
        name, code, stdout, stderr = future.result()
        results[name] = (code, stdout, stderr)

for folder in FOLDERS:
    code, stdout, stderr = results[folder.name]
    print(f"== {folder.name} ==")
    if stdout.strip():
        print(stdout.rstrip())
    if code:
        if stderr.strip():
            print(stderr.rstrip(), file=sys.stderr)
        failures.append((folder.name, code))

print(f"passed={len(FOLDERS) - len(failures)} failed={len(failures)} workers={WORKERS}")
if failures:
    print(failures, file=sys.stderr)
    raise SystemExit(1)
