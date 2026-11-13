"""Genuine fresh native V6 gate; no ROOT reassignment or failed-outer continuation."""

from __future__ import annotations

import importlib
import importlib.util
import json
import os
from datetime import UTC, datetime
from hashlib import file_digest
from pathlib import Path

STATUS = "completed_fresh_candidate_regression_root_visual_review_pending"


def sha(path):
    with Path(path).open("rb") as f:
        return file_digest(f, "sha256").hexdigest()


def completion_contract(value, config):
    if (
        value.get("status") != STATUS
        or value.get("candidate_commit") != config["expected_commit"]
        or value.get("source_sha256") != config["source_sha256"]
        or value.get("frames") != config["frame_count"]
        or value.get("test", 2) != 2
    ):
        raise ValueError("Incomplete or differently bound orchestration; do not consume new results")
    for key in [
        "new_neural_inference",
        "own_run_semantic_parity",
        "annotations_and_baselines_unchanged",
        "source_helpers_models_profile_frozen",
        "actual_model_identity_equal",
        "no_cleanup",
        "no_test3",
    ]:
        if value.get(key) is not True:
            raise ValueError("Unverified completed-run contract: " + key)
    if not isinstance(value.get("artifact_sha256"), dict) or not value["artifact_sha256"]:
        raise ValueError("Completed orchestration has no preserved artifact population")
    for name in value["artifact_sha256"]:
        p = Path(name)
        if p.is_absolute() or ".." in p.parts:
            raise ValueError("Foreign artifact path")


def source_pair_contract(bound, config, source_size):
    if (
        bound["source_sha256"] != config["source_sha256"]
        or bound["proxy_sha256"] != config["expected_proxy_sha256"]
        or source_size != config["source_size_bytes"]
        or bound["media"]["n_frames"] != config["frame_count"]
    ):
        raise ValueError("Exact source/proxy byte extent or timeline differs")


def native_module_contract(actual_file, actual_root, native):
    native = Path(native).resolve()
    if (
        Path(actual_file).resolve() != native / "research/pipeline_repair_run_analysis.py"
        or Path(actual_root).resolve() != native
    ):
        raise ValueError("Actual native helper ROOT required; do not rebase imported modules")


def frame_role_contract(frame, config):
    """Require role/provenance fields before raw/selected diagnostic export."""
    observation = frame.get("sa")
    if not isinstance(observation, dict) or observation.get("schema") != config["expected_association_schema"]:
        raise ValueError("Current association role/schema is unavailable")
    if "raw_masked_peak_xy" not in observation or "selected_model_support" not in observation:
        raise ValueError("Current observed-selection provenance fields are missing")
    if observation.get("raw_xy") != frame.get("s") or observation.get("raw_model_support") != frame.get("c"):
        raise ValueError("Raw NN coordinate/support provenance differs")
    if "aq" not in frame:
        raise ValueError("Current acquisition availability field is missing")
    if frame["aq"] is not None and (
        not isinstance(frame["aq"], dict) or frame["aq"].get("version") != config["expected_motion_acquisition_version"]
    ):
        raise ValueError("Current acquisition proof family differs")


def protected_scope_counts(paths, config):
    """Count exact declared prefixes; candidate copies are not extra original GT."""
    main, native = Path(config["main_root"]) / "Part2", Path(config["native_root"]) / "Part2"
    result = dict.fromkeys(
        ("primary_original_annotations", "candidate_test2_annotation_references", "other_protected_inputs"), 0
    )
    for value in paths:
        path = Path(value)
        key = (
            "primary_original_annotations"
            if path.is_relative_to(main)
            else "candidate_test2_annotation_references"
            if path.is_relative_to(native)
            else "other_protected_inputs"
        )
        result[key] += 1
    return result


def model_asset_contract(models):
    expected = {
        ("registry_artifacts", "rfdetr_small"),
        ("registry_artifacts", "rtmpose_m_body7"),
        ("registry_artifacts", "tracknetv3"),
        ("package_ocr_artifacts", "det"),
        ("package_ocr_artifacts", "cls"),
        ("package_ocr_artifacts", "rec"),
    }
    observed = {
        (group, name): value["sha256"]
        for group, entries in models.items()
        for name, value in entries.items()
        if value.get("sha256")
    }
    if set(observed) != expected or any(
        not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest)
        for digest in observed.values()
    ):
        raise ValueError("Six actual primary/OCR model asset bindings required")
    return {group + "/" + name: digest for (group, name), digest in sorted(observed.items())}


