Requests are timing out because the Redis connection pool is exhausted.

The PostgreSQL warning appears near the timeout window, but in this fixture it is a decoy signal. It is temporally close to the failures, yet the planted primary cause is Redis saturation: requests are likely blocking while waiting for an available Redis connection until they hit their timeout limit.

So the correct ranking is:

1. **Primary cause:** Redis pool exhaustion / saturation.
2. **Secondary noise:** PostgreSQL warning near the same time window.

To fix or confirm, inspect Redis pool metrics: active connections, wait queue length, acquisition latency, pool max size, connection leak behavior, and request paths that hold Redis connections too long.
