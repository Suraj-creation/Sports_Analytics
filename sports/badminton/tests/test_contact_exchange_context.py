"""Engine source windows retain detector association separately from fresh pose."""

from dataclasses import replace

import numpy as np

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.events.contact import ContactCandidate
from bai_badminton.events.contact_evidence import Reliability
from bai_badminton.participant_contact import ParticipantSnapshot
from bai_badminton.perception_types import ChunkPerception, FramePerception
from bai_badminton.testing.synth import make_rally
from bai_engine.store import EventStore


def test_contact_context_uses_only_current_detector_associations_and_preserves_uncertainty(tmp_path):
    source = make_rally(n_shots=3)
    with EventStore(tmp_path / "events.sqlite", "source-window") as store:
        engine = BadmintonMatchEngine("source-window", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
        engine.set_calibration(0, source.homography, emit=False)
        engine.ingest(ChunkPerception(0, 9, [FramePerception(i, None, 0.0) for i in range(10)]))
        frames = []
        for frame in range(source.obs.n):
            a = ParticipantSnapshot(
                1,
                np.array([100, 100, 200, 300]),
                None,
                (-1, -2),
                "birth-A",
                frame == 5,
                frame == 5,
                pose_frame_idx=frame,
            )
            b = ParticipantSnapshot(
                2, np.array([300, 100, 400, 300]), None, (1, 2), "birth-B", frame == 5, frame == 5, pose_frame_idx=frame
            )
            carried = replace(b, track_id=3, observation_id="birth-carried", detector_matched=False)
            frames.append({"A": a, "B": b, "carried": carried})
        candidate = engine._contact_with_observation_evidence(ContactCandidate(5, "A", 0.6), source.obs, frames)
        context = candidate.evidence.inputs.participant_context
        assert {(row.frame, row.participant_id) for row in context.observations} == {(5, "A"), (5, "B")}
        assert candidate.evidence.impact.reliability is not Reliability.CONFIRMED
        # Coobserved participants alone do not establish a shuttle impact.
        assert candidate.evidence.inputs.review is None
        engine._geometry_valid[5] = False
        candidate = engine._contact_with_observation_evidence(ContactCandidate(5, "A", 0.6), source.obs, frames)
        assert candidate.evidence.inputs.participant_context.observations == ()
