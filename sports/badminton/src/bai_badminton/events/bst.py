"""Optional singles BST-CG-AP inference with explicit temporal observations.

This adapter is for shadow evaluation until labelled comparisons justify its
use. It never replaces missing evidence with interpolated or invented poses.
Preprocessing follows the pinned official ShuttleSet merged-25 pipeline;
weights and source provenance are documented in docs/testing/bst-adapter-20261029.md.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from bai_badminton.court import HALF_LEN, LENGTH, WIDTH_DOUBLES, Homography
from bai_badminton.events.stroke import StrokePrediction

CHECKPOINT_FILENAME = "bst_CG_AP_JnB_bone_between_2_hits_with_max_limits_seq_100_merged_2.pt"
CHECKPOINT_SHA256 = "997f43e52b20cb47517132c71d3e147d7d717a2d9651cfbe7651a5003bd66809"
CHECKPOINT_URL = (
    "https://drive.usercontent.google.com/download?id=1snqpEEww-GG6xFUBzkuctYAPHcBP360B&export=download&confirm=t"
)
SEQ_LEN = 100
# Exact official get_merged_stroke_types order, with an explicit translation.
STROKES = (
    "net_shot",
    "block",
    "smash",
    "lift",
    "clear",
    "drive",
    "drop",
    "push",
    "rush",
    "cross_net",
    "short_serve",
    "long_serve",
)
SOURCE_LABELS = ("放小球", "擋小球", "殺球", "挑球", "長球", "平球", "切球", "推球", "撲球", "勾球", "發短球", "發長球")
CLASS_LABELS = ("未知球種", *(f"Top_{s}" for s in SOURCE_LABELS), *(f"Bottom_{s}" for s in SOURCE_LABELS))
BONE_PAIRS = (
    (0, 1),
    (0, 2),
    (1, 2),
    (1, 3),
    (2, 4),
    (3, 5),
    (4, 6),
    (5, 7),
    (7, 9),
    (6, 8),
    (8, 10),
    (5, 6),
    (5, 11),
    (6, 12),
    (11, 12),
    (11, 13),
    (13, 15),
    (12, 14),
    (14, 16),
)


@dataclass(frozen=True)
class BSTPlayer:
    bbox: np.ndarray  # original image xyxy
    keypoints: np.ndarray  # original image COCO-17 xy or xy+score
    observed: bool = True  # False for reused/propagated/unavailable pose


@dataclass(frozen=True)
class BSTFrame:
    frame_idx: int
    players: Sequence[BSTPlayer]
    shuttle_xy: tuple[float, float] | None  # observed image position, never ground-plane shuttle
    homography: Homography | None  # mapping for THIS image, including camera motion
    shot_id: int = 0


@dataclass(frozen=True)
class BSTSequence:
    pose: np.ndarray  # 100,2,72
    shuttle: np.ndarray  # 100,2
    positions: np.ndarray  # 100,2,2
    video_len: int
    source_frames: tuple[int, ...]
    usable_frames: int


@dataclass(frozen=True)
class BSTResult:
    prediction: StrokePrediction
    class_probabilities: tuple[float, ...]
    side_probabilities: dict[str, float]
    usable_frames: int
    video_len: int


def contact_window(frame: int, fps: float, previous: int | None, following: int | None) -> tuple[int, int]:
    """Official between-two-hits bounds, half-open and clamped at video start.

    A caller must have observed the entire interval before requesting inference.
    The next contact must come from detection, never reference labels in an
    end-to-end evaluation. Reference anchors may be used only for a separately
    labelled oracle-contact diagnostic.
    """
    if not math.isfinite(fps) or fps <= 0 or frame < 0:
        raise ValueError("invalid video time")
    if (previous is not None and previous >= frame) or (following is not None and following <= frame):
        raise ValueError("contacts must be chronological")
    half = int(fps // 2)
    epsilon = half // 2
    limit = int(fps * 3 // 2)
    start = previous if previous is not None else frame - half
    end = following + epsilon if following is not None else frame + half
    return max(0, start, frame - limit), min(end, frame + limit + epsilon)


def _frame_features(frame: BSTFrame, frame_size: tuple[int, int]) -> tuple[np.ndarray, np.ndarray, np.ndarray, bool]:
    joints = np.zeros((2, 17, 2), dtype=np.float32)
    positions = np.zeros((2, 2), dtype=np.float32)
    shuttle = np.zeros(2, dtype=np.float32)
    if frame.homography is None:
        return joints, positions, shuttle, False
    eligible = []
    for person in frame.players:
        kps, bbox = np.asarray(person.keypoints), np.asarray(person.bbox)
        if not person.observed or kps.shape not in ((17, 2), (17, 3)) or bbox.shape != (4,):
            continue
        if not np.isfinite(bbox).all() or np.any(bbox[2:] <= bbox[:2]):
            continue
        xy = kps[:, :2].copy()
        present = np.isfinite(xy).all(axis=1)
        if kps.shape[1] == 3:
            present &= np.isfinite(kps[:, 2]) & (kps[:, 2] > 0)
        if not present[15:17].all() or not (xy[15:17] != 0).all():
            continue
        xy[~present] = 0  # explicit missing sentinel; no interpolation
        # Project BOTH ankles before averaging; homography is not linear.
        ankle_court = frame.homography.image_to_court(xy[15:17]).mean(axis=0)
        pos = np.array([(ankle_court[0] + WIDTH_DOUBLES / 2) / WIDTH_DOUBLES, (HALF_LEN - ankle_court[1]) / LENGTH])
        if not np.isfinite(pos).all() or not ((pos > -0.01) & (pos < 1.01)).all():
            continue
        diagonal = np.linalg.norm(bbox[2:] - bbox[:2])
        # Official center_align=True also shifts zero-coordinate sentinels.
        norm = np.where(xy != 0, (xy - bbox[:2]) / diagonal, 0)
        norm -= (bbox[2:] - bbox[:2]) / (2 * diagonal)
        eligible.append((pos, norm))
    if len(eligible) != 2:
        # Official preparation zeros ALL modalities when two players are absent.
        return joints, positions, shuttle, False
    eligible.sort(key=lambda item: item[0][1])
    for i, (pos, norm) in enumerate(eligible):
        joints[i], positions[i] = norm, pos
    if frame.shuttle_xy is not None:
        raw = np.asarray(frame.shuttle_xy)
        if raw.shape == (2,) and np.isfinite(raw).all():
            shuttle = (raw / np.asarray(frame_size)).astype(np.float32)
    return joints, positions, shuttle, True


def prepare_sequence(frames: Sequence[BSTFrame], frame_size: tuple[int, int], *, match_format: str) -> BSTSequence:
    """Build exact pretrained inputs; reject unsupported doubles and mixed shots."""
    if match_format != "singles":
        raise ValueError("BST-CG-AP checkpoint supports singles only")
    if not frames or min(frame_size) <= 0:
        raise ValueError("nonempty temporal observations and positive image size required")
    indices = np.asarray([f.frame_idx for f in frames])
    if np.any(np.diff(indices) != 1):
        raise ValueError("BST requires chronological contiguous observations")
    if len({f.shot_id for f in frames}) != 1:
        raise ValueError("BST context cannot cross camera shots")
    features = [_frame_features(f, frame_size) for f in frames]
    joints, positions, shuttle = (np.stack([f[i] for f in features]) for i in range(3))
    usable = np.asarray([f[3] for f in features])
    if len(frames) > SEQ_LEN:
        # Reproduce the official stride/truncation rule, not generic interpolation.
        stride = len(frames) // SEQ_LEN + int(len(frames) % SEQ_LEN > SEQ_LEN // 2)
        joints, positions, shuttle, indices, usable = (
            v[::stride][:SEQ_LEN] for v in (joints, positions, shuttle, indices, usable)
        )
    length = len(indices)
    if not usable.any():
        raise ValueError("no observed two-player pose frames in BST context")
    pad = SEQ_LEN - length
    joints = np.pad(joints, ((0, pad), (0, 0), (0, 0), (0, 0)))
    positions = np.pad(positions, ((0, pad), (0, 0), (0, 0)))
    shuttle = np.pad(shuttle, ((0, pad), (0, 0)))
    bones = np.stack(
        [
            np.where((joints[:, :, a] != 0) & (joints[:, :, b] != 0), joints[:, :, b] - joints[:, :, a], 0)
            for a, b in BONE_PAIRS
        ],
        axis=-2,
    )
    pose = np.concatenate((joints, bones), axis=-2).reshape(SEQ_LEN, 2, 72)
    return BSTSequence(pose, shuttle, positions, length, tuple(int(i) for i in indices), int(usable.sum()))


class BSTClassifier:
    """Pinned, strictly loaded pretrained model; explicitly invoked shadow use."""

    name = "bst_cg_ap_shuttleset_merged25"

    def __init__(self, checkpoint: Path, *, device: str = "cpu"):
        from bai_badminton.events._bst_network import BST_CG_AP

        with checkpoint.open("rb") as stream:
            actual_hash = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual_hash != CHECKPOINT_SHA256:
            raise ValueError("BST checkpoint digest does not match pinned official weights")
        self.device = torch.device(device)
        self.model = BST_CG_AP(in_dim=72, seq_len=SEQ_LEN, n_class=25)
        state = torch.load(checkpoint, map_location="cpu", weights_only=True)
        self.model.load_state_dict(state, strict=True)
        self.model.to(self.device).eval()

    @torch.inference_mode()
    def predict_sequence(self, sequence: BSTSequence) -> BSTResult:
        if sequence.usable_frames <= 0 or not 0 < sequence.video_len <= SEQ_LEN:
            raise ValueError("empty temporal evidence")
        arrays = (sequence.pose, sequence.shuttle, sequence.positions)
        if tuple(a.shape for a in arrays) != ((SEQ_LEN, 2, 72), (SEQ_LEN, 2), (SEQ_LEN, 2, 2)):
            raise ValueError("invalid BST input dimensions")
        if any(not np.isfinite(a).all() for a in arrays):
            raise ValueError("non-finite temporal evidence")
        tensor = [torch.as_tensor(a, dtype=torch.float32, device=self.device).unsqueeze(0) for a in arrays]
        lengths = torch.tensor([sequence.video_len], dtype=torch.long, device=self.device)
        logits = self.model(*tensor, lengths)
        if logits.shape != (1, 25) or not torch.isfinite(logits).all():
            raise RuntimeError("invalid BST logits")
        p = logits.softmax(dim=-1)[0].cpu().numpy()
        # Marginalize the official side×stroke classes; retain side uncertainty separately.
        probs = {"unknown": float(p[0])}
        probs.update({stroke: float(p[1 + i] + p[13 + i]) for i, stroke in enumerate(STROKES)})
        sides = {"unknown": float(p[0]), "far": float(p[1:13].sum()), "near": float(p[13:25].sum())}
        return BSTResult(
            StrokePrediction(probs, self.name),
            tuple(float(v) for v in p),
            sides,
            sequence.usable_frames,
            sequence.video_len,
        )
