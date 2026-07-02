def dedupe_events(events):
    """Return one event per id."""
    deduped = {}
    order = []

    for event in events:
        event_id = event["id"]

        if event_id not in deduped:
            merged = dict(event)
            if isinstance(merged.get("payload"), dict):
                merged["payload"] = dict(merged["payload"])
            deduped[event_id] = merged
            order.append(event_id)
            continue

        payload = event.get("payload")
        if isinstance(payload, dict):
            merged_payload = deduped[event_id].setdefault("payload", {})
            for key, value in payload.items():
                if value is not None:
                    merged_payload[key] = value

    return [deduped[event_id] for event_id in order]
