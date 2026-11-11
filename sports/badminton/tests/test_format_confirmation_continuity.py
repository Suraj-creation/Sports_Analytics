"""Format confirmation preserves compatible observations without backdating rules."""

import numpy as np
import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig, _PendingRally
from bai_badminton.events.rally_fsm import RallySegment, RallyState
from bai_badminton.perception_types import ChunkPerception, FramePerception
from bai_badminton.testing.synth import make_rally
from bai_engine.schema import Provenance
from bai_engine.store import EventStore


def test_same_format_confirmation_preserves_candidate_and_coordinate_epoch(tmp_path):
    with EventStore(tmp_path / "events.sqlite", "S") as store:
        engine = BadmintonMatchEngine(
            "S", EngineConfig(fps=30, frame_width=1280, frame_height=720, match_format_known=False), store
        )
        engine.set_calibration(0, make_rally().homography, emit=False)
        engine.ingest(ChunkPerception(0, 9, [FramePerception(i, None, 0.0) for i in range(10)]))
        engine._handle_fsm(engine.fsm.on_contact(5), 5)
        old_start = engine._rally_start_event
        old_calibration = engine.calibration[0]
        epoch = engine._coordinate_epoch
        events = engine.set_match_format("singles", 10, Provenance(model="format-observation"))
        assert engine.fsm.state is not RallyState.IDLE
        assert engine.fsm.start == 5
        assert engine._rally_start_event is old_start
        assert engine.calibration[0] is old_calibration
        assert engine._coordinate_epoch == epoch
        assert events[0].payload["temporal_reset"] is False
        assert not store.query(types=["rally_start"], live_only=True)[0].supersedes


def test_unknown_origin_rally_cannot_acquire_confirmed_rules_at_completion(tmp_path, monkeypatch):
    with EventStore(tmp_path / "events.sqlite", "S") as store:
        engine = BadmintonMatchEngine(
            "S", EngineConfig(fps=30, frame_width=1280, frame_height=720, match_format_known=False), store
        )
        engine.ingest(ChunkPerception(0, 9, [FramePerception(i, None, 0.0) for i in range(10)]))
        engine.set_match_format("singles", 10, Provenance(model="format-observation"))
        # Continuous format-agnostic observation can straddle the confirmation.
        old = RallySegment(5, 80, None, "stationary")
        assert engine._outcome(old)[2] == "match_format_unknown"
        monkeypatch.setattr(engine, "_outcome", lambda seg: ("unknown", "unknown", "unobservable", 0.2))
        engine._finalize_rally(_PendingRally(old, [], None), until=80)
        event = store.query(types=["rally_end"])[0]
        assert event.payload["match_format_known"] is False
        assert event.payload["match_format"] == "unknown"
        assert event.payload["winner"] is None
        assert not store.query(types=["point"])


def test_actual_discipline_change_still_breaks_coordinate_context(tmp_path):
    with EventStore(tmp_path / "events.sqlite", "S") as store:
        engine = BadmintonMatchEngine(
            "S", EngineConfig(fps=30, frame_width=1280, frame_height=720, match_format_known=False), store
        )
        engine.set_calibration(0, make_rally().homography, emit=False)
        old = engine.calibration[0]
        event = engine.set_match_format("doubles", 0, Provenance(model="format-observation"))[0]
        assert event.payload["temporal_reset"] is True
        assert engine.calibration[0] is not old
        assert engine.cfg.match_format_known
        assert engine._coordinate_epoch > 0
        assert np.isfinite(engine.calibration[0].homography.H).all()


def test_compatible_confirmation_commit_failure_restores_candidate_and_format(tmp_path, monkeypatch):
    from contextlib import contextmanager

    from bai_badminton.events.contact import ContactCandidate

    with EventStore(tmp_path / "events.sqlite", "S") as store:
        engine = BadmintonMatchEngine(
            "S", EngineConfig(fps=30, frame_width=1280, frame_height=720, match_format_known=False), store
        )
        engine.ingest(ChunkPerception(0, 9, [FramePerception(i, None, 0.0) for i in range(10)]))
        engine._handle_fsm(engine.fsm.on_contact(5), 5)
        engine._last_contact_candidate = ContactCandidate(5, None, 0.5)
        original_transaction = store.transaction
        before_ids = [event.event_id for event in store.query(live_only=False)]
        start_id = engine._rally_start_event.event_id
        epoch = engine._coordinate_epoch

        @contextmanager
        def fail_commit():
            with original_transaction():
                yield
                raise RuntimeError("injected commit failure")

        monkeypatch.setattr(store, "transaction", fail_commit)
        with pytest.raises(RuntimeError, match="injected commit"):
            engine.set_match_format("singles", 10, Provenance(model="format-observation"))
        assert engine.cfg.match_format_known is False
        assert engine._format_known_from is None
        assert engine._coordinate_epoch == epoch
        assert engine.fsm.state is RallyState.IN_PLAY and engine.fsm.start == 5
        assert engine._rally_start_event.event_id == start_id
        assert engine._last_contact_candidate == ContactCandidate(5, None, 0.5)
        assert engine._pending == []
        assert [event.event_id for event in store.query(live_only=False)] == before_ids
