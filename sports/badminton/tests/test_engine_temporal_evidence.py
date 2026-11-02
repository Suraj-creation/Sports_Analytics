"""Integration regressions for observation provenance and event context."""

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.events.contact import ContactCandidate
from bai_badminton.perception_types import ChunkPerception, FramePerception
from bai_engine.store import EventStore


def _engine(tmp_path, seen=None):
    store = EventStore(tmp_path / "events.sqlite", "S1")
    engine = BadmintonMatchEngine(
        "S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store,
        emit=seen.extend if seen is not None else None,
    )
    return engine, store


def _frames(n, *, missing=(), cut=None):
    return [
        FramePerception(
            frame_idx=i,
            shuttle_xy=None if i in missing else (float(i * 10), 200.0),
            shuttle_conf=0.0 if i in missing else 0.9,
            shot_id=int(cut is not None and i >= cut),
        )
        for i in range(n)
    ]


def test_reconstructed_motion_cannot_start_an_exchange(tmp_path):
    seen = []
    engine, _ = _engine(tmp_path, seen)
    frames = _frames(12, missing=range(2, 6))
    for frame in frames[8:]:
        frame.shuttle_xy = (70.0, 200.0)
    engine.ingest(ChunkPerception(0, 11, frames))
    assert engine._window(0, 11).shuttle.interp[2:6].all()
    engine.flush()
    assert not any(event.type == "rally_start" for event in seen)


def test_bounded_reconstruction_cannot_keep_an_exchange_alive_through_long_loss(tmp_path):
    engine, store = _engine(tmp_path)
    frames = _frames(165, missing=range(70, 94))
    engine.ingest(ChunkPerception(0, 164, frames))
    assert engine._window(0, 164).shuttle.interp[70:94].all()
    engine.flush()
    rallies = store.query(types=["rally_end"])
    assert len(rallies) == 2
    assert rallies[0].frame_end < 70


def test_post_contact_kinematics_stop_at_recorded_cut(tmp_path):
    engine, _ = _engine(tmp_path)
    engine.ingest(ChunkPerception(0, 9, _frames(10, cut=3)))
    assert engine._post_contact_kinematics(0) == (None, None)


def test_next_contact_in_another_scene_is_not_a_flight_or_receiver(tmp_path):
    engine, store = _engine(tmp_path)
    engine.ingest(ChunkPerception(0, 9, _frames(10, cut=4)))
    window = engine._window(0, 9)
    engine._on_contact(ContactCandidate(0, None, 0.8, shuttle_xy=(0.0, 200.0)), window)
    engine._on_contact(ContactCandidate(6, None, 0.8, shuttle_xy=(60.0, 200.0)), window)
    stroke = store.query(types=["stroke"])[0]
    assert stroke.payload["flight_time_s"] is None
    assert stroke.payload["receiver_id"] is None
    assert "landing_source" not in stroke.payload
