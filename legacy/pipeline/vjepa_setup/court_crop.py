"""
court_crop.py
--------------
Compute a per-video crop box (x1, y1, x2, y2) from a court_annotation.json
(corners + net points), with padding for jump smashes above the court line
and player lunges to the sides.

Usage:
    from court_crop import load_crop_box
    box = load_crop_box("dataset/Test1_Full_rev_court.json", frame_w, frame_h)
"""

import json

# Mapping from the "video" column in clips_index.csv / dataset.csv to the
# court annotation file for that video. Paths are relative to vjepa_setup/
# (on the server, the annotations live under
# ~/Badminton-Video-Analysis/court_dataset/court_dataset/dataset/).
COURT_JSON = {
    "Test1_Full_rev": "../court_dataset/court_dataset/dataset/Test1_Full_rev_court.json",
    "Test3_Full_Rev": "../court_dataset/court_dataset/dataset/Test3_Full_court.json",
    "Test6_Full":     "../court_dataset/court_dataset/dataset/Test6_Full_court.json",
    "Test7_Full":     "../court_dataset/court_dataset/dataset/Test7_Full_court.json",
}


def load_crop_box(court_json_path, frame_w, frame_h, pad_top=250, pad_sides=100, pad_bottom=80):
    with open(court_json_path) as f:
        ann = json.load(f)

    points = list(ann["corners"].values()) + list(
        v for k, v in ann["net"].items() if isinstance(v, list)
    )
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    x1 = max(0, int(min(xs)) - pad_sides)
    y1 = max(0, int(min(ys)) - pad_top)
    x2 = min(frame_w, int(max(xs)) + pad_sides)
    y2 = min(frame_h, int(max(ys)) + pad_bottom)

    return x1, y1, x2, y2
