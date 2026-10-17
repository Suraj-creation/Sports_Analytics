"""Camera tracker: a synthetic broadcast camera with known motion (pan + zoom + roll + jitter), moving
"players", a static score bug and letterbox bars — the recovered ``G_t`` is compared with the truth."""

from __future__ import annotations

import cv2
import numpy as np
import pytest

from bai_badminton.perception.camera import CameraTracker, project

W, H = 1280, 720
PROBES = np.array([[x, y] for x in (260, 640, 1020) for y in (200, 360, 520)], dtype=np.float64)


def make_world(seed: int, w: int = 3600, h: int = 2000) -> np.ndarray:
    rng = np.random.default_rng(seed)
    base = rng.integers(40, 210, (h // 50, w // 50, 3)).astype(np.uint8)
    img = cv2.resize(base, (w, h), interpolation=cv2.INTER_CUBIC)
    for _ in range(900):
        x, y = int(rng.integers(0, w)), int(rng.integers(0, h))
        c = tuple(int(v) for v in rng.integers(0, 255, 3))
        if rng.random() < 0.5:
            cv2.rectangle(img, (x, y), (x + int(rng.integers(15, 130)), y + int(rng.integers(10, 90))), c, -1)
        else:
            cv2.ellipse(img, (x, y), (int(rng.integers(8, 60)), int(rng.integers(8, 40))), 0, 0, 360, c, -1)
    for _ in range(120):
        cv2.putText(
            img,
            "".join(chr(int(v)) for v in rng.integers(65, 90, 5)),
            (int(rng.integers(0, w - 200)), int(rng.integers(40, h))),
            cv2.FONT_HERSHEY_SIMPLEX,
            float(rng.uniform(0.8, 2.2)),
            (255, 255, 255),
            2,
        )
    return cv2.GaussianBlur(img, (0, 0), 1.0)


def pose(t: float, n: int, *, zoom1: float = 1.5, pan: float = 700.0, roll_deg: float = 3.0) -> np.ndarray:
    """world → frame homography at progress ``t`` ∈ [0, n]: pan right, zoom in, roll a little."""
    a = t / max(n, 1)
    z = 1.0 + (zoom1 - 1.0) * a
    th = np.deg2rad(roll_deg) * a
    cx, cy = 1200.0 + pan * a, 900.0 + 120.0 * np.sin(2 * np.pi * a)
    Rz = np.array([[np.cos(th), -np.sin(th), 0], [np.sin(th), np.cos(th), 0], [0, 0, 1]])
    S = np.diag([z, z, 1.0])
    T0 = np.array([[1, 0, W / 2], [0, 1, H / 2], [0, 0, 1.0]])
    T1 = np.array([[1, 0, -cx], [0, 1, -cy], [0, 0, 1.0]])
    M = T0 @ Rz @ S @ T1
    M[2, 0] = 1.5e-5 * a  # slight keystone as the camera tilts
    return M


def render(world: np.ndarray, M: np.ndarray, k: int, *, graphics: bool = True) -> np.ndarray:
    f = cv2.warpPerspective(world, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    if graphics:
        # two "players" crossing the court + a static score bug + pillar-box bars
        for off, col in ((0, (30, 30, 200)), (400, (200, 60, 30))):
            x = int(300 + off + 2.5 * k) % (W - 150)
            cv2.rectangle(f, (x, 260 + off // 8), (x + 70, 520 + off // 8), col, -1)
        cv2.rectangle(f, (110, 30), (520, 120), (240, 240, 240), -1)
        cv2.putText(f, "ANTONSEN 10  FARHAN 6", (122, 85), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
        f[:, :90] = 0
        f[:, -90:] = 0
    return f


def truth(M0: np.ndarray, Mt: np.ndarray) -> np.ndarray:
    return Mt @ np.linalg.inv(M0)


def err(G_est: np.ndarray, G_true: np.ndarray) -> float:
    return float(np.linalg.norm(project(G_est, PROBES) - project(G_true, PROBES), axis=1).mean())


@pytest.fixture(scope="module")
def world() -> np.ndarray:
    return make_world(1)


def run(world: np.ndarray, n: int = 120, chunk: int = 60) -> tuple[CameraTracker, list, list]:
    M0 = pose(0, n)
    tr = CameraTracker()
    assert tr.set_reference(render(world, M0, 0)) is not None
    est, gt = [], []
    for s in range(0, n, chunk):
        frames = [render(world, pose(k, n), k) for k in range(s, s + chunk)]
        est += tr.track(frames, [False] * chunk, s)
        gt += [truth(M0, pose(k, n)) for k in range(s, s + chunk)]
    return tr, est, gt


def test_follows_pan_zoom_roll_with_players_graphics_and_bars(world: np.ndarray) -> None:
    _, est, gt = run(world)
    errs = [err(e, g) for e, g in zip(est, gt, strict=True) if e is not None]
    assert len(errs) == len(est), "every frame of a continuous shot is registered"
    assert np.mean(errs) < 1.5 and max(errs) < 5.0, (np.mean(errs), max(errs))


def test_a_static_court_would_have_been_wrong(world: np.ndarray) -> None:
    """The bug being fixed: the pose at the end of the pan is far from the reference pose."""
    _, _, gt = run(world)
    assert err(np.eye(3), gt[-1]) > 150


def test_out_of_order_chunk_is_registered_and_backfilled(world: np.ndarray) -> None:
    """The runner perceives a chunk near the playhead before the ones in between (seek preview): no chain
    from the previous chunk exists, so it must anchor to the reference and fill its leading frames."""
    n = 120
    M0 = pose(0, n)
    tr = CameraTracker()
    tr.set_reference(render(world, M0, 0))
    frames = [render(world, pose(k, n), k) for k in range(60, 120)]
    est = tr.track(frames, [False] * 60, 60)
    assert all(e is not None for e in est)
    assert max(err(e, truth(M0, pose(60 + i, n))) for i, e in enumerate(est)) < 5.0


def test_camera_cut_to_a_different_view_and_back(world: np.ndarray) -> None:
    n = 90
    M0 = pose(0, n)
    other = make_world(2)
    tr = CameraTracker()
    tr.set_reference(render(world, M0, 0))
    frames, cuts, gt = [], [], []
    for k in range(n):
        if 30 <= k < 50:  # close-up / crowd camera: a different scene entirely
            frames.append(render(other, pose(k, n, zoom1=2.0), k))
            gt.append(None)
        else:
            frames.append(render(world, pose(k, n), k))
            gt.append(truth(M0, pose(k, n)))
        cuts.append(k in (30, 50))
    est = tr.track(frames, cuts, 0)
    for k, (e, g) in enumerate(zip(est, gt, strict=True)):
        if g is None:
            assert e is None, f"frame {k}: a foreign scene must not be registered"
        else:
            assert e is not None, f"frame {k}: court view lost"
            assert err(e, g) < 5.0, f"frame {k}"


def test_unrelated_scene_is_never_registered(world: np.ndarray) -> None:
    tr = CameraTracker()
    tr.set_reference(render(world, pose(0, 60), 0))
    other = make_world(3)
    frames = [render(other, pose(k, 60), k) for k in range(30)]
    assert all(e is None for e in tr.track(frames, [True] + [False] * 29, 0))


def test_textureless_reference_disables_tracking() -> None:
    tr = CameraTracker()
    assert tr.set_reference(np.full((H, W, 3), 90, np.uint8)) is None
    assert not tr.ready
    assert tr.track([np.zeros((H, W, 3), np.uint8)], [False], 0) == [None]


# ---------------------------------------------------------------- court-plane verification
FLOOR_Y = 520  # rows below this show the floor plane (the minority of the frame: the background dominates)


def render_two_planes(floor_world: np.ndarray, bg_world: np.ndarray, Mf: np.ndarray, Mb: np.ndarray) -> np.ndarray:
    f = cv2.warpPerspective(bg_world, Mb, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    fl = cv2.warpPerspective(floor_world, Mf, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    f[FLOOR_Y:] = fl[FLOOR_Y:]
    return f


def floor_world() -> np.ndarray:
    """A court-like floor: flat mat colour, thin white *finite* line segments in both directions and a few
    floor decals.  (Lines that run the whole frame would be invariant to a slide along them and so
    match a displaced floor — a real court's lines end at its boundaries.)"""
    rng = np.random.default_rng(11)
    img = np.full((2000, 3600, 3), (70, 150, 80), np.uint8)
    img = cv2.add(img, rng.integers(0, 6, img.shape, dtype=np.uint8))
    for _ in range(40):
        x, y, L = int(rng.integers(0, 3400)), int(rng.integers(0, 1900)), int(rng.integers(250, 800))
        if rng.random() < 0.5:
            cv2.line(img, (x, y), (min(x + L, 3599), y), (255, 255, 255), 5)
        else:
            cv2.line(img, (x, y), (x, min(y + L, 1999)), (255, 255, 255), 5)
    for _ in range(40):
        at = (int(rng.integers(0, 3300)), int(rng.integers(60, 2000)))
        cv2.putText(img, "ODENSE", at, cv2.FONT_HERSHEY_DUPLEX, 2.2, (240, 240, 240), 4)
    return cv2.GaussianBlur(img, (0, 0), 1.0)


FLOOR_POLY = [(0, FLOOR_Y + 10), (W, FLOOR_Y + 10), (W, H), (0, H)]


def test_pose_from_the_background_is_rejected_when_the_floor_does_not_line_up() -> None:
    """A camera that *moved* (not panned) shows the background through one homography and the floor
    through another.  The background-plane pose is a fine homography of the wrong plane for the court, so
    it must be refused — while a true pan/zoom, which moves both together, is accepted."""
    fw, bw = floor_world(), make_world(8)
    n = 60
    M0 = pose(0, n, zoom1=1.2, pan=300)
    tr = CameraTracker(verify_every=1)
    assert tr.set_reference(render_two_planes(fw, bw, M0, M0), floor=FLOOR_POLY) is not None

    # (a) pure pan/zoom: floor and background share the pose
    poses = [pose(k, n, zoom1=1.2, pan=300) for k in range(n)]
    frames = [render_two_planes(fw, bw, P, P) for P in poses]
    est = tr.track(frames, [False] * n, 0)
    # While the camera tilts up the floor all but leaves the frame (< 4% in view): those frames are
    # honestly "no court", but the pose keeps being tracked, so it is verified again as the floor returns.
    assert sum(e is not None for e in est) >= 0.8 * n, "a true pan/zoom keeps the court verified"
    assert all(e is not None for e in est[:30]) and all(e is not None for e in est[55:])
    for k, e in enumerate(est):
        if e is not None:
            assert err(e, truth(M0, pose(k, n, zoom1=1.2, pan=300))) < 3.0, f"frame {k}"

    # (b) a translating camera: the floor slides 6 px per frame relative to the background (parallax).
    # The background is the larger plane, so the tracker's natural lock is the *wrong* one for the court.
    tr2 = CameraTracker(verify_every=1)
    tr2.set_reference(render_two_planes(fw, bw, M0, M0), floor=FLOOR_POLY)
    frames, floor_truth = [], []
    for k in range(n):
        P = pose(k, n, zoom1=1.2, pan=300)
        shift = np.array([[1, 0, 0], [0, 1, 6.0 * k], [0, 0, 1]])
        frames.append(render_two_planes(fw, bw, shift @ P, P))
        floor_truth.append(truth(M0, shift @ P))
    est2 = tr2.track(frames, [False] * n, 0)
    assert est2[2] is not None, "before the planes have separated the pose is still good"
    assert all(e is None for e in est2[30:]), "once the floor has slid away the background pose is refused"
    for e, g in zip(est2, floor_truth, strict=True):  # and nothing that *is* accepted may misplace the floor
        assert e is None or err(e, g) < 12.0  # within the verifier tolerance (~1% of the frame width)


def test_close_up_with_no_floor_in_view_is_not_registered() -> None:
    fw, bw = floor_world(), make_world(8)
    M0 = pose(0, 60)
    tr = CameraTracker()
    tr.set_reference(render_two_planes(fw, bw, M0, M0), floor=FLOOR_POLY)
    # zoom 3x onto the background: the floor region has left the frame, nothing to verify against
    Mz = pose(0, 60, zoom1=1.0)
    Mz = np.array([[3, 0, -W], [0, 3, -H * 1.9], [0, 0, 1.0]]) @ Mz
    frames = [cv2.warpPerspective(bw, Mz, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)] * 12
    assert all(e is None for e in tr.track(frames, [True] + [False] * 11, 0))
