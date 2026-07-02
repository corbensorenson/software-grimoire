**Inferred Behaviors**

`price_for(plan, seats, coupon=None)` returns a `Decimal` monthly price quantized to cents. Supported plans appear to be `free`, `team`, and `enterprise`. `team` changes pricing after 10 seats, so 10 and 11 are critical. `ANNUAL10` applies a 10% discount after base/tier pricing. Negative seats, unknown plans, and unknown coupons raise `ValueError`.

**Ambiguities**

Accepted non-integer `seats` types are not specified, so these tests avoid them. Unknown-plan behavior is treated as characterization because the public docs only imply supported plans.

**Test File: `test_pricing.py`**

```python
from decimal import Decimal

import pytest

from pricing import price_for


CENT = Decimal("0.01")


def assert_money(actual, expected):
    assert actual == Decimal(expected)
    assert actual.same_quantum(CENT)


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
def test_supported_plan_prices_and_seat_boundaries(plan, seats, expected):
    assert_money(price_for(plan, seats), expected)


def test_annual10_applies_after_team_tier_pricing_regression():
    assert_money(price_for("team", 11, coupon="ANNUAL10"), "117.00")


def test_annual10_returns_cent_quantized_money():
    assert_money(price_for("enterprise", 1, coupon="ANNUAL10"), "96.30")


@pytest.mark.parametrize(
    ("plan", "seats", "coupon"),
    [
        ("team", -1, None),
        ("team", 1, "BOGUS"),
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

Nominal cases cover the observed public plans. Boundary cases focus on `0`, `1`, `10`, and `11`, especially the 10-to-11 team discount transition. Error cases cover negative seats and rejected coupons. The regression test locks discount ordering at the tier boundary, where happy-path tests commonly miss bugs.
