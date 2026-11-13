"""Read-only cached weak-acquisition design study; no detector/model execution."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import time

import msgpack
import numpy as np

from bai_badminton.court import Homography
from bai_badminton.perception.players import CourtROI, _box_iou

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
EVAL = ROOT / "evaluation/ground_truth_validation"
PREFIX = EVAL / "component_evaluations/pre_test03_scene_foreground_v1/prefix_v2"
inputs = {}


def sha(path):
    return hashlib.file_digest(Path(path).open("rb"), "sha256").hexdigest()


def bind(path):
    path = Path(path).resolve()
    inputs[str(path)] = sha(path)
    return path


def read(path):
    return json.loads(bind(path).read_text())


def intersect(a, b):
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


def weak_cohort(raw):
    reliable = raw.get("background_features", 0) >= 6 and (raw.get("background_consistent_fraction") or 0) >= .5
    eligible = [r for r in raw["regions"] if r["features"] >= 6 and r.get("discontinuity") is not None
                and r.get("adaptive_ratio") is not None and r["adaptive_ratio"] >= 3.0]
    independent = [r for r in eligible if not any(intersect(r["region"]["bbox"], s["region"]["bbox"])
                                              for s in eligible if s is not r)]
    return reliable, independent


def full_positive(previous, current):
    if not len(previous) or not len(current):
        return False, []
    overlap = _box_iou(np.asarray(previous), np.asarray(current)) >= .3
    pairs = [list(map(int, x)) for x in zip(*np.nonzero(overlap), strict=True)]
    positive = len(pairs) == len(previous) and (overlap.sum(0) <= 1).all() and (overlap.sum(1) == 1).all()
    return bool(positive), pairs


def load_geometry(test, a, z):
    run = ROOT.parent / f"ground-truth-validation-artifacts-20261110/test_{test:02d}/improved_v1/run"
    events = [json.loads(x) for x in bind(run / "events.jsonl").read_text().splitlines()]
    H = np.asarray(next(e["payload"]["H"] for e in events if e["type"] == "calibration"))
    format_events = [e for e in events if e["type"] == "format_decision"]
    info = read(run / "inference.json")
    raw = {}
    for item in read(run / "perception_completion_catalog.json")["files"]:
        if item["start"] <= z and item["end"] >= a:
            p = bind(run / item["path"])
            assert inputs[str(p)] == item["sha256"]
            chunk = msgpack.unpackb(p.read_bytes(), raw=False)
            raw.update({r["f"]: r for r in chunk["frames"] if a <= r["f"] <= z})
    return run, H, format_events, info, raw


def inspect_frame(test, key, row, det, H, fmt, frame):
    raw = row["raw_content"]
    reliable, cohort = weak_cohort(raw)
    current_format = next((e for e in reversed(fmt) if e["frame_start"] <= frame and e["payload"]["known"]), None)
    expected = {"singles": 2, "doubles": 4}.get(current_format["payload"]["match_format"]) if current_format else None
    previous = [x["region"]["bbox"] for x in raw["regions"]]
    result = {"test": test, "case": key, "frame": frame, "seconds": frame / 30,
              "weak_ratio_cohort": reliable and len(cohort) >= 2, "weak_region_keys": [x["region"]["key"] for x in cohort],
              "raw_hypothesis": raw["hypothesis"], "recorded_barrier": row["barrier"],
              "background_reliable": reliable, "expected_population": expected,
              "format_source": current_format, "raw_regions": raw["regions"],
              "full_raw_available": det is not None, "existing_absolute_floor_unchanged": 15.0,
              "raw_discontinuity": raw.get("discontinuity"), "hard_camera_cut": row["hard_camera_cut"],
              "current_layout_status": "unavailable_retained_raw_proposals", "production_action": "none_shadow_only"}
    if det is None or H is None:
        return result
    h = Homography(np.asarray(H[1]).reshape(3, 3) @ H[0], 0.0, 4)
    world = np.asarray([[-3.05, 6.7], [3.05, 6.7], [3.05, -6.7], [-3.05, -6.7]])
    roi = CourtROI(h.court_to_image(world).astype(np.float32), homography=h)
    crop = roi.crop_box(1280, 720)
    x0, y0, _, _ = crop
    current = np.asarray(det["boxes_crop"], float).reshape(-1, 4) + [x0, y0, x0, y0]
    strict = [i for i, box in enumerate(current) if roi.contains_feet(box, allow_runoff=False)]
    xy = h.image_to_court(np.asarray([[(box[0] + box[2]) / 2, box[3]] for box in current])) if len(current) else []
    selected = current[strict]
    veto, pairs = full_positive(previous, current)
    overlap = _box_iou(np.asarray(previous).reshape(-1, 4), selected) if previous and len(selected) else np.empty((len(previous), len(selected)))
    no_correspondence = bool(previous and len(selected) and not (overlap >= .3).any())
    literal_disjoint = bool(previous and len(selected) and not any(intersect(a, b) for a in previous for b in selected))
    distinct = len({tuple(b) for b in selected}) == len(selected)
    mutual_disjoint = not any(intersect(a, b) for i, a in enumerate(selected) for j, b in enumerate(selected) if i < j)
    side_counts = [sum(xy[i][1] < 0 for i in strict), sum(xy[i][1] >= 0 for i in strict)]
    complete = expected is not None and len(strict) == expected and distinct
    base = result["weak_ratio_cohort"] and not raw["hypothesis"] and complete and not veto
    result.update(current_layout_status="retained_current_raw_proposals", detector_crop=list(crop),
                  detector_crop_sha256=det["crop_pixels_sha256"], current_raw_boxes=current.tolist(), current_raw_scores=det["scores"],
                  strict_court_indices=strict, strict_court_side_counts=side_counts, distinct_strict_boxes=distinct,
                  strict_current_mutually_disjoint=mutual_disjoint, full_raw_positive_complete_veto=veto,
                  full_raw_correspondence_pairs=pairs, previous_to_strict_iou=overlap.tolist(),
                  no_point3_correspondence=no_correspondence, literal_previous_current_disjoint=literal_disjoint,
                  root_design_point3_shadow=bool(base and no_correspondence),
                  root_design_literal_shadow=bool(base and literal_disjoint),
                  optional_balanced_side_diagnostic=expected is not None and side_counts == [expected // 2] * 2,
                  geometry_scope="Original frozen source schedule/calibration with strict CourtROI, never inherited admission authority.")
    return result


if __name__ == "__main__":
    assert ROOT.name == "Sports_Analytics" and not (OUT / "summary.json").exists()
    started = time.time()
    bind(__file__)
    artifact = read(PREFIX / "artifact_receipt.json")
    records, cases = [], []
    for path in sorted(PREFIX.glob("test*.json")):
        assert sha(path) == artifact["artifact_sha256"][path.name]
        data = read(path)
        test, (a, z) = data["test"], data["range"]
        _, H, formats, info, source = load_geometry(test, a, z)
        assert info["source_sha256"] == data["source_sha256"] and info["proxy_sha256"] == data["proxy_sha256"]
        detector = {}
        for d in data["detector_inputs"]:
            assert d["frame"] not in detector
            detector[d["frame"]] = d
        rows = data["variants"]["foreground"]
        per_case = []
        for r in rows:
            f = r["frame"]
            record = inspect_frame(test, path.stem, r, detector.get(f), (H, source[f]["g"]) if source[f].get("g") is not None else None, formats, f)
            record.update(source_pixels_sha256=r["source_pixels_sha256"], source_sha256=data["source_sha256"], proxy_sha256=data["proxy_sha256"])
            records.append(record)
            per_case.append(record)
        cases.append({"case": path.stem, "test": test, "range": [a, z], "frames": len(rows),
                      "weak_ratio_cohort_frames": [r["frame"] for r in per_case if r["weak_ratio_cohort"]],
                      "weak_missing_proposals": [r["frame"] for r in per_case if r["weak_ratio_cohort"] and not r["full_raw_available"]],
                      "point3_shadow_candidates": [r["frame"] for r in per_case if r.get("root_design_point3_shadow")],
                      "literal_shadow_candidates": [r["frame"] for r in per_case if r.get("root_design_literal_shadow")],
                      "original_foreground_barriers": [r["frame"] for r in per_case if r["recorded_barrier"]]})
    with (OUT / "all_frame_design_records.jsonl").open("x") as f:
        for record in records:
            f.write(json.dumps(record, allow_nan=False) + "\n")
    summary = {"schema": "cached-source-weak-acquisition-shadow:v1", "scope": "No new neural inference, production or evaluator edits; no threshold lowering; incomplete candidate availability remains unknown.",
               "cases": cases, "frames": len(records), "elapsed_s": time.time() - started, "input_sha256": inputs}
    for p, digest in inputs.items():
        assert sha(p) == digest
    with (OUT / "summary.json").open("x") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps({k: v for k, v in summary.items() if k != "input_sha256"}), flush=True)
