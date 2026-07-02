**Assessment**

Evidence is insufficient to prove a root cause, but the strongest hypothesis is Redis shared-pool saturation after `profile_cache_v2`.

**Ranked Hypotheses**

1. **Hypothesis:** Redis connection-pool saturation is driving the timeout spike, likely triggered by `profile_cache_v2` batched `MGET`.
   **Evidence present:** checkout API requests show ~2.3-2.47s latency with `redis_timeout_ms=250` and `feature_profile_cache_v2=true` at `02:10:04-02:10:07` in `logs.txt`. Redis shows `pool_size=20 in_use=20` with `pool_wait_ms=244/251`, including `command=MGET key_prefix=profile_cache_v2` in `logs.txt`. `deploy.json` says `profile_cache_v2` is enabled and changed profile lookups from one `GET` to batched `MGET` using the shared Redis pool.
   **Missing evidence:** Redis pool wait percentiles, timeout counts, command volume by key prefix, and before/after flag comparison.

2. **Hypothesis:** PostgreSQL slowness is contributing but is probably correlated, not primary.
   **Evidence present:** one PostgreSQL query took `934ms` in `logs.txt`, but API-side `pg_ms` values are only `78-91ms` while total request latency is >2.3s and Redis timeouts are present in the same API lines.
   **Missing evidence:** PG p95/p99 latency, lock waits, connection pool saturation, slow query frequency, and whether PG latency remains high after Redis pressure is relieved.

3. **Hypothesis:** A broader traffic or concurrency spike exhausted shared resources.
   **Evidence present:** Redis pool is fully used at `20/20` in `logs.txt`.
   **Missing evidence:** RPS, checkout concurrency, worker queue depth, Redis command rate by caller, and app instance saturation.

**Next Three Inspections**

1. Redis dashboard: pool `in_use/max`, `pool_wait_ms` p95/p99, Redis timeout count, command rate by `GET`/`MGET`, and key prefix around deploy time `2026-07-02T01:54:00Z`.

2. Feature flag/deploy dashboard: compare checkout latency/error rate for `profile_cache_v2=true` vs false, then verify whether disabling or rolling back the flag reduces Redis pool waits.

3. PostgreSQL dashboard or `pg_stat_statements`/`pg_stat_activity`: inspect accounts query latency, locks, active connections, and wait events during the same window.
