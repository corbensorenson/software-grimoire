**Assumptions**

Invoices belong to an authenticated tenant/account. Money is stored in minor units with ISO currency. Payment attempts charge an invoice. Refunds apply to successful payment attempts.

**Endpoint Table**

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/v1/invoices` | List invoices with cursor pagination |
| `POST` | `/v1/invoices` | Create draft invoice |
| `GET` | `/v1/invoices/{invoice_id}` | Fetch invoice |
| `POST` | `/v1/invoices/{invoice_id}/finalize` | Finalize invoice |
| `GET` | `/v1/payment_attempts` | List payment attempts |
| `POST` | `/v1/payment_attempts` | Attempt payment for invoice |
| `GET` | `/v1/payment_attempts/{attempt_id}` | Fetch attempt |
| `GET` | `/v1/refunds` | List refunds |
| `POST` | `/v1/refunds` | Create refund |
| `GET` | `/v1/refunds/{refund_id}` | Fetch refund |

**Examples**

Create payment attempt:

```http
POST /v1/payment_attempts
Authorization: Bearer <token>
Idempotency-Key: 9b7c1f1a-7e9a-4c0d-bdf0-7e3c8b5b8c22
Content-Type: application/json
```

```json
{
  "invoice_id": "inv_123",
  "amount": 2500,
  "currency": "USD",
  "payment_method_id": "pm_456"
}
```

```json
{
  "id": "pa_789",
  "invoice_id": "inv_123",
  "status": "succeeded",
  "amount": 2500,
  "currency": "USD",
  "created_at": "2026-07-02T18:30:00Z"
}
```

List response:

```json
{
  "data": [
    {
      "id": "inv_123",
      "status": "open",
      "amount_due": 2500,
      "currency": "USD"
    }
  ],
  "pagination": {
    "next_cursor": "eyJpZCI6Imludl8xMjMifQ",
    "has_more": true
  }
}
```

Stable error envelope:

```json
{
  "error": {
    "code": "idempotency_key_conflict",
    "message": "Idempotency key was reused with a different request body.",
    "request_id": "req_abc",
    "field": null,
    "retryable": false
  }
}
```

**Auth Notes**

Use OAuth bearer tokens. Required scopes: `billing:read`, `billing:write`, `payments:write`, `refunds:write`. Enforce tenant isolation on every query using tenant/account ID from the token, never from client input.

**Idempotency Notes**

All mutating `POST` endpoints require `Idempotency-Key`. Store `(tenant_id, method, path, key, request_hash, response_status, response_body)` in PostgreSQL. Same key plus same request returns the original response, including errors. Same key with different body returns `409 idempotency_key_conflict`.

For in-flight duplicates, either block until the first request completes or return `409 idempotency_in_progress` with `retryable: true`. Never create a second charge/refund after a client timeout.

**Migration / Versioning Notes**

Use `/v1`. Backward-compatible changes are additive only: new nullable fields, new endpoints, new enum values only if clients are documented to ignore unknowns. Do not change existing field meanings, error shape, pagination shape, or idempotency behavior. Breaking changes require `/v2` and long deprecation windows because clients upgrade slowly.

**Verification Risks**

Race conditions: double payment attempts for one invoice, refund total exceeding captured amount, and concurrent finalize/pay flows. Use transactions, row locks, unique constraints, and refund-sum checks.

Retry hazards: network timeout after successful charge, provider webhook arriving before API response, duplicate mobile retries.

Compatibility risks: changing error codes, removing fields, changing cursor format, shortening idempotency retention, or returning a different response for repeated idempotent requests.
