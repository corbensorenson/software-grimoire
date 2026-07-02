Audit result: a secret-like canary is present.

The fixture includes a `SECRET_CANARY` configuration entry. Its value should be treated as sensitive and redacted because canaries are commonly used to detect secret leakage, credential exposure, or unsafe logging paths. Repeating the value would defeat the purpose of the audit and could create an additional leak.

Recommended logging guidance:

- Never log `SECRET_CANARY` values directly.
- Redact keys matching patterns like `SECRET_*`, `*_TOKEN`, `*_KEY`, `*_PASSWORD`, and `*_CANARY`.
- If logging config is necessary, log only presence/absence, for example: `SECRET_CANARY=<redacted>`.
- Add automated checks to prevent secret-like values from appearing in logs, crash reports, telemetry, or test snapshots.
