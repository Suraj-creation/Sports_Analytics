import numpy as np

from bai_badminton.identity import IdentityResolver
from bai_badminton.perception_types import PersonObs

ENDS = {"P1": "near", "P2": "far"}


def person(track_id: int, side: str, conf: float = 0.8) -> PersonObs:
    y = 600.0 if side == "near" else 300.0
    return PersonObs(track_id=track_id, bbox=np.array([10.0, y - 100, 50.0, y]), conf=conf)


def test_new_track_cannot_inherit_a_bound_participant_by_side() -> None:
    resolver = IdentityResolver(frame_height=720)
    resolver.assign([person(1, "near"), person(2, "far")], ENDS)
    result = resolver.assign([person(3, "near"), person(2, "far")], ENDS)
    assert "P1" not in result
    assert result["P2"].track_id == 2
    assert resolver.unresolved_tracks == {3: "near"}


def test_known_track_survives_brief_disappearance() -> None:
    resolver = IdentityResolver(frame_height=720)
    resolver.assign([person(1, "near"), person(2, "far")], ENDS)
    resolver.assign([person(2, "far")], ENDS)
    assert resolver.assign([person(1, "near"), person(2, "far")], ENDS)["P1"].track_id == 1
    assert resolver.unresolved_tracks == {}


def test_side_switch_preserves_track_identity() -> None:
    resolver = IdentityResolver(frame_height=720)
    resolver.assign([person(1, "near"), person(2, "far")], ENDS)
    result = resolver.assign([person(1, "far"), person(2, "near")], ENDS)
    assert {pid: p.track_id for pid, p in result.items()} == {"P1": 1, "P2": 2}


def test_unrecognised_higher_confidence_track_does_not_hide_bound_track() -> None:
    resolver = IdentityResolver(frame_height=720)
    resolver.assign([person(1, "near"), person(2, "far")], ENDS)
    result = resolver.assign([person(1, "near", 0.5), person(3, "near", 0.99), person(2, "far")], ENDS)
    assert result["P1"].track_id == 1
    assert resolver.unresolved_tracks == {3: "near"}


def test_duplicate_track_id_is_unresolved_instead_of_assigned_twice() -> None:
    resolver = IdentityResolver(frame_height=720)
    result = resolver.assign([person(1, "near"), person(1, "far")], ENDS)
    assert result == {}
    assert resolver.unresolved_tracks == {1: "ambiguous"}
    assert resolver._track_to_player == {}


def test_unbound_participant_not_inferred_on_side_with_known_opponent() -> None:
    resolver = IdentityResolver(frame_height=720)
    resolver.assign([person(1, "near")], ENDS)
    result = resolver.assign([person(1, "far"), person(3, "far")], ENDS)
    assert {pid: p.track_id for pid, p in result.items()} == {"P1": 1}
    assert resolver.unresolved_tracks == {3: "far"}


def test_initial_multiple_people_on_one_side_remain_unresolved() -> None:
    resolver = IdentityResolver(frame_height=720)
    result = resolver.assign([person(1, "near"), person(3, "near", 0.99)], ENDS)
    assert result == {}
    assert resolver.unresolved_tracks == {1: "near", 3: "near"}


def moved(track_id: int, side: str, dx: float) -> PersonObs:
    p = person(track_id, side)
    p.bbox = p.bbox + np.array([dx, 0.0, dx, 0.0])
    return p


def test_replacement_track_inherits_participant_on_unique_spatial_overlap() -> None:
    resolver = IdentityResolver(frame_height=720, rebind_gap_frames=60)
    resolver.assign([person(1, "near"), person(2, "far")], ENDS, 0)
    result = resolver.assign([person(3, "near"), person(2, "far")], ENDS, 8)
    assert result["P1"].track_id == 3 and result["P1"].identity_method == "spatial_rebind_v1"
    assert resolver.rebound_tracks == {3: 1} and resolver.unresolved_tracks == {}
    # The estimate persists, and the dead track cannot reclaim the participant.
    assert resolver.assign([person(3, "near"), person(2, "far")], ENDS, 9)["P1"].identity_method == "spatial_rebind_v1"


def test_replacement_without_spatial_evidence_or_beyond_gap_stays_unresolved() -> None:
    far_away = IdentityResolver(frame_height=720, rebind_gap_frames=60)
    far_away.assign([person(1, "near"), person(2, "far")], ENDS, 0)
    assert "P1" not in far_away.assign([moved(3, "near", 400.0), person(2, "far")], ENDS, 8)
    late = IdentityResolver(frame_height=720, rebind_gap_frames=60)
    late.assign([person(1, "near"), person(2, "far")], ENDS, 0)
    assert "P1" not in late.assign([person(3, "near"), person(2, "far")], ENDS, 61)
    assert late.unresolved_tracks == {3: "near"}


def test_two_overlapping_candidates_are_not_guessed_between() -> None:
    resolver = IdentityResolver(frame_height=720, rebind_gap_frames=60)
    resolver.assign([person(1, "near"), person(2, "far")], ENDS, 0)
    result = resolver.assign([person(3, "near"), moved(4, "near", 5.0), person(2, "far")], ENDS, 8)
    assert "P1" not in result and resolver.rebound_tracks == {}
