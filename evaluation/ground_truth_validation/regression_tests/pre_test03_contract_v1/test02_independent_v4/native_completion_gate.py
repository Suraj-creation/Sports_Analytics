"""Actual native completed-run guard; never rebase or patch an imported ROOT."""

import importlib
import json
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
    ):
        raise ValueError("Incomplete or differently bound orchestration; do not consume new results")
    for key in (
        "new_neural_inference",
        "own_run_semantic_parity",
        "annotations_and_baselines_unchanged",
        "source_helpers_models_profile_frozen",
        "actual_model_identity_equal",
        "no_cleanup",
        "no_test3",
    ):
        if value.get(key) is not True:
            raise ValueError("Unverified completed-run contract: " + key)
    if not isinstance(value.get("artifact_sha256"), dict) or not value["artifact_sha256"]:
        raise ValueError("Completed orchestration has no preserved artifact population")


def source_pair_contract(bound, config, source_size):
    if bound["source_sha256"] != config["source_sha256"]:
        raise ValueError("Different exact source video")
    if bound["proxy_sha256"] != config["expected_proxy_sha256"]:
        raise ValueError("Exact source/proxy pairing changed")
    if source_size != config["source_size_bytes"]:
        raise ValueError("Source video byte extent differs")
    media = bound["media"]
    if media["n_frames"] != config["frame_count"]:
        raise ValueError("Canonical source timeline frame population changed")


def verify_native_completion(config, out):
    art, native = Path(config["artifact_root"]), Path(config["native_root"])
    completion_path = art / "completion.json"
    if not completion_path.is_file():
        raise ValueError("Orchestration is not complete; no result consumption allowed")
    completion = json.loads(completion_path.read_text())
    completion_contract(completion, config)
    guard = importlib.import_module("research.pipeline_repair_run_analysis")
    if (
        Path(guard.__file__).resolve() != native / "research/pipeline_repair_run_analysis.py"
        or guard.ROOT.resolve() != native
    ):
        raise ValueError("Actual native helper ROOT required; do not rebase imported modules")
    bound = guard.load_analysis_input(art / "run", None)
    if bound["completion_mode"] != "normal_completed_worker":
        raise ValueError("Fresh review requires a genuine completed parent/worker")
    source_path = Path(json.loads((art / "run/session.json").read_text())["source"]["uri"])
    source_pair_contract(bound, config, source_path.stat().st_size)
    import bai_badminton.plugin as plugin

    if not Path(plugin.__file__).resolve().is_relative_to(native):
        raise ValueError("Native production imports required")
    plan_path = art / "protocol/plan.json"
    plan = json.loads(plan_path.read_text())
    for path, digest in plan["source_files_sha256"].items():
        if sha(path) != digest:
            raise ValueError("Frozen native source changed: " + path)
    inputs = {str(p): sha(p) for p in bound["input_paths"]}
    for name, digest in completion["artifact_sha256"].items():
        if sha(art / name) != digest:
            raise ValueError("Completed artifact changed: " + name)
    receipt = {
        "status": "passed_actual_candidate_native_strict_completion_guard",
        "verified_utc": datetime.now(UTC).isoformat(),
        "native_module": str(Path(guard.__file__).resolve()),
        "native_root": str(native),
        "completion_mode": bound["completion_mode"],
        "source_sha256": bound["source_sha256"],
        "proxy_sha256": bound["worker_info"]["proxy_sha256"],
        "media": bound["media"],
        "original_parent_status": bound["original_parent_status"],
        "input_paths_sha256": inputs,
        "source_plan_files_rehashed": len(plan["source_files_sha256"]),
        "orchestration_completion_sha256": sha(completion_path),
        "new_inference_performed": False,
        "guard_ROOT_rebased": False,
    }
    assert receipt["source_sha256"] == config["source_sha256"]
    with (Path(out) / "native_guard_receipt.json").open("x") as f:
        json.dump(receipt, f, indent=2)
        f.write("\n")
    return receipt
