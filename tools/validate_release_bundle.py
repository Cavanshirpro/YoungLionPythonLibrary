#!/usr/bin/env python3
"""Validate a YoungLion release bundle without requiring PyPI credentials."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    root = args.bundle
    manifest_path = root / "checksums" / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for row in manifest["files"]:
        path = root / row["file"]
        if not path.is_file():
            raise SystemExit(f"Missing: {row['file']}")
        if path.stat().st_size != row["size"]:
            raise SystemExit(f"Size mismatch: {row['file']}")
        if sha256(path) != row["sha256"]:
            raise SystemExit(f"SHA256 mismatch: {row['file']}")
    stable = list((root / "pypi").iterdir())
    if not any(p.suffix == ".whl" for p in stable):
        raise SystemExit("No stable wheel")
    if sum(p.name.endswith(".tar.gz") for p in stable) != 1:
        raise SystemExit("Expected exactly one sdist")
    print(f"OK: {len(manifest['files'])} distributions verified")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
