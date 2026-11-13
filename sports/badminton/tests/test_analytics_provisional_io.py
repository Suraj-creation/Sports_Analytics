"""Candidate-only analytics need no geometry; official statistics keep the gate."""

import pytest

from bai_badminton.analytics.rebuild import build
from bai_engine.schema import TRACK_ARROW_SCHEMA, Event, Provenance, TrackObject
from bai_engine.store import EventStore


@pytest.mark.parametrize("official", [False, True])
def test_geometry_is_read_only_when_an_official_rally_consumes_it(tmp_path, official):
    reads = []

    class Tracks:
        def read(self, objects, start, end):
            reads.append((objects, start, end))
            return TRACK_ARROW_SCHEMA.empty_table()

    with EventStore(tmp_path / "events.sqlite", "S1") as store:
        store.append(Event(
            session_id="S1", type="rally_end", frame_start=10, frame_end=80, pts_us=333333,
            provenance=Provenance(model="controlled"),
            payload={"official": official, "rally_no": 1 if official else 0, "shots": []},
        ))
        actual = build(store, Tracks(), 30).to_public()
        expected = build(store, None, 30).to_public()
    assert actual == expected  # Empty spatial evidence is never a physical measurement.
    assert reads == ([([TrackObject.CAMERA], 0, 80), ([TrackObject.PLAYER], 10, 80)] if official else [])


def test_empty_log_does_not_scan_geometry(tmp_path):
    class Tracks:
        def read(self, *_):
            pytest.fail("No spatial consumer exists in an empty log")

    with EventStore(tmp_path / "events.sqlite", "S1") as store:
        assert build(store, Tracks(), 30).to_public() == build(store, None, 30).to_public()
