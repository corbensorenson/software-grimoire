Assumptions: amounts are integer minor units plus currency; invoice status values are stable enums; refunds are separate resources linked to invoices and successful payment attempts.

| Method | Endpoint | Scope | Notes |
|---|---|---|---|
| `GET` | `/v1/invoices?limit=50&cursor=...` | `billing:read` | Paginated list |
| `POST` | `/v1/invoices` | `billing:write` | Create invoice |
| `GET` | `/v1/invoices/{invoice_id}` | `billing:read` | Stable invoice shape |
| `GET` | `/v1/invoices/{invoice_id}/payment_attempts` | `billing:read` | Paginated attempts |
| `POST` | `/v1/invoices/{invoice_id}/payment_attempts` | `billing:write` | Requires `Idempotency-Key` |
| `GET` | `/v1/payment_attempts/{attempt_id}` | `billing:read` | Retry/status polling |
| `POST` | `/v1/payment_attempts/{attempt_id}/refunds` | `billing:write` | Requires `Idempotency-Key` |
| `GET` | `/v1/refunds?invoice_id=...&limit=50&cursor=...` | `billing:read` | Paginated refunds |
| `GET` | `/v1/account_credits?limit=50&cursor=...` | `billing:read` | Existing resource support |

Create payment attempt:

```http
POST /v1/invoices/inv_123/payment_attempts
Authorization: Bearer <token>
Idempotency-Key: 7f6b2f0e-...
Content-Type: application/json
```

```json
{
  "amount": 1299,
  "currency": "USD",
  "payment_method_id": "pm_123"
}
```

```json
{
  "id": "pa_123",
  "invoice_id": "inv_123",
  "status": "succeeded",
  "amount": 1299,
  "currency": "USD",
  "created_at": "2026-07-01T12:00:00Z"
}
```

Paginated list response:

```json
{
  "data": [{ "id": "inv_123", "status": "paid", "refund_state": "none" }],
  "pagination": { "next_cursor": "cur_abc", "has_more": true }
}
```

Refund response:

```json
{
  "id": "rf_123",
  "invoice_id": "inv_123",
  "payment_attempt_id": "pa_123",
  "status": "pending",
  "amount": 500
}
```

Stable error schema:

```json
{
  "error": {
    "code": "idempotency_key_required",
    "message": "Idempotency-Key is required.",
    "request_id": "req_123"
  }
}
```

Auth: OAuth bearer tokens only. Preserve existing scopes: `billing:read` for reads, `billing:write` for mutations.

Idempotency: all payment attempts and refunds require `Idempotency-Key`. Reusing a key with the same body returns the original result; reusing it with a different body returns `409` with code `idempotency_key_conflict`.

Versioning/migration: keep `/v1`; additive fields only; never rename status values or change error shape. Mobile clients have a 120-day upgrade window, so breaking changes require `/v2` and overlap.

Verification risks: race concurrent retries with a unique idempotency-key constraint; prevent double refund by checking refundable balance transactionally; do not rely on clients preserving unknown fields.
