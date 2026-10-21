"""Court calibration from the painted lines, against ground truth from synthetic cameras.

Every claim the broadcast pipeline relies on: the court is found from a single frame for wide, tight and
side-on cameras (and nothing is found where there is no court); the camera behind each homography is
recovered; frames are attributed to the right physical camera (pan / tilt / zoom of the main camera vs a
different camera); a sequence is tracked through pans and cuts."""

from __future__ import annotations

import cv2
import numpy as np
import pytest

from bai_badminton.court import REFERENCE_POINTS
from bai_badminton.perception import court_lines as cl
from bai_badminton.testing.court_render import FOLLOW, MAIN, SIDE, Camera, noise_frame, render

PTS = np.array(list(REFERENCE_POINTS.values()), np.float64)
TURN = np.diag([-1.0, -1.0, 1.0])


def err(H_est: np.ndarray, H_true: np.ndarray, size: tuple[int, int] = (1280, 720), symmetric: bool = False) -> float:
    """Largest image error (px) over the court's reference points that are in view (``symmetric``: up to the
    court's 180° symmetry — a side-on view does not tell which end is which)."""
    a = cv2.perspectiveTransform(PTS.reshape(-1, 1, 2), H_true).reshape(-1, 2)
    m = (a[:, 0] >= 0) & (a[:, 0] < size[0]) & (a[:, 1] >= 0) & (a[:, 1] < size[1])
    out = []
    for T in (np.eye(3), TURN) if symmetric else (np.eye(3),):
        b = cv2.perspectiveTransform(PTS.reshape(-1, 1, 2), H_est @ T).reshape(-1, 2)
        out.append(float(np.linalg.norm(a[m] - b[m], axis=1).max()))
    return min(out)


@pytest.fixture(scope="module")
def main_fit() -> cl.CourtFit:
    fit = cl.detect_court(render(MAIN, players=[(0.4, -4.0), (-1.0, 4.5)]))
    assert fit is not None
    return fit


def test_wide_broadcast_view_is_calibrated_from_one_frame(main_fit: cl.CourtFit) -> None:
    assert main_fit.ok and main_fit.lines[0] >= 4 and main_fit.lines[1] >= 4
    assert err(main_fit.H, MAIN.H) < 2.0
    # the near end is the camera's end, without being told
    assert not main_fit.ambiguous_end


def test_the_camera_is_recovered(main_fit: cl.CourtFit) -> None:
    pose = main_fit.pose
    assert pose is not None
    assert np.linalg.norm(pose.centre - np.array(MAIN.centre)) < 0.5
    assert abs(pose.focal_px - MAIN.f) / MAIN.f < 0.05
    # the projected net posts agree with the true camera
    true_pose = cl.CameraPose(MAIN.f, MAIN.R, -MAIN.R @ np.array(MAIN.centre), MAIN.size)
    for a, b in zip(pose.net_top(), true_pose.net_top(), strict=True):
        assert np.hypot(a[0] - b[0], a[1] - b[1]) < 3.0


def test_tight_view_of_half_the_court() -> None:
    fit = cl.detect_court(render(FOLLOW, players=[(0.0, 4.0)]))
    assert fit is not None and fit.ok
    assert err(fit.H, FOLLOW.H) < 3.0


def test_side_on_camera_up_to_the_court_symmetry() -> None:
    fit = cl.detect_court(render(SIDE))
    assert fit is not None and fit.ok
    assert err(fit.H, SIDE.H, symmetric=True) < 4.0
    assert fit.ambiguous_end  # a camera level with the net cannot tell the ends apart from the lines


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_no_court_no_calibration(seed: int) -> None:
    assert cl.detect_court(noise_frame(seed)) is None
    plain = np.full((720, 1280, 3), (70, 160, 60), np.uint8)
    assert cl.detect_court(plain) is None


def test_a_human_calibration_is_refined_onto_the_lines() -> None:
    img = render(MAIN)
    rng = np.random.default_rng(0)
    corners = np.array([REFERENCE_POINTS[n] for n in ("far_left", "far_right", "near_right", "near_left")])
    clicked = cv2.perspectiveTransform(corners.reshape(-1, 1, 2), MAIN.H).reshape(-1, 2) + rng.normal(0, 4, (4, 2))
    H_click, _ = cv2.findHomography(corners, clicked)
    fit = cl.refine_court(img, H_click)
    assert fit is not None and fit.ok
    assert err(fit.H, MAIN.H) < err(H_click, MAIN.H) and err(fit.H, MAIN.H) < 2.0


