# Benchmark methodology

Run benchmarks on the deployment Python/compiler/CPU. Build release native code, warm up, use enough iterations, compare identical semantics, report data size/shape, separate index build from repeated query timing, and measure memory separately from throughput.

Microbenchmarks are not whole-application speedups; callbacks and I/O can dominate.
