"""Contact detection and player attribution are distinct pieces of evidence."""
import numpy as np
import pytest

from bai_badminton.events.contact import score_frame
from bai_badminton.observations import PlayerSeries, WindowObs
from bai_badminton.perception.shuttle_post import Track


def contact_window(players: list[tuple[str, float]]) -> WindowObs:
    # A 90-degree turn at (100, 100), with measured shuttle samples either side.
    track = Track.from_arrays(
        np.array([40, 60, 80, 100, 100, 100, 100], dtype=float),
        np.array([100, 100, 100, 100, 120, 140, 160], dtype=float),
        np.ones(7, dtype=bool),
    )
    out = {}
    for pid, horizontal_offset in players:
        series = PlayerSeries.empty(7)
        # Upper-bbox proxy is (100 + horizontal_offset, 100); height is 100px.
        series.bbox[:] = [90 + horizontal_offset, 85, 110 + horizontal_offset, 185]
        out[pid] = series
    return WindowObs(frame0=0, fps=30.0, shuttle=track, players=out)


@pytest.mark.parametrize("offset", [0.0, 2.0])
def test_equal_or_near_equal_player_proximity_is_unattributed(offset: float) -> None:
    candidate = score_frame(contact_window([("P1", 0.0), ("P2", offset)]), 3)
    baseline = score_frame(contact_window([("P1", 0.0)]), 3)
    assert candidate is not None and baseline is not None
    assert candidate.player_id is None
    assert candidate.attribution_reason == "ambiguous_proximity"
    assert candidate.scores["proximity_gap"] <= 0.05
    # Ambiguous player identity does not remove the physical-contact hypothesis.
    assert candidate.p == pytest.approx(baseline.p)


def test_clear_proximity_difference_keeps_nearest_player() -> None:
    candidate = score_frame(contact_window([("P1", 0.0), ("P2", 100.0)]), 3)
    assert candidate is not None and candidate.player_id == "P1"
    assert candidate.attribution_reason == "nearest_proximity"
    assert candidate.scores["proximity_gap"] > 0.05


def test_no_observed_player_has_explicit_reason() -> None:
    candidate = score_frame(contact_window([]), 3)
    assert candidate is not None and candidate.player_id is None
    assert candidate.attribution_reason == "no_player_observation"


def test_tie_is_unresolved_independently_of_input_order() -> None:
    a = score_frame(contact_window([("P1", 0.0), ("P2", 0.0)]), 3)
    b = score_frame(contact_window([("P2", 0.0), ("P1", 0.0)]), 3)
    assert a is not None and b is not None
    assert a.player_id is None and b.player_id is None
    assert a.p == pytest.approx(b.p)


def test_small_absolute_scores_are_compared_on_relative_scale() -> None:
    # Both players are far away; their tiny absolute score difference alone
    # should not make a roughly 2.5x distance-proximity advantage into a tie.
    candidate = score_frame(contact_window([("P1", 125.0), ("P2", 168.0)]), 3)
    assert candidate is not None
    assert candidate.scores["proximity_gap"] < 0.05
    assert candidate.scores["proximity_relative_gap"] > 0.05
    assert candidate.player_id == "P1"


def test_two_nearby_wrists_of_one_player_are_not_competing_people() -> None:
    from bai_badminton.perception.keypoints import KP

    window = contact_window([("P1", 0.0)])
    pose = window.players["P1"].kps
    pose[:, 0] = [0, 0, 1]
    pose[:, KP.L_WRIST] = [100, 100, 1]
    pose[:, KP.R_WRIST] = [101, 100, 1]
    candidate = score_frame(window, 3)
    assert candidate is not None and candidate.player_id == "P1"
    assert candidate.scores["proximity_candidates"] == 1
    assert candidate.attribution_reason == "nearest_proximity"


def test_contact_redirect_without_nearby_player_leaves_hitter_unresolved() -> None:
    from bai_badminton.events.contact import detect_contacts

    window = contact_window([("P1", 1000.0), ("P2", 2000.0)])
    window.shuttle.y[4:] = [160.0, 220.0, 280.0]
    contacts = detect_contacts(window)
    assert contacts
    contact = contacts[0]
    assert contact.player_id is None
    assert contact.attribution_reason == "insufficient_proximity"
    assert contact.p > 0.35


def test_tied_players_with_different_wrist_motion_do_not_change_score_by_order() -> None:
    from bai_badminton.perception.keypoints import KP

    a = contact_window([("P1", 0.0), ("P2", 0.0)])
    b = contact_window([("P2", 0.0), ("P1", 0.0)])
    for window in (a, b):
        points = window.players["P1"].kps
        points[:, 0, 0] = 0
        points[:, KP.L_WRIST] = [100.0, 100.0, 1.0]
        points[2, KP.L_WRIST] = [70.0, 100.0, 1.0]
    first, second = score_frame(a, 3), score_frame(b, 3)
    assert first is not None and second is not None
    assert first.player_id is None and second.player_id is None
    assert first.p == pytest.approx(second.p)


def test_distant_player_swing_is_not_contact_evidence() -> None:
    from bai_badminton.perception.keypoints import KP

    window = contact_window([("P1", 1000.0)])
    points = window.players["P1"].kps
    points[:, 0, 0] = 0
    points[:, KP.L_WRIST] = [1100.0, 100.0, 1.0]
    points[2, KP.L_WRIST] = [1070.0, 100.0, 1.0]
    candidate = score_frame(window, 3)
    assert candidate is not None and candidate.player_id is None
    assert candidate.attribution_reason == "insufficient_proximity"
    assert candidate.scores["swing"] == 0.0
