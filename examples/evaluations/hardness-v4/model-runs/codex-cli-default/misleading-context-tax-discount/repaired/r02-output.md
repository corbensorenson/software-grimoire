```py path=pricing.py
def calculate_total(subtotal_cents, discount_cents=0, tax_basis_points=825):
    if subtotal_cents < 0 or discount_cents < 0 or tax_basis_points < 0:
        raise ValueError("negative inputs are not allowed")

    tax_cents = (subtotal_cents * tax_basis_points) // 10_000
    return subtotal_cents + tax_cents - discount_cents
```
