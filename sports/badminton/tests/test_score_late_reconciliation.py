"""Delayed broadcast evidence revises decisions without fabricating attribution.

Perception is replaced by an explicit unknown terminal outcome and cached phase
context. OCR, phase policy, BWF rules, corrections, persistence and retries are
real. These fixtures establish software invariants, not video accuracy.
"""

import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig, _PendingRally
from bai_badminton.events.match_phase import RallyEvidence
from bai_badminton.events.rally_fsm import RallySegment
from bai_badminton.perception_types import ChunkPerception, FramePerception, ScoreReading
from bai_badminton.rules import MatchConfig
from bai_engine.schema import EventStatus, Provenance
from bai_engine.store import EventStore


_CONTEXT = RallyEvidence(
    calibrated=True, formation=True, still=True, gap_s=8.75, after_cut=False, scoreboard=None,
)
_NAMES = {
    "singles": ({"P1": "Alice", "P2": "Bob"}, ("ALICE", "BOB")),
    "doubles": (
        {"P1": "Alex Reed / Morgan Chen", "P2": "Robin Singh / Taylor Park"},
        ("REED A. / CHEN M.", "SINGH R. / PARK T."),
    ),
}


def _reading(frame, points, names=("ALICE", "BOB")):
    return ScoreReading(frame, ((names[0], points[0]), (names[1], points[1])), conf=0.95)


def _board(engine, frame, points, names=("ALICE", "BOB")):
    for offset in (0, 5):
        engine.on_ocr(_reading(frame + offset, points, names))


def _engine(tmp_path, monkeypatch, *, discipline="singles", player_names=None, horizon_s=None, emit=None):
    configured, names = _NAMES[discipline]
    kwargs = {} if horizon_s is None else {"score_reconciliation_s": horizon_s}
    cfg = EngineConfig(
        fps=30, frame_width=1280, frame_height=720, match=MatchConfig(discipline=discipline), **kwargs,
    )
    store = EventStore(tmp_path / "late-score.sqlite", "S1")
    engine = BadmintonMatchEngine(
        "S1", cfg, store, emit=emit,
        player_names=configured if player_names is None else player_names,
    )
    monkeypatch.setattr(engine, "_outcome", lambda seg: (
        "unknown", "unknown", "terminal_not_observed", 0.2,
    ))
    monkeypatch.setattr(engine, "_phase_evidence", lambda seg, until: _CONTEXT)
    _board(engine, 0, (3, 2), names)
    return engine, store, names


def _finalize_unknown(engine, store, intervals=None, segments=((100, 200),)):
    if intervals is not None:
        engine.set_reviewed_match_intervals(intervals, Provenance(model="human"))
    engine._pending = [
        _PendingRally(RallySegment(start, end, None, "stationary"), [], None)
        for start, end in segments
    ]
    # The built-in 4-second OCR wait has elapsed. No post-rally board was read.
    engine._finalize_pending(450)
    assert len(store.query(types=["rally_end"])) == len(segments)
    assert store.query(types=["point"]) == []
    assert all(event.payload["winner"] is None for event in store.query(types=["rally_end"]))


@pytest.mark.parametrize("discipline", ["singles", "doubles"])
def test_late_stable_increment_resolves_original_rally_for_individual_or_team(tmp_path, monkeypatch, discipline):
    engine, store, names = _engine(tmp_path, monkeypatch, discipline=discipline)
    with store:
        _finalize_unknown(engine, store)
        original = store.query(types=["rally_end"])[0]

        def do_not_recompute_old_geometry(seg, until):
            raise AssertionError("late OCR must retain the original rally's phase context")

        monkeypatch.setattr(engine, "_phase_evidence", do_not_recompute_old_geometry)
        _board(engine, 500, (4, 2), names)

        points = store.query(types=["point"])
        assert len(points) == 1
        point = points[0]
        rally = store.query(types=["rally_end"])[0]
        assert point.frame_start == point.frame_end == 200
        assert point.payload["winner"] == "P1"
        assert point.parent_id == rally.event_id
        assert rally.frame_start == 100 and rally.frame_end == 200
        assert rally.payload["official"] is True
        assert rally.payload["winner"] == "P1"
        assert rally.event_id != original.event_id
        assert rally.payload["phase_evidence"] == {
            **_CONTEXT.to_public(), "scoreboard": "changed",
        }
        assert store.state_at(200).state["score"] == engine.public_state()["score"]


