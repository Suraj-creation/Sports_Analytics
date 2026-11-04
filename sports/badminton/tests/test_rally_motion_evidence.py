"""Controlled motion-evidence contracts; not real player/pose accuracy labels."""

from dataclasses import replace

import numpy as np
import pytest

from bai_badminton.events.rally_motion import observed_participant_motion, trajectory_continuation_supported
from bai_badminton.observations import WindowObs
from bai_badminton.participant_contact import ParticipantSnapshot, participant_window
from bai_badminton.perception.shuttle_post import Track


def fixture(*, people=2, poses=False, fresh=True, stride=1, frame0=0):
    frames = []
    for _ in range(12):
        snapshots = {}
        for person in range(people):
            box = np.array([100.0 + person * 150, 100.0, 180.0 + person * 150, 300.0])
            pose = np.tile([140.0 + person * 150, 200.0, 0.9], (17, 1)) if poses else None
            snapshots[f"episode-{person}"] = ParticipantSnapshot(
                person,
                box,
                pose,
                (0.0, -3.0 if person % 2 else 3.0),
                f"birth-{person}",
                fresh,
                fresh,
            )
        frames.append(snapshots)
    shuttle = Track.from_arrays(np.arange(12.0) * 20, np.arange(12.0), np.ones(12, dtype=bool))
    window = WindowObs(frame0, 30, shuttle, {}, pose_stride=np.full(12, stride, dtype=np.int64))
    return participant_window(window, frames, restrict_target_court=True), frames


def refresh(window, frames):
    return participant_window(window, frames, restrict_target_court=True)


def test_stationary_players_are_false_even_with_moving_shuttle():
    window, frames = fixture()
    assert observed_participant_motion(window, frames, 11) is False
    window.shuttle.x[:] = np.nan
    window.shuttle.vis[:] = False
    assert observed_participant_motion(window, frames, 11) is False


@pytest.mark.parametrize("people", [2, 4])
def test_fresh_body_motion_supports_singles_or_doubles(people):
    window, frames = fixture(people=people)
    for index, frame in enumerate(frames):
        frame["episode-0"] = replace(frame["episode-0"], bbox=frame["episode-0"].bbox + [4 * index, 0, 4 * index, 0])
    assert observed_participant_motion(refresh(window, frames), frames, 11) is True


def test_current_scheduled_pose_can_move_on_carried_boxes():
    window, frames = fixture(poses=True, fresh=False)
    for index, frame in enumerate(frames):
        frame["episode-0"].kps[[5, 6], 0] += 5 * index
    assert observed_participant_motion(refresh(window, frames), frames, 11) is True


def test_one_jittering_joint_does_not_assert_motion():
    window, frames = fixture(poses=True, fresh=False)
    frames[-1]["episode-0"].kps[9, 0] += 200
    assert observed_participant_motion(refresh(window, frames), frames, 11) is False


def test_carried_boxes_and_missing_pose_are_unknown():
    window, frames = fixture(fresh=False)
    assert observed_participant_motion(window, frames, 11) is None


def test_missing_scheduled_pose_or_detector_match_cannot_bridge():
    window, frames = fixture(poses=True, fresh=False)
    frames[8]["episode-0"] = replace(frames[8]["episode-0"], kps=None)
    assert observed_participant_motion(refresh(window, frames), frames, 11) is None
    window, frames = fixture()
    frames[8]["episode-0"] = replace(frames[8]["episode-0"], detector_matched=False)
    assert observed_participant_motion(refresh(window, frames), frames, 11) is None


def test_off_schedule_pose_is_unknown():
    window, frames = fixture(poses=True, fresh=False, stride=2)
    assert observed_participant_motion(window, frames, 11) is None


def test_sparse_scheduled_poses_respect_absolute_frame_indices():
    window, frames = fixture(poses=True, fresh=False, stride=2, frame0=1)
    for index, frame in enumerate(frames):
        for snapshot in frame.values():
            if (window.frame0 + index) % 2:
                snapshot.kps[:] = np.nan
    assert observed_participant_motion(refresh(window, frames), frames, 11) is False


@pytest.mark.parametrize("field,value", [("track_id", 99), ("observation_id", "new-birth"), ("court_xy", None)])
def test_changed_lineage_or_unknown_geometry_is_rejected(field, value):
    window, frames = fixture()
    frames[8]["episode-0"] = replace(frames[8]["episode-0"], **{field: value})
    assert observed_participant_motion(refresh(window, frames), frames, 11) is None


