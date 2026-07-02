## Billing API Design

### Core Principles

This design explicitly addresses the two most common production failure modes in billing APIs: **duplicate charges from retries** and **breaking client error handling across versions**.

---

### Idempotency

Every mutating operation requires a client-supplied `Idempotency-Key` header (UUID). The server stores the key and its response for 24 hours. Replaying a request with the same key returns the cached response with a `X-Idempotency-Replayed: true` header — no double-charge.

```
POST /v1/charges
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000

{ "customer_id": "cus_123", "amount_cents": 4999, "currency": "usd" }
```

Keys are scoped per API credential. A key collision from a *different* customer returns `409 Conflict`, not a silent merge.

---

### Stable Error Envelope

All error responses — now and in future versions — conform to this envelope:

```json
{
  "error": {
    "code": "card_declined",
    "message": "The card was declined.",
    "param": null,
    "request_id": "req_abc123"
  }
}
```

**Stability contract:**
- `error.code` is a stable enum string; clients may switch on it.
- `error.message` is human-readable and may change across versions — do not parse it.
- New fields may be added; existing fields are never removed or renamed within a major version.
- HTTP status codes map predictably: `402` for payment failure, `422` for validation, `409` for idempotency conflicts, `429` for rate limits, `5xx` for server faults.

---

### Versioning

URL-versioned (`/v1/`, `/v2/`). Old versions remain live for a minimum 12-month deprecation window. Version sunset is communicated via `Deprecation` and `Sunset` response headers on every request to a deprecated version.

---

### Key Endpoints

| Method | Path | Idempotency Required |
|--------|------|----------------------|
| POST | `/v1/charges` | Yes |
| POST | `/v1/refunds` | Yes |
| GET | `/v1/charges/{id}` | No |
| POST | `/v1/subscriptions` | Yes |
| DELETE | `/v1/subscriptions/{id}` | No |

---

### Retry Guidance

Clients should retry on `429` and `5xx` with exponential backoff. Retries on `4xx` (except `429`) are safe only if the original request included an idempotency key — the server guarantees at-most-once execution for keyed requests.

---

**What's deliberately excluded:** webhook delivery semantics and PCI scope are real concerns but require separate specs — listing them here without detail would be worse than deferring.
