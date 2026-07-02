**Assumptions / Missing**
Amounts, currencies, exact status enum values, customer model, payment provider behavior, invoice line items, and account credit lifecycle are not specified. Design below uses generic fields and treats refunds/invoices as separate linked resources.

**Endpoint Table**

| Method | Endpoint | Scope | Notes |
|---|---|---:|---|
| `GET` | `/v1/invoices?limit=&cursor=&status=` | `billing:read` | Paginated list |
| `GET` | `/v1/invoices/{invoice_id}` | `billing:read` | Stable invoice representation |
| `POST` | `/v1/invoices` | `billing:write` | Create invoice |
| `GET` | `/v1/invoices/{invoice_id}/payment_attempts?limit=&cursor=` | `billing:read` | Paginated attempts |
| `POST` | `/v1/invoices/{invoice_id}/payment_attempts` | `billing:write` | Requires `Idempotency-Key` |
| `GET` | `/v1/payment_attempts/{attempt_id}` | `billing:read` | Fetch retry result |
| `GET` | `/v1/refunds?invoice_id=&limit=&cursor=` | `billing:read` | Paginated refunds |
| `POST` | `/v1/refunds` | `billing:write` | Separate refund resource linked to invoice/payment attempt |
| `GET` | `/v1/account_credits?limit=&cursor=` | `billing:read` | Included because fixture lists resource |

**Examples**

`POST /v1/invoices`

```json
{
  "customer_id": "cus_123",
  "amount_minor": 5000,
  "currency": "USD"
}
```

```json
{
  "id": "inv_123",
  "status": "open",
  "amount_minor": 5000,
  "currency": "USD",
  "created_at": "2026-07-01T12:00:00Z"
}
```

`POST /v1/invoices/inv_123/payment_attempts` with `Idempotency-Key: pay_20260701_inv_123_001`

```json
{
  "payment_method_id": "pm_123"
}
```

```json
{
  "id": "pa_123",
  "invoice_id": "inv_123",
  "status": "succeeded",
  "amount_minor": 5000
}
```

Paginated list response:

```json
{
  "data": [{ "id": "inv_123", "status": "open" }],
  "page": { "limit": 50, "next_cursor": "cur_abc" }
}
```

Stable error:

```json
{
  "error": {
    "code": "idempotency_key_required",
    "message": "Idempotency-Key header is required.",
    "request_id": "req_123"
  }
}
```

**Auth**
Use OAuth bearer tokens. Existing scopes remain `billing:read` and `billing:write`; do not rename them without a new API version.

**Idempotency**
All payment attempts require `Idempotency-Key`. Same key plus same request returns the original result. Same key with different body returns `409` and stable code `idempotency_key_conflict`.

**Versioning / Migration**
Use `/v1`. Add fields only; do not rename invoice statuses, scopes, or error shape. Support old mobile clients for at least 120 days. New breaking behavior requires `/v2`.

**Verification Risks**
Race conditions: duplicate payment attempts for one invoice, refund while payment is pending, concurrent refund requests. Use PostgreSQL transactions, unique idempotency keys, and state transition checks.

Retry hazards: client timeout after successful charge; idempotency must return the existing attempt.

Compatibility risks: enum renames, unpaginated lists, changed error schema, and coupling refunds directly into invoice objects.
