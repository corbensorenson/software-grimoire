def dedupe_events(events):
    """Return one event per id, preserving first-seen replay order."""
    by_id = {}
    order = []

    for event in events:
        event_id = event["id"]

        if event_id not in by_id:
            by_id[event_id] = {
                **event,
                "payload": dict(event.get("payload") or {}),
            }
            order.append(event_id)
            continue

        merged = by_id[event_id]
        for key, value in (event.get("payload") or {}).items():
            if value is not None:
                merged["payload"][key] = value

    return [by_id[event_id] for event_id in order]
