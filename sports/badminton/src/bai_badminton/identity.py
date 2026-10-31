"""Conservative provisional identity assignment for singles.

Initial associations use court side and are hypotheses, not verified identities.
A known visual track retains its participant across side changes and temporary
occlusion. A new track cannot inherit an already-bound participant by side or
shirt colour alone. When ``rebind_gap_frames`` is set, a replacement track may
inherit a participant only on spatial evidence: the participant's bound track is
absent from the current frame, was last seen within the gap, and exactly one
unbound candidate overlaps its last box (and no other candidate does). Such
associations are flagged ``spatial_rebind_v1``; they are estimates, not verified
identities. Without that evidence fragmentation remains unresolved; tracker ID
reuse can still produce an incorrect association.
"""

from __future__ import annotations

from collections import Counter
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
    # Current-frame visual tracks not associated with a participant, keyed by track ID.
    unresolved_tracks: dict[int, str] = field(default_factory=dict, init=False)
    rebind_gap_frames: int = 0  # 0 disables spatial re-binding of replacement tracks
    rebind_min_iou: float = 0.3
    _last_box: dict[int, tuple[int, NDArray[np.float64]]] = field(default_factory=dict, init=False)
    rebound_tracks: dict[int, int] = field(default_factory=dict, init=False)  # new track -> track it replaced

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

    def assign(
        self, persons: list[PersonObs], ends: dict[str, str], frame: int | None = None
    ) -> dict[str, PersonObs]:
        """Return provisional participant associations, withholding unknown replacement tracks.

        ``unresolved_tracks`` describes only the current frame, and is cleared on
        every call. Known tracks take precedence over side and detection confidence.
        """
        side_to_player = {v: k for k, v in ends.items()}
        out: dict[str, PersonObs] = {}
        counts = Counter(p.track_id for p in persons)
        self.unresolved_tracks = {track_id: "ambiguous" for track_id, n in counts.items() if n > 1}
        persons = [p for p in persons if counts[p.track_id] == 1]
        # Preserve continuity even if the player crosses the net or changes ends.
        for p in persons:
            pid = self._track_to_player.get(p.track_id)
            if pid is not None and (pid not in out or p.conf > out[pid].conf):
                out[pid] = p

        # Bind each participant at most once. Initial side-based assignment is
        # only a provisional hypothesis, never a user-confirmed identity.
        unbound = [p for p in persons if p.track_id not in self._track_to_player]
        if frame is not None and self.rebind_gap_frames > 0:
            self._rebind(unbound, {p.track_id for p in persons}, frame)
            for p in unbound:
                pid = self._track_to_player.get(p.track_id)
                if pid is not None and (pid not in out or p.conf > out[pid].conf):
                    out[pid] = p
            unbound = [p for p in unbound if p.track_id not in self._track_to_player]
        bound_pids = set(self._track_to_player.values())
        side_counts = Counter(self.side_of(p) for p in persons)
        for side, p in self.select_players(unbound).items():
            pid = side_to_player.get(side)
            if pid is not None and pid not in bound_pids and side_counts[side] == 1:
                self._track_to_player[p.track_id] = pid
                bound_pids.add(pid)
                out[pid] = p

        for p in unbound:
            if p.track_id not in self._track_to_player:
                self.unresolved_tracks[p.track_id] = self.side_of(p)
        for p in out.values():
            if p.track_id in self.rebound_tracks:
                p.identity_method = "spatial_rebind_v1"
            if frame is not None:
                self._last_box[p.track_id] = (frame, np.asarray(p.bbox, dtype=np.float64))
        for pid, p in out.items():
            if p.appearance is not None:
                prev = self._sig.get(pid)
                self._sig[pid] = p.appearance if prev is None else (0.9 * prev + 0.1 * p.appearance).astype(np.float32)
        return out

    def _rebind(self, unbound: list[PersonObs], visible: set[int], frame: int) -> None:
        """Move a participant from a vanished bound track to its unique spatial successor."""
        lost = [
            (tid, pid, box)
            for tid, pid in self._track_to_player.items()
            if tid not in visible and (seen := self._last_box.get(tid)) is not None
            for last, box in [seen]
            if 0 < frame - last <= self.rebind_gap_frames
        ]
        if not lost or not unbound:
            return
        boxes = np.asarray([p.bbox for p in unbound], dtype=np.float64)
        lost_boxes = np.asarray([box for _, _, box in lost])
        lt = np.maximum(boxes[:, None, :2], lost_boxes[None, :, :2])
        rb = np.minimum(boxes[:, None, 2:], lost_boxes[None, :, 2:])
        inter = np.prod(np.clip(rb - lt, 0, None), axis=2)
        area = lambda b: np.prod(b[:, 2:] - b[:, :2], axis=1)  # noqa: E731
        iou = inter / np.maximum(area(boxes)[:, None] + area(lost_boxes)[None, :] - inter, 1e-9)
        ok = iou >= self.rebind_min_iou
        for j, (old, pid, _) in enumerate(lost):
            # One participant, one successor, and that successor claims no other lost track.
            if ok[:, j].sum() == 1 and ok[int(ok[:, j].argmax())].sum() == 1:
                new = unbound[int(ok[:, j].argmax())]
                del self._track_to_player[old]
                self._track_to_player[new.track_id] = pid
                self._last_box.pop(old, None)
                self.rebound_tracks[new.track_id] = old

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
