"""Estimated identities are strictly separated from human-verified counts."""

from __future__ import annotations

from pathlib import Path

import pytest

from bai_badminton.identity_review import IdentityReviewLedger
from bai_engine.schema import Actors, Event, EventStatus, Provenance, TrackObject, TrackSample
from bai_engine.schema.session import ParticipantInfo, ParticipantRoster, TeamInfo
from bai_engine.schema.tracks import samples_to_table
from bai_engine.store import EventStore, TrackStore


def _roster():
    return ParticipantRoster(
        match_format="doubles",
        teams=[TeamInfo(team_id="T1"), TeamInfo(team_id="T2")],
        participants=[
            ParticipantInfo(participant_id=f"U{i}", name=f"Person {i}", team_id="T1" if i < 3 else "T2")
            for i in range(1, 5)
        ],
    )


def _event(kind, frame, *, payload, model="test", status=EventStatus.CONFIRMED, actor=None):
    return Event(
        session_id="S1",
        type=kind,
        frame_start=frame,
        frame_end=frame,
        pts_us=frame * 33333,
        payload=payload,
        actors=actor or Actors(),
        status=status,
        provenance=Provenance(model=model),
    )


def _setup(tmp_path: Path, *, frames=(1, 5, 10), detector_observed=True):
    store = EventStore(tmp_path / "events.sqlite", "S1")
    tracks = TrackStore(tmp_path / "tracks")
    observations = []
    ledger = IdentityReviewLedger(store, {f"U{i}" for i in range(1, 5)}, max_frame=300, fps=30)
    rows = []
    shots = []
    seeds = []
    for i in range(1, 5):
        pid = f"participant-abcd-{i:06d}"
        obs = store.append(
            _event(
                "participant_observation",
                1,
                payload={"kind": "PARTICIPANT_FIRST_OBSERVED", "track_id": i, "participant_id": pid},
                model="participant_tracker_v1",
                status=EventStatus.PROVISIONAL,
            )
        )
        observations.append(obs)
        seeds.append(ledger.confirm(obs.event_id, f"U{i}", 1, 1))
        rows.extend(
            TrackSample(
                detector_observed=detector_observed,
                frame_idx=f,
                obj=TrackObject.PLAYER,
                track_id=i,
                bbox=(1, 1, 20, 30),
                conf=0.9,
                participant_observation_id=obs.event_id,
            )
            for f in frames
        )
        shots.append(
            store.append(
                _event(
                    "stroke",
                    10,
                    payload={
                        "stroke": "drive",
                        "participant_hypothesis": {
                            "status": "provisional",
                            "participant_id": pid,
                            "track_id": i,
                            "reason": "unique",
                            "observation_id": obs.event_id,
                        },
                    },
                )
            )
        )
    tracks.write_chunk(TrackObject.PLAYER, 1, 10, samples_to_table(rows))
    store.append(
        _event("rally_end", 12, payload={"official": True, "shots": [{"event_id": s.event_id} for s in shots]})
    )
    return store, tracks, observations, seeds, shots


def _fold(store, tracks):
    from bai_badminton.analytics.automatic_individual import build_estimated_individual_analytics

    return build_estimated_individual_analytics(
        store, tracks, _roster(), max_frame=300, fps=30, frame_width=1280, frame_height=720
    )


def test_four_participants_are_separate_estimates_and_not_verified(tmp_path):
    store, tracks, observations, seeds, shots = _setup(tmp_path)
    result = _fold(store, tracks)
    assert result["official"]["accounting"] == {
        "total_linked_shots": 4,
        "verified_shots": 0,
        "estimated_shots": 4,
        "unresolved_shots": 0,
    }
    for i in range(1, 5):
        person = result["official"]["participants"][f"U{i}"]
        assert person["estimated_shots"] == 1
        ev = person["events"][0]
        assert ev["seed_review_id"] == seeds[i - 1].event_id
        assert ev["observation_id"] == observations[i - 1].event_id
        assert ev["event_id"] == shots[i - 1].event_id and ev["status"] == "estimated"
        assert ev["detector_observed"] is True
        assert ev["detector_observation_scope"] == "frame_only_not_person_match"
    assert result["all_linked"]["accounting"]["estimated_shots"] == 4


