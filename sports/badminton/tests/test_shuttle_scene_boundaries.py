"""Shuttle postprocessing must respect the perception stream's scene boundaries."""

from pathlib import Path

import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.perception_types import ChunkPerception, FramePerception
from bai_engine.store import EventStore


def _window(tmp_path: Path, boundary: str):  # type: ignore[no-untyped-def]
    engine = BadmintonMatchEngine(
        "S1",
        EngineConfig(fps=30, frame_width=1280, frame_height=720),
        EventStore(tmp_path / "scene.sqlite", "S1"),
    )
    for frame in range(10):
        point = None if frame in (4, 5) else (float(frame * 10), 100.0)
        engine._append(
            FramePerception(
                frame_idx=frame,
                shuttle_xy=point,
                shuttle_conf=0.9 if point is not None else 0.0,
                shot_id=int(boundary == "shot" and frame >= 5),
                replay=boundary == "replay" and frame >= 5,
            )
        )
    return engine._window(0, 9)


@pytest.mark.parametrize("boundary", ["shot", "replay"])
def test_gap_across_scene_boundary_is_not_reconstructed(tmp_path: Path, boundary: str) -> None:
    window = _window(tmp_path, boundary)
    track = window.shuttle
    assert window.break_before.tolist() == [False, False, False, False, False, True, False, False, False, False]
    assert not track.vis[4:6].any()
    assert not track.interp[4:6].any()
    assert track.vis[3] and track.vis[6]
    assert track.x[3] == 30 and track.x[6] == 60


def test_gap_within_one_scene_retains_existing_reconstruction(tmp_path: Path) -> None:
    track = _window(tmp_path, "none").shuttle
    assert track.vis[4:6].all()
    assert track.interp[4:6].all()


def test_camera_cut_jump_cannot_start_rally_by_itself(tmp_path: Path) -> None:
    seen = []
    engine = BadmintonMatchEngine(
        "S1",
        EngineConfig(fps=30, frame_width=1280, frame_height=720),
        EventStore(tmp_path / "cut-motion.sqlite", "S1"),
        emit=seen.extend,
    )
    positions = [10.0, 10.0, 10.0, 10.0, 500.0, 510.0, 520.0, 520.0, 520.0, 520.0]
    frames = [
        FramePerception(
            frame_idx=i,
            shuttle_xy=(x, 100.0),
            shuttle_conf=0.9,
            shot_id=int(i >= 4),
        )
        for i, x in enumerate(positions)
    ]
    engine.ingest(ChunkPerception(start=0, end=len(frames) - 1, frames=frames))
    engine.flush()
    assert not any(event.type == "rally_start" for event in seen)
