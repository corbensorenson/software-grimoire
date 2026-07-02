def calculate_total(subtotal_cents, discount_cents=0, tax_basis_points=825):
    taxable = max(subtotal_cents - discount_cents, 0)
    tax = taxable * tax_basis_points // 10000
    return taxable + tax
