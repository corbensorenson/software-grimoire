I can’t safely clean up the module from the provided context alone.

I searched the workspace and found no Python source file or tests defining `normalize_user(raw)`. The only matches are prompt/evaluation text describing the task. Also, the current workspace is read-only, so I couldn’t apply edits even if the module were present.

Missing pieces needed to proceed:

- The actual module source containing `normalize_user(raw)`.
- The existing test file for that module.
- The current validation behavior for invalid input, especially exception types/messages.
- Write access to the workspace if you want me to make the change directly.

With those, I’d refactor the duplicated validation branches while preserving the public function name, stable return keys, email lowercasing, and unknown-field passthrough, then add focused tests beyond the current happy path.
