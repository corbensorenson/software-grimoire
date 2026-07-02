**Inferred Behaviors**

- `price_for(plan, seats, coupon=None)` returns a currency amount rounded to cents.
- Negative `seats` are rejected.
- Supported public plans appear to be `free`, `team`, and `enterprise`.
- Pricing is tiered by seat count.
- Coupons exist, at least for annual pricing.
- Invalid coupons currently lack tests and should be covered via observable behavior.

**Ambiguities**

Missing from the supplied context:

- Exact seat-tier boundaries.
- Exact prices per tier.
- Whether `seats=0` is valid.
- Return type: `float`, `Decimal`, or integer cents.
- Exact exception type/message for negative seats.
- Coupon format and valid coupon names.
- Expected behavior for invalid coupons: ignored, rejected, or treated as expired.
- Whether unknown plans raise or return a fallback.

Because those are ambiguous, the boundary and coupon tests below are labeled as characterization tests and use placeholders that should be filled from docstrings/examples/current callers.

**Test File: `test_price_for.py`**

```python
import pytest

from pricing import price_for


# Fill these from docstrings/examples/current callers.
TEAM_TIER_BOUNDARY = ...
ENTERPRISE_TIER_BOUNDARY = ...

VALID_ANNUAL_COUPON = ...
INVALID_COUPON = ...

EXPECTED_FREE_0 = ...
EXPECTED_TEAM_1 = ...
EXPECTED_TEAM_BOUNDARY = ...
EXPECTED_TEAM_AFTER_BOUNDARY = ...
EXPECTED_ENTERPRISE_1 = ...
EXPECTED_ENTERPRISE_BOUNDARY = ...
EXPECTED_ENTERPRISE_AFTER_BOUNDARY = ...
EXPECTED_TEAM_ANNUAL_COUPON = ...


@pytest.mark.parametrize(
    ("plan", "seats", "coupon", "expected"),
    [
        pytest.param("free", 0, None, EXPECTED_FREE_0, id="free-zero-seats"),
        pytest.param("team", 1, None, EXPECTED_TEAM_1, id="team-one-seat"),
        pytest.param("enterprise", 1, None, EXPECTED_ENTERPRISE_1, id="enterprise-one-seat"),
    ],
)
def test_price_for_nominal_supported_plans(plan, seats, coupon, expected):
    assert price_for(plan, seats, coupon) == expected


@pytest.mark.parametrize(
    ("plan", "seats", "expected"),
    [
        pytest.param("team", TEAM_TIER_BOUNDARY, EXPECTED_TEAM_BOUNDARY, id="team-at-tier-boundary"),
        pytest.param("team", TEAM_TIER_BOUNDARY + 1, EXPECTED_TEAM_AFTER_BOUNDARY, id="team-after-tier-boundary"),
        pytest.param(
            "enterprise",
            ENTERPRISE_TIER_BOUNDARY,
            EXPECTED_ENTERPRISE_BOUNDARY,
            id="enterprise-at-tier-boundary",
        ),
        pytest.param(
            "enterprise",
            ENTERPRISE_TIER_BOUNDARY + 1,
            EXPECTED_ENTERPRISE_AFTER_BOUNDARY,
            id="enterprise-after-tier-boundary",
        ),
    ],
)
def test_price_for_characterizes_tier_boundaries(plan, seats, expected):
    assert price_for(plan, seats) == expected


@pytest.mark.parametrize("seats", [-1, -10])
def test_price_for_rejects_negative_seats(seats):
    with pytest.raises(ValueError):
        price_for("team", seats)


def test_price_for_applies_valid_annual_coupon():
    assert price_for("team", 1, VALID_ANNUAL_COUPON) == EXPECTED_TEAM_ANNUAL_COUPON


def test_price_for_characterizes_invalid_coupon_behavior():
    """
    Characterization test.

    Replace the assertion with the observed public behavior:
    either raises a documented exception, ignores the coupon, or returns
    a specific validation result.
    """
    with pytest.raises(ValueError):
        price_for("team", 1, INVALID_COUPON)


def test_price_for_rounds_currency_to_cents_regression():
    result = price_for("team", TEAM_TIER_BOUNDARY + 1)

    # Works for float or Decimal without asserting private pricing internals.
    assert round(result, 2) == result
```

**Rationale**

- Nominal tests cover each public plan branch.
- Boundary tests target the highest-risk tier transitions.
- Error tests lock down negative-seat rejection.
- Coupon tests cover valid discount behavior and invalid coupon handling.
- The rounding regression test protects against fractional-cent leaks without depending on implementation details.
