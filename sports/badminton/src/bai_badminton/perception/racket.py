"""Local classical racket observations from a visible ellipse, shaft and posed wrist.

No weights, inferred equipment points, or neural accuracy claims. This conservative
detector misses blurred/occluded or edge-on rackets; missing output stays missing.
All thresholds express image geometry rather than calibrated probabilities.
"""

from __future__ import annotations

from collections import Counter

import cv2
import numpy as np

from bai_badminton.perception_types import PersonObs, RacketObservation

METHOD = "opencv_ellipse_shaft_v1"


class RacketDetector:
    def detect(self, image: np.ndarray, persons: list[PersonObs]) -> dict[int, RacketObservation]:
        if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 3 or min(image.shape[:2]) < 2:
            raise ValueError("racket detector requires a nonempty uint8 BGR image")
        height, width = image.shape[:2]
        proposals: list[tuple[int, float, RacketObservation]] = []
        counts = Counter(person.track_id for person in persons)
        for person in persons:
            if (
                person.track_id < 0
                or person.detector_matched is not True
                or person.kps is None
                or counts[person.track_id] != 1
                or not np.isfinite(person.conf)
                or not 0.5 <= person.conf <= 1
                or person.kps.shape != (17, 3)
                or not np.isfinite(person.bbox).all()
            ):
                continue
            body = float(person.bbox[3] - person.bbox[1])
            if body < 20:
                continue
            for wrist in (9, 10):
                point = person.kps[wrist]
                if (
                    not np.isfinite(point).all()
                    or point[2] < 0.5
                    or not (0 <= point[0] < width and 0 <= point[1] < height)
                ):
                    continue
                radius = round(0.75 * body)
                x0, y0 = max(0, int(point[0]) - radius), max(0, int(point[1]) - radius)
                x1, y1 = min(width, int(point[0]) + radius), min(height, int(point[1]) + radius)
                grey = cv2.cvtColor(image[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(grey, 45, 130)
                contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
                for contour in contours:
                    if len(contour) < 12:
                        continue
                    try:
                        (cx, cy), axes, angle = cv2.fitEllipse(contour)
                    except cv2.error:
                        continue
                    if not np.isfinite([cx, cy, *axes, angle]).all():
                        continue
                    if min(axes) < 0.07 * body or max(axes) > 0.5 * body or min(axes) / max(axes) < 0.35:
                        continue
                    radians = np.deg2rad(angle)
                    rotation = np.array([[np.cos(radians), np.sin(radians)], [-np.sin(radians), np.cos(radians)]])
                    normalized = (contour[:, 0] - [cx, cy]) @ rotation.T / (np.asarray(axes) / 2)
                    radial = np.linalg.norm(normalized, axis=1)
                    fit_error = float(np.median(np.abs(radial - 1)))
                    angles = np.arctan2(normalized[:, 1], normalized[:, 0])
                    coverage = len(np.unique(np.floor((angles + np.pi) * 12 / (2 * np.pi)))) / 12
                    center = np.array([cx + x0, cy + y0])
                    to_wrist = point[:2] - center
                    length = float(np.linalg.norm(to_wrist))
                    wrist_radius = float(np.linalg.norm(rotation @ to_wrist / (np.asarray(axes) / 2)))
                    if fit_error > 0.16 or coverage < 0.75 or wrist_radius < 1.4 or length > 0.7 * body:
                        continue
                    # Require an actual bright/dark shaft edge along the gap from
                    # the ellipse rim to the wrist, tolerating a few pixels of blur.
                    rim = center + to_wrist / wrist_radius
                    sample = rim[None] + np.linspace(0.15, 0.9, 24)[:, None] * (point[:2] - rim)[None]
                    local = np.rint(sample - [x0, y0]).astype(int)
                    thick = cv2.dilate(edges, np.ones((5, 5), np.uint8))
                    valid = (
                        (local[:, 0] >= 0)
                        & (local[:, 0] < grey.shape[1])
                        & (local[:, 1] >= 0)
                        & (local[:, 1] < grey.shape[0])
                    )
                    shaft = float(np.mean(thick[local[valid, 1], local[valid, 0]] > 0)) if valid.all() else 0
                    if shaft < 0.65:
                        continue
                    support = float(np.clip(0.5 + 0.25 * (1 - fit_error / 0.16) + 0.25 * shaft, 0, 1))
                    observation = RacketObservation(tuple(center), tuple(axes), float(angle), support, wrist)
                    proposals.append((person.track_id, length / body, observation))
        result: dict[int, RacketObservation] = {}
        for owner, distance, observation in sorted(proposals, key=lambda row: -row[2].confidence):
            # The same ellipse claimed by two people cannot establish ownership.
            competitors = [
                (other, gap)
                for other, gap, racket in proposals
                if other != owner
                and np.linalg.norm(np.asarray(racket.center) - observation.center) < min(observation.axes) / 2
            ]
            if any(gap <= distance + 0.05 for _, gap in competitors):
                continue
            result.setdefault(owner, observation)
        return result
