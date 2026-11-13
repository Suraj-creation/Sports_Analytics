"""Re-derive the frozen executor's explicit numerical-helper compatibility proof."""

import importlib.util
import json
from hashlib import file_digest
from pathlib import Path


def sha(path):
    with Path(path).open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def verify_method_bindings(config, out):
    out = Path(out)
    art, native = Path(config["artifact_root"]), Path(config["native_root"])
    # The caller must first run the actual producer-native completion guard.
    guard = json.loads((out / "native_guard_receipt.json").read_text())
    if guard["orchestration_completion_sha256"] != sha(art / "completion.json"):
        raise ValueError("Numerical-method review lacks its completed native source binding")
    path = native / "evaluation/ground_truth_validation/orchestration/run_pre_test03_regression.py"
    spec = importlib.util.spec_from_file_location("frozen_v6_executor_method_proof", path)
    executor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(executor)
    if Path(config["main_root"]) != executor.MAIN:
        raise ValueError("Actual executor primary-workspace contract differs")
    verified = executor.require_helper_compatibility(native)
    preflight = json.loads((art / "preflight.json").read_text())
    if verified != preflight["helper_compatibility"]:
        raise ValueError("Current helper byte/AST proof differs from the admitted frozen proof")
    rows = []
    for name, record in verified.items():
        if sha(Path(config["main_root"]) / name) != record["primary_workspace_sha256"]:
            raise ValueError("Primary numerical helper changed")
        if sha(native / name) != record["native_sha256"]:
            raise ValueError("Native numerical helper changed")
        rows.append({"file": name, **record})
    receipt = {
        "schema": "independent-frozen-numerical-helper-review:v1",
        "executor": str(path),
        "executor_sha256": sha(path),
        "preflight_sha256": sha(art / "preflight.json"),
        "unchanged_evaluator_byte_and_AST_bindings": rows,
        "scope": (
            "Exact bytes or only the executor's explicit codec25/native structural dispatch normalization; "
            "numerical matching remains unchanged"
        ),
        "ROOT_reassigned": False,
    }
    with (out / "method_bindings.json").open("x") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    return receipt
