"""CPU component probe of frozen images/poses; no neural or pipeline inference.

Traces unmodified RacketDetector's accepted candidates and records why its
geometric gates pass. Source-resized panels and actual proxy pixels are separate.
"""

from __future__ import annotations

import dataclasses
import hashlib
import inspect
import json
import sys
from pathlib import Path

import av
import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT))
from bai_badminton.perception.racket import RacketDetector  # noqa: E402
from bai_badminton.perception_types import PersonObs  # noqa: E402


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def people(frame):
    return [
        PersonObs(p["t"], np.asarray(p["b"], float), p["c"], kps=np.asarray(p["k"], float), detector_matched=p["dm"])
        for p in frame["p"]
    ]


def traced_detect(image, persons):
    source, start = inspect.getsourcelines(RacketDetector.detect)
    capture_line = start + next(i for i, line in enumerate(source) if "proposals.append(" in line)
    accepted = []

    def trace(frame, event, arg):
        if frame.f_code is RacketDetector.detect.__code__ and event == "line" and frame.f_lineno == capture_line:
            value = frame.f_locals
            local, edges, thick = value["local"], value["edges"], value["thick"]
            undilated = edges[local[:, 1], local[:, 0]] > 0
            dilated = thick[local[:, 1], local[:, 0]] > 0
            point = value["point"][:2]
            center = value["center"]
            wrist_vec = point - center
            kps = value["person"].kps
            head = kps[0, :2]
            # These extra quantities are probe diagnostics, not new admission gates.
            accepted.append(
                {
                    "track_id": value["person"].track_id,
                    "wrist": value["wrist"],
                    "center": center.tolist(),
                    "axes": list(value["axes"]),
                    "angle": float(value["angle"]),
                    "body_height": value["body"],
                    "wrist_xy": point.tolist(),
                    "head_joint_xy": head.tolist(),
                    "center_to_head_px": float(np.linalg.norm(center - head)),
                    "center_to_wrist_px": value["length"],
                    "wrist_radius": value["wrist_radius"],
                    "median_fit_error": value["fit_error"],
                    "angular_coverage": value["coverage"],
                    "dilated_shaft_support": value["shaft"],
                    "uncalibrated_support": value["support"],
                    "undilated_sample_support": float(undilated.mean()),
                    "dilated_samples": [bool(v) for v in dilated],
                    "undilated_samples": [bool(v) for v in undilated],
                    "sample_global_xy": value["sample"].tolist(),
                    "contour_point_count": len(value["contour"]),
                    "contour_global_xy": (value["contour"][:, 0] + [value["x0"], value["y0"]]).tolist(),
                    "rim_xy": value["rim"].tolist(),
                    "crop_xyxy": [value["x0"], value["y0"], value["x1"], value["y1"]],
                    "length_body_ratio": float(np.linalg.norm(wrist_vec) / value["body"]),
                }
            )
        return trace

    previous = sys.gettrace()
    sys.settrace(trace)
    try:
        selected = RacketDetector().detect(image, persons)
    finally:
        sys.settrace(previous)
    result = {str(track): dataclasses.asdict(observation) for track, observation in selected.items()}
    for proposal in accepted:
        chosen = result.get(str(proposal["track_id"]))
        proposal["selected"] = (
            chosen is not None
            and proposal["wrist"] == chosen["wrist"]
            and np.allclose(proposal["center"], chosen["center"], atol=1e-8)
        )
    return {"selected": result, "accepted_proposals": accepted}


