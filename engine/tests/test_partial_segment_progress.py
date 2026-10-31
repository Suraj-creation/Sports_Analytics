from types import SimpleNamespace
from unittest.mock import MagicMock

from bai_engine.runtime import runner as runtime


def test_final_partial_segment_reports_actual_perception_end(monkeypatch):
    r = runtime.SessionRunner.__new__(runtime.SessionRunner)
    r.session_id = "s"
    r.repo = MagicMock()
    r.repo.get.return_value = SimpleNamespace(media=object(), profile="p", source=SimpleNamespace(sha256="x"), meta={})
    r.settings = SimpleNamespace(profiles_dir="unused")
    r.plan = SimpleNamespace(frames_per_segment=120, fps=30)
    r.shared = SimpleNamespace(stop=MagicMock(), playhead=0)
    r.shared.stop.is_set.return_value = False
    r.bus = MagicMock()
    r._transcode_error = None
    sport = MagicMock()
    sport.degraded.return_value = []
    sport.drain_tracks.return_value = []
    r._create_sport = MagicMock(return_value=sport)
    r._sample_keyframes = MagicMock(return_value=[])
    r._perceive = MagicMock(return_value=SimpleNamespace(start=0, end=76))
    r._drain_commands = MagicMock()
    r._publish_tracks = MagicMock()
    r._progress = MagicMock()
    r._status = MagicMock()
    r._apply_carried = MagicMock()
    monkeypatch.setattr(runtime, "load_profile", lambda *_: SimpleNamespace(lead_buffer_s=1))
    monkeypatch.setattr(runtime, "SegmentDecoder", lambda *_: object())
    monkeypatch.setattr(runtime, "hls_status", lambda *_: SimpleNamespace(segments=1, ended=True))
    r._analyse()
    r._progress.assert_called_once_with(76, 30.0)
