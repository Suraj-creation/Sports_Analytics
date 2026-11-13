"""Isolated appearance-only research; never changes admission or stores descriptors."""
from collections import Counter, deque
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import time

import av
import cv2
import msgpack
import numpy as np
import torch

from bai_badminton.court import Homography
from bai_badminton.perception.offline_reid import OSNetAppearanceEmbedder
from bai_badminton.perception.players import CourtROI, _box_iou
from bai_badminton.perception.player_association import MIN_COSINE, ASSIGNMENT_MARGIN

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
EVAL = ROOT / "evaluation/ground_truth_validation"
SCENE = EVAL / "regression_tests/pre_test03_scene_v1"
PREFIX = EVAL / "component_evaluations/pre_test03_perception_v1/tracking_prefix_probe_v3"
CHECKPOINT = OUT / "inputs/osnet_ain_x0_25.pt"
EXPECTED = "ce171fe160b3608f5e4c19489774991419be965b1d6f4bdccc4b4cfd2ef95347"
inputs = {}


def digest(path):
    return hashlib.file_digest(Path(path).open("rb"), "sha256").hexdigest()


def bind(path):
    path = Path(path).resolve()
    inputs[str(path)] = digest(path)
    return path


def read(path):
    return json.loads(bind(path).read_text())


def roi_for(raw, H):
    if raw.get("g") is None:
        return None
    h = Homography(np.asarray(raw["g"]).reshape(3, 3) @ H, 0.0, 4)
    world = np.asarray([[-3.05, 6.7], [3.05, 6.7], [3.05, -6.7], [-3.05, -6.7]])
    return CourtROI(h.court_to_image(world).astype(np.float32), homography=h)


def load_raw(run, windows):
    info = read(run / "inference.json")
    assert info["status"] == "completed" and not info["cached_perception_used"]
    cat = read(run / "perception_completion_catalog.json")
    rows = {}
    for item in cat["files"]:
        path = run / item["path"]
        chunk = msgpack.unpackb(path.read_bytes(), raw=False)
        if not any(chunk["start"] <= z and chunk["end"] >= a for a, z in windows):
            continue
        assert digest(bind(path)) == item["sha256"]
        for r in chunk["frames"]:
            if any(a <= r["f"] <= z for a, z in windows):
                rows[r["f"]] = r
    events = bind(run / "events.jsonl")
    H = next(json.loads(x)["payload"]["H"] for x in events.read_text().splitlines() if json.loads(x)["type"] == "calibration")
    proxy = bind(run / "data/media" / info["source_sha256"] / "proxy.mp4")
    assert inputs[str(proxy)] == info["proxy_sha256"]
    return info, rows, np.asarray(H), proxy


def decode(proxy, windows):
    with av.open(str(proxy)) as container:
        stream = container.streams.video[0]
        stream.thread_count = 1
        for start, stop in windows:
            container.seek(int(Fraction(start, 30) / stream.time_base), stream=stream, backward=True)
            for decoded in container.decode(video=0):
                t = Fraction(decoded.pts) * decoded.time_base
                frame = round(t * 30)
                if frame < start:
                    continue
                if frame > stop:
                    break
                assert t == Fraction(frame, 30)
                yield frame, decoded.to_ndarray(format="bgr24"), decoded.pts, str(decoded.time_base)


def box_iou(a, b):
    return float(_box_iou(np.asarray(a).reshape(1, 4), np.asarray(b).reshape(1, 4))[0, 0])


def embed(image, boxes, model):
    result = []
    for start in range(0, len(boxes), 8):
        result.extend(model.embed(image, boxes[start:start + 8]))
    return result


def crop_metadata(image, box):
    b = np.rint(box).astype(int)
    h, w = image.shape[:2]
    assert 0 <= b[0] < b[2] <= w and 0 <= b[1] < b[3] <= h
    crop = np.ascontiguousarray(image[b[1]:b[3], b[0]:b[2]])
    return {"rounded_bbox": b.tolist(), "shape": list(crop.shape), "bgr_pixels_sha256": hashlib.sha256(crop.tobytes()).hexdigest()}


