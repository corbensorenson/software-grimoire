**API Shape**

Use HTTP/JSON, `/v1`, additive-only changes, cursor pagination, stable enum values, and webhook/event delivery for async changes. Mobile clients should be able to keep working for years, so avoid removing fields, renaming states, or changing default behavior.

**Core Resources**

`Invoice`
```json
{
  "id": "inv_123",
  "account_id": "acct_123",
  "status": "draft|open|paid|void|uncollectible",
  "currency": "USD",
  "amount_due": 12000,
  "amount_paid": 0,
  "credit_applied": 2000,
  "due_at": "2026-07-15T00:00:00Z",
  "line_items": [],
  "created_at": "...",
  "updated_at": "..."
}
```

`PaymentAttempt`
```json
{
  "id": "pa_123",
  "invoice_id": "inv_123",
  "status": "requires_action|processing|succeeded|failed|canceled",
  "amount": 10000,
  "failure_code": null,
  "retryable": true,
  "created_at": "..."
}
```

`Refund`
```json
{
  "id": "rf_123",
  "payment_attempt_id": "pa_123",
  "status": "pending|succeeded|failed",
  "amount": 5000,
  "reason": "requested_by_customer"
}
```

`AccountCredit`
```json
{
  "id": "cr_123",
  "account_id": "acct_123",
  "status": "available|applied|expired|reversed",
  "amount": 2000,
  "remaining_amount": 0,
  "source": "manual|refund_credit|promotion"
}
```

**Endpoints**

```http
GET    /v1/invoices
GET    /v1/invoices/{invoice_id}
POST   /v1/invoices/{invoice_id}/void
POST   /v1/invoices/{invoice_id}/pay

GET    /v1/payment_attempts/{payment_attempt_id}
POST   /v1/payment_attempts
POST   /v1/payment_attempts/{payment_attempt_id}/cancel

GET    /v1/refunds
POST   /v1/refunds
GET    /v1/refunds/{refund_id}

GET    /v1/account_credits
POST   /v1/account_credits
POST   /v1/account_credits/{credit_id}/apply
POST   /v1/account_credits/{credit_id}/reverse

GET    /v1/events?cursor=...
POST   /v1/webhook_endpoints
```

**Safe Retries**

All mutating `POST` requests require:

```http
Idempotency-Key: client-generated-uuid
```

The server stores the key with request body hash and final result. Retrying the same request returns the same response. Reusing the key with a different body returns `409 idempotency_conflict`.

Payment creation must be asynchronous-safe: `POST /payment_attempts` creates one attempt, never multiple charges, even if the client times out.

**OAuth Scopes**

```text
billing.invoices.read
billing.invoices.write
billing.payments.read
billing.payments.write
billing.refunds.read
billing.refunds.write
billing.credits.read
billing.credits.write
billing.events.read
```

Internal automations should use the same API with service accounts and narrower scopes, not hidden behavior.

**Missing To Finalize**

Need processor constraints, tax rules, multi-currency policy, PCI boundaries, invoice mutability rules, refund limits, and whether credits are cash-equivalent or promotional.
