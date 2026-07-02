Requests are most likely timing out because `profile_cache_v2` is saturating the shared Redis connection pool.

**Facts:**
- `profile_cache_v2` was enabled in the deploy at `2026-07-02T01:54:00Z`.
- Around `2026-07-02T02:10:04Z` to `02:10:09Z`, checkout requests show high latency: `2318-2470ms`.
- Those same API logs include `redis_timeout_ms=250` and `feature_profile_cache_v2=true`.
- Redis logs show the pool fully exhausted: `pool_size=20 in_use=20`, with `pool_wait_ms=244` and `251`.
- The recent change switched profile lookups from one `GET` to batched `MGET` calls using the shared Redis pool.

**Most likely hypothesis:**
`profile_cache_v2` increased Redis pool pressure enough that requests wait near or beyond the Redis timeout threshold. That Redis wait then pushes checkout request latency into timeout territory.

**PostgreSQL:**
There is one slow PostgreSQL query at `934ms`, but the API request logs show `pg_ms` around `78-91ms`. Based on this packet, PostgreSQL looks correlated or secondary, not the primary cause.

**Missing signals:**
We would need Redis pool wait metrics over time, Redis command latency, MGET batch sizes, timeout/error rates split by feature flag state, and before/after deploy comparisons to prove it.

**Next checks:**
Disable or roll back `profile_cache_v2` and verify whether checkout timeouts and Redis pool waits drop. Also inspect Redis pool saturation metrics and consider isolating profile-cache traffic from the shared pool or resizing/backpressuring the pool.
