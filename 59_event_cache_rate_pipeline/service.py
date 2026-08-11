from YoungLion import EventBus, TTLCache, RateLimiter
class ProfileService:
    def __init__(self): self.bus=EventBus(); self.cache=TTLCache(max_size=128,default_ttl=60); self.limit=RateLimiter(rate=100,capacity=5); self.calls=0
    def _load(self,user_id): self.calls+=1; return {"id":user_id,"name":f"User {user_id}"}
    def get(self,user_id):
        cached=self.cache.get(user_id)
        if cached is not None: return cached
        if not self.limit.acquire(timeout=0.1): raise RuntimeError("rate limit")
        value=self._load(user_id); self.cache.set(user_id,value); self.bus.emit("loaded",value); return value
