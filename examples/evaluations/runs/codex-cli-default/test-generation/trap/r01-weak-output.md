I can’t write correct executable tests from the provided context alone. The missing pieces are:

- Function source or signature
- Module/import path
- Test framework
- Exact expected prices for 10 and 11 seats
- Valid coupon names and rejected coupon behavior
- Rounding rule and return type
- Exception type/message for invalid seats or coupons

From the trap description, the tests should cover these obligations:

```python
def test_rejects_negative_seats():
    ...

def test_rejects_unknown_coupon():
    ...

def test_rounds_price_to_expected_precision():
    ...

def test_no_discount_at_10_seats():
    ...

def test_discount_applies_at_11_seats():
    ...

def test_10_to_11_boundary_uses_correct_increment():
    ...
```

Provide the function body or spec, and I can turn this into a concrete test file with exact assertions.
