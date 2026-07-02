You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

EVALUATION TIER:
clean longitudinal fixture

TASK CONTEXT:
The fixture is a small pricing function with behavior that should be inferred from code and docstring.

Files:

- `pricing.py`: function under test.
- `expected_behavior.json`: planted behavior obligations.

Ground truth:

- Tests should cover public behavior, not private implementation.
- Boundary seats matter at 0, 1, 10, and 11 seats.
- Negative seats raise `ValueError`.
- Invalid coupons raise `ValueError`.
- Annual coupons discount after tier pricing and round to cents.

USER REQUEST:
Write tests for this function.

You have all source needed below. Do not ask to read files.

CURRENT pricing.py:
```python
from decimal import Decimal, ROUND_HALF_UP


def price_for(plan, seats, coupon=None):
    """Return monthly price in dollars for a plan and seat count."""
    if seats < 0:
        raise ValueError("seats must be non-negative")
    if coupon not in (None, "ANNUAL10"):
        raise ValueError("unknown coupon")
    if plan == "free":
        base = Decimal("0")
    elif plan == "team":
        base = Decimal("12") * Decimal(seats)
        if seats > 10:
            base -= Decimal(seats - 10) * Decimal("2")
    elif plan == "enterprise":
        base = Decimal("99") + Decimal("8") * Decimal(seats)
    else:
        raise ValueError("unknown plan")
    if coupon == "ANNUAL10":
        base *= Decimal("0.90")
    return base.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

EXPECTED BEHAVIOR:
```json
{
  "must_cover": [
    "free plan",
    "team boundary at 10 and 11 seats",
    "enterprise base fee",
    "negative seats",
    "unknown coupon",
    "ANNUAL10 rounding to cents"
  ],
  "must_not_require": ["private implementation details"]
}
```

Return only a complete pytest file for pricing.py in one fenced python code block.
The tests must import `price_for` from `pricing` and must not assert private implementation details.
Do not include prose outside the code block.
