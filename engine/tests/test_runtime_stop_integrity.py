"""A stopped runner must relinquish every owned media writer before deletion/retry."""

import threading
from fractions import Fraction
from types import SimpleNamespace

import pytest

from bai_engine.bus import LocalBus
from bai_engine.config import Settings
from bai_engine.media.ffmpeg import FFmpegJob, MediaError
from bai_engine.media.probe import ProbeResult
from bai_engine.media.proxy import HlsStatus, ProxyPlan
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.runtime.runner import SessionRunner
from bai_engine.schema import Session, SessionStatus, Source, SourceKind
from bai_engine.store import SessionRepository


class BlockingJob:
    def __init__(self):
        self.started = threading.Event()
        self.cancelled = threading.Event()
        self.release = threading.Event()
        self.finished = threading.Event()

    def run(self):
        self.started.set()
        if not self.release.wait(timeout=10):
            raise TimeoutError("test media writer was not released")
        self.finished.set()
        raise MediaError("cancelled")

    def cancel(self):
        self.cancelled.set()


def make_runner(tmp_path, monkeypatch, job):
    repo = SessionRepository(tmp_path / "data")
    source = tmp_path / "source.mp4"
    source.write_bytes(b"controlled media metadata")
    session = repo.save(Session(title="Stop test", source=Source(
        kind=SourceKind.UPLOAD, uri=str(source), sha256="a" * 64,
    )))
    settings = Settings(data_dir=repo.data_dir, _env_file=None)
    runner = SessionRunner(session.session_id, repo, LocalBus(), settings, ModelRegistry(settings.models_dir))
    monkeypatch.setattr("bai_engine.runtime.runner.probe", lambda *args: ProbeResult(
        "mov,mp4,m4a,3gp,3g2,mj2", 10, 640, 360, "h264", Fraction(30), Fraction(30), 300, False,
    ))
    monkeypatch.setattr("bai_engine.runtime.runner.plan_proxy", lambda *args, **kwargs: ProxyPlan(
        Fraction(30), 360, 60, "libx264", False,
    ))
    monkeypatch.setattr("bai_engine.runtime.runner.hls_status", lambda *args: HlsStatus(0, False, ()))
    monkeypatch.setattr("bai_engine.runtime.runner.transcode", lambda *args, **kwargs: job)
    return runner, repo


def test_stop_cancels_and_joins_media_writer_before_runner_exits(tmp_path, monkeypatch):
    job = BlockingJob()
    runner, repo = make_runner(tmp_path, monkeypatch, job)
    runner.start()
    try:
        assert job.started.wait(timeout=3)
        runner.stop()
        assert job.cancelled.wait(timeout=1), "Stop left FFmpeg writing shared media"
        runner.join(timeout=0.05)
        assert runner.is_alive(), "Runner exited before its media writer released the files"
        job.release.set()
        runner.join(timeout=3)
        assert not runner.is_alive() and job.finished.is_set()
        saved = repo.get(runner.session_id)
        assert saved.status is SessionStatus.FAILED
        assert "stop" in saved.status_detail.lower()
    finally:
        job.release.set()
        runner.stop()
        runner.join(timeout=3)
        if runner._transcode_thread is not None:
            runner._transcode_thread.join(timeout=3)
        repo.close()


def test_unexpected_media_worker_failure_reaches_terminal_session_state(tmp_path, monkeypatch):
    cancelled = threading.Event()

    def fail():
        raise OSError("encoder process could not start")

    runner, repo = make_runner(tmp_path, monkeypatch, SimpleNamespace(run=fail, cancel=cancelled.set))
    runner.start()
    try:
        runner.join(timeout=1)
        assert not runner.is_alive(), "Media worker died but the session kept waiting for its first segment"
        saved = repo.get(runner.session_id)
        assert saved.status is SessionStatus.FAILED
        assert "encoder process" in saved.status_detail
        assert cancelled.is_set(), "A failed media thread left its registered job unclosed"
    finally:
        runner.stop()
        runner.join(timeout=3)
        repo.close()


def test_cancelled_job_does_not_start_a_new_process(monkeypatch):
    job = FFmpegJob(["unused-ffmpeg"])
    job.cancel()

    def unexpected(*args, **kwargs):
        raise AssertionError("A cancelled job spawned FFmpeg")

    monkeypatch.setattr("bai_engine.media.ffmpeg.subprocess.Popen", unexpected)
    with pytest.raises(MediaError, match="cancelled"):
        job.run()


def test_progress_callback_failure_kills_and_reaps_encoder(monkeypatch):
    killed, reaped = threading.Event(), threading.Event()

    def fail_progress(_):
        raise RuntimeError("transport unavailable")

    def wait():
        assert killed.is_set(), "A failing progress callback left an encoder running"
        reaped.set()
        return -9

    process = SimpleNamespace(
        stdout=[b"out_time_us=1\n"], stderr=[], kill=killed.set,
        poll=lambda: -9 if killed.is_set() else None, wait=wait,
    )
    monkeypatch.setattr("bai_engine.media.ffmpeg.subprocess.Popen", lambda *args, **kwargs: process)
    with pytest.raises(RuntimeError, match="transport unavailable"):
        FFmpegJob(["unused-ffmpeg"], on_progress=fail_progress).run()
    assert killed.is_set() and reaped.is_set()


def test_cancel_during_process_creation_is_applied_before_wait(monkeypatch):
    job = FFmpegJob(["unused-ffmpeg"])
    killed = threading.Event()

    def wait():
        assert killed.is_set(), "Cancellation between Popen and assignment was lost"
        return -9

    process = SimpleNamespace(stdout=[], stderr=[], kill=killed.set, poll=lambda: None, wait=wait)

    def spawn(*args, **kwargs):
        job.cancel()
        return process

    monkeypatch.setattr("bai_engine.media.ffmpeg.subprocess.Popen", spawn)
    with pytest.raises(MediaError, match="cancelled"):
        job.run()
