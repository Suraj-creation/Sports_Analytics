"""Real FFmpeg integration: probe → proxy/HLS → segment decode must preserve frame identity."""

import shutil
import subprocess
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import av
import numpy as np
import pytest

from bai_engine.decode import SegmentDecoder
from bai_engine.media import MediaError, Tools, hls_status, plan_proxy, probe, transcode, validate
from bai_engine.store.sessions import MediaPaths

pytestmark = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")


def _encoded_value(frame: np.ndarray) -> int:
    """Each synthetic frame carries its index (mod 64) as brightness of an 8-cell barcode."""
    h, w = frame.shape[:2]
    cells = []
    for b in range(6):
        x0 = int(w * (0.1 + 0.12 * b))
        patch = frame[int(h * 0.4) : int(h * 0.6), x0 : x0 + int(w * 0.08)]
        cells.append(1 if patch.mean() > 127 else 0)
    return sum(bit << i for i, bit in enumerate(cells))


def _make_source(path: Path, n: int, fps: int = 30, size: tuple[int, int] = (640, 360)) -> None:
    with av.open(str(path), "w") as out:
        s = out.add_stream("libx264", rate=fps)
        s.width, s.height = size
        s.pix_fmt = "yuv420p"
        for i in range(n):
            img = np.full((size[1], size[0], 3), 40, np.uint8)
            v = i % 64
            for b in range(6):
                if v >> b & 1:
                    x0 = int(size[0] * (0.1 + 0.12 * b))
                    img[int(size[1] * 0.4) : int(size[1] * 0.6), x0 : x0 + int(size[0] * 0.08)] = 230
            for pkt in s.encode(av.VideoFrame.from_ndarray(img, format="bgr24")):
                out.mux(pkt)
        for pkt in s.encode():
            out.mux(pkt)


@pytest.fixture(scope="module")
def proxied(tmp_path_factory: pytest.TempPathFactory) -> tuple[MediaPaths, object, int]:
    d = tmp_path_factory.mktemp("media")
    src = d / "src.mp4"
    n = 200  # 6.67 s → 4 segments of 60 frames (last partial)
    _make_source(src, n)
    tools = Tools.resolve()
    p = probe(src, tools)
    validate(p, max_duration_s=3600)
    plan = plan_proxy(p, tools, max_height=720, prefer_gpu=False)
    mp = MediaPaths(d / "m")
    mp.root.mkdir()
    prog: list[float] = []
    transcode(str(src), mp, plan, tools, p.duration_s, on_progress=prog.append).run()
    assert prog and prog[-1] > 0.9
    return mp, plan, n


def test_probe_and_plan(tmp_path: Path) -> None:
    src = tmp_path / "a.mp4"
    _make_source(src, 30)
    tools = Tools.resolve()
    p = probe(src, tools)
    assert (p.width, p.height) == (640, 360) and p.fps == 30 and not p.variable_frame_rate
    plan = plan_proxy(p, tools, prefer_gpu=False)
    assert plan.fps == Fraction(30) and plan.height == 360 and plan.frames_per_segment == 60  # no upscaling


def test_rejects_non_video(tmp_path: Path) -> None:
    bad = tmp_path / "x.mp4"
    bad.write_bytes(b"not a video at all" * 100)
    with pytest.raises(MediaError):
        probe(bad, Tools.resolve())


