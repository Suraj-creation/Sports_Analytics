from bai_engine.schema import Session, Source, SourceKind
from bai_engine.schema.session import MediaInfo, ParticipantInfo, ParticipantRoster


def test_estimated_analytics_route_exposes_separate_scopes(client):
    repo = client.app.state.repo
    session = repo.save(
        Session(
            title="test",
            source=Source(kind=SourceKind.UPLOAD, uri="none"),
            media=MediaInfo(fps_num=30, fps_den=1, n_frames=300, width=100, height=100, duration_us=10_000_000),
            roster=ParticipantRoster(
                match_format="doubles", participants=[ParticipantInfo(participant_id=f"U{i}") for i in range(4)]
            ),
        )
    )
    result = client.get(f"/api/sessions/{session.session_id}/estimated-individual-analytics")
    assert result.status_code == 200
    body = result.json()
    assert body["available"] and len(body["official"]["participants"]) == 4
    assert body["detail_included"] is False
    assert (
        client.get(f"/api/sessions/{session.session_id}/estimated-individual-analytics?include_events=true").json()[
            "detail_included"
        ]
        is True
    )
    assert body["official"]["accounting"]["verified_shots"] == 0
    assert body["all_linked"]["includes_official"] is True
    assert body["policy"]["kind"] == "uncalibrated_episode_estimate"


def test_estimated_analytics_requires_video_timeline(client):
    session = client.app.state.repo.save(Session(title="test", source=Source(kind=SourceKind.UPLOAD, uri="none")))
    assert client.get(f"/api/sessions/{session.session_id}/estimated-individual-analytics").status_code == 409
