"""One source score transition can support at most one accepted rally decision.

The engine fixtures bypass perception quality but retain the real OCR query,
phase, scoring rules, point publication, transaction and durable store.
"""

from dataclasses import FrozenInstanceError

import pytest

from bai_badminton import score_ocr
from bai_badminton.engine import BadmintonMatchEngine, EngineConfig, _PendingRally
from bai_badminton.events.match_phase import RallyEvidence
from bai_badminton.events.rally_fsm import RallySegment
from bai_badminton.perception_types import ScoreReading
from bai_badminton.score_ocr import ScoreReconciler
from bai_engine.schema import Provenance
from bai_engine.store import EventStore


def _board(score, frame, points, names=("ALICE", "BOB")):
    for offset in (0, 5):
        score.add(ScoreReading(frame + offset, ((names[0], points[0]), (names[1], points[1])), conf=0.95))


def _score(player_names=None):
    score = ScoreReconciler(player_names=player_names or {"P1": "Alice", "P2": "Bob"})
    _board(score, 0, (3, 2))
    _board(score, 205, (3, 2))
    _board(score, 300, (4, 2))
    return score


def _transition(score, start=100, end=200, until=320):
    query = getattr(score, "source_transition", None)
    assert callable(query), "score evidence needs a stable source-transition reference"
    return query(start, end, until, 900)


def _claim(score, ref, owner):
    claim = getattr(score, "claim_transition", None)
    assert callable(claim), "accepted scoring needs an explicit transition claim"
    return claim(ref, owner)


def _clear(score):
    clear = getattr(score, "clear_transition_claims", None)
    assert callable(clear), "refold and restore need an explicit transition-claim reset"
    clear()


def _restore_ref(value):
    ref_type = getattr(score_ocr, "ScoreTransitionRef", None)
    assert ref_type is not None, "durable score associations need a typed immutable reference"
    return ref_type.from_public(value)


def test_query_local_baselines_resolve_the_same_global_observation_transition():
    score = _score()
    _board(score, 340, (4, 2))

    first = _transition(score)
    later = _transition(score, 240, 330, 400)

    assert first is not None and later is not None
    assert first == later
    assert first.version == 1
    assert first.before_frames == (0, 5)
    assert first.after_frames == (300, 305)
    assert first.before_rows == (("ALICE", 3), ("BOB", 2))
    assert first.after_rows == (("ALICE", 4), ("BOB", 2))


def test_row_reorder_and_duplicate_delivery_do_not_create_another_transition():
    score = _score()
    original = _transition(score)
    score.add(ScoreReading(305, (("ALICE", 4), ("BOB", 2)), conf=0.95))
    _board(score, 340, (2, 4), names=("BOB", "ALICE"))

    reordered = _transition(score, 240, 330, 400)

    assert original is not None and reordered is not None
    assert original == reordered
    assert reordered.after_frames == (300, 305)


def test_different_observed_increments_have_different_transition_references():
    score = _score()
    _board(score, 500, (4, 3))

    first = _transition(score)
    second = _transition(score, 400, 450, 550)

    assert first is not None and second is not None
    assert first.transition_id != second.transition_id
    assert second.before_frames == (300, 305)
    assert second.after_frames == (500, 505)


def test_claim_is_idempotent_for_its_owner_and_rejects_a_different_owner():
    score = _score()
    ref = _transition(score)

    assert ref is not None
    assert _claim(score, ref, "rally:100:200")
    assert _claim(score, ref, "rally:100:200")
    assert not _claim(score, ref, "rally:240:280")
    assert _transition(score) == ref


def test_nonofficial_eligibility_queries_do_not_claim_source_evidence():
    score = _score()

    for _ in range(3):
        assert score.winner_from_ocr({"P1": 3, "P2": 2}, 100, 200, 320, None, 900) == ("P1", "ocr")
        ref = _transition(score)

    assert ref is not None
    assert _claim(score, ref, "actual-official-rally")


def test_claims_can_be_cleared_and_rebuilt_from_durable_validated_references():
    score = _score()
    ref = _transition(score)
    assert ref is not None and _claim(score, ref, "old-rally")
    durable = ref.to_public()

    _clear(score)
    restored = _restore_ref(durable)
    assert restored == ref
    assert _claim(score, restored, "replacement-rally")
    _clear(score)
    assert _claim(score, _restore_ref(durable), "old-rally")
    assert not _claim(score, ref, "replacement-rally")


def test_durable_claims_restore_without_reloading_perception_readings():
    ref = _transition(_score())
    assert ref is not None
    restored = ScoreReconciler()
    restored_ref = _restore_ref(ref.to_public())

    assert restored_ref == ref
    assert _claim(restored, restored_ref, "durable-rally")
    assert not _claim(restored, ref, "another-rally")
    assert _transition(restored) is None


def test_source_reference_is_immutable_and_public_payload_does_not_alias_it():
    ref = _transition(_score())
    assert ref is not None
    with pytest.raises((FrozenInstanceError, AttributeError)):
        ref.after_frames = (400, 405)

    public = ref.to_public()
    public["after_rows"][0][1] = 30
    assert ref.after_rows == (("ALICE", 4), ("BOB", 2))
    assert _restore_ref(ref.to_public()) == ref


