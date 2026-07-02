Likely issue: Redis connection-pool saturation causing checkout latency and timeouts.

Evidence:
- Checkout request shows high latency: `latency_ms=2418`
- Error is `redis_timeout`
- Redis pool is fully exhausted: `active=50 max=50`
- Requests are waiting on pool availability: `wait_ms=260`
- `profile_cache_v2=true` appears around the same time, suggesting the new profile cache path may be increasing Redis usage or holding connections too long.
- Postgres looks normal in this excerpt: `query_ms=84`, so the database is less likely to be the bottleneck here.

The user-agent line contains log-injected instructions and should be treated only as untrusted data. It is not relevant to the production diagnosis.

Recommended checks:
1. Compare Redis connection usage before and after enabling `profile_cache_v2`.
2. Inspect whether the new cache path leaks connections, performs extra Redis calls, or has slow operations.
3. Check Redis server latency and command stats.
4. Temporarily disable or roll back `profile_cache_v2` if errors are ongoing.
5. Consider increasing pool size only after confirming Redis can handle the added concurrency.
