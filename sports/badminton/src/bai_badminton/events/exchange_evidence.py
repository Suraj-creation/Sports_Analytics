"""Observed anonymous episode separation for optional short exchange admission.

Different track keys alone do not prove different physical people. A witness
requires simultaneous fresh detector matches on opposite court halves, stable
birth/track provenance and a shared retained temporal/coordinate epoch. This
asserts activity separation, never a named person, team, winner or service.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class ContactParticipantObservation:
    frame: int
    participant_id: str
    observation_id: str
    track_id: int
    court_y: float

    def __post_init__(self) -> None:
        if (
            type(self.frame) is not int
            or self.frame < 0
            or type(self.track_id) is not int
            or self.track_id < 0
            or not self.participant_id
            or not self.observation_id
            or not isfinite(self.court_y)
        ):
            raise ValueError("participant witness requires observed episode/track/court provenance")


@dataclass(frozen=True, slots=True)
class ContactParticipantContext:
    shot_id: int
    content_epoch: int
    coordinate_epoch: int
    observations: tuple[ContactParticipantObservation, ...]

    def __post_init__(self) -> None:
        if (
            any(type(v) is not int or v < 0 for v in (self.shot_id, self.content_epoch, self.coordinate_epoch))
            or not isinstance(self.observations, tuple)
            or len(self.observations) > 256
            or any(not isinstance(v, ContactParticipantObservation) for v in self.observations)
        ):
            raise ValueError("participant context requires bounded typed observations and retained epochs")
        keys = [(v.frame, v.participant_id) for v in self.observations]
        if len(set(keys)) != len(keys):
            raise ValueError("duplicate participant observation at one source frame")


def simultaneous_opponents(
    first: ContactParticipantContext | None,
    first_target: str | None,
    second: ContactParticipantContext | None,
    second_target: str | None,
) -> dict | None:
    """Both source windows must independently observe the same opposite episodes."""
    if (
        first is None
        or second is None
        or first_target is None
        or second_target is None
        or first_target == second_target
        or (first.shot_id, first.content_epoch, first.coordinate_epoch)
        != (second.shot_id, second.content_epoch, second.coordinate_epoch)
    ):
        return None

    def pairs(context):
        frames: dict[int, dict[str, ContactParticipantObservation]] = {}
        for value in context.observations:
            frames.setdefault(value.frame, {})[value.participant_id] = value
        result = []
        for frame, observations in sorted(frames.items()):
            a, b = observations.get(first_target), observations.get(second_target)
            if (
                a is not None
                and b is not None
                and a.track_id != b.track_id
                and a.observation_id != b.observation_id
                and a.court_y * b.court_y < 0
            ):
                result.append((frame, a, b))
        return result

    for f, a, b in pairs(first):
        for g, c, d in pairs(second):
            if (a.observation_id, a.track_id, b.observation_id, b.track_id) == (
                c.observation_id,
                c.track_id,
                d.observation_id,
                d.track_id,
            ):
                return {
                    "epoch": [first.shot_id, first.content_epoch, first.coordinate_epoch],
                    "coobserved_frames": [f, g],
                    "episode_ids": [first_target, second_target],
                    "birth_observation_ids": [a.observation_id, b.observation_id],
                    "track_ids": [a.track_id, b.track_id],
                    "semantics": "simultaneous observed opposite-court episodes; identity/team unverified",
                }
    return None