def test_missing_track_sample_gap_and_reset_abstain(tmp_path):
    store, tracks, observations, seeds, shots = _setup(tmp_path, frames=(1, 10))
    result = _fold(store, tracks)
    assert result["official"]["accounting"]["estimated_shots"] == 0
    assert set(result["official"]["unresolved_event_ids"]) == {s.event_id for s in shots}
    # A gap no longer than six frames is permitted, but a reset still invalidates propagation.
    rows = [
        TrackSample(
            detector_observed=True,
            frame_idx=f,
            obj=TrackObject.PLAYER,
            track_id=i,
            bbox=(1, 1, 20, 30),
            conf=0.9,
            participant_observation_id=observations[i - 1].event_id,
        )
        for i in range(1, 5)
        for f in (1, 5, 10)
    ]
    tracks.write_chunk(TrackObject.PLAYER, 1, 10, samples_to_table(rows))
    store.append(
        _event(
            "identity_ambiguity",
            7,
            payload={"reason": "visual_tracker_reset"},
            status=EventStatus.PROVISIONAL,
            model="participant_tracker_v1",
        )
    )
    assert _fold(store, tracks)["official"]["accounting"]["estimated_shots"] == 0


def test_future_conflicting_revoked_and_unresolved_seeds_do_not_credit(tmp_path):
    store, tracks, observations, seeds, shots = _setup(tmp_path)
    ledger = IdentityReviewLedger(store, {f"U{i}" for i in range(1, 5)}, max_frame=300, fps=30)
    ledger.revoke(seeds[0].event_id)
    # A second conflicting human identity for the same episode invalidates it.
    store.append(
        _event(
            "identity_review",
            2,
            payload=seeds[1].payload,
            actor=Actors(player_id="U3", track_id=2),
            model="human",
            status=EventStatus.HUMAN_VERIFIED,
        )
    )
    # The seed for U3 at frame 20 cannot explain a shot at frame 10.
    ledger.revoke(seeds[2].event_id)
    ledger.confirm(observations[2].event_id, "U3", 20, 20)
    # A model's unresolved/tied hypothesis must not produce a player.
    store.append(
        shots[3].correct(
            payload={
                "stroke": "drive",
                "participant_hypothesis": {"status": "unresolved", "participant_id": None, "track_id": None},
            }
        )
    )
    result = _fold(store, tracks)
    assert result["official"]["accounting"]["estimated_shots"] == 0
    assert result["official"]["accounting"]["unresolved_shots"] == 4


def test_preliminary_scope_separate_from_official_and_orphans_visible(tmp_path):
    store, tracks, observations, seeds, shots = _setup(tmp_path)
    preliminary = store.append(
        _event(
            "stroke",
            10,
            payload={
                "stroke": "unknown",
                "participant_hypothesis": {
                    "status": "provisional",
                    "participant_id": observations[0].payload["participant_id"],
                    "observation_id": observations[0].event_id,
                    "track_id": 1,
                },
            },
        )
    )
    orphan = store.append(_event("stroke", 11, payload={"stroke": "unknown"}))
    store.append(_event("rally_end", 13, payload={"official": False, "shots": [{"event_id": preliminary.event_id}]}))
    result = _fold(store, tracks)
    assert result["official"]["accounting"]["total_linked_shots"] == 4
    assert result["all_linked"]["accounting"]["total_linked_shots"] == 5
    assert result["all_linked"]["includes_official"] is True
    assert result["unlinked_stroke_events"] == 1
    assert orphan.event_id not in result["all_linked"]["unresolved_event_ids"]


@pytest.mark.parametrize(
    "problem", ["duplicate", "missing_provenance", "invisible", "low_confidence", "wrong_box", "jump", "scale_jump"]
)
def test_invalid_sample_never_infers_an_identity(tmp_path, problem):
    store, tracks, observations, seeds, shots = _setup(tmp_path)
    rows = []
    for i in range(1, 5):
        for f in (1, 5, 10):
            fields = {
                "frame_idx": f,
                "detector_observed": True,
                "obj": TrackObject.PLAYER,
                "track_id": i,
                "bbox": (1, 1, 20, 30),
                "conf": 0.9,
                "participant_observation_id": observations[i - 1].event_id,
            }
            if i == 1 and f == 5:
                if problem == "missing_provenance":
                    fields["participant_observation_id"] = None
                if problem == "invisible":
                    fields["visible"] = False
                if problem == "low_confidence":
                    fields["conf"] = 0.1
                if problem == "wrong_box":
                    fields["bbox"] = (10, 10, 5, 20)
                if problem == "jump":
                    fields["bbox"] = (2000, 1, 2020, 30)
                if problem == "scale_jump":
                    fields["bbox"] = (1, 1, 20, 150)
            row = TrackSample(**fields)
            rows.append(row)
            if i == 1 and f == 5 and problem == "duplicate":
                rows.append(row)
    tracks.write_chunk(TrackObject.PLAYER, 1, 10, samples_to_table(rows))
    result = _fold(store, tracks)
    assert result["official"]["participants"]["U1"]["estimated_shots"] == 0
    assert result["official"]["unresolved_reasons"][shots[0].event_id] == "track_continuity_unavailable"
    assert result["official"]["accounting"]["estimated_shots"] == 3


