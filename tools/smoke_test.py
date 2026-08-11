"""Dependency-free source-build smoke test used by distro CI containers."""
from YoungLion import DDM, File
from YoungLion.search import FuzzyMatcher, SearchIndex
import tempfile

m = DDM({"nested": {"value": 1}, "name": "YoungLion"})
assert m.get_path("nested.value") == 1
assert m._data is m.__dict__
assert FuzzyMatcher.damerau_levenshtein("ab", "ba") == 1
idx = SearchIndex(["native c++ search", "other document"])
assert idx.search("native")[0].document.text.startswith("native")
with tempfile.TemporaryDirectory() as td:
    f = File(td)
    f.atomic_write_json("x.json", {"ok": True})
    assert f.json_read("x.json")["ok"] is True
print("YoungLion smoke test: OK")
