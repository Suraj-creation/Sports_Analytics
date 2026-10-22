"""Product metrics must remain reproducible from persisted canonical evidence."""

from __future__ import annotations

import msgpack
from fastapi.testclient import TestClient
from pydantic import SecretStr
from test_api import _seed_match

from bai_api.app import create_app
from bai_engine.config import Settings
from bai_engine.schema import Session, SessionStatus, Source, SourceKind
from bai_engine.store import SessionRepository


def test_overview_empty_and_authenticated(settings: Settings) -> None:
    secured = settings.model_copy(update={"passphrase": SecretStr("private")})
    with TestClient(create_app(secured, start_engine=False)) as client:
        assert client.get("/api/analytics/overview").status_code == 401
        assert client.post("/api/auth/login", json={"passphrase": "private"}).status_code == 200
        data = client.get("/api/analytics/overview").json()
        assert data["matches"] == data["people"] == []
        assert data["progress"]["total_rallies"] == 0
        assert data["capabilities"]["doubles_individual_tracking"] is False


def test_overview_uses_canonical_totals_and_explicit_identity(settings: Settings) -> None:
    first, second = _seed_match(settings), _seed_match(settings)
    with TestClient(create_app(settings, start_engine=False)) as client:
        data = client.get("/api/analytics/overview").json()
        assert len(data["matches"]) == 2
        assert data["scope"]["truncated"] is False
        assert data["progress"]["total_rallies"] == 16
        assert data["progress"]["analysed_matches"] == 2
        people = {p["name"]: p for p in data["people"]}
        assert people["An Se Young"]["points_won"] == 10
        assert people["An Se Young"]["points_lost"] == 6
        assert people["An Se Young"]["win_rate"] == 0.625
        assert set(people["An Se Young"]["session_ids"]) == {first, second}
        for match in data["matches"]:
            assert match["availability"] == {"analytics": True, "partial": False, "reason": None}
            assert match["session"]["source"]["uri"] == ""
            assert match["lineage"]["event_seq"] > 0
            assert len(match["highlights"]) <= 10
        limited = client.get("/api/analytics/overview", params={"limit": 1}).json()
        assert limited["scope"] == {"limit": 1, "returned_matches": 1, "truncated": True}
        assert limited["progress"]["total_rallies"] == 8


def test_partial_and_unnamed_sessions_do_not_fabricate_people_or_results(settings: Settings) -> None:
    sid = _seed_match(settings)
    repo = SessionRepository(settings.data_dir)
    repo.update(sid, status=SessionStatus.ANALYSING)
    repo.save(Session(title="Unprocessed", source=Source(kind=SourceKind.UPLOAD, uri="/private/video.mp4")))
    repo.close()
    with TestClient(create_app(settings, start_engine=False)) as client:
        data = client.get("/api/analytics/overview").json()
        assert len(data["people"]) == 2  # named players only, never generic P1/P2
        assert all(p["points_won"] is None and p["win_rate"] is None for p in data["people"])
        assert data["progress"]["total_rallies"] == 0
        for item in data["matches"]:
            assert item["analytics"] is None and item["highlights"] == []
            assert item["availability"]["analytics"] is False
            assert item["availability"]["reason"]
            assert "/private" not in item["session"]["source"]["uri"]


def test_rally_insights_reconcile_and_keep_evidence(settings: Settings) -> None:
    sid = _seed_match(settings)
    with TestClient(create_app(settings, start_engine=False)) as client:
        data = client.get(f"/api/sessions/{sid}/insights").json()
        canonical = client.get(f"/api/sessions/{sid}/events", params={"types": "rally_end"}).json()["events"]
        assert len(data["rallies"]) == 8
        assert {r["rally_id"] for r in data["rallies"]} == {e["event_id"] for e in canonical}
        assert sum(r["winner"] == "P1" for r in data["rallies"]) == 5
        assert all(r["start_s"] == round(r["frame_start"] / 30, 3) for r in data["rallies"])
        assert all("confidence" in r and "status" in r for r in data["rallies"])
        p1 = data["tactics"]["P1"]
        assert sum(x["count"] for x in p1["shot_distribution"]) > 0
        assert p1["serve_win_rate"] is None or 0 <= p1["serve_win_rate"] <= 1
        assert client.get("/api/sessions/missing/insights").status_code == 404


def test_overview_rebuilds_after_correction_and_identity_rename(settings: Settings) -> None:
    sid = _seed_match(settings)
    with TestClient(create_app(settings, start_engine=False)) as client:
        before = client.get("/api/analytics/overview").json()
        repo = client.app.state.repo
        ev = next(e for e in repo.events(sid).query(types=["rally_end"]) if e.payload.get("winner") == "P1")
        payload = dict(ev.payload, winner="P2", loser="P1")
        repo.events(sid).append(ev.correct(payload=payload))
        after = client.get("/api/analytics/overview").json()
        person = next(p for p in after["people"] if p["name"] == "An Se Young")
        assert person["points_won"] == 4
        assert after["matches"][0]["lineage"]["event_seq"] > before["matches"][0]["lineage"]["event_seq"]
        assert client.patch(f"/api/sessions/{sid}", json={"player1": "New name"}).status_code == 200
        renamed = client.get("/api/analytics/overview").json()
        assert "New name" in {p["name"] for p in renamed["people"]}
        assert "An Se Young" not in {p["name"] for p in renamed["people"]}


