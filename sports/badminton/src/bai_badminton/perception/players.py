"""Player detection, tracking and pose.

* **Detection** — RF-DETR (Apache-2.0, ONNX via ``rtmlib``; YOLOX-humanart as an alternative) on
  a court region of interest; person class only; boxes whose feet fall outside the (padded)
  court polygon are discarded (umpires, line judges, coaches, crowd).
* **Tracking** — ByteTrack (Roboflow ``trackers``, Apache-2.0).  The detector runs every
  ``stride`` frames; in between, the last observed boxes are carried forward without a new detection.
* **Pose** — RTMPose (Apache-2.0) top-down on full-resolution crops of court-player candidates.
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

from bai_badminton.court import HALF_LEN, WIDTH_DOUBLES, Homography
from bai_badminton.identity import hsv_signature
from bai_badminton.perception.player_association import PersistentPlayerAssociator
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
    homography: Homography | None = None
    side_margin_m: float = 0.35
    end_margin_m: float = 0.75

    def contains_feet(self, bbox: NDArray[np.float64], *, allow_runoff: bool = True) -> bool:
        feet = (float((bbox[0] + bbox[2]) / 2), float(bbox[3]))
        if self.homography is not None:
            x, y = self.homography.image_to_court(np.array([feet]))[0]
            return bool(
                np.isfinite([x, y]).all()
                and abs(x) <= WIDTH_DOUBLES / 2 + (self.side_margin_m if allow_runoff else 0.0)
                and abs(y) <= HALF_LEN + (self.end_margin_m if allow_runoff else 0.0)
            )
        return cv2.pointPolygonTest(self.polygon.reshape(-1, 1, 2), feet, True) >= (
            -self.pad_px if allow_runoff else 0.0
        )

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
        # RF-DETR's exported backbone expects RGB. rtmlib only normalises and
        # transposes its input; decoded frames and court crops here are BGR.
        pre, ori = self.tool.preprocess(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
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
        # The checkpoint's MMDeploy pipeline specifies Normalize(to_rgb=True).
        # rtmlib performs the affine crop and normalisation, but no colour swap.
        kps, scores = self.tool(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), bboxes=[b.tolist() for b in boxes])
        return [np.concatenate([kps[i], scores[i][:, None]], axis=1).astype(np.float64) for i in range(len(boxes))]


class PlayerTracker:
    """ByteTrack over detector outputs using elapsed video time between detections."""

    def __init__(self, fps: float) -> None:
        from trackers import ByteTrackTracker

        self._tracker = ByteTrackTracker(
            frame_rate=fps,
            lost_track_buffer=30,  # expressed in 30-FPS frames: one second at any source rate
            track_activation_threshold=0.4,
            minimum_consecutive_frames=1,
            high_conf_det_threshold=0.5,
        )
        self.fps = fps

    def reset(self) -> None:
        self.__init__(self.fps)  # type: ignore[misc]

    def update(
        self, boxes: NDArray[np.float64], scores: NDArray[np.float64], frame_idx: int
    ) -> list[tuple[int, NDArray[np.float64], float]]:
        import supervision as sv

        det = sv.Detections(
            xyxy=boxes.astype(np.float32).reshape(-1, 4),
            confidence=scores.astype(np.float32),
            class_id=np.zeros(len(boxes), int),
        )
        # Detector cadence changes with rally state. Timestamp mode gives the
        # motion model and lost-track expiry elapsed video time, not call count.
        tracked = self._tracker.update(det, timestamp=frame_idx / self.fps)
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
        reid: Any | None = None,
    ) -> None:
        self.detector, self.pose = detector, pose
        self.last_detector_observed = False
        self.last_capacity_limited = False
        self.tracker = PlayerTracker(fps)
        self.det_stride, self.pose_stride = max(1, det_stride), max(1, pose_stride)
        self.max_players = max_players
        self.reid = reid
        self._reid_fingerprint = getattr(reid, "fingerprint", None)
        self._associator = PersistentPlayerAssociator(fps) if reid is not None else None
        self.last_identity_error: str | None = None
        self.roi: CourtROI | None = None
        self._last: list[PersonObs] = []
        self._admitted: dict[int, int] = {}
        self._court_tracks: dict[int, tuple[int, NDArray[np.float64]]] = {}
        self._last_detection_frame: int | None = None
        self.fps = fps

    @property
    def identity_policy(self) -> dict[str, Any]:
        """Cache provenance for association behavior; no neural features leave this object."""
        return {
            "state": "degraded"
            if self.last_identity_error is not None
            else "enabled"
            if self._associator
            else "disabled",
            "model": self._reid_fingerprint,
            "policy": self._associator.policy_fingerprint if self._associator else "bytetrack_v1",
            "court_membership": "observed_box_continuity_v1",
        }

    def set_roi(self, roi: CourtROI | None) -> None:
        self.roi = roi

    def on_cut(self) -> None:
        self.tracker.reset()
        self._last = []
        self._admitted.clear()
        self._court_tracks.clear()
        self._last_detection_frame = None
        if self._associator is not None:
            self._associator.reset()

    def process(
        self, frame_idx: int, img: NDArray[np.uint8], strides: tuple[int, int] | None = None
    ) -> list[PersonObs]:
        self.last_detector_observed = False
        self.last_capacity_limited = False
        det_stride, pose_stride = strides or (self.det_stride, self.pose_stride)
        if self.detector is None or det_stride == 0:
            return []
        if frame_idx % det_stride != 0:
            return self._carry(frame_idx, img, pose_stride, det_stride)
        h, w = img.shape[:2]
        x0, y0 = 0, 0
        view = img
        if self.roi is not None:
            x0, y0, x1, y1 = self.roi.crop_box(w, h)
            view = img[y0:y1, x0:x1]
        boxes, scores = self.detector(view)
        self.last_detector_observed = True
        self._last_detection_frame = frame_idx
        if len(boxes):
            boxes = boxes + np.array([x0, y0, x0, y0], dtype=np.float64)
        self._court_tracks = {
            tid: (last, box) for tid, (last, box) in self._court_tracks.items() if frame_idx - last <= self.fps
        }
        continuing: set[int] = set()
        if self.roi is not None and len(boxes):
            keep = np.array([self.roi.contains_feet(b) for b in boxes], bool)
            # Bbox bottoms are ground-plane feet only while grounded. A known
            # athlete can jump above a baseline or run beyond a sideline. Keep
            # a uniquely overlapping current detection of that existing track;
            # do not admit unrelated spectators by expanding the court mask.
            history = list(self._court_tracks.items())
            if history:
                overlap = _box_iou(boxes, np.asarray([value[1][1] for value in history])) >= 0.3
                for i in range(len(boxes)):
                    matches = np.flatnonzero(overlap[i])
                    if len(matches) == 1 and overlap[:, matches[0]].sum() == 1:
                        continuing.add(history[int(matches[0])][0])
                        keep[i] = True
            boxes, scores = boxes[keep], scores[keep]
        tracks = self.tracker.update(boxes, scores, frame_idx)
        self._admitted = {tid: last for tid, last in self._admitted.items() if frame_idx - last <= 2 * self.fps}
        if self.roi is not None:
            tracks = [
                t
                for t in tracks
                if self.roi.contains_feet(t[1], allow_runoff=t[0] in self._admitted) or t[0] in continuing
            ]
        # A doubles overflow is ambiguous: dropping a lower-ranked track could
        # discard a player. Withhold all participant evidence for this frame
        # and its carried frames rather than treating the survivors as certain.
        if self.max_players >= 4 and len(tracks) > self.max_players + 2:
            self.last_capacity_limited = True
            self.last_detector_observed = False
            self._last = []
            return []
        self._admitted.update({t[0]: frame_idx for t in tracks})
        tracks.sort(key=lambda t: -t[2] * (t[1][3] - t[1][1]))
        tracks = tracks[: self.max_players + 2]
        observed = _unique_detection_matches(tracks, boxes)
        for (tid, box, _), matched in zip(tracks, observed, strict=True):
            if matched:
                self._court_tracks[tid] = (frame_idx, box.copy())
        canonical = [tid for tid, _, _ in tracks]
        reasons = ["bytetrack_v1"] * len(tracks)
        if self._associator is not None:
            features = None
            selected = [
                i
                for i, (_, box, conf) in enumerate(tracks)
                if observed[i]
                and conf >= 0.5
                and np.isfinite(box).all()
                and 0 <= box[0] < box[2] <= w
                and 0 <= box[1] < box[3] <= h
            ]
            if self.reid is not None and selected:
                try:
                    features = np.zeros((len(tracks), 512), dtype=np.float32)
                    features[selected] = self.reid.embed(img, [tracks[i][1] for i in selected])
                except (OSError, ValueError, RuntimeError, ImportError) as exc:
                    # Keep the canonical namespace after failure. Reverting to raw
                    # ByteTrack IDs could silently re-use another person's identity.
                    self.last_identity_error = f"{type(exc).__name__}: {exc}"[:300]
                    self.reid, features = None, None
            canonical = self._associator.update(frame_idx, tracks, features, observed=observed)
            reasons = self._associator.last_reason
        persons = [
            PersonObs(
                track_id=canonical[i],
                bbox=b,
                conf=c,
                raw_track_id=tid,
                detector_matched=observed[i],
                identity_method=reasons[i],
            )
            for i, (tid, b, c) in enumerate(tracks)
        ]
        self._attach(frame_idx, img, persons, pose_stride)
        self._last = persons
        return persons

    def _carry(self, frame_idx: int, img: NDArray[np.uint8], pose_stride: int, det_stride: int) -> list[PersonObs]:
        if self._last_detection_frame is None or frame_idx - self._last_detection_frame > det_stride:
            # Scene gating can skip process() for a long interval. Returning to
            # the main camera between detector ticks must not revive old boxes.
            return []
        persons = [
            PersonObs(
                track_id=p.track_id,
                bbox=p.bbox.copy(),
                conf=p.conf * 0.98,
                raw_track_id=p.raw_track_id,
                detector_matched=False,
                identity_method=p.identity_method,
            )
            for p in self._last
            if self.roi is None or self.roi.contains_feet(p.bbox) or p.raw_track_id in self._court_tracks
        ]
        if self._associator is not None:
            canonical = self._associator.update(
                frame_idx,
                [(int(p.raw_track_id), p.bbox, p.conf) for p in persons],
                None,
                observed=[False] * len(persons),
            )
            for i, person in enumerate(persons):
                person.track_id = canonical[i]
                person.identity_method = self._associator.last_reason[i]
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


def _unique_detection_matches(tracks: list[tuple[int, NDArray, float]], boxes: NDArray) -> list[bool]:
    """A tracker output is fresh only when one current detection uniquely supports it.

    ByteTrack can return predictions on a detector-run frame. Neither a raw ID nor
    the frame-level detector flag establishes that this individual was observed.
    """
    if not tracks or len(boxes) == 0:
        return [False] * len(tracks)
    a = np.asarray([box for _, box, _ in tracks], dtype=np.float64)
    b = np.asarray(boxes, dtype=np.float64).reshape(-1, 4)
    iou = _box_iou(a, b)
    valid = np.isfinite(iou) & (iou >= 0.5)
    return [bool(valid[i].sum() == 1 and valid[:, int(valid[i].argmax())].sum() == 1) for i in range(len(tracks))]


def _box_iou(a: NDArray, b: NDArray) -> NDArray[np.float64]:
    intersection = np.prod(
        np.maximum(0, np.minimum(a[:, None, 2:], b[None, :, 2:]) - np.maximum(a[:, None, :2], b[None, :, :2])), axis=2
    )
    union = np.prod(a[:, 2:] - a[:, :2], axis=1)[:, None] + np.prod(b[:, 2:] - b[:, :2], axis=1)[None, :] - intersection
    return np.divide(intersection, union, out=np.zeros_like(intersection), where=union > 0)
