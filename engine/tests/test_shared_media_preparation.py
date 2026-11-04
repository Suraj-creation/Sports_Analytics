"""Independent sessions must not overwrite the same proxy/HLS concurrently."""

import threading
from fractions import Fraction

import pytest

from bai_engine.bus import LocalBus
from bai_engine.config import Settings
from bai_engine.media.probe import ProbeResult
from bai_engine.media.proxy import HlsStatus, ProxyPlan
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.runtime.runner import SessionRunner
from bai_engine.schema import Session, Source, SourceKind
from bai_engine.store import SessionRepository


@pytest.fixture
def preparation(tmp_path, monkeypatch):
    states, jobs, repositories, runners = {}, [], [], []
    release = threading.Event()
    guard = threading.Lock()

    class Job:
        def __init__(self, media, first):
            self.media, self.first = media, first

        def run(self):
            states[self.media.root] = HlsStatus(1, False, (2.0,))
            if self.first:
                assert release.wait(5), "test did not release the first writer"
            states[self.media.root] = HlsStatus(2, True, (2.0, 1.0))

        def cancel(self):
            pass

    def transcode(_src, media, *args, **kwargs):
        with guard:
            job = Job(media, not jobs)
            jobs.append(job)
            return job

    def make(digest="a" * 64):
        repo = SessionRepository(tmp_path / "data")
        repositories.append(repo)
        source = tmp_path / "source.mp4"
        source.write_bytes(b"controlled source metadata")
        session = repo.save(Session(title="Shared media", source=Source(
            kind=SourceKind.UPLOAD, uri=str(source), sha256=digest,
        )))
        settings = Settings(data_dir=repo.data_dir, _env_file=None)
        runner = SessionRunner(session.session_id, repo, LocalBus(), settings, ModelRegistry(settings.models_dir))
        runners.append(runner)
        return runner

    monkeypatch.setattr("bai_engine.runtime.runner.probe", lambda *a: ProbeResult(
        "mov,mp4,m4a,3gp,3g2,mj2", 10, 640, 360, "h264", Fraction(30), Fraction(30), 300, False,
    ))
    monkeypatch.setattr("bai_engine.runtime.runner.plan_proxy", lambda *a, **k: ProxyPlan(
        Fraction(30), 360, 60, "libx264", False,
    ))
    monkeypatch.setattr("bai_engine.runtime.runner.hls_status", lambda mp: states.get(
        mp.root, HlsStatus(0, False, ()),
    ))
    monkeypatch.setattr("bai_engine.runtime.runner.transcode", transcode)
    monkeypatch.setattr("bai_engine.runtime.runner.build_sprite", lambda *a, **k: None)
    yield make, release, jobs
    release.set()
    for runner in runners:
        runner.stop()
        if runner._transcode_thread is not None:
            runner._transcode_thread.join(3)
    for repo in repositories:
        repo.close()


def test_same_media_has_one_writer_and_both_sessions_get_final_frame_count(preparation):
    make, release, jobs = preparation
    first, second = make(), make()
    first._ensure_media()
    second._ensure_media()
    release.set()
    for runner in (first, second):
        runner._transcode_thread.join(3)
        assert not runner._transcode_thread.is_alive()
    assert len(jobs) == 1, "two encoders wrote the same content-addressed proxy/HLS"
    assert first.session.media.n_frames == second.session.media.n_frames == 90


def test_stopping_a_waiting_session_does_not_wait_for_or_cancel_the_owner(preparation):
    make, release, jobs = preparation
    first, second = make(), make()
    first._ensure_media()
    second._ensure_media()
    second.stop()
    second._transcode_thread.join(1)
    assert not second._transcode_thread.is_alive(), "cancelled waiter retained a media thread"
    assert first._transcode_thread.is_alive() and not release.is_set()
    assert len(jobs) == 1, "a waiting/cancelled session started another encoder"


def test_different_media_can_prepare_while_the_first_writer_is_busy(preparation):
    make, release, jobs = preparation
    first, second = make(), make("b" * 64)
    first._ensure_media()
    second._ensure_media()
    second._transcode_thread.join(1)
    assert not second._transcode_thread.is_alive()
    assert first._transcode_thread.is_alive() and not release.is_set()
    assert len(jobs) == 2
