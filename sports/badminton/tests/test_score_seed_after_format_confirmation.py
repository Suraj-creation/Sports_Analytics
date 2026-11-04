"""The first known-format rally anchors scores without authorizing old unknowns."""

import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig, _PendingRally
from bai_badminton.events.match_phase import RallyEvidence
from bai_badminton.events.rally_fsm import RallySegment
from bai_badminton.perception_types import ChunkPerception, FramePerception, ScoreReading
from bai_engine.schema import Provenance
from bai_engine.store import EventStore


@pytest.mark.parametrize("match_format", ["singles", "doubles"])
def test_first_known_format_rally_seeds_from_its_own_prior_board_after_an_unknown_official_rally(
    tmp_path, monkeypatch, match_format,
):
    players = {"P1": "Alice", "P2": "Bob"} if match_format == "singles" else {
        "P1": "Alex Reed / Morgan Chen", "P2": "Robin Singh / Taylor Park",
    }
    names = ("ALICE", "BOB") if match_format == "singles" else (
        "REED A. / CHEN M.", "SINGH R. / PARK T.",
    )
    with EventStore(tmp_path / "format-seed.sqlite", "S1") as store:
        engine = BadmintonMatchEngine(
            "S1", EngineConfig(fps=30, frame_width=1280, frame_height=720, match_format_known=False),
            store, player_names=players,
        )
        monkeypatch.setattr(engine, "_outcome", lambda seg: ("unknown", "unknown", "terminal_not_observed", .2))
        monkeypatch.setattr(engine, "_phase_evidence", lambda seg, until: RallyEvidence(
            calibrated=False, scoreboard=engine.ocr.board_change(seg.start, seg.end, until, 900),
        ))
        engine.set_reviewed_match_intervals([(100, 200), (600, 700)], Provenance(model="human"))
        engine._pending = [_PendingRally(RallySegment(100, 200, None, "stationary"), [], None)]
        engine.ingest(ChunkPerception(0, 450, [FramePerception(i, None, 0.0) for i in range(451)]))
        first = store.query(types=["rally_end"])[0]
        assert first.payload["official"] is True
        assert first.payload["match_format_known"] is False
        assert store.query(types=["point"]) == []

        engine.set_match_format(match_format, 451, Provenance(model="format-fixture"))
        engine._pending = [_PendingRally(RallySegment(600, 700, None, "stationary"), [], None)]
        readings = [
            ScoreReading(frame, ((names[0], points[0]), (names[1], points[1])), conf=.95)
            for frame, points in ((500, (3, 2)), (505, (3, 2)), (800, (4, 2)), (805, (4, 2)))
        ]
        engine.ingest(ChunkPerception(
            451, 900, [FramePerception(i, None, 0.0) for i in range(451, 901)], ocr=readings,
        ))

        points = store.query(types=["point"])
        assert len(points) == 1
        assert points[0].frame_start == 700
        assert points[0].payload["state_before"]["score"] == {"P1": 3, "P2": 2}
        assert engine.state.score == {"P1": 4, "P2": 2}
        rallies = store.query(types=["rally_end"])
        assert rallies[0].payload["match_format_known"] is False
        assert rallies[0].payload["winner"] is None
        assert rallies[1].payload["match_format"] == match_format
        seed = next(event for event in store.query(types=["match_phase"]) if event.payload.get("base_state"))
        assert seed.frame_start == 600