def test_missing_episode_and_camera_cut_are_unknown():
    window, frames = fixture()
    frames[8].pop("episode-0")
    assert observed_participant_motion(refresh(window, frames), frames, 11) is None
    window, frames = fixture()
    window.break_before[10] = True
    assert observed_participant_motion(window, frames, 11) is None
    window.replay[11] = True
    assert observed_participant_motion(window, frames, 11) is None


def test_changed_episode_key_is_not_reidentified_by_track_number():
    window, frames = fixture()
    frames[-1]["different-episode"] = frames[-1].pop("episode-0")
    assert observed_participant_motion(refresh(window, frames), frames, 11) is None


def test_unknown_participant_does_not_make_stationary_claim():
    window, frames = fixture(people=1)
    assert observed_participant_motion(window, frames, 11) is None


@pytest.mark.parametrize("window_s,fraction", [(0.0, 0.1), (0.25, 0.0), (np.nan, 0.1), (0.25, np.inf)])
def test_invalid_guards_are_rejected(window_s, fraction):
    window, frames = fixture()
    with pytest.raises(ValueError):
        observed_participant_motion(window, frames, 11, window_s=window_s, min_body_fraction=fraction)


def reconstructed_gap(*, speed_before=10.0, speed_after=10.0, gap=10):
    n = gap + 10
    x = np.zeros(n)
    x[:5] = np.arange(5) * speed_before
    x[gap + 5 :] = x[4] + np.arange(1, 6) * speed_after
    x[5 : gap + 5] = np.linspace(x[4], x[gap + 5], gap + 2)[1:-1]
    track = Track.from_arrays(x, np.zeros(n), np.ones(n, dtype=bool))
    track.interp[5 : gap + 5] = True
    return WindowObs(0, 30, track, {})


def test_moving_brackets_support_reconstruction_without_relabeling_observed():
    window = reconstructed_gap()
    original = window.shuttle.interp.copy()
    assert trajectory_continuation_supported(window, 8)
    assert np.array_equal(window.shuttle.interp, original)
    assert not trajectory_continuation_supported(window, 4)


@pytest.mark.parametrize("before,after", [(0.0, 10.0), (10.0, 0.0), (0.33, 0.51), (2.9, 10.0), (10.0, 2.9)])
def test_stationary_or_pickup_bracket_is_not_supported(before, after):
    assert not trajectory_continuation_supported(reconstructed_gap(speed_before=before, speed_after=after), 8)


def test_airborne_reconstruction_outside_image_is_still_eligible():
    window = reconstructed_gap()
    window.shuttle.y[5:15] = -30
    assert trajectory_continuation_supported(window, 8)


@pytest.mark.parametrize("side", [slice(0, 4), slice(16, 20)])
def test_two_observed_brackets_are_required(side):
    window = reconstructed_gap()
    window.shuttle.vis[side] = False
    assert not trajectory_continuation_supported(window, 8)


def test_sparse_nonadjacent_anchors_do_not_establish_motion():
    window = reconstructed_gap()
    window.shuttle.vis[[1, 3]] = False
    assert not trajectory_continuation_supported(window, 8)


def test_cut_or_replay_prevents_cross_segment_support():
    window = reconstructed_gap()
    window.break_before[5] = True
    assert not trajectory_continuation_supported(window, 8)
    window = reconstructed_gap()
    window.break_before[15] = True
    assert not trajectory_continuation_supported(window, 8)
    window.replay[8] = True
    assert not trajectory_continuation_supported(window, 8)


@pytest.mark.parametrize("field,value", [("x", np.nan), ("y", np.inf)])
def test_nonfinite_reconstruction_cannot_support_continuation(field, value):
    window = reconstructed_gap()
    getattr(window.shuttle, field)[9] = value
    assert not trajectory_continuation_supported(window, 8)


def test_gaps_and_motion_above_existing_fill_bounds_are_rejected():
    assert not trajectory_continuation_supported(reconstructed_gap(gap=26), 8)
    assert not trajectory_continuation_supported(reconstructed_gap(speed_after=121.0), 8)
    window = reconstructed_gap()
    window.shuttle.x[15:] += 100_000
    assert not trajectory_continuation_supported(window, 8)


def test_one_moving_step_with_stationary_overall_bracket_is_not_enough():
    window = reconstructed_gap()
    window.shuttle.x[:5] = [0, 0, 10, 0, 0]
    assert not trajectory_continuation_supported(window, 8)
