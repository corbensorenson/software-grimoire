from datetime import datetime, timedelta, timezone


def classify_account(last_seen_at, disabled_at=None, now=None):
    """Return disabled, unknown, active, or dormant for an account."""
    if disabled_at is not None:
        return "disabled"

    if last_seen_at is None:
        return "unknown"

    if now is None:
        now = datetime.now(timezone.utc)

    if last_seen_at.tzinfo is None:
        last_seen_at = last_seen_at.replace(tzinfo=timezone.utc)

    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    cutoff = now.astimezone(timezone.utc) - timedelta(days=30)
    if last_seen_at.astimezone(timezone.utc) >= cutoff:
        return "active"

    return "dormant"
