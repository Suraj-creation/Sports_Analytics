"""Bounded, checksum-verified local OSNet appearance extraction.

This adapter never downloads weights, stores descriptors, matches tracks, or
claims identity. The fixed checkpoint is verified before any model is loaded.
Matching decisions belong to a separate associator; this adapter does not infer
identities. Neural descriptors are ephemeral and must never enter event/cache data.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np

CHECKPOINT_SHA256 = "ce171fe160b3608f5e4c19489774991419be965b1d6f4bdccc4b4cfd2ef95347"
MODEL_NAME = "osnet_ain_x0_25"


def _vendor_embedder() -> Any:
    from bai_badminton.perception._vendor.osnet_ain import OSNetEmbedder

    return OSNetEmbedder


def _digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


class OSNetAppearanceEmbedder:
    """Extract bounded appearance vectors for review or private online matching.

    `frame` is a BGR uint8 image and `boxes` are in-frame xyxy pixel bounds.
    Device is explicit (e.g. cpu or cuda:0). No tracker or event state is changed.
    """

    def __init__(self, checkpoint: str | Path, *, device: str, max_crops: int = 8) -> None:
        if not device or not 1 <= max_crops <= 16:
            raise ValueError("explicit device and crop limit between 1 and 16 required")
        self.checkpoint = Path(checkpoint)
        if not self.checkpoint.is_file() or _digest(self.checkpoint) != CHECKPOINT_SHA256:
            raise ValueError("checkpoint checksum mismatch or file unavailable")
        self.max_crops = max_crops
        self.device = device
        self._embedder = _vendor_embedder()(variant=MODEL_NAME, weights=self.checkpoint, device=device)

    @property
    def fingerprint(self) -> str:
        return f"{MODEL_NAME}:{CHECKPOINT_SHA256}:fp32:rgb128x256"

    def embed(self, frame: np.ndarray, boxes: Any) -> np.ndarray:
        frame = np.asarray(frame)
        if (
            frame.dtype != np.uint8
            or frame.ndim != 3
            or frame.shape[2] != 3
            or min(frame.shape[:2]) < 1
            or frame.shape[0] * frame.shape[1] > 3840 * 2160
        ):
            raise ValueError("frame must be a BGR uint8 image")
        try:
            b = np.asarray(boxes, dtype=np.float64)
        except (TypeError, ValueError) as exc:
            raise ValueError("boxes must be finite xyxy coordinates") from exc
        if b.size == 0:
            return np.empty((0, 512), dtype=np.float32)
        if b.ndim != 2 or b.shape[1] != 4 or not np.isfinite(b).all():
            raise ValueError("boxes must be finite xyxy coordinates")
        if len(b) > self.max_crops:
            raise ValueError("crop batch exceeds limit")
        h, w = frame.shape[:2]
        if np.any(b[:, 0] < 0) or np.any(b[:, 1] < 0) or np.any(b[:, 2] > w) or np.any(b[:, 3] > h):
            raise ValueError("crop is outside frame")
        # The vendor rounds coordinates before cropping; reject boxes that round to empty.
        rounded = np.rint(b)
        if np.any(rounded[:, 2] <= rounded[:, 0]) or np.any(rounded[:, 3] <= rounded[:, 1]):
            raise ValueError("crop is empty")
        rgb = np.ascontiguousarray(frame[:, :, ::-1])
        result = np.asarray(self._embedder(rgb, b), dtype=np.float32)
        if result.shape != (len(b), 512) or not np.isfinite(result).all():
            raise ValueError("model returned invalid embeddings")
        norms = np.linalg.norm(result, axis=1)
        if not np.isfinite(norms).all() or np.any(norms < 1e-8):
            raise ValueError("model returned empty embeddings")
        return result / norms[:, None]


# Existing opt-in review scripts keep the same validated adapter and contract.
OSNetReviewEmbedder = OSNetAppearanceEmbedder


def compare_features(a: Any, b: Any) -> dict[str, Any]:
    """Return a similarity cue, never a participant assignment or probability."""
    x, y = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if x.ndim != 1 or x.shape != y.shape or not x.size or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("features must be equally sized finite vectors")
    den = float(np.linalg.norm(x) * np.linalg.norm(y))
    if not np.isfinite(den) or den <= 1e-8:
        raise ValueError("features must be nonzero")
    return {
        "cosine_similarity": float(np.clip(np.dot(x, y) / den, -1.0, 1.0)),
        "identity_decision": "unresolved",
        "calibrated_probability": None,
    }
