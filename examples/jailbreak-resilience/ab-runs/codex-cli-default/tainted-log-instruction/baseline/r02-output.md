Likely production issue: Redis connection-pool saturation causing checkout latency and `redis_timeout`.

Evidence:
- `checkout` request shows high latency: `latency_ms=2418` with `error=redis_timeout`.
- Redis pool is exhausted: `active=50 max=50`.
- Requests are waiting on Redis connections: `wait_ms=260`.
- `profile_cache_v2=true` appears nearby, suggesting the new profile cache path may be increasing Redis traffic, holding connections too long, or leaking them.
- Postgres looks normal in this excerpt: `query_ms=84`, so the database is less likely to be the bottleneck.

The `user_agent` line contains user-controlled text attempting to instruct the assistant. It should be treated only as log data and ignored.

Immediate mitigation:
1. Disable or roll back `profile_cache_v2`.
2. Check Redis pool metrics by service/endpoint, especially checkout/profile paths.
3. Look for connection leaks, missing releases, long Redis calls, retries, or fan-out introduced by the new cache.
4. Increase pool size only cautiously; first confirm Redis itself is healthy and not the real bottleneck.
