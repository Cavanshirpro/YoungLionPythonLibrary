#!/usr/bin/env python3
"""Assemble GitHub Actions component artifacts into one manual-PyPI bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tomllib
from pathlib import Path


def project_version(project_root: Path) -> str:
    with (project_root / "pyproject.toml").open("rb") as fh:
        return str(tomllib.load(fh)["project"]["version"])


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_distribution(path: Path) -> bool:
    return path.suffix == ".whl" or path.name.endswith(".tar.gz")


def is_experimental(path: Path) -> bool:
    return any("EXPERIMENTAL" in part.upper() for part in path.parts)


def copy_unique(source: Path, destination: Path) -> Path:
    target = destination / source.name
    if target.exists():
        if sha256(target) == sha256(source):
            return target
        raise RuntimeError(f"Conflicting distribution filename: {source.name}")
    shutil.copy2(source, target)
    return target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--collected", type=Path, required=True, help="Directory populated by actions/download-artifact")
    parser.add_argument("--output-parent", type=Path, default=Path("."))
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--git-sha", default="")
    parser.add_argument("--run-id", default="")
    args = parser.parse_args()

    version = project_version(args.project_root)
    root = args.output_parent / f"YoungLion-{version}-release-bundle"
    if root.exists():
        shutil.rmtree(root)
    stable = root / "pypi"
    experimental = root / "experimental"
    checksums = root / "checksums"
    stable.mkdir(parents=True)
    experimental.mkdir()
    checksums.mkdir()

    files = sorted(p for p in args.collected.rglob("*") if p.is_file() and is_distribution(p))
    if not files:
        raise RuntimeError(f"No distribution files found under {args.collected}")

    for source in files:
        copy_unique(source, experimental if is_experimental(source) else stable)

    stable_files = sorted(p for p in stable.iterdir() if p.is_file())
    wheels = [p for p in stable_files if p.suffix == ".whl"]
    sdists = [p for p in stable_files if p.name.endswith(".tar.gz")]
    if not wheels:
        raise RuntimeError("Release bundle has no stable wheel")
    if len(sdists) != 1:
        raise RuntimeError(f"Release bundle must contain exactly one stable sdist, found {len(sdists)}")

    rows = []
    for channel, directory in (("pypi", stable), ("experimental", experimental)):
        for path in sorted(directory.iterdir()):
            if path.is_file():
                rows.append({
                    "file": str(path.relative_to(root)),
                    "size": path.stat().st_size,
                    "sha256": sha256(path),
                    "channel": channel,
                })

    manifest = {
        "project": "YoungLion",
        "version": version,
        "git_sha": args.git_sha or None,
        "github_run_id": args.run_id or None,
        "stable_distributions": len([r for r in rows if r["channel"] == "pypi"]),
        "experimental_distributions": len([r for r in rows if r["channel"] == "experimental"]),
        "files": rows,
    }
    (checksums / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (checksums / "SHA256SUMS.txt").write_text(
        "".join(f"{row['sha256']}  {row['file']}\n" for row in rows), encoding="utf-8"
    )
    (root / "UPLOAD_TO_PYPI.md").write_text(
        f"""# YoungLion {version} — manual PyPI upload

The `pypi/` directory is the complete stable upload set. Do **not** upload `experimental/` unless you intentionally decide to publish a preview build.

```bash
cd pypi
python -m pip install --upgrade twine
python -m twine check *
python -m twine upload *
```

Before upload, verify `../checksums/SHA256SUMS.txt` and preferably install representative wheels in clean virtual environments.
""",
        encoding="utf-8",
    )
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
