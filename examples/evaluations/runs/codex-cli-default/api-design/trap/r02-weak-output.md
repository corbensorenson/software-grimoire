Missing specifics: billing model, currencies, taxes, discounts, proration, payment processor, auth/tenant model, retry window, and webhook needs.

A compatibility-safe REST shape:

**Core Contract**
- Base path: `/v1`
- Auth: bearer token or service token, exact scheme TBD.
- All mutating requests require `Idempotency-Key`.
- Reusing the same key with the same payload returns the original status/body.
- Reusing the same key with a different payload returns a stable conflict error.
- Error response envelope is never changed incompatibly.

**Stable Error Envelope**
```json
{
  "error": {
    "code": "invoice_not_found",
    "type": "not_found",
    "message": "Invoice was not found.",
    "request_id": "req_123",
    "details": {}
  }
}
```

**Resources**
```http
POST /v1/customers
GET /v1/customers/{customer_id}

POST /v1/invoices
GET /v1/invoices/{invoice_id}
POST /v1/invoices/{invoice_id}/finalize
POST /v1/invoices/{invoice_id}/void

POST /v1/payments
GET /v1/payments/{payment_id}
POST /v1/payments/{payment_id}/refunds

POST /v1/subscriptions
GET /v1/subscriptions/{subscription_id}
PATCH /v1/subscriptions/{subscription_id}
POST /v1/subscriptions/{subscription_id}/cancel
```

**Example Mutating Request**
```http
POST /v1/payments
Idempotency-Key: pay_2026_07_02_order_123
Content-Type: application/json
```

```json
{
  "customer_id": "cus_123",
  "invoice_id": "inv_123",
  "amount": 5000,
  "currency": "USD"
}
```

**Compatibility Rules**
- Existing fields are never renamed, removed, or given new meanings.
- New fields are additive and optional.
- Enum expansion is versioned or explicitly documented because clients may switch on values.
- Retryable failures use the same error envelope.
- `5xx`, `429`, and network failures are safe to retry with the same `Idempotency-Key`.
- Webhook/event delivery, if added, must also be idempotent and include stable event IDs.

This is intentionally conservative: billing clients often retry aggressively, so idempotency and stable errors are part of the API contract, not implementation details.
