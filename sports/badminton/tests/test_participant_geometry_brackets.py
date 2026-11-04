"""Opt-in geometry estimates retain their original detector-frame provenance.

These controlled observations test a context provider, not contact/identity
accuracy. No engine integration, detector weights or media are exercised.
"""

from __future__ import annotations

import copy
import importlib.util
from dataclasses import dataclass, replace

import numpy as np
import pytest

from bai_badminton.observations import WindowObs
from bai_badminton.participant_contact import ParticipantSnapshot
from bai_badminton.perception.shuttle_post import Track
from bai_badminton.perception_types import RacketObservation


@dataclass
class _Case:
    window: WindowObs
    frames: list[dict[str, ParticipantSnapshot]]
    geometry_valid: np.ndarray
    identity_unresolved: np.ndarray
    visible_counts: np.ndarray
    match_format: str
    index: int = 3


def _api():
    spec = importlib.util.find_spec("bai_badminton.participant_geometry")
    assert spec is not None, "the opt-in participant geometry context provider is not implemented"
    from bai_badminton import participant_geometry

    return participant_geometry


def _case(match_format="singles"):
    count = 4 if match_format == "doubles" else 2
    track = Track.from_arrays(
        np.array([80, 90, 100, 110, 100, 90, 80], float),
        np.full(7, 100.0),
        np.ones(7, bool),
    )
    frames = []
    for index in range(7):
        fresh = index % 2 == 0
        source = index if fresh else index - 1
        people = {}
        for person in range(1, count + 1):
            if person == 1:
                box = [70 + 10 * source, 85, 90 + 10 * source, 185]
                court = (0.1 * source - 0.2, -3.0)
            else:
                box = [100 + 250 * (person - 1), 85, 120 + 250 * (person - 1), 185]
                near_partner = match_format == "doubles" and person == 2
                court = (1.0 if person % 2 == 0 else -1.0, -3.0 if near_partner else 3.0)
            people[f"participant-test-{person:06d}"] = ParticipantSnapshot(
                track_id=person,
                bbox=np.asarray(box, dtype=float),
                kps=None,
                court_xy=court,
                observation_id=f"birth-{person}",
                detector_observed=fresh,
                detector_matched=fresh,
            )
        frames.append(people)
    return _Case(
        WindowObs(100, 30.0, track, {}),
        frames,
        np.ones(7, bool),
        np.zeros(7, bool),
        np.full(7, count, dtype=np.int64),
        match_format,
    )


def _evaluate(case, **overrides):
    api = _api()
    options = {
        "match_format": case.match_format,
        "geometry_valid": case.geometry_valid,
        "identity_unresolved": case.identity_unresolved,
        "visible_counts": case.visible_counts,
        "policy": api.GeometryBracketPolicy(),
    }
    options.update(overrides)
    return api.estimate_participant_geometry(case.window, case.frames, case.index, **options)


def _unresolved(result):
    assert result.status == "unresolved"
    assert result.estimate is None
    assert result.player_id is None
    assert isinstance(result.reason, str) and result.reason


def _change(case, frame, person=1, **fields):
    key = f"participant-test-{person:06d}"
    case.frames[frame][key] = replace(case.frames[frame][key], **fields)


@pytest.mark.parametrize("match_format,count", [("singles", 2), ("doubles", 4)])
def test_midpoint_geometry_has_absolute_observed_sources_and_no_named_actor(match_format, count):
    result = _evaluate(_case(match_format))
    assert result.status == "estimated"
    assert result.frame == 103
    assert result.player_id is None
    assert result.method == "same_episode_detector_bracket_v1"
    assert result.version == "1"
    assert result.reason
    assert len(result.candidates) == count
    assert result.support["proximity"] == pytest.approx(1.0)
    assert result.support_semantics == "uncalibrated_body_proximity"
    estimate = result.estimate
    assert estimate.participant_id == "participant-test-000001"
    assert estimate.track_id == 1
    assert estimate.observation_id == "birth-1"
    assert estimate.source_frames == (102, 104)
    assert estimate.position_kind == "estimated"
    np.testing.assert_allclose(estimate.bbox_estimate, [100, 85, 120, 185])
    np.testing.assert_allclose(estimate.court_xy_estimate, [0.1, -3.0])
    assert estimate.contact_above_head is None
    assert getattr(estimate, "kps", None) is None
    assert getattr(estimate, "racket", None) is None


