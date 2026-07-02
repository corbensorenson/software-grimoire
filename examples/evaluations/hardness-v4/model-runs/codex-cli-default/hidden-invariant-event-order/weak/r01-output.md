```py path=events.py
from copy import deepcopy


def dedupe_events(events):
    """Return one event per id."""
    deduped = []
    by_id = {}

    for event in events:
        event_id = event["id"]

        if event_id not in by_id:
            kept = deepcopy(event)
            by_id[event_id] = kept
            deduped.append(kept)
            continue

        kept = by_id[event_id]
        payload = event.get("payload")

        if isinstance(payload, dict):
            kept_payload = kept.setdefault("payload", {})
            if not isinstance(kept_payload, dict):
                kept_payload = {}
                kept["payload"] = kept_payload

            for key, value in payload.items():
                if value is not None:
                    kept_payload[key] = deepcopy(value)
        elif payload is not None:
            kept["payload"] = deepcopy(payload)

    return deduped
```
