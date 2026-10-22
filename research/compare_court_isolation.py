"""Compare geometric leakage in saved old/new perception; not detection accuracy."""

import json
import sqlite3
from pathlib import Path

import cv2
import msgpack
import numpy as np

from bai_badminton.court import REFERENCE_POINTS, Homography
from bai_badminton.perception.isolation import flight_mask
from bai_badminton.perception.players import CourtROI

root = Path("data/court-evaluation")
current = Path("data/sessions/01M5EXGZNEVGYAJ3AR6CJS5ZG9")
c = sqlite3.connect(current / "events.sqlite")
cal = json.loads(c.execute("select body from events where type='calibration' order by seq desc limit 1").fetchone()[0])[
    "payload"
]
h = Homography.from_json(cal)
poly = h.court_to_image(
    np.array([REFERENCE_POINTS[k] for k in ("far_left", "far_right", "near_right", "near_left")])
).astype(np.float32)
roi = CourtROI(poly, homography=h)
mask = flight_mask(poly, (1270, 720), (1270, 720))
distance_outside = cv2.distanceTransform(1 - mask, cv2.DIST_L2, 5)


def collect(path, minimum_version=1):
    frames = {}
    for p in sorted((path / "perception").glob("*.msgpack")):
        d = msgpack.unpackb(p.read_bytes(), raw=False)
        if d.get("v", 1) < minimum_version:
            continue
        for f in d["frames"]:
            frames[f["f"]] = f
    return frames


old, new = collect(root / "before-fixing-one"), collect(current, 5)
common = sorted(old.keys() & new.keys())


def metrics(frames):
    rows = [frames[i] for i in common]
    people = [p for f in rows for p in f["p"]]
    shuttle = [f["s"] for f in rows if f["s"] is not None]
    outside = 0
    max_distance = 0.0
    for x, y in shuttle:
        in_frame = 0 <= round(x) < 1270 and 0 <= round(y) < 720
        outside += not (in_frame and mask[round(y), round(x)])
        if in_frame:
            max_distance = max(max_distance, float(distance_outside[round(y), round(x)]))
    return {
        "frames": len(rows),
        "main_frames": sum(f.get("v") == "main" for f in rows),
        "player_observations": len(people),
        "players_outside_selected_court": sum(not roi.contains_feet(np.array(p["b"])) for p in people),
        "shuttle_observations": len(shuttle),
        "shuttles_outside_flight_region": outside,
        "maximum_shuttle_edge_distance_px": round(max_distance, 2),
        "camera_heads": sorted(set(f.get("h") for f in rows if f.get("h") is not None)),
    }


result = {
    "before": metrics(old),
    "after": metrics(new),
    "fixed_camera": cal.get("fixed_camera"),
    "caveat": "Geometric leakage only; not labelled object accuracy or event precision/recall.",
}
(root / "comparison.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
cap = cv2.VideoCapture("data/media/90d1f399c05312ede173de2f2c8cd2fee09f1d201df46b476119660a00039ff0/proxy.mp4")
for idx in (0, 900, 3600, 7200, 12000, 18000, 22000):
    if idx not in new:
        continue
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ok, img = cap.read()
    if not ok:
        continue
    sides = []
    for title, fp in (("BEFORE", old[idx]), ("AFTER", new[idx])):
        out = img.copy()
        for p in fp["p"]:
            b = np.array(p["b"], int)
            color = (255, 150, 0) if roi.contains_feet(b) else (0, 0, 255)
            cv2.rectangle(out, tuple(b[:2]), tuple(b[2:]), color, 2)
        if fp["s"]:
            cv2.circle(out, tuple(np.array(fp["s"], int)), 8, (0, 255, 255), 2)
        cv2.polylines(out, [poly.astype(int)], True, (0, 255, 0), 2)
        cv2.putText(out, title, (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 3)
        sides.append(cv2.resize(out, (635, 360)))
    cv2.imwrite(str(root / f"comparison-{idx}.jpg"), np.hstack(sides))
