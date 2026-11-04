"""Export publication failures and concurrent corrections must not leak partial results."""

import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from apps.web.e2e.score_fixture import create_score_fixture
from bai_api.analytics import AnalyticsCache
from bai_api.routes import exports
from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.events.match_phase import PhaseParams
from bai_engine.schema import MediaInfo, Provenance, Session, Source, SourceKind
from bai_engine.store import EventStore, SessionRepository


@pytest.fixture
def clip_setup(settings, monkeypatch):
    repo = SessionRepository(settings.data_dir)
    try:
        digest = "a" * 64
        media = MediaInfo(fps_num=30, fps_den=1, n_frames=120, width=640, height=360, duration_us=4_000_000)
        session = repo.save(Session(title="Clip", source=Source(kind=SourceKind.UPLOAD, uri="unused", sha256=digest),
                                    media=media))
        proxy = repo.media_paths(digest).proxy
        proxy.parent.mkdir(parents=True)
        proxy.write_bytes(b"controlled proxy placeholder; encoder is mocked")
        monkeypatch.setattr(exports.Tools, "resolve", lambda *args: SimpleNamespace(ffmpeg="controlled-ffmpeg"))
        yield repo, session, settings
    finally:
        repo.close()


def test_pdf_summary_and_rows_share_one_score_revision(tmp_path, monkeypatch):
    import bai_api.report

    repo = SessionRepository(tmp_path / "data")
    try:
        fixture = create_score_fixture(repo, "test-none", media=False)
        sid = fixture["session_id"]
        with EventStore(repo.events(sid).path, sid) as writer:
            engine = BadmintonMatchEngine(sid, EngineConfig(
                fps=30, frame_width=1280, frame_height=720,
                phase=PhaseParams(allow_heuristic_official=True),
            ), writer)
            engine.restore_from_log(fixture["frame"] + 1)
            cache = AnalyticsCache(repo)
            original_get = cache.get
            captured_summary, release = threading.Event(), threading.Event()
            rendered = []

            def get_summary(session_id):
                result = original_get(session_id)
                captured_summary.set()
                assert release.wait(timeout=10)
                return result

            def render(path, session, analytics, rows):
                rendered.append((analytics.score_timeline[-1]["score"], rows[-1]))
                path.write_bytes(b"controlled PDF renderer")

            monkeypatch.setattr(cache, "get", get_summary)
            monkeypatch.setattr(bai_api.report, "build_report", render)
            request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(analytics=cache)))
            with ThreadPoolExecutor(max_workers=1) as workers:
                response = workers.submit(exports.report_pdf, repo.get(sid), repo, request)
                try:
                    assert captured_summary.wait(timeout=10)
                    engine.correct_rally_winner(fixture["rally_event_ids"][1], "P1", Provenance(model="human"))
                finally:
                    release.set()
                response.result(timeout=10)
            summary, row = rendered[0]
            assert summary == {"P1": row["score_P1"], "P2": row["score_P2"]}
    finally:
        repo.close()


def _clip(setup):
    repo, session, settings = setup
    return exports.clip(session, repo, settings, frame_from=10, frame_to=30, pad_s=0)


def test_failed_clip_encoding_is_not_cached_as_a_success(clip_setup, monkeypatch):
    calls = []

    def encode(cmd, **kwargs):
        target = Path(cmd[-1])
        calls.append(target)
        target.write_bytes(b"partial" if len(calls) == 1 else b"complete")
        return SimpleNamespace(returncode=1 if len(calls) == 1 else 0)

    monkeypatch.setattr(exports.subprocess, "run", encode)
    with pytest.raises(HTTPException) as failed:
        _clip(clip_setup)
    assert failed.value.status_code == 500
    result = _clip(clip_setup)
    assert Path(result.path).read_bytes() == b"complete"
    assert len(calls) == 2


def test_clip_timeout_is_explicit_and_cannot_leave_a_cached_partial(clip_setup, monkeypatch):
    calls = 0

    def encode(cmd, **kwargs):
        nonlocal calls
        calls += 1
        Path(cmd[-1]).write_bytes(b"partial" if calls == 1 else b"complete")
        if calls == 1:
            raise subprocess.TimeoutExpired(cmd, kwargs["timeout"])
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(exports.subprocess, "run", encode)
    with pytest.raises(HTTPException) as failed:
        _clip(clip_setup)
    assert failed.value.status_code in (500, 504)
    assert Path(_clip(clip_setup).path).read_bytes() == b"complete"
    assert calls == 2


