"""Reviewed individual shot totals derived from the canonical official rallies.

Tracking episodes and provisional proximity are evidence, never player identities.
This fold does not mutate event data or infer a person from a court side.
"""

from __future__ import annotations

from typing import Any

from bai_badminton.analytics.rebuild import lineage_ids, rally_records
from bai_badminton.identity_review import IdentityReviewLedger
from bai_engine.schema import Event, EventStatus
from bai_engine.schema.session import ParticipantRoster
from bai_engine.store import EventStore


def machine_hypothesis_unchanged(store: EventStore, event: Any) -> bool:
    """Require current track evidence to match the original machine stroke."""
    current = event.payload.get("participant_hypothesis")
    if not isinstance(current, dict):
        return False
    ancestry = lineage_ids(store, event)
    origin = store.get(ancestry[-1])
    return bool(
        origin is not None
        and origin.supersedes is None
        and origin.type == "stroke"
        and origin.provenance.model
        and origin.provenance.model != "human"
        and origin.frame_start == event.frame_start
        and origin.payload.get("participant_hypothesis") == current
    )


def build_individual_analytics(
    store: EventStore,
    roster: ParticipantRoster | None,
    *,
    max_frame: int,
    fps: float,
    boundary_events: list[Event] | None = None,
) -> dict[str, Any]:
    """Fold current, referenced official strokes; leave all unproven identities unresolved."""
    people = {
        p.participant_id: {
            "name": p.name,
            "team_id": p.team_id,
            "total_shots": 0,
            "shot_distribution": {},
            "event_ids": [],
            "events": [],
            "rally_ids": [],
        }
        for p in (roster.participants if roster else [])
    }
    teams = {t.team_id: {"score_slot": t.score_slot, "attributed_shots": 0} for t in (roster.teams if roster else [])}
    observations = {e.event_id: e for e in store.query(types=["participant_observation"])}
    reviews = (
        IdentityReviewLedger(store, people, max_frame=max_frame, fps=fps).current(boundary_events=boundary_events)
        if roster
        else []
    )
    events = {e.event_id: e for e in store.query(types=["stroke"])}
    scoped_reviews = store.query(types=["stroke_participant_review"])
    official_rally_ids = {
        event.event_id for event in store.query(types=["rally_end"]) if event.payload.get("official") is True
    }
    seen: set[str] = set()
    unresolved: list[str] = []
    legacy = 0
    for rally in rally_records(store):
        if rally.rally_id not in official_rally_ids:
            continue
        for shot in rally.shots:
            event_id = shot.get("event_id")
            if not event_id:
                legacy += 1
                continue
            if event_id in seen:
                continue
            seen.add(event_id)
            event = events.get(event_id)
            hypothesis = event.payload.get("participant_hypothesis") if event else None
            matching = []
            if event and isinstance(hypothesis, dict) and machine_hypothesis_unchanged(store, event):
                episode = hypothesis.get("participant_id")
                track = hypothesis.get("track_id")
                if isinstance(episode, str) and isinstance(track, int) and not isinstance(track, bool) and track >= 0:
                    ancestry = set(lineage_ids(store, event))
                    episode_reviews = []
                    for review in reviews:
                        obs = observations.get(review.payload.get("observation_id"))
                        if (
                            obs
                            and obs.status == EventStatus.PROVISIONAL
                            and obs.provenance.model == "participant_tracker_v1"
                            and obs.payload.get("kind") in ("PARTICIPANT_FIRST_OBSERVED", "PLAYER_ENTERED")
                            and obs.payload.get("participant_id") == episode
                            and obs.payload.get("track_id") == track
                            and hypothesis.get("observation_id") == obs.event_id
                            and review.payload.get("participant_id") == episode
                            and review.actors.track_id == track
                            and review.actors.player_id in people
                            and obs.frame_start
                            <= review.frame_start
                            <= event.frame_start
                            <= review.frame_end
                            <= max_frame
                        ):
                            episode_reviews.append(review)
                    if len(episode_reviews) == 1:
                        identity = episode_reviews[0]
                        for scoped in scoped_reviews:
                            payload = scoped.payload
                            if (
                                scoped.status == EventStatus.HUMAN_VERIFIED
                                and scoped.provenance.model == "human"
                                and scoped.frame_start == event.frame_start == scoped.frame_end
                                and payload.get("scope") == "participant_only"
                                and payload.get("stroke_event_id") in ancestry
                                and payload.get("identity_review_id") == identity.event_id
                                and payload.get("observation_id") == identity.payload.get("observation_id")
                                and payload.get("participant_id") == episode
                                and payload.get("track_id") == track
                                and payload.get("player_id") == identity.actors.player_id
                                and scoped.actors.player_id == identity.actors.player_id
                                and scoped.actors.track_id == track
                            ):
                                matching.append((identity, scoped))
            if len(matching) != 1:
                unresolved.append(event_id)
                continue
            review, scoped_review = matching[0]
            participant = people[review.actors.player_id]
            participant["total_shots"] += 1
            stroke = str(event.payload.get("stroke") or "unknown")
            distribution = participant["shot_distribution"]
            distribution[stroke] = distribution.get(stroke, 0) + 1
            participant["event_ids"].append(event_id)
            participant["events"].append(
                {
                    "event_id": event_id,
                    "frame": event.frame_start,
                    "stroke": stroke,
                    "track_id": hypothesis["track_id"],
                    "review_id": review.event_id,
                    "stroke_participant_review_id": scoped_review.event_id,
                    "rally_id": rally.rally_id,
                }
            )
            if rally.rally_id not in participant["rally_ids"]:
                participant["rally_ids"].append(rally.rally_id)
            if participant["team_id"] in teams:
                teams[participant["team_id"]]["attributed_shots"] += 1
    total = len(seen)
    return {
        "available": roster is not None,
        "match_format": roster.match_format if roster else None,
        "participants": people,
        "teams": teams,
        "accounting": {
            "total_shots": total,
            "attributed_shots": total - len(unresolved),
            "unattributed_shots": len(unresolved),
        },
        "unattributed_event_ids": unresolved,
        "legacy_unlinked_shots": legacy,
        "counting_scope": (
            "Unique current stroke events referenced by rallies explicitly marked official; "
            "unlinked legacy shots excluded. Shot labels may be model predictions."
        ),
    }
