"""Identity resets retain the selected independent nested team implementation."""

import pytest

from bai_badminton.components import IdentityInference, NamedIdentity, ParticipantIdentity, TeamIdentity
from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.participation import ParticipantFrame
from bai_badminton.perception_types import ChunkPerception, FramePerception
from bai_badminton.rules import MatchConfig
from bai_badminton.teams import DoublesTeamEstimate
from bai_badminton.testing.synth import make_rally
from bai_engine.store import EventStore


class IndependentNames:
    __slots__ = ("net_image_y",)

    def __init__(self):
        self.net_image_y = None

    def assign(self, persons, ends, frame=None):
        return {}


class IndependentParticipants:
    __slots__ = ("instance_id",)

    def __init__(self, instance_id):
        self.instance_id = instance_id

    def update(self, frame_idx, persons, *, coverage_valid, absence_valid):
        return ParticipantFrame(frame_idx=frame_idx, tracker_instance=self.instance_id)


class IndependentTeams:
    __slots__ = ("generation", "frames")

    def __init__(self, generation):
        self.generation = generation
        self.frames = []

    def update(self, frame, *, court_valid, active_play_evidence):
        self.frames.append(frame.frame_idx)
        return DoublesTeamEstimate(
            frame_idx=frame.frame_idx, status="unknown", basis=f"independent-team-{self.generation}",
        )


class IndependentIdentityFactory:
    def __init__(self):
        self.teams = []

    def named_resolver(self):
        return IndependentNames()

    def participant_tracker(self, instance_id):
        return IndependentParticipants(instance_id)

    def team_tracker(self):
        tracker = IndependentTeams(len(self.teams) + 1)
        self.teams.append(tracker)
        return tracker


@pytest.mark.parametrize("boundary", ["calibration", "visual_reset", "coverage_gap"])
def test_identity_epoch_reset_preserves_independent_selected_team_behavior(tmp_path, boundary):
    provider = IndependentIdentityFactory()
    assert isinstance(provider, IdentityInference)
    assert isinstance(provider.named_resolver(), NamedIdentity)
    assert isinstance(provider.participant_tracker("controlled"), ParticipantIdentity)
    with EventStore(tmp_path / "identity-epoch.sqlite", "S1") as store:
        engine = BadmintonMatchEngine(
            "S1", EngineConfig(fps=30, frame_width=1280, frame_height=720, match=MatchConfig(discipline="doubles")),
            store, identity_provider=provider,
        )
        assert isinstance(engine.doubles_teams, TeamIdentity)
        engine.set_calibration(0, make_rally().homography)
        first = FramePerception(0, None, 0.0, detector_observed=True)
        engine.ingest(ChunkPerception(0, 0, [first], models={"player_detector": "controlled-detector@1"}))
        assert provider.teams[0].frames == [0]
        target = 1
        if boundary == "coverage_gap":
            engine.ingest(ChunkPerception(
                1, 65, [FramePerception(i, None, 0.0, detector_observed=False) for i in range(1, 66)],
            ))
            target = 66
        elif boundary == "calibration":
            engine.set_camera_reference(7)

        # A previous provisional hypothesis must close using this provider's
        # explicit unknown output, rather than a replacement baseline solver.
        engine._current_team_key = (("prior-team", ("prior-a", "prior-b"), "near"),)
        frame = FramePerception(target, None, 0.0, detector_observed=True,
                                shot_id=1 if boundary == "visual_reset" else 0)
        engine.ingest(ChunkPerception(target, target, [frame], cam_ref=7 if boundary == "calibration" else None))

        assert len(provider.teams) == 2
        assert provider.teams[-1].frames == [target]
        assert engine.doubles_teams is provider.teams[-1]
        event = store.query(types=["doubles_team_hypothesis"])[-1]
        assert event.frame_start == target
        assert event.payload["status"] == "unknown"
        assert event.payload["basis"] == "independent-team-2"
        assert store.query(types=["identity_ambiguity"])[-1].frame_start == target
