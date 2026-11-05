"""Probe and validate untrusted media before anything decodes it."""

from __future__ import annotations

import heapq
import queue
import subprocess
import threading
import time
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from bai_engine.media.ffmpeg import MediaError, Tools, run_json

ALLOWED_CONTAINERS = {
    "mov,mp4,m4a,3gp,3g2,mj2",
    "matroska,webm",
    "avi",
    "mpegts",
    "flv",
    "asf",
    "mpeg",
    "ogg",
    "mxf",
    "nut",
}
MAX_DIM = 4096
MIN_DIM = 160


@dataclass(frozen=True)
class ProbeResult:
    container: str
    duration_s: float
    width: int
    height: int
    codec: str
    r_frame_rate: Fraction
    avg_frame_rate: Fraction
    n_frames: int | None
    has_audio: bool
    rotation: int = 0
    video_stream_index: int = 0  # global source stream index selected by validation
    packet_pts_variable: bool | None = None
    packet_cadence_complete: bool | None = None  # None: legacy/header-only constructor
    packet_cadence_reason: str = "not_scanned"
    packet_cadence_count: int = 0

    @property
    def variable_frame_rate(self) -> bool:
        if self.avg_frame_rate <= 0 or self.r_frame_rate <= 0:
            return True
        if self.packet_pts_variable is not None:
            return self.packet_pts_variable
        if self.packet_cadence_complete is False:
            # A partial scan cannot certify constant cadence. Preserve the
            # explicit unknown fields and conservatively request CFR handling.
            return True
        return abs(float(self.r_frame_rate) - float(self.avg_frame_rate)) / float(self.r_frame_rate) > 0.01

    @property
    def fps(self) -> Fraction:
        return self.avg_frame_rate if self.avg_frame_rate > 0 else self.r_frame_rate

    @property
    def display_size(self) -> tuple[int, int]:
        """Dimensions after FFmpeg's automatic display-matrix rotation."""
        if self.rotation % 180 == 90:
            return self.height, self.width
        return self.width, self.height


def _frac(s: object) -> Fraction:
    try:
        f = Fraction(str(s))
    except (ValueError, ZeroDivisionError):
        return Fraction(0)
    return f


@dataclass(frozen=True)
class _CadenceScan:
    variable: bool | None
    complete: bool
    count: int
    reason: str


class _PacketCadence:
    """Bounded presentation reorder, verified through EOF before claiming CFR."""

    def __init__(self, reorder_limit: int = 256):
        self.limit = reorder_limit
        self.pending: list[int] = []
        self.count = 0
        self.previous: int | None = None
        self.minimum: int | None = None
        self.maximum: int | None = None
        self.invalid = False

    def _emit(self, point: int) -> None:
        if self.previous is not None:
            delta = point - self.previous
            if delta < 0:
                # Unusual codecs/reorder depths are unknown, never guessed CFR.
                self.invalid = True
            self.minimum = delta if self.minimum is None else min(self.minimum, delta)
            self.maximum = delta if self.maximum is None else max(self.maximum, delta)
        self.previous = point

    def add(self, point: int) -> None:
        self.count += 1
        heapq.heappush(self.pending, point)
        if len(self.pending) > self.limit:
            self._emit(heapq.heappop(self.pending))

    def finish(self) -> _CadenceScan:
        while self.pending:
            self._emit(heapq.heappop(self.pending))
        if self.invalid:
            return _CadenceScan(None, False, self.count, "reorder_limit_exceeded")
        if self.count < 3:
            return _CadenceScan(None, False, self.count, "insufficient_pts")
        assert self.minimum is not None and self.maximum is not None
        # One source clock tick accommodates rational CFR in coarse containers.
        variable = self.minimum <= 0 or self.maximum - self.minimum > 1
        return _CadenceScan(variable, True, self.count, "complete_selected_video_pts")


