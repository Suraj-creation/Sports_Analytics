"""A stateful sport must never mix cached chunks or advance a preview cursor."""

import threading
from types import SimpleNamespace

import msgpack
import pytest

from bai_engine.runtime import runner as runtime


class Sport:
    def __init__(self, sequential):
        self.requires_sequential_perception = sequential
        self.fresh = []
        self.cached = []
        self.ingested = []

    def perceive(self, chunk):
        if self.requires_sequential_perception and self.fresh:
            assert chunk.start > self.fresh[-1], "stateful matcher received out-of-order frames"
        self.fresh.append(chunk.start)
        return SimpleNamespace(start=chunk.start, end=chunk.end, origin="fresh")

    def decode_perception(self, data):
        value = SimpleNamespace(**msgpack.unpackb(data, raw=False))
        self.cached.append(value.start)
        return value

    def encode_perception(self, value):
        return msgpack.packb(vars(value), use_bin_type=True)

    def degraded(self):
        return []

    def seed(self, frames):
        pass

    def ingest(self, value):
        self.ingested.append(value.start)

    def tracks_from_perception(self, value):
        return []

    def drain_tracks(self):
        return []

    def flush(self):
        pass

    def public_state(self):
        return {}

    def analytics(self):
        return {}


class Decoder:
    def decode_segment(self, segment):
        return SimpleNamespace(start=segment * 64, end=segment * 64 + 63)


def runner(tmp_path, sport):
    value = runtime.SessionRunner.__new__(runtime.SessionRunner)
    value.session_id = "session"
    session = SimpleNamespace(media=object(), profile="test", source=SimpleNamespace(sha256="media"), meta={})
    value.repo = SimpleNamespace(
        get=lambda _: session,
        paths=lambda _: SimpleNamespace(root=tmp_path),
        media_paths=lambda _: tmp_path,
    )
    value.sport = sport
    value.plan = SimpleNamespace(frames_per_segment=64, fps=30)
    value.settings = SimpleNamespace(profiles_dir=tmp_path)
    value.shared = SimpleNamespace(stop=threading.Event(), playhead=0)
    value.bus = SimpleNamespace(publish=lambda *_: None)
    value._transcode_error = None
    value._create_sport = lambda: sport
    value._sample_keyframes = lambda: []
    value._status = lambda *_, **__: None
    value._progress = lambda *_: None
    value._drain_commands = lambda: None
    value._publish_tracks = lambda *_, **__: None
    value._apply_carried = lambda: None
    return value


@pytest.mark.parametrize("sequential,expected", [(True, "fresh"), (False, "cached")])
def test_stateful_mode_bypasses_existing_cache_and_still_writes_diagnostics(tmp_path, sequential, expected):
    sport = Sport(sequential)
    value = runner(tmp_path, sport)
    cache = value._cache_path(0)
    cache.write_bytes(sport.encode_perception(SimpleNamespace(start=0, end=63, origin="cached")))
    result = value._perceive(Decoder(), 0)
    assert result.origin == expected
    assert sport.cached == ([] if sequential else [0])
    assert sport.fresh == ([0] if sequential else [])
    assert msgpack.unpackb(cache.read_bytes(), raw=False)["origin"] == expected


@pytest.mark.parametrize("sequential", [True, False])
def test_only_stateless_mode_runs_seek_ahead_preview(tmp_path, monkeypatch, sequential):
    sport = Sport(sequential)
    value = runner(tmp_path, sport)
    value.shared.playhead = 320
    monkeypatch.setattr(runtime, "load_profile", lambda *_: SimpleNamespace(lead_buffer_s=1))
    monkeypatch.setattr(runtime, "SegmentDecoder", lambda *_: Decoder())
    monkeypatch.setattr(runtime, "hls_status", lambda *_: SimpleNamespace(segments=6, ended=True))
    value._analyse()
    assert sport.ingested == [0, 64, 128, 192, 256, 320]
    if sequential:
        assert sport.fresh == [0, 64, 128, 192, 256, 320]
        assert sport.cached == []
    else:
        assert sport.fresh == [320, 0, 64, 128, 192, 256]
        assert sport.cached == [320]


def test_cold_stateful_runner_rebuilds_every_chunk_instead_of_mixing_cached_birth_namespaces(tmp_path, monkeypatch):
    sport = Sport(True)
    value = runner(tmp_path, sport)
    # Cached frame zero and 128 used one continuous matcher. Skipping either
    # lets a cold frame-64 matcher allocate ID 1025 to a different person.
    for segment in (0, 2):
        value._cache_path(segment).write_bytes(
            sport.encode_perception(SimpleNamespace(start=segment * 64, end=segment * 64 + 63, origin="cached"))
        )
    monkeypatch.setattr(runtime, "load_profile", lambda *_: SimpleNamespace(lead_buffer_s=1))
    monkeypatch.setattr(runtime, "SegmentDecoder", lambda *_: Decoder())
    monkeypatch.setattr(runtime, "hls_status", lambda *_: SimpleNamespace(segments=3, ended=True))
    value._analyse()
    assert sport.fresh == [0, 64, 128]
    assert sport.cached == []
