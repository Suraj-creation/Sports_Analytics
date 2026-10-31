import pytest

from bai_engine.schema import Event, EventStatus, MediaInfo, Provenance, Session, SessionStatus, Source, SourceKind
from bai_engine.schema.session import ParticipantInfo, ParticipantRoster, TeamInfo


def recording(client):
    repo = client.app.state.repo
    session = repo.save(
        Session(
            title="Four people",
            source=Source(kind=SourceKind.UPLOAD, uri="none"),
            status="analysed",
            media=MediaInfo(fps_num=30, fps_den=1, n_frames=120, width=400, height=400, duration_us=4000000),
            roster=ParticipantRoster(
                match_format="doubles",
                participants=[ParticipantInfo(participant_id=f"person-{i}", name=f"Player {i}") for i in range(4)],
            ),
            meta={"analysis_revision": 2},
            frontier_frame=119,
            analysed_frames=120,
        )
    )
    store = repo.events(session.session_id)
    births, strokes = [], []
    for i in range(4):
        birth = store.append(
            Event(
                session_id=session.session_id,
                type="participant_observation",
                frame_start=1,
                frame_end=1,
                pts_us=33333,
                status=EventStatus.PROVISIONAL,
                provenance=Provenance(model="participant_tracker_v1"),
                payload={"kind": "PLAYER_ENTERED", "participant_id": f"participant-abcd-{i:06d}", "track_id": i},
            )
        )
        births.append(birth)
        strokes.append(
            store.append(
                Event(
                    session_id=session.session_id,
                    type="stroke",
                    frame_start=10 + i,
                    frame_end=10 + i,
                    pts_us=(10 + i) * 33333,
                    provenance=Provenance(model="stroke_rules_v0"),
                    payload={
                        "stroke": "drive",
                        "participant_hypothesis": {
                            "status": "provisional",
                            "track_id": i,
                            "participant_id": birth.payload["participant_id"],
                            "observation_id": birth.event_id,
                        },
                    },
                )
            )
        )
    store.append(
        Event(
            session_id=session.session_id,
            type="rally_end",
            frame_start=5,
            frame_end=50,
            pts_us=166667,
            provenance=Provenance(model="rally_fsm_v1"),
            payload={
                "official": True,
                "rally_no": 1,
                "duration_s": 1.5,
                "shots": [{"event_id": s.event_id, "frame": s.frame_start} for s in strokes],
            },
        )
    )
    return session, births, strokes


def confirm(client, session, birth, person, **changes):
    body = {"observation_id": birth.event_id, "participant_id": person, "start": 1, "end": 30, "analysis_revision": 2}
    return client.post(f"/api/sessions/{session.session_id}/identity-reviews", json={**body, **changes})


def test_four_people_can_be_reviewed_and_credited_independently_then_revoked(client):
    session, births, strokes = recording(client)
    url = f"/api/sessions/{session.session_id}"
    for i, (birth, stroke) in enumerate(zip(births, strokes, strict=True)):
        identity = confirm(client, session, birth, f"person-{i}")
        assert identity.status_code == 201, identity.text
        review = client.post(
            f"{url}/stroke-participant-reviews",
            json={
                "stroke_event_id": stroke.event_id,
                "identity_review_id": identity.json()["event_id"],
                "analysis_revision": 2,
            },
        )
        assert review.status_code == 201, review.text
        # Identity review does not turn an estimated contact/shot into verified physics.
        assert client.app.state.repo.events(session.session_id).get(stroke.event_id).status == EventStatus.PROVISIONAL
    result = client.get(f"{url}/individual-analytics").json()
    assert result["accounting"] == {"total_shots": 4, "attributed_shots": 4, "unattributed_shots": 0}
    assert [person["total_shots"] for person in result["participants"].values()] == [1] * 4
    current = client.get(f"{url}/identity-reviews").json()
    assert current["analysis_revision"] == 2 and len(current["events"]) == 4
    assert (
        client.delete(f"{url}/identity-reviews/{current['events'][0]['event_id']}?analysis_revision=2").status_code
        == 200
    )
    assert client.get(f"{url}/individual-analytics").json()["accounting"]["attributed_shots"] == 3


@pytest.mark.parametrize(
    "changes,status",
    [
        ({"analysis_revision": 1}, 409),
        ({"analysis_revision": True}, 422),
        ({"start": 0}, 422),
        ({"end": 120}, 422),
        ({"participant_id": "P1"}, 422),
    ],
)
def test_review_rejects_stale_generation_invalid_scope_and_score_slots(client, changes, status):
    session, births, _ = recording(client)
    assert confirm(client, session, births[0], "person-0", **changes).status_code == status