def test_estimation_does_not_rewrite_current_flags_or_invent_pose_racket_shuttle_observations():
    case = _case()
    for index in (2, 4):
        keypoints = np.zeros((17, 3), dtype=float)
        keypoints[9] = [100 + 10 * index, 100, 0.9]
        _change(
            case,
            index,
            kps=keypoints,
            racket=RacketObservation((100 + 10 * index, 100), (20, 30), 0, 0.9, 9),
        )
    before = copy.deepcopy(case)
    result = _evaluate(case)
    assert result.status == "estimated"
    for index, people in enumerate(case.frames):
        assert people.keys() == before.frames[index].keys()
        for key, person in people.items():
            prior = before.frames[index][key]
            np.testing.assert_equal(person.bbox, prior.bbox)
            np.testing.assert_equal(person.kps, prior.kps)
            assert person.racket == prior.racket
            assert person.detector_observed is prior.detector_observed
            assert person.detector_matched is prior.detector_matched
            assert (person.track_id, person.observation_id) == (prior.track_id, prior.observation_id)
    np.testing.assert_equal(case.window.shuttle.x, before.window.shuttle.x)
    np.testing.assert_equal(case.window.shuttle.vis, before.window.shuttle.vis)
    np.testing.assert_equal(case.window.shuttle.interp, before.window.shuttle.interp)
    assert result.estimate.contact_above_head is None
    assert getattr(result.estimate, "kps", None) is None
    assert getattr(result.estimate, "racket", None) is None


@pytest.mark.parametrize("detector_observed", [True, None])
def test_only_an_explicitly_skipped_current_detector_run_can_be_estimated(detector_observed):
    case = _case()
    for person in (1, 2):
        _change(case, 3, person, detector_observed=detector_observed, detector_matched=False)
    _unresolved(_evaluate(case))


@pytest.mark.parametrize("indices", [(0, 2), (4, 6)], ids=["left", "right"])
@pytest.mark.parametrize("field,value", [("detector_observed", False), ("detector_observed", None),
                                        ("detector_matched", False), ("detector_matched", None)])
def test_each_bracket_requires_a_fresh_unique_person_match(indices, field, value):
    case = _case()
    for index in indices:
        _change(case, index, **{field: value})
    _unresolved(_evaluate(case))


@pytest.mark.parametrize("index", [0, 6])
def test_missing_one_bracket_does_not_extrapolate(index):
    case = _case()
    case.index = index
    for person in (1, 2):
        _change(case, index, person, detector_observed=False, detector_matched=False)
    _unresolved(_evaluate(case))


@pytest.mark.parametrize("fps,eligible", [(30.0, False), (60.0, True)])
def test_maximum_span_is_enforced_in_video_seconds(fps, eligible):
    api = _api()
    case = _case()
    case.window.fps = fps
    result = _evaluate(case, policy=api.GeometryBracketPolicy(max_span_s=0.05))
    if eligible:
        assert result.status == "estimated"
        assert result.estimate.source_frames == (102, 104)
    else:
        _unresolved(result)


def test_a_failed_scheduled_match_cannot_be_skipped_to_reach_an_older_good_anchor():
    case = _case()
    _change(case, 2, detector_observed=True, detector_matched=False)
    # A tempting earlier same-ID observation exists at frame 100; it cannot
    # erase the failed scheduled observation at frame 102.
    _unresolved(_evaluate(case))


def test_segment_boundary_excludes_cross_cut_or_coordinate_epoch_brackets():
    case = _case()
    case.window.break_before[3] = True
    _unresolved(_evaluate(case))


@pytest.mark.parametrize("index", [2, 3, 4])
def test_replay_inside_the_bracket_is_not_geometry_support(index):
    case = _case()
    case.window.replay[index] = True
    _unresolved(_evaluate(case))


@pytest.mark.parametrize("mask", ["geometry_valid", "identity_unresolved"])
@pytest.mark.parametrize("index", [2, 3, 4])
def test_all_bracket_frames_need_valid_geometry_and_unambiguous_raw_identity(mask, index):
    case = _case()
    getattr(case, mask)[index] = mask == "identity_unresolved"
    _unresolved(_evaluate(case))


@pytest.mark.parametrize("field,value", [("track_id", 99), ("observation_id", "different-birth"),
                                        ("observation_id", None)])
@pytest.mark.parametrize("index", [2, 3, 4])
def test_reused_tracks_changed_births_and_episode_epochs_cannot_supply_geometry(field, value, index):
    case = _case()
    _change(case, index, **{field: value})
    _unresolved(_evaluate(case))


@pytest.mark.parametrize("match_format", ["singles", "doubles"])
@pytest.mark.parametrize("index", [2, 3, 4])
@pytest.mark.parametrize("difference", [-1, 1])
def test_missing_or_extra_raw_competitors_withhold_context(match_format, index, difference):
    case = _case(match_format)
    case.visible_counts[index] += difference
    _unresolved(_evaluate(case))


@pytest.mark.parametrize("match_format", ["singles", "doubles"])
def test_missing_competitor_episode_cannot_be_hidden_by_a_raw_count(match_format):
    case = _case(match_format)
    del case.frames[4][f"participant-test-{len(case.frames[4]):06d}"]
    _unresolved(_evaluate(case))


