Requests are most likely timing out because Redis connections are saturated after `profile_cache_v2` was enabled.

**Facts**
- `profile_cache_v2` is enabled.
- Recent deploy changed profile lookups from single Redis `GET` calls to batched `MGET` calls using the shared Redis pool.
- Checkout requests show ~2.3-2.5s latency with `redis_timeout_ms=250`.
- Redis logs show `pool_size=20` and `in_use=20`, with `pool_wait_ms` around 244-251ms.
- There is one PostgreSQL slow query at 934ms.

**Best Hypothesis**
The new `profile_cache_v2` behavior is exhausting the shared Redis connection pool. Requests then wait roughly the Redis timeout window before continuing/failing, causing checkout latency spikes and timeouts.

**Why PostgreSQL Is Lower-Ranked**
PostgreSQL is slow in one log line, but the Redis pool is fully saturated and its wait time matches the configured Redis timeout much more directly. The DB slowness looks correlated, not the primary cause in this packet.

**Missing Evidence**
To confirm, I would want Redis pool metrics over time: saturation, wait duration, timeout count, command volume, and checkout latency split by feature flag state.

**Next Checks**
- Disable or roll back `profile_cache_v2` and verify checkout latency drops.
- Compare Redis pool usage before and after the 2026-07-02T01:54:00Z deploy.
- Check whether `MGET` calls increased pool hold time or request fanout.
