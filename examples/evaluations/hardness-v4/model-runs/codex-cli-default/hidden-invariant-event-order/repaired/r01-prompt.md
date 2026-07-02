ROLE
Act as a careful software engineer producing the smallest reviewable artifact that satisfies the task.

OBJECTIVE
Solve this Bench v4 hardness-rung task without changing behavior outside the stated artifact boundary.

CONTEXT
# Hidden-Invariant Rung: Event Deduplication Order

The visible task is to deduplicate events by `id`. The hidden invariant is that
downstream replay depends on first-seen event order and first-seen `timestamp`
while still merging later non-null payload fields for the same event id.

The task is to replace `events.py` without changing the public function name.
An artifact that merely converts the list to a dict, sorts ids, or keeps only
the last duplicate loses replay semantics even though it looks like a valid
dedupe.

STARTING FILES
### events.py

```py
def dedupe_events(events):
    """Return one event per id."""
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
- `events.py`

VERIFICATION
The replacement files will be applied to a disposable repo-local fixture copy and checked by a private deterministic grader. Return only artifacts that should pass that check.
