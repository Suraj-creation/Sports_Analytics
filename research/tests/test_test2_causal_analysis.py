"""Recorded gates cannot silently become physical-error or defect conclusions."""

import copy
import json

import pytest

from research import test2_causal_analysis as tool


def fixture(count=20):
    raw, steps = {}, {}
    for frame in range(count):
        raw[frame] = {
            "f": frame, "s": [10.0 + frame, 20.0], "c": 0.8, "v": "main", "cs": "VALID", "r": False,
            "sa": {"status": "observed", "selected_xy": [10.0 + frame, 20.0], "reasons": []}, "p": [],
        }
        state = {"state": "idle", "start": None, "tentative_end": None, "end_reason": "", "closed": None}
        steps[frame] = {
            "call": "step", "frame": frame, "available_through": count - 1,
            "observation": {"frame": frame, "kind": "observed", "speed": 5.0, "player_motion": None,
                            "context_valid": True},
            "before": copy.deepcopy(state), "after": copy.deepcopy(state), "update": {},
        }
    return raw, steps


def test_frame_runs_preserve_half_open_counts_and_reject_duplicate_frames():
    assert tool.intervals([2, 3, 4, 6]) == [[2, 5], [6, 7]]
    assert tool.intervals([]) == []
    with pytest.raises(ValueError, match="unique"):
        tool.intervals([2, 2])


def test_raw_absence_without_diagnostic_does_not_invent_masking():
    raw, steps = fixture()
    raw[0]["s"] = None
    raw[0]["sa"] = {"status": "missing", "selected_xy": None}
    steps[0]["observation"]["kind"] = "missing"
    flags = tool.gate_status(raw[0], steps[0])
    assert "raw_provider_coordinate_absent" in flags
    assert not any("mask" in flag or "threshold" in flag for flag in flags)
    raw[0]["dg"] = {"shuttle": {"reason": "mask_rejected"}}
    assert "recorded_heatmap_mask_rejection" in tool.gate_status(raw[0], steps[0])


def test_competing_masked_peak_is_not_called_a_correct_lost_shuttle():
    raw, steps = fixture()
    raw[0]["sa"]["candidates"] = [{"above_inference_threshold": True, "mask_allows_peak": False}]
    flags = tool.gate_status(raw[0], steps[0])
    assert flags == ["above_threshold_heatmap_competitor_outside_mask"]


def test_association_abstention_distinct_from_raw_loss_and_processed_loss():
    raw, steps = fixture()
    raw[0]["sa"].update(status="ambiguous", selected_xy=None, reasons=["coobserved_static_competitor"])
    steps[0]["observation"]["kind"] = "ambiguous"
    flags = tool.gate_status(raw[0], steps[0])
    assert flags == ["association_withheld"]
    raw[1]["sa"]["status"] = "observed"
    steps[1]["observation"]["kind"] = "reconstructed"
    flags = tool.gate_status(raw[1], steps[1])
    assert "selected_coordinate_not_processed_as_observed" in flags
    assert "processed_reconstruction" in flags


def test_gate_window_preserves_gaps_firsts_and_actual_motion_threshold():
    raw, steps = fixture()
    for frame in [3, 4, 5, 9]:
        raw[frame]["s"] = None
    summary = tool.recorded_window(0, 12, steps, raw, start_speed=6)
    assert summary["gate_patterns"]["raw_provider_coordinate_absent"]["runs_half_open"] == [[3, 6], [9, 10]]
    assert summary["gate_patterns"]["raw_provider_coordinate_absent"]["longest_run_frames"] == 3
    assert summary["firsts"]["processed_observed"] == 0
    assert summary["firsts"]["measured_movement_above_start_gate"] is None
    assert summary["detailed_heatmap_diagnostic_frames"] == 0
    assert summary["participant_evidence_coverage"]["frames_without_player_tracks"] == 12


def test_candidate_cancellation_uses_recorded_closed_duration_not_gt_length():
    _, steps = fixture()
    row = steps[7]
    row["before"].update(state="closed", closed={"start": 1, "end": 4, "reason": "gap"})
    row["update"] = {"cancelled_start": 1}
    summary = tool.transition_summary([row], 5)
    case = summary["cancelled_candidates"][0]
    assert case["candidate_length_under_fsm_contract"] == 4
    assert case["recorded_mechanism"] == "candidate_below_minimum_duration"