def test_duplicate_track_ids_across_episodes_are_unresolved():
    case = _case("doubles")
    _change(case, 3, 2, track_id=1)
    _unresolved(_evaluate(case))


def test_a_non_target_competitor_cannot_be_dropped_to_make_the_remaining_candidate_unique():
    case = _case("doubles")
    _change(case, 4, 2, court_xy=(10.0, -3.0))
    _unresolved(_evaluate(case))


def test_a_same_episode_court_side_flip_does_not_cross_the_net_with_interpolation():
    case = _case()
    _change(case, 3, court_xy=(0.0, 3.0))
    _unresolved(_evaluate(case))


@pytest.mark.parametrize("field,value", [
    ("bbox", np.array([np.nan, 85, 120, 185])),
    ("bbox", np.array([100, 85, 100, 185])),
    ("bbox", np.array([100, 85, 120])),
    ("court_xy", (np.inf, -3.0)),
    ("court_xy", (10.0, -3.0)),
    ("court_xy", None),
])
def test_nonfinite_degenerate_or_non_target_endpoint_geometry_is_withheld(field, value):
    case = _case()
    _change(case, 4, **{field: value})
    _unresolved(_evaluate(case))


def test_implausible_court_motion_cannot_establish_an_episode_bridge():
    case = _case()
    _change(case, 4, court_xy=(2.0, -3.0))  # 2 m in two frames exceeds the explicit 12 m/s gate.
    _unresolved(_evaluate(case))


def test_large_body_scale_change_cannot_establish_an_episode_bridge():
    case = _case()
    _change(case, 4, bbox=np.array([110, 85, 130, 485], dtype=float))
    _unresolved(_evaluate(case))


def test_overlapping_doubles_partners_do_not_pick_a_winner_by_dictionary_order():
    case = _case("doubles")
    for people in case.frames:
        first, partner = people["participant-test-000001"], people["participant-test-000002"]
        people["participant-test-000002"] = replace(partner, bbox=first.bbox.copy())
    _unresolved(_evaluate(case))
    case.frames = [dict(reversed(tuple(people.items()))) for people in case.frames]
    _unresolved(_evaluate(case))


@pytest.mark.parametrize("kind", ["distant", "missing", "reconstructed"])
def test_query_shuttle_must_be_observed_and_near_a_unique_body_context(kind):
    case = _case()
    if kind == "distant":
        case.window.shuttle.x[3] = 10_000
    elif kind == "missing":
        case.window.shuttle.vis[3] = False
    else:
        case.window.shuttle.interp[3] = True
    _unresolved(_evaluate(case))


def test_complete_context_slice_keeps_absolute_sources_and_estimated_geometry_identical():
    case = _case("doubles")
    whole = _evaluate(case)
    shuttle = case.window.shuttle
    subset = _Case(
        WindowObs(102, 30.0, Track(shuttle.x[2:5], shuttle.y[2:5], shuttle.vis[2:5],
                                 shuttle.conf[2:5], shuttle.interp[2:5]), {}),
        case.frames[2:5], case.geometry_valid[2:5], case.identity_unresolved[2:5],
        case.visible_counts[2:5], "doubles", 1,
    )
    result = _evaluate(subset)
    assert result.frame == whole.frame == 103
    assert result.estimate.source_frames == whole.estimate.source_frames == (102, 104)
    assert result.estimate.participant_id == whole.estimate.participant_id
    np.testing.assert_allclose(result.estimate.bbox_estimate, [100, 85, 120, 185])
    np.testing.assert_allclose(result.estimate.court_xy_estimate, [0.1, -3.0])


def test_unknown_format_does_not_inherit_singles_context():
    _unresolved(_evaluate(_case(), match_format="unknown"))


@pytest.mark.parametrize("bad", ["frame_count", "mask_length", "mask_dtype", "index", "fps"])
def test_malformed_alignment_and_timeline_fail_explicitly(bad):
    case = _case()
    if bad == "frame_count":
        case.frames.pop()
    elif bad == "mask_length":
        case.geometry_valid = np.ones(6, bool)
    elif bad == "mask_dtype":
        case.identity_unresolved = np.zeros(7, dtype=np.int64)
    elif bad == "index":
        case.index = 7
    else:
        case.window.fps = 0
    with pytest.raises(ValueError):
        _evaluate(case)


@pytest.mark.parametrize("field,value", [
    ("max_span_s", 0), ("max_span_s", np.nan), ("max_court_speed_m_s", 0),
    ("max_scale_ratio", 0.5), ("min_proximity", 0), ("relative_gap", 1.0),
])
def test_invalid_policy_cannot_silently_disable_safety_gates(field, value):
    api = _api()
    with pytest.raises(ValueError):
        api.GeometryBracketPolicy(**{field: value})
