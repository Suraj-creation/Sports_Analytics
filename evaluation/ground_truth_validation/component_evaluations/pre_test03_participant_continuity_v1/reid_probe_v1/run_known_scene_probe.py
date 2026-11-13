"""Separate source-known reset intervention; original completed crop probe preserved."""
from bisect import bisect_right
import hashlib
import importlib.util
import json
from pathlib import Path
import time

import cv2
import torch

HERE = Path(__file__).resolve().parent
OUT = HERE / "known_scene_reset_v2"
ORIGINAL = HERE / "run_probe.py"

if __name__ == "__main__":
    assert not OUT.exists()
    OUT.mkdir()
    spec = importlib.util.spec_from_file_location("isolated_original_crop_probe", ORIGINAL)
    p = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(p)
    p.bind(ORIGINAL)
    p.bind(__file__)
    p.bind(HERE / "completion.json")
    assert p.digest(p.bind(p.CHECKPOINT)) == p.EXPECTED
    start = time.time()
    torch.set_num_threads(2)
    cv2.setNumThreads(1)
    p.model = p.OSNetAppearanceEmbedder(p.CHECKPOINT, device="cuda:0", max_crops=8)
    prefix = p.read(p.PREFIX / "test2_05505_06510.json")
    original_barriers = [r["frame"] for r in prefix["variants"]["after"] if r["barrier"]]
    known = [5958, 6151, 6307]
    # Explicit research intervention only: no source annotation/prefix/cache edits.
    for row in prefix["variants"]["after"]:
        if row["frame"] in known:
            row["barrier"] = True
    receipt = {"schema": "source-known-research-reset-plan:v1", "known_reset_frames": known,
               "original_detected_prefix_barriers": original_barriers,
               "scope": "Gallery reset from previously source-reviewed edited jumps; not a claim these were all acquired by production.",
               "source_evidence": [str(p.EVAL / "component_evaluations/pre_test03_perception_v1/REPORT.md"),
                                   str(p.EVAL / "component_evaluations/pre_test03_scene_foreground_v1/independent_review_6151_v1/REPORT.md")],
               "thresholds_changed": False, "weights_changed": False, "outside_gallery_learning": False}
    for path in receipt["source_evidence"]:
        p.bind(path)
    (OUT / "reset_intervention.json").write_text(json.dumps(receipt, indent=2))
    run = p.ROOT.parent / "ground-truth-validation-artifacts-20261110/test_02/improved_v1/run"
    rows, seeds, pixels, resets = p.execute_case(2, run, [[5505, 6492]], {}, prefix)
    for collection in [rows, seeds, pixels]:
        for row in collection:
            row["research_reset_segment"] = bisect_right(resets, row["frame"]) - 1
    for name, collection in [("comparison_rows.jsonl", rows), ("gallery_seed_receipts.jsonl", seeds), ("decoded_frame_receipts.jsonl", pixels)]:
        with (OUT / name).open("x") as f:
            for row in collection:
                f.write(json.dumps(row, allow_nan=False) + "\n")
    torch.cuda.synchronize()
    from collections import Counter
    summary = {"schema": "source-known-reset-osnet-crop-probe:v2", "status": "completed",
               "test1": "Unchanged original completed182target probe; no rerun or overwrite.",
               "test2_proposals": len(rows), "test2_status_counts": dict(Counter(r["appearance"]["status"] for r in rows)),
               "gallery_resets": resets, "scope": "Conditional appearance-only proposal comparisons, not production admission/identity accuracy.",
               "elapsed_s": time.time() - start, "cuda_peak_allocated_bytes": torch.cuda.max_memory_allocated(),
               "device": torch.cuda.get_device_name(0), "checkpoint_sha256": p.EXPECTED,
               "private_descriptors_saved": False, "input_sha256": p.inputs}
    for path, value in p.inputs.items():
        assert p.digest(path) == value
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    outputs = {str(q.relative_to(OUT)): p.digest(q) for q in OUT.rglob("*") if q.is_file()}
    (OUT / "completion.json").write_text(json.dumps({"status": "completed", "artifact_sha256": outputs,
                                                    "original_probe_preserved": True, "inputs_unchanged": True}, indent=2))
    print(json.dumps({k: v for k, v in summary.items() if k != "input_sha256"}), flush=True)
