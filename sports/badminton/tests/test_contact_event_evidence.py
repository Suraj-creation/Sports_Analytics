from pathlib import Path

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.events.contact import ContactCandidate
from bai_badminton.testing.synth import make_rally
from bai_engine.store import EventStore


def test_unresolved_attribution_reason_reaches_contact_and_stroke(tmp_path: Path) -> None:
    store = EventStore(tmp_path / "events.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
    candidate = ContactCandidate(frame=10, player_id=None, p=0.6, attribution_reason="ambiguous_proximity")
    engine._on_contact(candidate, make_rally(n_shots=3).obs)
    contact = store.query(types=["contact"])[0]
    assert contact.actors.player_id is None
    assert contact.payload["attribution_reason"] == "ambiguous_proximity"
    assert contact.payload["attribution_policy"] == "relative_proximity_gap_v1"
    engine._classify(engine._open_contacts[-1], next_frame=20, is_serve=False, receiver=None)
    stroke = store.query(types=["stroke"])[0]
    assert stroke.actors.player_id is None
    assert stroke.payload["attribution_reason"] == "ambiguous_proximity"
    assert stroke.payload["attribution_policy"] == "relative_proximity_gap_v1"
