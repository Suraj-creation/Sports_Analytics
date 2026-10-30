"""Opening completed and interrupted analyses never silently clears saved work."""

from bai_engine.bus import LocalBus
from bai_engine.config import Settings
from bai_engine.runtime.runner import EngineService
from bai_engine.schema import Session, SessionStatus, Source, SourceKind
from bai_engine.store import SessionRepository


def test_completed_empty_detection_result_is_not_analysed_again(tmp_path):
    repo = SessionRepository(tmp_path)
    session = repo.save(
        Session(
            title="No detections",
            status=SessionStatus.ANALYSED,
            source=Source(kind=SourceKind.UPLOAD, uri="source.mp4"),
        )
    )
    service = EngineService(repo, LocalBus(), Settings(data_dir=tmp_path, _env_file=None))
    assert service._prepare_start(session.session_id) is True
    assert not (tmp_path / "backups").exists()
    repo.close()


def test_restart_marks_stale_jobs_interrupted_without_clearing_results(tmp_path):
    repo = SessionRepository(tmp_path)
    session = repo.save(
        Session(
            title="Interrupted",
            status=SessionStatus.ANALYSING,
            frontier_frame=119,
            analysed_frames=120,
            source=Source(kind=SourceKind.UPLOAD, uri="source.mp4"),
        )
    )
    store = repo.events(session.session_id)
    store.set_meta("calibration", "saved")
    done = repo.save(
        Session(title="Done", status=SessionStatus.ANALYSED, source=Source(kind=SourceKind.UPLOAD, uri="other.mp4"))
    )
    service = EngineService(repo, LocalBus(), Settings(data_dir=tmp_path, _env_file=None))
    service.start()
    try:
        saved = repo.get(session.session_id)
        assert saved.status is SessionStatus.FAILED
        assert "interrupt" in saved.status_detail.lower()
        assert saved.analysed_frames == 120 and saved.frontier_frame == 119
        assert repo.events(session.session_id).get_meta("calibration") == "saved"
        assert repo.get(done.session_id).status is SessionStatus.ANALYSED
        assert not service.runners
    finally:
        service.shutdown()
        service._thread.join(timeout=2)
        repo.close()


def test_legacy_youtube_download_opens_existing_results_without_pipeline(tmp_path, monkeypatch):
    from bai_engine.runtime.registry import ModelRegistry
    from bai_engine.runtime.runner import SessionRunner
    from bai_engine.schema import MediaInfo
    from bai_engine.sources import StoredMedia, YouTubeSource

    repo = SessionRepository(tmp_path)
    source_file = tmp_path / "original.mp4"
    source_file.write_bytes(b"saved video")
    sha = "a" * 64
    old = repo.save(
        Session(
            title="Existing match",
            status=SessionStatus.ANALYSED,
            source=Source(kind=SourceKind.YOUTUBE, uri=str(source_file), sha256=sha),
            media=MediaInfo(fps_num=30, fps_den=1, n_frames=90, width=320, height=180, duration_us=3000000),
            analysed_frames=90,
            frontier_frame=89,
        )
    )
    repo.events(old.session_id).set_meta("manual-calibration", "keep")
    pending = repo.save(
        Session(
            title="YouTube video",
            source=Source(kind=SourceKind.YOUTUBE, uri="https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
            meta={"youtube_video_id": "dQw4w9WgXcQ"},
        )
    )
    monkeypatch.setattr(YouTubeSource, "download", lambda *a, **k: StoredMedia(sha, source_file, 11, "Existing match"))
    settings = Settings(data_dir=tmp_path, _env_file=None)
    runner = SessionRunner(pending.session_id, repo, LocalBus(), settings, ModelRegistry(settings.models_dir))

    def unexpected(*args, **kwargs):
        raise AssertionError("saved results must bypass media processing and analysis")

    monkeypatch.setattr(runner, "_analyse", unexpected)
    monkeypatch.setattr("bai_engine.runtime.runner.probe", unexpected)
    runner.run()
    alias = repo.get(pending.session_id)
    assert alias.meta.get("reused_session_id") == old.session_id
    assert alias.status is SessionStatus.ANALYSED and alias.analysed_frames == 90
    assert repo.events(old.session_id).get_meta("manual-calibration") == "keep"
    assert repo.get(old.session_id).meta["youtube_video_id"] == "dQw4w9WgXcQ"
    assert [s.session_id for s in repo.list()] == [old.session_id]
    assert not (tmp_path / "backups").exists()
    repo.close()


def test_retry_of_eventless_partial_analysis_backs_up_tracks(tmp_path):
    repo = SessionRepository(tmp_path)
    session = repo.save(
        Session(
            title="Partial",
            status=SessionStatus.FAILED,
            frontier_frame=119,
            analysed_frames=120,
            source=Source(kind=SourceKind.UPLOAD, uri="source.mp4"),
        )
    )
    tracks = repo.paths(session.session_id).tracks
    tracks.mkdir()
    (tracks / "saved.parquet").write_bytes(b"partial tracking")
    service = EngineService(repo, LocalBus(), Settings(data_dir=tmp_path, _env_file=None))
    assert service._prepare_start(session.session_id) is False
    backups = list((tmp_path / "backups" / session.session_id).glob("*"))
    assert len(backups) == 1
    assert (backups[0] / "tracks" / "saved.parquet").read_bytes() == b"partial tracking"
    assert repo.get(session.session_id).analysed_frames == 0
    repo.close()
