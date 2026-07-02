ROLE
Act as a careful software engineer producing the smallest reviewable artifact that satisfies the task.

OBJECTIVE
Solve this Bench v4 hardness-rung task without changing behavior outside the stated artifact boundary.

CONTEXT
# Ambiguity Rung: Disabled Account Status

The public docstring says an account is active when it has been seen in the
last 30 days. A caller contract, however, says disabled accounts must always be
reported as `disabled` even if their last-seen timestamp is recent. Missing
last-seen data must be reported as `unknown`, not guessed active or dormant.

The task is to replace `account_status.py` while preserving the public function
name and return strings. The ambiguity is intentional: the correct artifact
must resolve the conflict by giving the caller contract precedence over the
older docstring.

STARTING FILES
### account_status.py

```py
from datetime import datetime, timezone


def classify_account(last_seen_at, disabled_at=None, now=None):
    """Return active when the account was seen within the last 30 days."""
    raise NotImplementedError("replace this function")
```

CONSTRAINTS
- Prefer the current task contract over stale comments or misleading local context.
- Preserve public function names and compatible behavior unless the task explicitly says otherwise.
- Keep blast radius narrow: change only the allowed artifact files and document preserved out-of-scope files when a manifest is requested.
- Do not invent human signoff, external approval, network access, or device-global scratch paths.
- If the task is underspecified, encode the safest bounded behavior rather than guessing hidden state.

OUTPUT CONTRACT
Return only the replacement artifact files. Use one fenced block per file.
Each fence must identify the path using `path=<filename>` in the fence info string.
Do not include the hidden grader, shell commands, prose explanations, or files outside this list.
Allowed output paths:
- `account_status.py`

VERIFICATION
The replacement files will be applied to a disposable repo-local fixture copy and checked by a private deterministic grader. Return only artifacts that should pass that check.
