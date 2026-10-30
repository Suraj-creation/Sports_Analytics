"""Reimporting a recording must open its saved analysis without starting a worker."""

from fastapi.testclient import TestClient

from bai_api.app import create_app
from bai_engine.bus import LocalBus
from bai_engine.schema import Session, SessionStatus, Source, SourceKind


def test_upload_reuses_saved_session_and_preserves_calibration(settings):
    bus = LocalBus()
    with TestClient(create_app(settings, bus=bus, start_engine=False)) as client:
        first = client.post("/api/sessions", files={"file": ("match.mp4", b"same recording", "video/mp4")})
        sid = first.json()["session_id"]
        repo = client.app.state.repo
        repo.update(sid, status=SessionStatus.ANALYSED, meta={"saved_calibration": "keep"})
        assert bus.next_command(timeout=0.01)["cmd"] == "start"
        again = client.post("/api/sessions", files={"file": ("renamed.mp4", b"same recording", "video/mp4")})
        assert again.status_code == 200
        assert again.json()["session_id"] == sid
        assert again.json()["meta"]["saved_calibration"] == "keep"
        assert len(repo.list()) == 1
        assert bus.next_command(timeout=0.01) is None


def test_youtube_variants_reuse_same_session_without_redownload(settings):
    bus = LocalBus()
    settings.youtube_ingest = True
    with TestClient(create_app(settings, bus=bus, start_engine=False)) as client:
        first = client.post(
            "/api/sessions/youtube", json={"url": "https://youtu.be/dQw4w9WgXcQ", "acknowledge_rights": True}
        )
        sid = first.json()["session_id"]
        repo = client.app.state.repo
        saved = repo.get(sid)
        assert saved.meta.get("youtube_video_id") == "dQw4w9WgXcQ"
        # The downloader replaces the URL with a local path. Identity must survive it.
        repo.update(
            sid, source=saved.source.model_copy(update={"uri": "/local/source.mp4"}), status=SessionStatus.ANALYSED
        )
        assert bus.next_command(timeout=0.01)["cmd"] == "start"
        again = client.post(
            "/api/sessions/youtube",
            json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30", "acknowledge_rights": True},
        )
        assert again.status_code == 200
        assert again.json()["session_id"] == sid
        assert len(repo.list()) == 1
        assert bus.next_command(timeout=0.01) is None


def test_reading_saved_session_does_not_start_analysis(settings):
    bus = LocalBus()
    with TestClient(create_app(settings, bus=bus, start_engine=False)) as client:
        repo = client.app.state.repo
        saved = repo.save(
            Session(title="Done", status=SessionStatus.ANALYSED, source=Source(kind=SourceKind.UPLOAD, uri="local.mp4"))
        )
        assert client.get(f"/api/sessions/{saved.session_id}").json()["status"] == "analysed"
        with client.websocket_connect(f"/ws/sessions/{saved.session_id}") as ws:
            ws.receive_bytes()
            ws.send_json({"type": "seek", "frame": 10})
            ws.receive_bytes()
        command = bus.next_command(timeout=0.01)
        assert command is None or command["cmd"] == "playhead"
        assert repo.get(saved.session_id).status is SessionStatus.ANALYSED


def test_new_profile_keeps_separate_analysis(settings):
    bus = LocalBus()
    with TestClient(create_app(settings, bus=bus, start_engine=False)) as client:
        first = client.post("/api/sessions", files={"file": ("match.mp4", b"same", "video/mp4")})
        different = client.post(
            "/api/sessions", files={"file": ("match.mp4", b"same", "video/mp4")}, data={"profile": "cpu-dev"}
        )
        assert different.status_code == 201
        assert different.json()["session_id"] != first.json()["session_id"]
