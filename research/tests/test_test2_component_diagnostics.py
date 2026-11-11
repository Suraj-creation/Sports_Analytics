"""Supersession must not inflate component coverage from append-only exports."""

from research.test2_component_diagnostics import live_events


def test_only_latest_nonretracted_contact_counts():
    events = [
        {"event_id": "a", "supersedes": None, "status": "provisional"},
        {"event_id": "b", "supersedes": "a", "status": "confirmed"},
        {"event_id": "c", "supersedes": None, "status": "retracted"},
        {"event_id": "d", "supersedes": "b", "status": "confirmed"},
    ]
    assert [row["event_id"] for row in live_events(events)] == ["d"]


def test_independent_events_survive_unknown_superseded_id():
    events = [
        {"event_id": "a", "supersedes": "not-exported", "status": "confirmed"},
        {"event_id": "b", "supersedes": None, "status": "provisional"},
    ]
    assert live_events(events) == events
