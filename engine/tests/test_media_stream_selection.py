"""Probe, transcode and warm-start must select the same real video stream."""

from fractions import Fraction
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from bai_engine.media import Tools, plan_proxy, probe
from bai_engine.media.proxy import build_command
from bai_engine.runtime.runner import SessionRunner
from bai_engine.store.sessions import MediaPaths


def test_proxy_does_not_encode_cover_art_excluded_by_probe(tmp_path: Path, monkeypatch) -> None:
    metadata = {
        "format": {"format_name": "mov,mp4,m4a,3gp,3g2,mj2", "duration": "2"},
        "streams": [
            {
                "index": 0, "codec_type": "video", "codec_name": "mjpeg", "width": 200, "height": 200,
                "r_frame_rate": "1/1", "avg_frame_rate": "1/1", "disposition": {"attached_pic": 1},
            },
            {"index": 1, "codec_type": "audio"},
            {
                "index": 2, "codec_type": "video", "codec_name": "h264", "width": 640, "height": 360,
                "r_frame_rate": "30/1", "avg_frame_rate": "30/1", "disposition": {"attached_pic": 0},
            },
        ],
    }
    monkeypatch.setattr(import_module("bai_engine.media.probe"), "run_json", lambda *args, **kwargs: metadata)
    source = tmp_path / "cover-first.mp4"
    tools = Tools("ffmpeg", "ffprobe")
    info = probe(source, tools)
    assert (info.width, info.height, info.fps) == (640, 360, Fraction(30))
    plan = plan_proxy(info, tools, prefer_gpu=False)
    command = build_command(str(source), MediaPaths(tmp_path / "media"), plan, tools)
    selected = command[command.index("-map") + 1]
    # Uppercase V excludes attached pictures; a selected global index is also
    # valid. Ordinary 0:v:0 points at the image that probe explicitly rejected.
    assert selected in {"0:V:0", "0:2"}, "Proxy selected cover art instead of the validated movie"


def test_warm_start_samples_movie_instead_of_attached_picture(monkeypatch) -> None:
    cover = SimpleNamespace(
        index=0, type="video", disposition=SimpleNamespace(attached_pic=True),
        duration=60, time_base=Fraction(1, 30), start_time=0,
    )
    movie = SimpleNamespace(
        index=2, type="video", disposition=SimpleNamespace(attached_pic=False),
        duration=60, time_base=Fraction(1, 30), start_time=0,
    )
    used = []

    class Container:
        streams = SimpleNamespace(video=[cover, movie])

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def seek(self, target, *, stream, any_frame):
            self.target = target

        def decode(self, stream):
            used.append(stream.index)
            pixels = np.full((180, 320, 3), 20 if stream is cover else 180, np.uint8)
            yield SimpleNamespace(pts=self.target, to_ndarray=lambda **kwargs: pixels)

    monkeypatch.setattr("bai_engine.runtime.runner.av.open", lambda *args, **kwargs: Container())
    session = SimpleNamespace(
        media=SimpleNamespace(width=320, height=180, duration_us=2_000_000),
        source=SimpleNamespace(uri="cover-first.mp4"),
        meta={"source_rotation": 0, "source_video_stream_index": 2},
    )
    runner = SessionRunner.__new__(SessionRunner)
    runner.session_id = "stream-selection"
    runner.repo = SimpleNamespace(get=lambda _: session)
    runner.settings = SimpleNamespace(ffprobe_timeout_s=30)
    runner.tools = Tools("ffmpeg", "ffprobe")
    frames = runner._sample_keyframes(n=1)
    assert used == [movie.index], "Calibration/background sampling used cover art"
    assert len(frames) == 1 and frames[0].mean() == 180
