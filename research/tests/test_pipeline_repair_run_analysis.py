"""Posthoc measurement scopes and source-bound comparisons stay explicit."""

import json

import msgpack
import pytest

from research.pipeline_repair_run_analysis import (
    analyse,
    audit_frames,
    compare_frame_fields,
    event_summary,
    load_analysis_input,
    load_baseline,
    ocr_summary,
    prediction_changes,
    resource_summary,
    select_live_events,
    sha,
    track_summary,
)
from scripts.benchmarking.evaluate_rallies import Rally, write_predictions


def parent():
    return {
        "allocated_gpu_uuid": "GPU-0",
        "worker_pid": 12,
        "physical_gpu_index": 0,
        "status": "partial_or_failed",
        "worker_exit_code": 1,
        "elapsed_s": 20.0,
    }


def test_original_failure_runtime_and_lost_measurements_are_not_relabelled_success():
    samples = [
        {
            "elapsed_s": 1.0,
            "rows": "GPU-0, 99, 9999\nGPU-1, 12, 9998\nGPU-0, 12, 321\n",
            "worker_tree_rss_bytes": 200,
            "worker_tree_cpu_seconds": 7.0,
            "system_available_ram_bytes": 900,
        },
        {
            "elapsed_s": 2.0,
            "rows": "GPU-0, 12, N/A\n",
            "worker_tree_rss_bytes": 300,
            "worker_tree_cpu_seconds": 9.0,
            "system_available_ram_bytes": 800,
        },
        {"sampling_error": "TimeoutExpired"},
    ]
    stages = {"ocr": [{"seconds": 0.1, "frames": 10}, {"seconds": 0.3, "frames": 10}]}
    result = resource_summary(parent(), samples, stages, 100)
    assert result["original_parent_status"] == "partial_or_failed"
    assert result["worker_exit_code"] == 1
    assert result["parent_failure_inclusive_source_fps"] == 5.0
    assert result["sampled_worker_gpu_peak_mib"] == 321
    assert result["sampled_worker_tree_peak_rss_bytes"] == 300
    assert result["sampled_cpu_seconds_max_observed"] == 9.0
    assert result["sampled_system_available_ram_min_bytes"] == 800
    for field in (
        "model_loading_time_s",
        "model_staging_time_s",
        "media_ready_time_s",
        "worker_final_cpu_s",
        "worker_maxrss_bytes",
        "neural_only_throughput_fps",
    ):
        assert result[field] is None
    assert result["stage_latency"]["ocr"]["p50_ms"] == pytest.approx(200)
    assert result["stage_latency"]["ocr"]["p95_ms"] == pytest.approx(290)
    assert result["stage_latency"]["ocr"]["frame_population_sum"] == 20
    assert not any("Test1/Test2" in note for note in result["limits"])


def frame(f, *, epoch=0, raw=False, decision=None, people=None):
    return {
        "f": f,
        "ce": epoch,
        "cc": {"hypothesis": raw, "status": "hypothesis" if raw else "measured"},
        "cd": decision,
        "p": people or [],
        "do": f % 2 == 0,
        "cs": "VALID",
        "v": "main",
        "s": None,
    }


def test_raw_telemetry_hypotheses_vetoes_and_actual_barriers_are_separate():
    current_pose_on_carried_box = {"t": 1, "dm": False, "k": [[1, 2, 0.8]], "pf": 1, "rf": None}
    rows = [
        frame(0),
        frame(
            1,
            raw=True,
            decision={"decision": "no_barrier", "reason": "layout", "detector_frame": 1},
            people=[current_pose_on_carried_box],
        ),
        frame(
            2,
            epoch=1,
            raw=True,
            decision={"decision": "unknown", "reason": "raw_barrier_fallback", "detector_frame": None},
        ),
    ]
    result, coverage = audit_frames(rows, 3)
    counts = result["counts"]
    assert counts["scene_telemetry_present"] == 3
    assert counts["scene_raw_hypotheses"] == 2
    assert counts["actual_content_epoch_increments"] == 1
    assert counts["scene_positive_correspondence_vetoes"] == 1
    assert counts["pose_current_on_propagated_box"] == 1
    assert counts["person_current_detector_matches"] == 0
    assert len(coverage) == 3


def test_cache_audit_rejects_future_pose_missing_frames_and_contradictory_reset():
    with pytest.raises(ValueError, match="cover each"):
        audit_frames([frame(0), frame(2)], 3)
    future = {"t": 1, "dm": True, "pf": 2, "k": [[1, 2, 1]]}
    with pytest.raises(ValueError, match="future"):
        audit_frames([frame(0, people=[future])], 1)
    with pytest.raises(ValueError, match="contradicted"):
        audit_frames(
            [
                frame(0),
                frame(
                    1, epoch=1, raw=True, decision={"decision": "no_barrier", "reason": "layout", "detector_frame": 1}
                ),
            ],
            2,
        )


