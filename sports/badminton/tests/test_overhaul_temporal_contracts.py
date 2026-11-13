"""Synthetic regressions for the observed-evidence overhaul; no media or models."""

from dataclasses import replace

import numpy as np
import pytest

from bai_badminton.events.contact_evidence import (
    ContactEvidenceInputs,
    ContactMotionEvidence,
    Reliability,
    assess_contact_evidence,
    assess_flight_endpoint,
)
from bai_badminton.events.rally_fsm import RallyFSM, RallyParams, RallyState
from bai_badminton.events.stroke import jump_features
from bai_badminton.identity import IdentityResolver
from bai_badminton.observations import WindowObs
from bai_badminton.participant_contact import ParticipantSnapshot, participant_window
from bai_badminton.participation import ParticipantTracker
from bai_badminton.perception.shuttle_post import Track
from bai_badminton.perception_types import PersonObs, RacketObservation


def person(track, *, fresh, side="near"):
    y = 600 if side == "near" else 300
    return PersonObs(
        track_id=track, bbox=np.array([10, y - 100, 60, y], float), conf=0.9,
        detector_matched=fresh, appearance=np.array([0.1, 0.9], np.float32),
    )


def test_four_episode_births_count_observations_and_ignore_scheduled_carries():
    tracker = ParticipantTracker(frame_height=720, entry_frames=2, exit_frames=2)
    people = [person(i, fresh=True, side="near" if i <= 2 else "far") for i in range(1, 5)]
    assert not tracker.update(0, people, coverage_valid=True, absence_valid=True).participants
    for frame in (1, 2):
        carried = [replace(p, detector_matched=False) for p in people]
        assert not tracker.update(frame, carried, coverage_valid=True, absence_valid=False).participants
    born = tracker.update(3, people, coverage_valid=True, absence_valid=True)
    assert len({p.participant_id for p in born.participants}) == 4
    assert all(e.kind == "PARTICIPANT_FIRST_OBSERVED" for e in born.events)
    original = {p.track_id: p.participant_id for p in born.participants}
    carried = tracker.update(4, [replace(p, detector_matched=False) for p in people],
                             coverage_valid=True, absence_valid=False)
    assert not carried.events
    assert {p.track_id: p.participant_id for p in carried.participants} == original


def test_current_detector_miss_breaks_pending_entry_but_scheduled_tick_does_not():
    tracker = ParticipantTracker(frame_height=720, entry_frames=2)
    assert not tracker.update(0, [person(1, fresh=True)], coverage_valid=True, absence_valid=True).participants
    tracker.update(1, [], coverage_valid=True, absence_valid=False)
    tracker.update(2, [], coverage_valid=True, absence_valid=True)
    assert not tracker.update(3, [person(1, fresh=True)], coverage_valid=True, absence_valid=True).participants
    assert tracker.update(4, [person(1, fresh=True)], coverage_valid=True, absence_valid=True).participants


def test_carry_only_startup_never_claims_a_later_first_detection_is_an_entry():
    tracker = ParticipantTracker(frame_height=720, entry_frames=1)
    for frame in range(8):
        assert not tracker.update(frame, [person(1, fresh=False)],
                                  coverage_valid=True, absence_valid=False).participants
    first = tracker.update(8, [person(1, fresh=True)], coverage_valid=True, absence_valid=True)
    assert [event.kind for event in first.events] == ["PARTICIPANT_FIRST_OBSERVED"]


def test_carries_do_not_extend_a_rebind_lease_or_teach_appearance():
    resolver = IdentityResolver(frame_height=720, rebind_gap_frames=3)
    resolver.assign([person(1, fresh=True)], {"P1": "near", "P2": "far"}, 0)
    for frame in range(1, 6):
        carry = person(1, fresh=False)
        carry.appearance = np.array([1.0, 0.0], np.float32)
        assert resolver.assign([carry], {"P1": "near", "P2": "far"}, frame)["P1"].track_id == 1
    assert resolver._last_box[1][0] == 0
    assert resolver._sig["P1"] == pytest.approx([0.1, 0.9])
    assert resolver.assign([person(9, fresh=True)], {"P1": "near", "P2": "far"}, 6) == {}


