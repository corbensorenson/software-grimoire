You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

TASK CONTEXT:
A function `price_for(plan, seats, coupon=None)` applies tiered seat pricing, rejects negative seats, supports annual coupons, and rounds currency to cents. The implementation has branches for free, team, and enterprise plans, but no tests for boundary seats or invalid coupons.

USER REQUEST:
ROLE: Act as a meticulous test engineer.

OBJECTIVE: Generate focused tests that capture observable behavior and important edge cases for the supplied function.

CONTEXT: Existing behavior is inferred from docstrings, examples, type hints, and current callers.

CONSTRAINTS: Prefer high-signal tests over high-count tests. Do not assert private implementation details unless no public behavior exists.

OUTPUT CONTRACT: Return inferred behaviors, ambiguities, the test file, and a rationale for each test group.

VERIFICATION: Include nominal cases, boundary cases, error cases, and one regression-style case.

FAILURE BEHAVIOR: If behavior is ambiguous, write characterization tests and label them as such.
