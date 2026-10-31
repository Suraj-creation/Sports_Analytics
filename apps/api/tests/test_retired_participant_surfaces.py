"""Legacy aliases stay retired; restored scoped review routes require current evidence."""

from fastapi.testclient import TestClient

from bai_api.app import create_app
from bai_engine.schema import Event, EventStatus, Provenance, Session, Source, SourceKind

REMOVED_PATHS = (
    "/api/sessions/{session_id}/episode-movement",
    "/api/sessions/{session_id}/participant-observations/{observation_id}/box",
    "/api/sessions/{session_id}/strokes/{stroke_id}/participant-review",
)


def test_retired_review_and_track_movement_are_not_registered(settings):
    app = create_app(settings, start_engine=False)
    assert set(REMOVED_PATHS).isdisjoint(app.openapi()["paths"])
    paths = app.openapi()["paths"]
    assert "/__test__/review-fixture/{session_id}" not in paths
    assert {"get", "post"} <= paths["/api/sessions/{session_id}/identity-reviews"].keys()
    assert "post" in paths["/api/sessions/{session_id}/stroke-participant-reviews"]


def test_retired_endpoints_cannot_mutate_historical_reviews(settings):
    with TestClient(create_app(settings, start_engine=False)) as client:
        repo = client.app.state.repo
        session = repo.save(Session(title="Historical review", source=Source(kind=SourceKind.UPLOAD, uri="none")))
        store = repo.events(session.session_id)
        historical = [
            store.append(
                Event(
                    session_id=session.session_id,
                    type=kind,
                    frame_start=5,
                    frame_end=10,
                    pts_us=0,
                    payload={"scope": "reviewed_interval" if kind == "identity_review" else "participant_only"},
                    status=EventStatus.HUMAN_VERIFIED,
                    provenance=Provenance(model="human", worker="review-ui"),
                )
            )
            for kind in ("identity_review", "stroke_participant_review")
        ]
        root = f"/api/sessions/{session.session_id}"
        requests = (
            ("GET", "/episode-movement?from=0&to=10", {404, 405}),
            ("GET", "/participant-observations/observation/box?frame=5", {404, 405}),
            ("GET", "/identity-reviews", {409}),
            ("POST", "/identity-reviews", {422}),
            ("DELETE", f"/identity-reviews/{historical[0].event_id}", {422}),
            ("GET", "/stroke-participant-reviews", {404, 405}),
            ("POST", "/strokes/stroke/participant-review", {404, 405}),
            ("DELETE", f"/stroke-participant-reviews/{historical[1].event_id}", {422}),
        )
        for method, path, expected in requests:
            response = client.request(method, root + path, json={} if method == "POST" else None)
            assert response.status_code in expected, (method, path, response.status_code)
        response = client.get(root + "/events", params={"types": "identity_review,stroke_participant_review"})
        assert response.status_code == 200
        events = response.json()["events"]
        assert [event["event_id"] for event in events] == [event.event_id for event in historical]
        assert all(event["status"] == "human_verified" for event in events)
        assert store.last_seq() == len(historical)
