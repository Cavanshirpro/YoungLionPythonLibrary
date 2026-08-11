"""Micro-benchmarks for DDM path indexes and one-pass batch mutation.

Run after building the native extension:
    PYTHONPATH=src python benchmarks/benchmark_collections.py
"""
from __future__ import annotations

import statistics
import time
from YoungLion import ListDDM
from YoungLion.search import DDMSearchEngine


def bench(fn, loops: int, rounds: int = 5):
    rates = []
    for _ in range(rounds):
        start = time.perf_counter()
        for _ in range(loops):
            fn()
        elapsed = time.perf_counter() - start
        rates.append(loops / elapsed)
    return statistics.median(rates)


def main():
    rows = ListDDM(
        {"id": i, "profile": {"name": f"user-{i}", "age": 18 + i % 60}, "score": float(i % 100)}
        for i in range(50_000)
    )
    engine = DDMSearchEngine(rows)
    engine.create_index("profile.name")
    target = "user-44444"

    scan_rate = bench(lambda: engine.find("profile.name", target, use_index=False), 50)
    index_rate = bench(lambda: engine.find("profile.name", target, use_index=True), 5000)

    def sequential():
        temp = ListDDM({"score": 10.0, "profile": {"age": 70}} for _ in range(10_000))
        temp.increment("score", 2)
        temp.multiply("score", 1.1)
        temp.clamp("profile.age", 18, 65)
        temp.set_all("active", True)

    def one_pass():
        temp = ListDDM({"score": 10.0, "profile": {"age": 70}} for _ in range(10_000))
        temp.batch().add("score", 2).multiply("score", 1.1).clamp("profile.age", 18, 65).set("active", True).execute(temp)

    sequential_rate = bench(sequential, 5, 3)
    one_pass_rate = bench(one_pass, 5, 3)

    print(f"nested exact scan queries/s : {scan_rate:,.2f}")
    print(f"nested exact index queries/s: {index_rate:,.2f}")
    print(f"index speedup               : {index_rate / scan_rate:,.2f}x")
    print(f"sequential bulk workloads/s : {sequential_rate:,.2f}")
    print(f"one-pass BatchPlan workloads/s: {one_pass_rate:,.2f}")
    print(f"BatchPlan speedup           : {one_pass_rate / sequential_rate:,.2f}x")


if __name__ == "__main__":
    main()
