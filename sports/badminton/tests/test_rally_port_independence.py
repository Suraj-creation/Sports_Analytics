"""A compliant replacement segmenter need not inherit baseline FSM internals."""

from bai_badminton.components import RallySegmentation
from bai_badminton.engine import BadmintonMatchEngine, EngineConfig, _PendingRally
from bai_badminton.events.match_phase import RallyEvidence
from bai_badminton.events.rally_fsm import RallyParams, RallySegment, RallyState, RallyUpdate
from bai_badminton.perception_types import ChunkPerception, FramePerception, ScoreReading
from bai_engine.store import EventStore


class IndependentRallyPort:
    __slots__ = ("state", "params", "start", "tentative_end", "closed", "calls", "_owner")

    def __init__(self):
        self.params = RallyParams(fps=30)
        self.calls = 0
        self._owner = object()
        self.reset()

    def reset(self):
        self.state = RallyState.IDLE
        self.start = None
        self.tentative_end = None
        self.closed = None

    def close(self):
        self.reset()

    def checkpoint(self):
        return (self._owner, self.state, self.start, self.tentative_end, self.closed, self.calls)

    def restore(self, checkpoint):
        if not isinstance(checkpoint, tuple) or checkpoint[0] is not self._owner:
            raise ValueError("foreign checkpoint")
        _, self.state, self.start, self.tentative_end, self.closed, self.calls = checkpoint

    def on_contact(self, frame):
        self.calls += 1
        self.start = frame
        self.state = RallyState.IN_PLAY
        return RallyUpdate()

    def step(self, frame, visible, speed, replay=False):
        self.calls += 1
        return RallyUpdate()

    def on_discontinuity(self, frame):
        self.calls += 1
        self.reset()
        return RallyUpdate()

    def flush(self, frame):
        self.calls += 1
        self.reset()
        return RallyUpdate()


def test_independent_rally_port_runs_ingest_and_late_scoring_using_only_declared_contract(tmp_path, monkeypatch):
    provider = IndependentRallyPort()
    assert isinstance(provider, RallySegmentation)
    with EventStore(tmp_path / "independent-rally.sqlite", "S1") as store:
        engine = BadmintonMatchEngine(
            "S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store,
            player_names={"P1": "Alice", "P2": "Bob"}, rally_segmenter=provider,
        )
        monkeypatch.setattr(engine, "_outcome", lambda seg: ("unknown", "unknown", "terminal_not_observed", .2))
        monkeypatch.setattr(engine, "_phase_evidence", lambda seg, until: RallyEvidence(
            calibrated=False, scoreboard=engine.ocr.board_change(seg.start, seg.end, until, 900),
        ))
        for frame in (0, 5):
            engine.on_ocr(ScoreReading(frame, (("ALICE", 3), ("BOB", 2)), conf=.95))
        engine.ingest(ChunkPerception(0, 450, [FramePerception(i, None, 0.0) for i in range(451)]))
        assert engine.fsm is provider
        assert provider.calls > 0
        engine._pending = [_PendingRally(RallySegment(100, 200, None, "stationary"), [], None)]
        engine._finalize_pending(450)
        assert store.query(types=["point"]) == []
        for frame in (500, 505):
            engine.on_ocr(ScoreReading(frame, (("ALICE", 4), ("BOB", 2)), conf=.95))

        assert len(store.query(types=["point"])) == 1
        assert store.query(types=["point"])[0].frame_start == 200
        assert engine.state.score == {"P1": 4, "P2": 2}
        # Lifecycle uses the same opaque checkpoint on the same provider.
        checkpoint = provider.checkpoint()
        provider.on_contact(600)
        provider.restore(checkpoint)
        assert provider.state is RallyState.IDLE
