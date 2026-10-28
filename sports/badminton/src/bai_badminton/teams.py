"""Bounded, non-scoring hypotheses for doubles partnerships.

Two players occupying a court side does not prove a team, match, or user identity.
The tracker exposes only hypotheses and intentionally withholds them when court,
participant, or active-play evidence is insufficient. It does not assign P1/P2.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import isfinite

from bai_badminton.participation import ParticipantFrame


@dataclass(frozen=True)
class TeamHypothesis:
    team_id: str
    members: tuple[str, str]
    side: str
    certainty: str = "hypothesis"


@dataclass(frozen=True)
class DoublesTeamEstimate:
    frame_idx: int
    status: str
    teams: tuple[TeamHypothesis, ...] = ()
    basis: str = "insufficient_evidence"
    supporting_frames: int = 0
    match_intent: str = "unknown"
    version: str = "doubles_team_hypothesis_v1"


def _team_id(members: tuple[str, str]) -> str:
    # Namespaced participant IDs do not imply named users or score ownership.
    digest = sha256("\0".join(members).encode()).hexdigest()[:16]
    return f"team-{digest}"


class DoublesTeamTracker:
    """Infer stable pair candidates from selected-court sides and active-play cues.

    `court_valid` must represent verified geometry, not the image-midline
    fallback. `active_play_evidence` must represent an independent observed
    activity cue, not an assumption that the recording is an official match.
    A provisional team is withheld immediately when evidence is missing, and
    may reappear only after sustained support. Tracker state is constant-size.
    """

    def __init__(self, fps: float, *, sustain_frames: int | None = None, min_confidence: float = 0.5) -> None:
        if fps <= 0 or not 0 <= min_confidence <= 1:
            raise ValueError("invalid team tracker configuration")
        if sustain_frames is None:
            sustain_frames = max(1, round(2 * fps))
        if sustain_frames < 1:
            raise ValueError("sustain_frames must be positive")
        self.sustain_frames = sustain_frames
        self.min_confidence = min_confidence
        self._last_frame: int | None = None
        self._candidate: tuple[tuple[str, str], tuple[str, str]] | None = None
        self._support = 0

    def update(self, frame: ParticipantFrame, *, court_valid: bool, active_play_evidence: bool) -> DoublesTeamEstimate:
        idx = frame.frame_idx
        if idx < 0 or (self._last_frame is not None and idx <= self._last_frame):
            raise ValueError("frame indices must be nonnegative and strictly increasing")
        if self._last_frame is not None and idx != self._last_frame + 1:
            self._candidate, self._support = None, 0
        self._last_frame = idx
        people = frame.participants
        ids = [p.participant_id for p in people]
        tracks = [p.track_id for p in people]
        if (
            not court_valid
            or not active_play_evidence
            or frame.capacity_limited
            or frame.ambiguous_track_ids
            or len(people) != 4
            or len(set(ids)) != 4
            or len(set(tracks)) != 4
            or any(
                not p.participant_id
                or p.track_id < 0
                or p.side not in ("near", "far")
                or not isfinite(p.confidence)
                or not self.min_confidence <= p.confidence <= 1
                for p in people
            )
        ):
            self._candidate, self._support = None, 0
            return DoublesTeamEstimate(idx, "unknown")
        near = sorted(p.participant_id for p in people if p.side == "near")
        far = sorted(p.participant_id for p in people if p.side == "far")
        if len(near) != 2 or len(far) != 2:
            self._candidate, self._support = None, 0
            return DoublesTeamEstimate(idx, "unknown")
        key = ((near[0], near[1]), (far[0], far[1]))
        if key == self._candidate:
            self._support = min(self._support + 1, self.sustain_frames)
        else:
            self._candidate, self._support = key, 1
        if self._support < self.sustain_frames:
            return DoublesTeamEstimate(idx, "candidate", supporting_frames=self._support)
        teams = (TeamHypothesis(_team_id(key[0]), key[0], "near"), TeamHypothesis(_team_id(key[1]), key[1], "far"))
        return DoublesTeamEstimate(
            idx, "provisional", teams, "sustained_cooccurrence_during_active_play", self._support
        )
