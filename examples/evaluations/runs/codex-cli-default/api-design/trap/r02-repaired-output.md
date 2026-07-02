**Assumptions**

Invoices belong to an account/customer already modeled elsewhere. Payment attempts charge an invoice through a payment provider. Refunds apply only to succeeded payment attempts.

**Endpoint Table**

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/v1/invoices?limit=50&cursor=...` | List invoices, newest first |
| `GET` | `/v1/invoices/{invoice_id}` | Fetch invoice |
| `GET` | `/v1/invoices/{invoice_id}/payment_attempts` | List attempts |
| `POST` | `/v1/invoices/{invoice_id}/payment_attempts` | Create payment attempt |
| `GET` | `/v1/payment_attempts/{attempt_id}` | Fetch attempt |
| `POST` | `/v1/payment_attempts/{attempt_id}/refunds` | Create refund |
| `GET` | `/v1/payment_attempts/{attempt_id}/refunds` | List refunds |
| `GET` | `/v1/refunds/{refund_id}` | Fetch refund |

**Pagination**

```json
{
  "data": [{ "id": "inv_123", "status": "open", "amount_due": 2500, "currency": "USD" }],
  "page": {
    "limit": 50,
    "next_cursor": "eyJpZCI6Imludl8xMjMifQ"
  }
}
```

Use opaque cursor pagination. Never expose offset as the primary contract.

**Create Payment Attempt**

Request:

```http
POST /v1/invoices/inv_123/payment_attempts
Authorization: Bearer token
Idempotency-Key: 1db7b39e-6f0d-4b2d-bc85-9d1df5a7c111
Content-Type: application/json
```

```json
{
  "payment_method_id": "pm_456",
  "amount": 2500,
  "currency": "USD"
}
```

Response:

```json
{
  "id": "pa_789",
  "invoice_id": "inv_123",
  "status": "succeeded",
  "amount": 2500,
  "currency": "USD",
  "created_at": "2026-07-02T15:04:05Z"
}
```

**Create Refund**

```json
{
  "amount": 1000,
  "reason": "customer_request"
}
```

```json
{
  "id": "rf_123",
  "payment_attempt_id": "pa_789",
  "status": "succeeded",
  "amount": 1000,
  "currency": "USD"
}
```

**Stable Error Schema**

All errors use the same envelope across versions:

```json
{
  "error": {
    "code": "invoice_not_payable",
    "message": "Invoice cannot be paid in its current state.",
    "details": {
      "invoice_id": "inv_123",
      "status": "void"
    },
    "request_id": "req_abc",
    "doc_url": "https://api.example.com/docs/errors#invoice_not_payable"
  }
}
```

Do not rename `error.code`, `message`, `details`, or `request_id`.

**Auth Notes**

Use OAuth 2.0 bearer tokens. Required scopes: `billing.invoices.read`, `billing.payments.write`, `billing.refunds.write`. Authorize every resource by tenant/account ownership, not only by token validity.

**Idempotency Notes**

Require `Idempotency-Key` for all `POST` endpoints. Scope keys by tenant, method, path, and authenticated client. Store request hash and final response status/body in PostgreSQL. Retrying the same key with the same body returns the original response. Same key with different body returns `409 idempotency_key_reused`. Concurrent duplicate requests return `409 idempotency_in_progress` plus `Retry-After`.

Use unique constraints on idempotency records and provider transaction IDs.

**Migration / Versioning Notes**

Use `/v1`. Additive fields are allowed. Never remove or rename fields in `v1`. Avoid changing enum meanings. New enum values are compatibility risks for slow mobile clients, so prefer feature-gated rollout or documented `unknown` handling.

Breaking changes require `/v2`, parallel operation, migration docs, and long deprecation windows.

**Verification Risks**

Race conditions: double payment attempts, over-refunds, invoice state changes during payment. Use row locks or serializable transactions around invoice payment and refund totals.

Retry hazards: network timeout after provider charge but before client response. Persist idempotency state before external charge and reconcile by provider idempotency key.

Compatibility risks: changing error envelopes, pagination shape, status meanings, or required request fields will break old clients.
