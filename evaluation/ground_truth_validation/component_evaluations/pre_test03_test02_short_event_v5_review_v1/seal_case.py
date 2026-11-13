"""Bind factual conclusions and original source evidence, then seal the report."""
import json
import re
from hashlib import file_digest
from pathlib import Path

OUT = Path(__file__).resolve().parent
MAIN = OUT.parents[3]
NATIVE = MAIN.parent / "test03-scene-overlap-20261112"
ART = MAIN.parent / "ground-truth-validation-artifacts-20261112/pre_test03_v5/test02_candidate_v5"


def sha(p):
    with Path(p).open("rb") as f:
        return file_digest(f, "sha256").hexdigest()


def main():
    from bai_badminton.events.exchange_evidence import (
        ContactParticipantContext,
        ContactParticipantObservation,
        simultaneous_opponents,
    )

    receipt = json.loads((OUT / "extraction_receipt.json").read_text())
    inputs = dict(receipt["input_sha256"])
    events = json.loads((OUT / "actual_case_events.json").read_text())
    cache = json.loads((OUT / "actual_case_cache.json").read_text())
    trace = json.loads((OUT / "actual_ordered_trace.json").read_text())
    a, b = [{r["f"]: r for r in cache[name]} for name in ["previous2418", "current5ae"]]
    equality = {key: all(a[f].get(key) == b[f].get(key) for f in a)
                for key in ["s", "c", "p", "do", "ps", "g", "v", "cs"]}
    assert all(equality.values())
    assert all(r["ps"] == 1 for r in cache["current5ae"])

    def contact(arm, frame):
        return next(r for r in events[arm]["append_only"]
                    if r["type"] == "contact" and r["frame_start"] == frame and r["payload"])

    def context(value):
        return ContactParticipantContext(value["shot_id"], value["content_epoch"], value["coordinate_epoch"],
                                         tuple(ContactParticipantObservation(**r) for r in value["observations"]))

    pairs = {}
    for arm, frames in [("original", (11715, 11740)), ("current5ae", (11731, 11740))]:
        first, second = [contact(arm, f)["payload"]["physical_evidence"]["inputs"] for f in frames]
        proof = simultaneous_opponents(context(first["participant_context"]), first["attribution_target"],
                                       context(second["participant_context"]), second["attribution_target"])
        pairs[arm] = {"frames": frames, "targets": [first["attribution_target"], second["attribution_target"]],
                      "same_target": first["attribution_target"] == second["attribution_target"],
                      "native_pair_helper_proof": proof,
                      "motion_sample_intersection": sorted(set(first["motion"]["before_frames"] + first["motion"]["after_frames"])
                                                           & set(second["motion"]["before_frames"] + second["motion"]["after_frames"]))}
    assert pairs["current5ae"]["same_target"] and pairs["current5ae"]["native_pair_helper_proof"] is None
    assert pairs["original"]["native_pair_helper_proof"] is not None
    canceled = [r for r in trace["current5ae"] if r["update"].get("cancelled_start") == 11716]
    assert len(canceled) == 1 and canceled[0]["frame"] == 11774
    assert canceled[0]["after"]["exchange_admission"]["witness_frames"] == []
    compare_path = ART / "bound_reference_diagnostics/reference_row_comparisons.json"
    inputs[str(compare_path)] = sha(compare_path)
    rows = json.loads(compare_path.read_text())["Test2_Full.csv"]["comparison"]
    missed = next(r for r in rows if r.get("reference_data_row") == 33)
    assert missed["matching_status"] == "missed" and [missed["gt_start_frame"], missed["gt_end_frame"]] == [11700, 11760]
    snapshot = OUT / "source_snapshots"
    sources = ["events/rally_evidence.py", "events/rally_fsm.py", "events/exchange_evidence.py", "components.py",
               "engine.py", "events/contact.py", "perception/pipeline.py"]
    source_sha = {}
    for relative in sources:
        path = NATIVE / "sports/badminton/src/bai_badminton" / relative
        inputs[str(path)] = sha(path)
        target = snapshot / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
        source_sha[relative] = inputs[str(path)]
    visual = MAIN / "evaluation/ground_truth_validation/regression_tests/pre_test03_contract_v1/visual_test02_lost_short_event_v1"
    complete = json.loads((visual / "completion.json").read_text())
    assert complete["source_sha256"] == "4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a"
    inputs[str(visual / "completion.json")] = sha(visual / "completion.json")
    for frame in [11715, 11731, 11740, 11751]:
        name = f"frame_{frame:07d}/source_resized.png"
        assert sha(visual / name) == complete["artifact_sha256"][name]
        inputs[str(visual / name)] = sha(visual / name)
    facts = {"current_reference_row33": missed, "same_raw_window_vs2418": equality, "pose_stride_one_entire_window": True,
             "episode_pair_proofs": pairs, "current_cancellation_frame": 11774,
             "current_closed_segment": [11716, 11751], "FSM_inclusive_length": 36, "unchanged_minimum_frames": 60,
             "current_live_short_event_rows": len(events["current5ae"]["live"]),
             "physical_release_contact_hitter_verified": False, "source_snapshots_sha256": source_sha}
    (OUT / "verified_case_facts.json").write_text(json.dumps(facts, indent=2) + "\n")
    links = []
    for target in re.findall(r"\]\(([^)]+)\)", (OUT / "REPORT.md").read_text()):
        p = (OUT / target.split("#", 1)[0]).resolve()
        assert p.exists(), p
        links.append(str(p))
    for p, h in inputs.items():
        assert sha(p) == h, p
    artifacts = {str(p.relative_to(OUT)): sha(p) for p in sorted(OUT.rglob("*"))
                 if p.is_file() and "__pycache__" not in p.parts and p.name != "verification_receipt.json"}
    with (OUT / "verification_receipt.json").open("x") as f:
        json.dump({"status": "sealed_completed_current_Test2_short_exchange_diagnosis", "candidate_commit": receipt["candidate_commit"],
                   "actual_native_ROOT_verified": True, "original_and_current_data_unchanged": True,
                   "fulltrace_steps_each_current_and2418": 29296, "native_pair_helper_same_target_refusal_verified": True,
                   "new_neural_inference": False, "new_semantic_replay": False, "production_fix_implemented": False,
                   "new_threshold_or_contact_label": False, "physical_ground_truth": None,
                   "local_links_verified": len(links), "input_sha256": inputs, "artifact_sha256": artifacts}, f, indent=2)
        f.write("\n")
    print(json.dumps({"status": "sealed", "artifacts": len(artifacts), "inputs": len(inputs),
                      "report_sha256": sha(OUT / "REPORT.md"), "receipt_sha256": sha(OUT / "verification_receipt.json")}))


if __name__ == "__main__":
    main()
