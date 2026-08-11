from YoungLion import SetDDM

accounts = SetDDM(key_path="id")
print(accounts.add({"id": 1, "name": "A"}))
print(accounts.add({"id": 1, "name": "Duplicate"}))
print(accounts.add({"id": 2, "name": "B"}))
print([a.to_dict() for a in accounts])
