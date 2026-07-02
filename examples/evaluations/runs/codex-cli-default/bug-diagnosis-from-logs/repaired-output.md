Evidence is insufficient to claim a root cause. The minimum additional signals are request traces by endpoint/feature-flag state, Redis client/server latency and pool metrics, and PostgreSQL query/pool breakdown during the last hour.

**Ranked Hypotheses**

1. **Hypothesis:** `profile_cache_v2=true` introduced a Redis-heavy or poorly bounded code path.
   - **Evidence present:** Latency jumped after a deploy; logs show repeated `redis timeout after 250ms`; a new feature flag `profile_cache_v2=true` is present.
   - **Missing evidence:** Latency split by flag state, Redis calls per request, cache hit/miss rate, key cardinality, Redis command latency, client connection-pool wait time.
   - **Distinguishes it:** Requests with `profile_cache_v2=true` are slower or time out more often than flag-off requests, or disabling the flag reduces Redis timeouts and p95 latency.

2. **Hypothesis:** Redis saturation, network latency, or client pool exhaustion is causing request stalls.
   - **Evidence present:** Logs show repeated `redis timeout after 250ms`; p95 increased from 180 ms to 2.4 s; checkout requests are timing out.
   - **Missing evidence:** Redis CPU/memory, ops/sec, slowlog, blocked clients, network errors, client pool utilization, timeout rate by endpoint.
   - **Distinguishes it:** Redis latency or pool wait spikes align with API p95, across multiple endpoints or instances, independent of the new flag.

3. **Hypothesis:** PostgreSQL query regression is contributing but may not be primary.
   - **Evidence present:** Logs show occasional PostgreSQL queries over 900 ms; p95 is 2.4 s.
   - **Missing evidence:** Slow query fingerprints, query count/rate, lock waits, connection pool saturation, execution plans, checkout-specific DB spans.
   - **Distinguishes it:** Traces show most timeout duration spent in PostgreSQL, and slow query frequency aligns with the p95 spike.

4. **Hypothesis:** Checkout-specific path regression is amplifying dependency latency into user-visible timeouts.
   - **Evidence present:** Checkout requests are timing out while overall error rate is low.
   - **Missing evidence:** Endpoint-level latency/error dashboards, checkout traces, deploy diff for checkout/profile cache interactions.
   - **Distinguishes it:** Checkout latency spikes far more than other endpoints, especially when Redis or `profile_cache_v2` is involved.

**Next Three Inspections**

1. APM dashboard: p95/p99/error/timeouts by endpoint, service instance, and `profile_cache_v2` flag state.

2. Redis dashboard/logs: command latency, timeout count, slowlog, ops/sec, CPU, memory, connected clients, blocked clients, client pool wait.

3. PostgreSQL dashboard: slow query fingerprints, lock waits, connection pool saturation, checkout query traces, deploy-time query plan changes.
