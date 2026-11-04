"""Name evidence and one observed score change cannot manufacture named points.

The fixtures exercise real score observations and reconciliation. They do not
establish OCR or match-winner accuracy on footage.
"""

import pytest

from bai_badminton.perception_types import ScoreReading
from bai_badminton.score_ocr import ScoreReconciler


def _board(score, frame, points, names):
    for offset in (0, 5):
        score.add(ScoreReading(
            frame_idx=frame + offset,
            rows=((names[0], points[0]), (names[1], points[1])),
            conf=0.95,
        ))


@pytest.mark.parametrize(
    ("player_names", "broadcast_names"),
    [
        ({"P1": "Tai Tzu Ying", "P2": "Carolina Marin"}, ("TAI T.Y.", "MARIN")),
        ({"P1": "Lee Zii Jia", "P2": "Viktor Axelsen"}, ("LEE Z.J.", "AXELSEN")),
        ({"P1": "Viktor Axelsen", "P2": "Lee Zii Jia"}, ("AXELSEN V.", "LEE Z.J.")),
        ({"P1": "Lea Müller", "P2": "Chloé García"}, ("MULLER L.", "GARCIA C.")),
        ({"P1": "Zii Jia Lee", "P2": "Axelsen Viktor"}, ("LEE ZII JIA", "VIKTOR AXELSEN")),
        ({"P1": "Lee Zii-Jia", "P2": "Viktor Axelsen"}, ("LEE Z.J.", "AXELSEN")),
    ],
)
def test_unique_surname_and_initials_bind_a_broadcast_row_to_the_supplied_player(player_names, broadcast_names):
    score = ScoreReconciler(player_names=player_names)
    _board(score, 0, (3, 2), broadcast_names)
    _board(score, 250, (3, 3), broadcast_names)

    assert score.winner_from_ocr({"P1": 3, "P2": 2}, 100, 200, 300, None, 900) == ("P2", "ocr")
    assert score.readings[-1].rows == ((broadcast_names[0], 3), (broadcast_names[1], 3))


def test_full_names_remain_a_supported_mapping_control():
    score = ScoreReconciler(player_names={"P1": "Tai Tzu Ying", "P2": "Carolina Marin"})
    names = ("TAI TZU YING", "CAROLINA MARIN")
    _board(score, 0, (3, 2), names)
    _board(score, 250, (4, 2), names)

    assert score.winner_from_ocr({"P1": 3, "P2": 2}, 100, 200, 300, None, 900) == ("P1", "ocr")


@pytest.mark.parametrize(
    ("player_names", "broadcast_names"),
    [
        ({"P1": "Li", "P2": "Zhang"}, ("CAROLINA", "ZHANG")),
        ({"P1": "Tai Tzu Ying", "P2": "Carolina Marin"}, ("TAI C.Y.", "MARIN")),
        ({"P1": "Lee Zii Jia", "P2": "Lee Chong Wei"}, ("LEE", "LEE J.")),
        ({"P1": "Alex Reed", "P2": "Morgan Reed"}, ("REED", "REED M.")),
    ],
)
def test_substrings_incompatible_initials_and_ambiguous_surnames_do_not_name_a_winner(player_names, broadcast_names):
    score = ScoreReconciler(player_names=player_names)
    _board(score, 0, (3, 2), broadcast_names)
    _board(score, 250, (3, 3), broadcast_names)

    assert score.winner_from_ocr({"P1": 3, "P2": 2}, 100, 200, 300, None, 900)[0] is None
    assert score.row_map is None


@pytest.mark.parametrize("names", [
    ("REED A. / CHEN M.", "SINGH R. / PARK T."),
    ("CHEN M. / REED A.", "PARK T. / SINGH R."),
    ("REED A. CHEN M.", "SINGH R. PARK T."),
])
def test_doubles_team_label_can_bind_both_abbreviated_partners_without_individual_hitter_evidence(names):
    score = ScoreReconciler(player_names={
        "P1": "Alex Reed / Morgan Chen",
        "P2": "Robin Singh / Taylor Park",
    })
    _board(score, 0, (3, 2), names)
    _board(score, 250, (3, 3), names)

    assert score.winner_from_ocr({"P1": 3, "P2": 2}, 100, 200, 300, None, 900) == ("P2", "ocr")


def test_partial_doubles_team_name_cannot_bind_the_wrong_partner_pair():
    score = ScoreReconciler(player_names={
        "P1": "Alex Reed / Morgan Chen",
        "P2": "Alex Reed / Taylor Park",
    })
    names = ("REED A.", "PARK T.")
    _board(score, 0, (3, 2), names)
    _board(score, 250, (4, 2), names)

    assert score.winner_from_ocr({"P1": 3, "P2": 2}, 100, 200, 300, None, 900)[0] is None
    assert score.row_map is None


def test_numeric_score_slot_names_do_not_bind_named_broadcast_competitors():
    score = ScoreReconciler(player_names={"P1": "1", "P2": "2"})
    names = ("KJAERSFELDT", "PUSARLA")
    _board(score, 0, (5, 3), names)
    _board(score, 250, (5, 4), names)

    assert score.winner_from_ocr({"P1": 0, "P2": 0}, 100, 200, 300, None, 900)[0] is None
    assert score.row_map is None
    assert score.stable_after(200, 300) == (5, 4)


@pytest.mark.parametrize(
    ("player_names", "broadcast_names"),
    [
        ({"P1": "Alice", "P2": "Bob"}, ("ALICE", "BOB")),
        ({"P1": "Team North", "P2": "Team South"}, ("TEAM NORTH", "TEAM SOUTH")),
    ],
)
def test_one_stable_score_increment_cannot_be_claimed_by_two_accepted_rallies(player_names, broadcast_names):
    score = ScoreReconciler(player_names=player_names)
    _board(score, 0, (3, 2), broadcast_names)
    _board(score, 205, (3, 2), broadcast_names)
    _board(score, 300, (4, 2), broadcast_names)

    first = score.winner_from_ocr({"P1": 3, "P2": 2}, 100, 200, 320, None, 900)
    second = score.winner_from_ocr({"P1": 4, "P2": 2}, 240, 280, 400, None, 900)

    # Eligibility queries are repeatable evidence lookups. Counting a point is
    # a separate accepted-engine operation, which must claim that evidence once.
    assert first == second == ("P1", "ocr")
    transition = getattr(score, "source_transition", None)
    claim = getattr(score, "claim_transition", None)
    assert callable(transition), "score evidence needs a stable source-transition reference"
    assert callable(claim), "accepted scoring needs an explicit transition claim"
    first_ref = transition(100, 200, 320, 900)
    second_ref = transition(240, 280, 400, 900)
    assert first_ref is not None and second_ref is not None
    assert first_ref.transition_id == second_ref.transition_id
    assert claim(first_ref, "rally:100:200")
    assert not claim(second_ref, "rally:240:280")


def test_two_different_stable_score_increments_can_supply_two_rally_winners():
    score = ScoreReconciler(player_names={"P1": "Alice", "P2": "Bob"})
    names = ("ALICE", "BOB")
    _board(score, 0, (3, 2), names)
    _board(score, 250, (4, 2), names)
    _board(score, 600, (4, 3), names)

    assert score.winner_from_ocr({"P1": 3, "P2": 2}, 100, 200, 320, None, 900) == ("P1", "ocr")
    assert score.winner_from_ocr({"P1": 4, "P2": 2}, 400, 500, 650, None, 900) == ("P2", "ocr")
