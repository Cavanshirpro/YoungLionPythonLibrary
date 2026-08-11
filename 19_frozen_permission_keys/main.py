from YoungLion import FrozenDDM

def permission(resource: str, action: str):
    return FrozenDDM({"resource": resource, "action": action})

allowed = {permission("users", "read"), permission("users", "write"), permission("audit", "read")}
required = permission("audit", "read")
print("allowed:", required in allowed)
cache = {required: {"checked": True, "source": "role:admin"}}
print(cache[required])
