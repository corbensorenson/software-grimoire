def dedupe_events(events):
    """Return one event per id."""
    by_id = {}
    ordered = []

    for event in events:
        event_id = event["id"]

        if event_id not in by_id:
            deduped = dict(event)
            if isinstance(event.get("payload"), dict):
                deduped["payload"] = dict(event["payload"])
            by_id[event_id] = deduped
            ordered.append(deduped)
            continue

        existing = by_id[event_id]

        if "timestamp" in existing and "timestamp" in event:
            existing["timestamp"] = existing["timestamp"]

        payload = event.get("payload")
        if isinstance(payload, dict):
            existing_payload = existing.get("payload")
            if not isinstance(existing_payload, dict):
                existing_payload = {}
                existing["payload"] = existing_payload

            for key, value in payload.items():
                if value is not None:
                    existing_payload[key] = value

    return ordered
