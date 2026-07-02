from copy import deepcopy


def dedupe_events(events):
    """Return one event per id."""
    by_id = {}
    deduped = []

    for event in events:
        event_id = event["id"]

        if event_id not in by_id:
            merged = deepcopy(event)
            by_id[event_id] = merged
            deduped.append(merged)
            continue

        existing = by_id[event_id]
        payload = event.get("payload") or {}
        existing_payload = existing.setdefault("payload", {})

        for key, value in payload.items():
            if value is not None:
                existing_payload[key] = deepcopy(value)

    return deduped
