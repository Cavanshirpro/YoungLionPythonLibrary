from __future__ import annotations

import time

import pytest

from YoungLion import DDM
from YoungLion.DataModel import (
    Color, DefaultDDM, DictDDM, FrozenDDM, LazyDDM, ListDDM, Matrix, PackedDDM,
    Point, SchemaDDM, SetDDM, Size, TreeDDM, Vector, ViewDDM,
)
from YoungLion.search import ApplicationSearch, DDMSearchEngine, SearchAlgorithm


def make_rows(count=100):
    return ListDDM(
        DDM({
            "id": i,
            "profile": DDM({"name": f"User {i}", "age": 18 + (i % 50), "city": "Baku" if i % 2 == 0 else "Ganja"}),
            "score": float(i),
        })
        for i in range(count)
    )


def test_native_collection_batch_and_algorithms():
    rows = make_rows(100)
    assert rows.path_values("profile.age")[:3] == [18, 19, 20]
    assert len(rows.filter_path("profile.age", 60, op="ge")) == 16
    assert rows.increment("score", 2) == 100
    assert rows.sum("score") == pytest.approx(sum(range(100)) + 200)
    assert rows.mean("score") == pytest.approx((sum(range(100)) + 200) / 100)
    ordered = rows.sort_by("score")
    assert ordered[0].score == 2.0 and ordered[-1].score == 101.0
    rows.sort_by("score", inplace=True)
    assert rows.is_sorted("score")
    assert rows.lower_bound("score", 52.0) == 50
    assert rows.nth("score", 50).score == 52.0
    assert rows.nth("score", 0, largest=True).score == 101.0
    assert rows.clamp("score", 10, 20) == 100
    assert rows.min("score") == 10
    assert rows.max("score") == 20


def test_bulk_operations():
    rows = make_rows(20)
    rows.set_all("profile.active", True)
    assert all(rows.path_values("profile.active"))
    rows.apply_path("profile.name", str.upper)
    assert rows[0].profile.name == "USER 0"
    assert rows.count_by("profile.city")["Baku"] == 10
    assert set(rows.distinct("profile.city")) == {"Baku", "Ganja"}
    rows.copy_path("profile.city", "location.city")
    assert rows[1].get_path("location.city") == "Ganja"
    rows.rename_path("location.city", "location.name")
    assert rows[1].get_path("location.name") == "Ganja"
    rows.delete_path("location.name")
    assert not rows[1].has_path("location.name")
    rows.fill_missing("profile.country", "AZ")
    assert set(rows.path_values("profile.country")) == {"AZ"}


def test_list_set_dict_ddm():
    rows = make_rows(10)
    mapping = DictDDM({str(i): row for i, row in enumerate(rows)})
    assert mapping.keys_for("profile.city", "Baku") == ["0", "2", "4", "6", "8"]
    unique = SetDDM(rows, key=lambda d: d.id)
    assert len(unique) == 10
    assert not unique.add(DDM({"id": 1, "profile": DDM({"name": "duplicate"})}))
    unique.add(DDM({"id": 99}))
    assert len(unique) == 11


def test_ddm_path_indexes_and_composite():
    rows = make_rows(500)
    engine = rows.indexed("profile.name", "profile.age", "id")
    engine.create_composite_index("profile.city", "profile.age")
    assert engine.find_one("profile.name", "User 321").id == 321
    assert [x.id for x in engine.between("profile.age", 20, 22)[:3]] == [2, 52, 102]
    assert engine.where(profile__age__gte=60, profile__city="Baku")
    composite = engine.composite(("profile.city", "profile.age"), ("Baku", 20))
    assert composite and all(x.profile.city == "Baku" and x.profile.age == 20 for x in composite)
    fuzzy = engine.text("profile.name", "Usr 321", algorithm=SearchAlgorithm.HYBRID, limit=3)
    assert any(x.id == 321 for x in fuzzy)


