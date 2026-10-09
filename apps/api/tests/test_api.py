from __future__ import annotations

import io
import shutil
import time
from pathlib import Path

import msgpack
import pytest
from conftest import make_video
from fastapi.testclient import TestClient

from bai_engine.config import Settings
from bai_engine.schema import Session, SessionStatus, Source, SourceKind

ffmpeg = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")


def _wait(client: TestClient, sid: str, statuses: set[str], timeout: float = 90) -> dict:
    t0 = time.time()
    while time.time() - t0 < timeout:
        s = client.get(f"/api/sessions/{sid}").json()
        if s["status"] in statuses:
            return s
        time.sleep(0.25)
    raise AssertionError(f"timeout waiting for {statuses}; last={s['status']} {s.get('status_detail')}")


def test_health_and_auth_disabled(client: TestClient) -> None:
    assert client.get("/api/health").json() == {"status": "ok"}
    me = client.get("/api/auth/me").json()
    assert me["authenticated"] and not me["auth_required"]
    assert client.get("/metrics").status_code == 200
    sysinfo = client.get("/api/system").json()
    assert sysinfo["profile"]["name"] == "test-none"
    assert any(m["name"] == "tracknetv3" for m in client.get("/api/models").json())


def test_rejects_bad_upload(client: TestClient) -> None:
    r = client.post("/api/sessions", files={"file": ("x.exe", b"MZ....", "application/octet-stream")})
    assert r.status_code == 422
    assert client.get("/api/sessions/does-not-exist").status_code == 404
    assert client.get("/api/sessions/..%2F..%2Fetc").status_code == 404


def test_youtube_gated(client: TestClient) -> None:
    r = client.post("/api/sessions/youtube", json={"url": "https://youtu.be/dQw4w9WgXcQ", "acknowledge_rights": True})
    assert r.status_code == 403


@ffmpeg
def test_upload_to_playback_end_to_end(client: TestClient, tmp_path: Path) -> None:
    video = make_video(tmp_path / "match.mp4", n=150)
    with video.open("rb") as f:
        r = client.post(
            "/api/sessions",
            files={"file": ("match.mp4", f, "video/mp4")},
            data={"title": "Test match", "player1": "Axelsen", "player2": "Momota"},
        )
    assert r.status_code == 201, r.text
    sid = r.json()["session_id"]
    s = _wait(client, sid, {"analysed", "failed"})
    assert s["status"] == "analysed", s
    assert s["media"]["n_frames"] == 150 and s["media"]["height"] == 360
    assert [p["name"] for p in s["players"]] == ["Axelsen", "Momota"]

    pl = client.get(f"/api/sessions/{sid}/hls/index.m3u8")
    assert pl.status_code == 200 and "#EXT-X-ENDLIST" in pl.text and pl.headers["cache-control"] == "no-cache"
    seg = client.get(f"/api/sessions/{sid}/hls/seg_00000.m4s")
    assert seg.status_code == 200 and len(seg.content) > 100
    assert client.get(f"/api/sessions/{sid}/hls/../../secret").status_code == 404

    tr = client.get(f"/api/sessions/{sid}/tracks", params={"from": 0, "to": 149})
    assert tr.status_code == 200 and msgpack.unpackb(tr.content)["v"] == 1

    ev = client.get(f"/api/sessions/{sid}/events").json()
    assert "last_seq" in ev
    legacy = client.get(f"/api/sessions/{sid}/exports/legacy.csv")
    assert legacy.text.startswith("start_time,end_time,win_point_player")
    pdf = client.get(f"/api/sessions/{sid}/exports/report.pdf")
    assert pdf.status_code == 200 and pdf.content[:4] == b"%PDF"
    clip = client.get(f"/api/sessions/{sid}/exports/clip.mp4", params={"from": 30, "to": 90, "pad_s": 0})
    assert clip.status_code == 200 and len(clip.content) > 1000

    with client.websocket_connect(f"/ws/sessions/{sid}") as ws:
        hello = msgpack.unpackb(ws.receive_bytes())
        assert hello["type"] == "hello" and hello["session"]["session_id"] == sid
        ws.send_bytes(msgpack.packb({"type": "seek", "frame": 60}))
        types = set()
        for _ in range(3):
            m = msgpack.unpackb(ws.receive_bytes())
            types.add(m["type"])
            if "state_at" in types:
                break
        assert "state_at" in types

    assert client.post(f"/api/sessions/{sid}/reanalyse").status_code == 202
    assert client.delete(f"/api/sessions/{sid}").status_code == 204
    assert client.get(f"/api/sessions/{sid}").status_code == 404


