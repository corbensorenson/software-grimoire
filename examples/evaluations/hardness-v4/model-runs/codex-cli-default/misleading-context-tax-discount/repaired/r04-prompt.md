ROLE
Act as a careful software engineer producing the smallest reviewable artifact that satisfies the task.

OBJECTIVE
Solve this Bench v4 hardness-rung task without changing behavior outside the stated artifact boundary.

CONTEXT
# Misleading-Context Rung: Tax Discount Contract

The fixture contains a stale inline comment that says discounts reduce taxable
basis. The current merchant contract says the opposite: tax is computed on the
subtotal, then discounts are applied against the final amount.

The task is to replace `pricing.py` while preserving `calculate_total`. A weak
artifact follows the stale comment and looks plausible. A repaired artifact
must prefer the executable contract and reject invalid negative inputs.

STARTING FILES
### pricing.py

```py
def calculate_total(subtotal_cents, discount_cents=0, tax_basis_points=825):
    # Legacy note: discount reduces taxable basis before tax is computed.
    raise NotImplementedError("replace this artifact")
```

CONSTRAINTS
- Prefer the current task contract over stale comments or misleading local context.
- Preserve public function names and compatible behavior unless the task explicitly says otherwise.
- Keep blast radius narrow: change only the allowed artifact files and document preserved out-of-scope files when a manifest is requested.
- Do not invent human signoff, external approval, network access, or device-global scratch paths.
- If the task is underspecified, encode the safest bounded behavior rather than guessing hidden state.

OUTPUT CONTRACT
Return only the replacement artifact files. Use one fenced block per file.
Each fence must identify the path using `path=<filename>` in the fence info string.
Do not include the hidden grader, shell commands, prose explanations, or files outside this list.
Allowed output paths:
- `pricing.py`

VERIFICATION
The replacement files will be applied to a disposable repo-local fixture copy and checked by a private deterministic grader. Return only artifacts that should pass that check.
