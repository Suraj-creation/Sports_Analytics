"""Accepted score decisions link directly to reviewable canonical OCR frames.

These fixtures bypass perception quality while exercising source observations,
phase/rule decisions, durable corrections and point publication. Team score
slots in doubles do not imply an individual hitter identity.
"""

import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig, _PendingRally
from bai_badminton.events.match_phase import RallyEvidence
from bai_badminton.events.rally_fsm import RallySegment
from bai_badminton.perception_types import ScoreReading
from bai_badminton.rules import MatchConfig
from bai_badminton.score_ocr import ScoreTransitionRef
from bai_engine.schema import EvidenceKind
from bai_engine.store import EventStore


@pytest.mark.parametrize("discipline", ["singles", "doubles"])
@pytest.mark.parametrize("timing", ["initial", "late"])
def test_score_decisions_expose_canonical_source_frames_for_visual_review(tmp_path, monkeypatch, discipline, timing):
    if discipline == "singles":
        players = {"P1": "Alice", "P2": "Bob"}
        names = ("ALICE", "BOB")
    else:
        players = {"P1": "Alex Reed / Morgan Chen", "P2": "Robin Singh / Taylor Park"}
        names = ("REED A. / CHEN M.", "SINGH R. / PARK T.")
    with EventStore(tmp_path / "visual-score.sqlite", "S1") as store:
        engine = BadmintonMatchEngine(
            "S1", EngineConfig(fps=30, frame_width=1280, frame_height=720, match=MatchConfig(discipline=discipline)),
            store, player_names=players,
        )
        monkeypatch.setattr(engine, "_outcome", lambda seg: ("unknown", "unknown", "terminal_not_observed", .2))
        monkeypatch.setattr(engine, "_phase_evidence", lambda seg, until: RallyEvidence(
            calibrated=False, scoreboard=engine.ocr.board_change(seg.start, seg.end, until, 900),
        ))

        def board(frame, points):
            for offset in (0, 5):
                engine.on_ocr(ScoreReading(frame + offset, ((names[0], points[0]), (names[1], points[1])), conf=.95))

        board(0, (3, 2))
        engine._pending = [_PendingRally(RallySegment(100, 200, None, "stationary"), [], None)]
        original_tracks = ()
        if timing == "late":
            engine._finalize_pending(400)
            assert store.query(types=["point"]) == []
            original = store.query(types=["rally_end"])[0]
            original_tracks = tuple(item for item in original.evidence if item.kind is EvidenceKind.TRACK_WINDOW)
            assert original_tracks
            board(500, (4, 2))
        else:
            board(300, (4, 2))
            engine._finalize_pending(400)

        points = store.query(types=["point"])
        assert len(points) == 1
        point = points[0]
        rally = store.query(types=["rally_end"])[0]
        ref = ScoreTransitionRef.from_public(rally.payload["score_transition"])
        assert ref is not None
        assert ref.after_frames == ((500, 505) if timing == "late" else (300, 305))
        assert rally.payload["winner"] == point.payload["winner"] == "P1"
        assert rally.payload["match_format"] == point.payload["match_format"] == discipline
        assert point.frame_start == point.frame_end == 200
        assert point.parent_id == rally.event_id
        assert all(item in rally.evidence for item in original_tracks)
        assert any(item.kind is EvidenceKind.TRACK_WINDOW for item in rally.evidence)

        # A parent reference or an opaque nested payload alone cannot provide a
        # direct video-navigation target for the supporting broadcast update.
        for decision in (rally, point):
            assert any(
                item.kind is EvidenceKind.SCORE_OCR and item.frames == ref.after_frames
                for item in decision.evidence
            ), f"{decision.type} needs explicit canonical OCR confirmation frames"
        assert any(
            item.kind is EvidenceKind.EVENT and item.event_id == rally.event_id
            for item in point.evidence
        )
