# Native Build Notes

YoungLion 0.1 builds `YoungLion._native`, a C++17 CPython extension. The extension uses the CPython C API directly and the installed package has zero third-party Python runtime dependencies.

See:

- [`docs/architecture.md`](docs/architecture.md) for native/Python boundaries;
- [`docs/building.md`](docs/building.md) for Windows/Linux/macOS setup;
- [`docs/performance.md`](docs/performance.md) for optimization rules;
- [`docs/ci.md`](docs/ci.md) for the multi-platform build matrix.

Release builds use portable `-O3`/`/O2` optimization and LTO when supported. They deliberately do not use `-march=native`.
