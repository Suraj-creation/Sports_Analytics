"""Exact timestamp/provenance guards; no sporting accuracy claims."""

import csv
from fractions import Fraction
from types import SimpleNamespace

import pytest

from research.test2_failure_package import case_ranges, finite_json, merge_ranges, sha, verified_pts, verify_replay


def pts_file(tmp_path, frames=3, offset=0):
    path = tmp_path / "source_frame_pts.csv"
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["source_frame", "pts", "time_base_num", "time_base_den", "source_time_sec"])
        for frame in range(frames):
            writer.writerow([frame, frame * 512 + offset, 1, 15360, "ignored-display-value"])
    return path


def test_exact_pts_uses_rational_integer_values_and_full_ordered_coverage(tmp_path):
    result = verified_pts(pts_file(tmp_path), 3, Fraction(30))
    assert result[2] == (1024, Fraction(1, 15360))


@pytest.mark.parametrize("mismatch", ["offset", "short", "fps"])
def test_offset_truncated_and_differing_rate_source_maps_are_rejected(tmp_path, mismatch):
    path = pts_file(tmp_path, frames=2 if mismatch == "short" else 3, offset=1 if mismatch == "offset" else 0)
    with pytest.raises(ValueError, match="source PTS map"):
        verified_pts(path, 3, Fraction(25 if mismatch == "fps" else 30))


def proof_fixture(tmp_path):
    report = tmp_path / "inference.json"
    report.write_text("completed actual report")
    trace = tmp_path / "bounded_fsm_trace.jsonl"
    trace.write_text("recorded actual trace")
    recorded = SimpleNamespace(media={"n_frames": 3}, report_path=report, expected_caches={"seg": "cache"})
    proof = {
        "schema": "cached-external-semantic:v2",
        "baseline_parity": True,
        "geometry_bracket": False,
        "contact_motion_reliability": False,
        "no_GT_or_neural_model_input": True,
        "session_id": "TEST2",
        "source_report_sha256": sha(report),
        "cache_sha256": {"seg": "cache"},
        "frames": 3,
        "trace_step_count": 3,
        "output_artifact_sha256": {trace.name: sha(trace)},
    }
    rows = [{"call": "step", "frame": f} for f in range(3)]
    return proof, recorded, trace, rows


def test_actual_baseline_cache_report_and_trace_binding_is_required(tmp_path):
    proof, recorded, trace, rows = proof_fixture(tmp_path)
    verify_replay(proof, recorded, trace, rows, "TEST2")
    trace.write_text("modified trace")
    with pytest.raises(ValueError, match="trace digest"):
        verify_replay(proof, recorded, trace, rows, "TEST2")


@pytest.mark.parametrize(
    "field,value",
    [
        ("baseline_parity", False),
        ("geometry_bracket", True),
        ("cache_sha256", {"other": "cache"}),
        ("session_id", "TEST1"),
    ],
)
def test_nonbaseline_or_borrowed_evidence_is_rejected(tmp_path, field, value):
    proof, recorded, trace, rows = proof_fixture(tmp_path)
    proof[field] = value
    with pytest.raises(ValueError, match="own-source"):
        verify_replay(proof, recorded, trace, rows, "TEST2")


def test_duplicate_missing_or_reordered_semantic_steps_cannot_pass(tmp_path):
    proof, recorded, trace, rows = proof_fixture(tmp_path)
    with pytest.raises(ValueError, match="every ordered"):
        verify_replay(proof, recorded, trace, rows[::-1], "TEST2")


def test_each_unmatched_failure_gets_all_overlap_boundaries_and_full_context():
    case = {
        "matching_status": "missed",
        "gt_start_frame": 100,
        "gt_end_frame": 400,
        "positive_overlap_prediction_ids": [1, 2],
    }
    windows, context = case_ranges(
        case, [{"start_frame": 150, "end_frame": 200}, {"start_frame": 250, "end_frame": 390}], 500
    )
    for frame in (100, 150, 200, 250, 390, 400):
        assert any(lo <= frame < hi for lo, hi in windows)
    assert context == (55, 446)
    assert windows == merge_ranges(windows)


def test_nonfinite_diagnostic_values_are_explicit_nulls_not_invented_coordinates():
    assert finite_json({"x": float("nan"), "y": float("inf"), "raw": [None, 2]}) == {
        "x": None,
        "y": None,
        "raw": [None, 2],
    }


def test_unmatched_prediction_context_includes_each_overlapping_reference_boundary():
    case = {
        "matching_status": "unmatched_prediction",
        "start_frame": 150,
        "end_frame": 160,
        "positive_overlap_gt_ids": [1],
    }
    windows, context = case_ranges(case, [], 500, [{"start_frame": 100, "end_frame": 400}])
    assert context == (55, 446)
    assert all(any(lo <= frame < hi for lo, hi in windows) for frame in (100, 150, 160, 400))


