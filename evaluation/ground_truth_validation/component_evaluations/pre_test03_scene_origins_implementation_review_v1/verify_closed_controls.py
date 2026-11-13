"""Verify reported component-control inputs and run source-bound focused guards."""
import hashlib
import json
import os
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = HERE.parents[3]
PRODUCER = MAIN.parent / "test03-scene-overlap-20261112"
CONTROLS = HERE.parent / "pre_test03_test02_regression_diagnosis_v1/isolated_scene_prefix_v1"


def sha(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def main():
    receipt_path = CONTROLS / "layout_receipt_v3.json"
    receipt = json.loads(receipt_path.read_text())
    assert receipt["fresh_RFD_forwards"] == 0 and not receipt["full_NN_pipeline_rerun"]
    assert receipt["reused_actual_source_crop_model_bound_queries"] == 6
    for path, digest in receipt["input_sha256"].items():
        assert sha(path) == digest, path
    controls = json.loads((CONTROLS / "layout_results_v3.json").read_text())
    expected = {2928: "barrier", 11082: "barrier", 22416: "barrier", 23279: "barrier",
                7703: "no_barrier", 23639: "no_barrier"}
    assert {row["frame"]: row["decision"]["decision"] for row in controls} == expected
    evidence = MAIN / "evaluation/ground_truth_validation/regression_tests/pre_test03_contract_v1/visual_test02_pending_v2_batch_01/frame_0002928/evidence.json"
    pixels = json.loads(evidence.read_text())
    basis = {"evidence_path": str(evidence), "evidence_sha256": sha(evidence),
             "original_source_shape": pixels["source_decode"]["shape"],
             "canonical_proxy_shape": pixels["arms"]["current"]["proxy_decode"]["shape"],
             "observer_source_frame_size": "canonical input pixels;1280x720 in these runs, not original1920x1080",
             "analysis_frame_size": "observer measurement raster;480x270 default"}
    test_names = ["test_scene_feature_origins_v5.py", "test_scene_feature_origin_codec_v24.py",
                  "test_scene_acquisition_v4.py", "test_scene_acquisition_codec_v23.py",
                  "test_scene_witness_v3.py", "test_scene_witness_layout.py"]
    files = list(receipt["input_sha256"])
    source_paths = [PRODUCER / "sports/badminton/src/bai_badminton/perception/scene_change.py",
                    PRODUCER / "sports/badminton/src/bai_badminton/perception/content.py",
                    PRODUCER / "sports/badminton/src/bai_badminton/perception/components.py",
                    PRODUCER / "sports/badminton/src/bai_badminton/plugin.py"]
    tests = [PRODUCER / "sports/badminton/tests" / name for name in test_names]
    before = {str(p): sha(p) for p in [*source_paths, *tests]}
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = ":".join(str(PRODUCER / p) for p in
                                  ["sports/badminton/src", "engine/src", "sports/badminton/tests"])
    command = [str(MAIN / ".venv/bin/python"), "-m", "pytest", "-q", "-p", "no:cacheprovider", *map(str, tests)]
    with (HERE / "focused_tests_source_bound.log").open("x") as output:
        result = subprocess.run(command, cwd=PRODUCER, env=env, stdout=output, stderr=subprocess.STDOUT, check=False)
    after = {p: sha(p) for p in before}
    assert before == after, "sources or tests changed while focused checks ran"
    assert result.returncode == 0
    data = {"status": "passed_bounded_component_and_synthetic_guards", "command": command,
            "cwd": str(PRODUCER), "source_and_tests_before_after_sha256": before,
            "source_and_tests_unchanged": True, "controls_receipt_path": str(receipt_path),
            "controls_receipt_sha256": sha(receipt_path), "controls_results_sha256": sha(CONTROLS / "layout_results_v3.json"),
            "verified_control_inputs": len(files), "controls": expected, "coordinate_basis": basis,
            "new_neural_inference": False, "physical_ground_truth": None}
    (HERE / "bounded_controls_verification.json").write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps({"status": "passed", "verified_inputs": len(files), "coordinate_basis": basis}))


if __name__ == "__main__":
    main()
