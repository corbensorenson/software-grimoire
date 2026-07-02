def dedupe_events(events):
    """Return one event per id, preserving replay order and merged payload data."""
    deduped = []
    by_id = {}

    for event in events:
        event_id = event["id"]

        if event_id not in by_id:
            merged = event.copy()
            payload = merged.get("payload")
            if isinstance(payload, dict):
                merged["payload"] = payload.copy()

            by_id[event_id] = merged
            deduped.append(merged)
            continue

        incoming_payload = event.get("payload")
        if not isinstance(incoming_payload, dict):
            continue

        merged = by_id[event_id]
        merged_payload = merged.get("payload")
        if not isinstance(merged_payload, dict):
            merged_payload = {}
            merged["payload"] = merged_payload

        for key, value in incoming_payload.items():
            if value is not None:
                merged_payload[key] = value

    return deduped
