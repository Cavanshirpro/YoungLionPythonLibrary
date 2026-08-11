# Troubleshooting

## `_native` ImportError
The extension was not built for the active interpreter/platform. Rebuild with the same Python executable.

## pip is compiling and fails
No matching wheel exists. Install C++ build tools/Python headers or choose a supported wheel target.

## DDM index looks stale
Direct external mutation bypassed collection invalidation. Call `invalidate()` or `refresh()`.

## SetDDM duplicate-key error after mutation
The mutation produced two records with the same uniqueness key. Resolve data or choose another uniqueness strategy.

## Complex YAML/PDF behavior missing
YoungLion deliberately avoids large runtime dependencies. Use a dedicated library in the application for standards-complete advanced behavior.
