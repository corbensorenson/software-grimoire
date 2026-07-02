**Billing API Design**

Base path: `/v1/billing`
Versioning: keep `/v1` backward compatible. Only additive response fields are allowed. Do not rename status values or change error shape without a new version. Mobile-breaking removals require at least the 120-day mobile upgrade window.

| Method | Endpoint | Scope | Purpose |
|---|---|---:|---|
| `GET` | `/invoices` | `billing:read` | List invoices, paginated |
| `GET` | `/invoices/{invoice_id}` | `billing:read` | Fetch invoice |
| `POST` | `/payment_attempts` | `billing:write` | Attempt payment, idempotent |
| `GET` | `/payment_attempts` | `billing:read` | List attempts, paginated |
| `GET` | `/payment_attempts/{attempt_id}` | `billing:read` | Fetch attempt |
| `POST` | `/refunds` | `billing:write` | Create refund as separate resource |
| `GET` | `/refunds` | `billing:read` | List refunds, paginated |
| `GET` | `/refunds/{refund_id}` | `billing:read` | Fetch refund |
| `GET` | `/account_credits` | `billing:read` | List account credits, paginated |

Payment attempts require an `Idempotency-Key` header. Repeating the same request with the same key returns the same payment attempt. Reusing the key with a different body returns `409 idempotency_key_conflict`.

Example:

```http
POST /v1/billing/payment_attempts
Authorization: Bearer ...
Idempotency-Key: pay_2026_001
Content-Type: application/json
```

```json
{
  "invoice_id": "inv_123",
  "payment_method_id": "pm_456",
  "amount": 5000,
  "currency": "USD"
}
```

Response:

```json
{
  "id": "pa_789",
  "invoice_id": "inv_123",
  "status": "succeeded",
  "amount": 5000,
  "currency": "USD",
  "created_at": "2026-07-01T12:00:00Z"
}
```

Refunds are separate from invoices but linked:

```json
{
  "id": "ref_123",
  "invoice_id": "inv_123",
  "payment_attempt_id": "pa_789",
  "status": "pending",
  "amount": 2000,
  "currency": "USD"
}
```

List responses use cursor pagination:

```http
GET /v1/billing/invoices?limit=50&page_after=cursor_abc
```

```json
{
  "data": [],
  "next_page_token": "cursor_def"
}
```

Stable error schema:

```json
{
  "error": {
    "code": "idempotency_key_required",
    "message": "Idempotency-Key header is required.",
    "request_id": "req_123",
    "details": {}
  }
}
```

Error `code` is the machine contract; messages may change, codes must not.
