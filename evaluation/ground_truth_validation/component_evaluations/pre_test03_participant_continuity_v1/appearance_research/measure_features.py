# ruff: noqa: E501
"""Read-only source/crop-bound HSV diagnostics; no NN, mutation or fitted cutoff."""

from __future__ import annotations

import bisect
import hashlib
import inspect
import json
from collections import defaultdict
from pathlib import Path

import av
import cv2
import msgpack
import numpy as np

from bai_badminton.court import Homography
from bai_badminton.identity import hsv_signature
from bai_badminton.perception.players import CourtROI

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
WORK = ROOT / "evaluation/ground_truth_validation"
ART = ROOT.parent / "ground-truth-validation-artifacts-20261112/pre_test03_v2/test01_candidate_v2"
BASE2 = ROOT.parent / "ground-truth-validation-artifacts-20261110/test_02/improved_v1"
PREFIX = WORK / "component_evaluations/pre_test03_scene_foreground_v1/prefix_v2"
INPUTS = {}
FEATURES = {}
REQUESTS = defaultdict(dict)
GALLERIES = defaultdict(list)
QUERIES = []


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    INPUTS[str(path)] = sha(path)
    return json.loads(Path(path).read_text())


def save(name, data):
    with (HERE / name).open("x") as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write("\n")


def load(run, ranges=None):
    info = read(run / "inference.json")
    assert info["status"] == "completed" and not info["cached_perception_used"]
    cat = read(run / "perception_completion_catalog.json")
    assert cat["source_sha256"] == info["source_sha256"] and cat["proxy_sha256"] == info["proxy_sha256"]
    rows = {}
    for item in cat["files"]:
        if ranges and not any(item["start"] <= b and item["end"] >= a for a, b in ranges):
            continue
        p = run / item["path"]
        assert sha(p) == item["sha256"]
        INPUTS[str(p)] = item["sha256"]
        rows.update(
            {
                r["f"]: r
                for r in msgpack.unpackb(p.read_bytes(), raw=False)["frames"]
                if not ranges or any(a <= r["f"] <= b for a, b in ranges)
            }
        )
    p = run / "events.jsonl"
    INPUTS[str(p)] = sha(p)
    calibration_h = np.asarray(
        next(json.loads(s)["payload"]["calibration_h"] for s in p.open() if json.loads(s)["type"] == "calibration")
    )
    proxy = run / "data/media" / info["source_sha256"] / "proxy.mp4"
    assert sha(proxy) == info["proxy_sha256"]
    INPUTS[str(proxy)] = info["proxy_sha256"]
    return info, rows, calibration_h, proxy


def geometry(row, calibration_h):
    if row["v"] != "main" or row["cs"] != "VALID":
        return None
    current = np.asarray(row["g"]).reshape(3, 3) @ calibration_h if row.get("g") is not None else calibration_h
    h = Homography(current, 0.0, 4)
    world = np.array([[-3.05, 6.7], [3.05, 6.7], [3.05, -6.7], [-3.05, -6.7]])
    return CourtROI(h.court_to_image(world).astype(np.float32), homography=h)


def context(row):
    return int(row["sh"]), int(row["ce"])


def feature_id(test, frame, key, box, **metadata):
    marker = f"{test}:{frame}:{key}"
    if marker in REQUESTS[test]:
        assert REQUESTS[test][marker]["bbox"] == list(box)
    else:
        REQUESTS[test][marker] = {"test": test, "frame": frame, "key": key, "bbox": list(box), **metadata}
    return marker


def bank(test, ctx, key, frame):
    values = GALLERIES[test, ctx, key]
    idx = bisect.bisect_left([v["frame"] for v in values], frame)
    chosen = values[max(0, idx - 32) : idx]
    return [
        feature_id(
            test,
            v["frame"],
            key,
            v["bbox"],
            role="fresh_strict_incourt_reference",
            context=ctx,
            fresh=True,
            strict_incourt=True,
        )
        for v in chosen
    ]


def tv(a, b):
    return float(np.abs(a - b).sum() / 2)


def hellinger(a, b):
    return float(np.sqrt(np.square(np.sqrt(a) - np.sqrt(b)).sum() / 2))


