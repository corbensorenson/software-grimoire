# Codex Task Template: Spell of Test Generation

Use this as a local instruction snippet for a Codex task. Keep the artifact boundary, verification, and failure behavior visible.

Source: `spell.test-generation.v1`

Seal: `spell://test-generation/16A7DCF9E2`

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
