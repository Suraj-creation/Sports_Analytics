"""Probe and validate untrusted media before anything decodes it."""

from __future__ import annotations

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

    @property
    def variable_frame_rate(self) -> bool:
        if self.avg_frame_rate == 0:
            return True
        return abs(float(self.r_frame_rate) - float(self.avg_frame_rate)) / float(self.r_frame_rate) > 0.01

    @property
    def fps(self) -> Fraction:
        return self.avg_frame_rate if self.avg_frame_rate > 0 else self.r_frame_rate


def _frac(s: object) -> Fraction:
    try:
        f = Fraction(str(s))
    except (ValueError, ZeroDivisionError):
        return Fraction(0)
    return f


def probe(path: Path, tools: Tools, timeout: float = 30.0) -> ProbeResult:
    data = run_json(
        [tools.ffprobe, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
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
