import numpy as np
import pytest

from bai_badminton.court import fit_homography
from bai_badminton.perception.players import CourtROI
from bai_badminton.perception.tracknet import heatmap_to_point


def test_neighbor_peak_does_not_hide_target_shuttle():
    heat = np.zeros((30, 50), np.float32)
    heat[10, 5] = 0.99  # neighboring court
    heat[12, 30] = 0.7  # selected court
    mask = np.zeros_like(heat, np.uint8)
    mask[:, 20:40] = 1
    assert heatmap_to_point(heat, 0.5, mask=mask) == pytest.approx((30, 12, 0.7))
    mask[:] = 0
    assert heatmap_to_point(heat, 0.5, mask=mask) is None


def test_player_margin_is_in_metres_at_both_ends():
    h = fit_homography(dict(far_left=(400, 100), far_right=(600, 100), near_right=(950, 700), near_left=(50, 700)))
    poly = h.court_to_image(np.array([[-3.05, 6.7], [3.05, 6.7], [3.05, -6.7], [-3.05, -6.7]]))
    roi = CourtROI(poly.astype(np.float32), homography=h)
    for y in (-5.0, 5.0):
        for x, expected in ((3.2, True), (4.1, False), (8.0, False)):
            px, py = h.court_to_image(np.array([[x, y]]))[0]
            assert roi.contains_feet(np.array([px - 10, py - 80, px + 10, py])) == expected


def test_airborne_region_retains_high_shuttle_and_excludes_other_side():
    from bai_badminton.perception.isolation import flight_mask

    poly = np.array([[300, 200], [500, 200], [650, 700], [150, 700]], np.float32)
    mask = flight_mask(poly, (800, 720), (800, 720))
    assert mask[80, 400]  # above the floor outline
    assert not mask[350, 30]  # adjacent court
    assert mask[500, 400]


def test_locked_court_never_reacquires_a_different_court():
    from bai_badminton.perception.court_lines import CourtTracker
    from bai_badminton.testing.court_render import MAIN, render

    tracker = CourtTracker()
    tracker.lock(MAIN.H)
    fits = tracker.track([render(MAIN)], [False], 0)
    assert fits[0] is not None
    # Translation by one court width produces a different floor region.
    shifted = MAIN.H @ np.array([[1, 0, 8], [0, 1, 0], [0, 0, 1]], float)
    tracker.lock(shifted)
    assert tracker.track([render(MAIN)], [True], 1) == [None]


def test_primary_selection_prefers_large_central_valid_court():
    from dataclasses import replace

    from bai_badminton.perception.court_lines import CourtFit, select_primary
    from bai_badminton.testing.court_render import MAIN

    target = CourtFit(MAIN.H, 0.9, 2.0, (6, 5), 1.0, None, area=0.45)
    side = replace(target, H=np.array([[1, 0, 550], [0, 1, 0], [0, 0, 1]]) @ MAIN.H, area=0.15, support=2.1)
    invalid = replace(target, precision=0.4, area=0.9, support=5.0)
    assert select_primary([side, invalid, target], (1280, 720)) is target
    assert select_primary([invalid], (1280, 720)) is None


def test_fixed_camera_uses_background_despite_people_moving():
    from bai_badminton.perception.isolation import is_fixed_camera
    from bai_badminton.testing.court_render import MAIN, Camera, render

    fixed = [render(MAIN, players=[(x, -4)]) for x in (-1.0, 0.0, 1.0, 2.0)]
    assert is_fixed_camera(fixed)
    moving = [render(Camera(MAIN.centre, (x, 0, 0), MAIN.f)) for x in (0.0, 1.0, 2.0, 3.0)]
    assert not is_fixed_camera(moving)
    assert not is_fixed_camera([np.zeros((720, 1280, 3), np.uint8)] * 4)


def test_uncalibrated_session_does_not_analyse_all_courts(tmp_path):
    from test_plugin_court_lines import chunk, make_session

    session, _ = make_session(tmp_path)
    observations = session.perceive(chunk(0, 4))
    assert all(f.replay and f.view == "none" and not f.persons and f.shuttle_xy is None for f in observations.frames)


