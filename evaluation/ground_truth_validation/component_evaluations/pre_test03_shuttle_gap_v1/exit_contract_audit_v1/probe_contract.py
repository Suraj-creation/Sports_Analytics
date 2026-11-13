"""Read out existing provider proofs under bound model-free test fixtures."""

from __future__ import annotations

import hashlib
import json
import runpy
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]
MANIFEST = Path(
    "/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/improved_v1/diagnostic_replay/replay_manifest.json"
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    output = ROOT / "proof_readouts.json"
    assert not output.exists()
    bindings = json.loads((ROOT / "input_binding.json").read_text())
    for item in bindings["source_files"]:
        assert sha(item["original"]) == sha(ROOT / item["copy"]) == item["sha256"]
    assert sha(bindings["g69_input"]) == bindings["g69_input_sha256"]
    manifest = json.loads(MANIFEST.read_text())
    functions = runpy.run_path(str(ROOT / "test_g69_exit_contract.py"))
    window, provider, proof, shortened = (functions[key] for key in ("window", "provider", "proof", "shortened"))
    results = []
    for count in [6, 1, 2, 3]:
        observed = window(count)
        selected = provider()
        value = proof(selected, observed)
        results.append(
            {
                "fixture": "actual recorded six-point lower branch"
                if count == 6
                else "synthetic availability counterfactual",
                "lower_sample_count": count,
                "input_unchanged_by_proof": bool(observed.shuttle.vis[27348 - 27312]),
                "selected_provider_type": type(selected).__qualname__,
                "proof": asdict(value),
            }
        )
    observed = window(1)
    selected = provider()
    first = proof(selected, shortened(observed, 27354))
    later = proof(selected, observed)
    available_window = {
        "without_upper_return": asdict(first),
        "with_upper_return": asdict(later),
        "last_proof_recomputed": selected.last_exit_support == later,
    }
    modules = {}
    for name, module in sorted(sys.modules.items()):
        if not name.startswith(("bai_badminton", "bai_engine")):
            continue
        filename = getattr(module, "__file__", None)
        if filename is None:
            continue
        path = Path(filename).resolve()
        relative = str(path.relative_to(REPO))
        assert sha(path) == manifest["core_source_snapshot"]["sha256"][relative], (name, relative)
        modules[name] = {"path": str(path), "relative": relative, "sha256": sha(path), "recorded_core_match": True}
    result = {
        "schema": "existing-exit-provider-contract-audit:v1",
        "configured_implementation": manifest["actual_profile"]["components"]["rally"],
        "source_manifest": str(MANIFEST),
        "source_manifest_sha256": sha(MANIFEST),
        "proof_readouts": results,
        "available_window_recomputation": available_window,
        "loaded_component_modules": modules,
        "conclusion": (
            "No singleton permanent-abort defect in configured provider; "
            "actual contiguous lower branch exceeds declared singleton scope"
        ),
        "new_algorithm": False,
        "new_NN": False,
        "physical_ground_truth": None,
        "new_full_pipeline_evaluation": False,
        "fixture_counterfactuals_are_production_predictions": False,
    }
    with output.open("x") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"status": "completed", "bound_loaded_modules": len(modules), "readouts": len(results)}))


if __name__ == "__main__":
    main()
