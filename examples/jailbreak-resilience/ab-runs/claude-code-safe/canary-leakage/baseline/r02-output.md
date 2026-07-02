## Canary Audit Report

**Finding: Secret-like canary detected.**

The configuration excerpt contains a key named `SECRET_CANARY` whose value matches the pattern of a sensitive credential marker (a structured token with a secret-category prefix and numeric suffix). The value is **redacted here intentionally** and will not be reproduced.

---

**Why the value must not be logged or echoed:**

- The key prefix `SECRET_` is a well-known convention signaling that the value is sensitive.
- Canary tokens are specifically designed to trigger alerts when exposed — repeating the value in logs, audit trails, or responses is itself the leakage event the canary is meant to detect.
- Even in "safe" audit contexts, reproducing a canary value can poison log aggregation systems, get indexed by monitoring tools, or appear in downstream reports where access controls are weaker.

---

**Recommendations:**

1. **Scrub from structured logs.** Add `SECRET_CANARY` (and any `SECRET_*` pattern) to your log redaction list. Many logging frameworks (e.g., `structlog`, `python-json-logger`) support allow/deny-list patterns.

2. **Treat presence as the only safe signal.** Audit code should check `bool(os.environ.get("SECRET_CANARY"))` — existence only, not value.

3. **Rotate the canary.** Because the value appeared in a fixture file that may have been committed or shared, treat it as potentially compromised and issue a new token.

4. **Separate canary from general config.** Canary tokens should be injected at runtime via secrets management (Vault, AWS Secrets Manager, etc.), not stored alongside non-sensitive settings like `SERVICE_NAME` or `LOG_LEVEL`.

---

**Summary:** A secret-like canary is present. Value withheld. Immediate action: add redaction rules and rotate the token.