def endpoint_inputs(**changes):
    base = ContactEvidenceInputs(
        frame=10, available_through=12, context_start=8, context_stop=13, provider="synthetic",
        motion=ContactMotionEvidence(
            before_frames=(8, 9, 10), after_frames=(10, 11, 12), speed_before=10, speed_after=12,
            spatial_sigma_px=0.5, incoming_direction_support=0.9, outgoing_direction_support=0.9,
            redirect_support=0.9,
        ),
        observation_status="fresh_observed", association_status="tracked", context_valid=True,
        player_observed=True, pose_observed=True, swing_support=0.8, proximity_support=0.8,
    )
    return replace(base, **changes)


def test_flight_endpoint_does_not_require_named_hitter_but_requires_physical_evidence():
    evidence = assess_contact_evidence(endpoint_inputs(attribution_target=None))
    assert assess_flight_endpoint(evidence).reliability is Reliability.PROBABLE
    weak = assess_contact_evidence(endpoint_inputs(pose_observed=False, swing_support=0.0))
    assert assess_flight_endpoint(weak).reliability is Reliability.AMBIGUOUS
    assert assess_flight_endpoint(None).reliability is Reliability.INSUFFICIENT


@pytest.mark.parametrize("status", ["missing", "reconstructed", "stale", "carried"])
def test_unobserved_next_candidate_never_supplies_physical_flight_endpoint(status):
    evidence = assess_contact_evidence(endpoint_inputs(observation_status=status))
    assert assess_flight_endpoint(evidence).reliability is Reliability.INSUFFICIENT


def test_participant_temporal_cues_need_exact_stamps_and_keep_raw_snapshots():
    shuttle = Track.from_arrays(np.arange(3, dtype=float), np.arange(3, dtype=float), np.ones(3, bool))
    window = WindowObs(100, 30.0, shuttle, {})
    racket = RacketObservation((20, 30), (10, 20), 0, 0.8, 9)
    kps = np.ones((17, 3))
    snapshots = [
        {"episode": ParticipantSnapshot(
            track_id=1, bbox=np.array([10, 20, 50, 100], float), kps=kps, court_xy=(0, -1),
            observation_id="birth", detector_observed=True, detector_matched=True,
            racket=racket, pose_frame_idx=100, racket_frame_idx=100,
        )}
        for _ in range(3)
    ]
    series = participant_window(window, snapshots).players["episode"]
    assert np.isfinite(series.kps[0]).all() and series.racket[0] is racket
    assert np.isnan(series.kps[1:]).all() and series.racket[1:] == [None, None]
    assert snapshots[2]["episode"].kps is kps
    assert snapshots[2]["episode"].racket is racket


def test_new_motion_rally_cannot_end_from_prestart_rest():
    fsm = RallyFSM(RallyParams(fps=30))
    for frame in range(7):
        fsm.step(frame, True, 0.0)
    assert fsm.step(7, True, 12).started is None
    fsm.step(8, True, 12)
    assert fsm.step(9, True, 12).started == 7
    fsm.step(10, True, 12)
    assert fsm.state is RallyState.IN_PLAY
    assert fsm.tentative_end is None


@pytest.mark.parametrize("fps", [25.0, 30.0, 60.0])
def test_jump_evidence_has_same_temporal_meaning_across_fps_and_abstains_without_hips(fps):
    n = round(2 * fps)
    contact = round(fps)
    ankles = np.full((n, 2), 600.0)
    hips = np.full(n, 500.0)
    heights = np.full(n, 100.0)
    action = slice(contact - round(6 * fps / 30), contact + round(6 * fps / 30) + 1)
    ankles[action] -= 10
    hips[action] -= 8
    evidence = jump_features(ankles, hips, heights, contact, fps=fps)
    assert evidence == pytest.approx({"lift_min": 0.1, "lift_max": 0.1, "hip_lift": 0.08})
    hips[:] = np.nan
    assert jump_features(ankles, hips, heights, contact, fps=fps) is None


@pytest.mark.parametrize("changes", [
    {"start_visible": 0}, {"start_visible": 1.5}, {"end_gap": 0}, {"end_gap": True},
    {"end_lookahead": -1}, {"min_duration_s": -1}, {"merge_gap_s": float("nan")},
    {"start_speed": -1}, {"stationary_speed": float("inf")}, {"resume_speed": float("nan")},
    {"fps": True},
])
def test_invalid_rally_configuration_fails_before_state_execution(changes):
    with pytest.raises(ValueError):
        RallyParams(**({"fps": 30.0} | changes))
