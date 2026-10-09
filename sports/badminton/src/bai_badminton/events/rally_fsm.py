"""Streaming rally segmentation.

States: ``IDLE → IN_PLAY → ENDING → (CLOSED, mergeable) → IDLE``.  Thresholds follow the
validated legacy ``detect_rallies.py`` (start: 3 consecutive visible frames moving > 3 px/frame;
end: 10 consecutive invisible frames or ≥7 of the last 10 visible frames slower than 3 px/frame;
15-frame look-ahead cancels a false end; rallies < 2 s are dropped; gaps ≤ 0.75 s are merged).

Two upgrades over the legacy detector:

* **contact-driven start** — a detected contact while IDLE starts a rally at that contact (the
  serve), which is more precise than shuttle motion alone;
* **replay/cut suppression** — while ``replay`` is true the FSM is frozen and any open rally is
  ended at the last in-play frame (a broadcast cut ends the live view of the rally).

The FSM is fed one frame at a time and is fully deterministic; it never needs to look back
further than its own buffers, and look-ahead is expressed as delayed confirmation.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import StrEnum


class RallyState(StrEnum):
    IDLE = "idle"
    IN_PLAY = "in_play"
    ENDING = "ending"
    CLOSED = "closed"  # ended, waiting out the merge window before finalising


@dataclass(frozen=True)
class RallyParams:
    fps: float
    start_speed: float = 3.0  # px/frame
    start_visible: int = 3
    end_gap: int = 10  # invisible frames
    stationary_window: int = 10
    stationary_count: int = 7
    stationary_speed: float = 3.0
    end_lookahead: int = 15
    min_duration_s: float = 2.0
    merge_gap_s: float = 0.75
    resume_speed: float = 6.0

    @property
    def min_frames(self) -> int:
        return int(round(self.min_duration_s * self.fps))

    @property
    def merge_frames(self) -> int:
        return int(round(self.merge_gap_s * self.fps))


@dataclass(frozen=True)
class RallySegment:
    start: int
    end: int
    serve_frame: int | None
    reason: str  # why it ended: gap | stationary | cut | flush

    @property
    def length(self) -> int:
        return self.end - self.start + 1


@dataclass
class RallyUpdate:
    """Output of one FSM step."""

    started: int | None = None  # provisional rally start (frame)
    cancelled_start: int | None = None  # a provisional start that turned out to be noise / too short
    finalized: RallySegment | None = None


@dataclass
class RallyFSM:
    params: RallyParams
    state: RallyState = RallyState.IDLE
    start: int | None = None
    serve: int | None = None
    tentative_end: int | None = None
    end_reason: str = ""
    closed: RallySegment | None = None
    _run_visible: int = 0
    _run_start: int | None = None
    _invisible: int = 0
    _recent: deque[tuple[bool, float]] = field(default_factory=lambda: deque(maxlen=10))
    _last_in_play_frame: int | None = None

    def on_contact(self, frame: int) -> RallyUpdate:
        """A detected hit: start (serve) or keep the rally alive."""
        upd = RallyUpdate()
        if self.state is RallyState.IDLE:
            self._open(frame, upd)
            self.serve = frame
        elif self.state is RallyState.ENDING:
            self.state, self.tentative_end = RallyState.IN_PLAY, None
        elif self.state is RallyState.CLOSED and self.closed is not None:
            self._reopen(upd)
        if self.serve is None and self.state is RallyState.IN_PLAY:
            self.serve = frame
        return upd

    def step(self, frame: int, visible: bool, speed: float, replay: bool = False) -> RallyUpdate:
        p = self.params
        upd = RallyUpdate()
        self._recent.append((visible, speed))

        if replay:
            if self.state in (RallyState.IN_PLAY, RallyState.ENDING):
                end = self._last_in_play_frame if self._last_in_play_frame is not None else frame
                self._close(end, "cut", upd)
            if self.state is RallyState.CLOSED:
                self._finalize(upd)
            self._run_visible, self._invisible = 0, 0
            return upd

        if visible:
            self._invisible = 0
            if speed > p.start_speed:
                if self._run_visible == 0:
                    self._run_start = frame
                self._run_visible += 1
            else:
                self._run_visible = 0
        else:
            self._invisible += 1
            self._run_visible = 0

        if self.state is RallyState.IDLE:
            if self._run_visible >= p.start_visible and self._run_start is not None:
                self._open(self._run_start, upd)
        elif self.state is RallyState.IN_PLAY:
            self._last_in_play_frame = frame
            if self._invisible >= p.end_gap:
                self._begin_end(frame - p.end_gap, "gap")
            elif self._stationary():
                self._begin_end(frame - p.stationary_window + 1, "stationary")
        elif self.state is RallyState.ENDING:
            assert self.tentative_end is not None
            if visible and speed > p.resume_speed:
                self.state, self.tentative_end = RallyState.IN_PLAY, None
            elif frame - self.tentative_end >= p.end_lookahead:
                self._close(self.tentative_end, self.end_reason, upd)
        elif self.state is RallyState.CLOSED:
            assert self.closed is not None
            if self._run_visible >= p.start_visible and frame - self.closed.end <= p.merge_frames:
                self._reopen(upd)
            elif frame - self.closed.end > p.merge_frames:
                self._finalize(upd)
                if self._run_visible >= p.start_visible and self._run_start is not None:
                    self._open(self._run_start, upd)
        return upd

    def flush(self, frame: int) -> RallyUpdate:
        """End of stream: close and finalise any open rally."""
        upd = RallyUpdate()
        if self.state in (RallyState.IN_PLAY, RallyState.ENDING):
            end = self.tentative_end if self.tentative_end is not None else frame
            self._close(end, "flush", upd)
        if self.state is RallyState.CLOSED:
            self._finalize(upd)
        return upd

    # ------------------------------------------------------------------ internals
    def _stationary(self) -> bool:
        p = self.params
        vis = [s for v, s in self._recent if v]
        return (
            len(self._recent) == p.stationary_window
            and sum(1 for s in vis if s < p.stationary_speed) >= p.stationary_count
        )

    def _open(self, start: int, upd: RallyUpdate) -> None:
        self.state, self.start, self.serve, self.tentative_end = RallyState.IN_PLAY, start, None, None
        upd.started = start

    def _begin_end(self, tentative: int, reason: str) -> None:
        self.state, self.tentative_end, self.end_reason = RallyState.ENDING, max(tentative, self.start or 0), reason

    def _close(self, end: int, reason: str, upd: RallyUpdate) -> None:
        assert self.start is not None
        self.closed = RallySegment(self.start, max(end, self.start), self.serve, reason)
        self.state = RallyState.CLOSED

    def _reopen(self, upd: RallyUpdate) -> None:
        assert self.closed is not None
        self.start, self.serve = self.closed.start, self.closed.serve_frame
        self.closed, self.state, self.tentative_end = None, RallyState.IN_PLAY, None

    def _finalize(self, upd: RallyUpdate) -> None:
        seg = self.closed
        self.closed, self.state, self.start, self.serve = None, RallyState.IDLE, None, None
        if seg is None:
            return
        if seg.length < self.params.min_frames:
            upd.cancelled_start = seg.start
        else:
            upd.finalized = seg


def segment_offline(
    frames: list[int],
    visible: list[bool],
    speed: list[float],
    params: RallyParams,
    contacts: set[int] | None = None,
    replay: list[bool] | None = None,
) -> list[RallySegment]:
    """Convenience: run the FSM over full arrays and return finalised rallies."""
    fsm = RallyFSM(params)
    out: list[RallySegment] = []
    contacts = contacts or set()
    for k, f in enumerate(frames):
        if f in contacts:
            u = fsm.on_contact(f)
            if u.finalized:
                out.append(u.finalized)
        u = fsm.step(f, visible[k], speed[k], replay[k] if replay else False)
        if u.finalized:
            out.append(u.finalized)
    u = fsm.flush(frames[-1] if frames else 0)
    if u.finalized:
        out.append(u.finalized)
    return out
