from datetime import datetime, timezone


def classify_account(last_seen_at, disabled_at=None, now=None):
    """Return active when the account was seen within the last 30 days."""
    raise NotImplementedError("replace this function")
