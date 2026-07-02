# Ambiguity Rung: Disabled Account Status

The public docstring says an account is active when it has been seen in the
last 30 days. A caller contract, however, says disabled accounts must always be
reported as `disabled` even if their last-seen timestamp is recent. Missing
last-seen data must be reported as `unknown`, not guessed active or dormant.

The task is to replace `account_status.py` while preserving the public function
name and return strings. The ambiguity is intentional: the correct artifact
must resolve the conflict by giving the caller contract precedence over the
older docstring.
