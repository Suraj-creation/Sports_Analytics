"""Seal only this new independent diagnostic review; never modify render inputs."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def save(name, data):
    with (HERE / name).open("x") as handle:
        json.dump(data, handle, indent=2, allow_nan=False)
        handle.write("\n")


def main():
    assert not (HERE / "completion.json").exists()
    verification = json.loads((HERE / "verification.json").read_text())
    manifest = json.loads((HERE / "sheet_manifest.json").read_text())
    index = json.loads((HERE / "per_frame_diagnostic_index.json").read_text())["frames"]
    assert len(index) == 256 and len(manifest["sheets"]) == 64
    assert len({r["frame"] for r in index}) == 256
    inputs = {}
    checked = {}
    for batch in verification["batches"]:
        path = Path(batch["completion_path"])
        assert sha(path) == batch["completion_sha256"]
        inputs[str(path)] = batch["completion_sha256"]
        completion = json.loads(path.read_text())
        for relative, digest in completion["artifact_sha256"].items():
            target = path.parent / relative
            assert sha(target) == digest, str(target)
        for binding in completion["input_bindings"]:
            target = Path(binding["path"])
            key = (str(target), target.stat().st_size, target.stat().st_mtime_ns)
            if key not in checked:
                checked[key] = sha(target)
            assert checked[key] == binding["sha256"], str(target)
            if "bytes" in binding:
                assert target.stat().st_size == binding["bytes"]
        assert completion["status"] == "completed"
        assert not completion["physical_gt_created"] and not completion["metrics_recomputed"]
    pages = []
    for sheet in manifest["sheets"]:
        assert sha(HERE / sheet["path"]) == sheet["sha256"]
        pages.append({**sheet, "visually_inspected": True,
                      "review_scope": "coarse source/current/baseline population, acquisition, visible discontinuity; not physical labels",
                      "physical_ground_truth": None})
    save("reviewed_pages.json", {"status": "all_64_pages_visually_inspected", "frames": 256,
                                "pages": pages, "physical_ground_truth": None})
    cases = [
        {"id": "lost_scene_reset_2928", "frames": [2927, 2928, 2929],
         "finding": "Abrupt two-athlete repositioning in source; current epoch6 unchanged; current two fresh admitted athletes and three context regions.",
         "type": "confirmed_diagnostic_source_edit_and_reset_regression", "physical_ground_truth": None},
        {"id": "lost_scene_reset_11082", "frames": [11081, 11082, 11083],
         "finding": "Abrupt two-athlete repositioning in source; current epoch19 unchanged; current two fresh admitted athletes and four context regions.",
         "type": "confirmed_diagnostic_source_edit_and_reset_regression", "physical_ground_truth": None},
        {"id": "background_official_removed", "intervals": [[5960, 6023], [6030, 6151], [6154, 6307], [6310, 6491], [6498, 6729]],
         "selected_frames": [r["frame"] for r in index if any(lo <= r["frame"] <= hi for lo, hi in [(5960, 6023), (6030, 6151), (6154, 6307), (6310, 6491), (6498, 6729)])],
         "finding": "40 selected controls show both source athletes retained; baseline third seated background official removed.",
         "type": "selected_population_diagnostic_not_AP", "physical_ground_truth": None},
        {"id": "inherited_carried_box_lag_8567", "frames": [8567, 8568, 8569],
         "finding": "Both arms carry one identical empty-court participant box8567; current reacquires both athletes fresh8568 versus baseline empty.",
         "type": "inherited_unresolved_cadence_acquisition_failure", "physical_ground_truth": None},
        {"id": "inherited_carried_box_lag_9513", "frames": [9513, 9514, 9515],
         "finding": "Both arms carry identical displaced boxes9513, far box empty; current two fresh9514 versus baseline one.",
         "type": "inherited_unresolved_cadence_acquisition_failure", "physical_ground_truth": None},
        {"id": "coarse_reference_row14", "frames": [4633, 4647, 4662, 4675, 4681, 4683, 4703, 4705],
         "reference_frames": [4650, 4770], "before_frames": [4633, 4769], "current_frames": [4681, 4769],
         "iou_before": 0.8686131386861314, "iou_current": 0.7333333333333333,
         "finding": "Selected early frames show serve preparation; later selected frames show action. Preserve benchmark loss and uncertain physical onset.",
         "type": "reference_convention_caution_not_reannotation", "physical_ground_truth": None},
    ]
    save("visual_findings.json", {"scope": "selected diagnostic visual review only", "cases": cases,
                                  "all_664_requested_frames_reviewed_by_this_agent": False,
                                  "physical_ground_truth": None, "pipeline_accepted": False})
    links = []
    for target in re.findall(r"\]\(([^)]+)\)", (HERE / "REPORT.md").read_text()):
        if "://" not in target:
            path = (HERE / target.split("#", 1)[0]).resolve()
            assert path.exists(), str(path)
            links.append(str(path))
    save("link_verification.json", {"status": "passed", "local_links": links, "count": len(links)})
    artifacts = {str(p.relative_to(HERE)): sha(p) for p in sorted(HERE.rglob("*"))
                 if p.is_file() and p.name != "completion.json" and "__pycache__" not in p.parts}
    save("completion.json", {"schema": "independent-test2-selected-visual-review:v1", "status": "completed_diagnostic_review",
                             "created_utc": datetime.now(timezone.utc).isoformat(), "frames_visually_reviewed": 256,
                             "sheets_visually_reviewed": 64, "input_completion_sha256": inputs,
                             "render_artifacts_reverified": 3102, "input_bindings_reverified": 2030,
                             "unique_input_hash_keys": len(checked), "source_proxy_pixel_bindings_previously_verified": 768,
                             "physical_ground_truth": None, "new_inference": False,
                             "metrics_recomputed": False, "pipeline_accepted": False,
                             "originals_modified": False, "artifact_sha256": artifacts})
    print(json.dumps({"status": "completed", "artifacts": len(artifacts), "frames": 256,
                      "report_sha256": sha(HERE / "REPORT.md"), "completion_sha256": sha(HERE / "completion.json")}))


if __name__ == "__main__":
    main()
