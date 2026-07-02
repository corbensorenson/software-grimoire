# Falsy Metadata Refactor Trap

Trap: Naive cleanup drops falsy unknown metadata such as 0, False, empty string, empty list, and empty dict.

Expected weak failure: Weak artifact fails invariant tests for preserving unknown falsy values.
