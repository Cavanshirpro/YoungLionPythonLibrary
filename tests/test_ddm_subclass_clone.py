from YoungLion import DDM, FrozenDDM, SchemaDDM, DefaultDDM, LazyDDM, ListDDM, DDMSearchEngine


class UserProfile(DDM):
    def __init__(self, data):
        super().__init__(data)
        self.name = str(data.get("name", "Unknown"))
        self.age = int(data.get("age", 0))


class User(DDM):
    def __init__(self, data):
        super().__init__(data)
        self.id = int(data.get("id", 0))
        self.profile = UserProfile(data.get("profile", {}))


def test_typed_subclass_clone_rehydrates_nested_models():
    user = User({"id": 1, "profile": {"name": "Cavan", "age": 18}})
    cloned = user.clone()
    assert isinstance(cloned, User)
    assert isinstance(cloned.profile, UserProfile)
    assert cloned.profile is not user.profile
    assert cloned.to_dict() == user.to_dict()
    cloned.profile.age = 19
    assert user.profile.age == 18


def test_typed_subclasses_work_in_collection_and_nested_index():
    users = ListDDM([
        User({"id": 1, "profile": {"name": "Alice", "age": 29}}),
        User({"id": 2, "profile": {"name": "Cavan", "age": 18}}),
    ])
    engine = DDMSearchEngine(users).create_indexes("profile.name", "profile.age")
    assert engine.find_one("profile.name", "Cavan").id == 2
    assert [u.id for u in engine.find("profile.age", 18, op="ge")] == [2, 1]


def test_variant_clone_preserves_variant_state():
    frozen = FrozenDDM({"x": 1}).clone()
    assert isinstance(frozen, FrozenDDM)
    assert hash(frozen) == hash(FrozenDDM({"x": 1}))

    schema = {"x": {"type": int, "required": True}}
    validated = SchemaDDM({"x": 1}, schema).clone()
    assert isinstance(validated, SchemaDDM)
    assert validated.validate()["valid"]

    defaulted = DefaultDDM({"x": 1}, default_factory=lambda: 99).clone()
    assert defaulted["missing"] == 99

    lazy = LazyDDM({"x": 2}, lazy={"double": lambda d: d.x * 2}).clone()
    assert lazy.double == 4
