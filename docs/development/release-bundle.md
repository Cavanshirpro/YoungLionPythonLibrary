# Release bundle

Individual matrix jobs upload component artifacts. The final assembly produces one release bundle:

```text
YoungLion-0.1.0-release-bundle/
├── pypi/
├── experimental/
├── checksums/
└── UPLOAD_TO_PYPI.md
```

`tools/assemble_release_bundle.py` combines components, separates experimental files and writes SHA-256 metadata. `tools/validate_release_bundle.py` verifies the result. Only `pypi/` is intended for the normal manual PyPI upload.
