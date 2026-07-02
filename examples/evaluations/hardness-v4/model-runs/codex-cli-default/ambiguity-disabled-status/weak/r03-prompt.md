You are helping with a small software task.

Task context:

# Ambiguity Rung: Disabled Account Status

The public docstring says an account is active when it has been seen in the
last 30 days. A caller contract, however, says disabled accounts must always be
reported as `disabled` even if their last-seen timestamp is recent. Missing
last-seen data must be reported as `unknown`, not guessed active or dormant.

The task is to replace `account_status.py` while preserving the public function
name and return strings. The ambiguity is intentional: the correct artifact
must resolve the conflict by giving the caller contract precedence over the
older docstring.

Starting files:

### account_status.py

```py
from datetime import datetime, timezone


def classify_account(last_seen_at, disabled_at=None, now=None):
    """Return active when the account was seen within the last 30 days."""
    raise NotImplementedError("replace this function")
```

Return only the replacement artifact files. Use one fenced block per file.
Each fence must identify the path using `path=<filename>` in the fence info string.
Do not include the hidden grader, shell commands, prose explanations, or files outside this list.
Allowed output paths:
- `account_status.py`
