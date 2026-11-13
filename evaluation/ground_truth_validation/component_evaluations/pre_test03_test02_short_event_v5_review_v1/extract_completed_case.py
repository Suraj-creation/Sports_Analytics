"""Read-only source-native short-case audit after genuine outer completion."""
import importlib.util
import json
from collections import Counter
from hashlib import file_digest
from pathlib import Path

import msgpack

OUT = Path(__file__).resolve().parent
MAIN = OUT.parents[3]
SPACE = MAIN.parent
NATIVE = SPACE / "test03-scene-overlap-20261112"
CURRENT = SPACE / "ground-truth-validation-artifacts-20261112/pre_test03_v5/test02_candidate_v5"
ORIGINAL = SPACE / "ground-truth-validation-artifacts-20261110/test_02/improved_v1"
PREVIOUS = SPACE / "ground-truth-validation-artifacts-20261112/pre_test03_v4/test02_postprocessing_v1"
PREVIOUS_RUN = SPACE / "ground-truth-validation-artifacts-20261112/pre_test03_v4/test02_candidate_v4/run"
INPUTS = {}


def sha(p):
    with Path(p).open("rb") as f:
        return file_digest(f, "sha256").hexdigest()


def read(p):
    INPUTS[str(p)] = sha(p)
    return json.loads(Path(p).read_text())


def save(name, value):
    with (OUT / name).open("x") as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write("\n")


def main():
    complete = read(CURRENT / "completion.json")
    assert complete["status"] == "completed_fresh_candidate_regression_root_visual_review_pending"
    assert complete["test"] == 2 and complete["frames"] == 29296
    assert complete["candidate_commit"] == "5ae614826e6f909defb02445386962ac13b4641a"
    assert all(complete[k] is True for k in ["new_neural_inference", "own_run_semantic_parity",
                                           "annotations_and_baselines_unchanged", "source_helpers_models_profile_frozen",
                                           "actual_model_identity_equal"])
    from research import pipeline_repair_run_analysis as native
    from research.production_external_semantic_replay import verify_replay_output_artifacts

    assert native.ROOT == NATIVE
    adapter_path = NATIVE / "evaluation/ground_truth_validation/orchestration/analyse_native_completed_run.py"
    spec = importlib.util.spec_from_file_location("short_native_adapter", adapter_path)
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    bound = native.load_analysis_input(CURRENT / "run", None)
    adapter.require_recorded_producer(bound, NATIVE, native)
    assert bound["completion_mode"] == "normal_completed_worker"
    assert bound["source_sha256"] == "4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a"
    manifest = read(CURRENT / "diagnostic_replay/replay_manifest.json")
    verify_replay_output_artifacts(CURRENT / "diagnostic_replay", manifest)
    assert manifest["baseline_parity"] is True and manifest["trace_step_count"] == 29296
    assert manifest["source_report_sha256"] == sha(CURRENT / "run/inference.json")
    paths = [CURRENT / "run/events.jsonl", CURRENT / "diagnostic_replay/bounded_fsm_trace.jsonl",
             CURRENT / "bound_reference_diagnostics/component_reference_metrics.json",
             CURRENT / "bound_reference_diagnostics/reference_row_comparisons.json"]
    for p in paths:
        relative = str(p.relative_to(CURRENT))
        assert sha(p) == complete["artifact_sha256"][relative]
    trace = {}
    for arm, root in [("previous2418", PREVIOUS), ("current5ae", CURRENT)]:
        path = root / "diagnostic_replay/bounded_fsm_trace.jsonl"
        INPUTS[str(path)] = sha(path)
        selected, steps = [], []
        for line in path.open():
            row = json.loads(line)
            if row["call"] == "step":
                steps.append(row["frame"])
            if 11690 <= row["frame"] <= 11775:
                selected.append(row)
        assert steps == list(range(29296))
        trace[arm] = selected
    save("actual_ordered_trace.json", trace)
    events, cache = {}, {}
    for arm, run in [("original", ORIGINAL / "run"), ("previous2418", PREVIOUS_RUN), ("current5ae", CURRENT / "run")]:
        p = run / "events.jsonl"
        INPUTS[str(p)] = sha(p)
        rows = [json.loads(line) for line in p.open()]
        live = native.select_live_events(rows, rows[0]["session_id"])
        relevant = lambda r: 11690 <= r["frame_start"] <= 11775 and r["type"] in {"contact", "stroke", "rally_start", "rally_end"}
        events[arm] = {"append_only": [r for r in rows if relevant(r)], "live": [r for r in live if relevant(r)]}
        catalogue = read(run / "perception_completion_catalog.json")
        selected = []
        for entry in catalogue["files"]:
            if entry["start"] > 11775 or entry["end"] < 11690:
                continue
            p = run / entry["path"]
            assert sha(p) == entry["sha256"]
            INPUTS[str(p)] = entry["sha256"]
            selected.extend(f for f in msgpack.unpackb(p.read_bytes(), raw=False)["frames"] if 11690 <= f["f"] <= 11775)
        assert [r["f"] for r in selected] == list(range(11690, 11776))
        cache[arm] = selected
    save("actual_case_events.json", events)
    save("actual_case_cache.json", cache)
    summary = {}
    for arm, rows in trace.items():
        changes = [r for r in rows if r["before"]["state"] != r["after"]["state"]
                   or any(r["update"].values()) or r["call"] != "step"]
        summary[arm] = {"state_and_callback_transitions": changes,
                        "observed_frames": [r["frame"] for r in rows if r["call"] == "step" and r["observation"]["kind"] == "observed"],
                        "source_context_epochs": sorted({(r["raw_perception"]["sh"], r["raw_perception"]["ce"])
                                                         for r in rows if r["call"] == "step"})}
    for arm in events:
        summary.setdefault(arm, {})["append_only_types"] = dict(Counter(r["type"] for r in events[arm]["append_only"]))
        summary[arm]["live_types"] = dict(Counter(r["type"] for r in events[arm]["live"]))
    save("short_case_summary.json", summary)
    assert all(sha(p) == h for p, h in INPUTS.items())
    save("extraction_receipt.json", {"status": "completed_native_bound_readonly_short_case_extraction",
                                     "actual_producer": str(NATIVE), "candidate_commit": complete["candidate_commit"],
                                     "worker_mode": bound["completion_mode"], "own_fulltrace_steps": 29296,
                                     "input_sha256": INPUTS, "new_neural_inference": False,
                                     "physical_ground_truth": None})
    print(json.dumps({arm: {k: v for k, v in data.items() if k not in {"state_and_callback_transitions", "observed_frames"}}
                      for arm, data in summary.items()}))


if __name__ == "__main__":
    main()
