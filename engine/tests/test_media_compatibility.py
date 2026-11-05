"""Actual selected-stream timestamp cadence, independent of codec header rates."""

import sys
import time
from fractions import Fraction
from importlib import import_module

import pytest

from bai_engine.media import Tools, probe
from research.production_media_probe import make_source


def test_real_matroska_variable_pts_cannot_be_declared_cfr_by_equal_header_rates(tmp_path):
    source = tmp_path / "irregular.mkv"
    make_source(source, Fraction(30), irregular=True)
    result = probe(source, Tools.resolve())
    assert result.r_frame_rate == result.avg_frame_rate == 30
    assert result.variable_frame_rate is True


def test_coarsely_quantized_constant_rate_is_not_mistaken_for_vfr(tmp_path):
    source = tmp_path / "constant24.mkv"
    make_source(source, Fraction(24))
    assert probe(source, Tools.resolve()).variable_frame_rate is False


@pytest.mark.parametrize(
    "timestamps,expected",
    [
        ([0, 60, 20, 40], False),  # decode-order B frames have constant presentation cadence
        ([0, 17, 67, 83], True),
        ([0, 42, 83, 125, 167], False),  # one-tick rational-rate quantization
        ([0, 40, 40, 80], True),
    ],
)
def test_packet_cadence_uses_only_selected_video_and_preserves_reported_fps(
    monkeypatch, tmp_path, timestamps, expected
):
    data = {
        "format": {"format_name": "matroska,webm", "duration": "1"},
        "streams": [
            {
                "index": 0,
                "codec_type": "video",
                "codec_name": "mjpeg",
                "width": 180,
                "height": 180,
                "disposition": {"attached_pic": 1},
            },
            {
                "index": 2,
                "codec_type": "video",
                "codec_name": "h264",
                "width": 320,
                "height": 180,
                "r_frame_rate": "25/1",
                "avg_frame_rate": "25/1",
            },
        ],
        "packets": [{"stream_index": 0, "pts": 0}, {"stream_index": 0, "pts": 999}]
        + [{"stream_index": 2, "pts": point} for point in timestamps],
    }
    monkeypatch.setattr(import_module("bai_engine.media.probe"), "run_json", lambda *args, **kwargs: data)
    executable = tmp_path / "selected_pts.py"
    executable.write_text(
        f"#!{sys.executable}\nimport sys\n"
        "assert sys.argv[sys.argv.index('-select_streams')+1] == '2'\n"
        f"for point in {timestamps!r}: print(point)\n"
    )
    executable.chmod(0o700)
    result = probe(tmp_path / "unread-source", Tools("ffmpeg", str(executable)))
    assert result.packet_cadence_complete is True
    assert result.packet_cadence_count == len(timestamps)
    assert result.video_stream_index == 2
    assert result.fps == 25
    assert result.variable_frame_rate is expected


@pytest.mark.parametrize(
    "rate,audio",
    [
        (24, False),
        (25, False),
        (30, False),
        (50, False),
        (60, False),
        (30, True),
        (Fraction(30000, 1001), False),
        (Fraction(60000, 1001), False),
    ],
)
def test_hls_presentation_origin_matches_canonical_proxy_and_decoder(tmp_path, rate, audio):
    """Browser PTS and SegmentDecoder indexes must select identical physical images."""
    import io
    import subprocess

    import av

    from bai_engine.decode import SegmentDecoder
    from bai_engine.media import hls_status, plan_proxy, transcode
    from bai_engine.store.sessions import MediaPaths
    from research.production_media_probe import identity, inspect

    tools = Tools.resolve()
    original = tmp_path / "original.mp4"
    make_source(original, Fraction(rate))
    source = original
    if audio:
        source = tmp_path / "with_audio.mp4"
        subprocess.run(
            [
                tools.ffmpeg,
                "-v",
                "error",
                "-nostdin",
                "-i",
                str(original),
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=48000:cl=stereo",
                "-map",
                "0:v",
                "-map",
                "1:a",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-threads",
                "1",
                "-shortest",
                str(source),
            ],
            check=True,
        )
    info = probe(source, tools)
    plan = plan_proxy(info, tools, max_height=180, prefer_gpu=False)
    media = MediaPaths(tmp_path / "media")
    media.root.mkdir()
    job = transcode(str(source), media, plan, tools, info.duration_s)
    job.cmd[1:1] = ["-threads", "1", "-filter_threads", "1"]
    index = job.cmd.index("-f")
    job.cmd[index:index] = ["-threads", "1"]
    job.run()
    proxy_frames = inspect(media.proxy)
    canonical_ids = [row["identity"] for row in proxy_frames]
    presentation_times = []
    presentation_ids = []
    decoder_ids = []
    decoder = SegmentDecoder(media, plan.frames_per_segment, threads=1)
    for segment in range(hls_status(media).segments):
        decoder_ids.extend(identity(image) for image in decoder.decode_segment(segment).frames)
        payload = (media.hls / "init.mp4").read_bytes() + (media.hls / f"seg_{segment:05d}.m4s").read_bytes()
        with av.open(io.BytesIO(payload)) as container:
            stream = container.streams.video[0]
            stream.codec_context.thread_count = 1
            for frame in container.decode(stream):
                presentation_times.append(frame.pts * frame.time_base)
                presentation_ids.append(identity(frame.to_ndarray(format="bgr24")))
    assert decoder_ids == presentation_ids == canonical_ids
    assert presentation_times == [Fraction(index) / plan.fps for index in range(len(proxy_frames))]


def test_timestamp_scan_memory_is_bounded_and_long_reorder_stays_unknown():
    module = import_module("bai_engine.media.probe")
    accumulator = module._PacketCadence()
    for point in range(100_000):
        accumulator.add(point * 40)
        assert len(accumulator.pending) <= 256
    assert accumulator.finish().variable is False
    excessive = module._PacketCadence(reorder_limit=2)
    for point in [100, 200, 300, 400, 0]:
        excessive.add(point)
    result = excessive.finish()
    assert result.variable is None
    assert result.complete is False
    assert result.reason == "reorder_limit_exceeded"


def test_missing_pts_cannot_certify_constant_cadence(tmp_path):
    module = import_module("bai_engine.media.probe")
    executable = tmp_path / "missing_pts.py"
    executable.write_text(f"#!{sys.executable}\nprint('0')\nprint('N/A')\nprint('80')\n")
    executable.chmod(0o700)
    result = module._scan_packet_cadence(tmp_path / "unused", Tools("ffmpeg", str(executable)), 0, 2)
    assert result.variable is None and result.complete is False
    assert result.reason == "missing_or_invalid_pts"
    incomplete = module.ProbeResult(
        "matroska,webm", 1, 320, 180, "h264", Fraction(25), Fraction(25), None, False, packet_cadence_complete=False
    )
    assert incomplete.variable_frame_rate is True


def test_packet_probe_deadline_terminates_own_process_and_marks_unknown(tmp_path):
    module = import_module("bai_engine.media.probe")
    executable = tmp_path / "blocked_pts.py"
    executable.write_text(f"#!{sys.executable}\nimport time\nprint('0', flush=True)\ntime.sleep(10)\n")
    executable.chmod(0o700)
    started = time.monotonic()
    result = module._scan_packet_cadence(tmp_path / "unused", Tools("ffmpeg", str(executable)), 0, 0.1)
    assert time.monotonic() - started < 2
    assert result.variable is None and result.complete is False
    assert result.reason == "packet_probe_timeout"