def _scan_packet_cadence(path: Path, tools: Tools, video_stream_index: int, timeout: float) -> _CadenceScan:
    """Stream only selected-video PTS, with fixed memory and a total deadline.

    No decoded frames or whole-video JSON is retained. A bounded pipe reader
    works on Windows as well as POSIX; timeout always terminates and reaps its
    own ffprobe. Missing, malformed or excessive reorder evidence remains unknown.
    """
    command = [
        tools.ffprobe,
        "-v",
        "error",
        "-select_streams",
        str(video_stream_index),
        "-show_packets",
        "-show_entries",
        "packet=pts",
        "-of",
        "csv=p=0",
        str(path),
    ]
    accumulator = _PacketCadence()
    try:
        process = subprocess.Popen(  # noqa: S603 - validated tool, no shell
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return _CadenceScan(None, False, 0, "packet_probe_unavailable")
    assert process.stdout is not None
    messages: queue.Queue[bytes | None] = queue.Queue(maxsize=16)
    stopped = threading.Event()

    def read() -> None:
        while not stopped.is_set():
            line = process.stdout.readline(256)
            while not stopped.is_set():
                try:
                    messages.put(line or None, timeout=0.05)
                    break
                except queue.Full:
                    continue
            if not line:
                break

    reader = threading.Thread(target=read, name="media-pts-reader", daemon=True)
    reader.start()
    deadline = time.monotonic() + max(0, timeout)
    try:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return _CadenceScan(None, False, accumulator.count, "packet_probe_timeout")
            try:
                line = messages.get(timeout=remaining)
            except queue.Empty:
                return _CadenceScan(None, False, accumulator.count, "packet_probe_timeout")
            if line is None:
                try:
                    code = process.wait(timeout=max(0.001, deadline - time.monotonic()))
                except subprocess.TimeoutExpired:
                    return _CadenceScan(None, False, accumulator.count, "packet_probe_timeout")
                if code != 0:
                    return _CadenceScan(None, False, accumulator.count, "packet_probe_failed")
                return accumulator.finish()
            # ffprobe emits empty side-data separator lines for some codecs.
            token = line.strip().split(b",", 1)[0]
            if not token:
                continue
            try:
                point = int(token)
            except ValueError:
                return _CadenceScan(None, False, accumulator.count, "missing_or_invalid_pts")
            if len(line) == 256 and not line.endswith(b"\n"):
                return _CadenceScan(None, False, accumulator.count, "packet_line_limit")
            accumulator.add(point)
            if accumulator.invalid:
                return _CadenceScan(None, False, accumulator.count, "reorder_limit_exceeded")
    finally:
        stopped.set()
        if process.poll() is None:
            process.kill()
        process.wait()
        reader.join(timeout=1)
        process.stdout.close()


def probe(path: Path, tools: Tools, timeout: float = 30.0) -> ProbeResult:
    started = time.monotonic()
    data = run_json(
        [
            tools.ffprobe,
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(path),
        ],
        timeout=timeout,
    )
    fmt = data.get("format") or {}
    streams = data.get("streams") or []
    assert isinstance(fmt, dict) and isinstance(streams, list)
    video = next(
        (s for s in streams if s.get("codec_type") == "video" and not s.get("disposition", {}).get("attached_pic")),
        None,
    )
    if video is None:
        raise MediaError("no video stream")
    container = str(fmt.get("format_name", ""))
    duration = float(fmt.get("duration") or video.get("duration") or 0.0)
    nb = video.get("nb_frames")
    rotation = 0
    for sd in video.get("side_data_list", []) or []:
        if "rotation" in sd:
            rotation = int(sd["rotation"]) % 360
    cadence = _scan_packet_cadence(
        path,
        tools,
        int(video.get("index", 0)),
        max(0, timeout - (time.monotonic() - started)),
    )
    return ProbeResult(
        container=container,
        duration_s=duration,
        width=int(video.get("width") or 0),
        height=int(video.get("height") or 0),
        codec=str(video.get("codec_name", "")),
        r_frame_rate=_frac(video.get("r_frame_rate", "0/1")),
        avg_frame_rate=_frac(video.get("avg_frame_rate", "0/1")),
        n_frames=int(nb) if nb and str(nb).isdigit() else None,
        has_audio=any(s.get("codec_type") == "audio" for s in streams),
        rotation=rotation,
        video_stream_index=int(video.get("index", 0)),
        packet_pts_variable=cadence.variable,
        packet_cadence_complete=cadence.complete,
        packet_cadence_reason=cadence.reason,
        packet_cadence_count=cadence.count,
    )


def validate(p: ProbeResult, max_duration_s: float) -> None:
    if p.container not in ALLOWED_CONTAINERS:
        raise MediaError(f"unsupported container {p.container!r}")
    if p.duration_s <= 0:
        raise MediaError("video has no duration")
    if p.duration_s > max_duration_s:
        raise MediaError(f"video is {p.duration_s / 60:.0f} min long; the limit is {max_duration_s / 60:.0f} min")
    if not (MIN_DIM <= p.width <= MAX_DIM and MIN_DIM <= p.height <= MAX_DIM):
        raise MediaError(f"unsupported resolution {p.width}×{p.height}")
    if p.fps <= 0 or p.fps > 300:
        raise MediaError(f"unsupported frame rate {float(p.fps):.2f}")
