def calculate_total(subtotal_cents, discount_cents=0, tax_basis_points=825):
    if subtotal_cents < 0 or discount_cents < 0 or tax_basis_points < 0:
        raise ValueError("amounts and tax rate must be non-negative")

    tax_cents = (subtotal_cents * tax_basis_points + 5000) // 10000
    return subtotal_cents + tax_cents - discount_cents
