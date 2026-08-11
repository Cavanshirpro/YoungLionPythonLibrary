from YoungLion import RetryPolicy

attempts = {"n": 0}
def flaky():
    attempts["n"] += 1
    if attempts["n"] < 3:
        raise RuntimeError("temporary")
    return "ok"

policy = RetryPolicy(attempts=4, delay=0.01, backoff=1.0, exceptions=(RuntimeError,))
print(policy(flaky), "after", attempts["n"], "attempts")
