# Release bundle

`build-artifacts.yml` first executes the **Release preflight** job. If the source,
metadata, strict native build, tests, type-stub audit, or tag/version check fails,
no stable distribution matrix is started.

After preflight, individual matrix jobs upload component artifacts. The final
assembly produces one artifact with this layout:

```text
YoungLion-0.1.1-release-bundle/
├── pypi/                 # stable wheels + exactly one sdist
├── experimental/         # preview targets; do not upload by default
├── checksums/
│   ├── MANIFEST.json
│   └── SHA256SUMS.txt
└── UPLOAD_TO_PYPI.md
```

`tools/assemble_release_bundle.py` combines components, separates experimental
files, detects filename collisions, and writes SHA-256 metadata.
`tools/validate_release_bundle.py` verifies file existence, sizes, hashes, stable
wheel presence, and the single-sdist invariant.

Only `pypi/` is intended for the normal manual PyPI upload. The workflows contain
no PyPI token, `twine upload`, Trusted Publishing permission, or automatic GitHub
Release step.
