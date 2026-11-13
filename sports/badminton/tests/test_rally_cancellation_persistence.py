"""Cancellation evidence survives the append-only ledger and export model."""

from types import SimpleNamespace

import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.events.rally_fsm import RallySegment, RallyUpdate
from bai_engine.schema import EventStatus, EvidenceKind
from bai_engine.store import EventStore


@pytest.mark.parametrize("legacy", [False, True])
def test_retraction_preserves_old_start_and_exact_candidate_or_unknown_interval(tmp_path, legacy):
    store = EventStore(tmp_path / "events.sqlite", "S1")
    try:
        engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
        start = engine._event("rally_start", 10, 10, payload={"rally_no": 1}, model="controlled")
        engine._rally_start_event = start
        engine._emit([start])
        if legacy:
            update = SimpleNamespace(cancelled_start=10, finalized=None, started=50)
        else:
            update = RallyUpdate(cancelled_start=10, cancelled_segment=RallySegment(10, 20, 10, "gap"), started=50)
        engine._handle_fsm(update, 50)
        events = store.since()
        withdrawn = next(e for e in events if e.status is EventStatus.RETRACTED)
        assert withdrawn.supersedes == start.event_id
        assert withdrawn.frame_start == 10
        details = withdrawn.payload["cancellation"]
        assert details["candidate_start"] == 10
        assert details["minimum_duration_frames"] == 60
        assert details["semantics"] == "rejected_numerical_candidate;not_verified_physical_rally"
        assert details["candidate_end"] == (None if legacy else 20)
        assert details["duration_frames"] == (None if legacy else 11)
        assert details["terminal_reason"] == (None if legacy else "gap")
        windows = [e.frames for e in withdrawn.evidence if e.kind is EvidenceKind.TRACK_WINDOW]
        assert windows == ([] if legacy else [(10, 20)])
        assert engine._rally_start_event.frame_start == 50
        assert not any(e.type == "rally_end" for e in events)
    finally:
        store.close()
