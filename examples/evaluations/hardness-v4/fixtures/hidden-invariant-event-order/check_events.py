from copy import deepcopy

from events import dedupe_events


def test_preserves_first_seen_order_and_timestamp_while_merging_payloads():
    events = [
        {"id": "b", "timestamp": "2026-07-02T10:00:00Z", "payload": {"count": 1, "note": None}},
        {"id": "a", "timestamp": "2026-07-02T10:01:00Z", "payload": {"count": 2}},
        {"id": "b", "timestamp": "2026-07-02T10:02:00Z", "payload": {"note": "kept", "flag": True}},
    ]
    result = dedupe_events(events)
    assert [event["id"] for event in result] == ["b", "a"]
    assert result[0]["timestamp"] == "2026-07-02T10:00:00Z"
    assert result[0]["payload"] == {"count": 1, "note": "kept", "flag": True}


def test_does_not_mutate_input_events():
    events = [
        {"id": "a", "timestamp": "2026-07-02T10:00:00Z", "payload": {"count": 1}},
        {"id": "a", "timestamp": "2026-07-02T10:01:00Z", "payload": {"note": "later"}},
    ]
    before = deepcopy(events)
    dedupe_events(events)
    assert events == before


def test_rejects_missing_id_instead_of_collapsing_into_none():
    try:
        dedupe_events([{"timestamp": "2026-07-02T10:00:00Z", "payload": {}}])
    except ValueError as exc:
        assert "id" in str(exc)
    else:
        raise AssertionError("events without id must be rejected")
