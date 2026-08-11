# Contributing

For every public API change: update runtime code, matching `.pyi`, tests and documentation. Run normal + strict native build, compileall and full pytest suite. Performance changes should have correctness coverage and a representative benchmark; do not gain speed by silently losing search recall or changing semantics.
