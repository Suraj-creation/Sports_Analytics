"""A moving camera must not change the match: the engine works in the calibration's reference view, so
pushing every observation through a known (changing) camera pose and handing the engine that pose has to
reproduce the static analysis."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.perception.camera import project
from bai_badminton.perception_types import ChunkPerception, PersonObs
from bai_badminton.testing.synth import SynthMatch, make_match
from bai_engine.schema import TrackObject
from bai_engine.store import EventStore

WINNERS = ["P1", "P2", "P2", "P1", "P1", "P1", "P2", "P1"]
CAM_REF = 1234


def pose(i: int, roll: float = 0.0) -> np.ndarray:
    """A slow pan + zoom (+ optional roll) about the frame centre: the camera follows the rally."""
    z = 1.0 + 0.18 * np.sin(i / 260.0)
    tx, ty = 140.0 * np.sin(i / 170.0), 40.0 * np.sin(i / 230.0)
    th = np.deg2rad(roll) * np.sin(i / 300.0)
    c, s = np.cos(th), np.sin(th)
    C = np.array([[1, 0, 640], [0, 1, 360], [0, 0, 1.0]])
    R = np.array([[z * c, -z * s, tx], [z * s, z * c, ty], [0, 0, 1.0]])
    return C @ R @ np.linalg.inv(C)


def move(m: SynthMatch, roll: float = 0.0) -> list[ChunkPerception]:
    out = []
    for ch in m.chunks:
        frames = []
        for fp in ch.frames:
            G = pose(fp.frame_idx, roll)
            persons = []
            for p in fp.persons:
                x1, y1, x2, y2 = p.bbox
                q = project(G, [[x1, y1], [x2, y1], [x2, y2], [x1, y2]])
                kps = p.kps.copy() if p.kps is not None else None
                if kps is not None:
                    kps[:, :2] = project(G, kps[:, :2])
                persons.append(
                    PersonObs(
                        track_id=p.track_id,
                        bbox=np.array([q[:, 0].min(), q[:, 1].min(), q[:, 0].max(), q[:, 1].max()]),
                        conf=p.conf,
                        kps=kps,
                    )
                )
            xy = tuple(project(G, [fp.shuttle_xy])[0]) if fp.shuttle_xy else None
            frames.append(replace(fp, shuttle_xy=xy, persons=persons, cam=G))
        out.append(replace(ch, frames=frames, cam_ref=CAM_REF))
    return out


def run(tmp_path: Path, name: str, chunks: list[ChunkPerception], m: SynthMatch, *, tracked: bool):
    store = EventStore(tmp_path / f"{name}.sqlite", "S1")
    eng = BadmintonMatchEngine("S1", EngineConfig(fps=m.fps, frame_width=1280, frame_height=720), store)
    eng.set_calibration(0, m.homography, cam_ref=CAM_REF if tracked else None)
    tracks = []
    for ch in chunks:
        eng.ingest(ch)
        tracks += eng.drain_tracks()
    eng.flush()
    return eng, store, tracks


@pytest.fixture(scope="module")
def match() -> SynthMatch:
    return make_match(WINNERS)


def test_pan_and_zoom_reproduce_the_static_analysis(tmp_path: Path, match: SynthMatch) -> None:
    _, still, _ = run(tmp_path, "still", match.chunks, match, tracked=False)
    _, moving, _ = run(tmp_path, "moving", move(match), match, tracked=True)
    assert [r.payload["winner"] for r in moving.query(types=["rally_end"])] == WINNERS
    assert len(moving.query(types=["contact"])) == len(still.query(types=["contact"]))
    s0, s1 = still.query(types=["stroke"]), moving.query(types=["stroke"])
    assert len(s0) == len(s1)
    for a, b in zip(sorted(s0, key=lambda e: e.frame_start), sorted(s1, key=lambda e: e.frame_start), strict=True):
        # (a contact scored on a near-tie may land a frame or two apart: float rounding of the pose)
        assert abs(a.frame_start - b.frame_start) <= 3
        # (labels are not compared: the synthetic hitters stand exactly on a classifier threshold, y = -4.9 m,
        # where a 1e-15 difference flips drop/push/short_serve — the *measurements* are what the camera affects)
        assert b.payload["speed_px_s"] == pytest.approx(a.payload["speed_px_s"], rel=0.05, abs=15.0)
        if a.payload["hitter_court_xy"]:
            assert b.payload["hitter_court_xy"] == pytest.approx(a.payload["hitter_court_xy"], abs=0.15)


def test_rolling_camera_still_scores_the_match(tmp_path: Path, match: SynthMatch) -> None:
    _, moving, _ = run(tmp_path, "roll", move(match, roll=4.0), match, tracked=True)
    assert [r.payload["winner"] for r in moving.query(types=["rally_end"])] == WINNERS


def test_untracked_camera_is_what_breaks_the_match(tmp_path: Path, match: SynthMatch) -> None:
    """The bug: the same moving footage with the camera *ignored* (a fixed calibration) misreads it."""
    _, bad, _ = run(tmp_path, "ignored", move(match), match, tracked=False)
    assert [r.payload["winner"] for r in bad.query(types=["rally_end"])] != WINNERS


def test_court_positions_are_in_metres_wherever_the_camera_points(tmp_path: Path, match: SynthMatch) -> None:
    _, _, still_tracks = run(tmp_path, "t0", match.chunks, match, tracked=False)
    _, _, moving_tracks = run(tmp_path, "t1", move(match), match, tracked=True)

    def key(t):
        return (t.frame_idx, t.player_id)

    a = {key(t): t for t in still_tracks if t.obj is TrackObject.PLAYER}
    b = {key(t): t for t in moving_tracks if t.obj is TrackObject.PLAYER}
    assert a.keys() == b.keys()
    for k, t in a.items():
        assert b[k].court_x == pytest.approx(t.court_x, abs=2e-3) and b[k].court_y == pytest.approx(t.court_y, abs=2e-3)
        # …while the *track samples* stay in raw frame pixels (they are drawn on the video)
        assert b[k].bbox != t.bbox or pose(k[0]).tolist() == np.eye(3).tolist()


def test_camera_samples_are_emitted_per_frame_and_events_carry_screen_pixels(tmp_path: Path, match: SynthMatch) -> None:
    _, store, tracks = run(tmp_path, "cam", move(match), match, tracked=True)
    cams = [t for t in tracks if t.obj is TrackObject.CAMERA]
    assert len(cams) == match.n_frames
    assert np.allclose(np.array(cams[500].cam).reshape(3, 3), pose(500))
    moved = {fp.frame_idx: fp.shuttle_xy for ch in move(match) for fp in ch.frames}
    contacts = store.query(types=["contact"])
    assert contacts
    for c in contacts:  # the contact ring is drawn on the video: it must be where the shuttle *appears*
        xy = c.payload["shuttle_xy"]
        near = [moved[f] for f in range(c.frame_start - 2, c.frame_start + 3) if moved.get(f)]
        assert min(np.hypot(xy[0] - p[0], xy[1] - p[1]) for p in near) < 6.0


def test_lost_frames_are_marked_and_never_analysed(tmp_path: Path, match: SynthMatch) -> None:
    chunks = move(match)
    lost = []
    for ch in chunks:  # the camera cuts away for a while: tracked, but the court is not in view
        frames = [
            replace(fp, cam=None, cam_lost=True, replay=True, shuttle_xy=None, persons=[])
            if 300 <= fp.frame_idx < 360
            else fp
            for fp in ch.frames
        ]
        lost.append(replace(ch, frames=frames))
    _, _, tracks = run(tmp_path, "lost", lost, match, tracked=True)
    cams = {t.frame_idx: t for t in tracks if t.obj is TrackObject.CAMERA}
    assert all(not cams[f].visible and cams[f].cam is None for f in range(300, 360))
    assert all(cams[f].visible for f in (299, 360))
