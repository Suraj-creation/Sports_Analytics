"""Analysis/playback proxy: one encode → fMP4 HLS (browser playback + analysis chunks) + MP4.

Canonical-timeline guarantees:

* constant frame rate (``fps`` filter + ``-fps_mode cfr``) — frame index ↔ time is exact;
* a keyframe every ``F = frames_per_segment`` frames (``force_key_frames`` on frame number),
  ``sc_threshold 0`` so the encoder never inserts extra IDRs — HLS segment ``k`` therefore holds
  exactly frames ``[k·F, (k+1)·F − 1]``;
* the HLS playlist is an ``event`` playlist while encoding (playback starts after the first
  segment) and becomes VOD (``#EXT-X-ENDLIST``) when done.

The analysis engine decodes the *same* segments the browser plays, so overlay frame indices and
analysis frame indices can never drift apart.
"""

from __future__ import annotations

import errno
import json
import math
import os
import re
import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from bai_engine.media.ffmpeg import FFmpegJob, MediaError, Tools, nvenc_works
from bai_engine.media.probe import ProbeResult, probe
from bai_engine.store.sessions import MediaPaths
from bai_engine.timeline import _snap_rate

SEGMENT_SECONDS = 2.0
_STD = [Fraction(25), Fraction(30000, 1001), Fraction(30), Fraction(50), Fraction(60000, 1001), Fraction(60)]


@contextmanager
def media_writer_lock(mp: MediaPaths, stop: threading.Event) -> Iterator[None]:
    """One writer per content-addressed media directory; waiting is cancellable.

    Readers may consume completed segments while the owner encodes. Keep the
    stable lock file: unlinking it would let another process lock a new inode.
    """
    mp.root.mkdir(parents=True, exist_ok=True)
    with (mp.root / ".prepare.lock").open("a+b") as stream:
        if os.name == "nt":
            import msvcrt

            stream.seek(0)
            if not stream.read(1):
                stream.write(b"\0")
                stream.flush()

            def acquire() -> None:
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)

            def release() -> None:
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            def acquire() -> None:
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

            def release() -> None:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

        acquired = False
        try:
            while not stop.is_set():
                try:
                    acquire()
                    acquired = True
                    break
                except OSError as error:
                    if error.errno not in (errno.EAGAIN, errno.EACCES, errno.EDEADLK):
                        raise
                    stop.wait(0.05)
            if not acquired or stop.is_set():
                raise MediaError("Media preparation cancelled while waiting for its writer")
            yield
        finally:
            if acquired:
                release()


@dataclass(frozen=True)
class ProxyPlan:
    fps: Fraction
    height: int
    frames_per_segment: int
    encoder: str  # libx264 | h264_nvenc
    audio: bool
    video_stream_index: int = 0

    @property
    def segment_seconds(self) -> float:
        return self.frames_per_segment / float(self.fps)


def plan_proxy(p: ProbeResult, tools: Tools, max_height: int = 720, prefer_gpu: bool = True) -> ProxyPlan:
    src_fps = _snap_rate(float(p.fps)) if p.fps > 0 else Fraction(30)
    if src_fps in _STD:
        fps = src_fps
    elif src_fps > 60:
        fps = Fraction(60)  # high-speed footage: analyse at 60 (TrackNet-family models expect 25–60)
    else:
        fps = Fraction(30)
    display_height = p.display_size[1]
    height = min(max_height, display_height - (display_height % 2))
    fps_seg = max(1, round(float(fps) * SEGMENT_SECONDS))
    encoder = "h264_nvenc" if prefer_gpu and nvenc_works(tools.ffmpeg) else "libx264"
    return ProxyPlan(
        fps=fps, height=height, frames_per_segment=fps_seg, encoder=encoder,
        audio=p.has_audio, video_stream_index=p.video_stream_index,
    )