def test_separate_reviewed_and_estimated_shots_are_never_double_counted(tmp_path):
    store, tracks, observations, seeds, shots = _setup(tmp_path)
    store.append(
        _event(
            "stroke_participant_review",
            10,
            model="human",
            status=EventStatus.HUMAN_VERIFIED,
            actor=Actors(player_id="U1", track_id=1),
            payload={
                "scope": "participant_only",
                "stroke_event_id": shots[0].event_id,
                "identity_review_id": seeds[0].event_id,
                "observation_id": observations[0].event_id,
                "participant_id": observations[0].payload["participant_id"],
                "track_id": 1,
                "player_id": "U1",
            },
        )
    )
    # Review must cover the shot to count as verified; construct a valid new interval seed.
    ledger = IdentityReviewLedger(store, {f"U{i}" for i in range(1, 5)}, max_frame=300, fps=30)
    current = ledger.confirm(observations[0].event_id, "U1", 10, 10)
    store.append(
        _event(
            "stroke_participant_review",
            10,
            model="human",
            status=EventStatus.HUMAN_VERIFIED,
            actor=Actors(player_id="U1", track_id=1),
            payload={
                "scope": "participant_only",
                "stroke_event_id": shots[0].event_id,
                "identity_review_id": current.event_id,
                "observation_id": observations[0].event_id,
                "participant_id": observations[0].payload["participant_id"],
                "track_id": 1,
                "player_id": "U1",
            },
        )
    )
    result = _fold(store, tracks)
    assert result["official"]["accounting"] == {
        "total_linked_shots": 4,
        "verified_shots": 1,
        "estimated_shots": 3,
        "unresolved_shots": 0,
    }
    assert result["official"]["participants"]["U1"]["estimated_shots"] == 0
    assert result["all_linked"]["accounting"]["estimated_shots"] == 4


def test_ambiguity_after_seed_and_before_shot_prevents_propagation(tmp_path):
    store, tracks, observations, seeds, shots = _setup(tmp_path)
    store.append(
        _event(
            "participant_observation",
            5,
            model="participant_tracker_v1",
            status=EventStatus.PROVISIONAL,
            payload={
                "kind": "PLAYER_SUBSTITUTION_OR_IDENTITY_UNCERTAIN",
                "participant_id": observations[0].payload["participant_id"],
                "track_id": 1,
            },
        )
    )
    result = _fold(store, tracks)
    assert result["official"]["unresolved_reasons"][shots[0].event_id] == "identity_ambiguity"
    assert result["official"]["accounting"]["estimated_shots"] == 3


def test_new_ambiguity_on_seed_frame_after_review_prevents_propagation(tmp_path):
    store, tracks, observations, seeds, shots = _setup(tmp_path)
    store.append(
        _event(
            "participant_observation",
            1,
            model="participant_tracker_v1",
            status=EventStatus.PROVISIONAL,
            payload={
                "kind": "PLAYER_REIDENTIFICATION_UNCERTAIN",
                "participant_id": observations[0].payload["participant_id"],
                "track_id": 1,
            },
        )
    )
    result = _fold(store, tracks)
    assert result["official"]["unresolved_reasons"][shots[0].event_id] == "identity_ambiguity"


def test_stroke_track_must_reference_exact_live_birth_observation(tmp_path):
    store, tracks, observations, seeds, shots = _setup(tmp_path)
    data = dict(shots[0].payload)
    data["participant_hypothesis"] = {**data["participant_hypothesis"], "observation_id": "old-run-birth"}
    corrected = store.append(shots[0].correct(payload=data))
    result = _fold(store, tracks)
    assert result["official"]["unresolved_reasons"][corrected.event_id] == "changed_track_hypothesis"
    assert result["official"]["accounting"]["estimated_shots"] == 3


