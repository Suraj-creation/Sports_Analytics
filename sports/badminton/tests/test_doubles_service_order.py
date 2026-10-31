import pytest

from bai_badminton.rules.doubles import DoublesServiceOrder

TEAMS = {"P1": ("A", "B"), "P2": ("C", "D")}


def test_serving_pair_swaps_only_when_it_wins_and_opponents_keep_their_courts():
    state = DoublesServiceOrder.seed(TEAMS, "A", "C", {"P1": 0, "P2": 0})
    assert (state.server, state.receiver, state.court) == ("A", "C", "right")
    state = state.point("P1")
    assert (state.server, state.receiver, state.court) == ("A", "D", "left")
    state = state.point("P2")
    assert (state.server, state.receiver, state.court) == ("D", "A", "left")
    state = state.point("P2")
    assert (state.server, state.receiver, state.court) == ("D", "B", "right")
    state = state.point("P1")
    assert (state.server, state.receiver, state.court) == ("B", "D", "right")


def test_midgame_seed_preserves_named_server_and_receiving_court():
    state = DoublesServiceOrder.seed(TEAMS, "B", "D", {"P1": 13, "P2": 10})
    assert state.court == "left"
    assert state.point("P2").server == "D"


@pytest.mark.parametrize(
    "teams,server,receiver,score",
    [
        ({"P1": ("A", "A"), "P2": ("C", "D")}, "A", "C", {"P1": 0, "P2": 0}),
        (TEAMS, "A", "B", {"P1": 0, "P2": 0}),
        (TEAMS, "missing", "C", {"P1": 0, "P2": 0}),
        (TEAMS, "A", "C", {"P1": True, "P2": 0}),
    ],
)
def test_invalid_membership_or_score_cannot_seed_order(teams, server, receiver, score):
    with pytest.raises(ValueError):
        DoublesServiceOrder.seed(teams, server, receiver, score)
