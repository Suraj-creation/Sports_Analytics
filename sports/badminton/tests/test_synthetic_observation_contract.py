"""A controlled perception stream exercises the anonymous production path."""

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.testing.synth import make_match
from bai_engine.store import EventStore


def test_synthetic_observations_reach_contacts_and_classification_without_binding_names(tmp_path):
    match = make_match(["P1"])
    with EventStore(tmp_path / "anonymous.sqlite", "S1") as store:
        engine = BadmintonMatchEngine("S1", EngineConfig(fps=match.fps, frame_width=1280, frame_height=720), store)
        engine.set_calibration(0, match.homography)
        for chunk in match.chunks:
            engine.ingest(chunk)
        engine.flush()
        contacts, strokes = store.query(types=["contact"]), store.query(types=["stroke"])
        assert contacts and strokes
        assert all(event.actors.player_id is None for event in contacts + strokes)
        assert any(
            event.payload.get("classification_context_source") == "provisional_track_episode" for event in strokes
        )
        assert all(event.payload["contact_status"] == "estimated" for event in contacts)
        assert not store.query(types=["point"]), "fixture labels are not production scoring evidence"
