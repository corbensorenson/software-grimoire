You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

TASK CONTEXT:
The fixture is a Python module at `examples/evaluations/fixtures/safe-refactoring/normalize_user.py`.

Ground truth:

- Public function `normalize_user(raw)` must keep its name, one-argument signature, return type, and return keys.
- Email values are stripped and lowercased.
- `display_name` is stripped when present.
- Unknown fields must be preserved in `extra`.
- Falsy-but-valid values such as `0`, `False`, and empty strings in unknown fields must not be dropped.
- Invalid input still raises `TypeError`.

Use `python -m pytest examples/evaluations/fixtures/safe-refactoring/check_normalize_user.py` as the executable fixture check.

USER REQUEST:
ROLE: Act as a senior Python engineer performing behavior-preserving refactoring.

OBJECTIVE: Remove duplication in the supplied module without changing public behavior.

CONTEXT: The module is imported by two API handlers and one CLI entry point. Existing tests cover only the happy path.

CONSTRAINTS: Do not change public function names, parameter order, return types, or raised exception classes. Touch only this module and its tests.

OUTPUT CONTRACT: Return a minimal patch plan, the proposed refactor, and tests that prove unchanged behavior.

VERIFICATION: State the invariants first; then show before/after test cases for edge inputs.

FAILURE BEHAVIOR: If the module boundary is too small for a safe refactor, say exactly what adjacent file must also move and why.
