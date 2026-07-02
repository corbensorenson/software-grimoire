def calculate_total(subtotal_cents, discount_cents=0, tax_basis_points=825):
    if subtotal_cents < 0:
        raise ValueError("subtotal_cents must be non-negative")
    if discount_cents < 0:
        raise ValueError("discount_cents must be non-negative")
    if tax_basis_points < 0:
        raise ValueError("tax_basis_points must be non-negative")

    tax_cents = subtotal_cents * tax_basis_points // 10_000
    return subtotal_cents + tax_cents - discount_cents