def test_index_invalidation_on_collection_batch_mutation():
    rows = make_rows(20)
    engine = rows.indexed("profile.city")
    assert len(engine.find("profile.city", "Baku")) == 10
    rows.set_all("profile.city", "Lankaran")
    assert len(engine.find("profile.city", "Lankaran")) == 20


def test_ddm_variants():
    frozen = FrozenDDM({"profile": {"name": "A"}, "values": [1, 2]})
    assert frozen.profile.name == "A"
    assert isinstance(hash(frozen), int)
    with pytest.raises(TypeError): frozen["x"] = 1

    packed = PackedDDM({"profile": DDM({"name": "B"})})
    assert packed.get_path("profile.name") == "B"
    packed.set_path("profile.name", "C")
    assert packed.profile.name == "C"

    raw = {"x": 1}; view = ViewDDM(raw); view["x"] = 2; assert raw["x"] == 2
    lazy = LazyDDM({"x": 2}, {"double": lambda d: d.x * 2}); assert lazy.double == 4
    lazy.x = 3; lazy.invalidate("double"); assert lazy.double == 6
    defaults = DefaultDDM({}, list); assert defaults.missing == []


def test_models():
    assert Size(1920, 1080).aspect_ratio == pytest.approx(16/9)
    assert Point(0, 0).distance_to(Point(3, 4)) == 5
    assert Color.from_hex("#FF0000").to_hex() == "#FF0000"
    assert Matrix.identity(2).matmul(Matrix([[2, 3], [4, 5]])).rows == [[2.0, 3.0], [4.0, 5.0]]
    root = TreeDDM("root"); root.add_child("a").add_child("b")
    assert root.size() == 3 and root.find(lambda n: n.value == "b").value == "b"


def test_application_search():
    search = ApplicationSearch()
    search.add(1, "Discord moderation bot", "fast automod", tags=["discord", "bot"], fields={"category": "bot"}, payload="A")
    search.add(2, "Minecraft server manager", "panel", tags=["minecraft"], fields={"category": "tool"}, payload="B")
    assert search.search("discord")[0] == "A"
    assert search.facet("category") == [("bot", 1), ("tool", 1)]
    assert search.suggest("Disc")[0].payload == 1


def test_builtin_collection_sources_and_identity_ddm():
    from YoungLion import DDM, FrozenDDM, IdentityDDM
    from YoungLion.search import DDMSearchEngine

    a = DDM({"profile": {"name": "Alice", "age": 30}})
    b = DDM({"profile": {"name": "Bob", "age": 20}})
    assert DDMSearchEngine([a, b]).find("profile.name", "Alice") == [a]
    assert DDMSearchEngine({"a": a, "b": b}).find("profile.age", 20) == [b]

    i1 = IdentityDDM({"profile": {"name": "Set One"}})
    i2 = IdentityDDM({"profile": {"name": "Set Two"}})
    source_set = {i1, i2}
    assert DDMSearchEngine(source_set).find("profile.name", "Set Two") == [i2]

    frozen = FrozenDDM({"profile": {"name": "Frozen"}})
    assert DDMSearchEngine({frozen}).find("profile.name", "Frozen") == [frozen]


def test_batch_plan_single_pass_and_index_invalidation():
    from YoungLion import ListDDM
    rows = ListDDM([
        {"profile": {"age": 17}, "score": 1},
        {"profile": {"age": 80}, "score": 2},
    ])
    engine = rows.indexed("score", "profile.age")
    assert engine.find("score", 1)[0].profile["age"] == 17
    plan = rows.batch().add("score", 10).clamp("profile.age", 18, 65).set("active", True)
    assert plan.execute(rows) == 6
    assert [r.score for r in rows] == [11.0, 12.0]
    assert [r.profile["age"] for r in rows] == [18.0, 65.0]
    assert len(engine.find("score", 11.0)) == 1


