You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

EVALUATION TIER:
trap-tier fixture with planted failure mode

TASK CONTEXT:
# Boundary Obligation Trap

Trap: Happy-path tests miss negative seats, coupon rejection, rounding, and the 10-to-11 seat discount boundary.

Expected weak failure: Weak tests overfit common examples and miss behavior obligations.

USER REQUEST:
ROLE: Act as a meticulous test engineer.

OBJECTIVE: Generate focused tests that capture observable behavior and important edge cases for the supplied function.

CONTEXT: Existing behavior is inferred from docstrings, examples, type hints, and current callers.

CONSTRAINTS: Prefer high-signal tests over high-count tests. Do not assert private implementation details unless no public behavior exists.

OUTPUT CONTRACT: Return inferred behaviors, ambiguities, the test file, and a rationale for each test group.

VERIFICATION: Include nominal cases, boundary cases, error cases, and one regression-style case.

FAILURE BEHAVIOR: If behavior is ambiguous, write characterization tests and label them as such.