def render_crop(image, candidate, path):
    center, wrist = np.asarray(candidate["center"]), np.asarray(candidate["wrist_xy"])
    margin = round(candidate["body_height"] * 0.25)
    xmin, ymin = np.minimum(center, wrist).astype(int) - margin
    xmax, ymax = np.maximum(center, wrist).astype(int) + margin
    xmin, ymin, xmax, ymax = max(0, xmin), max(0, ymin), min(image.shape[1], xmax), min(image.shape[0], ymax)
    overlay = image.copy()
    contour = np.asarray(candidate["contour_global_xy"], np.int32)[:, None]
    cv2.polylines(overlay, [contour], True, (0, 255, 0), 1)
    cv2.ellipse(
        overlay,
        tuple(np.round(center).astype(int)),
        tuple(np.round(np.asarray(candidate["axes"]) / 2).astype(int)),
        candidate["angle"],
        0,
        360,
        (0, 0, 255),
        1,
    )
    for sample, support in zip(candidate["sample_global_xy"], candidate["dilated_samples"], strict=True):
        cv2.circle(overlay, tuple(np.round(sample).astype(int)), 2, (0, 255, 255) if support else (0, 0, 255), -1)
    cv2.circle(overlay, tuple(np.round(wrist).astype(int)), 4, (255, 0, 0), -1)
    raw = image[ymin:ymax, xmin:xmax]
    marked = overlay[ymin:ymax, xmin:xmax]
    panels = np.concatenate((raw, marked), axis=1)
    cv2.imwrite(str(path), cv2.resize(panels, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST))


def main():
    output = HERE / "probe_v3"
    output.mkdir(exist_ok=False)
    (output / "executed_probe.py").write_bytes(Path(__file__).read_bytes())
    (output / "executed_production_racket.py").write_bytes(Path(inspect.getsourcefile(RacketDetector)).read_bytes())
    visual = HERE.parent / "component_visual_review"
    proxy = (
        ROOT
        / "evaluation/ground_truth_validation/test_02/baseline_v1/run/data/media"
        / "4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a/proxy.mp4"
    )
    inputs = {
        str(Path(inspect.getsourcefile(RacketDetector))): digest(inspect.getsourcefile(RacketDetector)),
        str(Path(__file__)): digest(__file__),
    }
    result = {
        "classification": (
            "CPU image detector component probes with frozen pose inputs, "
            "not fresh pipeline/neural evaluation or human ground truth"
        ),
        "probe_inference": "classical CPU RacketDetector only",
        "pipeline_modified": False,
        "frames": {},
    }
    proxy_images = {}
    with av.open(str(proxy)) as container:
        container.streams.video[0].thread_count = 2
        for index, frame in enumerate(container.decode(video=0)):
            if index in (300, 1594):
                proxy_images[index] = frame.to_ndarray(format="bgr24")
            if index >= 1594:
                break
    inputs[str(proxy)] = digest(proxy)
    for index in (300, 1594):
        frame_dir = visual / f"frame_{index:05d}"
        cache = frame_dir / "current_cache_frame.json"
        raw_path = frame_dir / "exact_source_resized.png"
        frame = json.loads(cache.read_text())
        inputs.update({str(cache): digest(cache), str(raw_path): digest(raw_path)})
        entries = {}
        for label, image in (
            ("original_source_resized", cv2.imread(str(raw_path))),
            ("analysis_proxy", proxy_images[index]),
        ):
            entries[label] = traced_detect(image, people(frame))
            entries[label]["pixels_sha256"] = hashlib.sha256(image.tobytes()).hexdigest()
            entries[label]["cache_observation_matches"] = {
                str(p["t"]): bool(
                    entries[label]["selected"].get(str(p["t"])) is not None
                    and np.allclose(entries[label]["selected"][str(p["t"])]["center"], p["rk"]["center"], atol=1e-8)
                )
                for p in frame["p"]
                if p.get("rk") is not None
            }
            for candidate in entries[label]["accepted_proposals"]:
                if candidate["selected"]:
                    render_crop(
                        image,
                        candidate,
                        output
                        / f"test2_frame{index:05d}_{label}_track{candidate['track_id']}_wrist{candidate['wrist']}.png",
                    )
        result["frames"][str(index)] = entries
    result["input_sha256"] = inputs
    if any(digest(path) != value for path, value in inputs.items()):
        raise ValueError("Diagnostic input changed during component probe")
    (output / "probe_results.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "status": "completed",
                "output": str(output),
                "frames": {
                    f: {
                        kind: {"selected": entry["selected"], "cache_matches": entry["cache_observation_matches"]}
                        for kind, entry in rows.items()
                    }
                    for f, rows in result["frames"].items()
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