def _seed_match(settings: Settings) -> str:
    """A synthetic analysed match written straight into the store (no video needed)."""
    from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
    from bai_badminton.testing.synth import make_match
    from bai_engine.schema import MediaInfo
    from bai_engine.store import SessionRepository

    repo = SessionRepository(settings.data_dir)
    m = make_match(["P1", "P2", "P2", "P1", "P1", "P1", "P2", "P1"])
    s = repo.save(
        Session(
            title="Synthetic",
            source=Source(kind=SourceKind.UPLOAD, uri="none"),
            status=SessionStatus.ANALYSED,
            media=MediaInfo(
                fps_num=30,
                fps_den=1,
                n_frames=m.n_frames,
                width=1280,
                height=720,
                duration_us=int(m.n_frames / 30 * 1e6),
            ),
        )
    )
    eng = BadmintonMatchEngine(
        s.session_id, EngineConfig(fps=30, frame_width=1280, frame_height=720), repo.events(s.session_id)
    )
    eng.set_calibration(0, m.homography)
    from bai_engine.schema import PlayerInfo, TrackObject, samples_to_table

    ts = repo.tracks(s.session_id)
    for ch in m.chunks:
        eng.ingest(ch)
        samples = eng.drain_tracks()
        for obj in (TrackObject.SHUTTLE, TrackObject.PLAYER):
            part = [x for x in samples if x.obj is obj]
            if part:
                ts.write_chunk(obj, ch.start, ch.end, samples_to_table(part))
    eng.flush()
    repo.update(
        s.session_id,
        players=[PlayerInfo(player_id="P1", name="An Se Young"), PlayerInfo(player_id="P2", name="Tai Tzu Ying")],
    )
    repo.close()
    return s.session_id


def test_analytics_exports_and_corrections(settings: Settings) -> None:
    from bai_api.app import create_app

    sid = _seed_match(settings)
    with TestClient(create_app(settings)) as client:
        a = client.get(f"/api/sessions/{sid}/analytics").json()
        assert a["rallies"] == 8 and a["players"]["P1"]["points_won"] == 5
        hm = client.get(f"/api/sessions/{sid}/heatmap", params={"player": "P1", "kind": "presence"}).json()
        assert hm["shape"] and hm["total"] > 0
        assert client.get(f"/api/sessions/{sid}/heatmap", params={"player": "P9"}).status_code == 422
        hl = client.get(f"/api/sessions/{sid}/highlights", params={"player": "P2"}).json()["highlights"]
        assert all(h["player"] == "P2" for h in hl)
        csv = client.get(f"/api/sessions/{sid}/exports/rallies.csv").text.splitlines()
        assert len(csv) == 9 and "An Se Young" in csv[1] + csv[4]
        legacy = client.get(f"/api/sessions/{sid}/exports/legacy.csv").text.splitlines()
        assert len(legacy) == 9
        assert client.get(f"/api/sessions/{sid}/exports/report.pdf").content[:4] == b"%PDF"
        jl = client.get(f"/api/sessions/{sid}/exports/events.jsonl").text.splitlines()
        assert len(jl) > 20
        state = client.get(f"/api/sessions/{sid}/state").json()
        assert state["state"]["score"] == {"P1": 5, "P2": 3} and len(state["states"]) == 8


class _FakeProvider:
    """Calls a tool, then answers citing what the tool returned (exercises the grounded loop)."""

    name, model = "fake", "fake-1"

    def __init__(self) -> None:
        self.turn = 0

    def complete(self, system, messages, tools, *, max_tokens=4096, agent="agent"):  # type: ignore[no-untyped-def]
        import json

        from bai_agents.providers import LLMTurn, ToolCall

        self.turn += 1
        if self.turn == 1:
            return LLMTurn("", [ToolCall("t1", "list_rallies", {"winner": "An Se Young"})], "tool_use")
        res = json.loads(next(m for m in reversed(messages) if m["role"] == "tool")["content"])
        rid = res["rallies"][0]["rally_event_id"]
        return LLMTurn(f"An Se Young won {res['count']} rallies [[ev:{rid}]].", [], "end_turn")


def test_ask_grounded_and_fallback(settings: Settings, monkeypatch: pytest.MonkeyPatch) -> None:
    from bai_api.app import create_app
    from bai_api.routes import agents

    sid = _seed_match(settings)
    with TestClient(create_app(settings)) as client:
        monkeypatch.setattr(agents, "_provider", lambda: _FakeProvider())
        r = client.post(f"/api/sessions/{sid}/ask", json={"question": "How many rallies did An Se Young win?"}).json()
        assert r["grounded"], r["issues"]
        assert r["text"].startswith("An Se Young won 5 rallies")
        assert r["citations"][0]["type"] == "rally_end" and "frame" in r["citations"][0]
        monkeypatch.setattr(agents, "_provider", lambda: None)
        fb = client.post(f"/api/sessions/{sid}/ask", json={"question": "Summarise"}).json()
        assert fb["provider"] == "deterministic" and "automatic summary" in fb["text"]


def test_passphrase_auth(tmp_path: Path, settings: Settings) -> None:
    from pydantic import SecretStr

    from bai_api.app import create_app

    with pytest.raises(RuntimeError), TestClient(create_app(settings.model_copy(update={"bind_host": "0.0.0.0"}))):
        pass
    s2 = settings.model_copy(update={"passphrase": SecretStr("correct horse")})
    with TestClient(create_app(s2)) as c:
        assert c.get("/api/sessions").status_code == 401
        assert c.post("/api/auth/login", json={"passphrase": "nope"}).status_code == 401
        r = c.post("/api/auth/login", json={"passphrase": "correct horse"})
        assert r.status_code == 200
        csrf = r.json()["csrf"]
        assert c.get("/api/sessions").status_code == 200
        f = {"file": ("a.mp4", io.BytesIO(b"x"), "video/mp4")}
        assert c.post("/api/sessions", files=f).status_code == 403  # missing CSRF
        r2 = c.post(
            "/api/sessions", files={"file": ("a.mp4", io.BytesIO(b"x"), "video/mp4")}, headers={"X-CSRF-Token": csrf}
        )
        assert r2.status_code in (201, 422)
