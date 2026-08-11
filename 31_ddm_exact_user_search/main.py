from YoungLion import ListDDM, DDMSearchEngine

users = ListDDM({"id": i, "profile": {"name": f"User {i}"}} for i in range(100))
engine = DDMSearchEngine(users)
engine.create_index("profile.name")
print(engine.find_one("profile.name", "User 73").id)
