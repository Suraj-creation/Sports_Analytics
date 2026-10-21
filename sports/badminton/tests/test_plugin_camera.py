"""The plugin glue around camera tracking: a calibration names the frame it was made on, the camera is tracked
from it, the pose rides along with each frame (and through the perception cache), tracking resumes after a
restart, a cached chunk made against another reference is recognised as stale, and a cut to another camera
is "no court"."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest
from test_camera import H, W, err, make_world, pose, truth

from bai_badminton.court import REFERENCE_POINTS
from bai_badminton.plugin import BadmintonSession, StaleCacheError
from bai_engine.config import Profile
from bai_engine.decode import DecodedChunk
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.schema import MediaInfo, Session, Source, SourceKind
from bai_engine.store import EventStore

REPO_ROOT = Path(__file__).resolve().parents[3]
N = 120
FLOOR_TOP = 470  # rows below this show the (green, lined) floor in the synthetic scene
PROFILE = Profile.model_validate(
    {
        "name": "t",
        "shuttle": {"model": "none", "backend": "none"},
        "player_detector": {"model": "none", "backend": "none"},
        "pose": {"model": "none", "backend": "none"},
        "stroke": {"model": "none", "backend": "none"},
    }
)
# the court as clicked on the reference frame (inside the floor region of the scene)
CLICKS = {
    "far_left": (420.0, 520.0),
    "far_right": (860.0, 520.0),
    "near_right": (1130.0, 712.0),
    "near_left": (150.0, 712.0),
}


@pytest.fixture(scope="module")
def worlds() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(5)
    floor = np.full((2000, 3600, 3), (70, 150, 80), np.uint8)
    floor = cv2.add(floor, rng.integers(0, 6, floor.shape, dtype=np.uint8))
    for _ in range(60):
        x, y, n = int(rng.integers(0, 3300)), int(rng.integers(0, 1900)), int(rng.integers(250, 800))
        if rng.random() < 0.5:
            cv2.line(floor, (x, y), (min(x + n, 3599), y), (255, 255, 255), 5)
        else:
            cv2.line(floor, (x, y), (x, min(y + n, 1999)), (255, 255, 255), 5)
    for _ in range(40):
        cv2.putText(
            floor, "ODENSE", (int(rng.integers(0, 3300)), int(rng.integers(60, 2000))), 0, 2.2, (240, 240, 240), 4
        )
    return cv2.GaussianBlur(floor, (0, 0), 1.0), make_world(8)


def scene(worlds: tuple[np.ndarray, np.ndarray], k: int) -> np.ndarray:
    floor, bg = worlds
    M = pose(k, N, zoom1=1.25, pan=350, roll_deg=2.0)
    f = cv2.warpPerspective(bg, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    fl = cv2.warpPerspective(floor, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    f[FLOOR_TOP:] = fl[FLOOR_TOP:]
    return f


def make_session(tmp_path: Path, worlds: tuple[np.ndarray, np.ndarray]) -> tuple[BadmintonSession, EventStore]:
    media = MediaInfo(fps_num=25, fps_den=1, n_frames=N, width=W, height=H, duration_us=int(N / 25 * 1e6))
    sess = Session(
        title="t",
        source=Source(kind=SourceKind.UPLOAD, uri="x.mp4", original_name="x.mp4", sha256="0" * 64),
        media=media,
    )
    store = EventStore(tmp_path / "e.sqlite", sess.session_id)
    return open_session(sess, store, tmp_path, worlds), store


def open_session(
    sess: Session, store: EventStore, tmp_path: Path, worlds: tuple[np.ndarray, np.ndarray]
) -> BadmintonSession:
    s = BadmintonSession(sess, store, PROFILE, ModelRegistry(REPO_ROOT / "models"), lambda evs: None)
    s.attach_frames(lambda idx: scene(worlds, idx), tmp_path / "session")
    return s


def calibrate(s: BadmintonSession, frame: int = 0) -> dict:
    return s.handle({"cmd": "calibrate", "points": CLICKS, "frame": frame})


def chunk(worlds: tuple[np.ndarray, np.ndarray], a: int, b: int) -> DecodedChunk:
    return DecodedChunk(start=a, frames=[scene(worlds, k) for k in range(a, b)])


def test_calibration_names_its_frame_and_tracking_starts(tmp_path: Path, worlds) -> None:  # type: ignore[no-untyped-def]
    s, store = make_session(tmp_path, worlds)
    reply = calibrate(s, frame=0)
    assert reply["ok"] and reply["camera_tracking"] is True
    cal = store.query(types=["calibration"])[-1].payload
    assert cal["source"] == "human" and cal["ref_frame"] == 0 and cal["cam_ref"] == s.perception.camera.ref_id
    assert (tmp_path / "session" / "camera_ref.png").exists()


def test_every_frame_carries_the_pose_of_the_camera(tmp_path: Path, worlds) -> None:  # type: ignore[no-untyped-def]
    s, _ = make_session(tmp_path, worlds)
    calibrate(s)
    M0 = pose(0, N, zoom1=1.25, pan=350, roll_deg=2.0)
    got = []
    for a in (0, 60):
        p = s.perceive(chunk(worlds, a, a + 60))
        assert p.cam_ref == s.perception.camera.ref_id
        got += p.frames
    truth_at = lambda k: truth(M0, pose(k, N, zoom1=1.25, pan=350, roll_deg=2.0))  # noqa: E731
    # while the court is in view (the first ~75 frames) every frame carries an accurate pose …
    assert all(fp.cam is not None and not fp.replay and not fp.cam_lost for fp in got[:75])
    for k in (0, 25, 50, 74):
        assert err(got[k].cam, truth_at(k)) < 4.0, k
    # … later the camera tilts until the court has slid out of the bottom of the frame: those frames are
    # honestly "no court" — and whatever *is* reported is never wrong
    assert any(fp.cam is None and fp.cam_lost and fp.replay for fp in got[75:])
    for k, fp in enumerate(got):
        assert fp.cam is None or err(fp.cam, truth_at(k)) < 6.0, k


def test_the_pose_survives_the_perception_cache(tmp_path: Path, worlds) -> None:  # type: ignore[no-untyped-def]
    s, _ = make_session(tmp_path, worlds)
    calibrate(s)
    p = s.perceive(chunk(worlds, 0, 30))
    q = s.decode_perception(s.encode_perception(p))
    assert q.cam_ref == p.cam_ref
    assert all(np.allclose(a.cam, b.cam) for a, b in zip(p.frames, q.frames, strict=True))
    assert [f.cam_lost for f in q.frames] == [f.cam_lost for f in p.frames]


def test_a_chunk_cached_against_another_reference_is_stale(tmp_path: Path, worlds) -> None:  # type: ignore[no-untyped-def]
    s, _ = make_session(tmp_path, worlds)
    calibrate(s, frame=0)
    old = s.encode_perception(s.perceive(chunk(worlds, 0, 30)))
    calibrate(s, frame=40)  # recalibrated on a different frame: a new reference view
    with pytest.raises(StaleCacheError):
        s.decode_perception(old)


def test_tracking_resumes_after_a_restart(tmp_path: Path, worlds) -> None:  # type: ignore[no-untyped-def]
    s, store = make_session(tmp_path, worlds)
    calibrate(s)
    ref = s.perception.camera.ref_id
    sess = s.session
    del s
    again = open_session(sess, store, tmp_path, worlds)  # new process, same log and session directory
    assert again.perception.camera.ref_id == ref and again.engine._cam_ref == ref
    p = again.perceive(chunk(worlds, 40, 70))  # out of order: no chain from before the restart, it must re-acquire
    assert p.cam_ref == ref and all(fp.cam is not None for fp in p.frames)


def test_an_untracked_calibration_does_not_reuse_an_old_reference(tmp_path: Path, worlds) -> None:  # type: ignore[no-untyped-def]
    s, store = make_session(tmp_path, worlds)
    calibrate(s)
    s.handle({"cmd": "calibrate", "points": CLICKS})  # no frame named: nothing to track against
    assert not (tmp_path / "session" / "camera_ref.png").exists()
    sess = s.session
    again = open_session(sess, store, tmp_path, worlds)
    assert not again.perception.camera.ready


def test_a_cut_to_another_camera_is_no_court(tmp_path: Path, worlds) -> None:  # type: ignore[no-untyped-def]
    s, _ = make_session(tmp_path, worlds)
    calibrate(s)
    other = make_world(99)
    frames = [scene(worlds, k) for k in range(30)] + [
        cv2.warpPerspective(other, pose(k, N), (W, H), borderMode=cv2.BORDER_REFLECT) for k in range(30, 50)
    ]
    p = s.perceive(DecodedChunk(start=0, frames=frames))
    assert all(fp.cam is not None for fp in p.frames[:30])
    after = p.frames[32:]
    assert all(fp.cam is None and fp.cam_lost and fp.replay for fp in after)


def test_reference_points_are_the_ones_the_api_validates() -> None:
    assert set(CLICKS) <= set(REFERENCE_POINTS)
