import numpy as np
import pytest

from bai_badminton.events.stroke import post_contact_motion


def motion(x, y, visible=None, interpolated=None, fps=30.0, height=1080.0):
    n = len(x)
    return post_contact_motion(
        np.array(x, dtype=float),
        np.array(y, dtype=float),
        np.ones(n, dtype=bool) if visible is None else np.array(visible, dtype=bool),
        np.zeros(n, dtype=bool) if interpolated is None else np.array(interpolated, dtype=bool),
        0,
        fps,
        height,
    )


def test_estimates_speed_and_direction_from_multiple_observed_frames():
    speed, vy = motion([0, 10, 20, 30, 40, 50], [0, 5, 10, 15, 20, 25])
    assert speed == pytest.approx(np.hypot(300, 150))
    assert vy == pytest.approx(150)


def test_two_actual_samples_do_not_establish_consistent_motion():
    speed, vy = motion([0, 10, 20, 30, 40, 50], [0, 5, 10, 15, 20, 25], visible=[True, True, False, False, False, True])
    assert speed is None and vy is None


def test_interpolated_points_cannot_manufacture_evidence():
    speed, vy = motion(
        [0, 10, 20, 30, 40, 50], [0, 5, 10, 15, 20, 25], interpolated=[False, False, True, True, True, False]
    )
    assert speed is None and vy is None


def test_large_tracking_outlier_abstains_instead_of_inflating_speed():
    speed, vy = motion([0, 10, 20, 900, 40, 50], [0, 5, 10, 800, 20, 25])
    assert speed is None and vy is None


def test_missing_nonfinite_samples_are_not_treated_as_real_observations():
    speed, vy = motion([0, 10, np.nan, 30, np.nan, np.nan], [0, 5, 10, 15, 20, 25])
    assert speed is None and vy is None


def test_frames_before_contact_and_after_five_frames_do_not_affect_estimate():
    speed, vy = motion([9000, 10, 20, 30, 40, 50, -9000], [9000, 5, 10, 15, 20, 25, -9000])
    assert speed == pytest.approx(np.hypot(300, 150))
    assert vy == pytest.approx(150)


@pytest.mark.parametrize("fps,height", [(0, 1080), (30, 0), (float("nan"), 1080)])
def test_invalid_timebase_or_frame_size_abstains(fps, height):
    speed, vy = motion([0, 10, 20, 30, 40, 50], [0, 5, 10, 15, 20, 25], fps=fps, height=height)
    assert speed is None and vy is None


def test_nonconsecutive_observed_samples_use_actual_elapsed_frames():
    speed, vy = motion([0, 10, 20, 30, 40, 50], [0, 5, 10, 15, 20, 25], visible=[True, True, False, True, False, True])
    assert speed == pytest.approx(np.hypot(300, 150))
    assert vy == pytest.approx(150)


def test_low_evidence_keeps_nonserve_classifier_unknown():
    from bai_badminton.events.stroke import RuleStrokeClassifier, StrokeContext

    speed, vy = motion([0, 10, 20, 30, 40, 50], [0, 5, 10, 15, 20, 25], visible=[True, True, False, False, False, True])
    prediction = RuleStrokeClassifier().predict(
        StrokeContext(
            frame=0,
            player_id="A",
            is_serve=False,
            hitter_court_xy=(0, 3),
            speed_after_px_s=speed,
            frame_height_px=1080,
            flight_time_s=1.0,
            vy_after_px_s=vy,
            hitter_side="near",
            contact_above_head=None,
        )
    )
    assert prediction.top[0] == "unknown"
    assert prediction.abstention_reason == "missing_required_evidence"


def test_serve_with_missing_post_contact_evidence_is_unknown():
    from bai_badminton.events.stroke import RuleStrokeClassifier, StrokeContext

    prediction = RuleStrokeClassifier().predict(
        StrokeContext(
            frame=0,
            player_id="A",
            is_serve=True,
            hitter_court_xy=None,
            speed_after_px_s=None,
            frame_height_px=1080,
            flight_time_s=1.0,
            vy_after_px_s=None,
            hitter_side="near",
            contact_above_head=None,
        )
    )
    assert prediction.top[0] == "unknown"
    assert prediction.abstention_reason == "missing_required_evidence"


def test_next_contact_excludes_opponent_motion_and_abstains_when_too_few_samples():
    x = np.array([0, 10, 20, 30, 40, 50], dtype=float)
    y = np.zeros(6, dtype=float)
    speed, vy = post_contact_motion(x, y, np.ones(6, dtype=bool), np.zeros(6, dtype=bool),
                                    0, 30.0, 1080.0, next_contact_idx=3)
    assert speed is None and vy is None


def test_next_contact_excludes_later_return_from_velocity_estimate():
    x = np.array([0, 10, 20, 30, -300, -600], dtype=float)
    y = np.zeros(6, dtype=float)
    speed, vy = post_contact_motion(x, y, np.ones(6, dtype=bool), np.zeros(6, dtype=bool),
                                    0, 30.0, 1080.0, next_contact_idx=4)
    assert speed == pytest.approx(300.0)
    assert vy == pytest.approx(0.0)


def test_engine_excludes_next_contact_when_building_shot_speed(tmp_path):
    from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
    from bai_badminton.events.contact import ContactCandidate
    from bai_badminton.perception.shuttle_post import Track
    from bai_badminton.testing.synth import make_rally
    from bai_engine.store import EventStore

    store = EventStore(tmp_path / "events.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
    track = Track.from_arrays(np.arange(6, dtype=float) * 10, np.zeros(6), np.ones(6, dtype=bool))
    engine._shuttle_around = lambda _frame: (track, 0)
    engine._on_contact(ContactCandidate(frame=10, player_id=None, p=0.8), make_rally(n_shots=3).obs)
    engine._classify(engine._open_contacts[-1], next_frame=13, is_serve=False, receiver=None)
    stroke = store.query(types=["stroke"])[0]
    assert stroke.payload["speed_px_s"] is None
    assert stroke.payload["stroke"] == "unknown"
    store.close()


@pytest.mark.parametrize("is_serve", [True, False])
def test_stationary_shuttle_observations_do_not_imply_a_shot_family(is_serve):
    from bai_badminton.events.stroke import RuleStrokeClassifier, StrokeContext

    speed, vy = motion([10, 10, 10, 10, 10, 10], [20, 20, 20, 20, 20, 20])
    assert speed == 0.0 and vy == 0.0
    prediction = RuleStrokeClassifier().predict(StrokeContext(
        frame=0, player_id="A", is_serve=is_serve, hitter_court_xy=(0, 3),
        speed_after_px_s=speed, frame_height_px=1080, flight_time_s=1.1,
        vy_after_px_s=vy, hitter_side="near", contact_above_head=None,
    ))
    assert prediction.top[0] == "unknown"
    assert prediction.abstention_reason == "missing_required_evidence"
