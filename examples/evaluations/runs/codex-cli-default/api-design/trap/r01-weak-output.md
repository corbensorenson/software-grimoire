Missing details: billing model, pricing units, tax rules, currencies, payment provider, auth scheme, tenant model, invoice lifecycle, and compliance requirements. Below is a compatibility-safe billing API shape.

**Core Principles**

- All mutating requests support `Idempotency-Key`.
- Retries with the same key must return the original result, including success or failure.
- Error responses use one stable envelope across all endpoints.
- API versioning is explicit: `/v1/...`.
- New fields may be added, but existing fields and error codes are not removed or retyped.

**Endpoints**

```http
POST /v1/customers
POST /v1/subscriptions
GET  /v1/subscriptions/{subscription_id}
POST /v1/subscriptions/{subscription_id}/cancel
POST /v1/invoices
GET  /v1/invoices/{invoice_id}
POST /v1/invoices/{invoice_id}/pay
GET  /v1/payments/{payment_id}
```

**Idempotency Contract**

Required for all `POST` requests:

```http
Idempotency-Key: 7f8c9b6e-...
```

Behavior:

- Same key + same request body returns the same response.
- Same key + different request body returns `409 idempotency_key_conflict`.
- Keys are scoped to account/tenant and endpoint.
- Server stores the final response envelope for replay.
- Clients may safely retry on network failures, `408`, `409` idempotency conflict only after correction, `429`, and `5xx`.

**Stable Error Envelope**

```json
{
  "error": {
    "code": "payment_declined",
    "message": "Payment was declined.",
    "request_id": "req_123",
    "retryable": false,
    "details": {
      "invoice_id": "inv_123"
    }
  }
}
```

Required fields are always present: `error.code`, `error.message`, `error.request_id`, `error.retryable`.

Error codes are stable API contract values, for example:

- `invalid_request`
- `not_found`
- `authentication_failed`
- `authorization_failed`
- `idempotency_key_conflict`
- `payment_declined`
- `invoice_already_paid`
- `rate_limited`
- `internal_error`

**Example: Pay Invoice**

```http
POST /v1/invoices/inv_123/pay
Idempotency-Key: pay-inv-123-attempt-1
```

```json
{
  "payment_method_id": "pm_123"
}
```

Success:

```json
{
  "payment": {
    "id": "pay_123",
    "invoice_id": "inv_123",
    "status": "succeeded"
  }
}
```

This design preserves retry safety and keeps clients insulated from breaking changes through explicit idempotency and stable error envelopes.
