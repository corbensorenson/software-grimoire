Evidence is insufficient for a certain root cause, but enough to rank Redis pool saturation first.

**Ranked Hypotheses**
1. **Redis shared-pool saturation triggered by `profile_cache_v2` MGET usage.**
   Evidence: Redis logs show `pool_size=20 in_use=20` with `pool_wait_ms=244` and `251`; API logs show `redis_timeout_ms=250`; deploy metadata says `profile_cache_v2` changed profile lookups from one `GET` to batched `MGET` using the shared Redis pool.

2. **`profile_cache_v2` rollout caused a request-path latency regression.**
   Evidence: deploy at `2026-07-02T01:54:00Z`; logs at `2026-07-02T02:10:04Z` through `02:10:09Z` show `feature_profile_cache_v2=true` and checkout latencies around `2318-2470ms`. Hypothesis: the rollout timing and enabled flag are causally related.

3. **PostgreSQL slowness is contributing, but likely not primary from supplied evidence.**
   Evidence: one PostgreSQL log shows `duration_ms=934`; however API request logs show `pg_ms=78`, `83`, and `91` while Redis timeout is consistently `250ms`. Hypothesis: PG slowness may be correlated load or fallback behavior, not the main timeout driver.

**Missing Evidence**
- Redis pool wait, in-use, timeout, and command-latency time series before/after `01:54Z`.
- Request traces showing exact time spent waiting for Redis pool vs executing Redis vs PostgreSQL.
- Feature-flag exposure percentage and whether affected requests all use `profile_cache_v2`.
- PostgreSQL p95/p99 query latency, lock waits, connection saturation, and active session counts.

**Next Three Inspections**
1. Redis dashboard: pool `in_use/pool_size`, pool wait p95/p99, timeout count, command latency by `GET`/`MGET`, filtered around `2026-07-02T01:54Z-02:15Z`.

2. Feature flag/deploy dashboard: confirm `profile_cache_v2` rollout timing, exposure, and test disable/rollback while watching checkout latency and Redis pool wait.

3. APM/tracing plus DB dashboard: inspect slow checkout traces split by Redis pool wait, Redis command time, PostgreSQL query time, and compare requests with `profile_cache_v2=true` vs false.
