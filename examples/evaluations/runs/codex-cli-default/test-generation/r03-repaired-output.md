**Inferred Behaviors**
`price_for(plan, seats, coupon=None)` returns monthly dollar pricing. Supported plans are `free`, `team`, and `enterprise`. Negative seats, unknown plans, and unknown coupons raise `ValueError`. `ANNUAL10` applies after base/tier pricing and returns cents.

**Ambiguities**
The docstring does not explicitly document return type or valid plan names. I treat unknown-plan behavior as a characterization test and avoid asserting private implementation details or exact error messages.

**Test File: `test_pricing.py`**
```python
from decimal import Decimal

import pytest

from pricing import price_for


@pytest.mark.parametrize("seats", [0, 1, 10, 11])
def test_free_plan_costs_zero_at_boundary_seat_counts(seats):
    assert price_for("free", seats) == Decimal("0.00")


@pytest.mark.parametrize(
    ("seats", "expected"),
    [
        (0, Decimal("0.00")),
        (1, Decimal("12.00")),
        (10, Decimal("120.00")),
        (11, Decimal("130.00")),
    ],
)
def test_team_plan_boundary_pricing(seats, expected):
    assert price_for("team", seats) == expected


@pytest.mark.parametrize(
    ("seats", "expected"),
    [
        (0, Decimal("99.00")),
        (1, Decimal("107.00")),
    ],
)
def test_enterprise_plan_includes_base_fee(seats, expected):
    assert price_for("enterprise", seats) == expected


def test_negative_seats_raise_value_error():
    with pytest.raises(ValueError):
        price_for("team", -1)


def test_unknown_coupon_raises_value_error():
    with pytest.raises(ValueError):
        price_for("team", 1, coupon="BOGUS")


def test_unknown_plan_raises_value_error_characterization():
    with pytest.raises(ValueError):
        price_for("unknown", 1)


def test_annual10_discount_applies_after_tier_pricing_and_rounds_to_cents():
    assert price_for("team", 11, coupon="ANNUAL10") == Decimal("117.00")
    assert str(price_for("team", 1, coupon="ANNUAL10")) == "10.80"
```

**Rationale**
Nominal coverage checks free, team, and enterprise public prices. Boundary coverage focuses on seats `0`, `1`, `10`, and `11`, especially the team tier transition. Error tests cover required invalid inputs without depending on messages. The annual coupon test is regression-style: it catches applying the discount before the team tier adjustment and verifies cents formatting.
