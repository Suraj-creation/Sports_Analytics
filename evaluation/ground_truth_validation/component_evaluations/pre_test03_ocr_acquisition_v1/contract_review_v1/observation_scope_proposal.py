"""Unregistered diagnostic contract proposal; does not acquire or interpret scores.

Completeness cannot be certified from parse success. This proposal deliberately
has no flag or confidence threshold that promotes cropped observations to a
verified current column. It is not imported by any production component.
"""

from __future__ import annotations

import re
from copy import deepcopy


def capture_scope(*, frame, image_sha256, image_shape, crop, raw, primary_reading):
    """Retain an original read and raw OCR with an explicitly unknown extent."""
    if type(frame) is not int or frame < 0:
        raise ValueError("canonical nonnegative frame required")
    if not isinstance(image_sha256, str) or re.fullmatch(r"[a-f0-9]{64}", image_sha256) is None:
        raise ValueError("exact source-image pixel hash required")
    if len(image_shape) != 3 or any(type(v) is not int or v <= 0 for v in image_shape) or image_shape[2] != 3:
        raise ValueError("exact BGR image shape required")
    if len(crop) != 4 or any(type(v) is not int for v in crop):
        raise ValueError("exact integer crop required")
    x0, y0, x1, y1 = crop
    if not 0 <= x0 < x1 <= image_shape[1] or not 0 <= y0 < y1 <= image_shape[0]:
        raise ValueError("crop must lie inside its bound image")
    if primary_reading is not None and primary_reading.get("frame_idx") != frame:
        raise ValueError("reading is foreign to this canonical frame")
    return {
        "schema": "proposed-score-ocr-acquisition-scope:v1",
        "frame": frame,
        "image_sha256": image_sha256,
        "image_shape": list(image_shape),
        "crop": list(crop),
        "raw_ocr": deepcopy(raw),
        "primary_reading": deepcopy(primary_reading),
        "selection_scope": "rightmost_parseable_field_in_supplied_pixels",
        "board_extent_status": "unknown",
        "current_column_status": "unknown",
        "physical_ground_truth": None,
        "layout_evidence": None,
        "additional_ocr_calls": 0,
    }
