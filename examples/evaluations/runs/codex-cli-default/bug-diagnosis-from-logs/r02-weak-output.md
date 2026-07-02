Requests are most likely timing out because `profile_cache_v2` is saturating the shared Redis connection pool.

**Facts**
- `profile_cache_v2` is enabled.
- Recent deploy changed profile lookups from single Redis `GET` calls to batched `MGET` calls using the shared Redis pool.
- Redis logs show `pool_size=20` and `in_use=20`, with `pool_wait_ms=244-251`.
- API logs show `redis_timeout_ms=250`, so Redis pool wait is reaching the Redis timeout threshold.
- Checkout request latency is around `2318-2470ms`.
- API-side PostgreSQL timings are low on the timed-out checkout requests: `78-91ms`.

**Hypothesis**
The new `profile_cache_v2` batched Redis behavior is exhausting the shared Redis pool. Requests then wait about 250ms for a Redis connection, hit the Redis timeout, and overall checkout latency climbs until requests time out.

**Not primary from this evidence**
There is one PostgreSQL slow query at `934ms`, but the checkout request logs do not show PostgreSQL as the dominant latency source. Based on the packet, PostgreSQL looks correlated, not the primary planted cause.

**Missing signals**
I would want Redis pool utilization over time, MGET command volume/latency, request timeout budget, error rates by feature flag state, and before/after metrics around the `2026-07-02T01:54:00Z` deploy.

**Next checks**
Disable or roll back `profile_cache_v2` and verify whether Redis `in_use`, `pool_wait_ms`, Redis timeouts, and checkout latency drop. If they do not, then investigate PostgreSQL separately.