def build_command(src: str, mp: MediaPaths, plan: ProxyPlan, tools: Tools) -> list[str]:
    mp.hls.mkdir(parents=True, exist_ok=True)
    f = plan.frames_per_segment
    vf = f"scale=-2:{plan.height}:flags=bicubic,fps={plan.fps.numerator}/{plan.fps.denominator},format=yuv420p"
    if plan.encoder == "h264_nvenc":
        venc = [
            "-c:v",
            "h264_nvenc",
            "-preset",
            "p4",
            "-tune",
            "hq",
            "-rc",
            "vbr",
            "-cq",
            "23",
            "-b:v",
            "0",
            "-forced-idr",
            "1",
            "-g",
            str(f),
            "-bf",
            "0",
        ]
    else:
        venc = [
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "21",
            "-g",
            str(f),
            "-keyint_min",
            str(f),
            "-sc_threshold",
            "0",
            "-bf",
            "2",
        ]
    # Outputs are relative to the media root (ffmpeg runs with cwd=mp.root): the tee muxer's option
    # syntax cannot carry Windows drive letters, and relative names need no escaping at all.
    # fMP4 can represent the encoder's negative decode timestamps. The HLS
    # muxer must retain them: shifting all timestamps to make DTS nonnegative
    # also shifts physical video presentation away from canonical frame zero.
    # This applies to encoder reorder delay and AAC priming without changing
    # encoded pixels, cadence, or the independent MP4 output.
    hls = (
        f"[f=hls:onfail=abort:hls_time={plan.segment_seconds * 0.999:.4f}:hls_playlist_type=event"
        ":hls_segment_type=fmp4:hls_fmp4_init_filename=init.mp4:hls_segment_filename=hls/seg_%05d.m4s"
        ":avoid_negative_ts=disabled:hls_flags=independent_segments+temp_file]hls/index.m3u8"
    )
    mp4 = "[f=mp4:onfail=abort:movflags=+faststart]proxy.mp4"
    cmd = [
        tools.ffmpeg,
        "-hide_banner",
        "-nostdin",
        "-y",
        "-loglevel",
        "error",
        "-i",
        str(Path(src).resolve()) if src != "pipe:0" else src,
        "-map",
        f"0:{plan.video_stream_index}",
    ]
    if plan.audio:
        cmd += ["-map", "0:a:0?"]
    cmd += ["-vf", vf, "-fps_mode", "cfr", *venc, "-pix_fmt", "yuv420p", "-force_key_frames", f"expr:eq(mod(n,{f}),0)"]
    if plan.audio:
        cmd += ["-c:a", "aac", "-b:a", "128k", "-ac", "2", "-ar", "48000"]
    cmd += ["-f", "tee", f"{hls}|{mp4}", "-progress", "pipe:1", "-nostats"]
    return cmd


def transcode(
    src: str,
    mp: MediaPaths,
    plan: ProxyPlan,
    tools: Tools,
    duration_s: float,
    on_progress: Callable[[float], None] | None = None,
    stdin: int | None = None,
) -> FFmpegJob:
    """Create the job (call ``.run()`` on a worker thread; ``.cancel()`` to abort)."""
    cmd = build_command(src, mp, plan, tools)

    def prog(out_us: int) -> None:
        if on_progress is not None and duration_s > 0:
            on_progress(min(1.0, out_us / 1e6 / duration_s))

    return FFmpegJob(cmd, on_progress=prog, stdin=stdin, cwd=mp.root)


# ---------------------------------------------------------------------- playlist inspection
_EXTINF = re.compile(r"#EXTINF:([0-9.]+),")


@dataclass(frozen=True)
class HlsStatus:
    segments: int  # complete segments available
    ended: bool  # #EXT-X-ENDLIST present (encode finished)
    durations: tuple[float, ...]

    def frames_available(self, plan_frames_per_segment: int) -> int:
        return self.segments * plan_frames_per_segment


def hls_status(mp: MediaPaths) -> HlsStatus:
    try:
        text = mp.playlist.read_text(encoding="utf-8")
    except FileNotFoundError:
        return HlsStatus(0, False, ())
    durs = tuple(float(m.group(1)) for m in _EXTINF.finditer(text))
    return HlsStatus(len(durs), "#EXT-X-ENDLIST" in text, durs)


def segment_path(mp: MediaPaths, k: int) -> Path:
    return mp.hls / f"seg_{k:05d}.m4s"


def init_path(mp: MediaPaths) -> Path:
    return mp.hls / "init.mp4"


# ---------------------------------------------------------------------- scrubber sprite
def build_sprite(
    src: Path,
    mp: MediaPaths,
    tools: Tools,
    duration_s: float,
    every_s: float | None = None,
    tile: int = 10,
    thumb_w: int = 192,
    run_job: Callable[[FFmpegJob], None] | None = None,
) -> dict[str, object]:
    """Thumbnail sprite sheets for the scrubber (``sprite_000.jpg`` …) + ``sprite.json``."""
    every = every_s or max(2.0, duration_s / 400)
    pattern = (mp.root / "sprite_%03d.jpg").as_posix()
    cmd = [
        tools.ffmpeg,
        "-hide_banner",
        "-nostdin",
        "-y",
        "-loglevel",
        "error",
        "-i",
        str(src),
        "-vf",
        f"fps=1/{every:.3f},scale={thumb_w}:-2,tile={tile}x{tile}",
        "-q:v",
        "5",
        pattern,
    ]
    job = FFmpegJob(cmd)
    if run_job is None:
        job.run()
    else:
        run_job(job)
    n_thumbs = math.ceil(duration_s / every)
    width, height = probe(src, tools).display_size
    meta = {
        "interval_s": every,
        "tile": tile,
        "thumb_w": thumb_w,
        "thumb_h": round(thumb_w * height / width / 2) * 2,
        "count": n_thumbs,
        "sheets": sorted(p.name for p in mp.root.glob("sprite_*.jpg")),
    }
    mp.sprite_meta.write_text(json.dumps(meta), encoding="utf-8")
    return meta


def ensure_ok(mp: MediaPaths) -> None:
    st = hls_status(mp)
    if st.segments == 0:
        raise MediaError("proxy produced no HLS segments")
