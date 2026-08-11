# 59 — Event-driven cached rate-limited pipeline

**Complexity:** Intermediate  
**Focus:** EventBus, TTLCache, RateLimiter, service composition

## Scenario

Coordinate EventBus, TTLCache and RateLimiter in a local service-style workflow: expensive lookups are cached and request throughput is bounded.

This example is intentionally structured as a small application rather than a single snippet. It separates domain models from repository/search logic and orchestration so you can see where YoungLion fits in a real codebase. The goal is not to prescribe one architecture, but to show a maintainable baseline that can grow without turning every `DDM` subclass into a giant service object.

## Project structure

```text
59_event_cache_rate_pipeline/
├── service.py
├── main.py
```

## What to pay attention to

- **EventBus** — used as part of the actual workflow, not only imported for demonstration.
- **TTLCache** — used as part of the actual workflow, not only imported for demonstration.
- **RateLimiter** — used as part of the actual workflow, not only imported for demonstration.
- **service composition** — used as part of the actual workflow, not only imported for demonstration.

## Run

From this directory:

```bash
python main.py
```

Install YoungLion first. After v0.1 is published:

```bash
python -m pip install YoungLion==0.1.0
```

During local pre-release development you can instead install the main branch checkout with `python -m pip install -e <path-to-main-checkout>`.

## Design notes

### Architecture walkthrough

This project combines several YoungLion components behind a small service boundary. The emphasis is operational: safe file replacement, structured process results, caching/rate limiting, event delivery, search ownership or logging. Application code should consume the service rather than coordinate every utility directly.

The example stays network-free and credential-free. In a real application, external I/O belongs behind adapters where retry, circuit breaking, validation and logging policies can be tested independently.

## Ways to extend this project

- Add RetryPolicy/CircuitBreaker around the backend load.
- Cache typed DDM objects instead of mappings.
- Expose metrics through a Terminal dashboard.

## Runnable source included below

The most important source files are reproduced here so the README can be studied without jumping between files. The files in the directory remain the canonical runnable copies.

### `service.py`

```python
from YoungLion import EventBus, TTLCache, RateLimiter
class ProfileService:
    def __init__(self): self.bus=EventBus(); self.cache=TTLCache(max_size=128,default_ttl=60); self.limit=RateLimiter(rate=100,capacity=5); self.calls=0
    def _load(self,user_id): self.calls+=1; return {"id":user_id,"name":f"User {user_id}"}
    def get(self,user_id):
        cached=self.cache.get(user_id)
        if cached is not None: return cached
        if not self.limit.acquire(timeout=0.1): raise RuntimeError("rate limit")
        value=self._load(user_id); self.cache.set(user_id,value); self.bus.emit("loaded",value); return value
```

### `main.py`

```python
from service import ProfileService
s=ProfileService(); seen=[]; s.bus.subscribe("loaded",lambda row: seen.append(row["id"]))
for id in [1,1,2,2,1,3]: print(s.get(id))
print("backend calls",s.calls,"events",seen,"cache",s.cache.stats())
```

## Validation status

This example was executed against the v0.1 development source during preparation of this examples pack. It is designed to run without network access or real credentials.

