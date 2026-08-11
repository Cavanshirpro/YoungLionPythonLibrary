# Continuous integration

`native-ci.yml` validates source builds on Windows/Linux/macOS, strict compiler diagnostics, clean Linux distribution containers and optional Windows ARM preview.

`build-artifacts.yml` creates the source distribution and stable wheels, plus opt-in experimental platform/architecture components. It does not publish to PyPI and does not require PyPI credentials.
