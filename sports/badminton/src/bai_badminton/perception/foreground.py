"""Court-origin image regions for scene continuity, never participant authority.

An athlete can leave the floor polygon without disappearing from the image.
Conversely an image-region correspondence does not certify athlete identity.
Keep these observations separate from court admission, pose and named tracks.
"""

from __future__ import annotations

import numpy as np

from bai_badminton.perception.scene_change import ForegroundRegion


class CourtForegroundMemory:
    """Bounded causal image-box continuity with explicit freshness and overflow.

    Only fresh in-court detections seed regions. Unique raw detector matches
    may continue an image region outside court, without renewing membership.
    Carries never renew the existing one-second observation allowance. An
    overflow abstains until reset rather than selecting a convenient subset.
    """

    def __init__(self, fps: float, capacity: int = 8) -> None:
        self.fps, self.capacity = fps, capacity
        self._regions: dict[str, tuple[int, np.ndarray]] = {}
        self._next = 0
        self._matched: set[str] = set()
        self._observed_frame: int | None = None
        self._frame: int | None = None
        self.overflow = False

    def reset(self) -> None:
        self._regions.clear()
        self._matched.clear()
        self._observed_frame = self._frame = None
        self.overflow = False

    def update(self, frame: int, boxes: np.ndarray, inside: np.ndarray) -> None:
        from bai_badminton.perception.players import _box_iou

        if self._frame is not None and frame <= self._frame:
            raise ValueError("foreground observations require increasing canonical frames")
        self._frame = self._observed_frame = frame
        self._matched.clear()
        self._regions = {k: v for k, v in self._regions.items() if frame - v[0] <= self.fps}
        if self.overflow:
            return
        keys = list(self._regions)
        overlap = (
            _box_iou(boxes, np.asarray([self._regions[k][1] for k in keys])) >= 0.3
            if len(boxes) and keys
            else np.zeros((len(boxes), len(keys)), dtype=bool)
        )
        used = set()
        for column, key in enumerate(keys):
            matches = np.flatnonzero(overlap[:, column])
            if len(matches) == 1 and overlap[matches[0]].sum() == 1:
                row = int(matches[0])
                self._regions[key] = (frame, boxes[row].copy())
                self._matched.add(key)
                used.add(row)
            # Ambiguous and absent matches remain bounded missing estimates.
            # Neither may move the box or renew its last observed timestamp.
            # A later unique image match can recover before that lease expires;
            # these image estimates never renew participant court authority.
        for row in np.flatnonzero(inside):
            if int(row) not in used and not overlap[int(row)].any():
                key = f"court-origin:{self._next}"
                self._next += 1
                self._regions[key] = (frame, boxes[row].copy())
                self._matched.add(key)
        if len(self._regions) > self.capacity:
            self.overflow = True
            self._regions.clear()
            self._matched.clear()

    def at(self, frame: int) -> tuple[ForegroundRegion, ...]:
        if self.overflow or frame != self._frame:
            return ()
        return tuple(
            ForegroundRegion(
                frame,
                key,
                tuple(float(v) for v in box),
                self._observed_frame == frame and key in self._matched,
                self._observed_frame == frame,
            )
            for key, (last, box) in self._regions.items()
            if 0 <= frame - last <= self.fps
        )

    def carry(self, frame: int) -> None:
        if self._frame is not None and frame <= self._frame:
            raise ValueError("foreground observations require increasing canonical frames")
        self._frame = frame
        self._regions = {k: v for k, v in self._regions.items() if frame - v[0] <= self.fps}
