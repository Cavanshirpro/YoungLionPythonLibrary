from YoungLion import ListDDM, DDMSearchEngine

users = ListDDM({"id": i, "profile": {"age": 15 + i}} for i in range(30))
engine = DDMSearchEngine(users).create_indexes("profile.age")
print([u.id for u in engine.between("profile.age", 18, 21)])
