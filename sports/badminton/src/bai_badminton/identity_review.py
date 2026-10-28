"""Human-reviewed, epoch-scoped identity associations, not tracking decisions.

This ledger is deliberately not consumed by shot attribution or match scoring.
A review explicitly covers a finite interval; it does not join track epochs or
turn automatic re-identification suggestions into identity assertions.
"""

from __future__ import annotations

import re
from collections.abc import Collection

from bai_engine.schema import Actors, Event, EventStatus, Evidence, EvidenceKind, Provenance
from bai_engine.store import EventStore
from bai_engine.timeline import Timeline

TRACKER_IDENTITY_EVIDENCE_TYPES = frozenset(
    {
        "identity_review",
        "identity_ambiguity",
        "participant_observation",
        "doubles_team_hypothesis",
        "stroke_participant_review",
    }
)


class IdentityReviewLedger:
    def __init__(self, store: EventStore, player_ids: Collection[str], *, max_frame: int, fps: float | str) -> None:
        self.store = store
        self.player_ids = frozenset(player_ids)
        self.max_frame = max_frame
        self.timeline = Timeline.from_rate(fps, max_frame + 1)

    def _reviews(self) -> list[Event]:
        return [
            e
            for e in self.store.query(types=["identity_review"])
            if e.status == EventStatus.HUMAN_VERIFIED and e.provenance.model == "human"
        ]

    def current(self) -> list[Event]:
        observations = {e.event_id: e for e in self.store.query(types=["participant_observation"])}
        return [
            e
            for e in self._reviews()
            if (obs := observations.get(e.payload.get("observation_id"))) is not None
            and self._episode_error(obs, e.frame_end) is None
        ]

    def _episode_error(self, obs: Event, end: int) -> str | None:
        participant = obs.payload.get("participant_id")
        track = obs.payload.get("track_id")
        match = (
            re.fullmatch(r"participant-([A-Za-z0-9]+)-[0-9]{6}", participant) if isinstance(participant, str) else None
        )
        if not match:
            return "invalid participant observation"
        epoch = match.group(1)
        for other in self.store.query(types=["identity_ambiguity", "participant_observation"]):
            if other.event_id == obs.event_id or not obs.frame_start <= other.frame_start <= end:
                continue
            if other.frame_start == obs.frame_start:
                # Two births using the same tracker ID at one frame are ambiguous,
                # independent of append order. For reset/exit, event order matters.
                if (
                    other.type == "participant_observation"
                    and other.payload.get("kind") in ("PARTICIPANT_FIRST_OBSERVED", "PLAYER_ENTERED")
                    and other.payload.get("track_id") == track
                    and other.payload.get("participant_id") != participant
                ):
                    return "interval crosses track reuse"
                if other.seq is not None and obs.seq is not None and other.seq < obs.seq:
                    continue
            if other.type == "identity_ambiguity":
                reason = other.payload.get("reason")
                if reason in (
                    "visual_tracker_reset",
                    "calibration_changed",
                    "prolonged_coverage_loss",
                ) or other.payload.get("tracker_instance") not in (None, epoch):
                    return "interval crosses tracker epoch"
            elif other.payload.get("kind") == "PLAYER_EXITED" and other.payload.get("participant_id") == participant:
                return "interval crosses participant exit"
            elif (
                other.payload.get("kind") in ("PARTICIPANT_FIRST_OBSERVED", "PLAYER_ENTERED")
                and other.payload.get("track_id") == track
                and other.payload.get("participant_id") != participant
            ):
                return "interval crosses track reuse"
        return None

    def confirm(self, observation_id: str, player_id: str, start: int, end: int) -> Event:
        if player_id not in self.player_ids:
            raise ValueError("unknown session player")
        if isinstance(start, bool) or isinstance(end, bool) or not isinstance(start, int) or not isinstance(end, int):
            raise ValueError("invalid interval")
        if start < 0 or end < start or end > self.max_frame:
            raise ValueError("invalid interval")
        observations = self.store.query(types=["participant_observation"])
        obs = next((event for event in observations if event.event_id == observation_id), None)
        if (
            obs is None
            or obs.type != "participant_observation"
            or obs.status != EventStatus.PROVISIONAL
            or obs.provenance.model != "participant_tracker_v1"
            or obs.payload.get("kind") not in ("PARTICIPANT_FIRST_OBSERVED", "PLAYER_ENTERED")
        ):
            raise ValueError("invalid participant observation")
        participant = obs.payload.get("participant_id")
        track = obs.payload.get("track_id")
        match = (
            re.fullmatch(r"participant-([A-Za-z0-9]+)-[0-9]{6}", participant) if isinstance(participant, str) else None
        )
        if not match or isinstance(track, bool) or not isinstance(track, int) or track < 0 or start < obs.frame_start:
            raise ValueError("invalid participant observation or interval")
        epoch = match.group(1)
        error = self._episode_error(obs, end)
        if error:
            raise ValueError(error)
        for review in self.current():
            if (
                start <= review.frame_end
                and review.frame_start <= end
                and (
                    review.actors.player_id == player_id
                    or review.payload.get("participant_id") == participant
                    or (review.payload.get("tracker_instance") == epoch and review.actors.track_id == track)
                )
            ):
                raise ValueError("overlapping identity review")
        return self.store.append(
            Event(
                session_id=self.store.session_id,
                type="identity_review",
                frame_start=start,
                frame_end=end,
                pts_us=self.timeline.frame_to_pts_us(start),
                actors=Actors(player_id=player_id, track_id=track),
                payload={
                    "participant_id": participant,
                    "tracker_instance": epoch,
                    "observation_id": observation_id,
                    "scope": "reviewed_interval",
                    "applied_to_attribution": False,
                },
                status=EventStatus.HUMAN_VERIFIED,
                provenance=Provenance(model="human", worker="review-ui"),
                evidence=(Evidence(kind=EvidenceKind.EVENT, event_id=observation_id),),
            )
        )

    def revoke(self, event_id: str) -> Event:
        review = next((e for e in self._reviews() if e.event_id == event_id), None)
        if review is None:
            raise ValueError("unknown current identity review")
        return self.store.append(
            review.retract(Provenance(model="human", worker="review-ui"), "identity review revoked")
        )
