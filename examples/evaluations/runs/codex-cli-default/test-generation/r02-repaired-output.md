**Inferred Behaviors**

`price_for` returns a `Decimal` monthly price rounded/quantized to cents. Plans observed: `free`, `team`, `enterprise`. `team` charges `$12/seat` through 10 seats, then `$10` for each seat above 10. `enterprise` charges `$99 + $8/seat`. Negative seats, unknown plans, and unknown coupons raise `ValueError`. `ANNUAL10` applies after tier pricing.

**Ambiguities**

No type hints define accepted `seats` types, so these tests avoid non-integer characterization. Unknown-plan behavior is inferred from the public function branch. No public input appears to create a half-cent, so the coupon test asserts cent output without asserting private rounding internals.

**Test File: `test_pricing.py`**

```python
from decimal import Decimal

import pytest

from pricing import price_for


@pytest.mark.parametrize(
    ("plan", "seats", "expected"),
    [
        ("free", 0, "0.00"),
        ("free", 11, "0.00"),
        ("team", 0, "0.00"),
        ("team", 1, "12.00"),
        ("team", 10, "120.00"),
        ("team", 11, "130.00"),
        ("enterprise", 0, "99.00"),
        ("enterprise", 1, "107.00"),
    ],
)
def test_plan_prices_and_seat_boundaries(plan, seats, expected):
    assert price_for(plan, seats) == Decimal(expected)


def test_annual_coupon_discounts_after_team_tier_pricing_regression():
    assert price_for("team", 11, coupon="ANNUAL10") == Decimal("117.00")


def test_annual_coupon_returns_cents():
    price = price_for("enterprise", 1, coupon="ANNUAL10")

    assert price == Decimal("96.30")
    assert str(price) == "96.30"


@pytest.mark.parametrize(
    ("plan", "seats", "coupon"),
    [
        ("team", -1, None),
        ("team", 1, "BADCOUPON"),
    ],
)
def test_invalid_seats_and_coupons_raise_value_error(plan, seats, coupon):
    with pytest.raises(ValueError):
        price_for(plan, seats, coupon=coupon)


def test_unknown_plan_raises_value_error_characterization():
    with pytest.raises(ValueError):
        price_for("unknown", 1)
```

**Rationale**

The first group covers nominal pricing and the important `0`, `1`, `10`, `11` seat boundaries. The coupon tests lock the annual discount order and cents output. Error tests cover specified validation failures. The unknown-plan test is labeled characterization because the valid plan set is inferred from current public behavior.
