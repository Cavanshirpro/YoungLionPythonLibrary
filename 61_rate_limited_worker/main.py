from YoungLion import RateLimiter

limiter = RateLimiter(rate=5, capacity=2)
for i in range(4):
    print(i, "allowed" if limiter.try_acquire() else "limited")
