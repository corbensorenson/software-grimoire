from datetime import datetime, timezone, timedelta


def classify_account(last_seen_at, disabled_at=None, now=None):
    """Return the caller-visible account status."""
    if disabled_at is not None:
        return "disabled"

    if last_seen_at is None:
        return "unknown"

    if now is None:
        now = datetime.now(timezone.utc)

    return "active" if last_seen_at >= now - timedelta(days=30) else "dormant"