def test_seed_expires_after_bounded_duration(tmp_path):
    from bai_badminton.analytics.automatic_individual import build_estimated_individual_analytics

    store, tracks, observations, seeds, shots = _setup(tmp_path)
    late = store.append(
        _event(
            "stroke",
            250,
            payload={
                "stroke": "drive",
                "participant_hypothesis": {
                    "status": "provisional",
                    "participant_id": observations[0].payload["participant_id"],
                    "track_id": 1,
                    "observation_id": observations[0].event_id,
                },
            },
        )
    )
    store.append(_event("rally_end", 255, payload={"official": True, "shots": [{"event_id": late.event_id}]}))
    tracks.write_chunk(
        TrackObject.PLAYER,
        250,
        250,
        samples_to_table(
            [
                TrackSample(
                    detector_observed=True,
                    frame_idx=250,
                    obj=TrackObject.PLAYER,
                    track_id=1,
                    bbox=(1, 1, 20, 30),
                    conf=0.9,
                    participant_observation_id=observations[0].event_id,
                )
            ]
        ),
    )
    result = build_estimated_individual_analytics(
        store, tracks, _roster(), max_frame=300, fps=30, frame_width=1280, frame_height=720
    )
    # 249 frames is under 10 s at 30 fps, but no continuity exists.
    assert result["official"]["unresolved_reasons"][late.event_id] == "track_continuity_unavailable"
    slower = build_estimated_individual_analytics(
        store, tracks, _roster(), max_frame=300, fps=20, frame_width=1280, frame_height=720
    )
    assert slower["official"]["unresolved_reasons"][late.event_id] == "seed_expired"


def test_same_person_seeded_on_two_live_episodes_abstains(tmp_path):
    store, tracks, observations, seeds, shots = _setup(tmp_path)
    ledger = IdentityReviewLedger(store, {f"U{i}" for i in range(1, 5)}, max_frame=300, fps=30)
    ledger.confirm(observations[1].event_id, "U1", 2, 2)
    result = _fold(store, tracks)
    assert result["official"]["unresolved_reasons"][shots[0].event_id] == "person_has_conflicting_episode_seed"
    assert result["official"]["unresolved_reasons"][shots[1].event_id] == "conflicting_identity_seeds"
    assert result["official"]["accounting"]["estimated_shots"] == 2


def test_human_correction_cannot_introduce_a_forged_track_hypothesis(tmp_path):
    store, tracks, observations, seeds, shots = _setup(tmp_path)
    forged = store.append(
        shots[0].correct(
            payload={**shots[0].payload, "participant_hypothesis": shots[1].payload["participant_hypothesis"]},
            status=EventStatus.HUMAN_VERIFIED,
            provenance=Provenance(model="human"),
        )
    )
    result = _fold(store, tracks)
    assert result["official"]["unresolved_reasons"][forged.event_id] == "changed_track_hypothesis"
    assert result["official"]["participants"]["U2"]["estimated_shots"] == 1


def test_anonymous_four_episodes_are_available_without_roster_or_seeds(tmp_path):
    from bai_badminton.analytics.automatic_individual import build_estimated_individual_analytics

    store, tracks, observations, seeds, shots = _setup(tmp_path)
    result = build_estimated_individual_analytics(
        store, tracks, None, max_frame=300, fps=30, frame_width=1280, frame_height=720
    )
    assert result["available"] is False
    scopes = result["episode_profiles"]
    assert scopes["official"]["accounting"] == {
        "total_linked_shots": 4,
        "episode_candidate_shots": 4,
        "unresolved_shots": 0,
    }
    episodes = scopes["official"]["episodes"]
    assert len(episodes) == 4
    assert {e["observation_id"] for e in episodes} == {o.event_id for o in observations}
    assert all(e["candidate_shots"] == 1 and e["status"] == "anonymous_track_episode" for e in episodes)
    assert all(e["events"][0]["status"] == "anonymous_track_candidate" for e in episodes)
    assert scopes["all_linked"]["includes_official"] is True


