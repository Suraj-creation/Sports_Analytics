"""Persistent player identity for singles.

Identity is *who*, side is *where*.  The tracker gives short-lived ``track_id`` s; this module maps
them to stable match identities ``P1``/``P2`` using three cues, in order of authority:

1. **Court side + match state** — in singles the players never share a half; the BWF state
   machine knows which end each player occupies (it flips ends after games and at 11 in the
   decider), so the person in the near half *is* whoever the state says is near.
2. **Track continuity** — a track keeps its identity while it lives.
3. **Appearance** — an HSV shirt signature (EMA) re-links identities after camera cuts and
   breaks, and disambiguates the end change between games (players walk across the net).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from bai_badminton.perception_types import PersonObs


@dataclass
class IdentityResolver:
    frame_height: float
    net_image_y: float | None = None  # fallback side divider (image y of the net's floor line)
    _sig: dict[str, NDArray[np.float32]] = field(default_factory=dict)
    _track_to_player: dict[int, str] = field(default_factory=dict)

    def side_of(self, p: PersonObs) -> str:
        if p.court_xy is not None and np.isfinite(p.court_xy[1]):
            return "near" if p.court_xy[1] < 0 else "far"
        div = self.net_image_y if self.net_image_y is not None else self.frame_height * 0.5
        return "near" if p.bbox[3] > div else "far"

    def select_players(self, persons: list[PersonObs]) -> dict[str, PersonObs]:
        """Pick at most one person per half: the most confident, then the largest."""
        best: dict[str, PersonObs] = {}
        for p in persons:
            side = self.side_of(p)
            cur = best.get(side)
            area = (p.bbox[2] - p.bbox[0]) * (p.bbox[3] - p.bbox[1])
            if cur is None:
                best[side] = p
                continue
            cur_area = (cur.bbox[2] - cur.bbox[0]) * (cur.bbox[3] - cur.bbox[1])
            if (p.conf, area) > (cur.conf, cur_area):
                best[side] = p
        return best

    def assign(self, persons: list[PersonObs], ends: dict[str, str]) -> dict[str, PersonObs]:
        """Return ``{player_id: person}`` for this frame given the match state's ``ends``."""
        by_side = self.select_players(persons)
        side_to_player = {v: k for k, v in ends.items()}
        out: dict[str, PersonObs] = {}
        for side, p in by_side.items():
            pid = side_to_player.get(side)
            if pid is None:
                continue
            out[pid] = p
            self._track_to_player[p.track_id] = pid
            if p.appearance is not None:
                prev = self._sig.get(pid)
                self._sig[pid] = p.appearance if prev is None else (0.9 * prev + 0.1 * p.appearance).astype(np.float32)
        return out

    def appearance_vote(self, persons: list[PersonObs]) -> dict[str, str] | None:
        """Suggest ``{side: player_id}`` from appearance alone (used to verify end changes)."""
        if len(self._sig) < 2:
            return None
        by_side = self.select_players(persons)
        if len(by_side) < 2 or any(p.appearance is None for p in by_side.values()):
            return None

        def d(a: NDArray[np.float32], b: NDArray[np.float32]) -> float:
            return float(np.linalg.norm(a - b))

        near, far = by_side["near"].appearance, by_side["far"].appearance
        assert near is not None and far is not None
        keep = d(near, self._sig["P1"]) + d(far, self._sig["P2"])
        swap = d(near, self._sig["P2"]) + d(far, self._sig["P1"])
        if abs(keep - swap) < 0.15 * max(keep, swap, 1e-6):
            return None
        return {"near": "P1", "far": "P2"} if keep < swap else {"near": "P2", "far": "P1"}


def hsv_signature(bgr_crop: NDArray[np.uint8], bins: int = 8) -> NDArray[np.float32] | None:
    """Normalised hue/saturation histogram of the torso region (rows 20–55 % of the box)."""
    import cv2

    if bgr_crop.size == 0:
        return None
    h = bgr_crop.shape[0]
    torso = bgr_crop[int(0.2 * h) : int(0.55 * h)]
    if torso.size == 0:
        return None
    hsv = cv2.cvtColor(torso, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1], None, [bins, bins], [0, 180, 0, 256]).astype(np.float32).ravel()
    s = hist.sum()
    return hist / s if s > 0 else None
