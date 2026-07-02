You are completing a software-engineering task. Use only the context below.
If the task is underspecified, say what is missing instead of inventing facts.
Keep the answer under 450 words.

EVALUATION TIER:
trap-tier fixture with planted failure mode

TASK CONTEXT:
# Falsy Metadata Refactor Trap

Trap: Naive cleanup drops falsy unknown metadata such as 0, False, empty string, empty list, and empty dict.

Expected weak failure: Weak artifact fails invariant tests for preserving unknown falsy values.

USER REQUEST:
ROLE: Act as a senior Python engineer performing behavior-preserving refactoring.

OBJECTIVE: Remove duplication in the supplied module without changing public behavior.

CONTEXT: The module is imported by two API handlers and one CLI entry point. Existing tests cover only the happy path.

CONSTRAINTS: Do not change public function names, parameter order, return types, or raised exception classes. Touch only this module and its tests.

OUTPUT CONTRACT: Return a minimal patch plan, the proposed refactor, and tests that prove unchanged behavior.

VERIFICATION: State the invariants first; then show before/after test cases for edge inputs.

FAILURE BEHAVIOR: If the module boundary is too small for a safe refactor, say exactly what adjacent file must also move and why.