def test_hls_segments_have_exact_frame_ranges(proxied: tuple[MediaPaths, object, int]) -> None:
    mp, plan, n = proxied
    st = hls_status(mp)
    assert st.ended
    F = plan.frames_per_segment  # type: ignore[attr-defined]
    assert st.segments == -(-n // F)
    dec = SegmentDecoder(mp, F)
    total = 0
    for k in range(st.segments):
        ch = dec.decode_segment(k)
        assert ch.start == k * F
        assert len(ch.frames) == (F if k < st.segments - 1 else n - k * F)
        for i, fr in enumerate(ch.frames):
            assert _encoded_value(fr) == (ch.start + i) % 64, f"frame identity drift at {ch.start + i}"
        total += len(ch.frames)
    assert total == n
    assert mp.proxy.exists()
    assert _encoded_value(dec.decode_frame(137)) == 137 % 64
    assert _encoded_value(dec.keyframe(2)) == 120 % 64


def test_decode_rejects_missing_and_negative_frames(proxied: tuple[MediaPaths, object, int]) -> None:
    mp, plan, n = proxied
    dec = SegmentDecoder(mp, plan.frames_per_segment)
    with pytest.raises(ValueError, match="non-negative"):
        dec.decode_frame(-1)
    with pytest.raises(ValueError, match="non-negative"):
        dec.decode_segment(-1)
    with pytest.raises(IndexError, match="beyond"):
        dec.decode_frame(n)
    # A corrupt/mismatched segment size must not silently discard frames.
    with pytest.raises(ValueError, match="expected at most"):
        SegmentDecoder(mp, 20).decode_segment(0)


@pytest.mark.parametrize("rotation", [0, 90, 180, 270])
def test_rotated_proxy_and_warm_start_share_orientation_and_target_frame(tmp_path: Path, rotation: int) -> None:
    from bai_engine.bus import LocalBus
    from bai_engine.config import Settings
    from bai_engine.media.proxy import build_sprite
    from bai_engine.runtime.registry import ModelRegistry
    from bai_engine.runtime.runner import SessionRunner
    from bai_engine.schema import MediaInfo, Session, Source, SourceKind
    from bai_engine.store import SessionRepository

    src, rotated = tmp_path / "raw.mp4", tmp_path / "rotated.mp4"
    _make_source(src, 30)
    tools = Tools.resolve()
    subprocess.run(
        [
            tools.ffmpeg,
            "-v",
            "error",
            "-display_rotation",
            str(rotation),
            "-i",
            str(src),
            "-c",
            "copy",
            str(rotated),
        ],
        check=True,
        capture_output=True,
    )
    p = probe(rotated, tools)
    assert p.rotation == rotation
    assert replace(p, r_frame_rate=Fraction(0)).variable_frame_rate
    plan = plan_proxy(p, tools, prefer_gpu=False)
    width, height = p.display_size
    assert plan.height == height
    mp = MediaPaths(tmp_path / "media")
    mp.root.mkdir()
    transcode(str(rotated), mp, plan, tools, p.duration_s).run()
    dec = SegmentDecoder(mp, plan.frames_per_segment)
    middle = dec.decode_frame(15)
    assert middle.shape[:2] == (height, width)
    repo = SessionRepository(tmp_path / "data")
    try:
        session = repo.save(
            Session(
                title="Orientation",
                source=Source(kind=SourceKind.UPLOAD, uri=str(rotated)),
                media=MediaInfo(fps_num=30, fps_den=1, width=width, height=height, n_frames=30, duration_us=1_000_000),
                meta={"source_rotation": p.rotation},
            )
        )
        settings = Settings(data_dir=repo.data_dir, _env_file=None)
        runner = SessionRunner(session.session_id, repo, LocalBus(), settings, ModelRegistry(settings.models_dir))
        samples = runner._sample_keyframes(n=1)
        assert len(samples) == 1
        # Frame 15 is not a keyframe. Seeking without decoding forward would use frame zero.
        assert _encoded_value(np.rot90(samples[0], -(rotation // 90))) == 15
        # A second lossy encode changes a few block-edge pixels. Mean error
        # checks orientation/alignment without demanding identical codecs.
        assert np.abs(samples[0].astype(float) - middle.astype(float)).mean() < 1
    finally:
        repo.close()
    sprite = build_sprite(mp.proxy, mp, tools, p.duration_s, every_s=0.5, tile=2)
    assert sprite["thumb_h"] == round(192 * height / width / 2) * 2