def test_cache_rebuilds_same_sequence_after_analysis_reset(settings: Settings) -> None:
    from bai_api.analytics import AnalyticsCache

    sid = _seed_match(settings)
    repo = SessionRepository(settings.data_dir)
    cache = AnalyticsCache(repo)
    original = cache.get(sid)
    assert len(original.rallies) == 8
    old_events = repo.events(sid).query(live_only=False)
    repo.reset_analysis(sid)
    for event in old_events:
        # Keep sequence length identical but change the canonical winner evidence.
        if event.type == "rally_end":
            event = event.model_copy(update={"payload": dict(event.payload, winner=None, loser=None)})
        repo.events(sid).append(event.model_copy(update={"seq": None}))
    rebuilt = cache.get(sid)
    assert rebuilt is not original
    assert all(r.winner is None for r in rebuilt.rallies)
    repo.close()


def test_cache_invalidates_track_revision_without_new_events(settings: Settings) -> None:
    from bai_api.analytics import AnalyticsCache
    from bai_engine.schema import TrackObject

    sid = _seed_match(settings)
    repo = SessionRepository(settings.data_dir)
    cache = AnalyticsCache(repo)
    first = cache.get(sid)
    assert cache.get(sid) is first
    track_store = repo.tracks(sid)
    start, end = track_store.covered_ranges(TrackObject.PLAYER)[0]
    table = track_store.read([TrackObject.PLAYER], start, end)
    track_store.write_chunk(TrackObject.PLAYER, start, end, table)
    assert cache.get(sid) is not first
    repo.close()


def test_missing_coordinates_are_null_distance_not_zero(settings: Settings) -> None:
    sid = _seed_match(settings)
    repo = SessionRepository(settings.data_dir)
    # Events remain; an empty TrackStore is a valid absence of coordinate evidence.
    repo.paths(sid).tracks.rename(repo.paths(sid).root / "tracks.saved")
    repo.close()
    with TestClient(create_app(settings, start_engine=False)) as client:
        data = client.get("/api/analytics/overview").json()
        assert data["matches"][0]["availability"]["analytics"] is True
        assert data["matches"][0]["analytics"]["players"]["P1"]["distance_m"] is None
        assert all(p["distance_m"] is None for p in data["people"])


def test_session_responses_hide_source_locations_without_mutating_storage(settings: Settings) -> None:
    sid = _seed_match(settings)
    repo = SessionRepository(settings.data_dir)
    private_uri = "/private/server/recordings/original.mp4"
    repo.update(sid, source=Source(kind=SourceKind.UPLOAD, uri=private_uri))
    repo.close()
    enabled = settings.model_copy(update={"youtube_ingest": True})
    with TestClient(create_app(enabled, start_engine=False)) as client:
        assert client.get("/api/sessions").json()[0]["source"]["uri"] == ""
        assert client.get(f"/api/sessions/{sid}").json()["source"]["uri"] == ""
        assert client.patch(f"/api/sessions/{sid}", json={"title": "Renamed"}).json()["source"]["uri"] == ""
        summary = client.get(f"/api/sessions/{sid}/exports/summary.json").json()
        assert summary["session"]["source"]["uri"] == ""
        with client.websocket_connect(f"/ws/sessions/{sid}") as ws:
            hello = msgpack.unpackb(ws.receive_bytes())
            assert hello["session"]["source"]["uri"] == ""
        assert client.app.state.repo.get(sid).source.uri == private_uri
        uploaded = client.post("/api/sessions", files={"file": ("match.mp4", b"video-data", "video/mp4")})
        assert uploaded.status_code == 201
        assert uploaded.json()["source"]["uri"] == ""
        assert client.app.state.repo.get(uploaded.json()["session_id"]).source.uri.endswith("source.mp4")
        youtube = client.post(
            "/api/sessions/youtube",
            json={
                "url": "https://youtu.be/dQw4w9WgXcQ",
                "acknowledge_rights": True,
            },
        )
        assert youtube.status_code == 201
        assert youtube.json()["source"]["uri"] == ""
        assert client.app.state.repo.get(youtube.json()["session_id"]).source.uri.startswith("https://www.youtube.com/")


def test_delete_refuses_a_writer_that_survives_stop(settings: Settings) -> None:
    from bai_engine.bus import LocalBus
    from bai_engine.runtime.runner import EngineService

    class StubbornWriter:
        def is_alive(self) -> bool:
            return True

        def stop(self) -> None:
            pass

        def join(self, timeout: float) -> None:
            pass

    sid = _seed_match(settings)
    with TestClient(create_app(settings, start_engine=False)) as client:
        repo = client.app.state.repo
        engine = EngineService(repo, LocalBus(), settings)
        writer = StubbornWriter()
        engine.runners[sid] = writer  # type: ignore[assignment]
        client.app.state.engine = engine
        try:
            before = repo.events(sid).last_seq()
            response = client.delete(f"/api/sessions/{sid}")
            assert response.status_code == 409
            assert (
                response.json()["detail"]
                == "The recording is still processing. Wait for its worker to stop, then retry deletion."
            )
            assert repo.get(sid) is not None
            assert repo.events(sid).last_seq() == before
            assert engine.runners[sid] is writer
            assert repo.paths(sid).tracks.exists()
        finally:
            # This fake represents an external writer; never let app teardown manage it.
            client.app.state.engine = None