def test_new_aisle_track_is_excluded_but_established_player_can_step_out():
    from bai_badminton.court import Homography
    from bai_badminton.perception.players import PlayerPerception

    h = Homography(np.array([[50.0, 0.0, 320.0], [0.0, -40.0, 360.0], [0.0, 0.0, 1.0]]), 0.0, 4)
    poly = h.court_to_image(np.array([[-3.05, 6.7], [3.05, 6.7], [3.05, -6.7], [-3.05, -6.7]])).astype(np.float32)
    roi = CourtROI(poly, homography=h)
    position = [3.2]

    def detector(image):
        px, py = h.court_to_image(np.array([[position[0], 0.0]]))[0]
        x0, y0, _, _ = roi.crop_box(640, 720)
        return np.array([[px - 15 - x0, py - 90 - y0, px + 15 - x0, py - y0]]), np.array([0.99])

    perception = PlayerPerception(detector, None, 30, det_stride=1)
    perception.set_roi(roi)
    image = np.zeros((720, 640, 3), np.uint8)
    assert perception.process(0, image) == []
    assert perception.process(1, image) == []
    position[0] = 2.9
    admitted = perception.process(2, image)
    assert len(admitted) == 1
    position[0] = 3.2
    assert len(perception.process(3, image)) == 1
    perception.on_cut()
    assert perception.process(4, image) == []


def test_legacy_line_calibration_gets_fixed_camera_lock_on_seed(tmp_path):
    from test_plugin_court_lines import make_session, open_session

    from bai_badminton.court import Homography
    from bai_badminton.testing.court_render import MAIN, render

    session, store = make_session(tmp_path)
    session.engine.set_calibration(0, Homography(MAIN.H, 0.0, 4), extra={"mode": "lines"})
    restored = open_session(session.session, store, tmp_path)
    assert restored.perception.court._locked is None
    restored.seed([render(MAIN, players=[(x, -4)]) for x in (-1.0, 0.0, 1.0, 2.0)])
    assert restored.perception.court._locked is not None
    assert store.query(types=["calibration"])[-1].payload["fixed_camera"] is True
    reopened = open_session(session.session, store, tmp_path)
    assert reopened.perception.court._locked is not None


def test_manual_calibration_preserves_known_fixed_camera_lock(tmp_path):
    from test_plugin_court_lines import _clicks, make_session, open_session

    from bai_badminton.court import Homography
    from bai_badminton.testing.court_render import MAIN

    session, store = make_session(tmp_path)
    session._apply_calibration(Homography(MAIN.H, 0.0, 4), mode="lines", record={"fixed_camera": True})
    assert session.perception.court._locked is not None
    reply = session.handle({"cmd": "calibrate", "points": _clicks(0.0), "frame": 10})
    assert reply["ok"]
    assert session.perception.court._locked is not None
    assert store.query(types=["calibration"])[-1].payload["fixed_camera"] is True
    assert open_session(session.session, store, tmp_path).perception.court._locked is not None


def test_static_cache_is_invalid_after_changing_selected_court(tmp_path):
    from test_plugin_court_lines import chunk, make_session

    from bai_badminton.court import Homography
    from bai_badminton.plugin import StaleCacheError
    from bai_badminton.testing.court_render import MAIN

    session, _ = make_session(tmp_path)
    session._apply_calibration(Homography(MAIN.H, 0.0, 4))
    assert session.perception.ref_id is None
    cached = session.encode_perception(session.perceive(chunk(0, 4)))
    assert session.decode_perception(cached, diagnostic=True).start == 0
    shifted = MAIN.H @ np.array([[1, 0, 8], [0, 1, 0], [0, 0, 1]], float)
    session._apply_calibration(Homography(shifted, 0.0, 4))
    with pytest.raises(StaleCacheError):
        session.decode_perception(cached, diagnostic=True)


def test_uncalibrated_session_rejects_calibrated_cache(tmp_path):
    from test_plugin_court_lines import chunk, make_session

    from bai_badminton.court import Homography
    from bai_badminton.plugin import StaleCacheError
    from bai_badminton.testing.court_render import MAIN

    session, _ = make_session(tmp_path)
    session._apply_calibration(Homography(MAIN.H, 0.0, 4), mode="lines")
    cached = session.encode_perception(session.perceive(chunk(0, 4)))
    fresh_dir = tmp_path / "fresh"
    fresh_dir.mkdir()
    fresh, _ = make_session(fresh_dir)
    with pytest.raises(StaleCacheError):
        fresh.decode_perception(cached, diagnostic=True)


def test_cache_is_invalid_after_camera_lock_policy_changes(tmp_path):
    from test_plugin_court_lines import chunk, make_session

    from bai_badminton.court import Homography
    from bai_badminton.plugin import StaleCacheError
    from bai_badminton.testing.court_render import MAIN

    session, _ = make_session(tmp_path)
    h = Homography(MAIN.H, 0.0, 4)
    session._apply_calibration(h, mode="lines", record={"fixed_camera": False})
    cached = session.encode_perception(session.perceive(chunk(0, 4)))
    session._apply_calibration(h, mode="lines", record={"fixed_camera": True})
    with pytest.raises(StaleCacheError):
        session.decode_perception(cached, diagnostic=True)
