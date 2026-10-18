"""Scene segments: which camera shot each stretch of the video.

Every frame carries a view from perception — ``main`` (the calibration's camera: analysed), ``alt``
(another camera showing the court: calibrated for display, not analysed) or ``none`` (no court in
view: close-ups, crowd, graphics).  Frame labels flicker (a missed fit, a two-frame logo wipe), so
segments shorter than ``min_frames`` are absorbed into the segment around them.  A segment is
*final* once the next one has lasted ``min_frames`` (or the stream ends); only final segments are
emitted, so the scene timeline never needs retracting.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SceneSegment:
    start: int
    end: int
    view: str  # main | alt | none
    head: int | None  # physical camera (0 = main); None without a court fit
    q_sum: float = 0.0  # sum of the court-fit precision over frames that had one
    q_n: int = 0

    @property
    def key(self) -> tuple[str, int | None]:
        return self.view, (self.head if self.view == "alt" else None)

    @property
    def frames(self) -> int:
        return self.end - self.start + 1

    @property
    def quality(self) -> float | None:
        return round(self.q_sum / self.q_n, 3) if self.q_n else None

    def absorb(self, other: SceneSegment) -> None:
        self.end = max(self.end, other.end)
        self.q_sum += other.q_sum
        self.q_n += other.q_n


class SceneSegmenter:
    def __init__(self, min_frames: int = 12) -> None:
        self.min_frames = min_frames
        self._cur: SceneSegment | None = None
        self._cand: SceneSegment | None = None
        self._ready: list[SceneSegment] = []

    def add(self, frame: int, view: str, head: int | None, quality: float | None) -> None:
        seg = SceneSegment(frame, frame, view, head, quality or 0.0, int(quality is not None))
        cur, cand = self._cur, self._cand
        if cur is None:
            self._cur = seg
            return
        if seg.key == cur.key:
            if cand is not None:  # a blip of another view inside this segment
                cur.absorb(cand)
                self._cand = None
            cur.absorb(seg)
            return
        if cand is not None and seg.key == cand.key:
            cand.absorb(seg)
            if cand.frames >= self.min_frames:
                self._ready.append(cur)
                self._cur, self._cand = cand, None
            return
        if cand is not None:  # the previous candidate was too short to count
            cur.absorb(cand)
        self._cand = seg

    def drain(self) -> list[SceneSegment]:
        out, self._ready = self._ready, []
        return out

    def flush(self) -> list[SceneSegment]:
        """End of stream: everything is final (a trailing short candidate stands on its own)."""
        out = self.drain()
        if self._cur is not None:
            out.append(self._cur)
        if self._cand is not None:
            out.append(self._cand)
        self._cur = self._cand = None
        return out
