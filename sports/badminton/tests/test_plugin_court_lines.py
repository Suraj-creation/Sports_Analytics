"""The plugin with court-line calibration, end to end on a synthetic broadcast.

A video cuts between the main camera (wide, then panning and zooming), a close-up (no court) and a side
camera.  Without any click: the court is calibrated from sampled frames, every frame gets its view
(main / alt / none) and camera, only the main camera's frames are analysed, the court is drawn in every
view that shows it, the scene timeline is recorded, and all of it survives the cache and a restart."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest
from test_court_lines import err

from bai_badminton.court import REFERENCE_POINTS
from bai_badminton.plugin import BadmintonSession, StaleCacheError
from bai_badminton.testing.court_render import MAIN, SIDE, Camera, noise_frame, render
from bai_engine.config import Profile
from bai_engine.decode import DecodedChunk
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.schema import MediaInfo, Session, Source, SourceKind, TrackObject
from bai_engine.store import EventStore

REPO_ROOT = Path(__file__).resolve().parents[3]
W, H = 1280, 720
N = 160
PROFILE = Profile.model_validate(
    {
        "name": "t",
        "shuttle": {"model": "none", "backend": "none"},
        "player_detector": {"model": "none", "backend": "none"},
        "pose": {"model": "none", "backend": "none"},
        "stroke": {"model": "none", "backend": "none"},
    }
)


def camera_at(k: int) -> Camera | None:
    """The shot list: main (still, then a pan + zoom) · close-up · side camera · main again."""
    if k < 40:
        return MAIN
    if k < 70:
        u = k - 40
        return Camera(MAIN.centre, (0.06 * u, 0.08 * u, 0.0), MAIN.f * (1 + 0.02 * u))
    if k < 90:
        return None
    if k < 120:
        return SIDE
    return MAIN


_cache: dict[int, np.ndarray] = {}


def frame(k: int) -> np.ndarray:
    if k not in _cache:
        cam = camera_at(k)
        _cache[k] = noise_frame(k) if cam is None else render(cam, players=[(0.3, -4.0), (-0.8, 4.2)])
    return _cache[k]


def make_session(tmp_path: Path) -> tuple[BadmintonSession, EventStore]:
    media = MediaInfo(fps_num=25, fps_den=1, n_frames=N, width=W, height=H, duration_us=int(N / 25 * 1e6))
    sess = Session(
        title="t",
        source=Source(kind=SourceKind.UPLOAD, uri="x.mp4", original_name="x.mp4", sha256="0" * 64),
        media=media,
    )
    store = EventStore(tmp_path / "e.sqlite", sess.session_id)
    return open_session(sess, store, tmp_path), store


def open_session(sess: Session, store: EventStore, tmp_path: Path) -> BadmintonSession:
    s = BadmintonSession(sess, store, PROFILE, ModelRegistry(REPO_ROOT / "models"), lambda evs: None)
    s.attach_frames(frame, tmp_path / "session")
    return s


def chunk(a: int, b: int) -> DecodedChunk:
    return DecodedChunk(start=a, frames=[frame(k) for k in range(a, b)])


@pytest.fixture(scope="module")
def keyframes() -> list[np.ndarray]:
    return [frame(k) for k in (5, 20, 35, 80, 100, 110, 130, 150)]


def test_the_court_is_calibrated_without_a_click(tmp_path: Path, keyframes: list[np.ndarray]) -> None:
    s, store = make_session(tmp_path)
    s.seed(keyframes)
    cal = store.query(types=["calibration"])[-1]
    p = cal.payload
    assert p["mode"] == "lines" and p["method"] == "court_lines_v1" and p["validity"] == "per_frame"
    assert p["quality"]["precision"] > 0.8 and p["camera"]["centre_m"][1] < -15  # behind the near baseline
    assert p["coverage"] == pytest.approx(7 / 8)  # the close-up has no court
    assert err(np.asarray(p["H"]), MAIN.H) < 2.0  # the main camera (seen most), not the side camera
    assert p["net_top"] is not None and cal.confidence is not None and cal.confidence > 0.8
    assert s.perception.mode == "lines"


def test_every_frame_gets_its_view_and_only_the_main_camera_is_analysed(
    tmp_path: Path, keyframes: list[np.ndarray]
) -> None:
    s, store = make_session(tmp_path)
    s.seed(keyframes)
    frames = []
    for a in range(0, N, 40):
        p = s.perceive(chunk(a, a + 40))
        assert p.cam_ref == s.perception.ref_id
        s.ingest(p)
        frames += p.frames
    s.flush()
    H_ref = np.asarray(store.query(types=["calibration"])[-1].payload["H"])
    for k, fp in enumerate(frames):
        cam = camera_at(k)
        if cam is None:
            assert fp.view == "none" and fp.cam is None and fp.replay, k
            continue
        expected = "alt" if cam is SIDE else "main"
        assert fp.view == expected, (k, fp.view)
        assert fp.replay is (expected != "main")
        assert fp.cam is not None
        # the drawn court (pose · reference calibration) lands on the court in every view that shows it
        assert err(fp.cam @ H_ref, cam.H, symmetric=cam is SIDE) < 5.0, k
    assert {fp.head for fp in frames if fp.view == "main"} == {0}
    assert {fp.head for fp in frames if fp.view == "alt"} == {1}
    scenes = store.query(types=["scene"])
    assert [e.payload["view"] for e in scenes] == ["main", "none", "alt", "main"]
    assert all(e.payload["analysed"] == (e.payload["view"] == "main") for e in scenes)


def test_camera_rows_carry_the_camera_and_the_fit_quality(tmp_path: Path, keyframes: list[np.ndarray]) -> None:
    s, _ = make_session(tmp_path)
    s.seed(keyframes)
    s.perceive(chunk(0, 80))
    p = s.perceive(chunk(80, 130))
    rows = [t for t in s.tracks_from_perception(p) if t.obj is TrackObject.CAMERA]
    assert len(rows) == 50
    by_frame = {t.frame_idx: t for t in rows}
    assert by_frame[85].track_id == -1 and not by_frame[85].visible
    assert by_frame[110].track_id == 1 and by_frame[110].visible and by_frame[110].conf > 0.6
    assert by_frame[125].track_id == 0


def test_scene_survives_the_perception_cache(tmp_path: Path, keyframes: list[np.ndarray]) -> None:
    s, _ = make_session(tmp_path)
    s.seed(keyframes)
    p = s.perceive(chunk(80, 120))
    q = s.decode_perception(s.encode_perception(p))
    assert [(f.view, f.head, f.court_q) for f in q.frames] == [(f.view, f.head, f.court_q) for f in p.frames]
    assert all((a.cam is None) == (b.cam is None) for a, b in zip(p.frames, q.frames, strict=True))


def test_court_line_tracking_resumes_after_a_restart_without_the_reference_image(
    tmp_path: Path, keyframes: list[np.ndarray]
) -> None:
    s, store = make_session(tmp_path)
    s.seed(keyframes)
    ref = s.perception.ref_id
    sess = s.session
    del s
    again = open_session(sess, store, tmp_path)
    assert again.perception.mode == "lines" and again.perception.ref_id == ref and again.engine._cam_ref == ref
    p = again.perceive(chunk(120, 150))
    assert all(fp.view == "main" and fp.cam is not None for fp in p.frames)


def _clicks(offset: np.ndarray | float) -> dict[str, list[float]]:
    names = ("far_left", "far_right", "near_right", "near_left")
    corners = np.array([REFERENCE_POINTS[n] for n in names])
    img = cv2.perspectiveTransform(corners.reshape(-1, 1, 2), MAIN.H).reshape(-1, 2) + offset
    return dict(zip(names, img.tolist(), strict=True))


def test_a_clicked_calibration_is_refined_onto_the_painted_lines(tmp_path: Path) -> None:
    s, store = make_session(tmp_path)
    clicks = _clicks(np.random.default_rng(1).normal(0, 3, (4, 2)))
    reply = s.handle({"cmd": "calibrate", "points": clicks, "frame": 10})
    assert reply["ok"] and reply["mode"] == "lines" and reply["adjusted_px"] is not None
    p = store.query(types=["calibration"])[-1].payload
    assert p["source"] == "human" and p["method"] == "human+court_lines_v1"
    assert err(np.asarray(p["H"]), MAIN.H) < 2.0  # better than the clicks


def test_a_chunk_cached_against_another_calibration_is_stale(tmp_path: Path, keyframes: list[np.ndarray]) -> None:
    s, _ = make_session(tmp_path)
    s.seed(keyframes)
    old = s.encode_perception(s.perceive(chunk(0, 20)))
    s.handle({"cmd": "calibrate", "points": _clicks(1.5), "frame": 20})
    with pytest.raises(StaleCacheError):
        s.decode_perception(old)
