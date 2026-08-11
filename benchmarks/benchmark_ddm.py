from __future__ import annotations

import copy
import platform
import sys
import timeit
from YoungLion import DDM, SmartCache
from YoungLion.search import InvertedIndex, tokenize
from YoungLion import _native

DATA = {
    "id": 42,
    "profile": {"name": "YoungLion", "flags": [True, False, True]},
    "items": [{"id": i, "name": f"item-{i}", "meta": {"score": i * 2}} for i in range(100)],
}
FLAT = {f"field_{i}": i for i in range(200)}
MODEL = DDM(DATA)
FLAT_MODEL = DDM(FLAT)
CACHE = SmartCache({"id": 0, "profile": {"name": "", "score": 0}, "active": True})
RAW = {"id": 9, "profile": {"name": "YL"}}


class LegacyDDM:
    def __init__(self, data):
        self._data = dict(data)
        for key, value in data.items():
            setattr(self, key, value)


def python_plain(value):
    if isinstance(value, dict):
        return {k: python_plain(v) for k, v in value.items()}
    if isinstance(value, list):
        return [python_plain(v) for v in value]
    if isinstance(value, tuple):
        return tuple(python_plain(v) for v in value)
    return value


def python_complete(template, raw):
    result = copy.deepcopy(raw)
    for key, value in template.items():
        if key not in result:
            result[key] = copy.deepcopy(value)
        elif isinstance(value, dict) and isinstance(result[key], dict):
            result[key] = python_complete(value, result[key])
    return result


def bench(label, stmt, number=10_000):
    elapsed = timeit.timeit(stmt, number=number)
    print(f"{label:36} {elapsed:.6f}s  ({number / elapsed:,.0f} ops/s)")
    return elapsed


def search_benchmark():
    documents = []
    for i in range(5_000):
        base = ["younglion", "native", "search", "filesystem", f"item{i}"]
        if i % 25 == 0:
            base += ["mentalist", "detective"]
        documents.append(base)
    index = InvertedIndex()
    for i, tokens in enumerate(documents):
        index.add(i, tokens)
    query = tokenize("native detective")

    naive = bench("Native rebuild-all BM25", lambda: _native.bm25_scores(query, documents), 100)
    posting = bench("Persistent posting-list BM25", lambda: index.bm25(query), 100)
    print(f"BM25 repeated-query ratio:          {naive / posting:.2f}x")


def memory_report():
    legacy = LegacyDDM(FLAT)
    new_shallow = sys.getsizeof(FLAT_MODEL) + sys.getsizeof(FLAT_MODEL.__dict__)
    old_shallow = sys.getsizeof(legacy) + sys.getsizeof(legacy.__dict__) + sys.getsizeof(legacy._data)
    saved = old_shallow - new_shallow
    pct = (saved / old_shallow * 100.0) if old_shallow else 0.0
    print(f"Legacy flat shallow storage:        {old_shallow:,} bytes")
    print(f"0.1 DDM flat shallow storage:       {new_shallow:,} bytes")
    print(f"Shallow storage reduction:          {saved:,} bytes ({pct:.1f}%)")


if __name__ == "__main__":
    print("YoungLion 0.1 native benchmark")
    print(f"Python: {platform.python_version()} | {platform.platform()}")
    print()
    memory_report()
    print()
    py_flat = bench("Python dict.copy (flat baseline)", lambda: FLAT.copy(), 25_000)
    native_flat = bench("YoungLion flat DDM.to_dict", FLAT_MODEL.to_dict, 25_000)
    print(f"Flat copy ratio (baseline/native):  {py_flat / native_flat:.2f}x")
    py = bench("Python recursive to_dict", lambda: python_plain(DATA), 5_000)
    native = bench("YoungLion nested DDM.to_dict", MODEL.to_dict, 5_000)
    print(f"Nested to_dict ratio (py/native):   {py / native:.2f}x")
    pyc = bench("Python template complete", lambda: python_complete(CACHE.template, RAW), 20_000)
    nativec = bench("Native SmartCache.complete", lambda: CACHE.complete(RAW), 20_000)
    print(f"SmartCache ratio (py/native):       {pyc / nativec:.2f}x")
    print()
    search_benchmark()
