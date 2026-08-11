from YoungLion import FrozenDDM

permission = FrozenDDM({"user_id": 7, "roles": ["admin", "editor"]})
cache = {permission: "ALLOW"}
print(cache[permission])
print("Mutable copy:", permission.thaw())
