Missing requirements: billing model, authentication, currencies, tax rules, payment provider, retry window, webhook needs, and compliance constraints.

A safe API shape should make compatibility explicit:

```http
POST /v1/billing/accounts
GET  /v1/billing/accounts/{account_id}

POST /v1/billing/invoices
GET  /v1/billing/invoices/{invoice_id}
POST /v1/billing/invoices/{invoice_id}/finalize
POST /v1/billing/invoices/{invoice_id}/void

POST /v1/billing/payments
GET  /v1/billing/payments/{payment_id}

POST /v1/billing/refunds
GET  /v1/billing/refunds/{refund_id}
```

All mutation endpoints must support idempotent retries:

```http
Idempotency-Key: client-generated-unique-key
```

Semantics:

- Same key + same authenticated client + same method + same path + same body returns the original response, including status and body.
- Same key with a different body returns `409 idempotency_key_reused`.
- Idempotency records must live at least as long as the documented client retry window.
- Clients can safely retry `POST` requests after timeouts or `5xx` responses.
- Server-generated side effects must happen at most once per accepted idempotency key.

Stable error envelope:

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Amount must be greater than zero.",
    "param": "amount",
    "request_id": "req_123",
    "type": "validation_error"
  }
}
```

Compatibility rules:

- Never remove or rename response fields in `/v1`.
- Additive fields are allowed.
- Error `code` values are stable API contract, not free-form strings.
- Clients should branch on `error.code`, not `message`.
- Deprecated fields remain until a new major version.
- Every response includes a request ID.
- Money amounts use integer minor units plus explicit currency, for example `{ "amount": 1299, "currency": "USD" }`.

Example payment request:

```json
{
  "account_id": "acct_123",
  "invoice_id": "inv_123",
  "amount": 1299,
  "currency": "USD"
}
```

Example response:

```json
{
  "id": "pay_123",
  "status": "succeeded",
  "amount": 1299,
  "currency": "USD",
  "invoice_id": "inv_123"
}
```
