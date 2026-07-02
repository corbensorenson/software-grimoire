**Assumptions:** amounts are integer minor units plus ISO currency; invoices, payment attempts, and refunds are separate resources; refunds link to a successful payment attempt and update invoice/payment lifecycle state.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/v1/invoices?customer_id=&limit=&cursor=` | List invoices with cursor pagination |
| `GET` | `/v1/invoices/{id}` | Fetch invoice |
| `POST` | `/v1/invoices` | Create invoice |
| `GET` | `/v1/payment_attempts?invoice_id=&limit=&cursor=` | List attempts |
| `POST` | `/v1/payment_attempts` | Create/retry payment attempt |
| `GET` | `/v1/payment_attempts/{id}` | Fetch attempt |
| `GET` | `/v1/refunds?invoice_id=&limit=&cursor=` | List refunds |
| `POST` | `/v1/refunds` | Create refund |
| `GET` | `/v1/refunds/{id}` | Fetch refund |

**Create Payment Attempt**

```http
POST /v1/payment_attempts
Authorization: Bearer <oauth-token>
Idempotency-Key: payatt_2026_07_01_abc123
Content-Type: application/json
```

```json
{
  "invoice_id": "inv_123",
  "amount": 2599,
  "currency": "USD",
  "payment_method_id": "pm_456"
}
```

```json
{
  "id": "pa_789",
  "invoice_id": "inv_123",
  "status": "succeeded",
  "amount": 2599,
  "currency": "USD",
  "created_at": "2026-07-01T12:00:00Z"
}
```

**Paginated List**

```json
{
  "data": [
    { "id": "inv_123", "status": "paid", "amount_due": 2599, "currency": "USD" }
  ],
  "pagination": {
    "limit": 50,
    "next_cursor": "cur_abc",
    "has_more": true
  }
}
```

**Error Schema**

```json
{
  "error": {
    "code": "invoice_already_paid",
    "message": "Invoice is already paid.",
    "request_id": "req_123",
    "details": {
      "invoice_id": "inv_123"
    }
  }
}
```

Error `code` is stable and machine-readable. Messages may change.

**Auth Notes**

Use OAuth bearer tokens. Scope by action: `billing.invoices.read`, `billing.invoices.write`, `billing.payments.write`, `billing.refunds.write`. Never infer tenant/customer access from request body alone; validate ownership server-side.

**Idempotency Notes**

Require `Idempotency-Key` for all mutating endpoints. Store key, endpoint, OAuth subject, request hash, response body, status code, and expiry. Same key plus same request returns the original response. Same key plus different body returns `idempotency_key_conflict`.

**Migration / Versioning Notes**

Use `/v1` path versioning. Preserve response fields and enum meanings. Additive fields are allowed. Avoid removing fields, changing types, or reusing error codes. Mobile clients may lag, so support old versions through a documented deprecation window.

**Verification Risks**

Race conditions: concurrent payment attempts for one invoice, duplicate refunds, refund amount exceeding captured amount, invoice status changing during payment. Use DB constraints, transactions, row locks, and lifecycle checks.

Retry hazards: network timeout after charge succeeds; client retries must receive the same attempt, not create a second charge.

Compatibility risks: enum additions, pagination shape changes, unstable errors, and merging refunds into invoices would break slow-upgrading clients.
