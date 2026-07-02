from datetime import datetime, timedelta, timezone


def _require_aware(value, name):
    if value is not None and value.tzinfo is None:
        raise ValueError(f"{name} must be timezone-aware")


def classify_account(last_seen_at, disabled_at=None, now=None):
    """Classify account status using the caller contract before stale docs."""
    now = now or datetime.now(timezone.utc)
    _require_aware(now, "now")
    _require_aware(last_seen_at, "last_seen_at")
    _require_aware(disabled_at, "disabled_at")

    if disabled_at is not None:
        return "disabled"
    if last_seen_at is None:
        return "unknown"
    if now - last_seen_at <= timedelta(days=30):
        return "active"
    return "dormant"
