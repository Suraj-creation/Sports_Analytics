"""Official shot totals only credit explicitly reviewed person and track evidence."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from bai_badminton.identity_review import IdentityReviewLedger
from bai_engine.schema import Actors, Event, EventStatus, Provenance
from bai_engine.schema.session import ParticipantInfo, ParticipantRoster, TeamInfo
from bai_engine.store import EventStore


def _module():
    spec = importlib.util.find_spec("bai_badminton.analytics.individual")
    assert spec is not None, "individual analytics fold is not yet implemented"
    from bai_badminton.analytics import individual

    return individual


def _roster() -> ParticipantRoster:
    return ParticipantRoster(
        match_format="doubles",
        teams=[TeamInfo(team_id="T1", score_slot="P1"), TeamInfo(team_id="T2", score_slot="P2")],
        participants=[
            ParticipantInfo(participant_id=f"U{i}", name=f"Player {i}", team_id="T1" if i < 3 else "T2")
            for i in range(1, 5)
        ],
    )


def _event(kind, frame, *, payload, actors=None, status=EventStatus.CONFIRMED, model="test"):
    return Event(
        session_id="S1",
        type=kind,
        frame_start=frame,
        frame_end=frame,
        pts_us=frame * 33333,
        actors=actors or Actors(),
        payload=payload,
        status=status,
        provenance=Provenance(model=model),
    )


def _observation(store, track, frame=1, epoch="abcd"):
    pid = f"participant-{epoch}-{track:06d}"
    return store.append(
        _event(
            "participant_observation",
            frame,
            status=EventStatus.PROVISIONAL,
            model="participant_tracker_v1",
            payload={"kind": "PARTICIPANT_FIRST_OBSERVED", "participant_id": pid, "track_id": track},
        )
    )


def _stroke(store, frame, obs, *, verified=True, hypothesis_status="human_verified", track=None):
    track = obs.payload["track_id"] if track is None else track
    return store.append(
        _event(
            "stroke",
            frame,
            status=EventStatus.HUMAN_VERIFIED if verified else EventStatus.CONFIRMED,
            model="stroke_rules_v0",
            payload={
                "stroke": "drive",
                "participant_hypothesis": {
                    "status": hypothesis_status,
                    "participant_id": obs.payload["participant_id"],
                    "track_id": track,
                    "observation_id": obs.event_id,
                },
            },
        )
    )


def _rally(store, strokes, *, official=True):
    return store.append(
        _event(
            "rally_end",
            50,
            payload={
                "official": official,
                "rally_no": 1,
                "duration_s": 1.0,
                "shots": [{"event_id": event.event_id, "frame": event.frame_start} for event in strokes],
            },
        )
    )


def test_four_people_and_team_totals_reconcile_without_guessing(tmp_path: Path):
    fold = _module().build_individual_analytics
    store = EventStore(tmp_path / "events.sqlite", "S1")
    obs = [_observation(store, i) for i in range(1, 5)]
    ledger = IdentityReviewLedger(store, {f"U{i}" for i in range(1, 5)}, max_frame=100, fps=30)
    identities = [ledger.confirm(item.event_id, f"U{i}", 1, 40) for i, item in enumerate(obs, 1)]
    confirmed = [_stroke(store, i + 5, item) for i, item in enumerate(obs)]
    for i, shot in enumerate(confirmed):
        _review_stroke(store, shot, obs[i], identities[i], f"U{i + 1}")
    provisional = _stroke(store, 20, obs[0], verified=False, hypothesis_status="provisional")
    mismatch = _stroke(store, 21, obs[1], track=99)
    ignored = _stroke(store, 22, obs[0])
    _rally(store, [ignored], official=False)
    _rally(store, [*confirmed, provisional, mismatch, confirmed[0]])
    data = fold(store, _roster(), max_frame=100, fps=30)
    assert data["accounting"] == {"total_shots": 6, "attributed_shots": 4, "unattributed_shots": 2}
    assert [data["participants"][f"U{i}"]["total_shots"] for i in range(1, 5)] == [1, 1, 1, 1]
    assert data["teams"]["T1"]["attributed_shots"] == 2
    assert data["teams"]["T2"]["attributed_shots"] == 2
    assert set(data["unattributed_event_ids"]) == {provisional.event_id, mismatch.event_id}
    assert ignored.event_id not in data["unattributed_event_ids"]


def test_corrections_retractions_and_review_revoke_refold_without_duplicates(tmp_path: Path):
    fold = _module().build_individual_analytics
    store = EventStore(tmp_path / "events.sqlite", "S1")
    obs = _observation(store, 1)
    ledger = IdentityReviewLedger(store, {"U1"}, max_frame=100, fps=30)
    review = ledger.confirm(obs.event_id, "U1", 1, 40)
    initial = _stroke(store, 5, obs, verified=False, hypothesis_status="provisional")
    _rally(store, [initial, initial])
    assert fold(store, _roster(), max_frame=100, fps=30)["accounting"]["unattributed_shots"] == 1
    payload = dict(initial.payload)
    corrected = store.append(
        initial.correct(payload=payload, status=EventStatus.HUMAN_VERIFIED, provenance=Provenance(model="human"))
    )
    _review_stroke(store, corrected, obs, review)
    after = fold(store, _roster(), max_frame=100, fps=30)
    assert after["accounting"] == {"total_shots": 1, "attributed_shots": 1, "unattributed_shots": 0}
    assert after["participants"]["U1"]["event_ids"] == [corrected.event_id]
    ledger.revoke(review.event_id)
    assert fold(store, _roster(), max_frame=100, fps=30)["accounting"]["unattributed_shots"] == 1
    store.append(corrected.retract(Provenance(model="human")))
    assert fold(store, _roster(), max_frame=100, fps=30)["accounting"]["total_shots"] == 0


def test_unknown_roster_never_credits_legacy_score_slots(tmp_path: Path):
    fold = _module().build_individual_analytics
    store = EventStore(tmp_path / "events.sqlite", "S1")
    event = store.append(_event("stroke", 5, actors=Actors(player_id="P1"), payload={"stroke": "smash"}))
    _rally(store, [event])
    data = fold(store, None, max_frame=100, fps=30)
    assert data["available"] is False
    assert data["participants"] == {} and data["teams"] == {}
    assert data["accounting"] == {"total_shots": 1, "attributed_shots": 0, "unattributed_shots": 1}


def test_episode_reset_invalidates_reviews_and_legacy_shots_are_reported(tmp_path: Path):
    fold = _module().build_individual_analytics
    store = EventStore(tmp_path / "events.sqlite", "S1")
    obs = _observation(store, 1)
    identity = IdentityReviewLedger(store, {"U1"}, max_frame=100, fps=30).confirm(obs.event_id, "U1", 1, 40)
    stroke = _stroke(store, 10, obs)
    _review_stroke(store, stroke, obs, identity)
    store.append(
        _event(
            "rally_end",
            50,
            payload={"official": True, "shots": [{"event_id": stroke.event_id}, {"frame": 11, "stroke": "drive"}]},
        )
    )
    before = fold(store, _roster(), max_frame=100, fps=30)
    assert before["accounting"]["attributed_shots"] == 1
    assert before["legacy_unlinked_shots"] == 1
    store.append(_event("identity_ambiguity", 8, payload={"reason": "visual_tracker_reset"}))
    after = fold(store, _roster(), max_frame=100, fps=30)
    assert after["accounting"]["unattributed_shots"] == 1
    assert after["unattributed_event_ids"] == [stroke.event_id]


def test_conflicting_human_mappings_remain_unattributed(tmp_path: Path):
    fold = _module().build_individual_analytics
    store = EventStore(tmp_path / "events.sqlite", "S1")
    obs = _observation(store, 1)
    review = IdentityReviewLedger(store, {"U1"}, max_frame=100, fps=30).confirm(obs.event_id, "U1", 1, 40)
    store.append(
        _event(
            "identity_review",
            1,
            status=EventStatus.HUMAN_VERIFIED,
            model="human",
            actors=Actors(player_id="U2", track_id=1),
            payload=review.payload,
        ).model_copy(update={"frame_end": 40})
    )
    stroke = _stroke(store, 10, obs)
    _review_stroke(store, stroke, obs, review)
    _rally(store, [stroke])
    result = fold(store, _roster(), max_frame=100, fps=30)
    assert result["accounting"]["unattributed_shots"] == 1
    assert result["unattributed_event_ids"] == [stroke.event_id]


def _review_stroke(store, stroke, obs, identity, player="U1"):
    return store.append(
        _event(
            "stroke_participant_review",
            stroke.frame_start,
            status=EventStatus.HUMAN_VERIFIED,
            model="human",
            actors=Actors(player_id=player, track_id=obs.payload["track_id"]),
            payload={
                "stroke_event_id": stroke.event_id,
                "identity_review_id": identity.event_id,
                "observation_id": obs.event_id,
                "participant_id": obs.payload["participant_id"],
                "track_id": obs.payload["track_id"],
                "player_id": player,
                "scope": "participant_only",
            },
        )
    )


def test_scoped_review_attributes_unverified_classification_without_verifying_it(tmp_path: Path):
    fold = _module().build_individual_analytics
    store = EventStore(tmp_path / "events.sqlite", "S1")
    obs = _observation(store, 1)
    identity = IdentityReviewLedger(store, {"U1"}, max_frame=100, fps=30).confirm(obs.event_id, "U1", 1, 40)
    shot = _stroke(store, 5, obs, verified=False, hypothesis_status="provisional")
    _rally(store, [shot])
    review = _review_stroke(store, shot, obs, identity)
    assert fold(store, _roster(), max_frame=100, fps=30)["accounting"]["attributed_shots"] == 1
    assert store.get(shot.event_id).status == EventStatus.CONFIRMED
    corrected = store.append(shot.correct(payload={**shot.payload, "stroke": "clear"}))
    assert fold(store, _roster(), max_frame=100, fps=30)["participants"]["U1"]["event_ids"] == [corrected.event_id]
    store.append(review.retract(Provenance(model="human")))
    assert fold(store, _roster(), max_frame=100, fps=30)["accounting"]["unattributed_shots"] == 1


def test_stale_and_duplicate_scoped_reviews_do_not_attribute(tmp_path: Path):
    fold = _module().build_individual_analytics
    store = EventStore(tmp_path / "events.sqlite", "S1")
    obs = _observation(store, 1)
    identity = IdentityReviewLedger(store, {"U1"}, max_frame=100, fps=30).confirm(obs.event_id, "U1", 1, 40)
    shot = _stroke(store, 5, obs, verified=False, hypothesis_status="provisional")
    _rally(store, [shot])
    _review_stroke(store, shot, obs, identity)
    duplicate = _review_stroke(store, shot, obs, identity)
    assert fold(store, _roster(), max_frame=100, fps=30)["accounting"]["unattributed_shots"] == 1
    store.append(duplicate.retract(Provenance(model="human")))
    assert fold(store, _roster(), max_frame=100, fps=30)["accounting"]["attributed_shots"] == 1
    changed = {**shot.payload, "participant_hypothesis": {**shot.payload["participant_hypothesis"], "track_id": 2}}
    store.append(shot.correct(payload=changed))
    assert fold(store, _roster(), max_frame=100, fps=30)["accounting"]["unattributed_shots"] == 1



def test_verified_fold_rejects_missing_or_mismatched_birth_after_correction(tmp_path: Path):
    fold = _module().build_individual_analytics
    store = EventStore(tmp_path / "stale-birth.sqlite", "S1")
    obs = _observation(store, 1)
    identity = IdentityReviewLedger(store, {"U1"}, max_frame=100, fps=30).confirm(obs.event_id, "U1", 1, 40)
    shot = _stroke(store, 5, obs, verified=False, hypothesis_status="provisional")
    _rally(store, [shot])
    _review_stroke(store, shot, obs, identity)
    assert fold(store, _roster(), max_frame=100, fps=30)["accounting"]["attributed_shots"] == 1
    for bad_id in (None, "other-birth"):
        changed = {
            **shot.payload,
            "participant_hypothesis": {**shot.payload["participant_hypothesis"], "observation_id": bad_id},
        }
        shot = store.append(shot.correct(payload=changed))
        result = fold(store, _roster(), max_frame=100, fps=30)
        assert result["accounting"]["unattributed_shots"] == 1
        assert result["participants"]["U1"]["total_shots"] == 0


def test_verified_fold_rejects_preexisting_human_hypothesis_rewrite(tmp_path: Path):
    fold = _module().build_individual_analytics
    store = EventStore(tmp_path / "rewritten.sqlite", "S1")
    obs = _observation(store, 1)
    identity = IdentityReviewLedger(store, {"U1"}, max_frame=100, fps=30).confirm(obs.event_id, "U1", 1, 40)
    machine = _stroke(store, 5, obs, verified=False, hypothesis_status="provisional")
    _rally(store, [machine])
    forged = store.append(machine.correct(
        payload={**machine.payload, "participant_hypothesis": {
            **machine.payload["participant_hypothesis"], "reason": "forged"
        }},
        provenance=Provenance(model="human"),
    ))
    _review_stroke(store, forged, obs, identity)
    result = fold(store, _roster(), max_frame=100, fps=30)
    assert result["accounting"]["unattributed_shots"] == 1
    assert result["participants"]["U1"]["total_shots"] == 0


def test_verified_fold_requires_explicit_true_official_status(tmp_path: Path):
    fold = _module().build_individual_analytics
    store = EventStore(tmp_path / "legacy-rally.sqlite", "S1")
    obs = _observation(store, 1)
    identity = IdentityReviewLedger(store, {"U1"}, max_frame=100, fps=30).confirm(obs.event_id, "U1", 1, 40)
    stroke = _stroke(store, 5, obs, verified=False, hypothesis_status="provisional")
    _review_stroke(store, stroke, obs, identity)
    legacy = store.append(_event("rally_end", 50, payload={"shots": [{"event_id": stroke.event_id}]}))
    assert fold(store, _roster(), max_frame=100, fps=30)["accounting"]["total_shots"] == 0
    malformed = store.append(legacy.correct(payload={**legacy.payload, "official": "yes"}))
    assert fold(store, _roster(), max_frame=100, fps=30)["accounting"]["total_shots"] == 0
    confirmed = store.append(malformed.correct(payload={**malformed.payload, "official": True}))
    data = fold(store, _roster(), max_frame=100, fps=30)
    assert data["accounting"]["attributed_shots"] == 1
    assert data["participants"]["U1"]["rally_ids"] == [confirmed.event_id]