def evaluate(query):
    p = np.asarray(FEATURES[query["candidate"]]["histogram"], float)
    ids = query["reference_bank"]
    result = {
        **query,
        "ground_truth": None,
        "reference_samples": len(ids),
        "envelope_support": None,
        "reason": "minimum2_reference_samples_required",
        "distance_to_mean_TV": None,
        "distance_to_mean_Hellinger": None,
    }
    if len(ids) < 2:
        return result
    hist = np.asarray([FEATURES[k]["histogram"] for k in ids], float)
    mean = hist.mean(axis=0)
    loo = [tv(hist[i], np.delete(hist, i, axis=0).mean(axis=0)) for i in range(len(hist))]
    distance = tv(p, mean)
    result.update(
        reason="self_consistent" if distance <= max(loo) else "outside_incourt_self_consistency_envelope",
        distance_to_mean_TV=distance,
        distance_to_mean_Hellinger=hellinger(p, mean),
        nearest_reference_TV=min(tv(p, h) for h in hist),
        reference_LOO_TV={"minimum": min(loo), "maximum": max(loo), "mean": float(np.mean(loo))},
        envelope_support=bool(distance <= max(loo)),
        reference_age_frames=query["frame"] - max(FEATURES[k]["frame"] for k in ids),
        current_support_eligible=bool(query["fresh_raw_candidate"] and query["same_context"]),
    )
    alternatives = []
    for key, bank_ids in query["other_banks"].items():
        if len(bank_ids) >= 2:
            alternatives.append(
                {
                    "key": key,
                    "distance_TV": tv(p, np.asarray([FEATURES[k]["histogram"] for k in bank_ids]).mean(axis=0)),
                }
            )
    result["other_gallery_distances"] = alternatives
    result["target_gallery_uniquely_nearest"] = (
        bool(all(distance < q["distance_TV"] for q in alternatives)) if alternatives else None
    )
    competitors = [
        {"candidate": cid, "distance_TV": tv(np.asarray(FEATURES[cid]["histogram"], float), mean)}
        for cid in query["competing_candidates"]
        if cid != query["candidate"]
    ]
    result["competing_candidate_distances"] = competitors
    result["target_candidate_uniquely_nearest_to_gallery"] = (
        bool(all(distance < q["distance_TV"] for q in competitors)) if competitors else None
    )
    result["mutual_unique_nearest"] = bool(
        result["target_gallery_uniquely_nearest"] and result["target_candidate_uniquely_nearest_to_gallery"]
    )
    return result


