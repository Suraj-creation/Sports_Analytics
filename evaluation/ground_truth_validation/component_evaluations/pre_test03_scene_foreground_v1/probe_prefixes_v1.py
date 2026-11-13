"""Chronological exact-pixel component controls; not a full-pipeline benchmark.

Original dacc05e, frozen c7cf871, and current scene-only candidate run independently
against shared source/crop-bound detector proposals. No GT is passed to a worker.
Run only after root freezes candidate and explicitly authorizes GPU launch.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import importlib.metadata
import importlib.util
import json
import subprocess
import sys

# Read-only Git argument arrays; paths are local candidate/workspace roots.
# ruff: noqa: S603
from dataclasses import asdict
from pathlib import Path

import av
import cv2
import msgpack
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = ROOT.parent / "ground-truth-validation-artifacts-20261110"
FRESH = ROOT.parent / "ground-truth-validation-artifacts-20261111/pre_test03_v1/test_01"
OLD_PROBES = HERE.parent / "pre_test03_perception_v1"
CASES = {
    1: ("test_01/improved_v1", [(0, 80), (235, 310), (7650, 8150), (9000, 9060)]),
    2: (
        "test_02/improved_v1",
        [(300, 365), (5505, 6510), (7640, 7740), (11300, 11360), (23570, 23680), (25206, 25540)],
    ),
}
FOCUS = {
    1: {
        0,
        1,
        2,
        243,
        300,
        7770,
        7800,
        7801,
        7854,
        7856,
        7857,
        7858,
        7859,
        7860,
        8056,
        8086,
        8087,
        8105,
        8106,
        8107,
        8108,
        9000,
    },
    2: {
        300,
        354,
        355,
        356,
        5956,
        5957,
        5958,
        5960,
        6306,
        6307,
        6486,
        6492,
        6493,
        7702,
        7703,
        7704,
        11345,
        11346,
        11347,
        11348,
        23638,
        23639,
        23640,
        25518,
        25519,
        25520,
        25521,
        25524,
    },
}
SCOPE = (
    "Bounded RFDETR/ROI/ByteTrack/content controls with frozen original rate/geometry schedule; "
    "no pose, shuttle, engine/FSM feedback, full inference, independent physical accuracy or new ground truth."
)


def sha(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    with Path(path).open("x") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write("\n")


def module_at(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class SharedDetector:
    def __init__(self, detector):
        self.detector = detector
        self.cache = {}
        self.frame = None
        self.last_diagnostic = None
        self.fresh_calls = 0
        self.reused_calls = 0
        self.seeded_keys = set()
        self.seed_lookups = 0
        self.same_run_lookups = 0

    def __call__(self, image):
        key = self.frame, hashlib.sha256(image.tobytes()).hexdigest()
        if key not in self.cache:
            boxes, scores = self.detector(image)
            self.cache[key] = boxes.copy(), scores.copy(), copy.deepcopy(self.detector.last_diagnostic)
            self.fresh_calls += 1
        else:
            self.reused_calls += 1
            if key in self.seeded_keys:
                self.seed_lookups += 1
            else:
                self.same_run_lookups += 1
        boxes, scores, self.last_diagnostic = self.cache[key]
        return boxes.copy(), scores.copy()

    def seed(self, item):
        key = item["frame"], item["crop_pixels_sha256"]
        value = (
            np.asarray(item["boxes_crop"], float).reshape(-1, 4),
            np.asarray(item["scores"], float),
            item["diagnostics"],
        )
        if key in self.cache:
            old = self.cache[key]
            if not np.array_equal(old[0], value[0]) or not np.array_equal(old[1], value[1]):
                raise ValueError("Conflicting retained detector proposals for exact source crop")
        self.cache[key] = value
        self.seeded_keys.add(key)


def detector_ast(path):
    tree = ast.parse(Path(path).read_text())
    return {
        node.name: ast.dump(node, include_attributes=False)
        for node in tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef))
        and node.name in {"PlayerDetector", "_nms", "_swap_session"}
    }


def body(person):
    return {
        "track": person.track_id,
        "raw_track": person.raw_track_id,
        "bbox": person.bbox.tolist(),
        "confidence": person.conf,
        "detector_matched": person.detector_matched,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pipeline-root", type=Path, default=ROOT.parent / "test03-scene-continuity-20261112")
    parser.add_argument("--output", type=Path, default=HERE / "prefix_v1")
    parser.add_argument("--test", type=int, choices=[1, 2], action="append")
    parser.add_argument("--seed-prefix", type=Path, action="append", default=[])
    args = parser.parse_args()
    candidate = args.pipeline_root.resolve()
    out = args.output.resolve()
    if out.exists():
        raise FileExistsError(f"New output required: {out}")
    if not out.is_relative_to(HERE.resolve()):
        raise ValueError("Prefix output must stay in NEW diagnostic workspace")
    from bai_badminton.court import Homography
    from bai_badminton.perception import players
    from bai_badminton.perception.content import ContentContinuityProviderV2
    from bai_badminton.perception.scene_change import ForegroundRegion

    if not Path(players.__file__).resolve().is_relative_to(candidate):
        raise RuntimeError("Candidate-native imports required")
    if not hasattr(players.PlayerPerception, "foreground_regions"):
        raise RuntimeError("Candidate foreground API unavailable")
    cv2.setNumThreads(1)
    inputs = {str(Path(__file__).resolve()): sha(__file__)}
    # Whole candidate implementation/config captured before import-driven probes.
    listing = subprocess.check_output(["/usr/bin/git", "-C", str(candidate), "ls-files"], text=True).splitlines()
    for relative in listing:
        path = candidate / relative
        if (
            path.is_file()
            and path.suffix in {".py", ".yaml", ".toml", ".json"}
            and relative.startswith(("engine/", "sports/badminton/src/", "agents/src/", "apps/api/src/"))
        ):
            inputs[str(path)] = sha(path)
    for relative in ["sports/badminton/src/bai_badminton/perception/foreground.py"]:
        path = candidate / relative
        inputs[str(path)] = sha(path)
    commit = subprocess.check_output(["/usr/bin/git", "-C", str(candidate), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["/usr/bin/git", "-C", str(candidate), "diff", "--binary", "HEAD"], text=True)
    status = subprocess.check_output(["/usr/bin/git", "-C", str(candidate), "status", "--porcelain"], text=True)
    model = ROOT / "models/cache/rfdetr_small/rfdetr_s_v142_512x512.onnx"
    if sha(model) != "fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e":
        raise ValueError("Unexpected RFDETR checkpoint")
    inputs[str(model)] = sha(model)
    completed_seeds = []
    for supplied in args.seed_prefix:
        prefix = supplied.resolve()
        if not prefix.is_relative_to(HERE.resolve()) or prefix == out:
            raise ValueError("Seed must be a different completed diagnostic prefix")
        receipt_path = prefix / "artifact_receipt.json"
        receipt = read(receipt_path)
        if receipt["status"] != "preserved_closed_bounded_probe_artifacts":
            raise ValueError("Uncompleted prefix seed")
        inputs[str(receipt_path)] = sha(receipt_path)
        summary_path = prefix / "summary.json"
        if sha(summary_path) != receipt["artifact_sha256"]["summary.json"]:
            raise ValueError("Completed seed summary changed")
        prior_summary = read(summary_path)
        inputs[str(summary_path)] = sha(summary_path)
        if (
            prior_summary["status"] != "completed_bounded_scene_foreground_probe"
            or prior_summary["input_sha256"].get(str(model)) != inputs[str(model)]
        ):
            raise ValueError("Seed checkpoint/completion identity mismatch")
        old_detector_source = (
            prefix / "executed_candidate_commit/sports/badminton/src/bai_badminton/perception/players.py"
        )
        if sha(old_detector_source) != receipt["artifact_sha256"][str(old_detector_source.relative_to(prefix))]:
            raise ValueError("Seed executed detector source changed")
        inputs[str(old_detector_source)] = sha(old_detector_source)
        if detector_ast(old_detector_source) != detector_ast(Path(players.__file__)):
            raise ValueError("Seed neural decoder/preprocessing differs from current detector")
        completed_seeds.append((prefix, receipt))
    out.mkdir()
    (out / "candidate.diff").write_text(dirty)
    (out / "candidate_status.txt").write_text(status)
    snapshots = out / "executed_control_sources"
    snapshots.mkdir()
    frozen = FRESH / "protocol/executed_source/sports/badminton/src/bai_badminton/perception"
    original = ROOT / "sports/badminton/src/bai_badminton/perception"
    controls = {}
    for label, source in [("original", original), ("c7", frozen)]:
        controls[label] = {}
        for name in ["players.py", "content.py"]:
            path = source / name
            inputs[str(path)] = sha(path)
            revision = "dacc05e" if label == "original" else "c7cf871"
            expected = subprocess.check_output(
                [
                    "/usr/bin/git",
                    "-C",
                    str(candidate),
                    "show",
                    f"{revision}:sports/badminton/src/bai_badminton/perception/{name}",
                ]
            )
            if hashlib.sha256(expected).hexdigest() != inputs[str(path)]:
                raise ValueError("Control snapshot differs from exact historical implementation")
            copied = snapshots / f"{label}_{name}"
            copied.write_bytes(path.read_bytes())
            controls[label][name[:-3]] = module_at(f"bai_badminton.perception._prefix_{label}_{name[:-3]}", copied)
    save(
        out / "input_manifest_at_start.json",
        {"candidate_root": str(candidate), "candidate_commit": commit, "input_sha256": inputs, "scope": SCOPE},
    )
    detector = players.PlayerDetector(
        model, (512, 512), [("CUDAExecutionProvider", {"device_id": 0}), "CPUExecutionProvider"], score_thr=0.35
    )
    detector.set_diagnostics(True, 8)
    summaries = []
    for test in args.test or [1, 2]:
        relative, windows = CASES[test]
        run = BASE / relative / "run"
        info = read(run / "inference.json")
        inputs[str(run / "inference.json")] = sha(run / "inference.json")
        expected_frames = {1: 17268, 2: 29296}[test]
        if (
            info["status"] != "completed"
            or info["frames_processed"] != expected_frames
            or info["cached_perception_used"]
        ):
            raise ValueError("Original control worker is not completed fresh full inference")
        parent_path = run.parent / "run.executor.json"
        parent = read(parent_path)
        inputs[str(parent_path)] = sha(parent_path)
        if (
            parent["status"] != "completed"
            or parent["worker_exit_code"] != 0
            or not parent["frozen_source_inputs_unchanged"]
            or parent["worker_report_sha256"] != inputs[str(run / "inference.json")]
        ):
            raise ValueError("Original control parent/worker binding failed")
        session = read(run / "session.json")
        inputs[str(run / "session.json")] = sha(run / "session.json")
        proxy = run / "data/media" / info["source_sha256"] / "proxy.mp4"
        if sha(proxy) != info["proxy_sha256"]:
            raise ValueError("Completed proxy identity differs")
        inputs[str(proxy)] = info["proxy_sha256"]
        events_path = run / "events.jsonl"
        inputs[str(events_path)] = sha(events_path)
        events = [json.loads(line) for line in events_path.open()]
        calibration = next(e for e in events if e["type"] == "calibration")
        calibration_h = np.asarray(calibration["payload"]["H"])
        catalog_path = run / "perception_completion_catalog.json"
        catalog = read(catalog_path)
        if (
            catalog["session_id"] != session["session_id"]
            or catalog["source_sha256"] != info["source_sha256"]
            or catalog["proxy_sha256"] != info["proxy_sha256"]
            or catalog["frame_count"] != {1: 17268, 2: 29296}[test]
        ):
            raise ValueError("Completed catalogue source/session/extent mismatch")
        inputs[str(catalog_path)] = sha(catalog_path)
        raw = {}
        profiles = []
        for item in catalog["files"]:
            path = run / item["path"]
            if sha(path) != item["sha256"]:
                raise ValueError("Completed perception cache changed")
            packet = msgpack.unpackb(path.read_bytes(), raw=False)
            if any(packet["start"] <= end and packet["end"] >= start for start, end in windows):
                inputs[str(path)] = item["sha256"]
                raw.update(
                    {r["f"]: r for r in packet["frames"] if any(start <= r["f"] <= end for start, end in windows)}
                )
                profiles.append(packet["ci"]["profile"])
        profile = profiles[0]
        if not all(value == profile for value in profiles):
            raise ValueError("Profile changes inside original controls")
        rates = {profile["pose_rates"][state]: profile["detector_rates"][state] for state in ["in_play", "idle"]}
        parameters = profile["components"]["content_continuity"]["params"]
        if parameters["mode"] != "barrier_detector_layout_v2":
            raise ValueError("Unexpected original content policy")
        fps = info["media"]["fps_num"] / info["media"]["fps_den"]
        for start, end in windows:
            key = f"test{test}_{start:05d}_{end:05d}"
            shared = SharedDetector(detector)
            for parent in [OLD_PROBES / "tracking_prefix_probe_v2", OLD_PROBES / "tracking_prefix_probe_v3"]:
                for path in sorted(parent.glob(f"test{test}_*.json")):
                    previous = read(path)
                    selected = [r for r in previous.get("detector_inputs", []) if start <= r["frame"] <= end]
                    if selected:
                        inputs[str(path)] = sha(path)
                        for item in selected:
                            shared.seed(item)
            for prefix, receipt in completed_seeds:
                for path in sorted(prefix.glob(f"test{test}_*.json")):
                    if sha(path) != receipt["artifact_sha256"][str(path.relative_to(prefix))]:
                        raise ValueError("Completed seed case changed")
                    prior = read(path)
                    if (
                        prior["test"] != test
                        or prior["source_sha256"] != info["source_sha256"]
                        or prior["proxy_sha256"] != info["proxy_sha256"]
                    ):
                        raise ValueError("Seed dataset/source/proxy pairing differs")
                    selected = [item for item in prior["detector_inputs"] if start <= item["frame"] <= end]
                    if selected:
                        inputs[str(path)] = sha(path)
                        for item in selected:
                            shared.seed(item)
            seeded = len(shared.cache)
            variants = {}
            for name in ["original", "c7", "foreground"]:
                pm = players if name == "foreground" else controls[name]["players"]
                cm = None if name == "foreground" else controls[name]["content"]
                perception = pm.PlayerPerception(shared, None, fps, det_stride=2, pose_stride=0, max_players=2)
                perception.set_diagnostics(True, 8)
                content = (
                    ContentContinuityProviderV2(**parameters)
                    if cm is None
                    else cm.ContentContinuityProviderV2(**parameters)
                )
                variants[name] = {"players": perception, "content": content, "previous": None, "rows": [], "epoch": 0}
            with av.open(str(proxy)) as container:
                stream = container.streams.video[0]
                stream.thread_count = 1
                container.seek(int(start / fps / stream.time_base), stream=stream, backward=True)
                for decoded in container.decode(video=0):
                    frame = round(float(decoded.pts * decoded.time_base) * fps)
                    if frame < start:
                        continue
                    if frame > end:
                        break
                    if abs(float(decoded.pts * decoded.time_base) - frame / fps) >= 1e-8:
                        raise ValueError("CFR frame/PTS mismatch")
                    image = decoded.to_ndarray(format="bgr24")
                    current = raw[frame]
                    camera_g = np.asarray(current["g"]).reshape(3, 3) if current.get("g") is not None else None
                    h = Homography(camera_g @ calibration_h if camera_g is not None else calibration_h, 0, 4)
                    world = np.asarray([[-3.05, 6.7], [3.05, 6.7], [3.05, -6.7], [-3.05, -6.7]])
                    hardcut = frame > start and current["sh"] != raw[frame - 1]["sh"]
                    det_stride = rates[current["ps"]]
                    shared.frame = frame
                    for name, variant in variants.items():
                        p, content, previous = variant["players"], variant["content"], variant["previous"]
                        # Use each control's native ROI object, identical source geometry.
                        pm = players if name == "foreground" else controls[name]["players"]
                        roi = pm.CourtROI(h.court_to_image(world).astype(np.float32), homography=h)
                        p.set_roi(roi)
                        regions = (
                            []
                            if previous is None
                            else previous["foreground"]
                            if name == "foreground"
                            else [
                                ForegroundRegion(
                                    frame - 1,
                                    f"track:{x.track_id}",
                                    tuple(x.bbox),
                                    x.detector_matched,
                                    previous["detector_observed"],
                                )
                                for x in previous["persons"]
                            ]
                        )
                        evidence = content.observe(
                            frame,
                            image,
                            previous_regions=regions,
                            previous_view_valid=previous is not None and previous["view_valid"],
                            current_view_valid=current["v"] == "main",
                            hard_cut=hardcut,
                        )
                        probe = decision = None
                        barrier = False
                        if evidence.hypothesis:
                            probe = p.probe_detection(frame, image)
                            decision = content.layout_decision(
                                evidence,
                                probe,
                                detector_model="rfdetr_small@1.4.2",
                                geometry_valid=current["v"] == "main" and current["cs"] == "VALID",
                            )
                            barrier = content.tracking_barrier_for_decision(decision)
                        if hardcut or barrier:
                            p.on_cut()
                        if barrier:
                            variant["epoch"] += 1
                        persons = (
                            p.process(frame, image, (det_stride, 0), detection_probe=probe)
                            if current["v"] == "main"
                            else []
                        )
                        if name == "foreground" and current["v"] != "main":
                            p.reset_foreground()
                        foreground = p.foreground_regions(frame) if name == "foreground" else ()
                        variant["rows"].append(
                            {
                                "frame": frame,
                                "source_pts": decoded.pts,
                                "source_time_base": str(decoded.time_base),
                                "detector_stride": det_stride,
                                "detector_observed": p.last_detector_observed,
                                "persons": [body(x) for x in persons],
                                "foreground_regions": [asdict(x) for x in foreground],
                                "scene_foreground_overflow": getattr(getattr(p, "_foreground", None), "overflow", None),
                                "raw_content": asdict(evidence),
                                "decision": asdict(decision) if decision is not None else None,
                                "barrier": barrier,
                                "content_epoch_local": variant["epoch"],
                                "hard_camera_cut": hardcut,
                                "tracking_diagnostic": copy.deepcopy(p.last_diagnostic),
                                "original_persons": [{k: x[k] for k in ["t", "b", "dm"]} for x in current["p"]],
                                "outside_person_count": sum(not roi.contains_feet(x.bbox) for x in persons),
                                "outside_foreground_count": sum(
                                    not roi.contains_feet(np.asarray(x.bbox)) for x in foreground
                                ),
                                "source_pixels_sha256": hashlib.sha256(image.tobytes()).hexdigest(),
                            }
                        )
                        variant["previous"] = {
                            "persons": persons,
                            "foreground": foreground,
                            "detector_observed": p.last_detector_observed,
                            "view_valid": current["v"] == "main",
                        }
                    if frame in FOCUS[test]:
                        panels = []
                        for name, variant in variants.items():
                            row = variant["rows"][-1]
                            panel = image.copy()
                            for person in row["persons"]:
                                box = np.asarray(person["bbox"]).astype(int)
                                color = (0, 230, 0) if person["detector_matched"] else (0, 150, 250)
                                cv2.rectangle(panel, tuple(box[:2]), tuple(box[2:]), color, 2)
                            for region in row["foreground_regions"]:
                                box = np.asarray(region["bbox"]).astype(int)
                                cv2.rectangle(panel, tuple(box[:2]), tuple(box[2:]), (255, 170, 0), 1)
                            cv2.putText(
                                panel,
                                f"{name} f{frame} barrier={row['barrier']}",
                                (10, 25),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6,
                                (255, 255, 255),
                                2,
                            )
                            panels.append(panel)
                        if not cv2.imwrite(str(out / f"{key}_frame_{frame:05d}.png"), np.concatenate(panels, axis=1)):
                            raise OSError("Evidence image write failed")
            for variant in variants.values():
                if [r["frame"] for r in variant["rows"]] != list(range(start, end + 1)):
                    raise ValueError("Incomplete chronological prefix")
            detail = {
                "scope": SCOPE,
                "test": test,
                "range": [start, end],
                "source_sha256": info["source_sha256"],
                "proxy_sha256": info["proxy_sha256"],
                "variants": {name: value["rows"] for name, value in variants.items()},
                "detector_inputs": [
                    {
                        "frame": f,
                        "crop_pixels_sha256": digest,
                        "boxes_crop": boxes.tolist(),
                        "scores": scores.tolist(),
                        "diagnostics": diagnostic,
                    }
                    for (f, digest), (boxes, scores, diagnostic) in shared.cache.items()
                ],
            }
            save(out / f"{key}.json", detail)
            summary = {
                "test": test,
                "range": [start, end],
                "seeded_detector_observations": seeded,
                "unique_detector_observations": len(shared.cache),
                "fresh_neural_detector_calls": shared.fresh_calls,
                "shared_or_retained_reuses": shared.reused_calls,
                "retained_seed_lookups": shared.seed_lookups,
                "same_run_shared_lookups": shared.same_run_lookups,
                "barriers": {
                    name: [r["frame"] for r in variant["rows"] if r["barrier"]] for name, variant in variants.items()
                },
                "foreground_capacity": {
                    name: {
                        "overflow_frames": [
                            r["frame"] for r in variant["rows"] if r["scene_foreground_overflow"] is True
                        ],
                        "nonempty_frames": sum(bool(r["foreground_regions"]) for r in variant["rows"]),
                        "max_returned_regions": max(len(r["foreground_regions"]) for r in variant["rows"]),
                    }
                    for name, variant in variants.items()
                },
                "focus": {
                    str(f): {name: variant["rows"][f - start] for name, variant in variants.items()}
                    for f in sorted(FOCUS[test] & set(range(start, end + 1)))
                },
            }
            summaries.append(summary)
            progress = {k: v for k, v in summary.items() if k not in {"focus", "foreground_capacity"}}
            progress["foreground_capacity"] = {
                name: {
                    **{k: v for k, v in values.items() if k != "overflow_frames"},
                    "overflow_frame_count": len(values["overflow_frames"]),
                }
                for name, values in summary["foreground_capacity"].items()
            }
            print(json.dumps(progress), flush=True)
    if not all(sha(path) == digest for path, digest in inputs.items()):
        raise RuntimeError("Input/source changed during bounded probe")
    if subprocess.check_output(["/usr/bin/git", "-C", str(candidate), "diff", "--binary", "HEAD"], text=True) != dirty:
        raise RuntimeError("Candidate diff changed during probe")
    packages = {}
    for name in ["trackers", "onnxruntime-gpu", "numpy", "opencv-python", "opencv-python-headless", "av"]:
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    (out / "executed_probe.py").write_bytes(Path(__file__).read_bytes())
    save(
        out / "summary.json",
        {
            "status": "completed_bounded_scene_foreground_probe",
            "scope": SCOPE,
            "cases": summaries,
            "candidate_root": str(candidate),
            "candidate_commit": commit,
            "input_sha256": inputs,
            "runtime_packages": packages,
            "actual_ort_providers": detector.tool.session.get_providers(),
            "full_pipeline": False,
            "independent_physical_accuracy": False,
        },
    )


if __name__ == "__main__":
    main()
