"""Annotation-free curve diagnostics for recorded missing-observation runs.

No candidate is accepted and no prediction is generated. A pixel-space
quadratic is not a physical 3D shuttle trajectory. Fits use observed points
only, with the existing five-frame anchor and two-second diagnostic horizon.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import msgpack
import numpy as np


def fit(points, left, right):
    frames = np.asarray([p[0] for p in points], dtype=float)
    center = (left + right) / 2
    t = frames - center
    xy = np.asarray([p[1:] for p in points], dtype=float)
    xfit = np.polyfit(t, xy[:, 0], 1)
    yfit = np.polyfit(t, xy[:, 1], 2)
    predicted = np.column_stack([np.polyval(xfit, t), np.polyval(yfit, t)])
    residual = np.linalg.norm(predicted - xy, axis=1)
    apex_t = -yfit[1] / (2 * yfit[0]) if yfit[0] > 0 else None
    apex_frame = apex_t + center if apex_t is not None else None
    return {
        "origin_frame": center,
        "x_linear_coefficients": xfit.tolist(),
        "y_quadratic_coefficients": yfit.tolist(),
        "residual_rmse_px": float(np.sqrt(np.mean(residual**2))),
        "residual_max_px": float(residual.max()),
        "apex_frame": apex_frame,
        "apex_y": float(np.polyval(yfit, apex_t)) if apex_t is not None else None,
        "apex_in_gap": bool(apex_frame is not None and left < apex_frame < right),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    traces = [json.loads(line) for line in args.trace.open()]
    steps = {row["frame"]: row for row in traces if row["call"] == "step"}
    cuts = {row["frame"] for row in traces if row["call"] == "discontinuity"}
    chunks = []
    for path in args.run.glob("runtime/sessions/*/perception/*.msgpack"):
        value = msgpack.unpackb(path.read_bytes(), raw=False)
        chunks.append((value["start"], value["end"]))
    chunks.sort()
    frame_count = len(steps)
    assert set(steps) == set(range(frame_count))
    results = []
    first = 0
    while first < frame_count:
        if steps[first]["visible"]:
            first += 1
            continue
        end = first + 1
        while end < frame_count and not steps[end]["visible"]:
            end += 1
        if 10 <= end - first <= 60 and not any(
            frame in cuts for frame in range(max(0, first - 5), min(frame_count, end + 5))
        ):
            before = [(f, steps[f]["x"], steps[f]["y"]) for f in range(max(0, first - 5), first) if steps[f]["visible"]]
            after = [
                (f, steps[f]["x"], steps[f]["y"]) for f in range(end, min(frame_count, end + 5)) if steps[f]["visible"]
            ]
            if len(before) >= 2 and len(after) >= 2:
                points = before + after
                curve = fit(points, first - 1, end)
                frontier = next((hi for _, hi in chunks if hi - 40 >= first), chunks[-1][1])
                loo = [fit(points[:i] + points[i + 1 :], first - 1, end) for i in range(len(points))]
                apexes = [entry["apex_y"] for entry in loo if entry["apex_y"] is not None]
                results.append(
                    {
                        "missing_span_half_open": [first, end],
                        "observed_points": points,
                        "fit": curve,
                        "leave_one_out_apex_y_range": [min(apexes), max(apexes)] if apexes else None,
                        "available_frontier_at_first_missing_sample": frontier,
                        "all_used_points_available_at_first_sample": after[-1][0] <= frontier,
                        "limits": (
                            "Pixel-space fit and leave-one-out sensitivity, "
                            "not calibrated uncertainty or physical visibility labels"
                        ),
                    }
                )
        first = end
    (args.output / "curves.json").write_text(json.dumps(results, indent=2, allow_nan=False) + "\n")
    manifest = {
        "mode": "annotation-free recorded-evidence curve diagnostics; no fresh inference or changed predictions",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "trace_sha256": hashlib.sha256(args.trace.read_bytes()).hexdigest(),
        "anchor_frames": 5,
        "diagnostic_missing_duration_frames": [10, 60],
        "latency_scope": "first source cache chunk whose normal 40-frame frontier reaches the missing frame",
        "limits": [
            "Per-frame final trace snapshots can differ from future samples of an earlier window",
            "Pixel-space parabola is not a physical 3D trajectory",
            "No thresholds adopted from these fits",
        ],
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    for result in results:
        if 14640 <= result["missing_span_half_open"][0] <= 14700:
            print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
