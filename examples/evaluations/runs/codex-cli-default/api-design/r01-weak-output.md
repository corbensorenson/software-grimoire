The fixture is missing exact lifecycle status names, amount/currency rules, and payment processor details, so those should be filled from production contracts. This design preserves compatibility.

| Endpoint | Method | Scope | Notes |
|---|---:|---|---|
| `/v1/invoices` | `GET` | `billing:read` | Cursor-paginated list |
| `/v1/invoices/{invoice_id}` | `GET` | `billing:read` | Stable invoice status values; never rename |
| `/v1/payment_attempts` | `POST` | `billing:write` | Requires `Idempotency-Key` header |
| `/v1/payment_attempts/{attempt_id}` | `GET` | `billing:read` | Retry-safe result lookup |
| `/v1/refunds` | `POST` | `billing:write` | Separate refund resource linked to invoice/payment |
| `/v1/refunds/{refund_id}` | `GET` | `billing:read` | Linked lifecycle state |
| `/v1/account_credits` | `GET` | `billing:read` | Cursor-paginated list |

**Payment Attempt Request**

```http
POST /v1/payment_attempts
Authorization: Bearer <token>
Idempotency-Key: pay_2026_07_01_customer_123_invoice_456
Content-Type: application/json
```

```json
{
  "invoice_id": "inv_456",
  "account_id": "acct_123",
  "amount": 5000
}
```

**Payment Attempt Response**

```json
{
  "id": "pa_789",
  "invoice_id": "inv_456",
  "status": "<stable_payment_attempt_status>",
  "created_at": "2026-07-01T12:00:00Z"
}
```

If the same idempotency key is retried with the same body, return the original result. If reused with a different body, return a stable error.

**Paginated List Response**

```http
GET /v1/invoices?limit=50&cursor=cur_abc
```

```json
{
  "data": [
    {
      "id": "inv_456",
      "status": "<existing_invoice_status>",
      "refund_ids": ["ref_123"]
    }
  ],
  "pagination": {
    "next_cursor": "cur_def",
    "has_more": true
  }
}
```

**Refund Response**

```json
{
  "id": "ref_123",
  "invoice_id": "inv_456",
  "payment_attempt_id": "pa_789",
  "status": "<stable_refund_status>"
}
```

**Stable Error Schema**

```json
{
  "error": {
    "code": "IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_BODY",
    "message": "The idempotency key was already used for a different request.",
    "request_id": "req_abc"
  }
}
```

Compatibility rules: keep `/v1` backward compatible, add fields only, never rename invoice statuses or error fields, and support old mobile behavior for at least the 120-day upgrade window.
