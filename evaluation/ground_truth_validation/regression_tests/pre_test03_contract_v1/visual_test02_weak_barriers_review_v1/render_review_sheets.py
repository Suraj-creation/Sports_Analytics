"""Verify sealed rendered evidence and create aspect-preserving review sheets.

No video decoder, model, pipeline module or original event store is opened.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

OUT = Path(__file__).resolve().parent
PACKAGE = OUT.parent / "visual_test02_weak_barriers_v1"
WEAK = [355, 699, 1095, 3394, 4581, 5958, 11691, 11985, 25521]
CONTROLS = [6151, 6307, 6492, 7703, 11333, 11346, 13153, 23639]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, data):
    with path.open("x") as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write("\n")


def tile(image, label):
    height, width = image.shape[:2]
    scale = min(640 / width, 445 / height)
    resized = cv2.resize(image, (round(width * scale), round(height * scale)), interpolation=cv2.INTER_AREA)
    canvas = np.zeros((473, 640, 3), np.uint8)
    y, x = 28 + (445 - resized.shape[0]) // 2, (640 - resized.shape[1]) // 2
    canvas[y : y + resized.shape[0], x : x + resized.shape[1]] = resized
    cv2.putText(canvas, label, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
    return canvas


def main():
    cv2.setNumThreads(1)
    assert not (OUT / "verification.json").exists()
    completion = read(PACKAGE / "completion.json")
    assert completion["status"] == "completed"
    assert completion["source_sha256"] == "4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a"
    assert len(completion["frames"]) == 75
    assert completion["neural_inference_performed"] is False
    assert completion["physical_gt_created"] is False
    for relative, digest in completion["artifact_sha256"].items():
        assert sha(PACKAGE / relative) == digest, relative
    input_hashes = {}
    for item in completion["input_bindings"]:
        path, digest = item["path"], item["sha256"]
        if path in input_hashes:
            assert input_hashes[path] == digest
        else:
            assert sha(path) == digest, path
            input_hashes[path] = digest
    pixels, machine = [], {}
    for frame in completion["frames"]:
        folder = PACKAGE / f"frame_{frame:07}"
        evidence = read(folder / "evidence.json")
        assert evidence["frame"] == frame
        for arm in ["source", "baseline", "current"]:
            name = "source_original.png" if arm == "source" else arm + "_proxy.png"
            expected = evidence["source_decode"] if arm == "source" else evidence["arms"][arm]["proxy_decode"]
            image = cv2.imread(str(folder / name))
            assert list(image.shape) == expected["shape"]
            assert hashlib.sha256(image.tobytes()).hexdigest() == expected["pixels_sha256"]
            pixels.append({"frame": frame, "arm": arm, **expected})
        rows = {arm: read(folder / f"{arm}_raw_frame.json") for arm in ("baseline", "current")}
        machine[str(frame)] = {}
        for arm, row in rows.items():
            assert row["f"] == frame
            decision = row.get("cd") or {}
            machine[str(frame)][arm] = {
                "raw_hypothesis": (row.get("cc") or {}).get("hypothesis"),
                "decision": decision.get("decision"),
                "reason": decision.get("reason"),
                "epoch": row["ce"],
                "person_count": len(row["p"]),
                "fresh_people": sum(p["dm"] for p in row["p"]),
                "detector_observed": row["do"],
                "shuttle": row["s"],
                "shuttle_support": row["c"],
                "association_status": (row.get("sa") or {}).get("status"),
                "previous_frame": (row.get("cc") or {}).get("previous_frame"),
                "view": row["v"],
                "calibration": row["cs"],
            }
    sets = {f"weak_{f:05}": list(range(f - 2, f + 2)) for f in WEAK}
    sets.update({f"control_{f:05}": list(range(f - 1, f + 2)) for f in CONTROLS})
    sets["g69_exit"] = list(range(27325, 27330))
    sets["g69_reacquisition_01"] = list(range(27347, 27352))
    sets["g69_reacquisition_02"] = list(range(27352, 27357))
    for name, frames in sets.items():
        rows = []
        for frame in frames:
            folder = PACKAGE / f"frame_{frame:07}"
            row = [
                tile(cv2.imread(str(folder / filename)), f"{frame} {label}")
                for filename, label in [
                    ("source_original.png", "ORIGINAL SOURCE"),
                    ("baseline_source_overlay.png", "BASELINE improved_v1"),
                    ("current_source_overlay.png", "CURRENT native2418"),
                ]
            ]
            rows.append(np.hstack(row))
        path = OUT / f"{name}.png"
        assert not path.exists()
        assert cv2.imwrite(str(path), np.vstack(rows))
    for frame in WEAK:
        row, previous = machine[str(frame)]["current"], machine[str(frame - 1)]["current"]
        assert row["raw_hypothesis"] is False and row["decision"] == "barrier"
        assert row["epoch"] == previous["epoch"] + 1
        assert row["person_count"] == row["fresh_people"] == 2
    write(OUT / "machine_readout.json", machine)
    write(
        OUT / "verification.json",
        {
            "status": "passed_closed_evidence_and_pixel_verification",
            "package_completion_sha256": sha(PACKAGE / "completion.json"),
            "sealed_artifact_count": len(completion["artifact_sha256"]),
            "recorded_input_count": len(completion["input_bindings"]),
            "unique_inputs_verified": len(input_hashes),
            "all_artifact_hashes_verified": True,
            "all_input_hashes_verified": True,
            "pixel_receipts": pixels,
            "pixel_receipt_count": len(pixels),
            "selected_frames": completion["frames"],
            "contact_sheets": {str(p.name): sha(p) for p in OUT.glob("*.png")},
            "source_shape": [1080, 1920, 3],
            "overlays_include_text_panel": [890, 1280, 3],
            "tile_policy": (
                "scale-to-fit640x445 with letterboxing and separate28px header; "
                "never stretch source16:9 to overlaypanel ratio"
            ),
            "scope_correction": (
                "Test2frames11333/13153 are extra context only; "
                "they do not validate the Test1carry/shoe cases with same numbers"
            ),
            "physical_GT": None,
            "new_video_decoding": False,
            "new_NN": False,
        },
    )
    print(
        json.dumps(
            {"status": "verified_and_rendered", "frames": 75, "pixel_receipts": len(pixels), "sheets": len(sets)}
        )
    )


if __name__ == "__main__":
    main()
