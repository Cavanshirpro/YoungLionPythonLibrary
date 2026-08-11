# Caching and resilience

`TTLCache` is bounded in-process memoization with expiration. `RateLimiter` is a token bucket. `RetryPolicy` handles transient retryable failures. `CircuitBreaker` stops repeatedly hitting an unhealthy dependency and transitions CLOSED → OPEN → HALF_OPEN.

Retry and circuit breaking are complementary but should wrap only operations whose retry semantics are understood.