def test_anonymous_episode_does_not_count_stale_or_invalid_shot_frame_box(tmp_path):
    store, tracks, observations, seeds, shots = _setup(tmp_path)
    rows = [
        TrackSample(
            detector_observed=True,
            frame_idx=10,
            obj=TrackObject.PLAYER,
            track_id=i,
            bbox=(1, 1, 20, 30),
            conf=0.9,
            participant_observation_id=("old-observation" if i == 1 else observations[i - 1].event_id),
        )
        for i in range(1, 5)
    ]
    tracks.write_chunk(TrackObject.PLAYER, 1, 10, samples_to_table(rows))
    result = _fold(store, tracks)
    scope = result["episode_profiles"]["official"]
    assert scope["accounting"]["episode_candidate_shots"] == 3
    assert shots[0].event_id in scope["unresolved_event_ids"]


def test_missing_birth_id_on_original_model_event_does_not_estimate(tmp_path):
    store, tracks, observations, seeds, shots = _setup(tmp_path)
    stale = store.append(
        _event(
            "stroke",
            10,
            payload={
                "stroke": "drive",
                "participant_hypothesis": {
                    "status": "provisional",
                    "participant_id": observations[0].payload["participant_id"],
                    "track_id": 1,
                    "observation_id": "old-run-birth",
                },
            },
        )
    )
    store.append(_event("rally_end", 13, payload={"official": True, "shots": [{"event_id": stale.event_id}]}))
    result = _fold(store, tracks)
    assert result["official"]["unresolved_reasons"][stale.event_id] == "missing_matching_observation_provenance"
    assert result["official"]["accounting"]["estimated_shots"] == 4


def test_track_windows_are_batched_across_people_and_scopes(tmp_path, monkeypatch):
    store, tracks, observations, seeds, shots = _setup(tmp_path)
    original = tracks.read
    calls = []

    def observed_read(*args):
        calls.append(args)
        return original(*args)

    monkeypatch.setattr(tracks, "read", observed_read)
    result = _fold(store, tracks)
    assert result["official"]["accounting"]["estimated_shots"] == 4
    assert result["episode_profiles"]["official"]["accounting"]["episode_candidate_shots"] == 4
    assert len(calls) == 1


def test_aggregate_only_omits_detailed_evidence_but_retains_counts(tmp_path):
    from bai_badminton.analytics.automatic_individual import build_estimated_individual_analytics

    store, tracks, observations, seeds, shots = _setup(tmp_path)
    result = build_estimated_individual_analytics(
        store, tracks, _roster(), max_frame=300, fps=30, frame_width=1280, frame_height=720, include_events=False
    )
    assert result["detail_included"] is False
    assert result["official"]["accounting"]["estimated_shots"] == 4
    assert result["official"]["participants"]["U1"]["events"] == []
    assert result["episode_profiles"]["official"]["accounting"]["episode_candidate_shots"] == 4
    assert all(ep["events"] == [] for ep in result["episode_profiles"]["official"]["episodes"])


def test_offscreen_shot_box_does_not_support_an_episode(tmp_path):
    store, tracks, observations, seeds, shots = _setup(tmp_path)
    rows = [
        TrackSample(
            detector_observed=True,
            frame_idx=10,
            obj=TrackObject.PLAYER,
            track_id=i,
            bbox=((1281, 1, 1300, 30) if i == 1 else (1, 1, 20, 30)),
            conf=0.9,
            participant_observation_id=observations[i - 1].event_id,
        )
        for i in range(1, 5)
    ]
    tracks.write_chunk(TrackObject.PLAYER, 1, 10, samples_to_table(rows))
    result = _fold(store, tracks)
    assert (
        result["episode_profiles"]["official"]["unresolved_reasons"][shots[0].event_id]
        == "shot_frame_track_unavailable"
    )
    assert result["episode_profiles"]["official"]["accounting"]["episode_candidate_shots"] == 3


def test_legacy_rally_without_explicit_official_decision_stays_preliminary(tmp_path):
    store, tracks, observations, seeds, shots = _setup(tmp_path)
    legacy = store.append(
        _event(
            "stroke",
            10,
            payload={
                "stroke": "drive",
                "participant_hypothesis": {
                    "status": "provisional",
                    "participant_id": observations[0].payload["participant_id"],
                    "track_id": 1,
                    "observation_id": observations[0].event_id,
                },
            },
        )
    )
    store.append(_event("rally_end", 15, payload={"shots": [{"event_id": legacy.event_id}]}))
    result = _fold(store, tracks)
    assert result["official"]["accounting"]["total_linked_shots"] == 4
    assert result["episode_profiles"]["official"]["accounting"]["total_linked_shots"] == 4
    assert result["all_linked"]["accounting"]["total_linked_shots"] == 5
    assert result["episode_profiles"]["all_linked"]["accounting"]["total_linked_shots"] == 5


