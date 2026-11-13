"""Separate original fresh-NN and new postprocessing gates; no ROOT rebasing."""

import ast
import hashlib
import importlib
import importlib.util
import inspect
import json
from datetime import UTC, datetime
from hashlib import file_digest
from pathlib import Path

STATUS = "completed_postprocessing_of_original_fresh_run_root_review_pending"
SCHEMA = "native-completed-test2-postprocessing-completion:v1"


def sha(path):
    with Path(path).open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def completion_contract(value, config):
    if (
        value.get("schema") != SCHEMA
        or value.get("status") != STATUS
        or value.get("candidate_commit") != config["expected_commit"]
        or value.get("source_sha256") != config["source_sha256"]
        or value.get("frames") != config["frame_count"]
        or value.get("test") != 2
        or value.get("original_NN_root") != config["neural_artifact_root"]
        or value.get("producer_root") != config["native_root"]
    ):
        raise ValueError("Incomplete or foreign postprocessing; do not consume metrics")
    if value.get("new_neural_inference") is not False:
        raise ValueError("Continuation must not claim new neural inference")
    for key in (
        "original_neural_inference_was_fresh",
        "original_failed_outer_unchanged",
        "own_run_semantic_parity",
        "annotations_and_baselines_unchanged",
        "source_helpers_models_profile_frozen",
        "actual_model_identity_equal",
        "no_cleanup",
        "no_test3",
    ):
        if value.get(key) is not True:
            raise ValueError("Unverified separate postprocessing contract: " + key)
    if not isinstance(value.get("artifact_sha256"), dict) or not value["artifact_sha256"]:
        raise ValueError("No preserved postprocessing artifacts")


def root_contract(config):
    art, neural = Path(config["artifact_root"]).resolve(), Path(config["neural_artifact_root"]).resolve()
    if art == neural or art in neural.parents or neural in art.parents:
        raise ValueError("Original NN and postprocessing must be distinct nonnested roots")
    if Path(config["original_run"]).resolve() != neural / "run":
        raise ValueError("Explicit original native run must belong to original NN root")
    if Path(config["original_failure_record"]).resolve() != neural / "failure.json":
        raise ValueError("Exact original failure record required")
    return art, neural


def original_failure_contract(neural, manifest):
    if (neural / "completion.json").exists() or not (neural / "failure.json").is_file():
        raise ValueError("Original outer failure must remain; no invented original completion")
    declared = manifest.get("original_artifact_sha256", {})
    for name in ("failure.json", "analysis.result.json", "analysis.log", "run/inference.json", "run.executor.json"):
        path = neural / name
        if str(path) not in declared or not path.is_file() or sha(path) != declared[str(path)]:
            raise ValueError("Original failure/worker evidence absent or changed: " + name)
    for path, digest in declared.items():
        if not Path(path).is_relative_to(neural) or sha(path) != digest:
            raise ValueError("Original artifact changed or foreign: " + path)


def source_pair_contract(bound, config, source_size):
    if (
        bound["source_sha256"] != config["source_sha256"]
        or bound["proxy_sha256"] != config["expected_proxy_sha256"]
        or source_size != config["source_size_bytes"]
        or bound["media"]["n_frames"] != config["frame_count"]
    ):
        raise ValueError("Exact source/proxy byte extent or frame timeline differs")


