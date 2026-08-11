from YoungLion import CircuitBreaker

breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=60)
def fail():
    raise RuntimeError("service unavailable")

for _ in range(2):
    try: breaker(fail)
    except RuntimeError: pass
print("State:", breaker.state, "Allowed now:", breaker.allow())
