You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

EVALUATION TIER:
clean longitudinal fixture

TASK CONTEXT:
The fixture is a small pricing function with behavior that should be inferred from code and docstring.

Files:

- `pricing.py`: function under test.
- `expected_behavior.json`: planted behavior obligations.

Ground truth:

- Tests should cover public behavior, not private implementation.
- Boundary seats matter at 0, 1, 10, and 11 seats.
- Negative seats raise `ValueError`.
- Invalid coupons raise `ValueError`.
- Annual coupons discount after tier pricing and round to cents.

USER REQUEST:
ROLE: Act as a meticulous test engineer.

OBJECTIVE: Generate focused tests that capture observable behavior and important edge cases for the supplied function.

CONTEXT: Existing behavior is inferred from docstrings, examples, type hints, and current callers.

CONSTRAINTS: Prefer high-signal tests over high-count tests. Do not assert private implementation details unless no public behavior exists.

OUTPUT CONTRACT: Return inferred behaviors, ambiguities, the test file, and a rationale for each test group.

VERIFICATION: Include nominal cases, boundary cases, error cases, and one regression-style case.

FAILURE BEHAVIOR: If behavior is ambiguous, write characterization tests and label them as such.
