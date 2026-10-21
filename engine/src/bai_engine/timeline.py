"""Canonical timeline.

The single source of truth for time in the platform is ``(session_id, frame_idx)`` on the
constant-frame-rate (CFR) analysis proxy, plus the derived presentation timestamp in integer
microseconds (``pts_us``).  Human-readable strings exist only at UI / export boundaries and are
produced and parsed exclusively by this module.

This replaces the five inconsistent parsers of the legacy code base (which disagreed on whether
``28:58:00`` means 28 hours or 28 minutes 58 seconds).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from fractions import Fraction

__all__ = ["TimeFormatError", "Timeline", "format_clock", "parse_clock"]

_US_PER_S = 1_000_000


class TimeFormatError(ValueError):
    """Raised when a human-readable time string cannot be parsed unambiguously."""


@dataclass(frozen=True, slots=True)
class Timeline:
    """Frame ↔ time conversions for one CFR video.

    ``fps`` is kept as an exact :class:`~fractions.Fraction` (e.g. ``30000/1001``) so that
    conversions round-trip without drift over long matches.
    """

    fps: Fraction
    n_frames: int

    def __post_init__(self) -> None:
        if self.fps <= 0:
            raise ValueError(f"fps must be positive, got {self.fps}")
        if self.n_frames < 0:
            raise ValueError(f"n_frames must be >= 0, got {self.n_frames}")

    # ------------------------------------------------------------------ constructors
    @classmethod
    def from_rate(cls, rate: str | float | Fraction, n_frames: int) -> Timeline:
        """Build from an ffprobe-style rate (``"30000/1001"``), a float or a Fraction."""
        if isinstance(rate, Fraction):
            fps = rate
        elif isinstance(rate, str) and "/" in rate:
            fps = Fraction(rate)
        else:
            fps = _snap_rate(float(rate))
        return cls(fps=fps, n_frames=n_frames)

    # ------------------------------------------------------------------ properties
    @property
    def fps_float(self) -> float:
        return float(self.fps)

    @property
    def frame_duration_us(self) -> float:
        return _US_PER_S / float(self.fps)

    @property
    def duration_us(self) -> int:
        return self.frame_to_pts_us(self.n_frames)

    # ------------------------------------------------------------------ conversions
    def frame_to_pts_us(self, frame_idx: int) -> int:
        """Presentation time (µs) of the *start* of ``frame_idx``.

        Rounded **up** to whole microseconds so that ``pts_us_to_frame`` (a floor) maps it back
        to the same frame exactly, for any rational fps.
        """
        if frame_idx < 0:
            raise ValueError(f"frame_idx must be >= 0, got {frame_idx}")
        return math.ceil(Fraction(frame_idx * _US_PER_S) / self.fps)

    def pts_us_to_frame(self, pts_us: int) -> int:
        """Frame whose display interval contains ``pts_us`` (floor), clamped to the video."""
        if pts_us < 0:
            return 0
        frame = math.floor(Fraction(pts_us) * self.fps / _US_PER_S)
        return self.clamp(frame)

    def seconds_to_frame(self, seconds: float) -> int:
        """Nearest frame to a media time in seconds (as reported by a browser ``mediaTime``).

        Browsers report ``mediaTime`` as the start of the presented frame, possibly with
        floating-point noise; rounding to the nearest frame is therefore correct.
        """
        if seconds <= 0:
            return 0
        return self.clamp(round(seconds * float(self.fps)))

    def frame_to_seconds(self, frame_idx: int) -> float:
        return self.frame_to_pts_us(frame_idx) / _US_PER_S

    def clamp(self, frame_idx: int) -> int:
        if self.n_frames == 0:
            return 0
        return max(0, min(frame_idx, self.n_frames - 1))

    def frames_for_duration(self, seconds: float) -> int:
        """Number of frames spanning ``seconds`` (rounded up, at least 1 for positive input)."""
        if seconds <= 0:
            return 0
        return max(1, math.ceil(seconds * float(self.fps)))

    # ------------------------------------------------------------------ display
    def format_frame(self, frame_idx: int, *, millis: bool = False) -> str:
        return format_clock(self.frame_to_pts_us(frame_idx), millis=millis)

    def parse_to_frame(self, text: str) -> int:
        return self.pts_us_to_frame(parse_clock(text))


_STANDARD_RATES = (
    Fraction(24000, 1001),
    Fraction(24),
    Fraction(25),
    Fraction(30000, 1001),
    Fraction(30),
    Fraction(50),
    Fraction(60000, 1001),
    Fraction(60),
    Fraction(120),
    Fraction(240),
)


def _snap_rate(rate: float) -> Fraction:
    """Snap a float frame rate to a standard broadcast rate when within 0.01 fps."""
    if rate <= 0:
        raise ValueError(f"fps must be positive, got {rate}")
    for std in _STANDARD_RATES:
        if abs(float(std) - rate) < 0.01:
            return std
    return Fraction(rate).limit_denominator(1001)


_CLOCK_RE = re.compile(r"^\s*(\d+)(?::(\d{1,2}))?(?::(\d{1,2}))?(?:[.,](\d{1,6}))?\s*$")


def parse_clock(text: str, *, legacy_mmss00: bool = False) -> int:
    """Parse a human time string into microseconds.

    Accepted forms:

    * ``SS[.fff]``, ``M:SS[.fff]``, ``MM:SS[.fff]``
    * ``H:MM:SS[.fff]``
    * legacy ``MM:SS:00`` (only with ``legacy_mmss00=True``, used by the legacy CSV importer):
      a three-field string whose last field is ``00`` is read as minutes:seconds with a zero
      suffix — the convention of the legacy rally CSVs (``24:38:00`` = 24 m 38 s).
      A first field above 23 is always minutes (a badminton video is never > 23 h long).

    Ambiguity is resolved deterministically and documented here instead of being re-decided
    by every caller.  The new platform never parses its own timestamps — it stores frames.
    """
    m = _CLOCK_RE.match(text)
    if not m:
        raise TimeFormatError(f"unrecognised time string: {text!r}")
    a, b, c, frac = m.groups()
    fields = [int(a)] + [int(x) for x in (b, c) if x is not None]
    frac_us = int((frac or "0").ljust(6, "0")[:6])

    if len(fields) == 1:
        seconds = fields[0]
    elif len(fields) == 2:
        minutes, secs = fields
        if secs >= 60:
            raise TimeFormatError(f"seconds field >= 60 in {text!r}")
        seconds = minutes * 60 + secs
    else:
        x, y, z = fields
        if y >= 60:
            raise TimeFormatError(f"middle field >= 60 in {text!r}")
        is_minutes = x > 23 or (legacy_mmss00 and z == 0 and frac is None)
        if is_minutes:
            seconds = x * 60 + y  # MM:SS:00 (trailing field is a zero frame suffix)
        else:
            if z >= 60:
                raise TimeFormatError(f"seconds field >= 60 in {text!r}")
            seconds = x * 3600 + y * 60 + z
    return seconds * _US_PER_S + frac_us


def format_clock(pts_us: int, *, millis: bool = False) -> str:
    """Format microseconds as ``M:SS`` / ``H:MM:SS`` (optionally with ``.mmm``)."""
    if pts_us < 0:
        raise ValueError("pts_us must be >= 0")
    total_ms = pts_us // 1000
    total_s, ms = divmod(total_ms, 1000)
    h, rem = divmod(total_s, 3600)
    m, s = divmod(rem, 60)
    base = f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
    return f"{base}.{ms:03d}" if millis else base