def test_application_search_update_keeps_body_and_autocomplete_clean():
    from YoungLion.search import ApplicationSearch
    app = ApplicationSearch()
    app.add(1, "Alpha Tool", "special searchable body", payload={"id": 1})
    app.update(1, title="Beta Tool")
    assert app.search("special")[0] == {"id": 1}
    assert [x.term for x in app.suggest("Beta")] == ["Beta Tool"]
    assert app.suggest("Alpha", fuzzy=False) == []
    assert app.remove(1)
    assert app.suggest("Beta", fuzzy=False) == []


def test_setddm_rehashes_after_bulk_mutation_and_key_path_optimization():
    rows = SetDDM([
        {"id": 1, "profile": {"name": "A"}, "score": 10},
        {"id": 2, "profile": {"name": "B"}, "score": 20},
    ], key_path="id")
    first = next(iter(rows))
    rows.increment("score", 5)
    # Non-key mutation must keep O(1) membership structure coherent.
    assert first in rows
    rows.increment("id", 10)
    assert first in rows
    assert DDM({"id": 11, "profile": {"name": "A"}, "score": 15.0}) in rows

    content_keyed = SetDDM([{"id": 1, "x": 1}, {"id": 2, "x": 2}])
    content_keyed.increment("x", 1)
    assert DDM({"id": 1, "x": 2.0}) in content_keyed


def test_search_shared_record_store_and_refresh_after_structural_mutation():
    rows = ListDDM([
        {"id": i, "profile": {"name": f"User {i}", "age": i % 50}}
        for i in range(100)
    ])
    engine = rows.indexed("profile.name", "profile.age")
    name_index = engine._indexes["profile.name"]
    age_index = engine._indexes["profile.age"]
    assert name_index._objects is age_index._objects
    assert name_index._entries == () and age_index._entries == ()
    rows.append({"id": 100, "profile": {"name": "Added", "age": 42}})
    assert engine.find_one("profile.name", "Added").id == 100


def test_ddm_indexed_queries_match_native_scan_randomized():
    import random
    random.seed(1234)
    rows = ListDDM([
        {
            "id": i,
            "profile": {
                "age": random.randint(10, 90),
                "name": random.choice(["Alice", "Bob", "Carol", "Dave"]) + str(i % 7),
                "city": random.choice(["Baku", "Ganja", "Lankaran"]),
            },
        }
        for i in range(1200)
    ])
    engine = rows.indexed("profile.age", "profile.name", "profile.city")
    for age in (10, 20, 42, 90):
        indexed = {x.id for x in engine.find("profile.age", age)}
        scanned = {x.id for x in engine.find("profile.age", age, use_index=False)}
        assert indexed == scanned
    for city in ("Baku", "Ganja", "Lankaran"):
        assert {x.id for x in engine.find("profile.city", city)} == {x.id for x in engine.find("profile.city", city, use_index=False)}
    for threshold in (25, 50, 75):
        assert {x.id for x in engine.find("profile.age", threshold, op="ge")} == {x.id for x in engine.find("profile.age", threshold, op="ge", use_index=False)}
        assert {x.id for x in engine.find("profile.age", threshold, op="lt")} == {x.id for x in engine.find("profile.age", threshold, op="lt", use_index=False)}


def test_native_cpp_algorithm_surface():
    rows = ListDDM([{"v": v, "group": v % 2} for v in [1, 2, 2, 2, 3, 5, 8]])
    assert rows.count_path("group", 0) == 4
    even, odd = rows.partition_path("group", 0)
    assert [x.v for x in even] == [2, 2, 2, 8]
    assert [x.v for x in odd] == [1, 3, 5]
    assert rows.binary_search("v", 2) == 1
    assert rows.equal_range("v", 2) == (1, 4)
    assert rows.binary_search("v", 4) == -1
    with pytest.raises(ValueError):
        ListDDM([{"v": 2}, {"v": 1}]).binary_search("v", 1)


def test_schema_ddm_accepts_valid_native_result():
    from YoungLion import SchemaDDM
    user = SchemaDDM({"name": "A", "age": 18}, {"name": str, "age": int})
    assert user.age == 18
    user.set_validated("age", 19)
    assert user.age == 19
