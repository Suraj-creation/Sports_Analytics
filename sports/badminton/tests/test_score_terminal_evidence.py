"""A disappearing in-flight shuttle must never manufacture a scored point."""

from dataclasses import replace

from synthetic_support import bind_labelled_synthetic_singles

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.perception_types import ChunkPerception
from bai_badminton.testing.synth import make_rally, to_frames
from bai_engine.schema import Provenance
from bai_engine.store import EventStore


def test_midflight_detection_loss_segments_an_exchange_without_awarding_a_point(tmp_path):
    rally = make_rally(n_shots=10)
    frames = to_frames(rally, 0)
    frames[160:] = [replace(frame, shuttle_xy=None, shuttle_conf=0.0) for frame in frames[160:]]
    with EventStore(tmp_path / "missing-terminal.sqlite", "S1") as store:
        engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
        engine.set_calibration(0, rally.homography)
        engine.set_match_start(0, Provenance(model="human"))
        engine.ingest(ChunkPerception(0, len(frames) - 1, frames))
        engine.flush()
        ends = store.query(types=["rally_end"])
        assert len(ends) == 1 and ends[0].payload["end_reason"] == "gap"
        assert ends[0].payload["winner"] is None
        assert ends[0].payload["rule_check"] == "terminal_not_observed"
        assert not store.query(types=["point"])
        assert engine.public_state()["score"] == {"P1": 0, "P2": 0}


def test_real_observed_stationary_terminal_still_scores_once_on_repeated_flush(tmp_path):
    rally = make_rally()
    frames = to_frames(rally, 0)
    with EventStore(tmp_path / "supported-terminal.sqlite", "S1") as store:
        engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
        bind_labelled_synthetic_singles(engine)
        engine.set_calibration(0, rally.homography)
        engine.set_match_start(0, Provenance(model="human"))
        engine.ingest(ChunkPerception(0, len(frames) - 1, frames))
        engine.flush()
        before = engine.public_state()
        engine.flush()
        assert len(store.query(types=["point"])) == 1
        assert engine.public_state() == before


def test_unmapped_ocr_does_not_inflate_geometric_winner_confidence(tmp_path):
    rally = make_rally()
    frames = to_frames(rally, 0)
    with EventStore(tmp_path / "unmapped-ocr.sqlite", "S1") as store:
        engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
        engine.set_calibration(0, rally.homography)
        engine.set_match_start(0, Provenance(model="human"))
        engine.ocr.winner_from_ocr = lambda *a, **kw: ("P2", "ocr_unmapped")
        engine.ingest(ChunkPerception(0, len(frames) - 1, frames))
        engine.flush()
        end = store.query(types=["rally_end"])[0]
        assert end.confidence <= 0.85
        assert store.query(types=["point"])[0].confidence == end.confidence
