from YoungLion import TTLCache

cache = TTLCache(max_size=3, default_ttl=10)
cache.set("user:1", {"name": "Alice"})
cache.set("user:2", {"name": "Bob"})
print(cache.get("user:1"))
print(cache.stats())
