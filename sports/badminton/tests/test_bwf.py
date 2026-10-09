import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from bai_badminton.rules import (
    End,
    MatchConfig,
    MatchFinishedError,
    PlayerId,
    ServiceCourt,
    Transition,
    apply_rally,
    fold,
    initial_state,
)

CFG = MatchConfig()


def play(winners: str) -> list:  # "1122" → P1,P1,P2,P2
    return fold([("P1" if c == "1" else "P2") for c in winners], CFG)  # type: ignore[misc]


def test_simple_game_21_0() -> None:
    res = play("1" * 21)
    last = res[-1]
    assert Transition.GAME_END in last.transitions
    assert last.after.games_won == {"P1": 1, "P2": 0}
    assert last.after.completed_games == ((21, 0),)
    assert last.after.score == {"P1": 0, "P2": 0}
    assert last.after.game_no == 2
    assert last.after.server == "P1"  # game winner serves first


def test_deuce_requires_two_point_lead() -> None:
    res = play("12" * 20)  # 20-20
    s = res[-1].after
    assert s.score == {"P1": 20, "P2": 20}
    assert s.is_deuce(CFG)
    assert s.game_point_for(CFG) is None  # neither one rally from winning... at 20-20 nobody
    r = apply_rally(s, "P1", CFG)  # 21-20 → game point P1, not won
    assert Transition.GAME_END not in r.transitions
    assert r.after.game_point_for(CFG) == "P1"
    r2 = apply_rally(r.after, "P1", CFG)  # 22-20 wins
    assert Transition.GAME_END in r2.transitions
    assert r2.after.completed_games == ((22, 20),)


def test_cap_at_30() -> None:
    res = play("12" * 29)  # 29-29
    s = res[-1].after
    assert s.score == {"P1": 29, "P2": 29}
    assert s.game_point_for(CFG) in ("P1", "P2")  # both have game point; first checked wins
    r = apply_rally(s, "P2", CFG)
    assert Transition.GAME_END in r.transitions
    assert r.after.completed_games == ((29, 30),)


def test_game_point_vs_match_point() -> None:
    # 20-19 in game 1 is game point, not match point (the legacy code called it match point)
    res = play("1" * 19 + "2" * 19 + "1")
    s = res[-1].after
    assert s.score == {"P1": 20, "P2": 19}
    assert s.game_point_for(CFG) == "P1"
    assert s.match_point_for(CFG) is None
    # after winning game 1, 20-x in game 2 is match point
    s2 = play("1" * 21 + "1" * 20)[-1].after
    assert s2.match_point_for(CFG) == "P1"


def test_service_court_parity_and_server_rotation() -> None:
    s = initial_state(CFG)
    assert s.server == "P1" and s.service_court is ServiceCourt.RIGHT
    s = apply_rally(s, "P1", CFG).after  # 1-0, P1 serves from left (odd)
    assert s.server == "P1" and s.service_court is ServiceCourt.LEFT
    s = apply_rally(s, "P2", CFG).after  # 1-1, P2 serves from left (odd)
    assert s.server == "P2" and s.receiver == "P1" and s.service_court is ServiceCourt.LEFT
    s = apply_rally(s, "P2", CFG).after  # 1-2, P2 serves from right (even)
    assert s.service_court is ServiceCourt.RIGHT


def test_mid_game_interval_once() -> None:
    res = play("1" * 11)
    assert Transition.INTERVAL in res[-1].transitions
    assert res[-1].after.interval_taken
    res = play("1" * 11 + "2" * 11)  # P2 reaching 11 does not trigger a second interval
    assert all(Transition.INTERVAL not in r.transitions for r in res[11:])


def test_change_of_ends_after_games_and_in_decider_at_11() -> None:
    res = play("1" * 21 + "2" * 21)
    s = res[-1].after
    assert s.games_won == {"P1": 1, "P2": 1}
    assert s.ends == {"P1": End.NEAR, "P2": End.FAR}  # switched twice
    assert s.is_deciding_game(CFG)
    res3 = fold([*(r.winner for r in res), *(["P1"] * 11)], CFG)
    r11 = res3[-1]
    assert Transition.SIDE_SWITCH in r11.transitions and Transition.INTERVAL in r11.transitions
    assert r11.after.ends == {"P1": End.FAR, "P2": End.NEAR}
    # no further switch in the decider
    more = fold([*(r.winner for r in res3), "P2", "P2"], CFG)
    assert all(Transition.SIDE_SWITCH not in r.transitions for r in more[-2:])


def test_match_end_and_finished() -> None:
    res = play("1" * 42)
    assert Transition.MATCH_END in res[-1].transitions
    assert res[-1].after.winner == "P1"
    with pytest.raises(MatchFinishedError):
        apply_rally(res[-1].after, "P2", CFG)


def test_public_view_is_json_friendly() -> None:
    import json

    s = play("1" * 20)[-1].after
    pub = s.to_public(CFG)
    json.dumps(pub)
    assert pub["game_point"] == "P1" and pub["service_court"] == "right"


@st.composite
def match_winners(draw: st.DrawFn) -> list[PlayerId]:
    """A random rally sequence that stops exactly at match end."""
    s = initial_state(CFG)
    out: list[PlayerId] = []
    while not s.finished:
        w: PlayerId = draw(st.sampled_from(["P1", "P2"]))
        out.append(w)
        s = apply_rally(s, w, CFG).after
    return out


@settings(max_examples=300, deadline=None)
@given(match_winners())
def test_invariants(winners: list[PlayerId]) -> None:
    results = fold(winners, CFG)
    final = results[-1].after
    assert final.finished
    assert max(final.games_won.values()) == CFG.games_to_win
    assert len(final.completed_games) == sum(final.games_won.values()) <= CFG.max_games
    for a, b in final.completed_games:
        hi, lo = max(a, b), min(a, b)
        assert hi == 30 or (hi >= 21 and hi - lo >= 2)
        assert hi <= 30 and (hi == 21 or hi - lo == 2 or hi == 30)
    # every rally awards exactly one point; server = previous rally winner
    for r in results:
        if Transition.MATCH_END in r.transitions:
            continue
        assert r.after.server == r.winner
    # every rally is a point in exactly one completed game (after match end the current score
    # keeps displaying the final game, which is also the last completed game)
    total = sum(a + b for a, b in final.completed_games)
    assert total == len(winners)
    assert tuple(final.score.values()) == final.completed_games[-1]
    # each game has at most one mid-game interval
    games_intervals: dict[int, int] = {}
    for r in results:
        if Transition.INTERVAL in r.transitions and Transition.GAME_END not in r.transitions:
            games_intervals[r.before.game_no] = games_intervals.get(r.before.game_no, 0) + 1
    assert all(v == 1 for v in games_intervals.values())