def load_file(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_native_completion(config, out):
    art, native = Path(config["artifact_root"]).resolve(), Path(config["native_root"]).resolve()
    completion_path = art / "completion.json"
    # This precedes imports, cache access, predictions and annotation content.
    if not completion_path.is_file():
        raise ValueError("Orchestration is not complete; no result consumption allowed")
    completion = json.loads(completion_path.read_text())
    completion_contract(completion, config)
    if (art / "failure.json").exists():
        raise ValueError("Failed outer workflow is not a complete fresh arm")
    guard = importlib.import_module("research.pipeline_repair_run_analysis")
    native_module_contract(guard.__file__, guard.ROOT, native)
    bound = guard.load_analysis_input(art / "run", None)
    if bound["completion_mode"] != "normal_completed_worker":
        raise ValueError("Genuine completed parent/worker required")
    worker_path, parent_path = art / "run/inference.json", art / "run.executor.json"
    worker, parent = json.loads(worker_path.read_text()), json.loads(parent_path.read_text())
    if (
        worker["status"] != "completed"
        or worker["cached_perception_used"] is not False
        or worker["frames_processed"] != config["frame_count"]
        or parent["status"] != "completed"
        or parent["worker_exit_code"] != 0
        or parent["worker_report_sha256"] != sha(worker_path)
    ):
        raise ValueError("Fresh worker/parent proof differs")
    session = json.loads((art / "run/session.json").read_text())
    source = Path(session["source"]["uri"])
    source_pair_contract(bound, config, source.stat().st_size)
    plan_path = art / "protocol/plan.json"
    plan = json.loads(plan_path.read_text())
    adapter_path = native / "evaluation/ground_truth_validation/orchestration/analyse_native_completed_run.py"
    adapter = load_file(adapter_path, "_actual_native_v6_review_adapter")
    original, auditor, decoder, bindings = adapter.load_native_interfaces(native, native)
    if original is not guard or bindings["native_ROOT_reassigned"] or bindings["native_globals_patched"]:
        raise ValueError("Native interfaces changed")
    adapter.require_recorded_producer(bound, native, original)
    os.environ["SPORTS_ANALYTICS_PRIMARY_WORKSPACE"] = config["main_root"]
    runner = load_file(
        native / "evaluation/ground_truth_validation/orchestration/run_pre_test03_regression.py",
        "_actual_native_v6_review_runner",
    )
    if Path(config["main_root"]).resolve() != runner.MAIN:
        raise ValueError("Workflow workspace differs from explicit primary")
    runner.require_native_plan(plan, native, art / "protocol", test=2, head=config["expected_commit"])
    if runner.git(native, "rev-parse", "HEAD").strip() != config["expected_commit"]:
        raise ValueError("Native checkout commit differs")
    helpers = runner.require_helper_compatibility(native)
    for path, digest in plan["source_files_sha256"].items():
        if sha(path) != digest:
            raise ValueError("Frozen native source changed: " + path)
    consumed = {str(p): sha(p) for p in bound["input_paths"]}
    packets, frames = guard.load_chunks(Path(bound["cache_dir"]), bound["cache_sha256"], consumed)
    if not packets or any(p["v"] != config["expected_codec"] for p in packets):
        raise ValueError("Fresh repair arm requires its exact declared codec")
    for packet in packets:
        for f in packet["frames"]:
            frame_role_contract(f, config)
            if f.get("cc") and f["cc"]["version"] != config["expected_raw_scene"]:
                raise ValueError("Fresh raw scene family differs")
            if f.get("cd") and f["cd"]["version"] != config["expected_scene_decision"]:
                raise ValueError("Fresh decision scene family differs")
    _, _, proof = auditor.audit_frames(frames, config["frame_count"], packets=packets, decode_packet=decoder)
    if proof["version"] != config["expected_audit_version"]:
        raise ValueError("Current source proof auditor family differs")
    published_analysis = json.loads((art / "analysis/technical_analysis.json").read_text())
    model_asset_contract(published_analysis["models_verified_during_analysis"])
    actual = published_analysis["structural_compatibility"]
    if (
        actual["scene_epoch_proof"] != proof
        or actual["producer_root"] != str(native)
        or actual["tool_root"] != str(native)
    ):
        raise ValueError("Published analysis differs from actual native proof")
    preflight_path = art / "preflight.json"
    preflight = json.loads(preflight_path.read_text())
    if (
        Path(preflight["pipeline_root"]).resolve() != native
        or preflight["commit"] != config["expected_commit"]
        or Path(preflight["new_output"]).resolve() != art
        or preflight["native_ROOT_reassigned"] is not False
    ):
        raise ValueError("Original producer/workflow preflight differs")
    scope_counts = protected_scope_counts(preflight["protected_input_sha256"], config)
    if scope_counts != config["expected_protected_scope_counts"]:
        raise ValueError("Original/candidate/protected input scopes differ")
    for path, digest in preflight["protected_input_sha256"].items():
        if sha(path) != digest:
            raise ValueError("Protected original baseline/annotation/model changed: " + path)
        consumed[path] = digest
    consumed[str(preflight_path)] = sha(preflight_path)
    # All original annotations remain opaque hash checks until the completed gate.
    manifest_path = Path(config["original_annotation_manifest"])
    if preflight["protected_input_sha256"].get(str(manifest_path)) != sha(manifest_path):
        raise ValueError("Annotation manifest differs from actual producer preflight")
    manifest = json.loads(manifest_path.read_text())
    annotation_hashes = {}
    if len(manifest["files"]) != config["original_annotation_file_count"]:
        raise ValueError("Original annotation inventory population changed")
    for item in manifest["files"]:
        if sha(item["path"]) != item["sha256"]:
            raise ValueError("Original annotation changed: " + item["path"])
        annotation_hashes[item["path"]] = item["sha256"]
    for name, digest in completion["artifact_sha256"].items():
        if sha(art / name) != digest:
            raise ValueError("Completed artifact changed: " + name)
    inputs = {
        **consumed,
        **bindings["source_sha256"],
        str(completion_path): sha(completion_path),
        str(manifest_path): sha(manifest_path),
        **annotation_hashes,
    }
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
        "input_paths_sha256": inputs,
        "source_plan_files_rehashed": len(plan["source_files_sha256"]),
        "orchestration_completion_sha256": sha(completion_path),
        "new_inference_performed": False,
        "guard_ROOT_rebased": False,
        "helper_compatibility": helpers,
        "native_scene_proof": proof,
        "all_original_annotation_hash_count": len(annotation_hashes),
        "protected_input_scope_counts": scope_counts,
        "actual_model_assets": model_asset_contract(published_analysis["models_verified_during_analysis"]),
        "source_plan_root_semantics": (
            "protocol artifact directory, separately bound to actual native producer source paths"
        ),
    }
    with (Path(out) / "native_guard_receipt.json").open("x") as f:
        json.dump(receipt, f, indent=2)
        f.write("\n")
    return receipt