def compare(frame, box, feature, gallery, all_features, query_index):
    scores = []
    for key, entries in sorted(gallery.items()):
        best = max(float(feature @ entry["feature"]) for entry in entries)
        last = entries[-1]["frame"]
        assert all(entry["frame"] < frame for entry in entries)
        scores.append({"seed_hypothesis": key, "cosine": best, "last_strict_court_seed_frame": last,
                       "age_frames": frame - last, "gallery_frames": [e["frame"] for e in entries],
                       "gallery_crop_sha256": [e["crop_sha256"] for e in entries]})
    scores.sort(key=lambda x: x["cosine"], reverse=True)
    if not scores:
        return {"status": "no_past_seed", "similarities": []}
    best = scores[0]
    runner = scores[1]["cosine"] if len(scores) > 1 else None
    key = best["seed_hypothesis"]
    competing = [max(float(f @ e["feature"]) for e in gallery[key])
                 for i, f in enumerate(all_features) if i != query_index]
    col_gap = best["cosine"] - max(competing) if competing else None
    row_gap = best["cosine"] - runner if runner is not None else None
    base_pass = best["cosine"] >= MIN_COSINE
    margin_pass = (row_gap is None or row_gap >= ASSIGNMENT_MARGIN) and (col_gap is None or col_gap >= ASSIGNMENT_MARGIN)
    dormant = best["age_frames"] > 30
    dormant_pass = not dormant or best["cosine"] >= 0.9
    return {"status": "appearance_support" if base_pass and margin_pass and dormant_pass else
                      "below_live_cosine" if not base_pass else "ambiguous_margin" if not margin_pass else "below_dormant_cosine",
            "best_seed_hypothesis": key, "best_cosine": best["cosine"], "row_cosine_gap": row_gap,
            "column_cosine_gap": col_gap, "dormant": dormant, "live_cosine_pass": base_pass,
            "cosine_margin_pass": margin_pass, "dormant_cosine_pass": dormant_pass,
            "similarities": scores, "motion_gate_applied": False, "production_assignment": False}


