"""Diagnostic-only study of anatomical aliases and straight-shaft evidence.

No production thresholds, classes, predictions, annotations or pipeline are
changed. Synthetic controls are engineering tests, not sporting accuracy GT.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import av
import cv2
import msgpack
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from probe_racket_candidates import ROOT, digest, people, render_crop, traced_detect  # noqa: E402

from bai_badminton.perception_types import PersonObs  # noqa: E402


def face_alias(candidate, persons):
    angle = np.deg2rad(candidate["angle"])
    rotation = np.array([[np.cos(angle), np.sin(angle)], [-np.sin(angle), np.cos(angle)]])
    matches = []
    for person in persons:
        contained = []
        if person.kps is None or person.detector_matched is not True:
            continue
        for index in range(5):
            point = person.kps[index]
            if np.isfinite(point).all() and point[2] >= 0.5:
                radial = np.linalg.norm(
                    rotation @ (point[:2] - candidate["center"]) / (np.asarray(candidate["axes"]) / 2)
                )
                if radial <= 1:
                    contained.append(index)
        if len(contained) >= 3:
            matches.append({"person_track_id": person.track_id, "contained_face_joint_indices": contained})
    return matches


def shaft_geometry(image, candidate):
    x0, y0, x1, y1 = candidate["crop_xyxy"]
    gray = cv2.cvtColor(image[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 45, 130)
    rim = np.asarray(candidate["rim_xy"]) - [x0, y0]
    wrist = np.asarray(candidate["wrist_xy"]) - [x0, y0]
    vector = wrist - rim
    gap = float(np.linalg.norm(vector))
    direction = vector / gap
    lines = cv2.HoughLinesP(
        edges, 1, np.pi / 180, max(5, round(gap * 0.15)), minLineLength=max(5, round(gap * 0.25)), maxLineGap=3
    )
    aligned = []
    for line in [] if lines is None else np.asarray(lines).reshape(-1, 4):
        a, b = line[:2].astype(float), line[2:].astype(float)
        delta = b - a
        length = np.linalg.norm(delta)
        cosine = abs(float(delta @ direction / length)) if length else 0
        angle = float(np.degrees(np.arccos(np.clip(cosine, 0, 1))))
        # Report candidate segments spanning the current detector's +/-2.5px corridor.
        normal = np.array([-direction[1], direction[0]])
        lateral = max(abs(float((a - rim) @ normal)), abs(float((b - rim) @ normal)))
        if lateral <= max(2.5, candidate["body_height"] * 0.04):
            start, end = sorted((float((a - rim) @ direction), float((b - rim) @ direction)))
            overlap = max(0, min(gap, end) - max(0, start))
            aligned.append(
                {
                    "angle_degrees": angle,
                    "overlap_fraction": overlap / gap,
                    "lateral_px": lateral,
                    "xyxy": [*np.add(a, (x0, y0)).tolist(), *np.add(b, (x0, y0)).tolist()],
                }
            )
    widths = {
        "fixed_2_5px": 2.5,
        "body_1pct": candidate["body_height"] * 0.01,
        "body_2pct": candidate["body_height"] * 0.02,
        "body_4pct": candidate["body_height"] * 0.04,
    }
    grid = {
        name: {
            str(angle): max(
                (x["overlap_fraction"] for x in aligned if x["angle_degrees"] <= angle and x["lateral_px"] <= width),
                default=0,
            )
            for angle in (10, 20, 30)
        }
        for name, width in widths.items()
    }
    return {
        "gap_px": gap,
        "best_corridor_line_overlap_at_angle_10": grid["fixed_2_5px"]["10"],
        "best_corridor_line_overlap_at_angle_20": grid["fixed_2_5px"]["20"],
        "best_corridor_line_overlap_at_angle_30": grid["fixed_2_5px"]["30"],
        "corridor_angle_sensitivity_grid": grid,
        "corridor_segments": aligned,
        "classification": "exploratory geometric diagnostic only; no production admission threshold selected",
    }


def scene(scale=1, angle=0, *, blur=False, occlusion=0, face="away", transverse=False):
    image = np.zeros((400, 400, 3), np.uint8)
    center, wrist = (200, 120), (200, 205)
    cv2.ellipse(image, center, (22, 32), 0, 0, 360, (240, 240, 240), 2)
    if transverse:
        for y in range(154, 204, 6):
            cv2.line(image, (196, y), (204, y), (230, 230, 230), 1)
    else:
        cv2.line(image, (200, 151), wrist, (230, 230, 230), 2)
    if occlusion:
        cv2.rectangle(image, (194, 175 - occlusion // 2), (206, 175 + occlusion // 2), (0, 0, 0), -1)
    if blur:
        image = cv2.GaussianBlur(image, (3, 3), 0.8)
    kps = np.zeros((17, 3), float)
    kps[9] = [*wrist, 0.95]
    face_center = {"away": (120, 220), "near_overhead": (200, 175), "overlap": center}[face]
    for index, offset in enumerate(((0, 0), (-4, -3), (4, -3), (-9, 0), (9, 0))):
        kps[index] = [face_center[0] + offset[0], face_center[1] + offset[1], 0.9]
    matrix = cv2.getRotationMatrix2D((200, 200), angle, scale)
    matrix[:, 2] += (400 * scale - 400) / 2
    image = cv2.warpAffine(image, matrix, (400 * scale, 400 * scale))
    kps[:, :2] = np.column_stack((kps[:, :2], np.ones(17))) @ matrix.T
    person = PersonObs(7, np.array([150, 180, 250, 380], float) * scale, 0.95, kps=kps, detector_matched=True)
    return image, person


def summarize(image, persons, trace):
    results = []
    for candidate in trace["accepted_proposals"]:
        results.append(
            {
                "track_id": candidate["track_id"],
                "wrist": candidate["wrist"],
                "center": candidate["center"],
                "support": candidate["uncalibrated_support"],
                "selected_by_current": candidate["selected"],
                "face_aliases": face_alias(candidate, persons),
                "shaft_geometry": shaft_geometry(image, candidate),
            }
        )
    return results


def main():
    output = HERE / "contract_study_v4"
    output.mkdir(exist_ok=False)
    (output / "executed_study.py").write_bytes(Path(__file__).read_bytes())
    (output / "executed_probe.py").write_bytes((HERE / "probe_racket_candidates.py").read_bytes())
    result = {
        "classification": "diagnostic component experiment only, not a pipeline fix or physical precision/recall",
        "real_frames": {},
        "test1_control_frames": {},
        "synthetic_controls": {},
    }
    inputs = {
        str(Path(__file__)): digest(__file__),
        str(HERE / "probe_racket_candidates.py"): digest(HERE / "probe_racket_candidates.py"),
    }
    proxy = (
        ROOT
        / "evaluation/ground_truth_validation/test_02/baseline_v1/run/data/media"
        / "4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a/proxy.mp4"
    )
    with av.open(str(proxy)) as container:
        container.streams.video[0].thread_count = 2
        for index, frame in enumerate(container.decode(video=0)):
            if index in (300, 1594):
                image = frame.to_ndarray(format="bgr24")
                cached = json.loads(
                    (HERE.parent / f"component_visual_review/frame_{index:05d}/current_cache_frame.json").read_text()
                )
                persons = people(cached)
                trace = traced_detect(image, persons)
                result["real_frames"][str(index)] = summarize(image, persons, trace)
            if index >= 1594:
                break
    inputs[str(proxy)] = digest(proxy)
    test1_run = ROOT / "evaluation/ground_truth_validation/test_01/improved_v1/run"
    test1_proxy = next((test1_run / "data/media").glob("*/proxy.mp4"))
    sid = json.loads((test1_run / "session.json").read_text())["session_id"]
    cached_test1 = {}
    for cache_path in sorted((test1_run / "data/sessions" / sid / "perception").glob("*.msgpack")):
        chunk = msgpack.unpackb(cache_path.read_bytes(), raw=False)
        for frame in chunk["frames"]:
            if frame["f"] in (243, 300, 9000):
                cached_test1[frame["f"]] = frame
                inputs[str(cache_path)] = digest(cache_path)
    with av.open(str(test1_proxy)) as container:
        container.streams.video[0].thread_count = 2
        for index, frame in enumerate(container.decode(video=0)):
            if index in cached_test1:
                image = frame.to_ndarray(format="bgr24")
                persons = people(cached_test1[index])
                trace = traced_detect(image, persons)
                result["test1_control_frames"][str(index)] = summarize(image, persons, trace)
                for candidate in trace["accepted_proposals"]:
                    if candidate["selected"]:
                        render_crop(
                            image,
                            candidate,
                            output
                            / f"test1_frame{index:05d}_track{candidate['track_id']}_wrist{candidate['wrist']}.png",
                        )
            if index >= 9000:
                break
    inputs[str(test1_proxy)] = digest(test1_proxy)
    controls = [
        (f"racket_scale{s}_angle{a}_blur{b}", dict(scale=s, angle=a, blur=b))
        for s in (1, 2)
        for a in (0, 35, 75)
        for b in (False, True)
    ]
    controls += [
        ("racket_short_occlusion", dict(occlusion=6)),
        ("racket_long_occlusion", dict(occlusion=24)),
        ("racket_near_head_without_overlap", dict(face="near_overhead")),
        ("head_ellipse_connected_to_arm", dict(face="overlap")),
        ("racket_directly_overlapping_face_ambiguous", dict(face="overlap")),
        ("ellipse_with_unconnected_transverse_clutter", dict(transverse=True)),
    ]
    for name, params in controls:
        image, person = scene(**params)
        trace = traced_detect(image, [person])
        result["synthetic_controls"][name] = {
            "parameters": params,
            "selected": trace["selected"],
            "candidates": summarize(image, [person], trace),
        }
        cv2.imwrite(str(output / (name + ".png")), image)
    # A second person's face inside an owned candidate is also ambiguous in doubles.
    image, owner = scene(face="away")
    _, other = scene(face="overlap")
    other.track_id = 8
    other.kps[9:] = 0
    trace = traced_detect(image, [owner, other])
    result["synthetic_controls"]["other_person_face_alias"] = {
        "selected": trace["selected"],
        "candidates": summarize(image, [owner, other], trace),
    }
    result["input_sha256"] = inputs
    if any(digest(path) != expected for path, expected in inputs.items()):
        raise ValueError("Component study input changed")
    (output / "contract_study.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": "completed", "output": str(output), "controls": len(result["synthetic_controls"])}))


if __name__ == "__main__":
    main()
