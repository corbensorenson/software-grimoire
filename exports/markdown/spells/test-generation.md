# Spell of Test Generation

- id: `spell.test-generation.v1`
- version: `1`
- working seal: `spell://test-generation/16A7DCF9E2`
- use when: Use when behavior needs focused tests and edge-case coverage.

## Template

```text
ROLE:
Act as a meticulous test engineer.

OBJECTIVE:
Generate a focused test suite for the supplied function or module that captures intended behavior and important edge cases.

CONTEXT:
The code may be partially undocumented. Existing examples, docstrings, and type hints are the primary clues to behavior.

CONSTRAINTS:
Prefer high-signal tests over high-count tests. Group tests by behavior. Avoid mocking unless interaction boundaries require it.

Call out assumptions whenever behavior is not explicit.

PROCEDURE:
Infer invariants, enumerate edge cases, identify boundary values, and generate tests that make hidden assumptions visible.

OUTPUT CONTRACT:
Return:

1\. inferred behaviors,

2\. missing-behavior ambiguities,

3\. the test file,

4\. a short rationale for each test group.

VERIFICATION:
Include nominal cases, boundary cases, error cases, and one regression-style case if appropriate.

FAILURE BEHAVIOR:
If the code is too ambiguous for faithful tests, write characterization tests and say that you are doing so.
```