def test_identity_boundaries_are_loaded_once_per_fold(tmp_path, monkeypatch):
    store, tracks, observations, seeds, shots = _setup(tmp_path)
    original = store.query
    queries = []

    def observed_query(*args, **kwargs):
        if set(kwargs.get("types") or ()) == {"identity_ambiguity", "participant_observation"}:
            queries.append(kwargs)
        return original(*args, **kwargs)

    monkeypatch.setattr(store, "query", observed_query)
    result = _fold(store, tracks)
    assert result["official"]["accounting"]["estimated_shots"] == 4
    assert len(queries) == 1


def test_carried_boxes_without_detector_evidence_do_not_propagate_identity():
    from bai_badminton.analytics.automatic_individual import _continuous

    rows = [
        {"frame_idx": frame, "track_id": 4, "visible": True, "participant_observation_id": "obs",
         "conf": 0.9, "bbox": [10, 10, 30, 50], "detector_observed": False}
        for frame in range(7)
    ]
    rows[0]["detector_observed"] = True
    assert not _continuous(rows, "obs", 4, 0, 6, 1280, 720)
    rows[-1]["detector_observed"] = True
    assert _continuous(rows, "obs", 4, 0, 6, 1280, 720)
    rows[0]["detector_observed"] = None
    assert not _continuous(rows, "obs", 4, 0, 6, 1280, 720)


def test_detector_run_gap_and_unknown_intermediate_provenance_abstain():
    from bai_badminton.analytics.automatic_individual import _continuous

    rows = [
        {"frame_idx": frame, "track_id": 4, "visible": True, "participant_observation_id": "obs",
         "conf": 0.9, "bbox": [10, 10, 30, 50], "detector_observed": False}
        for frame in range(14)
    ]
    rows[0]["detector_observed"] = rows[-1]["detector_observed"] = True
    assert not _continuous(rows, "obs", 4, 0, 13, 1280, 720)
    rows[6]["detector_observed"] = rows[12]["detector_observed"] = True
    assert _continuous(rows, "obs", 4, 0, 13, 1280, 720)
    rows[7]["detector_observed"] = None
    assert not _continuous(rows, "obs", 4, 0, 13, 1280, 720)


def test_legacy_unknown_detector_provenance_never_becomes_named_but_anonymous_remains(tmp_path):
    store, tracks, observations, seeds, shots = _setup(tmp_path, detector_observed=None)
    result = _fold(store, tracks)
    assert result["all_linked"]["accounting"]["estimated_shots"] == 0
    scope = result["episode_profiles"]["all_linked"]
    assert scope["accounting"]["episode_candidate_shots"] == 4
    assert scope["detector_run_counts"] == {"ran": 0, "not_run": 0, "unknown": 4}
    assert all(ep["events"][0]["detector_observed"] is None for ep in scope["episodes"])
    assert all(ep["events"][0]["detector_observation_scope"] == "frame_only_not_person_match"
               for ep in scope["episodes"])


def test_carried_shot_sample_abstains_named_but_discloses_anonymous_status(tmp_path):
    store, tracks, observations, seeds, shots = _setup(tmp_path)
    rows = [
        TrackSample(frame_idx=frame, obj=TrackObject.PLAYER, track_id=i, bbox=(1, 1, 20, 30),
                    conf=0.9, participant_observation_id=observations[i - 1].event_id,
                    detector_observed=(frame != 10))
        for i in range(1, 5) for frame in (1, 5, 10)
    ]
    tracks.write_chunk(TrackObject.PLAYER, 1, 10, samples_to_table(rows))
    result = _fold(store, tracks)
    assert result["official"]["accounting"]["estimated_shots"] == 0
    scope = result["episode_profiles"]["official"]
    assert scope["accounting"]["episode_candidate_shots"] == 4
    assert scope["detector_run_counts"] == {"ran": 0, "not_run": 4, "unknown": 0}
    assert all(ep["events"][0]["detector_observed"] is False for ep in scope["episodes"])
