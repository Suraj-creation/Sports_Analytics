"""COCO-17 keypoint layout — the only place index numbers appear.

The legacy V1 extractor read indices 15/13/11 as wrist/elbow/shoulder; they are the left
ankle/knee/hip.  Everything in the platform refers to keypoints by name through this module.
"""

from __future__ import annotations

from enum import IntEnum

import numpy as np
from numpy.typing import NDArray


class KP(IntEnum):
    NOSE = 0
    L_EYE = 1
    R_EYE = 2
    L_EAR = 3
    R_EAR = 4
    L_SHOULDER = 5
    R_SHOULDER = 6
    L_ELBOW = 7
    R_ELBOW = 8
    L_WRIST = 9
    R_WRIST = 10
    L_HIP = 11
    R_HIP = 12
    L_KNEE = 13
    R_KNEE = 14
    L_ANKLE = 15
    R_ANKLE = 16


N = 17
SKELETON: tuple[tuple[KP, KP], ...] = (
    (KP.L_SHOULDER, KP.R_SHOULDER),
    (KP.L_SHOULDER, KP.L_ELBOW),
    (KP.L_ELBOW, KP.L_WRIST),
    (KP.R_SHOULDER, KP.R_ELBOW),
    (KP.R_ELBOW, KP.R_WRIST),
    (KP.L_SHOULDER, KP.L_HIP),
    (KP.R_SHOULDER, KP.R_HIP),
    (KP.L_HIP, KP.R_HIP),
    (KP.L_HIP, KP.L_KNEE),
    (KP.L_KNEE, KP.L_ANKLE),
    (KP.R_HIP, KP.R_KNEE),
    (KP.R_KNEE, KP.R_ANKLE),
    (KP.NOSE, KP.L_EYE),
    (KP.NOSE, KP.R_EYE),
    (KP.L_EYE, KP.L_EAR),
    (KP.R_EYE, KP.R_EAR),
)
# horizontal flip permutation (left ↔ right) used by swap correction and augmentation
FLIP = (0, 2, 1, 4, 3, 6, 5, 8, 7, 10, 9, 12, 11, 14, 13, 16, 15)

Keypoints = NDArray[np.float32]  # shape (17, 3): x, y, score


def point(kps: Keypoints, kp: KP, min_score: float = 0.3) -> NDArray[np.float32] | None:
    x, y, s = kps[kp]
    return None if s < min_score else np.array([x, y], dtype=np.float32)


def midpoint(kps: Keypoints, a: KP, b: KP, min_score: float = 0.3) -> NDArray[np.float32] | None:
    pa, pb = point(kps, a, min_score), point(kps, b, min_score)
    if pa is None and pb is None:
        return None
    if pa is None:
        return pb
    if pb is None:
        return pa
    return (pa + pb) / 2


def hip_center(kps: Keypoints) -> NDArray[np.float32] | None:
    return midpoint(kps, KP.L_HIP, KP.R_HIP)


def ankle_center(kps: Keypoints) -> NDArray[np.float32] | None:
    return midpoint(kps, KP.L_ANKLE, KP.R_ANKLE)


def wrists(kps: Keypoints, min_score: float = 0.3) -> dict[str, NDArray[np.float32] | None]:
    return {"left": point(kps, KP.L_WRIST, min_score), "right": point(kps, KP.R_WRIST, min_score)}


def body_height(kps: Keypoints) -> float | None:
    """Nose→ankle vertical extent in px (scale reference for normalising features)."""
    nose = point(kps, KP.NOSE)
    ank = ankle_center(kps)
    if nose is None or ank is None:
        return None
    h = float(ank[1] - nose[1])
    return h if h > 1 else None


def lr_consistency_fix(kps: Keypoints, prev: Keypoints | None) -> Keypoints:
    """Fix left/right swaps by choosing the labelling closer to the previous frame.

    Pose models occasionally swap left/right labels when a player turns; temporal features
    (racket arm, footwork) break if that is not corrected.
    """
    if prev is None:
        return kps
    flipped = kps[list(FLIP)]
    valid = (kps[:, 2] > 0.3) & (prev[:, 2] > 0.3)
    if valid.sum() < 4:
        return kps
    d_keep = np.linalg.norm(kps[valid, :2] - prev[valid, :2], axis=1).mean()
    valid_f = (flipped[:, 2] > 0.3) & (prev[:, 2] > 0.3)
    d_flip = np.linalg.norm(flipped[valid_f, :2] - prev[valid_f, :2], axis=1).mean() if valid_f.any() else np.inf
    return flipped if d_flip < 0.7 * d_keep else kps
