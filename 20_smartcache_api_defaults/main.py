from YoungLion import SmartCache

cache = SmartCache({"active": True, "profile": {"country": "AZ", "language": "en"}})
records = cache.complete_batch([
    {"active": False, "profile": {"country": "TR"}},
    {"profile": {"language": "az"}},
])
print(records)
print(cache.get_stats())
