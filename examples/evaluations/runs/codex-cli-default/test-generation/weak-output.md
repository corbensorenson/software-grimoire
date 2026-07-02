I can’t write meaningful tests from this context alone without inventing behavior.

Missing details needed:

- The test framework: `pytest`, `unittest`, etc.
- The module/import path for `price_for`.
- Exact pricing rules for `free`, `team`, and `enterprise`.
- Seat tier boundaries and expected prices at each boundary.
- Expected behavior for unknown plans.
- Coupon format and rules:
  - Which coupon values are valid?
  - What makes a coupon “annual”?
  - Should invalid coupons be ignored or raise an error?
- Rounding policy details:
  - Standard `round()` behavior, decimal rounding, half-up, bankers rounding, etc.
- Expected return type: `float`, `Decimal`, integer cents, or formatted string.

With those specifics, I’d add tests covering:

- `seats < 0` raises an error.
- `seats == 0`, `1`, and tier boundary values.
- Free plan always prices correctly.
- Team and enterprise pricing across each tier.
- Annual coupon applies only when valid.
- Invalid coupons are rejected or ignored according to spec.
- Currency values are rounded to cents.
