from datetime import datetime, timezone, timedelta


def classify_account(last_seen_at, disabled_at=None, now=None):
    """Classify an account as disabled, unknown, active, or dormant."""
    if disabled_at is not None:
        return "disabled"

    if last_seen_at is None:
        return "unknown"

    if now is None:
        now = datetime.now(timezone.utc)

    return "active" if now - last_seen_at <= timedelta(days=30) else "dormant"
