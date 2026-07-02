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
Clean up this Python module and make it nicer.