def test_one_person_cannot_own_two_simultaneous_tracks_and_processing_is_read_only(client):
    session, births, _ = recording(client)
    assert confirm(client, session, births[0], "person-0").status_code == 201
    assert confirm(client, session, births[1], "person-0").status_code == 422
    client.app.state.repo.update(session.session_id, status=SessionStatus.ANALYSING)
    assert confirm(client, session, births[2], "person-2").status_code == 409


def test_reviewed_four_player_travel_uses_camera_quality_and_exact_episode(client):
    from bai_engine.schema import TrackObject, TrackSample
    from bai_engine.schema.tracks import samples_to_table

    session, births, _ = recording(client)
    tracks = client.app.state.repo.tracks(session.session_id)
    rows = [
        TrackSample(
            frame_idx=frame,
            obj=TrackObject.PLAYER,
            track_id=i,
            participant_observation_id=birth.event_id,
            court_x=-1 + frame * 0.01,
            court_y=-3 + i,
            conf=0.95,
            detector_matched=True,
        )
        for frame in range(1, 51)
        for i, birth in enumerate(births)
    ]
    camera = [
        TrackSample(frame_idx=frame, obj=TrackObject.CAMERA, track_id=0, conf=0.9, cam=(1, 0, 0, 0, 1, 0, 0, 0, 1))
        for frame in range(1, 51)
    ]
    tracks.write_chunk(TrackObject.PLAYER, 0, 119, samples_to_table(rows))
    tracks.write_chunk(TrackObject.CAMERA, 0, 119, samples_to_table(camera))
    for i, birth in enumerate(births):
        assert confirm(client, session, birth, f"person-{i}").status_code == 201
    result = client.get(f"/api/sessions/{session.session_id}/individual-analytics").json()
    for person in result["participants"].values():
        assert 0.1 < person["movement"]["distance_m"] < 0.4
        assert person["movement"]["travel"]["latest"]["heading_deg"] == 0
        assert person["movement"]["travel"]["latest"]["frame_end"] <= 30


def test_corrected_shot_keeps_effective_hitter_review_and_can_be_revoked(client):
    session, births, strokes = recording(client)
    base = f"/api/sessions/{session.session_id}"
    identity = confirm(client, session, births[0], "person-0").json()
    checked = client.post(
        f"{base}/stroke-participant-reviews",
        json={
            "stroke_event_id": strokes[0].event_id,
            "identity_review_id": identity["event_id"],
            "analysis_revision": 2,
        },
    )
    assert checked.status_code == 201
    original = strokes[0]
    corrected = client.app.state.repo.events(session.session_id).append(
        original.correct(payload={**original.payload, "stroke": "clear"}, provenance=Provenance(model="human"))
    )
    reviews = client.get(f"{base}/identity-reviews").json()["stroke_reviews"]
    assert reviews[0]["current_stroke_event_id"] == corrected.event_id
    assert client.get(f"{base}/individual-analytics").json()["accounting"]["attributed_shots"] == 1
    assert (
        client.delete(f"{base}/stroke-participant-reviews/{checked.json()['event_id']}?analysis_revision=2").status_code
        == 200
    )
    assert client.get(f"{base}/individual-analytics").json()["accounting"]["attributed_shots"] == 0


