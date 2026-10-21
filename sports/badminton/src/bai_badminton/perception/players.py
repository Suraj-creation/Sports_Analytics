"""Player detection, tracking and pose.

* **Detection** — RF-DETR (Apache-2.0, ONNX via ``rtmlib``; YOLOX-humanart as an alternative) on
  a court region of interest; person class only; boxes whose feet fall outside the (padded)
  court polygon are discarded (umpires, line judges, coaches, crowd).
* **Tracking** — ByteTrack (Roboflow ``trackers``, Apache-2.0).  The detector runs every
  ``stride`` frames; in between, the tracker's Kalman prediction carries the boxes.
* **Pose** — RTMPose (Apache-2.0) top-down on full-resolution crops of the (at most two) players.
* **Appearance** — an HSV torso signature per box for identity re-linking after cuts.

ONNX Runtime sessions are created by the platform (``ort_providers``) so TensorRT / CUDA / CPU
execution providers and the TensorRT engine cache are controlled per profile.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from numpy.typing import NDArray

from bai_badminton.identity import hsv_signature
from bai_badminton.perception_types import PersonObs

PERSON = 0


def _swap_session(tool: Any, onnx_path: Path, providers: list[Any]) -> None:
    """Replace an rtmlib tool's ORT session with one using the platform's providers."""
    import onnxruntime as ort

    so = ort.SessionOptions()
    so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    tool.session = ort.InferenceSession(str(onnx_path), sess_options=so, providers=providers)


@dataclass
class CourtROI:
    """Court polygon in image px (padded) used to crop detection and gate boxes by their feet."""

    polygon: NDArray[np.float32]  # (N, 2)
    pad_px: float = 60.0

    def contains_feet(self, bbox: NDArray[np.float64]) -> bool:
        feet = (float((bbox[0] + bbox[2]) / 2), float(bbox[3]))
        return cv2.pointPolygonTest(self.polygon.reshape(-1, 1, 2), feet, True) >= -self.pad_px

    def crop_box(self, w: int, h: int, top_margin: float = 0.25) -> tuple[int, int, int, int]:
        """Axis-aligned crop around the court, extended upwards for the far player's body/jumps."""
        x1, y1 = self.polygon.min(axis=0)
        x2, y2 = self.polygon.max(axis=0)
        ext = (y2 - y1) * top_margin
        return (
            int(max(0, x1 - self.pad_px)),
            int(max(0, y1 - ext - self.pad_px)),
            int(min(w, x2 + self.pad_px)),
            int(min(h, y2 + self.pad_px)),
        )


