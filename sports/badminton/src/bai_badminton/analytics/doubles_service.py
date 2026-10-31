"""Replay reviewed opening service order against the canonical point ledger."""

from __future__ import annotations

import hashlib
import json

from bai_badminton.rules.doubles import DoublesServiceOrder
from bai_engine.schema import EventStatus
from bai_engine.schema.session import ParticipantRoster
from bai_engine.store import EventStore


def teams_for(roster: ParticipantRoster) -> dict[str, tuple[str, str]]:
    if roster.match_format != "doubles":
        raise ValueError("doubles roster required")
    teams = {
        team.score_slot: tuple(
            sorted(person.participant_id for person in roster.participants if person.team_id == team.team_id)
        )
        for team in roster.teams
        if team.score_slot is not None
    }
    if set(teams) != {"P1", "P2"} or any(len(pair) != 2 for pair in teams.values()):
        raise ValueError("two players per team and explicit P1/P2 score-slot assignments required")
    return teams


def prefix_digest(store: EventStore, frame: int) -> str:
    events = [event.model_dump(mode="json") for event in store.query(types=["point"], frame_to=frame)]
    return hashlib.sha256(json.dumps(events, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def canonical_score_state(store: EventStore, frame: int) -> dict | None:
    """Validate actual point transitions before accepting a new manual service anchor."""
    previous = None
    for point in sorted(
        store.query(types=["point"], frame_to=frame), key=lambda event: (event.frame_start, event.seq or 0)
    ):
        before, after = point.payload.get("state_before"), point.payload.get("state_after")
        winner = point.payload.get("winner")
        if (
            not isinstance(before, dict)
            or not isinstance(after, dict)
            or winner not in ("P1", "P2")
            or not isinstance(before.get("score"), dict)
            or set(before["score"]) != {"P1", "P2"}
            or any(type(value) is not int or not 0 <= value < 30 for value in before["score"].values())
            or type(before.get("game_no")) is not int
            or before["game_no"] < 1
        ):
            raise ValueError("canonical point evidence is incomplete")
        if previous is not None and (
            previous.get("score") != before["score"]
            or previous.get("game_no") != before["game_no"]
            or previous.get("winner") is not None
        ):
            raise ValueError("canonical point sequence changed or is incomplete")
        expected = dict(before["score"])
        expected[winner] += 1
        if after.get("game_no") == before["game_no"]:
            if after.get("score") != expected:
                raise ValueError("point winner does not match score transition")
        elif after.get("game_no") == before["game_no"] + 1:
            completed = after.get("completed_games")
            if (
                after.get("score") != {"P1": 0, "P2": 0}
                or not completed
                or list(completed[-1]) != [expected["P1"], expected["P2"]]
            ):
                raise ValueError("game transition does not match point evidence")
        else:
            raise ValueError("invalid game transition")
        previous = after
    return previous


def service_at(store: EventStore, roster: ParticipantRoster, frame: int, revision: int) -> dict:
    setups = [
        event
        for event in store.query(types=["doubles_service_setup"], frame_to=frame)
        if event.status == EventStatus.HUMAN_VERIFIED and event.provenance.model == "human"
    ]
    unknown = {"status": "unknown", "reason": "opening_server_and_receiver_not_recorded"}
    if not setups:
        return unknown
    setup = max(setups, key=lambda event: (event.frame_start, event.seq or 0))
    payload = setup.payload
    if payload.get("analysis_revision") != revision or payload.get("score_prefix_sha256") != prefix_digest(
        store, setup.frame_start
    ):
        return {"status": "unknown", "reason": "analysis_or_score_history_changed"}
    try:
        teams = teams_for(roster)
        if {slot: list(pair) for slot, pair in teams.items()} != payload.get("teams"):
            return {"status": "unknown", "reason": "team_membership_changed"}
        state = DoublesServiceOrder.seed(teams, payload["server"], payload["receiver"], payload["score"])
        game = payload["game_no"]
        for point in sorted(
            store.query(types=["point"], frame_from=setup.frame_start + 1, frame_to=frame),
            key=lambda event: (event.frame_start, event.seq or 0),
        ):
            before, after = point.payload.get("state_before", {}), point.payload.get("state_after", {})
            if before.get("game_no") != game or before.get("score") != state.score:
                return {"status": "unknown", "reason": "incomplete_or_changed_point_sequence"}
            if after.get("game_no") != game or after.get("winner") is not None:
                return {"status": "unknown", "reason": "new_game_requires_service_selection"}
            state = state.point(point.payload.get("winner"))
            if after.get("score") != state.score:
                return {"status": "unknown", "reason": "incomplete_or_changed_point_sequence"}
        return {**state.to_public(), "game_no": game, "setup_event_id": setup.event_id}
    except (KeyError, ValueError, TypeError):
        return {"status": "unknown", "reason": "invalid_service_evidence"}