@pytest.mark.parametrize(("field", "value"), [
    ("version", 2),
    ("transition_id", "unrelated-transition"),
    ("before_frames", [5, 0]),
    ("after_frames", [True, 305]),
    ("after_frames", [3, 4]),
    ("before_rows", [["ALICE", 3], ["ALICE", 2]]),
    ("after_rows", [["ALICE", True], ["BOB", 2]]),
    ("after_rows", [["ALICE", 31], ["BOB", 2]]),
])
def test_restoring_a_malformed_or_tampered_transition_fails_closed(field, value):
    ref = _transition(_score())
    assert ref is not None
    public = ref.to_public()
    public[field] = value

    assert _restore_ref(public) is None


@pytest.mark.parametrize("player_names", [{}, {"P1": "1", "P2": "2"}])
def test_unbound_competitors_have_source_evidence_without_a_named_winner(player_names):
    score = ScoreReconciler(player_names=player_names)
    _board(score, 0, (3, 2))
    _board(score, 300, (4, 2))

    ref = _transition(score)

    assert ref is not None
    assert score.winner_from_ocr({"P1": 0, "P2": 0}, 100, 200, 320, None, 900)[0] is None
    assert score.row_map is None


def test_a_stable_multi_point_jump_is_not_one_source_transition_for_one_rally():
    score = ScoreReconciler(player_names={"P1": "Alice", "P2": "Bob"})
    _board(score, 0, (3, 2))
    _board(score, 300, (8, 2))

    assert _transition(score) is None


def test_uncorroborated_noise_does_not_split_a_globally_confirmed_board_run():
    score = ScoreReconciler(player_names={"P1": "Alice", "P2": "Bob"})
    _board(score, 0, (3, 2))
    score.add(ScoreReading(150, (("ALICE", 9), ("BOB", 8)), conf=0.95))
    _board(score, 205, (3, 2))
    _board(score, 300, (4, 2))

    ref = _transition(score)

    assert ref is not None
    assert ref.before_frames == (0, 5)
    assert ref.after_frames == (300, 305)
    assert ref == _transition(_score())


def test_a_game_point_lead_followed_by_a_reset_does_not_name_a_winner():
    score = ScoreReconciler(player_names={"P1": "Alice", "P2": "Bob"})
    _board(score, 0, (20, 18))
    _board(score, 300, (0, 0))

    assert score.winner_from_ocr({"P1": 20, "P2": 18}, 100, 200, 320, None, 900)[0] is None
    assert _transition(score) is None


def test_an_observed_final_increment_remains_evidence_after_the_new_game_reset():
    score = ScoreReconciler(player_names={"P1": "Alice", "P2": "Bob"})
    _board(score, 0, (20, 18))
    _board(score, 250, (21, 18))
    _board(score, 300, (0, 0))

    assert score.winner_from_ocr({"P1": 20, "P2": 18}, 100, 200, 320, None, 900) == ("P1", "ocr")
    ref = _transition(score)
    assert ref is not None
    assert ref.before_rows == (("ALICE", 20), ("BOB", 18))
    assert ref.after_rows == (("ALICE", 21), ("BOB", 18))
    assert ref.after_frames == (250, 255)


def _engine(tmp_path, monkeypatch):
    store = EventStore(tmp_path / "transition.sqlite", "S1")
    engine = BadmintonMatchEngine(
        "S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store,
        player_names={"P1": "Alice", "P2": "Bob"},
    )
    monkeypatch.setattr(engine, "_outcome", lambda seg: ("unknown", "unknown", "terminal_not_observed", 0.2))
    monkeypatch.setattr(engine, "_phase_evidence", lambda seg, until: RallyEvidence(
        calibrated=False, scoreboard=engine.ocr.board_change(seg.start, seg.end, until, 900),
    ))
    for frame, points in ((0, (3, 2)), (205, (3, 2)), (300, (4, 2))):
        for offset in (0, 5):
            engine.on_ocr(ScoreReading(frame + offset, (("ALICE", points[0]), ("BOB", points[1])), conf=0.95))
    engine._pending = [
        _PendingRally(RallySegment(100, 200, None, "stationary"), [], None),
        _PendingRally(RallySegment(240, 280, None, "stationary"), [], None),
    ]
    return engine, store


def test_two_distinct_rallies_cannot_publish_two_points_from_one_broadcast_increment(tmp_path, monkeypatch):
    engine, store = _engine(tmp_path, monkeypatch)
    with store:
        engine._finalize_pending(400)

        assert len(store.query(types=["rally_end"])) == 2
        assert len(store.query(types=["point"])) <= 1


def test_an_unofficial_candidate_cannot_take_the_later_official_rallys_transition(tmp_path, monkeypatch):
    engine, store = _engine(tmp_path, monkeypatch)
    with store:
        engine.set_reviewed_match_intervals([(240, 280)], Provenance(model="human"))
        engine._finalize_pending(400)

        points = store.query(types=["point"])
        assert len(points) == 1
        assert points[0].frame_start == 280