def event(identity, *, sid="S", supersedes=None, status="confirmed", kind="stroke", payload=None):
    return {
        "event_id": identity,
        "session_id": sid,
        "supersedes": supersedes,
        "status": status,
        "type": kind,
        "payload": payload or {},
        "actors": {"player_id": None},
        "frame_start": 0,
        "frame_end": 1,
    }


def test_event_ledger_supersession_and_unknown_actor_do_not_inflate_accuracy():
    events = [
        event("old"),
        event("new", supersedes="old", payload={"stroke": "unknown", "classification_status": "unknown"}),
        event("gone", status="retracted"),
    ]
    assert [e["event_id"] for e in select_live_events(events, "S")] == ["new"]
    result = event_summary(events, "S")
    assert result["live_counts"] == {"stroke": 1}
    assert result["categories"]["stroke_actor"] == {"unknown": 1}
    assert result["categories"]["stroke_stroke"] == {"unknown": 1}
    assert result["physical_accuracy_validated"] is False
    with pytest.raises(ValueError, match="duplicate or foreign"):
        select_live_events([event("x", sid="OTHER")], "S")
    with pytest.raises(ValueError, match="duplicate or foreign"):
        select_live_events([event("x"), event("x")], "S")


def test_branding_observation_is_retained_without_becoming_score_truth():
    result = ocr_summary([{"ocr": [{"f": 10, "r": [["SXFI", 21], ["LIVE", 12]], "c": 0.9}]}])
    assert result["previously_source_reviewed_branding_strings"] == {"SXFI": 1, "LIVE": 1}
    assert result["readouts"][0]["r"] == [["SXFI", 21], ["LIVE", 12]]
    assert result["accuracy_validated"] is False


def test_prediction_changes_never_call_baseline_ground_truth_or_make_errors_for_unpaired_rows():
    old = [Rally(10, 30, 1.0, 3.0), Rally(70, 80, 7.0, 8.0)]
    new = [Rally(12, 34, 1.2, 3.4), Rally(80, 100, 8.0, 10.0)]
    result = prediction_changes(old, new)
    assert result["paired"][0]["start_shift_frames"] == 2
    assert result["paired"][0]["end_shift_frames"] == 4
    assert result["unpaired_baseline_indices"] == [2]
    assert result["unpaired_current_indices"] == [2]
    assert len(result["paired"]) == 1
    assert "false_positives" not in result and "f1" not in result
    assert result["overlap_graph"] == [(1, 1)]  # Half-open adjacency80 is not overlap.


def test_legacy_absent_decision_field_stays_unknown_in_exact_cache_comparison():
    old = [{"f": 0, "s": [float("nan"), 1.0]}, {"f": 1, "s": None}]
    new = [{"f": 0, "s": [float("nan"), 1.0], "cd": None}, {"f": 1, "s": None, "cd": None}]
    result = compare_frame_fields(old, new)
    assert result["fields"]["cd"]["baseline_field_absent_frames"] == 2
    assert result["fields"]["cd"]["different_when_both_present"] == 0
    assert result["fields"]["s"]["different_when_both_present"] == 0
    with pytest.raises(ValueError, match="same canonical"):
        compare_frame_fields(old, new[:1])


def baseline_fixture(tmp_path):
    media = {"n_frames": 2, "fps_num": 30, "fps_den": 1}
    (tmp_path / "inference.json").write_text(json.dumps({"status": "analysed", "media": media}))
    write_predictions(tmp_path / "predicted_rallies.csv", [(0, 1)], 30.0)
    (tmp_path / "events.jsonl").write_text(json.dumps(event("r", kind="rally_end")) + "\n")
    metadata = {"source_video_sha256": "a" * 64, "prediction_sha256": sha(tmp_path / "predicted_rallies.csv")}
    (tmp_path / "benchmark_metadata.json").write_text(json.dumps(metadata))
    cache = tmp_path / "runtime/sessions/S/perception"
    cache.mkdir(parents=True)
    (cache / "seg_00000.msgpack").write_bytes(msgpack.packb({"frames": [{"f": 0}, {"f": 1}]}))
    return media


def test_baseline_requires_same_source_and_prediction_event_binding(tmp_path):
    media = baseline_fixture(tmp_path)
    predictions, frames = load_baseline(tmp_path, "a" * 64, media, {})
    assert len(predictions) == 1 and len(frames) == 2
    with pytest.raises(ValueError, match="source/media"):
        load_baseline(tmp_path, "b" * 64, media, {})
    (tmp_path / "predicted_rallies.csv").unlink()
    write_predictions(tmp_path / "predicted_rallies.csv", [(0, 2)], 30.0)
    with pytest.raises(ValueError, match="actual live rally ledger"):
        load_baseline(tmp_path, "a" * 64, media, {})


def test_strict_completion_gate_runs_before_any_data_analysis_or_output(tmp_path, monkeypatch):
    import research.pipeline_repair_completion as completion

    def reject(*_):
        raise ValueError("strict completion not established")

    monkeypatch.setattr(completion, "verify_completion_receipt", reject)
    output = tmp_path / "out"
    with pytest.raises(ValueError, match="strict completion"):
        analyse(tmp_path / "run", tmp_path / "proof", output)
    assert not output.exists()


