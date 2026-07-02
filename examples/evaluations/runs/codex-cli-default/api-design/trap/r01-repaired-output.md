**Assumptions**

Billing resources are tenant-scoped. Invoices are created by backend/admin clients, payment attempts charge an invoice, and refunds target a successful payment attempt. Currency is ISO-4217 minor units.

**Endpoint Table**

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/v1/invoices` | List invoices, paginated |
| `POST` | `/v1/invoices` | Create invoice |
| `GET` | `/v1/invoices/{invoice_id}` | Fetch invoice |
| `POST` | `/v1/invoices/{invoice_id}/payment_attempts` | Attempt payment |
| `GET` | `/v1/payment_attempts/{attempt_id}` | Fetch payment attempt |
| `POST` | `/v1/payment_attempts/{attempt_id}/refunds` | Create refund |
| `GET` | `/v1/refunds/{refund_id}` | Fetch refund |

Pagination: `?limit=50&starting_after=inv_123`. Responses include:

```json
{
  "data": [],
  "has_more": false,
  "next_cursor": null
}
```

**Create Invoice**

```http
POST /v1/invoices
Authorization: Bearer <token>
Idempotency-Key: 4f0b6b8a-...
Content-Type: application/json
```

```json
{
  "customer_id": "cus_123",
  "currency": "usd",
  "amount_due": 2500,
  "metadata": { "order_id": "ord_456" }
}
```

```json
{
  "id": "inv_123",
  "object": "invoice",
  "status": "open",
  "currency": "usd",
  "amount_due": 2500,
  "amount_paid": 0,
  "created_at": "2026-07-02T15:04:05Z"
}
```

**Payment Attempt**

```json
{
  "payment_method_id": "pm_123",
  "amount": 2500
}
```

Response:

```json
{
  "id": "pa_123",
  "object": "payment_attempt",
  "invoice_id": "inv_123",
  "status": "succeeded",
  "amount": 2500
}
```

**Stable Error Envelope**

Never change this shape in `/v1`; only add optional fields.

```json
{
  "error": {
    "type": "invalid_request",
    "code": "invoice_not_open",
    "message": "Invoice is not open.",
    "param": "invoice_id",
    "request_id": "req_123"
  }
}
```

**Auth Notes**

Use OAuth bearer tokens. Require scopes such as `billing:read`, `billing:write`, and tenant isolation from token claims. Return `401` for invalid tokens, `403` for insufficient scope.

**Idempotency Notes**

All unsafe writes require `Idempotency-Key`. Store key, tenant, method, path, request hash, status, and response body in PostgreSQL. Replaying the same key returns the original response, including `4xx` validation errors. Same key with different body returns `409 idempotency_key_conflict`. Keys expire after a documented window, e.g. 24 hours.

**Migration / Versioning**

Use path versions: `/v1`, `/v2`. In `/v1`, do not rename fields, remove fields, change enum meanings, or change error envelopes. Additive fields are allowed. New breaking behavior ships under `/v2`.

**Risks**

Race conditions: concurrent payment attempts can double-charge unless invoice payment is guarded by row locks or unique constraints on successful payment per invoice.

Retry hazards: clients may retry after timeout while the charge succeeded. Idempotency must return the original successful result.

Compatibility risks: mobile clients upgrade slowly, so error codes, enum values, pagination shape, timestamps, and id formats must remain stable in `/v1`.
