from datetime import datetime, timedelta, timezone


def classify_account(last_seen_at, disabled_at=None, now=None):
    """Return active when the account was seen within the last 30 days."""
    now = now or datetime.now(timezone.utc)
    if last_seen_at is None:
        return "dormant"
    if now - last_seen_at <= timedelta(days=30):
        return "active"
    return "dormant"
