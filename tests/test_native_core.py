from __future__ import annotations

import tempfile
from pathlib import Path

from YoungLion import DDM, DDMBuilder, Dataset, File, Range, SmartCache, Timeline, Vector


def test_ddm_core_roundtrip():
    model = DDM({"name": "Alice", "address": {"city": "Baku"}, "items": [{"id": 1}]})
    assert model.to_dict()["name"] == "Alice"
    assert model.get_path("address.city") == "Baku"
    assert model.set_path("address.city", "Lankaran")
    assert model.has_path("address.city")
    assert model.get_path("address.city") == "Lankaran"
    cloned = model.clone().update(name="Bob")
    assert model.name == "Alice"
    assert cloned.name == "Bob"
    assert model.diff(cloned)["name"] == {"old": "Alice", "new": "Bob"}
    encoded = model.to_json()
    assert DDM.from_json(encoded).to_dict() == model.to_dict()


def test_ddm_helpers_and_models():
    built = DDMBuilder().set("x", 1).nest("child", lambda b: b.set("y", 2)).build()
    assert built.get_path("child.y") == 2
    assert Range(0, 10).normalize(5) == 0.5
    assert round(Vector([3, 4]).magnitude(), 8) == 5.0
    assert Vector([1, 2, 3]).cross(Vector([4, 5, 6])).components == [-3.0, 6.0, -3.0]
    timeline = Timeline(0, 20)
    timeline.add_event(10, "late")
    timeline = timeline.copy()
    assert timeline.get_event("late")["time"] == 10
    dataset = Dataset(rows=[{"x": 1}, {"x": 3}])
    assert dataset.stats("x")["mean"] == 2.0


def test_smart_cache_native_completion():
    cache = SmartCache({"id": 0, "profile": {"name": "", "score": 0}})
    result = cache.complete({"id": 7, "profile": {"name": "YL"}})
    assert result == {"id": 7, "profile": {"name": "YL", "score": 0}}
    assert cache.get_missing_keys({"id": 7}) == ["profile"]
    assert cache.get_stats()["completed"] >= 1


def test_file_core_roundtrip():
    with tempfile.TemporaryDirectory() as td:
        f = File(td)
        assert f.create_folder("data")
        f.json_write("data/a.json", {"unicode": "şə", "values": [1, 2]})
        assert f.json_read("data/a.json")["unicode"] == "şə"
        f.txt_write_str("data/a.txt", "one\ntwo")
        assert f.txt_read_linear("data/a.txt") == {"1": "one", "2": "two"}
        f.csv_write("data/a.csv", [{"id": "1", "name": "A"}, {"id": "2", "name": "B"}])
        assert f.csv_read("data/a.csv")[1]["name"] == "B"
        f.ini_write("data/a.ini", {"main": {"enabled": "true"}})
        assert f.ini_read("data/a.ini")["main"]["enabled"] == "true"
        f.properties_write("data/a.properties", {"k": "v"})
        assert f.properties_read("data/a.properties")["k"] == "v"
        f.pdf_write("data/a.pdf", "Hello PDF\nSecond line")
        assert f.pdf_read("data/a.pdf") == "Hello PDF\nSecond line"
        assert f.copy_file("data/a.txt", "data/b.txt")
        assert f.move_file("data/b.txt", "data/c.txt")
        assert Path(td, "data", "c.txt").exists()
        assert f.delete_file("data/c.txt")


def test_zero_third_party_runtime_imports():
    # Public native hot paths must import using only CPython + stdlib.
    import YoungLion.DataModel
    import YoungLion.function
    assert YoungLion.DataModel.DDM is DDM
    assert YoungLion.function.File is File


def test_nested_defaults_xml_yaml_and_csv_edge_cases():
    with tempfile.TemporaryDirectory() as td:
        f = File(td)
        f.json_write("defaults.json", {"outer": {"present": 1}})
        value = f.json_read("defaults.json", {"outer": {"present": 0, "missing": 2}, "top": 3})
        assert value == {"outer": {"present": 1, "missing": 2}, "top": 3}

        xml = {"item": [{"@attributes": {"id": "1"}, "#text": "alpha"}, {"#text": "beta"}]}
        f.xml_write("data.xml", xml)
        loaded = f.xml_read("data.xml")
        assert isinstance(loaded, dict)
        assert loaded["item"][0]["@attributes"]["id"] == "1"

        yaml = {"server": {"host": "localhost", "port": 8080, "enabled": True}, "tags": ["a", "b"]}
        f.yaml_write("data.yml", yaml)
        assert f.yaml_read("data.yml") == yaml

        rows = [{"a": "hello,world", "b": 'a"b', "c": "line1\nline2"}, {"a": "şə", "b": "", "c": "x"}]
        f.csv_write("quoted.csv", rows)
        assert f.csv_read("quoted.csv") == rows


def test_script_runner_uses_stdlib_only():
    from YoungLion import ScriptRunner
    import sys
    with tempfile.TemporaryDirectory() as td:
        script = Path(td, "echo.py")
        script.write_text("import sys; print('|'.join(sys.argv[1:]))", encoding="utf-8")
        out = ScriptRunner(sys.executable).run_script(str(script), inputs=["a", "b"])
        assert out.strip() == "a|b"


def test_ddm_private_fields_omitted_and_clone_isolated():
    model = DDM({"public": 1, "nested": {"items": [1, 2]}})
    model._temporary = "private"
    plain = model.to_dict()
    assert "_temporary" not in plain
    clone = model.clone()
    clone.nested["items"].append(3)
    assert model.nested["items"] == [1, 2]
    assert clone.nested["items"] == [1, 2, 3]


def test_native_json_unicode_surrogates_and_number_grammar():
    from YoungLion import _native

    assert _native.json_loads(r'{"emoji":"\ud83d\ude00"}') == {"emoji": "😀"}
    assert _native.json_loads('{"unicode":"Azərbaycan"}') == {"unicode": "Azərbaycan"}
    for invalid in ('01', '1.', '1e', r'"\ud800"', '"line\nbreak"'):
        try:
            _native.json_loads(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid JSON accepted: {invalid!r}")
