"""Publish a new immutable engineering register from closed diagnostic evidence.

This is an evidence compiler, not an inference or benchmark evaluator. It never
loads a model, imports pipeline code, or modifies historical evidence.
"""

# Long literals are preserved report prose, not wide executable statements.
# ruff: noqa: E501

from __future__ import annotations

import copy
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = OUT.parent.parent
OLD = OUT.parent / "pre_test03_engineering_v2"
ACQ = BASE / "component_evaluations/pre_test03_scene_acquisition_v1"
PREFIX = ACQ / "prefix_v2"
REVIEW = ACQ / "independent_prefix_review_v1"
WORKTREE = Path("/home/administrator/Desktop/sport-analytics/test03-scene-acquisition-20261112")
COMMIT = "9992f87fc24c51da28ada77c07d15e9e18338232"
LATER = "a14695372f0d66d0c80a0bbad8d2c63864001d95"
TIMEBASE = "zero-origin canonical CFR30/1; ranges inclusive; source PTS remain separately bound"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(name, data):
    path = OUT / name
    with path.open("x") as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write("\n")


def git(*args):
    return subprocess.check_output(["/usr/bin/git", *args], cwd=WORKTREE)  # noqa: S603 - fixed read-only Git operations


def frame_info(frame=None, end=None, reason=None):
    return {
        "frame": frame,
        "inclusive_range": None if end is None else [frame, end],
        "seconds": None if frame is None else frame / 30,
        "end_seconds_inclusive": None if end is None else end / 30,
        "timebase": TIMEBASE,
        "not_applicable_reason": reason,
    }


def condensed(row):
    raw = row["raw_content"]
    tracking = row.get("tracking_diagnostic") or {}
    decision = row["decision"]
    return {
        "frame": row["frame"],
        "source_pts": row["source_pts"],
        "source_time_base": row["source_time_base"],
        "source_pixels_sha256": row["source_pixels_sha256"],
        "person_count": len(row["persons"]),
        "detector_observed_flag": row["detector_observed"],
        "actual_process_diagnostic": tracking.get("frame_idx") == row["frame"],
        "detector_executed": tracking.get("detector_executed"),
        "fresh_matched_count": sum(p["detector_matched"] for p in row["persons"]),
        "outside_person_count": row["outside_person_count"],
        "foreground_count": len(row["foreground_regions"]),
        "foreground_overflow": row["scene_foreground_overflow"],
        "raw_hypothesis": raw["hypothesis"],
        "supporting_region_keys": raw.get("supporting_region_keys", []),
        "acquisition_region_keys": raw.get("acquisition_region_keys", []),
        "relative_region_keys": raw.get("relative_region_keys", []),
        "decision": None if decision is None else decision["decision"],
        "decision_reason": None if decision is None else decision["reason"],
        "strict_current_indices": None if decision is None else decision.get("court_indices"),
        "expected_participants": None if decision is None else decision.get("expected_participants"),
        "barrier": row["barrier"],
        "episode_numbers_are_physical_identities": False,
    }


