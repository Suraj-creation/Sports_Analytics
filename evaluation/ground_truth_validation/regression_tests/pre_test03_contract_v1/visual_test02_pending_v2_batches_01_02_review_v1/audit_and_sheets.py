"""Read-only source-bound audit and viewing aids for Test2 pending batches01/02."""
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
HASHES = {}


def sha(path):
    path = Path(path)
    stat = path.stat()
    key = (str(path), stat.st_size, stat.st_mtime_ns)
    if key not in HASHES:
        with path.open("rb") as handle:
            HASHES[key] = hashlib.file_digest(handle, "sha256").hexdigest()
    return HASHES[key]


def save(name, value):
    with (HERE / name).open("x") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write("\n")


def concise(row):
    return {"frame": row["f"], "person_count": len(row["p"]), "persons": [
                {k: p.get(k) for k in ("t", "b", "c", "dm")} for p in row["p"]],
            "image_context_count": len(row.get("fg") or []), "detector_executed": row["do"],
            "content_epoch": row["ce"], "raw_scene": row.get("cc"), "scene_decision": row.get("cd"),
            "raw_shuttle_xy": row["s"], "raw_shuttle_support": row["c"],
            "association_status": (row.get("sa") or {}).get("association_status")}


def main():
    cv2.setNumThreads(1)
    (HERE / "sheets").mkdir(exist_ok=False)
    batches, index, sheets = [], [], []
    for batch in (1, 2):
        render = ROOT / f"visual_test02_pending_v2_batch_{batch:02d}"
        completion = json.loads((render / "completion.json").read_text())
        assert completion["status"] == "completed" and len(completion["frames"]) == 128
        assert completion["source_sha256"] == "4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a"
        assert not completion["physical_gt_created"] and not completion["metrics_recomputed"]
        for name, digest in completion["artifact_sha256"].items():
            assert sha(render / name) == digest, name
        for item in completion["input_bindings"]:
            assert sha(item["path"]) == item["sha256"], item["path"]
            if "bytes" in item:
                assert Path(item["path"]).stat().st_size == item["bytes"]
        pixels = 0
        for frame in completion["frames"]:
            folder = render / f"frame_{frame:07d}"
            evidence = json.loads((folder / "evidence.json").read_text())
            bindings = [("source_original.png", evidence["source_decode"])]
            bindings += [(f"{arm}_proxy.png", data["proxy_decode"]) for arm, data in evidence["arms"].items()]
            for file, expected in bindings:
                image = cv2.imread(str(folder / file))
                assert list(image.shape) == expected["shape"]
                assert hashlib.sha256(image.tobytes()).hexdigest() == expected["pixels_sha256"]
                pixels += 1
            index.append({"batch": batch, "frame": frame, "request": evidence["request"],
                          "source_decode": evidence["source_decode"], "evidence_path": str(folder / "evidence.json"),
                          "current": concise(json.loads((folder / "current_raw_frame.json").read_text())),
                          "baseline": concise(json.loads((folder / "baseline_raw_frame.json").read_text()))})
        batches.append({"batch": batch, "completion_path": str(render / "completion.json"),
                        "completion_sha256": sha(render / "completion.json"), "frames": completion["frames"],
                        "artifact_hashes_verified": len(completion["artifact_sha256"]),
                        "input_hashes_verified": len(completion["input_bindings"]), "pixel_bindings_verified": pixels})
        for start in range(0, len(completion["frames"]), 4):
            frames = completion["frames"][start:start + 4]
            rows = []
            for frame in frames:
                folder = render / f"frame_{frame:07d}"
                panels = []
                for label, filename in (("SOURCE", "source_resized.png"), ("CURRENT2418 raw", "current_proxy_overlay.png"),
                                        ("BASELINE raw", "baseline_proxy_overlay.png")):
                    image = cv2.imread(str(folder / filename))
                    assert image.shape[1] == 1280 and image.shape[0] >= 720
                    panel = np.zeros((296, 480, 3), np.uint8)
                    panel[26:] = cv2.resize(image[:720], (480, 270), interpolation=cv2.INTER_AREA)
                    cv2.putText(panel, f"{label} f{frame}; diagnostic / no physical GT", (4, 18), cv2.FONT_HERSHEY_SIMPLEX,
                                .38, (255, 255, 255), 1)
                    panels.append(panel)
                rows.append(np.concatenate(panels, axis=1))
            path = HERE / "sheets" / f"batch_{batch:02d}_page_{start//4+1:02d}.png"
            assert cv2.imwrite(str(path), np.concatenate(rows, axis=0))
            sheets.append({"path": str(path.relative_to(HERE)), "sha256": sha(path), "frames": frames,
                           "resize": "1280x720 image area to480x270; footer excluded; originals untouched"})
    save("verification.json", {"status": "passed", "batches": batches, "source_frames": len(index),
                               "source_proxy_pixel_bindings": sum(b["pixel_bindings_verified"] for b in batches),
                               "new_inference": False, "physical_ground_truth": None})
    save("per_frame_diagnostic_index.json", {"scope": "Saved typed model data, not physical GT", "frames": index})
    save("sheet_manifest.json", {"sheets": sheets, "total_frames": len(index), "total_sheets": len(sheets),
                                 "physical_ground_truth": None})
    print(json.dumps({"source_frames": len(index), "sheets": len(sheets), "batches": batches}))


if __name__ == "__main__":
    main()