def test_concurrent_clip_request_never_receives_in_progress_bytes(clip_setup, monkeypatch):
    writing, release = threading.Event(), threading.Event()
    calls = 0
    lock = threading.Lock()

    def encode(cmd, **kwargs):
        nonlocal calls
        with lock:
            calls += 1
            first = calls == 1
        target = Path(cmd[-1])
        target.write_bytes(b"partial")
        if first:
            writing.set()
            assert release.wait(timeout=10)
        target.write_bytes(b"complete")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(exports.subprocess, "run", encode)
    with ThreadPoolExecutor(max_workers=2) as workers:
        initial = workers.submit(_clip, clip_setup)
        try:
            assert writing.wait(timeout=10)
            repeated = workers.submit(_clip, clip_setup)
            try:
                observed = Path(repeated.result(timeout=0.5).path).read_bytes()
            except TimeoutError:
                observed = None
        finally:
            release.set()
        assert Path(initial.result(timeout=10).path).read_bytes() == b"complete"
        assert Path(repeated.result(timeout=10).path).read_bytes() == b"complete"
    assert observed is None or observed == b"complete"


@pytest.mark.parametrize("changed_input", ["proxy", "timeline"])
def test_clip_cache_is_invalidated_when_its_input_changes(clip_setup, monkeypatch, changed_input):
    repo, session, settings = clip_setup

    def encode(cmd, **kwargs):
        start = cmd[cmd.index("-ss") + 1]
        source = Path(cmd[cmd.index("-i") + 1]).read_bytes()
        Path(cmd[-1]).write_bytes(start.encode() + b":" + source)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(exports.subprocess, "run", encode)
    old = Path(_clip(clip_setup).path).read_bytes()
    if changed_input == "proxy":
        repo.media_paths(session.source.sha256).proxy.write_bytes(b"replacement proxy content")
    else:
        repo.update(session.session_id, media=session.media.model_copy(update={"fps_num": 60}))
        session = repo.get(session.session_id)
    current = Path(_clip((repo, session, settings)).path).read_bytes()
    assert current != old


def test_proxy_replacement_during_clip_encoding_does_not_publish_mixed_input(clip_setup, monkeypatch):
    repo, session, _ = clip_setup
    proxy = repo.media_paths(session.source.sha256).proxy

    def encode(cmd, **kwargs):
        Path(cmd[-1]).write_bytes(b"encoded from the previous proxy generation")
        replacement = proxy.with_suffix(".replacement")
        replacement.write_bytes(b"replacement proxy generation")
        replacement.replace(proxy)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(exports.subprocess, "run", encode)
    with pytest.raises(HTTPException) as changed:
        _clip(clip_setup)
    assert changed.value.status_code == 409
    assert not list(repo.paths(session.session_id).exports.glob("*.mp4"))


def test_export_rallies_and_point_children_share_a_database_snapshot(tmp_path, monkeypatch):
    repo = SessionRepository(tmp_path / "data")
    try:
        fixture = create_score_fixture(repo, "test-none", media=False)
        sid = fixture["session_id"]
        reader = repo.events(sid)
        with EventStore(reader.path, sid) as writer:
            engine = BadmintonMatchEngine(sid, EngineConfig(
                fps=30, frame_width=1280, frame_height=720,
                phase=PhaseParams(allow_heuristic_official=True),
            ), writer)
            engine.restore_from_log(fixture["frame"] + 1)
            read_rallies, release = threading.Event(), threading.Event()
            query = reader.query

            def pause_after_rallies(**kwargs):
                rows = query(**kwargs)
                if kwargs.get("types") == ["rally_end"] and not read_rallies.is_set():
                    read_rallies.set()
                    assert release.wait(timeout=10)
                return rows

            monkeypatch.setattr(reader, "query", pause_after_rallies)
            with ThreadPoolExecutor(max_workers=1) as workers:
                response = workers.submit(exports._rally_rows, repo.get(sid), repo)
                try:
                    assert read_rallies.wait(timeout=10)
                    engine.correct_rally_winner(fixture["rally_event_ids"][1], "P1", Provenance(model="human"))
                finally:
                    release.set()
                rows = response.result(timeout=10)
            assert len(rows) == 2
            assert all(row["score_available"] for row in rows)
            assert [(row["score_P1"], row["score_P2"]) for row in rows] in (
                [(1, 0), (1, 1)], [(1, 0), (2, 0)],
            )
    finally:
        repo.close()
