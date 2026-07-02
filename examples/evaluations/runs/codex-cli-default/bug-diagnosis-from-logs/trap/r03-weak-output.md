Requests are timing out because the Redis connection pool is saturated/exhausted. Requests that need Redis are likely waiting for an available Redis connection until they hit the timeout window.

The PostgreSQL warning is a decoy signal: it appears near the timeout window, but the planted primary cause is Redis pool exhaustion, not database latency.

So the failure chain is:

`Redis pool exhausted -> requests queue/block waiting for Redis -> request timeout`

The PostgreSQL warning may be secondary noise or a symptom of late-stage request pressure, but it should not be ranked above the Redis saturation signal.