def test_contact_admission_is_machine_candidate_not_verified_serve():
    _, steps = fixture()
    row = steps[7]
    row["call"] = "on_contact"
    row["update"] = {"started": 7}
    row["after"].update(state="in_play", start=7)
    summary = tool.transition_summary([row], 5)
    assert summary["starts"][0]["admission"] == "accepted_contact_candidate"
    assert "serve" not in json.dumps(summary)


def test_nested_trace_wrappers_do_not_duplicate_actual_finalization_or_cancellation():
    _, steps = fixture()
    outer = copy.deepcopy(steps[12])
    outer["update"] = {"finalized": {"start": 3, "end": 8, "reason": "cut"}, "cancelled_start": 10}
    nested = copy.deepcopy(outer)
    nested["call"] = "on_discontinuity"
    summary = tool.transition_summary([nested, outer], 5)
    assert len(summary["finalized_intervals"]) == len(summary["cancelled_candidates"]) == 1
    assert summary["finalized_intervals"][0]["recorded_wrapper_calls"] == ["on_discontinuity", "step"]


def test_missed_rally_retains_uncertainty_without_artificial_boundary_errors():
    raw, steps = fixture()
    case = {"case_id": "gt_001", "matching_status": "missed", "gt_start_frame": 3, "gt_end_frame": 12,
            "pred_start_frame": None, "pred_end_frame": None}
    summary = tool.summarize_case(case, steps, raw, list(steps.values()), [], 5)
    assert summary["matched_or_unmatched_prediction_terminal"] is None
    assert summary["software_defect_established"] is False
    assert summary["physical_failure_classification"].startswith("unresolved")
    assert "start_frame_error" not in summary["evaluation"]


def test_prediction_terminal_requires_own_exact_finalized_interval():
    raw, steps = fixture()
    case = {"case_id": "pred_001", "matching_status": "unmatched_prediction", "start_frame": 3, "end_frame": 12}
    trace = list(steps.values())
    with pytest.raises(ValueError, match="exactly one finalized"):
        tool.summarize_case(case, steps, raw, trace, [], 5)
    final = copy.deepcopy(steps[18])
    final["update"] = {"finalized": {"start": 3, "end": 12, "serve_frame": None, "reason": "gap"}}
    trace.append(final)
    summary = tool.summarize_case(case, steps, raw, trace, [], 5)
    terminal = summary["matched_or_unmatched_prediction_terminal"]
    assert terminal["finalization"]["frame"] == 18
    assert terminal["prediction_interval_half_open_under_benchmark_contract"] == [3, 12]
    assert "recorded_termination_gap" in summary["machine_mechanism_tags"]


def test_incomplete_run_is_rejected_before_annotation_derived_inputs(tmp_path, monkeypatch):
    from research import production_external_semantic_replay as replay

    run = tmp_path / "unfinished"
    run.mkdir()
    (run / "session.json").write_text('{"session_id":"TEST"}')

    def incomplete(*args, **kwargs):
        raise ValueError("unfinished run")

    monkeypatch.setattr(replay, "load_finished_input", incomplete)
    output = tmp_path / "out"
    with pytest.raises(ValueError, match="unfinished"):
        tool.analyse(run, tmp_path / "missing-replay", tmp_path / "missing-evaluation", output)
    assert not output.exists()


def test_manual_comparison_edit_is_rejected_against_bound_unchanged_evaluator(tmp_path):
    from scripts.benchmarking.evaluate_rallies import evaluate, read_csv, write_predictions

    gt, pred = tmp_path / "reference.csv", tmp_path / "prediction.csv"
    write_predictions(gt, [(0, 100)], 30)
    write_predictions(pred, [(5, 100)], 30)
    metrics, rows = evaluate(read_csv(gt, 30), read_csv(pred, 30), 30)
    comparison = [{key: "" if value is None else str(value) for key, value in row.items()} for row in rows]
    supplemental = {"provenance": {str(gt): "recorded", str(pred): "recorded"}, "metrics": metrics}
    tool.verify_comparison(comparison, supplemental, pred, 30)
    comparison[0]["pred_start_frame"] = "0"
    with pytest.raises(ValueError, match="differ from unchanged"):
        tool.verify_comparison(comparison, supplemental, pred, 30)
