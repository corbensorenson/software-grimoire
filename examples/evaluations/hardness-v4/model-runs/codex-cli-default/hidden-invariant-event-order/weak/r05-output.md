```py path=events.py
def dedupe_events(events):
    """Return one event per id, preserving replay order and first timestamps."""
    deduped = {}
    order = []

    for event in events:
        event_id = event["id"]

        if event_id not in deduped:
            order.append(event_id)
            deduped[event_id] = {
                **event,
                "payload": dict(event.get("payload") or {}),
            }
            continue

        merged_payload = deduped[event_id].setdefault("payload", {})
        for key, value in (event.get("payload") or {}).items():
            if value is not None:
                merged_payload[key] = value

    return [deduped[event_id] for event_id in order]
```
