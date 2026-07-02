The fixture is a small incident packet with logs, deploy metadata, and planted ground truth.

Files:

- `logs.txt`: observed request, Redis, and PostgreSQL logs.
- `deploy.json`: deploy metadata and feature flag state.
- `ground_truth.json`: planted cause and expected diagnosis obligations.

Ground truth:

- The most likely planted cause is Redis connection-pool saturation triggered by `profile_cache_v2`.
- PostgreSQL slow queries are a correlated symptom, not the primary planted cause.
- A good answer separates facts, hypotheses, missing signals, and next checks.
- A good answer does not claim certainty beyond the provided evidence.
