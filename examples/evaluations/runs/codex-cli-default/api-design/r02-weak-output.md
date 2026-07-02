Missing specifics: amount/currency format, full lifecycle enums, refund eligibility rules, and account-credit behavior. This design keeps those as stable fields without inventing business rules.

**API Shape**

Base path: `/v1/billing`
Auth: OAuth bearer token. Existing scopes: `billing:read`, `billing:write`.

| Method | Endpoint | Scope | Notes |
|---|---|---:|---|
| `GET` | `/invoices?limit=50&page_token=...` | `billing:read` | Paginated invoice list |
| `GET` | `/invoices/{invoice_id}` | `billing:read` | Invoice detail |
| `GET` | `/payment_attempts?invoice_id=...&limit=50&page_token=...` | `billing:read` | Paginated attempts |
| `POST` | `/payment_attempts` | `billing:write` | Requires `Idempotency-Key` |
| `GET` | `/refunds?invoice_id=...&limit=50&page_token=...` | `billing:read` | Refunds are separate resources |
| `POST` | `/refunds` | `billing:write` | Creates refund linked to invoice/payment attempt |
| `GET` | `/account_credits?limit=50&page_token=...` | `billing:read` | Paginated credits |

**Payment Attempt**

Request:

```http
POST /v1/billing/payment_attempts
Authorization: Bearer <token>
Idempotency-Key: pay_2026_07_01_customer_123_invoice_456
Content-Type: application/json
```

```json
{
  "invoice_id": "inv_456",
  "payment_method_id": "pm_789"
}
```

Response:

```json
{
  "id": "pa_123",
  "invoice_id": "inv_456",
  "status": "processing",
  "created_at": "2026-07-01T00:00:00Z"
}
```

Repeated requests with the same `Idempotency-Key` must return the original result, not create a second charge.

**Invoice With Linked Lifecycle**

```json
{
  "id": "inv_456",
  "status": "open",
  "payment_attempt_ids": ["pa_123"],
  "refund_ids": ["ref_222"],
  "account_credit_ids": []
}
```

Refunds remain separate resources:

```json
{
  "id": "ref_222",
  "invoice_id": "inv_456",
  "payment_attempt_id": "pa_123",
  "status": "pending"
}
```

**Pagination**

List responses use a stable envelope:

```json
{
  "data": [{ "id": "inv_456", "status": "open" }],
  "next_page_token": "opaque_token_or_null"
}
```

**Stable Error Schema**

Never change this shape without a new version:

```json
{
  "error": {
    "code": "idempotency_key_required",
    "message": "Idempotency-Key header is required.",
    "request_id": "req_123"
  }
}
```

`code` is the stable machine-readable contract.

**Compatibility Notes**

Use `/v1` versioning. Do not rename invoice status values, change the error shape, or make payment retries non-idempotent. Changes should be additive because mobile clients may take 120 days to upgrade.
