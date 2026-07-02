from copy import deepcopy


def dedupe_events(events):
    """Return one event per id while preserving replay order invariants."""
    ordered_ids = []
    by_id = {}
    for event in events:
        if "id" not in event:
            raise ValueError("event id is required")
        event_id = event["id"]
        if event_id not in by_id:
            ordered_ids.append(event_id)
            by_id[event_id] = deepcopy(event)
            by_id[event_id]["payload"] = dict(event.get("payload") or {})
            continue

        merged_payload = by_id[event_id].setdefault("payload", {})
        for key, value in (event.get("payload") or {}).items():
            if value is not None:
                merged_payload[key] = value
    return [by_id[event_id] for event_id in ordered_ids]
