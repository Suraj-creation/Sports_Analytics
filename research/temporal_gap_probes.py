"""Read-only source-bound probes of retained upper-flight continuity evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from bai_badminton.events.rally_motion import image_exit_return_curve_support, image_exit_return_tracklet_support
from bai_badminton.observations import WindowObs
from bai_badminton.perception.shuttle_post import Track


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    records = []
    for case, bounds, probe in [(39, (13520, 13585), 13550), (55, (20162, 20216), 20185), (69, (27318, 27361), 27335)]:
        path = args.cases / f"gt_{case:03}.json"
        source = json.loads(path.read_text())
        rows = [r for r in source["semantic_trace"] if r["call"] == "step" and bounds[0] <= r["frame"] < bounds[1]]
        if [r["frame"] for r in rows] != list(range(*bounds)):
            raise ValueError("missing source trace frame")
        coordinates = np.array([[np.nan if v is None else v for v in r["processed_xy"]] for r in rows])
        observed = np.array([r["observation"]["kind"] == "observed" for r in rows])
        track = Track.from_arrays(coordinates[:, 0], coordinates[:, 1], observed)
        replay = np.array([r["observation"]["replay"] or not r["observation"]["context_valid"] for r in rows])
        breaks = np.zeros(len(rows), bool)
        for i in range(1, len(rows)):
            breaks[i] = any(
                rows[i]["raw_perception"][k] != rows[i - 1]["raw_perception"][k] for k in ("sh", "ce", "cs", "v")
            )
        window = WindowObs(bounds[0], 30, track, {}, replay=replay, break_before=breaks)

        def image_xy(frame, xy, rows=rows, bounds=bounds):
            matrix = rows[frame - bounds[0]]["raw_perception"]["g"]
            if matrix is None:
                return xy
            value = np.array(matrix).reshape(3, 3) @ np.array([*xy, 1.0])
            return tuple(value[:2] / value[2])

        row = rows[probe - bounds[0]]
        start = row["before"]["start"]
        options = dict(frame_height=720, raw_xy=image_xy, minimum_exit_frame=start + 59 if start is not None else None)
        raw = [r for r in source["raw_perception"] if bounds[0] <= r["f"] < bounds[1]]
        value = {
            "case": case,
            "source_case": str(path.resolve()),
            "source_case_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "source_video_sha256": source["source_sha256"],
            "proxy_sha256": source["proxy_sha256"],
            "bounds_half_open": bounds,
            "probe_frame": probe,
            "qualification_minimum_exit": options["minimum_exit_frame"],
            "original_tracklet_proof": asdict(image_exit_return_tracklet_support(window, probe - bounds[0], **options)),
            "opt_in_curve_proof": asdict(image_exit_return_curve_support(window, probe - bounds[0], **options)),
            "raw_perception": raw,
            "semantic_rows": rows,
            "limits": (
                "Conditional helper diagnostics on actual recorded observations; "
                "not fresh inference, no coordinates altered"
            ),
        }
        (args.output / f"gt_{case:03}.json").write_text(json.dumps(value, indent=2) + "\n")
        records.append(
            {key: value[key] for key in ("case", "probe_frame", "original_tracklet_proof", "opt_in_curve_proof")}
        )
    (args.output / "summary.json").write_text(json.dumps(records, indent=2) + "\n")
    (args.output / "executed_source.py").write_bytes(Path(__file__).read_bytes())
    print(json.dumps(records))


if __name__ == "__main__":
    main()
