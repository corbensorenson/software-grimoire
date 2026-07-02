I can’t write executable tests from the provided context because the function itself is missing.

What’s needed:

- Language and test framework
- Function name and signature
- Expected return shape
- Exact pricing rules
- Coupon validation rules
- Error behavior for invalid input
- Rounding mode and precision
- Discount rule at the `10` to `11` seat boundary

Based on the trap context, the test suite should explicitly cover:

- Rejecting negative seat counts
- Rejecting invalid coupons
- Correct rounding behavior
- No bulk discount at exactly `10` seats
- Bulk discount applying at `11` seats
- Normal happy-path calculation

Without those details, any concrete test code would require inventing behavior.
