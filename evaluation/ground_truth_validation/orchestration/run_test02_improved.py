"""Fresh complete Test2 post-fix inference and immutable before/after evidence.

Invoke only after root applies the reviewed fix and writes its regression and
baseline-protection receipt. No automatic Test3 advancement or media cleanup.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
WORK = ROOT / "evaluation/ground_truth_validation"
TEST = WORK / "test_02"
BASE = ROOT.parent / "ground-truth-validation-artifacts-20261110/test_02/baseline_v1"
ART = BASE.parent / "improved_v1"
VIDEO = TEST / "inputs/Test2_Full_Rev.mp4"
FIX = TEST / "fixes/applied_fix_receipt.json"
BINDING = TEST / "diagnostics/annotation_visual_review/diagnostic_coordinate_binding.json"
PROFILE = ROOT / "config/profiles/experimental-pipeline-repair-v1.yaml"
PYTHON = ROOT / ".venv/bin/python"
GIT = shutil.which("git") or "/usr/bin/git"
NVIDIA_SMI = shutil.which("nvidia-smi") or "/usr/bin/nvidia-smi"
REPORT = WORK / "reports/test_02_improved_v1"
OWNED_ART = False
SOURCE_SHA = "4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a"
N = 29296
REFERENCE_NAMES = {"Test2_Full.csv", "Test2_Full_rally.csv", "win_predictions.csv"}
HELPERS = (
    "research/production_external_stress.py",
    "research/normal_timestamp_audit.py",
    "research/pipeline_repair_run_analysis.py",
    "research/pipeline_repair_evaluation.py",
    "research/production_external_semantic_replay.py",
    "research/test2_failure_package.py",
    "research/test2_causal_analysis.py",
    "evaluation/ground_truth_validation/orchestration/evaluate_test02_components.py",
    "evaluation/ground_truth_validation/orchestration/evaluate_test01_components.py",
    "evaluation/ground_truth_validation/orchestration/export_completed_analytics.py",
    "evaluation/ground_truth_validation/orchestration/export_test02_heatmaps.py",
    "evaluation/ground_truth_validation/orchestration/build_test02_matrix.py",
)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def state(stage, **details):
    path = TEST / "orchestration/improved_status.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(
            {
                "test": 2,
                "stage": stage,
                "epoch": time.time(),
                "details": details,
                "automatic_test3": False,
                "automatic_cleanup": False,
            },
            indent=2,
        )
        + "\n"
    )
    temporary.replace(path)
    print(stage, flush=True)


def file_inventory(directory):
    return {str(p.relative_to(directory)): sha(p) for p in sorted(directory.rglob("*")) if p.is_file()}


def component_path(root):
    path = root / "bound_reference_diagnostics/component_reference_metrics.json"
    if not path.is_file():
        raise ValueError("Coordinate-bound complete Test2 reference metrics are required")
    return path


def preflight():
    """Read-only admission; no output directory, inference or baseline re-evaluation."""
    if ART.exists() or REPORT.exists() or (TEST / "improved_v1").exists() or (TEST / "improved_v1").is_symlink():
        raise ValueError("Fresh improved output/link must not exist; retain failed attempts without overwriting")
    fix = read(FIX)
    if fix.get("regressions_passed") is not True or fix.get("baseline_protected") is not True:
        raise ValueError("Reviewed main integration requires passed regressions and explicit protected baseline")
    production = fix.get("production_files")
    if not isinstance(production, dict) or not production:
        raise ValueError("Applied fix receipt must enumerate exact absolute production source hashes")
    completion = read(BASE / "baseline_completion.json")
    diagnostics = read(BASE / "all_reference_diagnostics_completion.json")
    if (
        completion.get("status") != "completed_fresh_Test2_baseline_and_diagnostics"
        or completion.get("frames") != N
        or completion.get("annotations_unchanged") is not True
    ):
        raise ValueError("Fresh full Test2 baseline completion required")
    if (
        diagnostics.get("status") != "full_Test2_baseline_component_metrics_and_source_diagnostics_complete"
        or diagnostics.get("original_annotations_unchanged") is not True
    ):
        raise ValueError("Complete Test2 annotation/diagnostic baseline gate required")
    plan = read(BASE / "protocol/plan.json")
    old_files = plan["source_files_sha256"]
    for path, values in production.items():
        source = Path(path)
        if not source.is_absolute() or ROOT not in source.parents or not source.is_file():
            raise ValueError("Fix receipt source path is not an existing absolute repository file")
        relative = source.relative_to(ROOT)
        if not str(relative).startswith(("sports/badminton/src/", "engine/src/")):
            raise ValueError("Fix receipt must identify production sources")
        if "/perception/" in str(relative) or relative.name == "perception_types.py":
            raise ValueError(
                "This one-variable run permits semantic repairs only; perception changes require separate review"
            )
        if values.get("before_sha256") != old_files.get(path):
            raise ValueError("Fix preimage differs from preserved fresh Test2 baseline: " + path)
        if sha(source) != values.get("after_sha256"):
            raise ValueError("Applied main source differs from reviewed fix receipt: " + path)
    # Unlisted changes to any formerly frozen executor/production source are refused.
    for path, expected in old_files.items():
        current = production.get(path, {}).get("after_sha256", expected)
        if sha(path) != current:
            raise ValueError("Undeclared frozen-source change: " + path)
    current_core = {
        str(p) for directory in (ROOT / "engine/src", ROOT / "sports/badminton/src") for p in directory.rglob("*.py")
    }
    if current_core - set(old_files) - set(production):
        raise ValueError("New production sources are not declared in the reviewed fix receipt")
    if sha(VIDEO) != SOURCE_SHA or read(TEST / "inputs/download_verification.json")["sha256"] != SOURCE_SHA:
        raise ValueError("Exact original Test2 video pairing required")
    old_annotations = read(BASE / "annotation_hashes_before.json")
    actual_annotations = {str(p): sha(p) for p in sorted((ROOT / "Part2/dataset/Test2_Full").iterdir()) if p.is_file()}
    if len(actual_annotations) != 7 or actual_annotations != old_annotations:
        raise ValueError("All seven original Test2 annotations must match the preserved baseline")
    for path in (PROFILE, ROOT / "models/manifest.yaml", ROOT / "models/cache/lock.json"):
        expected = plan["input_files_sha256"].get(str(path))
        if expected is None or sha(path) != expected:
            raise ValueError("Numerical profile/model manifest/lock changed: " + str(path))
    if sha(PROFILE) != plan["profile_source_sha256"]:
        raise ValueError("Baseline profile-source hash mismatch")
    if not BINDING.is_file():
        raise ValueError("Source-bound Test2 coordinate review certificate required")
    certificate = read(BINDING)
    if certificate.get("source_sha256") != SOURCE_SHA:
        raise ValueError("Coordinate certificate belongs to another video")
    old_components = read(component_path(BASE))
    if (
        old_components.get("status") != "completed_readonly_component_reference_diagnostics"
        or old_components.get("test") != 2
        or set(old_components["interval_reference_comparisons"]) != REFERENCE_NAMES
    ):
        raise ValueError("Preserved baseline must contain exactly the three Test2 reference comparisons")
    baseline_report = Path(diagnostics["report"])
    if not baseline_report.is_file() or not baseline_report.with_suffix(".json").is_file():
        raise ValueError("Preserved baseline Markdown and machine-readable matrix are required")
    inference, parent = read(BASE / "run/inference.json"), read(BASE / "run.executor.json")
    if (
        inference.get("status") != "completed"
        or inference.get("cached_perception_used") is not False
        or inference.get("frames_processed") != N
        or inference.get("frontier_frame") != N - 1
        or parent.get("status") != "completed"
        or parent.get("worker_exit_code") != 0
    ):
        raise ValueError("Preserved baseline worker/parent must prove complete fresh inference")
    missing = [name for name in HELPERS if not (ROOT / name).is_file()]
    if missing:
        raise ValueError("Required reviewed helper missing: " + ", ".join(missing))
    engine_spec = importlib.util.find_spec("bai_badminton.engine")
    expected_engine = ROOT / "sports/badminton/src/bai_badminton/engine.py"
    if engine_spec is None or engine_spec.origin is None or Path(engine_spec.origin).resolve() != expected_engine:
        raise ValueError("Runtime must import the main integrated pipeline, not an isolated or old installed copy")
    return {
        "fix": fix,
        "plan": plan,
        "annotations": actual_annotations,
        "baseline_components": old_components,
        "baseline_report": str(baseline_report),
        "binding_sha256": sha(BINDING),
        "engine_import_source": engine_spec.origin,
    }


def call(args, label):
    command = [str(PYTHON), *map(str, args)]
    started = time.monotonic()
    dump(ART / (label + ".command.json"), {"argv": command, "started_epoch": time.time()})
    with (ART / (label + ".log")).open("x") as stream:
        # All argv entries are constructed by this fixed runner; no shell is used.
        result = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)  # noqa: S603
    dump(ART / (label + ".result.json"), {"exit_code": result.returncode, "elapsed_s": time.monotonic() - started})
    if result.returncode:
        raise RuntimeError(f"{label} failed exit{result.returncode}; all original and partial artifacts preserved")


def freeze_helpers():
    hashes = {}
    for source in [Path(__file__).resolve(), *(ROOT / name for name in HELPERS)]:
        destination = ART / "executed_helpers" / source.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
        hashes[str(source)] = sha(source)
    dump(ART / "helper_sources.json", hashes)
    return hashes


def scalar_values(value, prefix=""):
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            result.update(scalar_values(item, f"{prefix}.{key}" if prefix else key))
        return result
    if isinstance(value, list):
        return {}
    return {prefix: value}


def compare_saved_references(before, after):
    """Compare saved matrices only; never run current code against old baseline."""
    if (
        set(before["interval_reference_comparisons"]) != REFERENCE_NAMES
        or set(after["interval_reference_comparisons"]) != REFERENCE_NAMES
    ):
        raise ValueError("Before/after must contain exactly three Test2 reference families")
    comparisons = {}
    for name in sorted(REFERENCE_NAMES):
        old, new = before["interval_reference_comparisons"][name], after["interval_reference_comparisons"][name]
        if old["role"] != new["role"] or old["metrics"]["matching_policy"] != new["metrics"]["matching_policy"]:
            raise ValueError("Reference interpretation/matching changed during comparison")
        a, b = scalar_values(old["metrics"]), scalar_values(new["metrics"])
        deltas = {
            key: b[key] - value
            for key, value in a.items()
            if type(value) in (int, float) and type(b.get(key)) in (int, float)
        }
        comparisons[name] = {
            "role": old["role"],
            "baseline": old["metrics"],
            "fresh_postfix": new["metrics"],
            "metrics_equal": old["metrics"] == new["metrics"],
            "numeric_deltas": deltas,
        }
    return comparisons


def model_identity(analysis):
    return {
        group: {
            name: {k: value for k, value in record.items() if k in ("sha256", "status")}
            for name, record in rows.items()
        }
        for group, rows in analysis["models_verified_during_analysis"].items()
    }


def main():
    global OWNED_ART
    os.chdir(ROOT)
    admitted = preflight()
    baseline_hashes = file_inventory(BASE)
    baseline_report_hashes = file_inventory(Path(admitted["baseline_report"]).parent)
    ART.mkdir(parents=True, exist_ok=False)
    OWNED_ART = True
    (TEST / "improved_v1").symlink_to(ART, target_is_directory=True)
    helpers = freeze_helpers()
    dump(ART / "applied_fix_receipt.json", admitted["fix"])
    dump(ART / "annotation_hashes_before.json", admitted["annotations"])
    dump(ART / "baseline_preservation_before.json", baseline_hashes)
    dump(ART / "baseline_report_preservation_before.json", baseline_report_hashes)
    dump(ART / "input_pairing.json", read(TEST / "inputs/download_verification.json"))
    from research.validate_real_video_runtime import package_versions

    dump(
        ART / "environment.json",
        {
            "packages": package_versions(),
            "git_commit": subprocess.check_output([GIT, "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),  # noqa: S603
            "git_status": subprocess.check_output([GIT, "status", "--short"], cwd=ROOT, text=True),  # noqa: S603
            "gpu": subprocess.check_output(  # noqa: S603 -- resolved local executable and fixed read-only argv
                [NVIDIA_SMI, "--query-gpu=index,name,uuid,driver_version", "--format=csv"], text=True
            ),
            "runtime_env_source": str(ROOT.parent / "gpu-env.sh"),
            "engine_import_source": admitted["engine_import_source"],
        },
    )
    (ART / "source_changes.patch").write_bytes(
        subprocess.check_output(  # noqa: S603 -- fixed Git argv and repository-owned path
            [
                GIT,
                "diff",
                "--binary",
                "HEAD",
                "--",
                "engine/src",
                "sports/badminton/src",
                str(PROFILE.relative_to(ROOT)),
                "models/manifest.yaml",
            ],
            cwd=ROOT,
        )
    )
    state("preparing fresh full Test2 post-fix upload; protected baseline unchanged")
    call(
        [
            ROOT / "research/production_external_stress.py",
            "prepare-upload",
            "--case",
            "test2",
            "--video",
            VIDEO,
            "--profile-source",
            PROFILE,
            "--output",
            ART / "protocol",
        ],
        "prepare",
    )
    plan = read(ART / "protocol/plan.json")
    if (
        plan["cases"]["test2"]["frames"] != N
        or plan["profile_source_sha256"] != admitted["plan"]["profile_source_sha256"]
    ):
        raise ValueError("Fresh Test2 frame/profile pairing changed")
    if yaml.safe_load((ART / "protocol/profiles/experiment.yaml").read_text()) != yaml.safe_load(
        (BASE / "protocol/profiles/experiment.yaml").read_text()
    ):
        raise ValueError("Prepared numerical/diagnostic profile differs from baseline")
    state("fresh full Test2 post-fix inference on physical GPU1", frames=N)
    call(
        [
            ROOT / "research/production_external_stress.py",
            "run",
            "--case",
            "test2",
            "--plan",
            ART / "protocol/plan.json",
            "--output",
            ART / "run",
            "--gpu-index",
            "1",
        ],
        "inference",
    )
    state("verifying complete post-fix Test2 timestamps, models and component evidence")
    call(
        [ROOT / "research/normal_timestamp_audit.py", "--run", ART / "run", "--output", ART / "timestamps"],
        "timestamps",
    )
    call(
        [ROOT / "research/pipeline_repair_run_analysis.py", "--run", ART / "run", "--output", ART / "analysis"],
        "analysis",
    )
    old_analysis, new_analysis = (
        read(BASE / "analysis/technical_analysis.json"),
        read(ART / "analysis/technical_analysis.json"),
    )
    if model_identity(old_analysis) != model_identity(new_analysis):
        raise ValueError("Actual verified model/checkpoint identity changed")
    call(
        [
            WORK / "orchestration/evaluate_test02_components.py",
            "--run",
            ART / "run",
            "--output",
            ART / "all_reference_components",
        ],
        "components",
    )
    call(
        [
            WORK / "orchestration/evaluate_test02_components.py",
            "--run",
            ART / "run",
            "--output",
            ART / "bound_reference_diagnostics",
            "--coordinate-binding",
            BINDING,
        ],
        "bound_reference_diagnostics",
    )
    call(
        [
            ROOT / "research/pipeline_repair_evaluation.py",
            "--run",
            ART / "run",
            "--session",
            "UPLOADTEST2",
            "--reference",
            ROOT / "Part2/dataset/Test2_Full/Test2_Full_rally.csv",
            "--output",
            ART / "rally_reference_evaluation",
        ],
        "rally_evaluation",
    )
    call(
        [
            WORK / "orchestration/export_completed_analytics.py",
            "--run",
            ART / "run",
            "--output",
            ART / "downstream_exports",
        ],
        "downstream_exports",
    )
    state("building strict own-run post-fix parity and source-synchronized diagnostics")
    call(
        [
            ROOT / "research/production_external_semantic_replay.py",
            "--run",
            ART / "run",
            "--session",
            "UPLOADTEST2",
            "--output",
            ART / "diagnostic_replay",
            "--trace-ranges",
            "[[0,29296]]",
            "--focus",
            "",
        ],
        "diagnostic_replay",
    )
    replay = read(ART / "diagnostic_replay/replay_manifest.json")
    if (
        replay.get("baseline_parity") is not True
        or replay.get("source_intervention") is not None
        or replay.get("geometry_bracket") is not False
        or replay.get("contact_motion_reliability") is not False
        or replay.get("frames") != N
        or replay.get("trace_step_count") != N
    ):
        raise ValueError("Fresh post-fix own-run replay must prove full strict parity without intervention")
    call(
        [
            ROOT / "research/test2_failure_package.py",
            "--run",
            ART / "run",
            "--session",
            "UPLOADTEST2",
            "--replay",
            ART / "diagnostic_replay",
            "--source",
            VIDEO,
            "--source-pts",
            ART / "timestamps/source_frame_pts.csv",
            "--evaluation",
            ART / "rally_reference_evaluation",
            "--output",
            ART / "visual_failure_package",
        ],
        "visual_failure_package",
    )
    call(
        [
            ROOT / "research/test2_causal_analysis.py",
            "--run",
            ART / "run",
            "--replay",
            ART / "diagnostic_replay",
            "--evaluation",
            ART / "rally_reference_evaluation",
            "--output",
            ART / "causal_analysis",
        ],
        "causal_analysis",
    )
    call(
        [WORK / "orchestration/export_test02_heatmaps.py", "--artifact-root", ART, "--output", ART / "heatmap_exports"],
        "heatmaps",
    )
    after = read(component_path(ART))
    comparison = {
        "schema": "fresh_Test2_before_after:v1",
        "test": 2,
        "baseline_source": str(BASE),
        "fresh_postfix_source": str(ART),
        "comparison_scope": (
            "Actual full fresh pipeline before/after; diagnostic own-cache replay is separate and not fresh inference"
        ),
        "interval_references": compare_saved_references(admitted["baseline_components"], after),
        "baseline_component_matrix_sha256": sha(component_path(BASE)),
        "fresh_postfix_component_matrix_sha256": sha(component_path(ART)),
        "prediction_csv_bytes_equal": (BASE / "run/predicted_rallies.csv").read_bytes()
        == (ART / "run/predicted_rallies.csv").read_bytes(),
        "baseline_event_coverage": admitted["baseline_components"]["event_coverage"],
        "fresh_postfix_event_coverage": after["event_coverage"],
        "baseline_outcome_coverage": admitted["baseline_components"]["outcome_and_stroke_coverage"],
        "fresh_postfix_outcome_coverage": after["outcome_and_stroke_coverage"],
        "model_checkpoint_identity_equal": True,
        "profile_equal": True,
        "independent_physical_accuracy_gain_claimed": False,
        "complete_component_matrix_comparison": str(ART / "before_after_component_matrix_comparison.json"),
    }
    dump(ART / "before_after_comparison.json", comparison)
    if file_inventory(BASE) != baseline_hashes:
        raise ValueError("Protected Test2 baseline changed during post-fix evaluation")
    if (
        any(sha(path) != expected for path, expected in admitted["annotations"].items())
        or sha(BINDING) != admitted["binding_sha256"]
    ):
        raise ValueError("Original annotation or coordinate contract changed")
    if any(sha(path) != expected for path, expected in helpers.items()):
        raise ValueError("Executed helper changed during evaluation")
    dump(
        ART / "improved_completion.json",
        {
            "status": "completed_fresh_Test2_improved_and_diagnostics",
            "frames": N,
            "annotations_unchanged": True,
            "baseline_unchanged": True,
            "models_unchanged": True,
            "profile_unchanged": True,
            "fresh_neural_inference_performed": True,
            "own_run_semantic_parity": True,
            "test3_started": False,
        },
    )
    report = REPORT
    call(
        [WORK / "orchestration/build_test02_matrix.py", "--artifact-root", ART, "--output", report], "evaluation_matrix"
    )
    baseline_matrix_path = Path(admitted["baseline_report"]).with_suffix(".json")
    baseline_matrix, improved_matrix = read(baseline_matrix_path), read(report / "matrix.json")
    sections = (
        "interval_references",
        "point_diagnostics",
        "court_diagnostic",
        "component_coverage",
        "event_coverage",
        "track_coverage",
        "outcome_and_stroke_coverage",
        "ocr_coverage",
        "runtime_resources",
        "stage_status",
        "downstream",
        "unavailable_metrics",
    )
    dump(
        ART / "before_after_component_matrix_comparison.json",
        {
            "scope": "Read-only comparison of preserved baseline matrix and newly completed fresh post-fix matrix",
            "baseline_matrix": str(baseline_matrix_path),
            "baseline_matrix_sha256": sha(baseline_matrix_path),
            "fresh_postfix_matrix": str(report / "matrix.json"),
            "fresh_postfix_matrix_sha256": sha(report / "matrix.json"),
            "baseline_re_evaluated_with_current_code": False,
            "physical_accuracy_gain_claimed": False,
            "sections": {
                name: {"baseline": baseline_matrix[name], "fresh_postfix": improved_matrix[name]} for name in sections
            },
        },
    )
    if (
        file_inventory(BASE) != baseline_hashes
        or file_inventory(Path(admitted["baseline_report"]).parent) != baseline_report_hashes
        or any(sha(p) != h for p, h in admitted["annotations"].items())
        or any(sha(p) != h for p, h in helpers.items())
        or sha(VIDEO) != SOURCE_SHA
    ):
        raise ValueError("Protected baseline/report/annotation/helper/video changed during final reporting")
    dump(
        ART / "artifact_verification.json",
        {
            "status": "completed",
            "artifacts_sha256": file_inventory(ART),
            "report_sha256": file_inventory(report),
            "baseline_unchanged": file_inventory(BASE) == baseline_hashes,
            "original_annotations_unchanged": all(sha(p) == h for p, h in admitted["annotations"].items()),
        },
    )
    dump(
        ART / "all_reference_diagnostics_completion.json",
        {
            "status": "full_Test2_improved_component_metrics_and_source_diagnostics_complete",
            "report": str(report / "matrix.md"),
            "comparison": str(ART / "before_after_comparison.json"),
            "original_annotations_unchanged": True,
            "baseline_unchanged": True,
            "next": (
                "Root must review measured changes and Test1 regression before completion/cleanup; no automatic Test3"
            ),
        },
    )
    state(
        "Test2 fresh post-fix matrix and before/after evidence complete; root/Test1 regression review remains",
        report=str(report / "matrix.md"),
    )


def record_failure(error):
    """Write only within this invocation's newly reserved artifact directory."""
    if OWNED_ART and ART.is_dir():
        path = ART / "failure.json"
        if not path.exists():
            dump(
                path,
                {
                    "status": "failed",
                    "error": str(error),
                    "epoch": time.time(),
                    "artifacts_preserved": True,
                    "test3_started": False,
                    "media_deleted": False,
                },
            )
    state("Test2 fresh post-fix run failed; all source/baseline/partial artifacts preserved", error=str(error))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        traceback.print_exc()
        record_failure(error)
        sys.exit(1)
