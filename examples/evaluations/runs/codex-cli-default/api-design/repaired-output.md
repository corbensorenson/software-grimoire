**Assumptions**
- A customer/account owns invoices, payment attempts, refunds, and account credits.
- One invoice may have many payment attempts.
- Refunds apply to a successful payment attempt.
- Account credits are ledger entries, not mutable balances.

**Endpoint Table**

| Method | Endpoint | Purpose | Scope |
|---|---|---|---|
| `GET` | `/v1/invoices` | List invoices | `billing.invoices:read` |
| `GET` | `/v1/invoices/{invoice_id}` | Get invoice | `billing.invoices:read` |
| `POST` | `/v1/invoices/{invoice_id}/payment_attempts` | Attempt payment | `billing.payments:write` |
| `GET` | `/v1/invoices/{invoice_id}/payment_attempts` | List attempts | `billing.payments:read` |
| `GET` | `/v1/payment_attempts/{attempt_id}` | Get attempt | `billing.payments:read` |
| `POST` | `/v1/payment_attempts/{attempt_id}/refunds` | Create refund | `billing.refunds:write` |
| `GET` | `/v1/refunds` | List refunds | `billing.refunds:read` |
| `GET` | `/v1/account_credits` | List credit ledger | `billing.credits:read` |

Pagination:

```http
GET /v1/invoices?limit=25&cursor=eyJpZCI6...
```

```json
{
  "data": [],
  "pagination": {
    "next_cursor": "eyJpZCI6...",
    "has_more": true
  }
}
```

**Request / Response Examples**

Create payment attempt:

```http
POST /v1/invoices/inv_123/payment_attempts
Authorization: Bearer ...
Idempotency-Key: 8d8f1c7e-...
Content-Type: application/json
```

```json
{
  "payment_method_id": "pm_456",
  "amount": 4999,
  "currency": "usd"
}
```

```json
{
  "id": "pa_789",
  "invoice_id": "inv_123",
  "status": "processing",
  "amount": 4999,
  "currency": "usd",
  "created_at": "2026-07-01T12:00:00Z"
}
```

Create refund:

```json
{
  "amount": 2000,
  "reason": "requested_by_customer"
}
```

```json
{
  "id": "rf_123",
  "payment_attempt_id": "pa_789",
  "status": "succeeded",
  "amount": 2000,
  "currency": "usd"
}
```

Error schema:

```json
{
  "error": {
    "type": "invalid_request",
    "code": "amount_exceeds_refundable_balance",
    "message": "Refund amount exceeds refundable balance.",
    "request_id": "req_123"
  }
}
```

**Auth Notes**
- Use OAuth bearer tokens.
- Scopes are resource/action based.
- Internal automations should use the same public API with service-account tokens.
- Avoid exposing different semantics for internal callers.

**Idempotency Notes**
- Require `Idempotency-Key` on all `POST` mutation endpoints.
- Store key, account, endpoint, request hash, response body, and status in PostgreSQL.
- Same key + same request returns the original response.
- Same key + different request returns `409 idempotency_key_conflict`.
- Payment provider calls must also use stable downstream idempotency keys.

**Migration / Versioning Notes**
- Use `/v1`.
- Additive changes only: new fields, new enum values, new endpoints.
- Never rename or remove fields in `v1`.
- Mobile clients must tolerate unknown fields and unknown enum values.
- Breaking changes require `/v2` plus long deprecation windows.

**Risks To Verify**
- Double payment from concurrent retries: enforce invoice payment state with DB transactions and unique constraints.
- Refund races: lock payment/refund rows and compute refundable balance transactionally.
- Idempotency expiry: document retention period; expired keys may create new attempts.
- Compatibility risk: mobile clients may fail on new enum values unless explicitly hardened.
