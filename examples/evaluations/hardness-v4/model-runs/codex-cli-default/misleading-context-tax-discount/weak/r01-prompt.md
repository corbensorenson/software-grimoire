You are helping with a small software task.

Task context:

# Misleading-Context Rung: Tax Discount Contract

The fixture contains a stale inline comment that says discounts reduce taxable
basis. The current merchant contract says the opposite: tax is computed on the
subtotal, then discounts are applied against the final amount.

The task is to replace `pricing.py` while preserving `calculate_total`. A weak
artifact follows the stale comment and looks plausible. A repaired artifact
must prefer the executable contract and reject invalid negative inputs.

Starting files:

### pricing.py

```py
def calculate_total(subtotal_cents, discount_cents=0, tax_basis_points=825):
    # Legacy note: discount reduces taxable basis before tax is computed.
    raise NotImplementedError("replace this artifact")
```

Return only the replacement artifact files. Use one fenced block per file.
Each fence must identify the path using `path=<filename>` in the fence info string.
Do not include the hidden grader, shell commands, prose explanations, or files outside this list.
Allowed output paths:
- `pricing.py`
