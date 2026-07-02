def dedupe_events(events):
    """Return one event per id, preserving first replay order and timestamp."""
    deduped = {}

    for event in events:
        event_id = event["id"]

        if event_id not in deduped:
            merged = dict(event)
            if isinstance(event.get("payload"), dict):
                merged["payload"] = dict(event["payload"])
            deduped[event_id] = merged
            continue

        existing_payload = deduped[event_id].setdefault("payload", {})
        incoming_payload = event.get("payload") or {}

        for key, value in incoming_payload.items():
            if value is not None:
                existing_payload[key] = value

    return list(deduped.values())
