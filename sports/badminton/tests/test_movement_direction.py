"""Court-plane travel direction uses elapsed time and honest observation gaps."""

import numpy as np
import pytest

from bai_badminton.analytics.match import MatchAnalytics
from bai_badminton.analytics.spatial import movement


@pytest.mark.parametrize("fps", [25, 30, 60])
@pytest.mark.parametrize("velocity,heading", [((1, 0), 0), ((0, 1), 90), ((-1, 0), 180), ((0, -1), 270)])
def test_known_court_motion_retains_speed_and_direction_at_each_frame_rate(fps, velocity, heading):
    frames = list(range(fps + 1))
    xy = np.arange(fps + 1)[:, None] / fps * np.array(velocity)
    result = movement(xy, frames, [7] * len(frames), [True] * len(frames), fps)
    assert result.motion
    for sample in result.motion:
        assert (sample.vx_m_s, sample.vy_m_s) == pytest.approx(velocity)
        assert sample.speed_m_s == pytest.approx(1)
        assert sample.heading_deg == pytest.approx(heading)
        assert sample.frame_start < sample.frame_end and sample.track_id == 7


def test_stationary_jitter_has_zero_velocity_and_no_heading():
    xy = np.array([[0.02 if i % 2 else -0.02, -3.0] for i in range(31)])
    result = movement(xy, list(range(31)), [7] * 31, [True] * 31, 30)
    assert result.motion and result.distance_m == 0
    assert all(sample.speed_m_s == 0 and sample.heading_deg is None for sample in result.motion)


def test_missing_frames_track_switch_and_teleport_never_create_travel():
    for xy, frames, tracks, valid in [
        ([[0, 0], [1, 0]], [0, 6], [1, 1], [True, True]),
        ([[0, 0], [1, 0]], [0, 1], [1, 2], [True, True]),
        ([[0, 0], [2, 0]], [0, 1], [1, 1], [True, True]),
        ([[0, 0], [0.1, 0]], [0, 1], [1, 1], [True, False]),
    ]:
        assert movement(np.array(xy), frames, tracks, valid, 30).motion == []


def test_travel_is_connected_to_public_analytics_with_frames_and_units():
    analytics = MatchAnalytics(30)
    analytics.on_presence(
        "P1", [(i / 30, -3) for i in range(31)], frames=list(range(31)), track_ids=[7] * 31, valid=[True] * 31
    )
    travel = analytics.to_public()["players"]["P1"]["travel"]
    assert travel["meaning"] == "direction_of_travel"
    assert travel["coordinate_system"] == "court_metres"
    assert travel["mean_speed_m_s"] == pytest.approx(1)
    assert travel["latest"]["frame_end"] == 30
    assert travel["latest"]["pts_us"] == 1_000_000
    assert travel["latest"]["heading_deg"] == 0
    assert MatchAnalytics(30).players["P1"].to_public()["travel"]["latest"] is None