def main():
    for name in ["cases.json", "case_summary.csv", "README.md", "evidence_index.json", "verification_receipt.json"]:
        assert not (OUT / name).exists(), f"Refusing existing published output: {name}"
    old_hashes = {str(p.relative_to(OLD)): sha(p) for p in OLD.rglob("*") if p.is_file()}
    old = read(OLD / "cases.json")
    evidence = copy.deepcopy(read(OLD / "evidence_index.json")["evidence"])
    for entry in evidence.values():
        assert sha(entry["path"]) == entry["sha256"], entry["path"]
        entry["lineage"] = "Historical v2 evidence; no claim this is the current implementation"

    def add_evidence(key, path, role, selector=None):
        assert key not in evidence, key
        path = Path(path).resolve()
        evidence[key] = {
            "path": str(path),
            "sha256": sha(path),
            "bytes": path.stat().st_size,
            "role": role,
            "selector": selector,
        }
        return key

    add_evidence(
        "V2_CASE_DATABASE",
        OLD / "cases.json",
        "Preserved historical register, including explicitly corrected D04 claim",
    )
    add_evidence("V2_RECEIPT", OLD / "verification_receipt.json", "Historical immutable publication receipt")
    receipt = read(PREFIX / "artifact_receipt.json")
    assert receipt["status"] == "preserved_closed_bounded_probe_artifacts"
    assert receipt["source_files_unchanged"] is True
    assert receipt["pipeline_commit"] == COMMIT
    assert len(receipt["artifact_sha256"]) == 92
    for rel, digest in receipt["artifact_sha256"].items():
        assert sha(PREFIX / rel) == digest, rel
        add_evidence(
            "ACQ_ARTIFACT_" + rel, PREFIX / rel, "Closed bounded prefix artifact; no full-video accuracy claim"
        )
    add_evidence("ACQ_RECEIPT", PREFIX / "artifact_receipt.json", "All92 closed bounded artifacts")
    add_evidence(
        "ACQ_INPUT_MANIFEST", PREFIX / "input_manifest_at_start.json", "Executed source/model/proxy input bindings"
    )
    summary = read(PREFIX / "summary.json")
    assert summary["status"] == "completed_bounded_scene_foreground_probe"
    assert summary["candidate_commit"] == COMMIT and not summary["full_pipeline"]
    for path, digest in summary["input_sha256"].items():
        assert sha(path) == digest, path
    assert len(summary["cases"]) == 15
    assert sum(c["range"][1] - c["range"][0] + 1 for c in summary["cases"]) == 3054
    assert sum(c["fresh_neural_detector_calls"] for c in summary["cases"]) == 289
    assert sum(c["unique_detector_observations"] for c in summary["cases"]) == 1200
    later_paths = git("diff", "--name-only", COMMIT, LATER).decode().splitlines()
    assert len(later_paths) == 5 and all("/tests/" in p for p in later_paths)

    # Final independent source review is required before publication. The initial
    # numerical verification alone must not be called completed visual review.
    assert (REVIEW / "REPORT.md").is_file(), "Independent source review report not closed yet"
    assert (REVIEW / "completion.json").is_file(), "Independent final receipt not closed yet"
    independent_completion = read(REVIEW / "completion.json")
    assert independent_completion["status"] == "completed_read_only_bounded_review"
    assert independent_completion["executed_candidate_commit"] == COMMIT
    assert independent_completion["independent_source_proxy_frames_verified"] == 3054
    assert independent_completion["raw_layout_decisions_verified"] == 25
    assert independent_completion["saved_coverage_boxes_restored"] == 182
    assert independent_completion["physical_ground_truth"] is None
    assert independent_completion["full_pipeline_accepted"] is False
    for relative, digest in independent_completion["artifact_sha256"].items():
        assert sha(REVIEW / relative) == digest, relative
    for p in sorted(REVIEW.rglob("*")):
        if p.is_file():
            add_evidence(
                "INDEPENDENT_" + str(p.relative_to(REVIEW)),
                p,
                "Separate independent source/conditional coverage review; not physical ground truth",
            )
    coverage = read(REVIEW / "coverage_all182.json")
    assert coverage["arm_match_counts"] == {"original": 182, "c7": 0, "foreground": 182}
    assert len(coverage["rows"]) == 182
    assert all(r["arms"]["foreground"]["best_iou"] == 1.0 for r in coverage["rows"])
    for key, rel, role in [
        ("ACQ_DESIGN", "design_review_v1/REPORT.md", "Independent design/contract risks and23focused GREEN"),
        ("ACQ_DESIGN_RECEIPT", "design_review_v1/verification_receipt.json", "Closed independent design review"),
        (
            "ACQ_SHADOW",
            "source_design_probe_v1/REPORT.md",
            "Preproduction source-pixel/camera counterfactual; distinguished from actual chronological prefix",
        ),
    ]:
        add_evidence(key, ACQ / rel, role)
    add_evidence(
        "CLASS_CONTEXT",
        BASE / "component_evaluations/pre_test03_class_context_v1/REPORT.md",
        "Closed c585 class/contact lineage analysis; no physical contact/class correctness",
    )
    add_evidence(
        "CLASS_CONTEXT_RECEIPT",
        BASE / "component_evaluations/pre_test03_class_context_v1/verification_receipt.json",
        "Separate earlier completed class-context analysis",
    )

    native_files = {
        "players": "sports/badminton/src/bai_badminton/perception/players.py",
        "scene_change": "sports/badminton/src/bai_badminton/perception/scene_change.py",
        "content": "sports/badminton/src/bai_badminton/perception/content.py",
        "foreground": "sports/badminton/src/bai_badminton/perception/foreground.py",
        "pipeline": "sports/badminton/src/bai_badminton/perception/pipeline.py",
        "plugin": "sports/badminton/src/bai_badminton/plugin.py",
        "engine": "sports/badminton/src/bai_badminton/engine.py",
        "identity": "sports/badminton/src/bai_badminton/identity.py",
    }
    git_sources = {}
    for name, rel in native_files.items():
        blob = git("show", f"{COMMIT}:{rel}")
        digest = hashlib.sha256(blob).hexdigest()
        assert digest == summary["input_sha256"][str(WORKTREE / rel)], rel
        assert blob == git("show", f"{LATER}:{rel}"), rel
        git_sources[name] = {
            "commit": COMMIT,
            "path": rel,
            "sha256": digest,
            "git_object": git("rev-parse", f"{COMMIT}:{rel}").decode().strip(),
            "test_only_later_commit_production_identical": True,
        }

    timelines = {}
    for c in summary["cases"]:
        test = c["test"]
        a, z = c["range"]
        filename = f"test{test}_{a:05}_{z:05}.json"
        data = read(PREFIX / filename)
        for rows in data["variants"].values():
            assert [r["frame"] for r in rows] == list(range(a, z + 1))
        timelines[(test, a, z)] = (filename, data)

    executed_sets = {arm: set() for arm in ("original", "c7", "foreground")}
    for (test, _a, _z), (_filename, data) in timelines.items():
        for arm, rows in data["variants"].items():
            executed_sets[arm].update(
                (test, row["frame"])
                for row in rows
                if (row.get("tracking_diagnostic") or {}).get("frame_idx") == row["frame"]
                and (row.get("tracking_diagnostic") or {}).get("detector_executed") is True
            )
    assert {arm: len(values) for arm, values in executed_sets.items()} == {
        "original": 1187,
        "c7": 1187,
        "foreground": 1199,
    }
    assert len(set.union(*executed_sets.values())) == 1200
    execution_added = sorted(executed_sets["foreground"] - executed_sets["original"])
    execution_omitted = sorted(executed_sets["original"] - executed_sets["foreground"])
    assert len(execution_added) == 13 and execution_omitted == [(2, 7703)]

    def sample(test, frame):
        found = [(n, d) for (t, a, z), (n, d) in timelines.items() if t == test and a <= frame <= z]
        assert len(found) == 1, (test, frame)
        filename, data = found[0]
        return {
            arm: condensed(next(r for r in rows if r["frame"] == frame)) for arm, rows in data["variants"].items()
        }, "ACQ_ARTIFACT_" + filename

    def png(test, frame):
        for (t, a, z), (_name, _data) in timelines.items():
            if t == test and a <= frame <= z:
                rel = f"test{test}_{a:05}_{z:05}_frame_{frame:05}.png"
                assert "ACQ_ARTIFACT_" + rel in evidence
                return "ACQ_ARTIFACT_" + rel
        raise AssertionError((test, frame))

    cases = []
    for prior in old["cases"]:
        c = copy.deepcopy(prior)
        c["lineage"] = {
            "register": "V2_CASE_DATABASE",
            "prior_case_id": c["case_id"],
            "historical_validation": c.pop("Validation"),
            "historical_prediction": "Full historical values remain in immutable v2 case record",
        }
        c["case_id"] = c["case_id"].replace("ENG2-", "ENG3-").replace("CTRL2-", "CTRL3-")
        c["Prediction"] = {"historical_record": "V2_CASE_DATABASE", "prior_case_id": prior["case_id"]}
        c["component_modules"] = [native_files[x] for x in ["players", "scene_change", "content", "pipeline", "plugin"]]
        c["Validation"] = {
            "state": "inherited focused evidence plus new bounded prefix where applicable",
            "latest_candidate_full_fresh_Test1": "not established by this register",
            "latest_candidate_full_fresh_Test2": "not established by this register",
            "physical_accuracy_verified": False,
            "next_gate": "Source-native complete fresh Test1/Test2, unchanged original evaluators and independent source review",
        }
        frame = c["TimestampFrame"]["frame"]
        tests = c["Video"]["tests"]
        if frame is not None and len(tests) == 1:
            try:
                c["Prediction"]["new_bounded_prefix"], ref = sample(tests[0], frame)
                c["evidence_refs"].append(ref)
            except AssertionError:
                pass  # The inherited G69 full-run diagnostic is outside bounded scope.
        if c["case_id"].startswith(("ENG3-SCENE", "ENG3-FG", "ENG3-STALE")):
            c["Fix"]["current_implementation_commit"] = COMMIT
            c["Fix"]["unchanged"] = (
                "Numerical scene/model thresholds and original annotation/evaluation rules. Strict participant TTL is superseded by separately documented observed hypothesis continuity."
            )
            c["diagnostic_expectation"]["text"] = c["diagnostic_expectation"]["text"].replace(
                "athlete authority must remain withheld outside its lease",
                "outside target hypotheses must preserve provenance without acquiring named/scoring authority",
            )
            c["Validation"]["state"] = (
                "current chronological bounded prefix retains this scene/memory repair; latest full-video acceptance pending"
            )
        if c["case_id"] == "ENG3-AUTH-T2-6492":
            c["case_id"] = "ENG3-EDIT-CHAIN-T2-5958_6492"
            c["Component"] = "Source edit acquisition → target-participant origin reset →6492 downstream availability"
            c["TimestampFrame"] = frame_info(5958, 6492)
            c["ErrorType"] = "missed_true_source_edit_with_stale_origin_inheritance; prior TTL-only remedy rejected"
            c["RootCause"] = (
                "At5958 both athletes relocate in a same-camera edited jump. Their relative image innovations pass existing3x but mean9.059625 is below strong15; one official overlaps an old athlete box. Without source reset, spatial continuity can inherit the stale origin. The earlier strict last-in-court TTL reduced this artifact but also withheld182 genuine conditional athlete rows; it was not a general physical continuous-handover solution."
            )
            c["Fix"] = {
                "status": "implemented and bounded chronological source verified; complete fresh acceptance pending",
                "canonical_issue": "D04",
                "implementation_commit": COMMIT,
                "description": "Restore continuous fresh target hypotheses while keeping actual ROI anchors separate. Acquire relative evidence separately; reset only with independent same-channel2, prior confirmedN, strict current court/camera-bound complete replacement. Reset origins before reusing raw detector probe.",
                "not_claimed": "General same-person identity through uninterrupted athlete/official crossover; named or point authority",
            }
            c["diagnostic_expectation"] = {
                "basis": "agent_reviewed_edited_source_and_machine_contract",
                "physical_ground_truth": False,
                "text": "5958 source change should be acquired without deleting legitimate continuously observed offcourt athletes.6492 exact raw athlete proposals remain usable; no named attribution follows.",
            }
            c["Prediction"]["new5958"], ref = sample(2, 5958)
            c["Prediction"]["new6492"], _ = sample(2, 6492)
            c["Prediction"]["535_frame_scope"] = (
                "New foreground arm returns two target hypotheses in all535frames5958–6492; outside79frames includes legitimate runoff hypotheses, not a label for officials."
            )
            c["evidence_refs"] += [ref, png(2, 5958), png(2, 6492), "ACQ_DESIGN", "ACQ_SHADOW"]
        if c["case_id"] == "ENG3-BIRTH-T2-11346":
            c["Validation"]["state"] = (
                "two immediate observed boxes preserved at11346; no bounded source barrier; cold prefix starts11300 without prior scene memory"
            )
            c["Fix"]["status"] = (
                "birth availability preserved; full historical scene acquisition unresolved by this short prefix"
            )
        if c["case_id"] in {"D01", "D02"}:
            c["component_modules"] = [native_files["engine" if c["case_id"] == "D01" else "plugin"]]
            c["TimestampFrame"] = frame_info(reason="Component contract, not a particular physical source frame")
            c["Validation"]["state"] = (
                "prior deterministic contract validated; no new full temporal or named-identity evaluation in this bounded player/scene replay"
            )
            c["Fix"]["status"] = (
                "implemented in current source; accuracy and full latest candidate acceptance remain separate"
            )
            if c["case_id"] == "D01":
                c["evidence_refs"] += ["CLASS_CONTEXT", "CLASS_CONTEXT_RECEIPT"]
                c["Validation"]["earlier_c585_evidence"] = (
                    "Two class flips trace next estimated contact endpoints;7added anchors use unchanged raw observed velocity. No estimated-evidence leakage established in those focused cases; no classGT."
                )
        if c["case_id"] == "I-G69":
            c["Validation"]["state"] = (
                "inherited unresolved; no new shuttle/engine/FSM measurement in current scene prefix"
            )
        c["frequency_scope"] = (
            "One engineering/causal record or explicit interval, not independent failure frequency or physical accuracy"
        )
        cases.append(c)

    groups = [
        (753, 800, 700, 820),
        (3413, 3449, 3330, 3470),
        (6365, 6381, 6280, 6400),
        (7801, 7805, 7650, 8150),
        (7812, 7856, 7650, 8150),
        (8087, 8105, 7650, 8150),
        (14103, 14113, 14000, 14150),
    ]

    def make(case_id, component, test, frame, end, error, cause, fix, expectation, modules, refs):
        return {
            "case_id": case_id,
            "group": "confirmed_engineering",
            "related_issue_ids": ["D04"],
            "Component": component,
            "Video": {"tests": [test], "source_media_ids": [f"TEST{test}_MEDIA"]},
            "TimestampFrame": frame_info(frame, end),
            "GroundTruth": None,
            "diagnostic_expectation": {
                "basis": "agent_reviewed_source_and_machine_contract",
                "physical_ground_truth": False,
                "text": expectation,
            },
            "supplied_reference": None,
            "Prediction": {},
            "ErrorType": error,
            "RootCause": cause,
            "Fix": {
                "status": "implemented; bounded diagnostic validation only",
                "implementation_commit": COMMIT,
                "description": fix,
            },
            "Validation": {
                "state": "bounded chronological exact-source controls; no full latest inference acceptance",
                "physical_accuracy_verified": False,
                "full_latest_Test1_Test2_complete_claimed": False,
            },
            "component_modules": [native_files[m] for m in modules],
            "evidence_refs": refs,
            "frequency_scope": "Explicit engineering case or interval only; not measured failure prevalence",
        }

    for a, z, start, stop in groups:
        rows = [r for r in coverage["rows"] if a <= r["frame"] <= z]
        assert len(rows) == z - a + 1
        new_rows = [r for r in timelines[(1, start, stop)][1]["variants"]["foreground"] if a <= r["frame"] <= z]
        fresh = sum(r["arms"]["foreground"]["matched_person"]["detector_matched"] for r in rows)
        case = make(
            f"ENG3-COVERAGE-T1-{a}_{z}",
            "Target-participant observed continuity / actual ROI anchor",
            1,
            a,
            z,
            "strict_geometric_TTL_withheld_continuously_observed_target_hypothesis",
            "c7/c585 strict actual-court anchor expiry removes a visible conditional athlete hypothesis despite fresh unambiguous outside observations. Court geometry support and current source-supported hypothesis freshness were conflated.",
            "Fresh uniquely associated observed targets renew hypothesis freshness only; keep actual ROI-supported anchor separate. Missing/carry frames do not renew; expiry/cut resets prevent stale resurrection. Outside cannot bootstrap an origin.",
            "Preserve these previously source-reviewed athlete hypotheses while explicitly retaining fresh/carried and actual-anchor provenance; no physical identity or point authority follows.",
            ["players", "pipeline", "plugin"],
            ["INDEPENDENT_coverage_all182.json", "ACQ_ARTIFACT_" + timelines[(1, start, stop)][0], png(1, a), png(1, z)]
            if (a, z) not in [(7801, 7805), (7812, 7856), (8087, 8105)]
            else [
                "INDEPENDENT_coverage_all182.json",
                "ACQ_ARTIFACT_" + timelines[(1, start, stop)][0],
                png(1, 7801 if a in (7801, 7812) else 8087),
                png(1, 7856 if a in (7801, 7812) else 8105),
            ],
        )
        case["Prediction"] = {
            "conditional_rows": len(rows),
            "matched_saved_original_box": {"original_control": len(rows), "strict_c7": 0, "new9992": len(rows)},
            "new_iou_to_saved_box_min_max": [1.0, 1.0],
            "new_fresh_target_rows": fresh,
            "new_carried_target_rows": len(rows) - fresh,
            "new_person_count_min_max": [
                min(len(r["persons"]) for r in new_rows),
                max(len(r["persons"]) for r in new_rows),
            ],
            "denominator_is_physical_GT": False,
            "actual_private_anchor_timestamps_serialized_in_prefix": False,
        }
        case["Validation"]["anchor_separation_contract"] = (
            "Independent23-test source-bound GREEN; private timestamps not inferred from prefix person IDs"
        )
        case["measured_extent"] = {"conditional_rows": len(rows), "fresh": fresh, "carried": len(rows) - fresh}
        cases.append(case)

    for f, before in [(355, 354), (5958, 5957), (25521, 25520)]:
        pred, ref = sample(2, f)
        assert pred["foreground"]["barrier"] and not pred["foreground"]["raw_hypothesis"]
        c = make(
            f"ENG3-WEAK-SCENE-T2-{f}",
            "Relative image acquisition / corroborated court replacement",
            2,
            f,
            None,
            "missed_same_camera_edited_jump_below_strong_absolute_floor",
            "Two independent correspondence innovations satisfy unchanged relative3x conditions but not the strong absolute15 floor. Without a separate acquisition cue the current raw court layout is not obtained; weak image evidence alone must never become fallback reset authority.",
            "V4 exposes acquisition separately. Same-channel2 plus prior confirmedN, exactN distinct strict current court boxes, all-prior correspondence exclusion and adjacent-camera alignment corroborate weak reset. Keep strong policy and original numeric thresholds unchanged.",
            "Agent-reviewed simultaneous athlete-position jumps support a diagnostic source-edit expectation. This remains separate from independently annotated physical scene truth.",
            ["scene_change", "content", "players", "pipeline", "plugin"],
            [ref, png(2, before), png(2, f), "ACQ_SHADOW", "ACQ_DESIGN"],
        )
        c["Prediction"] = pred
        c["measured_extent"] = {"reviewed_source_event_examples": 1, "independent_scene_GT_labels": 0}
        cases.append(c)

    pred, ref = sample(1, 11333)
    c = make(
        "LIMIT3-CARRY-T1-11333",
        "Scheduled detector carry / current-pixel localization",
        1,
        11333,
        None,
        "inherited_strided_carry_lag",
        "The detector last executes11328; idle stride6 carries existing boxes through11333. Preserving target hypotheses does not localize athletes afresh on these skipped frames.",
        "No speculative threshold/flow/stride fix proposed. Evaluate source-bound motion-aware acquisition or validated current-pixel continuity with negative controls before altering scheduling.",
        "A carried box is an estimate, not an observed current localization; physical source disagreement should remain visible and labelled as diagnostic uncertainty.",
        ["players", "pipeline"],
        [ref, png(1, 11328), png(1, 11333)],
    )
    c["group"] = "inherited_unresolved"
    c["Prediction"] = pred
    c["Fix"]["status"] = "unresolved; no blind stride or threshold tuning"
    cases.append(c)
    c = make(
        "LIMIT3-IDENTITY-NONEDIT-HANDOVER",
        "Target hypothesis / physical identity / scoring authority",
        2,
        None,
        None,
        "unsupported_general_identity_guarantee",
        "Spatial continuity can cross an uninterrupted athlete/official occlusion or crossover without two-region source innovation. Correctly resetting edited5958 does not prove all nonedit handovers are distinguishable with the available observations.",
        "Retain explicit target-hypothesis status and actual ROI anchor provenance. Collect independently reviewed continuity/hitter/roster controls; consider independently validated appearance/motion models before named or score authority.",
        "Do not equate a track episode, court-origin target hypothesis, a physical person, a team and a scoring slot.",
        ["players", "identity", "plugin"],
        ["ACQ_DESIGN", "IDENT_ARCH", "IDENT_ARCH_RECEIPT"],
    )
    c["TimestampFrame"] = frame_info(
        reason="Architecture limitation, not a newly observed labelled physical handover event"
    )
    c["group"] = "inherited_unresolved"
    c["Fix"]["status"] = "unresolved capability / labels needed; no physical identity metric available"
    c["Prediction"] = {
        "general_nonedit_handover_accuracy": None,
        "named_binding_ground_truth": None,
        "singles_doubles": "No near/far permanent name binding; confirmed doubles remains four physical target hypotheses and two scoring slots",
    }
    cases.append(c)
    assert len(cases) == 25 and len({c["case_id"] for c in cases}) == 25
    assert all(c["GroundTruth"] is None for c in cases)
    assert sum(c.get("measured_extent", {}).get("conditional_rows", 0) for c in cases) == 182
    for c in cases:
        assert all(k in c for k in old["required_case_fields"]), c["case_id"]
        for key in c["evidence_refs"]:
            assert key in evidence, (c["case_id"], key)

    payload = {
        "schema": "pre-test03-engineering-failure-cases:v3",
        "created_utc": datetime.now(UTC).isoformat(),
        "records_immutable": True,
        "case_count": len(cases),
        "case_count_is_not_failure_frequency": True,
        "physical_ground_truth_case_count": 0,
        "scope": "Closed engineering/visual diagnostics and regression controls; no new physicalGT/AP or aggregate accuracy; no Test3 access",
        "required_case_fields": old["required_case_fields"],
        "media": old["media"],
        "correction_to_v2": "D04 strict in-courtTTL was not accepted: it withheld182 source-visible conditional athlete rows. New observed target continuity separates actual anchors, while5958 is a true edited jump requiring corroborated source reset. A generic physical continuous identity handover is not solved.",
        "implementation": {
            "executed_prefix_commit": COMMIT,
            "later_test_only_commit": LATER,
            "later_changed_paths": later_paths,
            "production_identical": True,
            "latest_full_video_acceptance": "pending; active suite outputs were not used as completed results",
            "c585_historical_state": "fullTest1 completed with ownparity;182coverage loss rejected before Test2 progression",
        },
        "bounded_measurement_scope": {
            "windows": 15,
            "test1_windows": 9,
            "test2_windows": 6,
            "source_frames": 3054,
            "fresh_neural_detector_calls_in_parent_probe": 289,
            "unique_proposal_bank_observations": 1200,
            "new_NN_calls_by_register_builder": 0,
            "latest_full_pipeline": False,
            "diagnostic_execution_counts": {"original": 1187, "c7": 1187, "foreground": 1199},
            "execution_added_vs_original_test_frame": execution_added,
            "execution_omitted_vs_original_test_frame": execution_omitted,
            "all_proposal_bank_observations_consumed_by_an_arm": True,
            "naive_detector_observed_flags": {"original": 1200, "c7": 1200, "foreground": 1212},
            "cadence_caveat": "13off-main801–813frames retain sticky observedTrue without current process diagnostic; do not count these as actual detector executions",
            "conditional182": {"restored_exact_saved_box": 182, "fresh": 72, "carried": 110, "physical_recall": None},
            "barriers": {"Test1": [7857, 8106], "Test2": [355, 5958, 6151, 6307, 25521]},
            "foreground_overflow_frames": 0,
            "max_foreground_regions": 4,
            "independent_review": "INDEPENDENT_REPORT.md",
        },
        "groups": dict(Counter(c["group"] for c in cases)),
        "priority_ranking": [
            {
                "rank": 1,
                "issue": "Coverage versus edited-source reset integration",
                "measured_basis": "182conditional rows in7intervals restored;3new weak edited-source examples;535frame5958–6492two-hypothesis scope. Development evidence, no prevalence/generalisation claim.",
            },
            {
                "rank": 2,
                "issue": "Retain source-context/memory and first-observation repairs",
                "measured_basis": "Existing7857/8106controls and6151/6307sourcecuts remain;6492/11346birth examples. Dependent records are not independent failure counts.",
            },
            {
                "rank": 3,
                "issue": "Unresolved physical interpretation and observation gaps",
                "measured_basis": "11333carry example,11346cold-prefix limitation and inherited G69rawgap. No measured global contact/class/identity accuracy; labels and held-out controls required.",
            },
        ],
        "cases": cases,
    }
    write("cases.json", payload)
    with (OUT / "case_summary.csv").open("x", newline="") as stream:
        fields = [
            "case_id",
            "group",
            "Component",
            "Video",
            "TimestampFrame",
            "GroundTruth",
            "Prediction",
            "ErrorType",
            "RootCause",
            "Fix",
            "Validation",
        ]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for c in cases:
            writer.writerow(
                {
                    k: (
                        json.dumps(c[k], separators=(",", ":"))
                        if isinstance(c[k], (dict, list))
                        else "null"
                        if c[k] is None
                        else c[k]
                    )
                    for k in fields
                }
            )
    write(
        "evidence_index.json",
        {
            "schema": "engineering-evidence-index:v3",
            "evidence": evidence,
            "source_git_objects": git_sources,
            "old_v2_file_sha256": old_hashes,
            "prefix_artifact_sha256": receipt["artifact_sha256"],
            "recorded_input_sha256": summary["input_sha256"],
            "original_annotation_files_modified": False,
        },
    )

    lines = [
        "# Pre-Test3 engineering cases — immutable v3",
        "",
        "This register corrects the earlier court-TTL diagnosis and preserves its historical evidence. The strict TTL withheld **182 conditional athlete rows across seven intervals**. The new observed target hypothesis restores those saved boxes while keeping the last actual ROI anchor separate. Test2 frame5958 is a **missed edited source jump**; fixing acquisition there does not establish reliable physical identity through uninterrupted athlete/official handovers.",
        "",
        "[Structured cases](cases.json), [CSV summary](case_summary.csv), [evidence and exact hashes](evidence_index.json), and [publication verification](verification_receipt.json) contain25 engineering/causal records. Record count is not failure frequency. Every physical `GroundTruth` is null. Agent-reviewed source expectations, saved model boxes and original CSV references have separate roles; none becomes a new AP, recall, contact, stroke, identity or scene-accuracy label.",
        "",
        "## Implementation and completed scope",
        "",
        f"The closed chronological prefix executed `{COMMIT}`. Later `{LATER}` changes five test fixtures only; all production modules are identical. Fifteen windows (nine Test1, six Test2) contain3,054 source frames and1,200 distinct proposal-bank observations, including289 fresh detector calls by the parent probe. This register performs no inference. The probe excludes pose, shuttle, engine/FSM feedback and full end-to-end scheduling. It is not a completed fresh full-video evaluation.",
        "",
        "The source-controlled cuts are Test1 **7857/8106** and Test2 **355/5958/6151/6307/25521**. The new weak-proof events355/5958/25521 preserve `raw_hypothesis=false`: acquisition and corroborated reset remain separate. Format must be confirmed before current acquisition; exactlyN strict target-court observations and all-prior/camera-aligned exclusions are required. Unknown format and partial doubles visibility abstain. No numerical threshold, checkpoint, original annotation or benchmark matching rule was tuned.",
        "",
        "The182 conditional boxes match the saved original-control boxes exactly (IoU1.0); c7 matches none of that selected withheld subset.72 restored target rows are fresh and110 carried. These selected rows were diagnosed after observing the regression; the182/182 result is **conditional box restoration**, not physical recall or held-out generalisation. Private actual-anchor timestamps are tested by contract and are not reconstructed from opaque prefix IDs.",
        "",
        "A cadence caveat is preserved:13off-main frames801–813 retain a sticky `detector_observed=True` although no current `players.process` diagnostic exists. Actual diagnostic execution counts are1,187/1,187/1,199 (original/c7/new), versus naive1,200/1,200/1,212 flags. The current arm adds13actual execution frames and omits original7703 (net+12). Every one of the1,200proposal-bank observations is consumed by at least one arm; none is labelled an unused seed. The unique proposal bank and actual new-neural-call counter are separate quantities. No foreground overflow occurred; maximum retained regions4.",
        "",
        "## Cases",
        "",
        "|Case|Video / frame(s)|Expected versus actual / disposition|",
        "|---|---|---|",
    ]
    for c in cases:
        t = ",".join(map(str, c["Video"]["tests"]))
        f = c["TimestampFrame"]
        where = (
            "component-level" if f["frame"] is None else str(f.get("inclusive_range") or f.get("frames") or f["frame"])
        )
        if "conditional_rows" in c["Prediction"]:
            msg = f"Saved box restored in{c['Prediction']['conditional_rows']}selected rows; fresh{c['Prediction']['new_fresh_target_rows']}/carried{c['Prediction']['new_carried_target_rows']}. No physical identity claim."
        else:
            msg = c["Fix"]["status"]
        lines.append(f"|{c['case_id']}|Test{t}; {where}|{msg.replace('|', '/')}|")
    lines += [
        "",
        "## What remains unresolved",
        "",
        "At Test1 frame11333 the detector last ran11328 and stride6 carries boxes; continuous availability does not imply current-pixel localization. No blind stride/flow threshold change is proposed. Test2's11300-start prefix has two immediate athlete hypotheses at11346 but no historical two-region acquisition proof; absence of a reset there is a cold-prefix limitation, not a full-video scene result.",
        "",
        "The broader uninterrupted nonedit athlete/official crossover remains a physical-identity limitation. Court geometry, fresh spatial matches and image-context keys are target hypotheses rather than names, teams or accepted score decisions. Singles, four-player doubles and unknown format remain distinct contracts. D01 preserves marked ordinary-missing temporal context; D02 truthfully reports missing/failed appearance capability. Neither supplies missing physical labels. G69's22-frame raw shuttle gap and branch ambiguity remain inherited and unresolved; the current scene-only prefix does not evaluate them.",
        "",
        "Earlier c585 contact/class diagnosis explains seven added candidate anchors and two class flips through restored body context and next-candidate flight intervals, without establishing correct physical contacts or labels. No new classification improvement is inferred from that execution. Full source-native Test1/Test2 inference, unchanged benchmark references, independent visual review, runtime/resource scopes and downstream effects remain required before acceptance or Test3.",
        "",
        "## Evidence, lineage and priorities",
        "",
    ]
    linked = [
        "ACQ_RECEIPT",
        "ACQ_INPUT_MANIFEST",
        "ACQ_DESIGN",
        "ACQ_SHADOW",
        "INDEPENDENT_REPORT.md",
        "INDEPENDENT_completion.json",
        "V2_CASE_DATABASE",
        "V2_RECEIPT",
        "CLASS_CONTEXT",
        "TEMP_REPORT",
        "IDENT_ARCH",
        "G69_REPORT",
    ]
    for key in linked:
        assert key in evidence, key
        lines.append(f"- [{key}]({evidence[key]['path']}): {evidence[key]['role']}.")
    lines += [
        "",
        "Each case links exact prefix/frame PNGs and source evidence through `evidence_refs`; the index binds every referenced byte and immutable Git object.92 prefix artifact hashes and274 original input bindings are verified, as are82 historical evidence bindings. Oldv2files are hashed before and after publication and remain untouched.",
        "",
        "Priorities follow measured impact rather than record frequency: first preserve the182-row coverage repair and source corroboration together; then retain first-observation, memory and old-cut safety controls; then address remaining raw observation, carry, identity/contact/class/outcome limitations using reviewed labels and match-disjoint controls. The latest full suite is not treated as complete by this publication. Future full-run results must append a new version or receipt; do not rewrite this immutable database.",
    ]
    (OUT / "README.md").write_text("\n".join(lines) + "\n")
    for c in cases:
        assert c["GroundTruth"] is None
    for name, digest in old_hashes.items():
        assert sha(OLD / name) == digest, name
    for entry in evidence.values():
        assert sha(entry["path"]) == entry["sha256"], entry["path"]
    links = []
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", (OUT / "README.md").read_text()):
        p = Path(target) if target.startswith("/") else OUT / target
        if p.name != "verification_receipt.json":
            assert p.exists(), p
        links.append(str(p.resolve()))
    artifact_hashes = {str(p.relative_to(OUT)): sha(p) for p in OUT.rglob("*") if p.is_file()}
    write(
        "verification_receipt.json",
        {
            "status": "completed_immutable_engineering_register_v3",
            "sealed_utc": datetime.now(UTC).isoformat(),
            "artifact_sha256": artifact_hashes,
            "all_evidence_hashes_verified": True,
            "evidence_files": len(evidence),
            "prefix_artifacts_verified": 92,
            "recorded_inputs_verified": len(summary["input_sha256"]),
            "historical_evidence_verified": 82,
            "old_v2_files_preserved": len(old_hashes),
            "old_v2_file_sha256": old_hashes,
            "all_local_links_exist": True,
            "local_links": links,
            "physical_GroundTruth_values_all_null": True,
            "case_count": len(cases),
            "case_count_is_failure_frequency": False,
            "executed_prefix_commit": COMMIT,
            "later_test_only_commit": LATER,
            "production_identical": True,
            "new_inference_by_register_builder": False,
            "new_full_video_result_claimed": False,
            "no_Test3_inspection": True,
            "annotations_pipeline_and_existing_results_modified": False,
        },
    )
    print(
        json.dumps(
            {
                "status": "sealed",
                "cases": len(cases),
                "evidence_files": len(evidence),
                "old_files_preserved": len(old_hashes),
            }
        )
    )


if __name__ == "__main__":
    main()
