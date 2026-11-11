"""Score-row mapping evidence counts distinct corroborated source increments, not retries."""

from copy import deepcopy

from bai_badminton.perception_types import ScoreReading
from bai_badminton.score_ocr import ScoreReconciler


def readings(rec, frame, points, names=("ALPHA", "BETA")):
    for offset in (0, 10):
        rec.add(ScoreReading(frame + offset, ((names[0], points[0]), (names[1], points[1])), conf=0.99))


def first_point():
    rec = ScoreReconciler()
    readings(rec, 0, (10, 10))
    readings(rec, 90, (11, 10))
    return rec


def vote(rec, start=40, end=80, until=100, winner="P1"):
    return rec.winner_from_ocr({"P1": 0, "P2": 0}, start, end, until, winner, lookback=600)


def test_repeated_single_source_increment_cannot_establish_row_map():
    rec = first_point()
    ref = rec.source_transition(40, 80, 100, 600)
    assert ref is not None
    for _ in range(8):
        assert vote(rec) == ("P1", "ocr_unmapped")
    assert rec.row_map is None
    assert rec._votes == {(0, "P1"): 1}


def test_three_independent_source_points_still_bind_the_mapping():
    rec = first_point()
    assert vote(rec) == ("P1", "ocr_unmapped")
    readings(rec, 190, (12, 10))
    assert vote(rec, 140, 180, 200) == ("P1", "ocr_unmapped")
    readings(rec, 290, (13, 10))
    assert vote(rec, 240, 280, 300) == ("P1", "ocr")
    assert rec.row_map == {0: "P1", 1: "P2"}


def test_same_source_point_with_changed_geometry_does_not_cast_another_vote():
    rec = first_point()
    vote(rec)
    for _ in range(8):
        vote(rec, winner="P2")
    assert rec.row_map is None
    assert sum(rec._votes.values()) == 1


def test_later_identical_scoreboard_confirmations_do_not_create_new_mapping_evidence():
    rec = first_point()
    vote(rec)
    before = rec.source_transition(40, 80, 100, 600)
    readings(rec, 120, (11, 10))
    after = rec.source_transition(40, 80, 130, 600)
    assert before.transition_id == after.transition_id
    for _ in range(4):
        vote(rec, until=130)
    assert rec.row_map is None and sum(rec._votes.values()) == 1


def test_score_claim_refold_does_not_reset_source_mapping_vote_deduplication():
    rec = first_point()
    vote(rec)
    rec.clear_transition_claims()
    for _ in range(4):
        vote(rec)
    assert rec.row_map is None and sum(rec._votes.values()) == 1


def test_competitor_label_epoch_clears_mapping_votes_and_their_provenance():
    rec = first_point()
    vote(rec)
    readings(rec, 150, (11, 10), ("GAMMA", "DELTA"))
    assert rec.row_map is None and rec._votes == {} and rec._mapping_vote_transitions == set()
    readings(rec, 190, (12, 10), ("GAMMA", "DELTA"))
    vote(rec, 160, 180, 200)
    assert len(rec._mapping_vote_transitions) == 1 and sum(rec._votes.values()) == 1


def test_mapping_vote_deduplication_is_independent_after_checkpoint_copy():
    rec = first_point()
    saved = deepcopy(rec)
    vote(rec)
    assert saved._mapping_vote_transitions == set()
    assert saved._votes == {}
    assert vote(saved) == ("P1", "ocr_unmapped")
    assert sum(saved._votes.values()) == 1
