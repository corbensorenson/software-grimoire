You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

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
Write tests for this function.
