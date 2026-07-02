# Hidden-Invariant Rung: Event Deduplication Order

The visible task is to deduplicate events by `id`. The hidden invariant is that
downstream replay depends on first-seen event order and first-seen `timestamp`
while still merging later non-null payload fields for the same event id.

The task is to replace `events.py` without changing the public function name.
An artifact that merely converts the list to a dict, sorts ids, or keeps only
the last duplicate loses replay semantics even though it looks like a valid
dedupe.