def verify_native_completion(config, out):
    art, neural = root_contract(config)
    completion_path = art / "completion.json"
    if not completion_path.is_file():
        raise ValueError("Postprocessing is not complete; no metrics may be consumed")
    native, main = Path(config["native_root"]).resolve(), Path(config["main_root"]).resolve()
    completion = json.loads(completion_path.read_text())
    completion_contract(completion, config)
    manifest_path = art / "continuation_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if (
        manifest.get("original_NN_root") != str(neural)
        or manifest.get("original_run") != str(neural / "run")
        or manifest.get("producer_root") != str(native)
        or manifest.get("producer_commit") != config["expected_commit"]
        or manifest.get("postprocessing_tool_root") != str(main)
        or manifest.get("new_neural_inference_here") is not False
        or manifest.get("original_neural_inference_was_fresh") is not True
        or manifest.get("native_ROOT_reassigned") is not False
        or manifest.get("original_outer_failure_rewritten") is not False
        or manifest.get("numeric_metric_or_threshold_change") is not False
    ):
        raise ValueError("Explicit continuation provenance differs")
    original_failure_contract(neural, manifest)
    for field in ("tool_sha256", "producer_source_sha256", "protected_input_sha256"):
        for path, digest in manifest[field].items():
            if sha(path) != digest:
                raise ValueError("Protected source/tool/baseline/annotation changed: " + path)
    if sha(neural / "preflight.json") != manifest["original_preflight_sha256"]:
        raise ValueError("Original preflight changed")
    # Navigation links never serve as substitutes for original NN provenance.
    for name in ("run", "run.executor.json", "environment.json", "preflight.json", "timestamps"):
        if not (art / name).is_symlink() or (art / name).resolve() != (neural / name).resolve():
            raise ValueError("Navigation link points outside original neural evidence: " + name)
    guard = importlib.import_module("research.pipeline_repair_run_analysis")
    if (
        Path(guard.__file__).resolve() != native / "research/pipeline_repair_run_analysis.py"
        or guard.ROOT.resolve() != native
    ):
        raise ValueError("Actual native producer ROOT required; no reassignment/monkeypatches")
    bound = guard.load_analysis_input(Path(config["original_run"]), None)
    if bound["completion_mode"] != "normal_completed_worker":
        raise ValueError("Original genuine completed worker and parent required")
    session = json.loads((neural / "run/session.json").read_text())
    source_pair_contract(bound, config, Path(session["source"]["uri"]).stat().st_size)
    worker = json.loads((neural / "run/inference.json").read_text())
    parent = json.loads((neural / "run.executor.json").read_text())
    if (
        worker["status"] != "completed"
        or worker["cached_perception_used"] is not False
        or worker["frames_processed"] != config["frame_count"]
        or parent["status"] != "completed"
        or parent["worker_exit_code"] != 0
        or parent["worker_report_sha256"] != sha(neural / "run/inference.json")
    ):
        raise ValueError("Original NN execution proof failed")
    plan_path = Path(bound["plan_path"])
    plan = json.loads(plan_path.read_text())
    if Path(plan["root"]).resolve() != native:
        raise ValueError("Source plan belongs to a different producer")
    for path, digest in plan["source_files_sha256"].items():
        if sha(path) != digest:
            raise ValueError("Frozen native source changed: " + path)
    # Use the explicit structural auditor with actual native decoder; never patch
    # the preserved historical analysis helper's globals or mathematical methods.
    adapter_path = main / "evaluation/ground_truth_validation/orchestration/analyse_native_completed_run.py"
    spec = importlib.util.spec_from_file_location("_independent_native_adapter_bindings", adapter_path)
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    actual, auditor, decoder, bindings = adapter.load_native_interfaces(native, main)
    if actual is not guard or bindings["native_ROOT_reassigned"] or bindings["native_globals_patched"]:
        raise ValueError("Native interfaces changed")
    consumed = {str(path): sha(path) for path in bound["input_paths"]}
    packets, frames = guard.load_chunks(Path(bound["cache_dir"]), bound["cache_sha256"], consumed)
    _, _, proof = auditor.audit_frames(frames, config["frame_count"], packets=packets, decode_packet=decoder)
    compatibility_path = art / "analysis/structural_compatibility_receipt.json"
    compatibility = json.loads(compatibility_path.read_text())
    if (
        compatibility["schema"] != "native-completed-run-postprocessing-compatibility:v1"
        or compatibility["status"] != "postprocessing_only_after_original_fresh_worker_completion"
        or compatibility["producer_root"] != str(native)
        or compatibility["tool_root"] != str(main)
        or compatibility["new_neural_inference"] is not False
        or compatibility["original_worker_and_parent_modified"] is not False
        or compatibility["original_outer_failure_modified"] is not False
        or compatibility["numeric_helper_binding"] != bindings["native_function_bindings"]
        or compatibility["structural_proof"] != proof
    ):
        raise ValueError("Postprocessing structural/numerical binding differs from native audit")
    component_path = art / "bound_reference_diagnostics/structural_compatibility_receipt.json"
    component = json.loads(component_path.read_text())
    module = importlib.import_module("evaluation.ground_truth_validation.orchestration.evaluate_test02_components")
    if (
        Path(module.__file__).resolve()
        != native / "evaluation/ground_truth_validation/orchestration/evaluate_test02_components.py"
        or module.ROOT.resolve() != native
    ):
        raise ValueError("Native component evaluator ROOT differs")
    expected_functions = dict(bindings["native_function_bindings"])
    for name in ("reference_comparison", "pair_points", "distribution", "court_diagnostic", "binding_status"):
        function = getattr(module, name)
        path = Path(inspect.getsourcefile(function)).resolve()
        if not path.is_relative_to(native):
            raise ValueError("Component numerical function imported from outside native producer")
        expected_functions[name] = {
            "path": str(path),
            "file_sha256": sha(path),
            "function_AST_sha256": hashlib.sha256(
                ast.dump(ast.parse(inspect.getsource(function)), include_attributes=False).encode()
            ).hexdigest(),
        }
    if (
        component["schema"] != "native-components-postprocessing-compatibility:v1"
        or component["status"] != "postprocessing_only_after_original_fresh_worker_completion"
        or component["producer_root"] != str(native)
        or component["tool_root"] != str(main)
        or component["new_neural_inference"] is not False
        or component["original_worker_and_parent_modified"] is not False
        or component["original_outer_failure_modified"] is not False
        or component["native_function_bindings"] != expected_functions
        or component["structural_proof"] != proof
    ):
        raise ValueError("Native component structural/numerical bindings differ")
    for name, digest in completion["artifact_sha256"].items():
        if sha(art / name) != digest:
            raise ValueError("New postprocessing artifact changed: " + name)
    consumed.update(
        {
            str(path): sha(path)
            for path in (completion_path, manifest_path, compatibility_path, component_path, plan_path)
        }
    )
    for path, digest in consumed.items():
        if sha(path) != digest:
            raise ValueError("Consumed native input changed")
    receipt = {
        "status": "passed_actual_candidate_native_strict_completion_guard",
        "verified_utc": datetime.now(UTC).isoformat(),
        "native_module": str(Path(guard.__file__).resolve()),
        "native_root": str(native),
        "completion_mode": bound["completion_mode"],
        "source_sha256": bound["source_sha256"],
        "proxy_sha256": bound["proxy_sha256"],
        "media": bound["media"],
        "original_parent_status": bound["original_parent_status"],
        "original_NN_root": str(neural),
        "new_postprocessing_root": str(art),
        "original_failure_sha256": sha(neural / "failure.json"),
        "original_outer_completion_exists": False,
        "original_neural_inference_was_fresh": True,
        "new_neural_inference_here": False,
        "input_paths_sha256": consumed,
        "source_plan_files_rehashed": len(plan["source_files_sha256"]),
        "orchestration_completion_sha256": sha(completion_path),
        "original_artifact_hashes_verified": len(manifest["original_artifact_sha256"]),
        "native_packets_audited": len(packets),
        "scene_epoch_proof": proof,
        "new_inference_performed": False,
        "guard_ROOT_rebased": False,
    }
    with (Path(out) / "native_guard_receipt.json").open("x") as handle:
        json.dump(receipt, handle, indent=2, allow_nan=False)
        handle.write("\n")
    return receipt
