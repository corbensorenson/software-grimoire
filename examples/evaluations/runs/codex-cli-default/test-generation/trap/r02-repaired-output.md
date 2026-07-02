**Missing**
Function name/import path, call signature, exact pricing table, valid coupon names, rejection mode, and rounding rule are not supplied. Below is a focused pytest file using a one-line adapter so only the import/call needs wiring.

**Inferred Behaviors**
- Seat count is an input and negative seats are invalid.
- A discount boundary exists between `10` and `11` seats.
- Coupons can be valid or rejected.
- Monetary output must be rounded consistently.
- Behavior at the 10-to-11 boundary is important enough to guard as regression risk.

**Ambiguities**
- Whether invalid input raises `ValueError`, returns an error object, or rejects another way.
- Exact numeric prices and coupon values.
- Rounding mode: half-up, bankers rounding, cents only, etc.

**Test File**

```python
# tests/test_pricing_behavior.py
import pytest

# TODO: replace with the real import.
# from app.pricing import calculate_total


def price(seats, coupon=None):
    """Adapter: update this only if the public API differs."""
    return calculate_total(seats=seats, coupon=coupon)


def assert_money(value):
    assert isinstance(value, (int, float))
    assert round(value, 2) == value


@pytest.mark.parametrize("seats", [1, 2, 10])
def test_nominal_seat_counts_return_non_negative_money(seats):
    total = price(seats)

    assert_money(total)
    assert total >= 0


def test_valid_coupon_reduces_or_preserves_total_without_invalidating_money():
    without_coupon = price(3)
    with_coupon = price(3, coupon="SAVE10")  # replace with documented valid coupon

    assert_money(with_coupon)
    assert with_coupon <= without_coupon


@pytest.mark.parametrize("seats", [-1, -10])
def test_negative_seats_are_rejected(seats):
    with pytest.raises((ValueError, TypeError)):
        price(seats)


def test_unknown_coupon_is_rejected():
    with pytest.raises((ValueError, TypeError)):
        price(3, coupon="NOT_A_REAL_COUPON")


def test_discount_boundary_changes_at_11_seats():
    ten_total = price(10)
    eleven_total = price(11)

    assert_money(ten_total)
    assert_money(eleven_total)

    ten_unit = ten_total / 10
    eleven_unit = eleven_total / 11

    assert eleven_unit < ten_unit


def test_rounding_regression_returns_two_decimal_money_for_fractional_case():
    total = price(3, coupon="SAVE10")  # choose inputs known to produce fractional cents

    assert_money(total)
```

**Rationale**
Nominal tests cover ordinary valid usage without overfitting exact examples. Boundary coverage targets the 10-to-11 seat discount transition. Error tests cover negative seats and invalid coupons. The regression-style rounding test guards against returning unrounded fractional money, but its fixture values should be replaced with documented inputs that actually exercise fractional rounding.