def execute_case(test, run, windows, target_rows, prefix=None):
    info, raw, H, proxy = load_raw(run, windows)
    prefix_rows = {x["frame"]: x for x in prefix["variants"]["after"]} if prefix else {}
    detector = {x["frame"]: x for x in prefix["detector_inputs"]} if prefix else {}
    gallery, previous_epoch, previous_frame = {}, None, None
    all_records, seeds, pixels, resets = [], [], [], []
    for frame, image, pts, tb in decode(proxy, windows):
        r = raw[frame]
        epoch = (r["sh"], r["ce"])
        reset = previous_frame is None or frame != previous_frame + 1 or epoch != previous_epoch
        if prefix and prefix_rows[frame]["barrier"]:
            reset = True
        if reset:
            gallery.clear()
            resets.append(frame)
        previous_frame, previous_epoch = frame, epoch
        gallery = {k: v for k, v in gallery.items() if frame - v[-1]["frame"] <= 240}
        image_sha = hashlib.sha256(image.tobytes()).hexdigest()
        if prefix:
            assert image_sha == prefix_rows[frame]["source_pixels_sha256"]
        roi = roi_for(r, H)
        assert image.shape == (720, 1280, 3)
        pixels.append({"test": test, "frame": frame, "pts": pts, "time_base": tb, "pixels_sha256": image_sha})
        observations = []
        if test == 1 and frame in target_rows:
            target = target_rows[frame]
            fg = target["fresh_fg"]
            observations.append({"kind": "withheld_target", "bbox": fg["bbox"],
                                 "detector_matched": fg["detector_matched"], "detector_observed": fg["detector_observed"],
                                 "confidence": None, "fresh_confidence_source": None, "foreground_key": fg["key"]})
            dg = ((r.get("dg") or {}).get("players") or {})
            for rejection in dg.get("roi_rejected", []):
                if box_iou(rejection["bbox"], fg["bbox"]) > 0.99:
                    observations[0]["confidence"] = rejection["support"]
                    observations[0]["fresh_confidence_source"] = "current_retained_roi_rejection"
                else:
                    observations.append({"kind": "retained_raw_rejected_competitor", "bbox": rejection["bbox"],
                                         "detector_matched": True, "detector_observed": True,
                                         "confidence": rejection["support"], "fresh_confidence_source": "current_retained_roi_rejection"})
            for fg2 in r.get("fg", []):
                if fg2["detector_matched"] and fg2["detector_observed"] and not any(box_iou(fg2["bbox"], x["bbox"]) > .99 for x in observations):
                    observations.append({"kind": "retained_fresh_fg_competitor", "bbox": fg2["bbox"], "detector_matched": True,
                                         "detector_observed": True, "confidence": None, "fresh_confidence_source": None})
        elif test == 2 and 5956 <= frame <= 6492 and frame in detector:
            det = detector[frame]
            crop = roi.crop_box(1280, 720)
            x0, y0, x1, y1 = crop
            assert hashlib.sha256(image[y0:y1, x0:x1].tobytes()).hexdigest() == det["crop_pixels_sha256"]
            boxes = np.asarray(det["boxes_crop"]) + [x0, y0, x0, y0]
            observations = [{"kind": "all_retained_test2_raw_proposals", "proposal_index": i, "bbox": box.tolist(),
                             "detector_matched": True, "detector_observed": True, "confidence": float(score),
                             "fresh_confidence_source": "retained_full_raw_detector_input", "detector_crop_sha256": det["crop_pixels_sha256"]}
                            for i, (box, score) in enumerate(zip(boxes, det["scores"], strict=True))]
        if observations:
            feats = embed(image, [x["bbox"] for x in observations], model)
            for i, (row, feat) in enumerate(zip(observations, feats, strict=True)):
                row.update(test=test, frame=frame, seconds=frame / 30, source_sha256=info["source_sha256"],
                           proxy_sha256=info["proxy_sha256"], image_pixels_sha256=image_sha, crop=crop_metadata(image, row["bbox"]),
                           named_identity=None, physical_gt=None, strict_court=roi.contains_feet(np.asarray(row["bbox"]), allow_runoff=False))
                row["appearance"] = compare(frame, row["bbox"], feat, gallery, feats, i)
                row["operational_eligibility"] = "not_evaluated_motion_and_admission_not_applied"
                row["current_confidence_available"] = row["confidence"] is not None
                row["current_observation_category"] = "fresh_detector_supported" if row["detector_matched"] and row["detector_observed"] else "carried_box_current_image_crop_only"
                row["full_raw_population_available"] = test == 2
                all_records.append(row)
        persons = prefix_rows[frame]["persons"] if prefix else r["p"]
        eligible = []
        for person in persons:
            b = np.asarray(person["bbox"] if prefix else person["b"], float)
            dm = person["detector_matched"] if prefix else person["dm"]
            conf = person["confidence"] if prefix else person["c"]
            if dm is True and conf >= .5 and roi is not None and roi.contains_feet(b, allow_runoff=False):
                if all(box_iou(b, np.asarray(other["bbox"] if prefix else other["b"])) < .3 for other in persons if other is not person):
                    key = str(person["raw_track"] if prefix else person["rt"])
                    eligible.append((key, b, conf))
        if eligible:
            features = embed(image, [x[1] for x in eligible], model)
            for (key, b, conf), feature in zip(eligible, features, strict=True):
                galkey = f"epoch:{epoch[0]}:{epoch[1]}:raw:{key}"
                if galkey not in gallery and len(gallery) >= 16:
                    continue
                cm = crop_metadata(image, b)
                gallery.setdefault(galkey, deque(maxlen=4)).append({"frame": frame, "feature": feature, "crop_sha256": cm["bgr_pixels_sha256"]})
                seeds.append({"test": test, "frame": frame, "hypothesis": galkey, "bbox": b.tolist(), "confidence": conf,
                              "strict_court": True, "detector_matched": True, "image_sha256": image_sha, "crop": cm,
                              "named_identity": None, "gallery_size": len(gallery[galkey])})
        assert len(gallery) <= 16 and all(len(g) <= 4 for g in gallery.values())
    return all_records, seeds, pixels, resets


