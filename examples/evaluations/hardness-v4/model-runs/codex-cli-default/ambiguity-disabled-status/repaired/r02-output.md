```py path=account_status.py
from datetime import datetime, timedelta, timezone


def classify_account(last_seen_at, disabled_at=None, now=None):
    """Return the account status as disabled, unknown, active, or dormant."""
    if disabled_at is not None:
        return "disabled"

    if last_seen_at is None:
        return "unknown"

    if now is None:
        now = datetime.now(timezone.utc)

    if last_seen_at.tzinfo is None:
        last_seen_at = last_seen_at.replace(tzinfo=timezone.utc)
    else:
        last_seen_at = last_seen_at.astimezone(timezone.utc)

    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    else:
        now = now.astimezone(timezone.utc)

    if now - last_seen_at <= timedelta(days=30):
        return "active"

    return "dormant"
```