def main():
    assert not (HERE / "results.json").exists(), "Use a new result version"
    cv2.setNumThreads(1)
    declaration = read(HERE / "CONFIG.json")
    assert declaration["minimum_bank_samples"] == 2
    function = inspect.getsource(hsv_signature)
    (HERE / "executed_hsv_signature.py.source").open("x").write(function)
    INPUTS[str(Path(inspect.getfile(hsv_signature)).resolve())] = sha(inspect.getfile(hsv_signature))
    gross = read(WORK / "regression_tests/pre_test03_scene_v1/test01_independent_v2/gross_coverage_all_182_rows.json")
    info1, raw1, h1, proxy1 = load(ART / "run")
    info2, raw2, h2, proxy2 = load(BASE2 / "run", [(5505, 6510)])
    prefix = read(PREFIX / "test2_05505_06510.json")
    assert prefix["source_sha256"] == info2["source_sha256"] and prefix["proxy_sha256"] == info2["proxy_sha256"]
    media = {
        1: {"info": info1, "raw": raw1, "calibration_h": h1, "proxy": proxy1},
        2: {"info": info2, "raw": raw2, "calibration_h": h2, "proxy": proxy2},
    }
    # Gallery metadata only, followed by selection of bounded past references.
    for test, source in media.items():
        for frame, row in source["raw"].items():
            roi = geometry(row, source["calibration_h"])
            if roi is None:
                continue
            regions = row["fg"] if test == 1 else prefix["variants"]["foreground"][frame - 5505]["foreground_regions"]
            ctx = (
                context(row)
                if test == 1
                else (int(row["sh"]), prefix["variants"]["foreground"][frame - 5505]["content_epoch_local"])
            )
            for region in regions:
                if (
                    region["detector_observed"] is True
                    and region["detector_matched"] is True
                    and roi.contains_feet(np.asarray(region["bbox"]), allow_runoff=False)
                ):
                    GALLERIES[test, ctx, region["key"]].append({"frame": frame, "bbox": region["bbox"]})
    for item in gross["all_rows"]:
        frame = item["frame"]
        row = raw1[frame]
        ctx = context(row)
        candidate = item["fresh_fg"]
        key = candidate["key"]
        target = feature_id(
            1,
            frame,
            key,
            candidate["bbox"],
            role="agent_reviewed_athlete_coverage_diagnostic",
            context=ctx,
            fresh=candidate["detector_matched"] is True and candidate["detector_observed"] is True,
            strict_incourt=False,
        )
        regions = row["fg"]
        others = {r["key"]: bank(1, ctx, r["key"], frame) for r in regions if r["key"] != key}
        competitors = [
            feature_id(
                1,
                frame,
                r["key"],
                r["bbox"],
                role="current_foreground_competitor",
                context=ctx,
                fresh=r["detector_matched"] is True and r["detector_observed"] is True,
                strict_incourt=None,
            )
            for r in regions
        ]
        group = next(i for i, g in enumerate(gross["groups"], 1) if g["frames"][0] <= frame <= g["frames"][1])
        QUERIES.append(
            {
                "test": 1,
                "frame": frame,
                "group": group,
                "kind": "coverage_diagnostic_not_identity_GT",
                "candidate": target,
                "target_visual_episode": key,
                "reference_bank": bank(1, ctx, key, frame),
                "other_banks": others,
                "competing_candidates": competitors,
                "same_context": True,
                "fresh_raw_candidate": candidate["detector_matched"] is True and candidate["detector_observed"] is True,
                "current_raw_confidence": item["current_diagnostic_uncalibrated_support"],
                "confidence_scope": "Null where current fg schema does not retain confidence; historical person confidence is not copied.",
            }
        )
    # The negative query is selected spatially from the already reviewed official
    # source region, not by appearance or a production blacklist.
    first = prefix["variants"]["foreground"][5958 - 5505]
    anchor = next(r for r in first["foreground_regions"] if r["key"] == "court-origin:0")
    target_context = (int(raw2[5958]["sh"]), first["content_epoch_local"])
    fixed_bank = bank(2, target_context, "court-origin:0", 5958)

    def iou(a, b):
        a, b = np.asarray(a), np.asarray(b)
        inter = np.maximum(0, np.minimum(a[2:], b[2:]) - np.maximum(a[:2], b[:2])).prod()
        return float(inter / ((a[2:] - a[:2]).prod() + (b[2:] - b[:2]).prod() - inter))

    for obs in prefix["detector_inputs"]:
        frame = obs["frame"]
        if not 5958 <= frame <= 6492:
            continue
        roi = geometry(raw2[frame], h2)
        assert roi is not None
        crop = roi.crop_box(1280, 720)
        offset = np.asarray([crop[0], crop[1], crop[0], crop[1]])
        boxes = [np.asarray(b) + offset for b in obs["boxes_crop"]]
        candidates = [i for i, box in enumerate(boxes) if iou(box, anchor["bbox"]) >= 0.3]
        assert len(candidates) <= 1, "Official diagnostic region selection ambiguous"
        if not candidates:
            continue
        current = prefix["variants"]["foreground"][frame - 5505]
        ctx = (int(raw2[frame]["sh"]), current["content_epoch_local"])
        ids = []
        for index, box in enumerate(boxes):
            cid = feature_id(
                2,
                frame,
                f"raw:{index}:{obs['crop_pixels_sha256'][:10]}",
                box.tolist(),
                role="retained_raw_model_candidate",
                context=ctx,
                fresh=True,
                strict_incourt=roi.contains_feet(box, allow_runoff=False),
                raw_detector_confidence=obs["scores"][index],
                model_input_crop_pixels_sha256=obs["crop_pixels_sha256"],
                model_crop_box=list(crop),
            )
            ids.append(cid)
        index = candidates[0]
        otherbanks = {
            r["key"]: bank(2, ctx, r["key"], frame)
            for r in current["foreground_regions"]
            if r["key"] != "court-origin:0"
        }
        QUERIES.append(
            {
                "test": 2,
                "frame": frame,
                "group": "official_5958_6492",
                "kind": "agent_reviewed_official_spatial_query_not_identity_GT",
                "candidate": ids[index],
                "target_visual_episode": "court-origin:0_pre_handover",
                "reference_bank": fixed_bank,
                "other_banks": otherbanks,
                "competing_candidates": ids,
                "same_context": ctx == target_context,
                "fresh_raw_candidate": True,
                "current_raw_confidence": obs["scores"][index],
                "confidence_scope": "Exact retained raw model score; uncalibrated",
                "negative_region_selection_IoU": iou(boxes[index], anchor["bbox"]),
            }
        )
    # Decode only requested source instants, grouping nearby seeks.
    for test, requests in REQUESTS.items():
        byframe = defaultdict(list)
        for fid, item in requests.items():
            byframe[item["frame"]].append((fid, item))
        numbers = sorted(byframe)
        blocks = []
        for frame in numbers:
            if not blocks or frame - blocks[-1][-1] > 30:
                blocks.append([frame])
            else:
                blocks[-1].append(frame)
        with av.open(str(media[test]["proxy"])) as container:
            stream = container.streams.video[0]
            stream.thread_count = 1
            for block in blocks:
                container.seek(int(block[0] / 30 / stream.time_base), stream=stream, backward=True)
                for decoded in container.decode(video=0):
                    frame = round(float(decoded.pts * decoded.time_base) * 30)
                    if frame < block[0]:
                        continue
                    if frame > block[-1]:
                        break
                    if frame not in byframe:
                        continue
                    assert abs(float(decoded.pts * decoded.time_base) - frame / 30) < 1e-8
                    image = decoded.to_ndarray(format="bgr24")
                    pixels = hashlib.sha256(image.tobytes()).hexdigest()
                    for fid, item in byframe[frame]:
                        x1, y1, x2, y2 = (int(v) for v in item["bbox"])
                        crop = image[max(0, y1) : max(0, y2), max(0, x1) : max(0, x2)]
                        descriptor = hsv_signature(crop)
                        assert descriptor is not None
                        if item.get("model_input_crop_pixels_sha256"):
                            a, b, c, d = item["model_crop_box"]
                            assert (
                                hashlib.sha256(image[b:d, a:c].tobytes()).hexdigest()
                                == item["model_input_crop_pixels_sha256"]
                            )
                        height = crop.shape[0]
                        torso = crop[int(0.2 * height) : int(0.55 * height)]
                        nonzero = descriptor[descriptor > 0]
                        FEATURES[fid] = {
                            **item,
                            "source_pts": decoded.pts,
                            "source_time_base": str(decoded.time_base),
                            "source_pixels_sha256": pixels,
                            "bbox_crop_pixels_sha256": hashlib.sha256(crop.tobytes()).hexdigest(),
                            "torso_pixels_sha256": hashlib.sha256(torso.tobytes()).hexdigest(),
                            "torso_shape": list(torso.shape),
                            "histogram": descriptor.tolist(),
                            "histogram_entropy_bits": float(-(nonzero * np.log2(nonzero)).sum()),
                        }
        assert all(fid in FEATURES for fid in requests)
    measured = [evaluate(q) for q in QUERIES]
    save(
        "results.json",
        {
            "scope": "Raw HSV distributions and predeclared online self-consistency diagnostics, not calibrated identity/physicalGT or pipeline admission results. No gallery learns outside.",
            "declaration": declaration,
            "queries": measured,
            "current_source_sha256": {t: m["info"]["source_sha256"] for t, m in media.items()},
            "proxy_sha256": {t: m["info"]["proxy_sha256"] for t, m in media.items()},
            "model_sha256": "fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e",
            "candidate_metadata_limits": "Test1fresh_fg raw proposal locations retained but all-proposal competition/crop hash/confidence not serialized except detailed frames. Feature source/torso crop hashes are newly measured diagnostics, not invented worker fields. Test2exact retained modelcrop hashes verified.",
            "input_sha256": INPUTS,
            "new_NN": False,
            "production_changes": False,
            "ground_truth": None,
        },
    )
    with (HERE / "raw_features.jsonl").open("x") as out:
        for fid, item in FEATURES.items():
            out.write(json.dumps({"feature_id": fid, **item}, allow_nan=False) + "\n")
    assert all(sha(path) == digest for path, digest in INPUTS.items())
    print(
        json.dumps(
            {
                "features": len(FEATURES),
                "queries": len(measured),
                "test1_rows": sum(q["test"] == 1 for q in measured),
                "negative_queries": sum(q["test"] == 2 for q in measured),
                "newNN": False,
            }
        )
    )


if __name__ == "__main__":
    main()
