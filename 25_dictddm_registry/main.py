from YoungLion import DictDDM

users = DictDDM({
    "alice": {"score": 10, "active": True},
    "bob": {"score": 20, "active": False},
})
users.increment("score", 5)
print(users["alice"].score)
print(users.keys_for("active", True))