def test_package_decodes_own_synthetic_source_pts_and_writes_all_case_evidence(tmp_path, monkeypatch):
    import json

    import av
    import cv2
    import msgpack
    import numpy as np

    from research import production_external_semantic_replay as replay_module
    from research.test2_failure_package import build
    from scripts.benchmarking.evaluate_rallies import write_predictions

    source = tmp_path / "source.mp4"
    writer = cv2.VideoWriter(str(source), cv2.VideoWriter_fourcc(*"mp4v"), 30, (32, 24))
    assert writer.isOpened()
    for color in (30, 120, 210):
        writer.write(np.full((24, 32, 3), color, np.uint8))
    writer.release()
    pts = tmp_path / "pts.csv"
    with av.open(str(source)) as container, pts.open("w", newline="") as stream:
        video = container.streams.video[0]
        csv_writer = csv.writer(stream)
        csv_writer.writerow(["source_frame", "pts", "time_base_num", "time_base_den", "source_time_sec"])
        for index, frame in enumerate(container.decode(video)):
            csv_writer.writerow(
                [
                    index,
                    frame.pts,
                    video.time_base.numerator,
                    video.time_base.denominator,
                    float(frame.pts * video.time_base),
                ]
            )
    run, replay, evaluation = (tmp_path / name for name in ("run", "replay", "evaluation"))
    for directory in (run, replay, evaluation):
        directory.mkdir()
    report = run / "inference.json"
    report.write_text(json.dumps({"source_sha256": sha(source), "proxy_sha256": "proxy"}))
    events = run / "events.jsonl"
    events.write_text("")
    write_predictions(run / "predicted_rallies.csv", [(0, 2)], 30)
    cache = run / "perception"
    cache.mkdir()
    raw = [
        {"f": frame, "s": [1, 2], "c": 0.8, "p": [], "cs": "VALID", "v": "main", "g": [1, 0, 0, 0, 1, 0, 0, 0, 1]}
        for frame in range(3)
    ]
    cache_file = cache / "seg.msgpack"
    cache_file.write_bytes(msgpack.packb({"frames": raw}, use_bin_type=True))
    traces = [
        {
            "call": "step",
            "frame": frame,
            "before": {"state": "idle"},
            "after": {"state": "idle"},
            "update": {},
            "observation": {"kind": "observed"},
            "processed_xy": [1, 2],
        }
        for frame in range(3)
    ]
    trace = replay / "bounded_fsm_trace.jsonl"
    trace.write_text("".join(json.dumps(row) + "\n" for row in traces))
    for filename in replay_module.REPLAY_OUTPUT_ARTIFACTS:
        (replay / filename).write_text("[]")
    recorded = SimpleNamespace(
        media={"n_frames": 3, "fps_num": 30, "fps_den": 1, "width": 32, "height": 24},
        report_path=report,
        events_path=events,
        expected_caches={cache_file.name: sha(cache_file)},
        cache_directory=cache,
    )
    proof = {
        "schema": "cached-external-semantic:v2",
        "baseline_parity": True,
        "geometry_bracket": False,
        "contact_motion_reliability": False,
        "no_GT_or_neural_model_input": True,
        "session_id": "TEST2",
        "source_report_sha256": sha(report),
        "cache_sha256": recorded.expected_caches,
        "frames": 3,
        "trace_step_count": 3,
        "trace_ranges_telemetry_only": [[0, 3]],
        "output_artifact_sha256": replay_module.replay_output_hashes(replay, trace=True),
    }
    (replay / "replay_manifest.json").write_text(json.dumps(proof))
    monkeypatch.setattr(replay_module, "load_finished_input", lambda run, sid: recorded)
    case = {"case_id": "pred_001", "matching_status": "unmatched_prediction", "start_frame": 0, "end_frame": 2}
    (evaluation / "supplemental_metrics.json").write_text(
        json.dumps(
            {
                "failure_cases": [case],
                "provenance": {
                    str((run / "predicted_rallies.csv").resolve()): sha(run / "predicted_rallies.csv"),
                    str(report.resolve()): sha(report),
                },
            }
        )
    )
    (evaluation / "per_rally_comparison.csv").write_text("gt_start_frame,gt_end_frame\n")
    output = tmp_path / "package"
    manifest = build(run, "TEST2", replay, source, pts, evaluation, output)
    assert manifest["source_images"] == 3
    assert manifest["failure_count"] == 1
    assert manifest["original_source_pts_exact"] is True
    assert len(list((output / "frames").glob("*.jpg"))) == 3
    case_output = json.loads((output / "cases/pred_001.json").read_text())
    assert len(case_output["raw_perception"]) == 3
    assert len(case_output["semantic_trace"]) == 3
    assert case_output["diagnostic_summary"]["first_processed_observation_frame"] == 0
    assert "__DATA__" not in (output / "index.html").read_text()
    from research.test2_source_frame_cache import prepare

    frame_cache = tmp_path / "source_frame_cache"
    prepare(source, pts, frame_cache, 3, Fraction(30))
    copied_output = tmp_path / "package_copied_images"
    copied = build(run, "TEST2", replay, source, pts, evaluation, copied_output, source_frames=frame_cache)
    assert copied["source_frame_cache"]["selected_images_verified_and_copied"] == 3
    assert copied["source_frame_cache"]["transform"]["jpeg_quality"] == 88
    for frame in range(3):
        assert (copied_output / f"frames/{frame}.jpg").read_bytes() == (
            frame_cache / f"frames/{frame}.jpg"
        ).read_bytes()