def test_track_export_checks_calibration_and_nonfinite_positions(tmp_path):
    import pyarrow as pa
    import pyarrow.parquet as pq

    directory = tmp_path / "data/sessions/S/tracks/player"
    directory.mkdir(parents=True)
    rows = [
        {"frame_idx": 0, "track_id": 1, "player_id": None, "detector_matched": False, "court_x": 1.0, "court_y": 2.0},
        {
            "frame_idx": 1,
            "track_id": 1,
            "player_id": None,
            "detector_matched": False,
            "court_x": float("nan"),
            "court_y": 2.0,
        },
    ]
    pq.write_table(pa.Table.from_pylist(rows), directory / "rows.parquet")
    source = [frame(0), {**frame(1), "cs": "LOST"}]
    result = track_summary(tmp_path, "S", source, {})
    assert result["counts"]["player_projected_court_rows"] == 1
    assert result["counts"]["nonfinite_projected_court_rows"] == 1
    assert result["player_rows_on_invalid_geometry"] == [{"frame": 1, "track_id": 1}]


def test_normal_completed_resources_use_original_worker_measurements_without_model_only_claim():
    outer = {**parent(), "status": "completed", "worker_exit_code": 0}
    info = {
        "status": "completed",
        "cached_perception_used": False,
        "elapsed_s": 18.0,
        "media_ready_s": 1.0,
        "model_staging_s": 0.2,
        "worker_cpu_s": 90.0,
        "worker_maxrss_kib": 123,
        "runner_stage_seconds": {"component_initialization_including_models_s": 2.0},
        "visible_torch_devices": [{"logical_index": 0, "name": "actual device"}],
    }
    result = resource_summary(outer, [], {}, 100, info)
    assert result["parent_completed_elapsed_s"] == 20.0
    assert result["worker_source_fps"] == pytest.approx(100 / 18.0)
    assert result["worker_final_cpu_s"] == 90.0
    assert result["worker_maxrss_bytes"] == 123 * 1024
    assert result["media_ready_time_s"] == 1.0
    assert result["component_initialization_including_models_s"] == 2.0
    assert result["model_loading_time_s"] is None
    assert result["neural_only_throughput_fps"] is None
    assert result["parent_failure_inclusive_elapsed_s"] is None
    assert not any("Test1/Test2" in note for note in result["limits"])
    with pytest.raises(ValueError, match="completed fresh"):
        resource_summary(outer, [], {}, 100, {**info, "cached_perception_used": True})


def normal_gate_fixture(tmp_path, monkeypatch, *, changes=None, catalogue=True):
    import research.production_external_semantic_replay as replay
    from research.production_external_semantic_replay import FinishedInput

    media = {"n_frames": 2, "fps_num": 30, "fps_den": 1}
    info = {
        "status": "completed",
        "cached_perception_used": False,
        "frames_processed": 2,
        "frontier_frame": 1,
        "source_sha256": "a" * 64,
        "proxy_sha256": "b" * 64,
    }
    info.update(changes or {})
    (tmp_path / "session.json").write_text(json.dumps({"session_id": "S", "source": {"uri": "source.mp4"}}))
    (tmp_path / "inference.json").write_text(json.dumps(info))
    (tmp_path / "predicted_rallies.csv").write_text("existing actual export")
    outer = {**parent(), "status": "completed", "worker_exit_code": 0, "frozen_source_inputs_unchanged": True}
    tmp_path.with_suffix(".executor.json").write_text(json.dumps(outer))
    finished = FinishedInput(
        "production-full-upload",
        tmp_path / "plan.json",
        tmp_path / "inference.json",
        tmp_path / "session.json",
        tmp_path / "events.jsonl",
        tmp_path / "perception",
        media,
        {},
        {},
        "commit",
        {},
        "original catalogue",
        (),
        {"schema": "bound"} if catalogue else None,
    )
    monkeypatch.setattr(replay, "load_finished_input", lambda run, sid: finished)


def test_normal_gate_is_distinct_from_explicit_independent_recovery(tmp_path, monkeypatch):
    normal_gate_fixture(tmp_path, monkeypatch)
    bound = load_analysis_input(tmp_path, None)
    assert bound["completion_mode"] == "normal_completed_worker"
    assert bound["original_parent_status"] == "completed"
    assert bound["worker_info"]["cached_perception_used"] is False


@pytest.mark.parametrize(
    "changes,catalogue",
    [
        ({"cached_perception_used": True}, True),
        ({"frames_processed": 1}, True),
        ({"frontier_frame": 0}, True),
        ({"status": "failed"}, True),
        ({}, False),
    ],
)
def test_normal_gate_rejects_cached_partial_failed_or_uncatalogued_input(tmp_path, monkeypatch, changes, catalogue):
    normal_gate_fixture(tmp_path, monkeypatch, changes=changes, catalogue=catalogue)
    with pytest.raises(ValueError, match="completed fresh source-guarded"):
        load_analysis_input(tmp_path, None)