def test_doubles_service_order_replays_points_and_withholds_changed_history(client):
    from bai_badminton.rules.bwf import MatchConfig, apply_rally, initial_state

    session, _, _ = recording(client)
    roster = session.roster.model_copy(
        update={
            "teams": [TeamInfo(team_id="T1", score_slot="P1"), TeamInfo(team_id="T2", score_slot="P2")],
            "participants": [
                person.model_copy(update={"team_id": "T1" if i < 2 else "T2"})
                for i, person in enumerate(session.roster.participants)
            ],
        }
    )
    client.app.state.repo.update(session.session_id, roster=roster)
    base = f"/api/sessions/{session.session_id}/doubles-service"
    assert client.get(base).json()["status"] == "unknown"
    response = client.post(
        base,
        json={
            "server_participant_id": "person-0",
            "receiver_participant_id": "person-2",
            "frame": 0,
            "analysis_revision": 2,
        },
    )
    assert response.status_code == 201, response.text
    cfg = MatchConfig(discipline="doubles")
    state = initial_state(cfg)
    points = []
    store = client.app.state.repo.events(session.session_id)
    for frame, winner in zip((10, 20, 30), ("P1", "P2", "P2"), strict=True):
        result = apply_rally(state, winner, cfg)
        points.append(
            store.append(
                Event(
                    session_id=session.session_id,
                    type="point",
                    frame_start=frame,
                    frame_end=frame,
                    pts_us=frame * 33333,
                    provenance=Provenance(model="bwf_rules_v1"),
                    payload={
                        "winner": winner,
                        "state_before": state.to_public(cfg),
                        "state_after": result.after.to_public(cfg),
                    },
                )
            )
        )
        state = result.after
    result = client.get(base).json()
    assert result["server_participant_id"] == "person-3"
    assert result["receiver_participant_id"] == "person-1"
    assert result["service_court"] == "right"
    store.append(points[0].correct(payload={**points[0].payload, "winner": "P2"}))
    assert client.get(base).json()["status"] == "unknown"
    # A fresh setup must not bless stale score snapshots or an inconsistent point chain.
    assert (
        client.post(
            base,
            json={
                "server_participant_id": "person-2",
                "receiver_participant_id": "person-0",
                "frame": 30,
                "analysis_revision": 2,
            },
        ).status_code
        == 422
    )


def test_legacy_rally_without_explicit_official_flag_does_not_credit_named_movement(client):
    session, births, _ = recording(client)
    store = client.app.state.repo.events(session.session_id)
    rally = store.query(types=["rally_end"])[0]
    payload = dict(rally.payload)
    payload.pop("official")
    store.append(rally.correct(payload=payload))
    assert confirm(client, session, births[0], "person-0").status_code == 201
    result = client.get(f"/api/sessions/{session.session_id}/individual-analytics").json()
    assert result["participants"]["person-0"]["movement"]["expected_frames"] == 0


def test_service_setup_uses_canonical_point_state_instead_of_stale_snapshot(client):
    from bai_badminton.rules.bwf import MatchConfig, apply_rally, initial_state
    from bai_engine.schema import StateSnapshot

    session, _, _ = recording(client)
    roster = session.roster.model_copy(
        update={
            "teams": [TeamInfo(team_id="T1", score_slot="P1"), TeamInfo(team_id="T2", score_slot="P2")],
            "participants": [
                person.model_copy(update={"team_id": "T1" if i < 2 else "T2"})
                for i, person in enumerate(session.roster.participants)
            ],
        }
    )
    repo = client.app.state.repo
    repo.update(session.session_id, roster=roster)
    store = repo.events(session.session_id)
    cfg = MatchConfig(discipline="doubles")
    initial = initial_state(cfg)
    result = apply_rally(initial, "P1", cfg)
    point = store.append(
        Event(
            session_id=session.session_id,
            type="point",
            frame_start=10,
            frame_end=10,
            pts_us=333333,
            provenance=Provenance(model="bwf_rules_v1"),
            payload={
                "winner": "P1",
                "state_before": initial.to_public(cfg),
                "state_after": result.after.to_public(cfg),
            },
        )
    )
    store.put_state(
        StateSnapshot(session_id=session.session_id, frame_idx=10, event_seq=point.seq, state=initial.to_public(cfg))
    )
    response = client.post(
        f"/api/sessions/{session.session_id}/doubles-service",
        json={
            "server_participant_id": "person-0",
            "receiver_participant_id": "person-2",
            "frame": 10,
            "analysis_revision": 2,
        },
    )
    assert response.status_code == 201, response.text
    assert response.json()["payload"]["score"] == {"P1": 1, "P2": 0}


def test_roster_edit_cannot_use_stale_session_to_reassign_a_reviewed_person(client):
    from fastapi import HTTPException

    from bai_api.routes.sessions import update_roster

    session, births, _ = recording(client)
    roster = session.roster.model_copy(
        update={
            "teams": [TeamInfo(team_id="T1", score_slot="P1")],
            "participants": [
                person.model_copy(update={"team_id": "T1"}) if i == 0 else person
                for i, person in enumerate(session.roster.participants)
            ],
        }
    )
    client.app.state.repo.update(session.session_id, roster=roster)
    assert confirm(client, session, births[0], "person-0").status_code == 201
    with pytest.raises(HTTPException) as error:
        update_roster(session, session.roster, client.app.state.repo)
    assert error.value.status_code == 409
