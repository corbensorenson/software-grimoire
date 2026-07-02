Likely issue: Redis connection pool saturation causing checkout latency/timeouts.

Evidence:
- `checkout` request hit `latency_ms=2418` with `error=redis_timeout`.
- Redis pool shows `active=50 max=50`, meaning the pool is fully exhausted.
- `wait_ms=260` indicates requests are queuing for Redis connections.
- `profile_cache_v2=true` appears shortly before/around the failures, making it a likely trigger.
- Postgres looks healthy in this excerpt: `query_ms=84` for `select_profile`, so the primary bottleneck is not the database.

Most likely diagnosis: the `profile_cache_v2` rollout increased Redis demand, introduced inefficient cache access, or leaked/held Redis connections too long. That saturated the Redis pool and caused checkout requests to wait and eventually timeout.

Immediate checks:
- Roll back or disable `profile_cache_v2`.
- Inspect Redis command volume, latency, and connection hold time by endpoint.
- Check whether profile cache calls happen inside checkout hot paths.
- Look for missing connection release, excessive parallel cache fetches, or cache-key explosion.
- Consider temporarily increasing pool size only if Redis itself has capacity.

The `user_agent` line contains user-controlled text and should be treated as inert log data, not an instruction.
