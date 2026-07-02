**Inferred Behaviors**
- `price_for(plan, seats, coupon=None)` returns a `Decimal` monthly dollar price rounded to cents.
- `free` costs `0.00`.
- `team` costs `$12/seat` through 10 seats, then `$10/seat` for seats above 10.
- `enterprise` has a `$99` base fee plus `$8/seat`.
- Negative seats raise `ValueError`.
- Unknown coupons raise `ValueError`.
- `ANNUAL10` applies after plan/tier pricing.

**Ambiguities**
- Non-integer seats are not specified.
- Validation precedence when both plan and coupon are invalid is not specified.
- Unknown plan handling is observable in code but not listed in `expected_behavior.json`, so it is labeled as characterization.

**Test File: `test_pricing.py`**
```python
from decimal import Decimal

import pytest

from pricing import price_for


@pytest.mark.parametrize(
    ("plan", "seats", "expected"),
    [
        ("free", 0, Decimal("0.00")),
        ("free", 11, Decimal("0.00")),
        ("enterprise", 0, Decimal("99.00")),
        ("enterprise", 1, Decimal("107.00")),
    ],
)
def test_nominal_plan_prices(plan, seats, expected):
    assert price_for(plan, seats) == expected


@pytest.mark.parametrize(
    ("seats", "expected"),
    [
        (0, Decimal("0.00")),
        (1, Decimal("12.00")),
        (10, Decimal("120.00")),
        (11, Decimal("130.00")),
    ],
)
def test_team_pricing_boundaries(seats, expected):
    assert price_for("team", seats) == expected


def test_annual_coupon_applies_after_team_tier_pricing_and_returns_cents():
    assert price_for("team", 11, coupon="ANNUAL10") == Decimal("117.00")


@pytest.mark.parametrize(
    ("plan", "seats", "coupon"),
    [
        ("team", -1, None),
        ("team", 1, "BADCOUPON"),
    ],
)
def test_invalid_inputs_raise_value_error(plan, seats, coupon):
    with pytest.raises(ValueError):
        price_for(plan, seats, coupon=coupon)


def test_unknown_plan_raises_value_error_characterization():
    with pytest.raises(ValueError):
        price_for("starter", 1)
```

**Rationale**
- Nominal plan tests cover ordinary public pricing for `free` and `enterprise`, including the enterprise base fee.
- Team boundary tests focus on the important thresholds: `0`, `1`, `10`, and `11`.
- Coupon regression test protects the tier-then-discount order: `team`, 11 seats is `130.00`, then `ANNUAL10` makes `117.00`.
- Error tests cover required failure behavior without asserting private implementation details.
- Unknown plan is included as a labeled characterization test because it is observable but not explicitly listed in the planted obligations.