def test_a_delayed_unchanged_board_never_creates_a_point(tmp_path, monkeypatch):
    engine, store, names = _engine(tmp_path, monkeypatch)
    with store:
        _finalize_unknown(engine, store)
        _board(engine, 500, (3, 2), names)

        assert store.query(types=["point"]) == []
        assert store.query(types=["rally_end"])[0].payload["winner"] is None


def test_two_eligible_unknown_rallies_do_not_arbitrarily_share_one_late_increment(tmp_path, monkeypatch):
    engine, store, names = _engine(tmp_path, monkeypatch)
    with store:
        _finalize_unknown(engine, store, intervals=[(100, 280)], segments=((100, 200), (240, 280)))
        _board(engine, 500, (4, 2), names)

        assert store.query(types=["point"]) == []
        rallies = store.query(types=["rally_end"])
        assert len(rallies) == 2
        assert all(rally.payload["winner"] is None for rally in rallies)


def test_reviewed_eligibility_can_resolve_which_rally_owns_a_late_increment(tmp_path, monkeypatch):
    engine, store, names = _engine(tmp_path, monkeypatch)
    with store:
        _finalize_unknown(engine, store, intervals=[(240, 280)], segments=((100, 200), (240, 280)))
        _board(engine, 500, (4, 2), names)

        points = store.query(types=["point"])
        assert len(points) == 1
        assert points[0].frame_start == 280
        assert points[0].payload["winner"] == "P1"
        earlier = next(event for event in store.query(types=["rally_end"]) if event.frame_start == 100)
        assert earlier.payload["winner"] is None


@pytest.mark.parametrize(("horizon_s", "expected_points"), [(5.0, 0), (15.0, 1)])
def test_reconciliation_horizon_bounds_actual_rally_end_to_confirmation_delay(
    tmp_path, monkeypatch, horizon_s, expected_points,
):
    engine, store, names = _engine(tmp_path, monkeypatch, horizon_s=horizon_s)
    with store:
        _finalize_unknown(engine, store, intervals=[(100, 200)])
        # Confirmation arrives 305 frames (10.17 s) after the rally end.
        _board(engine, 500, (4, 2), names)

        points = store.query(types=["point"])
        assert len(points) == expected_points
        if points:
            assert points[0].frame_start == 200
            assert points[0].payload["winner"] == "P1"


def test_late_ocr_does_not_replace_an_explicit_human_winner(tmp_path, monkeypatch):
    engine, store, names = _engine(tmp_path, monkeypatch)
    with store:
        _finalize_unknown(engine, store, intervals=[(100, 200)])
        original = store.query(types=["rally_end"])[0]
        engine.correct_rally_winner(original.event_id, "P2", Provenance(model="human"))
        reviewed = store.query(types=["rally_end"])[0]
        _board(engine, 500, (4, 2), names)

        points = store.query(types=["point"])
        assert len(points) == 1
        assert points[0].payload["winner"] == "P2"
        rally = store.query(types=["rally_end"])[0]
        assert rally.event_id == reviewed.event_id
        assert rally.status is EventStatus.HUMAN_VERIFIED
        assert rally.payload["winner"] == "P2"


def test_late_ocr_cannot_overrule_a_reviewers_not_official_decision(tmp_path, monkeypatch):
    engine, store, names = _engine(tmp_path, monkeypatch)
    with store:
        _finalize_unknown(engine, store)
        original = store.query(types=["rally_end"])[0]
        engine.set_rally_official(original.event_id, False, Provenance(model="human"))
        _board(engine, 500, (4, 2), names)

        assert store.query(types=["point"]) == []
        rally = store.query(types=["rally_end"])[0]
        assert rally.status is EventStatus.HUMAN_VERIFIED
        assert rally.payload["official"] is False
        assert rally.payload["winner"] is None


@pytest.mark.parametrize("player_names", [{}, {"P1": "1", "P2": "2"}])
def test_unbound_late_broadcast_rows_remain_visible_without_a_named_point(tmp_path, monkeypatch, player_names):
    engine, store, names = _engine(tmp_path, monkeypatch, player_names=player_names)
    with store:
        _finalize_unknown(engine, store, intervals=[(100, 200)])
        _board(engine, 500, (4, 2), names)

        assert store.query(types=["point"]) == []
        assert store.query(types=["rally_end"])[0].payload["winner"] is None
        broadcast = store.query(types=["broadcast_score"])[-1]
        assert broadcast.frame_start == 505
        assert broadcast.payload["rows"] == [{"name": "ALICE", "points": 4}, {"name": "BOB", "points": 2}]
        assert broadcast.payload["player_mapping"] is None


