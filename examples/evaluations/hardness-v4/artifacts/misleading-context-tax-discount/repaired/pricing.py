def calculate_total(subtotal_cents, discount_cents=0, tax_basis_points=825):
    for value in [subtotal_cents, discount_cents, tax_basis_points]:
        if value < 0:
            raise ValueError("money and tax inputs must be non-negative")
    tax = subtotal_cents * tax_basis_points // 10000
    return max(subtotal_cents + tax - discount_cents, 0)
