from pathlib import Path

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.testing.synth import make_match
from bai_engine.schema import Provenance
from bai_engine.store import EventStore


def test_reviewed_interval_is_bounded_and_survives_restore(tmp_path: Path):
    m = make_match(["P1", "P2"])
    store = EventStore(tmp_path / "review.sqlite", "S1")
    cfg = EngineConfig(fps=m.fps, frame_width=1280, frame_height=720)
    engine = BadmintonMatchEngine("S1", cfg, store)
    engine.set_calibration(0, m.homography)
    for chunk in m.chunks:
        engine.ingest(chunk)
    engine.flush()
    rallies = store.query(types=["rally_end"])
    assert len(rallies) == 2 and not any(r.payload["official"] for r in rallies)
    human = Provenance(model="human")
    interval = [(rallies[0].frame_start, rallies[0].frame_end)]
    engine.set_reviewed_match_intervals(interval, human)
    revised = store.query(types=["rally_end"])
    assert [r.payload["official"] for r in revised] == [True, False]
    restored = BadmintonMatchEngine("S1", cfg, store)
    restored.restore_from_log(engine._last_frame)
    assert restored.phase.reviewed_intervals == tuple(interval)
    restored.set_rally_official(revised[1].event_id, True, human)
    assert [r.payload["official"] for r in store.query(types=["rally_end"])] == [True, True]
