def dedupe_events(events):
    """Return one event per id."""
    by_id = {}
    for event in events:
        by_id[event.get("id")] = event
    return [by_id[key] for key in sorted(by_id)]
