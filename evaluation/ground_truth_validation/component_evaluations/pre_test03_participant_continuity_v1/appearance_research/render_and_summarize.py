# ruff: noqa: E501
"""Closed feature results -> descriptive summary/source-crop panels, no tuning."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

import av
import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(name, data):
    with (HERE / name).open("x") as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write("\n")


def main():
    if (HERE / "summary.json").exists() or (HERE / "source_crop_controls.png").exists():
        raise FileExistsError("Use a new diagnostic version; preserve completed plots/results")
    results = json.loads((HERE / "results.json").read_text())
    features = {r["feature_id"]: r for r in (json.loads(line) for line in (HERE / "raw_features.jsonl").open())}
    queries = results["queries"]
    summary = []
    panel_rows = []
    for group in [1, 2, 3, 4, 5, 6, 7, "official_5958_6492"]:
        rows = sorted([q for q in queries if q["group"] == group], key=lambda q: q["frame"])
        fresh = [q for q in rows if q["fresh_raw_candidate"]]
        distances = [q["distance_to_mean_TV"] for q in rows if q["distance_to_mean_TV"] is not None]
        fresh_distances = [q["distance_to_mean_TV"] for q in fresh if q["distance_to_mean_TV"] is not None]
        item = {
            "group": group,
            "frames": [min(q["frame"] for q in rows), max(q["frame"] for q in rows)],
            "query_count": len(rows),
            "fresh_candidate_count": len(fresh),
            "reference_sample_counts": sorted({q["reference_samples"] for q in rows}),
            "self_envelope_supported_all_rows": sum(q["envelope_support"] is True for q in rows),
            "self_envelope_supported_fresh": sum(q["envelope_support"] is True for q in fresh),
            "mutual_nearest_fresh": sum(q.get("mutual_unique_nearest") is True for q in fresh),
            "TV_all_min_median_max": [float(min(distances)), float(np.median(distances)), float(max(distances))]
            if distances
            else None,
            "TV_fresh_min_median_max": [
                float(min(fresh_distances)),
                float(np.median(fresh_distances)),
                float(max(fresh_distances)),
            ]
            if fresh_distances
            else None,
            "same_context_rows": sum(q["same_context"] for q in rows),
            "ground_truth": None,
        }
        summary.append(item)
        first = rows[0]
        bank = first["reference_bank"]
        chosen = [bank[0], bank[len(bank) // 2], bank[-1]] if bank else []
        examples = fresh or rows
        if group == "official_5958_6492":
            frames = [rows[0]["frame"], 6018, 6210, rows[-1]["frame"]]
            chosen += [next(q["candidate"] for q in rows if q["frame"] == f) for f in frames]
        else:
            chosen += [examples[0]["candidate"], examples[len(examples) // 2]["candidate"], examples[-1]["candidate"]]
        panel_rows.append((str(group), chosen))
    requested = defaultdict(lambda: defaultdict(list))
    for _, ids in panel_rows:
        for fid in ids:
            requested[features[fid]["test"]][features[fid]["frame"]].append(fid)
    media = {
        1: ROOT.parent / "ground-truth-validation-artifacts-20261112/pre_test03_v2/test01_candidate_v2/run",
        2: ROOT.parent / "ground-truth-validation-artifacts-20261110/test_02/improved_v1/run",
    }
    crops = {}
    for test, byframe in requested.items():
        info = json.loads((media[test] / "inference.json").read_text())
        proxy = media[test] / "data/media" / info["source_sha256"] / "proxy.mp4"
        assert sha(proxy) == results["proxy_sha256"][str(test)]
        with av.open(str(proxy)) as container:
            stream = container.streams.video[0]
            stream.thread_count = 1
            for frame, ids in sorted(byframe.items()):
                container.seek(int(frame / 30 / stream.time_base), stream=stream, backward=True)
                for decoded in container.decode(video=0):
                    f = round(float(decoded.pts * decoded.time_base) * 30)
                    if f < frame:
                        continue
                    assert f == frame
                    image = decoded.to_ndarray(format="bgr24")
                    for fid in ids:
                        item = features[fid]
                        assert hashlib.sha256(image.tobytes()).hexdigest() == item["source_pixels_sha256"]
                        x1, y1, x2, y2 = (int(v) for v in item["bbox"])
                        crop = image[max(0, y1) : max(0, y2), max(0, x1) : max(0, x2)]
                        assert hashlib.sha256(crop.tobytes()).hexdigest() == item["bbox_crop_pixels_sha256"]
                        crops[fid] = crop.copy()
                    break
    cell_w, cell_h = 180, 240
    canvas = np.zeros((len(panel_rows) * cell_h, 7 * cell_w, 3), np.uint8)
    for row, (label, ids) in enumerate(panel_rows):
        for col, fid in enumerate(ids):
            crop = crops[fid]
            scale = min((cell_w - 8) / crop.shape[1], (cell_h - 65) / crop.shape[0])
            small = cv2.resize(crop, (round(crop.shape[1] * scale), round(crop.shape[0] * scale)))
            y = row * cell_h + 55
            x = col * cell_w + (cell_w - small.shape[1]) // 2
            canvas[y : y + small.shape[0], x : x + small.shape[1]] = small
            role = "REF strict" if col < 3 else ("candidate fresh" if features[fid]["fresh"] else "CARRY unknown")
            cv2.putText(
                canvas,
                f"G{label} {role}",
                (col * cell_w + 3, row * cell_h + 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.34,
                (255, 255, 255),
                1,
            )
            cv2.putText(
                canvas,
                f"T{features[fid]['test']} f{features[fid]['frame']}",
                (col * cell_w + 3, row * cell_h + 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.40,
                (180, 230, 255),
                1,
            )
    assert cv2.imwrite(str(HERE / "source_crop_controls.png"), canvas)
    save(
        "summary.json",
        {
            "groups": summary,
            "fixed_policy_before_measurement_sha256": sha(HERE / "CONFIG.json"),
            "results_sha256": sha(HERE / "results.json"),
            "features_sha256": sha(HERE / "raw_features.jsonl"),
            "support_scope": "Self-consistency/nearest-neighbor diagnostic counts, not identity accuracy, TP/FP/FN or pipeline admissions.",
            "official_mutual_counterexamples": [
                {
                    "frame": q["frame"],
                    "same_context": q["same_context"],
                    "TV": q["distance_to_mean_TV"],
                    "envelope": q["reference_LOO_TV"]["maximum"],
                }
                for q in queries
                if q["test"] == 2 and q.get("mutual_unique_nearest")
            ],
            "panel_selection": "Each group first/middle/last bank and first/middle/last fresh candidate (or carry if no fresh). Official first/last plus ALL mutual-only counterexamples6018/6210. No success-biased selection.",
            "panel_rows": [{"group": g, "features": ids} for g, ids in panel_rows],
            "panel_sha256": sha(HERE / "source_crop_controls.png"),
        },
    )
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
