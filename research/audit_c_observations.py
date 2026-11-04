"""Read-only shuttle audit of immutable Test 1 caches; not production inference."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import msgpack
import numpy as np

from bai_badminton.perception.shuttle_post import Track, process

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "outputs/benchmarking/test1"
OUT = ROOT / "artifacts/benchmarking/investigation/audit_c"
OUT.mkdir(parents=True, exist_ok=True)
frames = {}
chunk_positions = {}
chunks = []
for p in sorted((BASE / "runtime/sessions/BenchmarkTest1/perception").glob("*.msgpack")):
    d = msgpack.unpackb(p.read_bytes(), raw=False)
    chunks.append((d["start"], d["end"]))
    for j, f in enumerate(d["frames"]):
        frames[f["f"]] = f
        chunk_positions[f["f"]] = j
assert list(sorted(frames)) == list(range(17268))
f = [frames[i] for i in range(len(frames))]
n = len(f)
raw = np.array([q["s"] is not None for q in f], bool)
conf = np.array([q["c"] for q in f], float)
coords = np.full((n, 2), np.nan)
usable = np.zeros(n, bool)
context = []
for i, q in enumerate(f):
    g = None if q["g"] is None else np.array(q["g"]).reshape(3, 3)
    valid = (
        q["v"] == "main"
        and not q["l"]
        and q["cs"] in (None, "VALID")
        and g is not None
        and np.isfinite(g).all()
        and np.linalg.cond(g) < 1e12
    )
    usable[i] = valid
    context.append((q["sh"], q["r"], valid, q["cs"], q["v"]))
    if raw[i]:
        xy = np.array([*q["s"], 1.0])
        if valid:
            xy = np.linalg.inv(g) @ xy
        coords[i] = xy[:2] / xy[2]
breaks = np.array([False] + [context[i] != context[i - 1] for i in range(1, n)], bool)
track = process(Track.from_arrays(coords[:, 0], coords[:, 1], raw & usable, conf), break_before=breaks)
observed = track.vis & ~track.interp
speed = np.full(n, np.nan)
speed[1:] = np.where(observed[1:] & observed[:-1], np.hypot(np.diff(track.x), np.diff(track.y)), np.nan)
speed[breaks] = np.nan


def runs(mask, a, b):
    found = []
    i = a
    while i <= b:
        if not mask[i]:
            i += 1
            continue
        j = i
        while j + 1 <= b and mask[j + 1]:
            j += 1
        found.append([i, j, j - i + 1])
        i = j + 1
    return found


with (ROOT / "Part2/dataset/Test1_Full/Test1_Full_rally.csv").open() as s:
    gt = list(csv.DictReader(s))
with (BASE / "rally_comparison.csv").open() as s:
    compare = list(csv.DictReader(s))
selected = {2, 19, 20, 27, 5, 23, 25, 28, 29, 31}
by_rally = []
gtmask = np.zeros(n, bool)
for number, (r, c) in enumerate(zip(gt, compare, strict=True), 1):
    a, b = int(r["Start_Frame"]), int(r["End_Frame"])
    gtmask[a : b + 1] = True
    stationary = [
        i for i in range(max(a, 9), b + 1) if sum(observed[j] and speed[j] < 3 for j in range(i - 9, i + 1)) >= 7
    ]
    row = {
        "gt_rally": number,
        "start": a,
        "end": b,
        "selected_failure_case": number in selected,
        "raw_observed_fraction": float(raw[a : b + 1].mean()),
        "valid_geometry_fraction": float(usable[a : b + 1].mean()),
        "postfilter_observed_fraction": float(observed[a : b + 1].mean()),
        "raw_missing_runs_ge10": [r for r in runs(~raw, a, b) if r[2] >= 10],
        "postfilter_missing_runs_ge10": [r for r in runs(~observed, a, b) if r[2] >= 10],
        "interpolated_frames": int(track.interp[a : b + 1].sum()),
        "raw_observed_rejected_or_invalid_frames": int((raw[a : b + 1] & ~observed[a : b + 1]).sum()),
        "stationary_gate_frames_count": len(stationary),
        "stationary_gate_ranges": runs(np.isin(np.arange(n), stationary), a, b),
        "raw_confidence_quantiles": np.quantile(conf[a : b + 1][raw[a : b + 1]], [0, 0.1, 0.5, 0.9, 1]).tolist()
        if raw[a : b + 1].any()
        else None,
    }
    if c["matching_status"] == "matched":
        for name, col in [("start", "pred_start_frame"), ("end", "pred_end_frame")]:
            k = int(c[col])
            row[name + "_context"] = [
                {
                    "frame": j,
                    "raw_xy": f[j]["s"],
                    "raw_conf": f[j]["c"],
                    "stabilized_xy": coords[j].tolist() if raw[j] else None,
                    "observed": bool(observed[j]),
                    "interpolated": bool(track.interp[j]),
                    "speed_px_per_frame": None if not np.isfinite(speed[j]) else float(speed[j]),
                    "view": f[j]["v"],
                    "calibration": f[j]["cs"],
                }
                for j in range(max(0, k - 15), min(n, k + 21))
            ]
    by_rally.append(row)
phase = []
for pos in range(60):
    idx = np.array([i for i in range(n) if chunk_positions[i] == pos and gtmask[i] and usable[i]])
    phase.append(
        {
            "chunk_position": pos,
            "samples": len(idx),
            "observed_fraction": float(raw[idx].mean()),
            "confidence_mean_detected": float(conf[idx][raw[idx]].mean()) if raw[idx].any() else None,
        }
    )
result = {
    "scope": (
        "Cached raw model detections; global postprocessing diagnostic approximates engine windows "
        "and is NOT a full production semantic replay."
    ),
    "cache_frames": n,
    "chunks": len(chunks),
    "chunk_lengths": dict(zip(*np.unique([b - a + 1 for a, b in chunks], return_counts=True), strict=True)),
    "raw_observed_count": int(raw.sum()),
    "usable_geometry_count": int(usable.sum()),
    "postfilter_observed_count": int(observed.sum()),
    "interpolated_count": int(track.interp.sum()),
    "raw_missing_runs_ge10_count": len([r for r in runs(~raw, 0, n - 1) if r[2] >= 10]),
    "phase_by_chunk_position_inside_gt": phase,
    "rallies": by_rally,
    "known_limitations": [
        "No heatmaps or subthreshold peaks are cached; zero confidence on a missing detection is a serialization "
        "convention, not the true heatmap maximum.",
        "Geometry/coordinate context reconstructed from cached frame metadata; exact engine identity/format "
        "resets and bounded window effects require semantic replay.",
        "Raw observations are model outputs, not independently labeled shuttle positions. "
        "No shuttle localization precision/recall is claimed.",
    ],
}
# Convert NumPy scalar keys/values in histogram.
result["chunk_lengths"] = {str(k): int(v) for k, v in result["chunk_lengths"].items()}
(OUT / "observation_audit.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
for r in by_rally:
    if r["gt_rally"] in selected:
        print(
            r["gt_rally"],
            r["raw_observed_fraction"],
            r["postfilter_observed_fraction"],
            r["interpolated_frames"],
            "missing10",
            r["postfilter_missing_runs_ge10"],
            "stationary",
            r["stationary_gate_frames_count"],
        )
print({k: v for k, v in result.items() if k not in ("rallies", "phase_by_chunk_position_inside_gt")})