@pytest.mark.parametrize("boundary", ["point", "snapshot"])
def test_failed_late_decision_rolls_back_and_exact_reading_retry_awards_once(tmp_path, monkeypatch, boundary):
    delivered = []
    engine, store, names = _engine(tmp_path, monkeypatch, emit=delivered.extend)
    with store:
        _finalize_unknown(engine, store, intervals=[(100, 200)])
        engine.on_ocr(_reading(500, (4, 2), names))
        old_public = engine.public_state()
        old_rally = store.query(types=["rally_end"])[0]
        old_states = store.states()
        delivered.clear()
        append, snapshot = store.append_many, store.put_state

        def fail_point(events):
            events = list(events)
            if any(event.type == "point" for event in events):
                raise OSError("injected late point failure")
            return append(events)

        def fail_snapshot(value):
            raise OSError("injected late snapshot failure")

        monkeypatch.setattr(store, "append_many", fail_point if boundary == "point" else append)
        monkeypatch.setattr(store, "put_state", fail_snapshot if boundary == "snapshot" else snapshot)
        with pytest.raises(OSError, match="injected late"):
            engine.on_ocr(_reading(505, (4, 2), names))

        assert store.query(types=["point"]) == []
        assert store.query(types=["rally_end"]) == [old_rally]
        assert store.states() == old_states
        assert engine.public_state() == old_public
        assert [event for event in delivered if event.type in ("point", "rally_end")] == []

        monkeypatch.setattr(store, "append_many", append)
        monkeypatch.setattr(store, "put_state", snapshot)
        engine.on_ocr(_reading(505, (4, 2), names))
        engine.on_ocr(_reading(505, (4, 2), names))
        _board(engine, 550, (4, 2), names)

        points = store.query(types=["point"])
        assert len(points) == 1
        assert points[0].frame_start == 200
        assert points[0].payload["winner"] == "P1"
        assert store.state_at(200).state["score"] == engine.public_state()["score"]


def test_ingest_does_not_accept_future_ocr_before_current_rally_candidates_are_known(tmp_path, monkeypatch):
    engine, store, names = _engine(tmp_path, monkeypatch)
    with store:
        _finalize_unknown(engine, store, intervals=[(100, 400)])
        engine.ingest(ChunkPerception(0, 450, [FramePerception(i, None, 0.0) for i in range(451)]))
        observed_before_detection = []
        revealed = False

        def reveal_competing_rally(frontier):
            nonlocal revealed
            if not revealed:
                observed_before_detection.append(len(store.query(types=["point"])))
                engine._pending.append(_PendingRally(RallySegment(240, 400, None, "stationary"), [], None))
                revealed = True

        # Replace only temporal perception, retaining real ingest/OCR/score and
        # persistence. The later rally is discovered after chunk OCR is added.
        monkeypatch.setattr(engine, "_advance", reveal_competing_rally)
        engine.ingest(ChunkPerception(
            451, 505, [FramePerception(i, None, 0.0) for i in range(451, 506)],
            ocr=[_reading(500, (4, 2), names), _reading(505, (4, 2), names)],
        ))
        assert observed_before_detection == [0]
        assert store.query(types=["point"]) == []
        engine.ingest(ChunkPerception(506, 550, [FramePerception(i, None, 0.0) for i in range(506, 551)]))
        assert len(store.query(types=["rally_end"])) == 2
        assert store.query(types=["point"]) == []


def test_a_pending_competitor_prevents_premature_late_point_acceptance(tmp_path, monkeypatch):
    engine, store, names = _engine(tmp_path, monkeypatch)
    with store:
        _finalize_unknown(engine, store, intervals=[(100, 400)])
        engine._pending = [_PendingRally(RallySegment(240, 400, None, "stationary"), [], None)]
        _board(engine, 500, (4, 2), names)
        assert store.query(types=["point"]) == []


def test_an_unresolved_open_rally_overlapping_source_time_defers_the_late_decision(tmp_path, monkeypatch):
    engine, store, names = _engine(tmp_path, monkeypatch)
    with store:
        _finalize_unknown(engine, store, intervals=[(100, 600)])
        engine.fsm.on_contact(350)
        _board(engine, 500, (4, 2), names)
        assert store.query(types=["point"]) == []
