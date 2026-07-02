```py path=events.py
def dedupe_events(events):
    """Return one event per id."""
    deduped = {}
    order = []

    for event in events:
        event_id = event["id"]

        if event_id not in deduped:
            deduped[event_id] = {
                **event,
                "payload": dict(event.get("payload") or {}),
            }
            order.append(event_id)
            continue

        current = deduped[event_id]
        incoming_payload = event.get("payload") or {}

        for key, value in incoming_payload.items():
            if value is not None:
                current.setdefault("payload", {})[key] = value

    return [deduped[event_id] for event_id in order]
```
