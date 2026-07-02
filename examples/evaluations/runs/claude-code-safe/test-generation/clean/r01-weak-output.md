Let me read the relevant files first.

<function_calls>
<invoke name="Read">
<parameter name="file_path">/Users/corbensorenson/Documents/software grimoire/pricing.py</parameter>
</invoke>
<invoke name="Read">
<parameter name="file_path">/Users/corbensorenson/Documents/software grimoire/expected_behavior.json</parameter>
</invoke>
</function_calls>
<function_calls>
<invoke name="Read">
<parameter name="file_path">/Users/corbensorenson/Documents/software grimoire/pricing.py</parameter>
</invoke>
</function_calls>

The files don't exist in the working directory. The task context references `pricing.py` and `expected_behavior.json` but neither is present — this evaluation fixture hasn't been provided to me.

**What's missing:**

- `pricing.py` — the function under test (needed to know the exact function signature, tier thresholds, and coupon codes)
- `expected_behavior.json` — the planted behavior obligations (needed to know exact expected output values)

Without these files I cannot write correct tests, only a speculative scaffold. If you'd like, paste the contents of both files here and I'll write the full test suite immediately.

---

If you want the scaffold anyway, here's the shape I'd fill in once the files are provided:

```python
import pytest
from pricing import calculate_price  # name inferred from context

# --- boundary seats ---
def test_zero_seats():        ...  # needs expected value
def test_one_seat():          ...
def test_ten_seats():         ...
def test_eleven_seats():      ...  # tier boundary flip

# --- negative seats ---
def test_negative_seats_raises():
    with pytest.raises(ValueError):
        calculate_price(-1)

# --- invalid coupon ---
def test_invalid_coupon_raises():
    with pytest.raises(ValueError):
        calculate_price(5, coupon="BOGUS")

# --- annual coupon discounts after tier pricing, rounded to cents ---
def test_annual_coupon_rounds_to_cents():
    result = calculate_price(5, coupon="ANNUAL")
    assert result == round(result, 2)

def test_annual_coupon_discounts_after_tier():
    base = calculate_price(5)
    discounted = calculate_price(5, coupon="ANNUAL")
    assert discounted < base
```

Provide the two files and I'll fill in all the concrete values.
