from datetime import datetime, timedelta, timezone

from account_status import classify_account


NOW = datetime(2026, 7, 2, 12, 0, tzinfo=timezone.utc)


def test_disabled_precedes_recent_activity():
    recent = NOW - timedelta(days=2)
    disabled = NOW - timedelta(hours=1)
    assert classify_account(recent, disabled_at=disabled, now=NOW) == "disabled"


def test_missing_last_seen_is_unknown():
    assert classify_account(None, now=NOW) == "unknown"


def test_recent_and_old_accounts_are_classified_from_utc_interval():
    assert classify_account(NOW - timedelta(days=1), now=NOW) == "active"
    assert classify_account(NOW - timedelta(days=45), now=NOW) == "dormant"


def test_naive_datetimes_are_rejected_instead_of_silently_guessed():
    naive = datetime(2026, 7, 1, 12, 0)
    try:
        classify_account(naive, now=NOW)
    except ValueError as exc:
        assert "timezone-aware" in str(exc)
    else:
        raise AssertionError("naive datetimes must be rejected")
