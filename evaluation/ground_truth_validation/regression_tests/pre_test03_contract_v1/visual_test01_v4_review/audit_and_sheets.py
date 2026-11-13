"""Read-only audit and derived diagnostic sheets for the closed Test1 v4 render."""
import hashlib
import json
import re
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
RENDER = HERE.parent / "visual_test01_v4"


def sha(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def save(name, value):
    with (HERE / name).open("x") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write("\n")


def main():
    completed = json.loads((RENDER / "completion.json").read_text())
    assert completed["status"] == "completed" and len(completed["frames"]) == 88
    assert not completed["physical_gt_created"] and not completed["metrics_recomputed"]
    for rel, digest in completed["artifact_sha256"].items():
        assert sha(RENDER / rel) == digest, rel
    for item in completed["input_bindings"]:
        path = Path(item["path"])
        assert sha(path) == item["sha256"], path
        if "bytes" in item:
            assert path.stat().st_size == item["bytes"]
    assert sha(RENDER / "executed_tool.py.source") == completed["executed_tool_sha256"]
    pixel_receipts = []
    for frame in completed["frames"]:
        directory = RENDER / f"frame_{frame:07d}"
        evidence = json.loads((directory / "evidence.json").read_text())
        bindings = [("source_original.png", evidence["source_decode"])]
        bindings += [(f"{arm}_proxy.png", value["proxy_decode"]) for arm, value in evidence["arms"].items()]
        for filename, expected in bindings:
            image = cv2.imread(str(directory / filename))
            assert list(image.shape) == expected["shape"]
            assert hashlib.sha256(image.tobytes()).hexdigest() == expected["pixels_sha256"]
            pixel_receipts.append({"frame": frame, "file": filename, "pixels_sha256": expected["pixels_sha256"]})
    links = []
    for href in re.findall(r'\]\(([^)]+)\)', (RENDER / "index.md").read_text()):
        if not href.startswith(("https://", "http://")):
            path = (RENDER / href.split("#", 1)[0]).resolve()
            assert path.exists(), path
            links.append(str(path))
    save("verification.json", {"status": "passed", "render_completion_sha256": sha(RENDER / "completion.json"),
         "output_hashes_verified": len(completed["artifact_sha256"]), "input_hashes_verified": len(completed["input_bindings"]),
         "original_source_and_proxy_pixel_bindings_verified": pixel_receipts, "local_index_links_exist": len(links),
         "source_sha256": completed["source_sha256"], "frames": completed["frames"], "new_inference": False,
         "physical_ground_truth": None})
    groups = {}
    coverage = [(752, 753, 800), (3412, 3413, 3449), (6364, 6365, 6381), (7800, 7801, 7805),
                (7811, 7812, 7856), (8086, 8087, 8105), (14102, 14103, 14113)]
    for i, frames in enumerate(coverage, 1):
        groups[f"coverage_{i:02d}"] = frames
    cuts = [2195, 4837, 7503, 7857, 8106, 10023, 10604, 10770, 11903, 15579, 15985, 16446, 17069]
    for frame in cuts:
        groups[f"cut_{frame:05d}"] = (frame - 1, frame)
    themes = {"contacts": [1438, 3015, 3558, 6471, 8108, 10676], "classes": [3540, 6456, 16600],
              "actors": [1522, 1534, 1654, 5459, 16600],
              "outliers": [11331, 11332, 11333, 13152, 13153, 13154, 13466, 13467, 13468, 13469,
                           16551, 16552, 16553, 14561, 7845, 7846, 7847, 1340, 3667, 5076, 5472]}
    for name, frames in themes.items():
        for i in range(0, len(frames), 2):
            groups[f"{name}_{i//2+1:02d}"] = frames[i:i+2]
    used = {frame for frames in groups.values() for frame in frames}
    other = sorted(set(completed["frames"]) - used)
    for i in range(0, len(other), 2):
        groups[f"other_{i//2+1:02d}"] = other[i:i+2]
    (HERE / "sheets").mkdir(exist_ok=False)
    sheet_receipts = []
    for name, frames in groups.items():
        rows = []
        for frame in frames:
            directory = RENDER / f"frame_{frame:07d}"
            row = []
            for label, file in [("SOURCE", "source_resized.png"), ("CURRENT 2418 raw", "current_proxy_overlay.png"),
                                ("ORIGINAL NN raw baseline", "baseline_proxy_overlay.png")]:
                image = cv2.imread(str(directory / file))
                image = cv2.resize(image, (640, 360), interpolation=cv2.INTER_AREA)
                panel = np.zeros((394, 640, 3), np.uint8)
                panel[34:] = image
                cv2.putText(panel, f"{label} f{frame}: diagnostic / no physical GT", (5, 22), cv2.FONT_HERSHEY_SIMPLEX, .46, (255, 255, 255), 1)
                row.append(panel)
            rows.append(np.concatenate(row, axis=1))
        path = HERE / "sheets" / f"{name}.png"
        assert cv2.imwrite(str(path), np.concatenate(rows, axis=0))
        sheet_receipts.append({"path": str(path.relative_to(HERE)), "sha256": sha(path), "frames": list(frames),
                               "purpose": "derived resized viewing aid; original source/render untouched; no GT annotations"})
    save("sheet_manifest.json", {"sheets": sheet_receipts, "union_frames": sorted({f for g in groups.values() for f in g}),
                                 "all88_included": used | set(other) == set(completed["frames"]), "physical_ground_truth": None})
    print(json.dumps({"outputs_verified": len(completed["artifact_sha256"]), "inputs_verified": len(completed["input_bindings"]),
                      "pixels_verified": len(pixel_receipts), "sheets": len(sheet_receipts), "frames": len(completed["frames"])}))


if __name__ == "__main__":
    main()
