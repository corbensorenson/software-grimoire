Requests are timing out because the Redis connection pool is exhausted.

The PostgreSQL warning near the timeout window is a decoy/noisy signal. The primary failure mode is Redis saturation: requests are likely blocking while waiting to acquire a Redis connection, which stalls request handling until the upstream/request timeout is hit.

What to check first:

- Redis pool active connections at max
- pending/waiting Redis connection acquisitions
- Redis pool acquire latency rising before request timeout
- leaked Redis clients or missing releases
- per-request Redis call volume
- pool size vs app concurrency

The database warning may be secondary, correlated, or caused by the same request backlog, but based on the provided context it is not the root cause.
