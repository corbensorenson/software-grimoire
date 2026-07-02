# Misleading-Context Rung: Tax Discount Contract

The fixture contains a stale inline comment that says discounts reduce taxable
basis. The current merchant contract says the opposite: tax is computed on the
subtotal, then discounts are applied against the final amount.

The task is to replace `pricing.py` while preserving `calculate_total`. A weak
artifact follows the stale comment and looks plausible. A repaired artifact
must prefer the executable contract and reject invalid negative inputs.