# ---------------------------------------------------------------------------------------- cameras
def _pan(cam: Camera, dx: float, dy: float = 0.0, zoom: float = 1.0) -> Camera:
    t = cam.target
    return Camera(cam.centre, (t[0] + dx, t[1] + dy, t[2]), cam.f * zoom, cam.size)


def test_rotation_residual_separates_cameras(main_fit: cl.CourtFit) -> None:
    assert main_fit.pose is not None
    same = [_pan(MAIN, 1.5, 2.0, 1.6), _pan(MAIN, -2.0, -1.0, 0.8), _pan(MAIN, 0.0, 4.0, 3.0)]
    for cam in same:
        assert cl.head_residual(main_fit.pose, main_fit.H, cam.H, cam.size) < 0.05
    for cam in (FOLLOW, SIDE):
        assert cl.head_residual(main_fit.pose, main_fit.H, cam.H, cam.size) > cl.SAME_HEAD_TOL


def test_rig_classifies_frames_by_camera(main_fit: cl.CourtFit) -> None:
    assert main_fit.pose is not None
    rig = cl.CameraRig.from_main(main_fit.H, main_fit.pose)
    heads = {}
    for name, cam in (("zoomed", _pan(MAIN, 1.0, 3.0, 2.5)), ("follow", FOLLOW), ("side", SIDE), ("main", MAIN)):
        fit = cl.detect_court(render(cam))
        assert fit is not None, name
        heads[name] = rig.classify(fit)
    assert heads["main"] == 0 and heads["zoomed"] == 0
    assert heads["follow"] not in (0, None) and heads["side"] not in (0, None)
    assert heads["follow"] != heads["side"]


def test_the_most_seen_camera_is_chosen_as_main() -> None:
    fits = [cl.detect_court(render(c)) for c in (SIDE, MAIN, _pan(MAIN, 0.5, 1.0, 1.3), FOLLOW, _pan(MAIN, -0.5))]
    main = cl.choose_main([f for f in fits if f is not None])
    assert main is not None and main.pose is not None
    assert np.linalg.norm(main.pose.centre - np.array(MAIN.centre)) < 0.6
    assert main.support >= max(f.support for f in fits[1:3] if f is not None) - 1e-9  # its widest view


# ---------------------------------------------------------------------------------------- tracking
def test_tracker_follows_a_pan_through_cuts() -> None:
    frames, truth, cuts = [], [], []
    for _ in range(12):  # still
        frames.append(render(MAIN))
        truth.append(MAIN.H)
    for k in range(16):  # pan right and zoom in
        cam = _pan(MAIN, 0.12 * k, 0.15 * k, 1 + 0.03 * k)
        frames.append(render(cam))
        truth.append(cam.H)
    cut1 = len(frames)
    for k in range(8):  # a close-up: no court
        frames.append(noise_frame(10 + k))
        truth.append(None)
    cut2 = len(frames)
    for _ in range(10):  # back to the main camera
        frames.append(render(MAIN))
        truth.append(MAIN.H)
    cuts = [i in (cut1, cut2) for i in range(len(frames))]
    tr = cl.CourtTracker()
    fits = []
    for a in range(0, len(frames), 20):  # in chunks, like the runner
        fits += tr.track(frames[a : a + 20], cuts[a : a + 20], a)
    for i, (fit, H) in enumerate(zip(fits, truth, strict=True)):
        if H is None:
            assert fit is None, i
        else:
            assert fit is not None, i
            assert err(fit.H, H) < 4.0, (i, fit.method)
    methods = {f.method for f in fits if f is not None}
    assert {"search", "track", "static"} <= methods
    assert tr.stats.searches <= 6  # searching is the expensive path: only at the start and the cuts


def test_a_fluke_fit_shorter_than_min_run_is_dropped() -> None:
    tr = cl.CourtTracker(min_run=4)
    frames = [noise_frame(1), render(MAIN), render(MAIN), noise_frame(2), noise_frame(3)]
    cuts = [False, True, False, True, False]
    fits = tr.track(frames, cuts, 0)
    assert fits == [None] * 5
