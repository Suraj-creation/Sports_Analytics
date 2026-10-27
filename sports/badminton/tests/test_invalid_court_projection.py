"""Invalid geometry must never produce court-relative player samples."""

import numpy as np
import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.perception_types import FramePerception, PersonObs
from bai_badminton.testing.synth import make_match
from bai_engine.schema import TrackObject
from bai_engine.store import EventStore


@pytest.mark.parametrize("prior", [None, (1.0, -2.0)])
@pytest.mark.parametrize("view,lost", [("none", True), ("alt", False), ("main", True)])
def test_unusable_view_does_not_project_or_retain_court_positions(tmp_path, view, lost, prior):
    match = make_match(["P1"])
    eng = BadmintonMatchEngine(
        "S1", EngineConfig(fps=match.fps, frame_width=1280, frame_height=720), EventStore(tmp_path / "e.sqlite", "S1")
    )
    eng.set_calibration(0, match.homography)
    person = PersonObs(track_id=1, bbox=np.array([500.0, 400.0, 550.0, 650.0]), conf=0.9, court_xy=prior)
    eng._append(
        FramePerception(frame_idx=0, shuttle_xy=None, shuttle_conf=0.0, persons=[person], view=view, cam_lost=lost)
    )
    tracks = [t for t in eng.drain_tracks() if t.obj is TrackObject.PLAYER]
    assert not tracks
    assert eng.identity._track_to_player == {}
    assert person.court_xy == prior  # input observations are not rewritten
    assert all(buf["court"][-1] is None for buf in eng._players.values())


def test_reacquiring_calibration_cannot_project_court_coordinates(tmp_path):
    from bai_badminton.perception.calibration_state import CalibrationState

    match = make_match(["P1"])
    eng = BadmintonMatchEngine(
        "S1",
        EngineConfig(fps=match.fps, frame_width=1280, frame_height=720),
        EventStore(tmp_path / "reacquire.sqlite", "S1"),
    )
    eng.set_calibration(0, match.homography)
    person = PersonObs(track_id=1, bbox=np.array([500.0, 400.0, 550.0, 650.0]), conf=0.9, court_xy=(1.0, -2.0))
    eng._append(
        FramePerception(
            frame_idx=0,
            shuttle_xy=None,
            shuttle_conf=0.0,
            persons=[person],
            calibration_state=CalibrationState.REACQUIRING,
        )
    )
    tracks = [t for t in eng.drain_tracks() if t.obj is TrackObject.PLAYER]
    assert not tracks
    assert eng.identity._track_to_player == {}
    assert all(buf["court"][-1] is None for buf in eng._players.values())


def test_lost_court_cannot_determine_a_winner_even_with_human_match_marker(tmp_path):
    from dataclasses import replace

    from bai_badminton.perception.calibration_state import CalibrationState
    from bai_engine.schema import Provenance

    match = make_match(["P1", "P2"])
    store = EventStore(tmp_path / "lost_rally.sqlite", "S1")
    eng = BadmintonMatchEngine("S1", EngineConfig(fps=match.fps, frame_width=1280, frame_height=720), store)
    eng.set_calibration(0, match.homography)
    eng.set_match_start(0, Provenance(model="human"))
    for chunk in match.chunks:
        eng.ingest(replace(chunk, frames=[replace(f, calibration_state=CalibrationState.LOST) for f in chunk.frames]))
    eng.flush()
    rallies = store.query(types=["rally_end"])
    assert rallies and all(r.payload["winner"] is None for r in rallies)
    assert not store.query(types=["point"])