if __name__ == "__main__":
    assert ROOT.name == "Sports_Analytics" and os.environ.get("CUDA_VISIBLE_DEVICES") == "1"
    assert not (OUT / "completion.json").exists() and digest(bind(CHECKPOINT)) == EXPECTED
    assert MIN_COSINE == .8 and ASSIGNMENT_MARGIN == .05
    started = time.time()
    torch.set_num_threads(2)
    cv2.setNumThreads(1)
    before = read(OUT.parent / "reid_investigation/source_and_local_availability.json")
    for item in before["source_files"]:
        assert digest(bind(item["path"])) == item["sha256"]
    bind(__file__)
    model = OSNetAppearanceEmbedder(CHECKPOINT, device="cuda:0", max_crops=8)
    gross = read(SCENE / "test01_independent_v2/gross_coverage_all_182_rows.json")
    targets = {r["frame"]: r for r in gross["all_rows"]}
    assert len(targets) == 182
    windows = []
    for group in gross["groups"]:
        a, z = group["frames"]
        if windows and a - 240 <= windows[-1][1] + 1:
            windows[-1][1] = z
        else:
            windows.append([max(0, a - 240), z])
    run1 = ROOT.parent / "ground-truth-validation-artifacts-20261112/pre_test03_v2/test01_candidate_v2/run"
    r1, s1, px1, resets1 = execute_case(1, run1, windows, targets)
    print("Test1 done", len(r1), "comparisons", len(s1), "past court seeds", flush=True)
    prefix = read(PREFIX / "test2_05505_06510.json")
    run2 = ROOT.parent / "ground-truth-validation-artifacts-20261110/test_02/improved_v1/run"
    r2, s2, px2, resets2 = execute_case(2, run2, [[5505, 6492]], {}, prefix)
    torch.cuda.synchronize()
    for name, values in [("comparison_rows.jsonl", r1 + r2), ("gallery_seed_receipts.jsonl", s1 + s2), ("decoded_frame_receipts.jsonl", px1 + px2)]:
        with (OUT / name).open("x") as f:
            for row in values:
                f.write(json.dumps(row, allow_nan=False) + "\n")
    assert len([x for x in r1 if x["kind"] == "withheld_target"]) == 182
    summary = {"schema": "isolated-osnet-appearance-crop-probe:v1", "status": "completed",
               "scope": "Appearance-only conditional/exploratory cosine and row/column cosine-margin probe; not production joint-motion assignment/admission or physical identity accuracy.",
               "test1_target_count": 182, "test1_counts": dict(Counter(x["appearance"]["status"] for x in r1 if x["kind"] == "withheld_target")),
               "test2_proposal_count": len(r2), "test2_counts": dict(Counter(x["appearance"]["status"] for x in r2)),
               "test1_resets": resets1, "test2_resets": resets2,
               "elapsed_s": time.time() - started, "cuda_peak_allocated_bytes": torch.cuda.max_memory_allocated(),
               "torch": torch.__version__, "device_name": torch.cuda.get_device_name(0), "CUDA_VISIBLE_DEVICES": "1",
               "checkpoint_sha256": EXPECTED, "private_descriptors_saved": False, "outside_gallery_learning": False,
               "named_identity_created": False, "physical_gt_created": False, "production_modified": False,
               "input_sha256": inputs}
    for path, value in inputs.items():
        assert digest(path) == value, path
    with (OUT / "summary.json").open("x") as f:
        json.dump(summary, f, indent=2)
    outputs = {str(p.relative_to(OUT)): digest(p) for p in OUT.rglob("*") if p.is_file()}
    with (OUT / "completion.json").open("x") as f:
        json.dump({"status": "completed", "artifact_sha256": outputs, "source_inputs_unchanged": True}, f, indent=2)
    print(json.dumps({k: v for k, v in summary.items() if k != "input_sha256"}), flush=True)