class PlayerDetector:
    def __init__(
        self,
        onnx_path: Path,
        input_size: tuple[int, int],
        providers: list[Any],
        score_thr: float = 0.35,
        kind: str = "rfdetr",
    ) -> None:
        if kind == "rfdetr":
            from rtmlib import RFDETR

            self.tool = RFDETR(str(onnx_path), model_input_size=(input_size[1], input_size[0]), score_thr=score_thr)
        else:
            from rtmlib import YOLOX

            self.tool = YOLOX(str(onnx_path), model_input_size=input_size, score_thr=score_thr)
        _swap_session(self.tool, onnx_path, providers)
        self.kind = kind

    def __call__(self, img: NDArray[np.uint8]) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Person boxes (N,4) xyxy and scores (N,) in ``img`` coordinates."""
        if self.kind == "rfdetr":
            return self._rfdetr(img)
        boxes = np.asarray(self.tool(img), dtype=np.float64).reshape(-1, 4)
        return boxes, np.ones(len(boxes))

    def _rfdetr(self, img: NDArray[np.uint8]) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        # rtmlib's "human" mode drops scores, which ByteTrack needs — decode the raw DETR outputs:
        # boxes (1, Q, 4) normalised cxcywh, logits (1, Q, C) with background at index 0.
        pre, ori = self.tool.preprocess(img)
        outs = self.tool.inference(pre)
        boxes, logits = (outs[0], outs[1]) if outs[0].shape[-1] == 4 else (outs[1], outs[0])
        prob = 1.0 / (1.0 + np.exp(-logits[0].astype(np.float64)))
        person = prob[:, PERSON + 1]
        best = prob[:, 1:].argmax(axis=1)
        keep = (person >= self.tool.score_thr) & (best == PERSON)
        b = boxes[0][keep].astype(np.float64)
        h, w = float(ori[0]), float(ori[1])
        xyxy = np.stack(
            [
                (b[:, 0] - b[:, 2] / 2) * w,
                (b[:, 1] - b[:, 3] / 2) * h,
                (b[:, 0] + b[:, 2] / 2) * w,
                (b[:, 1] + b[:, 3] / 2) * h,
            ],
            axis=1,
        )
        return _nms(xyxy, person[keep], 0.6)


def _nms(
    boxes: NDArray[np.float64], scores: NDArray[np.float64], iou: float
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    if len(boxes) == 0:
        return boxes.reshape(0, 4), scores
    xywh = np.concatenate([boxes[:, :2], boxes[:, 2:] - boxes[:, :2]], axis=1)
    idx = cv2.dnn.NMSBoxes(xywh.tolist(), scores.tolist(), 0.0, iou)
    idx = np.asarray(idx).reshape(-1)
    return boxes[idx], scores[idx]


class PoseEstimator:
    def __init__(self, onnx_path: Path, input_size: tuple[int, int], providers: list[Any]) -> None:
        from rtmlib import RTMPose

        self.tool = RTMPose(str(onnx_path), model_input_size=input_size)
        _swap_session(self.tool, onnx_path, providers)

    def __call__(self, img: NDArray[np.uint8], boxes: list[NDArray[np.float64]]) -> list[NDArray[np.float64]]:
        if not boxes:
            return []
        kps, scores = self.tool(img, bboxes=[b.tolist() for b in boxes])
        return [np.concatenate([kps[i], scores[i][:, None]], axis=1).astype(np.float64) for i in range(len(boxes))]


class PlayerTracker:
    """ByteTrack over detector outputs; predicts between detection frames."""

    def __init__(self, fps: float) -> None:
        from trackers import ByteTrackTracker

        self._tracker = ByteTrackTracker(
            frame_rate=fps,
            lost_track_buffer=int(fps),
            track_activation_threshold=0.4,
            minimum_consecutive_frames=1,
            high_conf_det_threshold=0.5,
        )
        self.fps = fps

    def reset(self) -> None:
        self.__init__(self.fps)  # type: ignore[misc]

    def update(
        self, boxes: NDArray[np.float64], scores: NDArray[np.float64]
    ) -> list[tuple[int, NDArray[np.float64], float]]:
        import supervision as sv

        det = sv.Detections(
            xyxy=boxes.astype(np.float32).reshape(-1, 4),
            confidence=scores.astype(np.float32),
            class_id=np.zeros(len(boxes), int),
        )
        tracked = self._tracker.update(det)
        out = []
        for i in range(len(tracked)):
            tid = int(tracked.tracker_id[i]) if tracked.tracker_id is not None else -1
            if tid < 0:
                continue
            conf = float(tracked.confidence[i]) if tracked.confidence is not None else 1.0
            out.append((tid, np.asarray(tracked.xyxy[i], dtype=np.float64), conf))
        return out


class PlayerPerception:
    """Detection (strided) → tracking → court gating → pose → appearance, per frame."""

    def __init__(
        self,
        detector: PlayerDetector | None,
        pose: PoseEstimator | None,
        fps: float,
        det_stride: int = 2,
        pose_stride: int = 1,
        max_players: int = 2,
    ) -> None:
        self.detector, self.pose = detector, pose
        self.tracker = PlayerTracker(fps)
        self.det_stride, self.pose_stride = max(1, det_stride), max(1, pose_stride)
        self.max_players = max_players
        self.roi: CourtROI | None = None
        self._last: list[PersonObs] = []

    def set_roi(self, roi: CourtROI | None) -> None:
        self.roi = roi

    def on_cut(self) -> None:
        self.tracker.reset()
        self._last = []

    def process(
        self, frame_idx: int, img: NDArray[np.uint8], strides: tuple[int, int] | None = None
    ) -> list[PersonObs]:
        det_stride, pose_stride = strides or (self.det_stride, self.pose_stride)
        if self.detector is None or det_stride == 0:
            return []
        if frame_idx % det_stride != 0:
            return self._carry(frame_idx, img, pose_stride)
        h, w = img.shape[:2]
        x0, y0 = 0, 0
        view = img
        if self.roi is not None:
            x0, y0, x1, y1 = self.roi.crop_box(w, h)
            view = img[y0:y1, x0:x1]
        boxes, scores = self.detector(view)
        if len(boxes):
            boxes = boxes + np.array([x0, y0, x0, y0], dtype=np.float64)
        if self.roi is not None and len(boxes):
            keep = np.array([self.roi.contains_feet(b) for b in boxes], bool)
            boxes, scores = boxes[keep], scores[keep]
        tracks = self.tracker.update(boxes, scores)
        tracks.sort(key=lambda t: -t[2] * (t[1][3] - t[1][1]))
        persons = [PersonObs(track_id=tid, bbox=b, conf=c) for tid, b, c in tracks[: self.max_players + 2]]
        self._attach(frame_idx, img, persons, pose_stride)
        self._last = persons
        return persons

    def _carry(self, frame_idx: int, img: NDArray[np.uint8], pose_stride: int) -> list[PersonObs]:
        persons = [PersonObs(track_id=p.track_id, bbox=p.bbox.copy(), conf=p.conf * 0.98) for p in self._last]
        self._attach(frame_idx, img, persons, pose_stride)
        return persons

    def _attach(self, frame_idx: int, img: NDArray[np.uint8], persons: list[PersonObs], pose_stride: int) -> None:
        if self.pose is not None and pose_stride and frame_idx % pose_stride == 0 and persons:
            for p, k in zip(persons, self.pose(img, [p.bbox for p in persons]), strict=True):
                p.kps = k
        for p in persons:
            x1, y1, x2, y2 = (int(v) for v in p.bbox)
            crop = img[max(0, y1) : max(0, y2), max(0, x1) : max(0, x2)]
            p.appearance = hsv_signature(crop) if crop.size else None
