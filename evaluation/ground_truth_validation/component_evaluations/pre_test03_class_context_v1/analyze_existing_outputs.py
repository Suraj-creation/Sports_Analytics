# ruff: noqa: E501
"""Read closed diagnostic replays; no engine, pipeline, evaluation or NN changes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ART = ROOT.parent / "ground-truth-validation-artifacts-20261112/pre_test03_v2/test01_candidate_v2"
CONTROL = ROOT.parent / "ground-truth-validation-artifacts-20261110/test_02/test1_semantic_regression_v1/replay"
INPUTS = {}


def sha(p):
    with Path(p).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(p):
    INPUTS[str(p)] = sha(p)
    return json.loads(Path(p).read_text())


def lines(p):
    INPUTS[str(p)] = sha(p)
    return [json.loads(s) for s in Path(p).open()]


def save(name, value):
    with (HERE / name).open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def main():
    completion = read(ART / "completion.json")
    assert completion["status"] == "completed_fresh_candidate_regression_root_visual_review_pending"
    before_completion = read(ART / "before_semantic_control_completion.json")
    control_events = CONTROL / "events.jsonl"
    assert sha(control_events) == before_completion["artifact_sha256"]["replay/events.jsonl"]
    before_meta = read(ART / "before_semantic_control.json")
    worker = read(ART / "run/inference.json")
    assert before_meta["source_sha256"] == worker["source_sha256"]
    manifests = {label: read(HERE / f"{label}_focus_replay/replay_manifest.json") for label in ["old", "new"]}
    old_parity = read(HERE / "old_focus_vs_latest_semantic_control.json")
    assert not old_parity["differences"]
    new_parity = read(HERE / "new_focus_replay/parity_vs_fresh.json")
    assert not new_parity["differences"]
    events = {label: lines(HERE / f"{label}_focus_replay/current-events.jsonl") for label in ["old", "new"]}
    event_maps = {
        label: {kind: {r["frame_start"]: r for r in rows if r["type"] == kind} for kind in ["contact", "stroke"]}
        for label, rows in events.items()
    }
    added = sorted(event_maps["new"]["contact"].keys() - event_maps["old"]["contact"].keys())
    assert added == [1438, 1488, 3015, 3558, 6471, 8108, 10676]
    assert not event_maps["old"]["contact"].keys() - event_maps["new"]["contact"].keys()
    readouts = {
        label: {r["frame"]: r for r in read(HERE / f"{label}_focus_replay/contact_readouts.json")}
        for label in ["old", "new"]
    }
    trace = {
        label: {
            r["frame"]: r for r in lines(HERE / f"{label}_focus_replay/bounded_fsm_trace.jsonl") if r["call"] == "step"
        }
        for label in ["old", "new"]
    }
    cases = []
    for frame in added:
        old, new = readouts["old"][frame], readouts["new"][frame]
        contact = event_maps["new"]["contact"][frame]
        stroke = event_maps["new"]["stroke"][frame]
        inputs = contact["payload"]["physical_evidence"]["inputs"]
        motion = inputs["motion"]
        sample_frames = sorted(set(motion["before_frames"]) | set(motion["after_frames"]))
        samples = []
        for f in sample_frames:
            a, b = trace["old"][f], trace["new"][f]
            assert b["observation"]["kind"] == "observed" and b["interpolated"] is False
            assert b["raw_perception"]["s"] is not None and b["raw_perception"]["sa"]["status"] == "observed"
            assert a["raw_perception"]["s"] == b["raw_perception"]["s"]
            samples.append(
                {
                    "frame": f,
                    "raw_xy": b["raw_perception"]["s"],
                    "interpolated": b["interpolated"],
                    "kind": b["observation"]["kind"],
                }
            )
        velocity_equal = (
            old["incoming_velocity"] == new["incoming_velocity"]
            and old["outgoing_velocity"] == new["outgoing_velocity"]
        )
        assert velocity_equal
        hypothesis = contact["payload"]["participant_hypothesis"]
        participant_ids = {item["participant_id"] for item in inputs["participant_context"]["observations"]}
        # Show earlier admission of the current pair, not physical name bindings.
        birth_rows = {
            label: [
                {
                    "frame": r["frame_start"],
                    "participant_id": r["payload"]["participant_id"],
                    "track_id": r["payload"]["track_id"],
                    "kind": r["payload"]["kind"],
                }
                for r in rows
                if r["type"] == "participant_observation"
                and r["payload"].get("participant_id") in participant_ids
                and r["payload"].get("kind") in ["PLAYER_ENTERED", "PARTICIPANT_FIRST_OBSERVED"]
            ]
            for label, rows in events.items()
        }
        reason = (
            "Former provider-selected trajectory-only turn now passes unchanged body-proximity gate."
            if old["selected_at_frame"]
            else "Restored body cues raise score above unchanged threshold/NMS; see neighboring selected candidates."
        )
        cases.append(
            {
                "frame": frame,
                "seconds": frame / 30,
                "ground_truth": None,
                "diagnostic_expectation": "Type-correct observed motion and explicit estimated/ambiguous physical status, not asserted real racket impact.",
                "old_readout": old,
                "new_readout": new,
                "actual_velocity_inputs_exactly_equal": velocity_equal,
                "all_used_motion_samples_observed_noninterpolated": True,
                "used_motion_samples": samples,
                "before_missing_body_series": old["current_bodies"] == 0,
                "after_current_body_series": new["current_bodies"],
                "mechanism": reason,
                "participant_birth_lineage": birth_rows,
                "new_contact_status": contact["payload"]["contact_status"],
                "new_physical_status": contact["payload"]["physical_event_status"],
                "new_physical_evidence": contact["payload"]["physical_evidence"],
                "new_participant_hypothesis": hypothesis,
                "new_stroke_payload": stroke["payload"],
                "new_actors": stroke["actors"],
                "D01_leak_observed": False,
                "physical_contact_or_stroke_accuracy_established": False,
            }
        )
    flips = []
    for frame in [3540, 6456]:
        a, b = [event_maps[label]["stroke"][frame]["payload"] for label in ["old", "new"]]
        previous_next = min(f for f in event_maps["old"]["contact"] if f > frame)
        current_next = min(f for f in event_maps["new"]["contact"] if f > frame)
        assert a["speed_px_s"] == b["speed_px_s"] and a["hitter_court_xy"] == b["hitter_court_xy"]
        flips.append(
            {
                "frame": frame,
                "ground_truth": None,
                "before": a,
                "after": b,
                "old_next_anchor": previous_next,
                "new_next_anchor": current_next,
                "speed_exactly_unchanged": True,
                "hitter_geometry_exactly_unchanged": True,
                "cause": "New intermediate estimated contact shortens next-candidate flight interval; same unchanged rule branches choose a different heuristic label.",
                "independent_class_label_available": False,
            }
        )
    # Every used current source sample was preserved; no normalization of a
    # missing/interpolated point into physical evidence is introduced here.
    source_files = {}
    for label in ["old", "new"]:
        core = HERE / f"{label}_focus_replay/executed_core_source/sports/badminton/src/bai_badminton"
        for relative in [
            "engine.py",
            "events/stroke.py",
            "events/contact.py",
            "events/rally_evidence.py",
            "participant_contact.py",
            "participation.py",
            "perception/components.py",
        ]:
            p = core / relative
            INPUTS[str(p)] = sha(p)
            source_files[f"{label}:{relative}"] = {"path": str(p), "sha256": INPUTS[str(p)]}
    result = {
        "schema": "actual-test1-class-context-diagnosis:v1",
        "ground_truth": None,
        "fresh_test1_commit": "c585e35",
        "source_sha256": worker["source_sha256"],
        "old_control_scope": "Latest dacc semantic intervention445contacts, not pre-racket original446contact NN arm. Existing full-event compare_live gives zero differences.",
        "new_scope": "Focus replay strict fresh own-parity true, no newNN.",
        "observed_motion_sample_leak_found": False,
        "use_reconstruction_scope": "Rally-provider continuation flag; not a global shuttle postprocessing/contact interpolation switch. Both contact scoring and stroke speed exclude interp samples.",
        "contact_configuration_equal": manifests["old"]["actual_contact_configuration"]
        == manifests["new"]["actual_contact_configuration"],
        "actual_contact_configuration": manifests["new"]["actual_contact_configuration"],
        "contact_counts": {
            "before": len(event_maps["old"]["contact"]),
            "after": len(event_maps["new"]["contact"]),
            "added": added,
            "removed": [],
        },
        "unknown_counts": {
            label: sum(e["payload"]["stroke"] == "unknown" for e in mapping["stroke"].values())
            for label, mapping in event_maps.items()
        },
        "added_cases": cases,
        "class_flips": flips,
        "source_files": source_files,
        "input_sha256": INPUTS,
        "limitations": [
            "No physical impact/hitter/class truth; restored body context can increase false candidate contacts.",
            "The two common label flips depend on unverified estimated next anchors; neither new label is called correct.",
            "No heuristic suppression of known shoe/head/racket aliases; no production, profile, evaluator or annotation edits.",
        ],
    }
    assert result["contact_configuration_equal"]
    save("causal_readout.json", result)
    print(
        json.dumps(
            {
                "added": added,
                "velocity_exact_equal_all": True,
                "all_motion_samples_observed": True,
                "common_label_flip_cause": "next candidate anchor",
                "configuration_equal": True,
            }
        )
    )


if __name__ == "__main__":
    main()
