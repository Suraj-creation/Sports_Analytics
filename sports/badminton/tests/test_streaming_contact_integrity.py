"""Processing boundaries must not create shots or service evidence."""

from itertools import pairwise
from pathlib import Path

import pytest

from bai_badminton.analytics.match import MatchAnalytics, RallyRecord
from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.events.contact import detect_contacts
from bai_badminton.events.rally_fsm import RallyFSM, RallyParams, RallySegment, RallyState, RallyUpdate
from bai_badminton.perception_types import ChunkPerception
from bai_badminton.testing.synth import make_rally, to_frames
from bai_engine.schema import ConfidenceBand
from bai_engine.store import EventStore


@pytest.mark.parametrize("size", [1, 16, 32, 53, 54, 55, 56, 64])
def test_contextual_peaks_are_independent_of_requested_partition(size: int) -> None:
    window = make_rally().obs
    expected = [c.frame for c in detect_contacts(window, enforce_alternation=False)]
    actual = [
        c.frame
        for start in range(0, window.n, size)
        for c in detect_contacts(window, start=start, stop=min(window.n, start + size), enforce_alternation=False)
    ]
    assert actual == expected
    assert all(b - a > 6 for a, b in pairwise(actual))


def run_rally(path: Path, *, chunk_size: int, lead_in: int = 30):
    rally = make_rally(lead_in=lead_in)
    frames = to_frames(rally, 0)
    store = EventStore(path, "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
    engine.set_calibration(0, rally.homography)
    for start in range(0, len(frames), chunk_size):
        selected = frames[start : start + chunk_size]
        engine.ingest(ChunkPerception(start=start, end=selected[-1].frame_idx, frames=selected))
    engine.flush()
    return engine, store


@pytest.mark.parametrize("size", [1, 16, 32, 64])
def test_engine_contact_and_classification_events_are_partition_invariant(tmp_path: Path, size: int) -> None:
    _, whole = run_rally(tmp_path / "whole.sqlite", chunk_size=1000)
    _, split = run_rally(tmp_path / "split.sqlite", chunk_size=size)
    for kind in ("contact", "stroke"):

        def signature(store, event_type=kind):
            return [
                (
                    e.frame_start,
                    e.actors.player_id,
                    e.payload.get("stroke"),
                    e.payload.get("is_serve"),
                    e.payload.get("flight_time_s"),
                )
                for e in store.query(types=[event_type])
            ]

        assert signature(split) == signature(whole)
    split.close()
    whole.close()


def test_segment_start_without_service_history_is_unknown_but_later_shots_remain(tmp_path: Path) -> None:
    _, store = run_rally(tmp_path / "cut.sqlite", chunk_size=32, lead_in=0)
    strokes = store.query(types=["stroke"])
    assert strokes
    first = strokes[0]
    assert first.payload["is_serve"] is None
    assert first.payload["stroke"] == "unknown"
    assert first.payload["serve_evidence"]["reason"] == "insufficient_precontact_context"
    assert any(s.payload["stroke"] != "unknown" for s in strokes[1:])
    assert all(s.payload["classification_status"] in ("estimated", "unknown") for s in strokes)
    store.close()


def test_service_formation_is_estimated_and_observed_incoming_flight_is_not_serve(tmp_path: Path) -> None:
    engine, store = run_rally(tmp_path / "serve.sqlite", chunk_size=64)
    strokes = store.query(types=["stroke"])
    assert strokes[0].payload["is_serve"] is True
    assert strokes[0].payload["serve_evidence"]["status"] == "estimated"
    serve, evidence = engine._serve_context(strokes[1].frame_start, initial=True)
    assert serve is False
    assert evidence["reason"] == "observed_incoming_flight"
    for contact in store.query(types=["contact"]):
        assert contact.payload["contact_status"] == "estimated"
        assert contact.payload["racket_contact_observed"] is False
        assert contact.band is not ConfidenceBand.CONFIRMED
    store.close()


def test_highlight_cites_shots_and_does_not_reward_unknown_family_variety() -> None:
    analytics = MatchAnalytics(30)
    rally = RallyRecord(
        rally_id="rally",
        rally_no=1,
        start=0,
        end=90,
        winner=None,
        loser=None,
        outcome="unknown",
        shots=[{"event_id": "shot", "stroke": "unknown"}],
        score_after={},
        game_no=1,
        flags_before={},
        duration_s=3,
    )
    highlight = analytics.score_rally(rally).to_public()
    assert highlight["reasons"]["variety"] == 0
    assert highlight["evidence_ids"] == ["rally", "shot"]
    assert highlight["evidence_status"] == "estimated_events"
    assert highlight["score_semantics"] == "ranking_score_not_probability"


def test_same_step_rally_finalization_preserves_both_start_references(tmp_path: Path) -> None:
    store = EventStore(tmp_path / "transitions.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
    engine._handle_fsm(RallyUpdate(started=10), 10)
    old = engine._rally_start_event
    engine._handle_fsm(RallyUpdate(finalized=RallySegment(10, 100, 10, "gap"), started=130), 130)
    assert engine._pending[0].start_event == old
    assert engine._rally_start_event is not None
    assert engine._rally_start_event.frame_start == 130
    assert engine._rally_start_event.event_id != old.event_id
    store.close()


def test_contact_after_merge_deadline_starts_new_rally() -> None:
    fsm = RallyFSM(RallyParams(fps=30))
    fsm.state = RallyState.CLOSED
    fsm.closed = RallySegment(0, 100, 0, "gap")
    update = fsm.on_contact(123)
    assert update.finalized == RallySegment(0, 100, 0, "gap")
    assert update.started == 123
    assert fsm.start == 123


def test_stationary_buffer_cannot_end_exchange_before_accepted_contact() -> None:
    fsm = RallyFSM(RallyParams(fps=30))
    fsm.on_contact(0)
    for frame in range(1, 70):
        fsm.step(frame, True, 10)
    for frame in range(70, 80):
        fsm.step(frame, True, 0)
    fsm.on_contact(80)
    fsm.step(80, True, 0)
    assert fsm.tentative_end is None or fsm.tentative_end >= 80
    final = fsm.flush(100).finalized
    assert final is not None and final.end >= 80
