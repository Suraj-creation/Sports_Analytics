"""Publish small evidence summaries only after completed fresh production inference."""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from itertools import pairwise
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.benchmarking.evaluate_rallies import evaluate, read_csv  # noqa: E402
from scripts.benchmarking.production_inference import digest, dump  # noqa: E402


def fmt(value):
    return "unavailable" if value is None else f"{value:.5g}"


def live_events(directory):
    rows = [json.loads(line) for line in (directory / "events.jsonl").open()]
    superseded = {row["supersedes"] for row in rows if row.get("supersedes")}
    return [row for row in rows if row["status"] != "retracted" and row["event_id"] not in superseded]


def verify_post_run(fresh, experiments, inference):
    import msgpack

    replay = experiments / "fresh_image_exit_semantic_check"
    replay_metadata = json.loads((replay / "replay_metadata.json").read_text())
    if not replay_metadata["baseline_interval_parity"] or not replay_metadata["source_unchanged"]:
        raise RuntimeError("fresh semantic replay did not reproduce the completed run")
    production_events, replay_events = live_events(fresh), live_events(replay)
    counts = {}
    for kind in ("rally_end", "contact"):

        def identity(row, event_kind=kind):
            return (
                row["frame_start"],
                row["frame_end"],
                row["payload"].get("end_reason") if event_kind == "rally_end" else None,
            )

        expected = sorted(identity(row) for row in production_events if row["type"] == kind)
        actual = sorted(identity(row) for row in replay_events if row["type"] == kind)
        if actual != expected:
            raise RuntimeError(f"fresh semantic replay differs for {kind}")
        counts[kind] = len(expected)
    alignment = json.loads((fresh / "proxy_alignment.json").read_text())
    if not alignment["decoded_timeline_matches_original"]:
        raise RuntimeError("fresh proxy/source timeline differs")
    caches = sorted((fresh / "runtime/sessions").glob("*/perception/*.msgpack"))
    cursor = 0
    camera_lost = 0
    views, calibrations = Counter(), Counter()
    for cache in caches:
        chunk = msgpack.unpackb(cache.read_bytes(), raw=False)
        if chunk["start"] != cursor or len(chunk["frames"]) != chunk["end"] - cursor + 1:
            raise RuntimeError(f"noncontiguous perception coverage: {cache}")
        if [row["f"] for row in chunk["frames"]] != list(range(cursor, chunk["end"] + 1)):
            raise RuntimeError(f"incorrect perception frame identities: {cache}")
        camera_lost += sum(bool(row["l"]) for row in chunk["frames"])
        views.update(row["v"] for row in chunk["frames"])
        calibrations.update(str(row["cs"]) for row in chunk["frames"])
        cursor = chunk["end"] + 1
    if cursor != inference["media"]["n_frames"]:
        raise RuntimeError("perception coverage does not span the complete video")
    case_index = fresh / "failure_cases/index.json"
    cases = json.loads(case_index.read_text())
    if cases["case_count"] != 40 or cases["false_positive_count"] != 4 or cases["misses"] != [23]:
        raise RuntimeError("fresh failure-case coverage differs from completed predictions")
    for case in cases["cases"]:
        folder = case_index.parent / case["case_id"]
        if digest(folder / "case.json") != case["manifest_sha256"]:
            raise RuntimeError(f"failure manifest changed: {folder}")
        for name in (
            "observations.msgpack",
            "events.jsonl",
            "fsm_trace.jsonl",
            "execution.log",
            "boundary_overlay.jpg",
        ):
            if not (folder / name).is_file() or not (folder / name).stat().st_size:
                raise RuntimeError(f"missing failure evidence: {folder / name}")
    result = {
        "source_video_filename": "Test1_Full_rev.mp4",
        "source_resolution": [1920, 1080],
        "source_duration_seconds": 575.6,
        "ground_truth_rally_count": 36,
        "frame_index_convention": "zero-origin source/proxy correspondence; no fitted offset",
        "endpoint_convention": "boundary timestamp spans [start,end); no inclusive extra frame",
        "semantic_replay": {
            "mode": "recorded-perception replay; not a second fresh model-inference run",
            "directory": str(replay.relative_to(ROOT)),
            "exact_interval_and_end_reason_count": counts["rally_end"],
            "exact_live_contact_timestamp_count": counts["contact"],
            "trace_sha256": digest(replay / "fsm_trace.jsonl"),
        },
        "proxy_alignment": alignment,
        "perception_cache_files": len(caches),
        "contiguous_perception_frames": cursor,
        "missing_perception_frame_indices": 0,
        "camera_lost_frames": camera_lost,
        "view_counts": dict(views),
        "calibration_counts": dict(calibrations),
        "failure_case_index_sha256": digest(case_index),
        "failure_case_index": cases,
        "full_gpu_inference_repeat_count": 1,
    }
    dump(fresh / "post_run_validation.json", result)
    return result


def main():
    frozen = ROOT / "outputs/benchmarking/test1"
    experiments = ROOT / "artifacts/benchmarking/experiments"
    fresh = experiments / "fresh_image_exit_v1"
    metadata = json.loads((fresh / "benchmark_metadata.json").read_text())
    if metadata["status"] != "completed":
        raise RuntimeError("fresh full-video inference is not complete")
    for name, sha in metadata["source_hashes"].items():
        if digest(ROOT / name) != sha:
            raise RuntimeError(f"production source differs from the measured fresh run: {name}")
    if digest(ROOT / "research/run_pipeline_experiment.py") != metadata["runner_sha256"]:
        raise RuntimeError("fresh inference wrapper changed after the measured run")
    lock = json.loads((ROOT / "research/evidence_registry.json").read_text())
    for name, sha in lock["baseline_files_sha256"].items():
        if digest(ROOT / name) != sha:
            raise RuntimeError(f"immutable baseline changed: {name}")
    if digest(ROOT / "data/benchmarking/test1/Test1_Full_rev.mp4") != lock["original_video_sha256"]:
        raise RuntimeError("original video changed")
    if digest(ROOT / metadata["ground_truth_path"]) != lock["ground_truth_sha256"]:
        raise RuntimeError("ground truth changed")
    for model in lock["models_verified"].values():
        if digest(ROOT / model["path"]) != model["sha256"]:
            raise RuntimeError("baseline model weights changed")
    inference = json.loads((fresh / "inference.json").read_text())
    if inference["frontier_frame"] != 17267 or inference["media"]["n_frames"] != 17268:
        raise RuntimeError("fresh video coverage incomplete")
    if subprocess.check_output(["git", "rev-parse", "main"], cwd=ROOT, text=True).strip() != lock["production_commit"]:
        raise RuntimeError("main no longer points to the frozen production commit")
    post_run = verify_post_run(fresh, experiments, inference)
    pred = read_csv(fresh / "predicted_rallies.csv", 30)
    if any(b.start_frame <= a.end_frame for a, b in pairwise(pred)):
        raise RuntimeError("overlapping or unordered primary intervals")
    comparison = json.loads((fresh / "comparison.json").read_text())
    baseline_metrics = json.loads((frozen / "metrics.json").read_text())
    selected = json.loads((fresh / "metrics.json").read_text())
    labels = read_csv(ROOT / metadata["ground_truth_path"], metadata["video_fps"])
    recomputed, _ = evaluate(labels, pred, metadata["video_fps"])
    if recomputed != selected or comparison["experiment"]["metrics"] != selected:
        raise RuntimeError("stored fresh metrics do not reproduce under the frozen evaluator")
    entries = [
        {
            "id": "frozen-production",
            "scope": "fresh full video (original baseline)",
            "path": str(frozen.relative_to(ROOT)),
            "metrics": baseline_metrics,
        }
    ]
    for parent, scope in [
        (experiments / "fsm_correctness", "fixed recorded FSM inputs"),
        (experiments / "evidence_ablations", "fixed recorded evidence; first factorial"),
        (experiments / "image_exit_factorial", "fixed recorded evidence; extended factorial"),
        (experiments / "image_exit_factorial_verified", "fixed recorded evidence; verified extended factorial"),
    ]:
        for path in sorted(parent.glob("*/metrics.json")):
            entries.append(
                {
                    "id": f"{parent.name}/{path.parent.name}",
                    "scope": scope,
                    "path": str(path.parent.relative_to(ROOT)),
                    "metrics": json.loads(path.read_text()),
                }
            )
    semantic = experiments / "evidence_feature_replay_v1/metrics.json"
    entries.append(
        {
            "id": "evidence_feature_replay_v1",
            "scope": "recorded-perception semantic replay; rejected combined signals",
            "path": str(semantic.parent.relative_to(ROOT)),
            "metrics": json.loads(semantic.read_text()),
            "acceptance": False,
        }
    )
    pilot = experiments / "reconstruction_semantic/metrics.json"
    entries.append(
        {
            "id": "generic-interpolation-pilot",
            "scope": "rejected pilot; source validation changed mid-run",
            "path": str(pilot.parent.relative_to(ROOT)),
            "metrics": json.loads(pilot.read_text()),
            "acceptance": False,
        }
    )
    entries.append(
        {
            "id": fresh.name,
            "scope": "fresh full original video",
            "path": str(fresh.relative_to(ROOT)),
            "metrics": selected,
            "prediction_sha256": digest(fresh / "predicted_rallies.csv"),
            "configuration": metadata["configuration"]["components"]["rally"],
        }
    )
    dump(
        ROOT / "research/experiment_results.json",
        {
            "development_only": True,
            "independent_generalization_verified": False,
            "baseline_integrity_verified_files": len(lock["baseline_files_sha256"]),
            "original_video_sha256": lock["original_video_sha256"],
            "ground_truth_sha256": lock["ground_truth_sha256"],
            "fresh_source_commit": metadata["git_commit_sha"],
            "summary_generator_sha256": digest(Path(__file__)),
            "experiments": entries,
            "fresh_runtime": inference,
            "fresh_model_fallback": inference["degraded"],
            "fresh_post_run_validation": post_run,
            "component_only_experiment": str((experiments / "tracknet_window_pair").relative_to(ROOT)),
        },
    )
    lines = [
        "# Final Test 1 pipeline investigation and benchmark",
        "",
        "This is an exploratory development benchmark on one exposed source, not held-out validation. "
        "The original video, all 36 labels, matching policy and frozen baseline remain unchanged.",
        "",
        f"Fresh full-video candidate completed at production source `{metadata['git_commit_sha']}`. "
        f"All {len(lock['baseline_files_sha256'])} frozen artifact hashes, original media/CSV hashes and "
        "active checkpoint bytes were rechecked. The final prediction CSV has exactly seven columns.",
        "",
        "## Dataset and conventions",
        "",
        "The sole source is `Test1_Full_rev.mp4`: 1920 × 1080, 30 FPS, 17,268 decoded frames, "
        "575.6 seconds. Production uses its normal 1280 × 720 CFR proxy; the original is unmodified. "
        "Ground truth is `Part2/dataset/Test1_Full/Test1_Full_rally.csv`, with 36 intervals and exactly "
        "`Start_Frame,End_Frame,Start_Time_sec,End_Time_sec,Duration_sec,Start_Time,End_Time`.",
        "",
        "Frame indices use the established zero-origin arithmetic convention, seconds=frame/30, "
        "duration=end timestamp−start timestamp. Human-readable MM:SS truncates to whole seconds. "
        "The evaluator measures timestamp spans [start,end), without an inclusive extra frame; "
        "production event payload duration is not substituted for that span. The unavailable human "
        "annotation-tool history leaves possible one-frame physical-boundary ambiguity. No offset "
        "was fitted and no annotations were changed.",
        "",
        f"Source SHA256: `{lock['original_video_sha256']}`. Annotation SHA256: `{lock['ground_truth_sha256']}`.",
        "",
        "## Diagnosis and implementation",
        "",
        "Seven independent audits, an exact 49-interval/end-reason/432-live-contact baseline replay and "
        "55 baseline diagnostic packages preceded production edits. See root_cause_analysis.md, "
        "improvement_strategy.md, experiment_matrix.md and implementation_roadmap.md for evidence, "
        "alternative explanations, risks and ownership.",
        "",
        "Implemented separately: parameter-sized stationary history; post-contact history rebasing; "
        "recovery based on observed motion onset rather than confirmation; injected model-root correctness; "
        "an optional typed sport-owned observation/provider retaining observed/reconstructed/missing/invalid "
        "distinctions and legacy compatibility; strict frame-aligned participant-motion and reconstruction "
        "quality helpers; bounded observed image-exit/re-entry support; isolated experiment/resource reporting.",
        "",
        "Selected provider: `rally-evidence-v2`, image-exit recovery enabled, generic reconstruction and "
        "motion guards disabled. The regular GPU profile remains unchanged. The explicit exploratory "
        "profile is config/profiles/gpu-rtx4000-rally-evidence.yaml. No detector/pose/racket/outcome/scoring "
        "capability was removed, and no weight/environment replacement was performed.",
        "",
        "Production entry point: `SessionRunner._ensure_media` then `SessionRunner._analyse`, using "
        "the normal `BadmintonSession`/perception/`BadmintonMatchEngine` chain. The research wrapper "
        "isolates output and records resources; it does not substitute predictions or consume labels "
        "inside inference. TrackNetV3 remains 512 × 288, eight-frame windows, step8, threshold0.5, "
        "batch4, CUDA FP16. RF-DETR Small, RTMPose M Body7, geometric racket/contact and production "
        "analytics remain active. The effective configuration and actual backend records are "
        "preserved in each experiment's metadata/inference JSON.",
        "",
        "Verified unchanged active checkpoint artifacts:",
        "",
        "| Artifact | SHA256 |",
        "| --- | --- |",
    ]
    for model in lock["models_verified"].values():
        lines.append(f"| `{model['path']}` | `{model['sha256']}` |")
    lines += [
        "",
        "## Baseline versus fresh production inference",
        "",
        "| Metric | Frozen baseline | Fresh candidate |",
        "| --- | --- | --- |",
    ]
    for key in ("predicted_count", "true_positives", "false_positives", "false_negatives", "precision", "recall", "f1"):
        lines.append(f"| {key} | {fmt(baseline_metrics['detection'][key])} | {fmt(selected['detection'][key])} |")
    for key in ("start_time_sec", "end_time_sec", "duration_sec"):
        for stat in ("mae", "rmse", "median_absolute_error", "mean_signed_error"):
            before = baseline_metrics["boundary_and_duration_errors"][key][stat]
            after = selected["boundary_and_duration_errors"][key][stat]
            lines.append(f"| {key}.{stat} (seconds) | {fmt(before)} | {fmt(after)} |")
    for key in ("mean_iou", "median_iou", "minimum_iou"):
        lines.append(f"| {key} | {fmt(baseline_metrics['overlap'][key])} | {fmt(selected['overlap'][key])} |")
    lines += [
        "",
        "The start median worsened from 23 to 29 frames, and maximum start error from 202 to 297 frames. "
        "GT31 is newly matched but still starts 9.9 seconds late. GT27 still ends 218 frames early; "
        "GT23 remains missed. Common matched rows GT4 and GT22 have worse starts. These are unresolved "
        "failures, even though aggregate detection and end-boundary quality improve.",
        "",
        "## Every rally experiment",
        "",
        "All rows use the frozen maximum-cardinality one-to-one assignment, IoU>=0.5 and the same "
        "boundary-span convention. Conditional errors and IoU must be read with TP/FP/FN.",
        "",
        "| Experiment | Evidence scope | Pred | TP | FP | FN | F1 | Start MAE frames | End MAE frames | Mean IoU |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for entry in entries:
        m = entry["metrics"]
        d, e = m["detection"], m["boundary_and_duration_errors"]
        lines.append(
            f"| {entry['id']} | {entry['scope']} | {d['predicted_count']} | {d['true_positives']} | "
            f"{d['false_positives']} | {d['false_negatives']} | {d['f1']:.4f} | {fmt(e['start_frame']['mae'])} | "
            f"{fmt(e['end_frame']['mae'])} | {fmt(m['overlap']['mean_iou'])} |"
        )
    lines += [
        "",
        "The verified factorial repeats preserve the earlier predictions/metrics while fixing ambiguous "
        "inherited provenance and separately measuring the FSM loop. They are repeats, not independent datasets. "
        "The generic pilot is rejected, including its incorrect adjacent-rally join. Motion guarding is "
        "rejected despite higher conditional IoU because it loses recall. Contact-history correctness "
        "alone is not claimed as an accuracy gain. All original artifacts remain available.",
        "",
        "Actual paired TrackNet inference compared 2160 frames/strategy on GPU1: step8/4 accepted 1582/1567 "
        "detections in 20.355/29.722 seconds (1.46× component cost), with the upper-image gap still 0/17 for both. "
        "It uses fixed background/context and measures continuity, not localization accuracy or a full "
        "rally benchmark. No alternative backbone or new weights were adopted. See shuttle_model_comparison.md "
        "for primary-source code/weight/data license separation and measured/unmeasured alternatives.",
        "",
        "## Fresh boundary and duration detail",
        "",
        "| Quantity | MAE | RMSE | Median absolute | Signed bias | P90 absolute | Maximum absolute |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for key, stats in selected["boundary_and_duration_errors"].items():
        lines.append(
            "| "
            + key
            + " | "
            + " | ".join(
                fmt(stats[k])
                for k in [
                    "mae",
                    "rmse",
                    "median_absolute_error",
                    "mean_signed_error",
                    "p90_absolute_error",
                    "max_absolute_error",
                ]
            )
            + " |"
        )
    lines += [
        "",
        f"Interval overlap: `{json.dumps(selected['overlap'], sort_keys=True)}`.",
        "",
        "Raw IoU and duration distributions, all-GT coverage, fragmentation, no-overlap predictions, "
        "merge/split topology and every missed/extra interval are in comparison.json/metrics.json. "
        "The comparison CSV contains all 36 ground-truth rows, preserving null errors for misses.",
        "",
        "| Tolerance | Seconds | Start count | Start / matched | Start / all GT | "
        "End count | End / matched | End / all GT |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    matched = selected["detection"]["matched_count"]
    for a, b in zip(selected["boundary_tolerances"]["start"], selected["boundary_tolerances"]["end"], strict=True):
        lines.append(
            f"| ±{a['frames']} frames | {a['seconds']:.5g} | {a['within_count']}/{matched} | "
            f"{fmt(a['matched_accuracy'])} | {fmt(a['all_gt_accuracy'])} | {b['within_count']}/{matched} | "
            f"{fmt(b['matched_accuracy'])} | {fmt(b['all_gt_accuracy'])} |"
        )
    lines += [
        "",
        "## Fragmentation and evidence completeness",
        "",
        "| Diagnostic | Frozen baseline | Fresh candidate |",
        "| --- | --- | --- |",
    ]
    for key in ("gt_with_multiple_predictions_count", "predictions_without_gt_overlap_count"):
        lines.append(
            f"| {key} | {comparison['baseline']['fragmentation'][key]} | "
            f"{comparison['experiment']['fragmentation'][key]} |"
        )
    lines += [
        "",
        "Fresh multi-segment labels are 23, 27 and 31. The sole unmatched label (23) has partial "
        "predicted coverage. All four unmatched predictions overlap annotated play; their IoUs/matching "
        "remain insufficient or another segment owns the one-to-one match. No false positive was hidden.",
        "",
        f"All {post_run['contiguous_perception_frames']} perception frame identities are contiguous in "
        f"{post_run['perception_cache_files']} cache chunks: no decoded/perception frame indices are missing. "
        f"Camera-lost state is separately recorded on {post_run['camera_lost_frames']} frames; it does "
        "not mean those video frames were dropped. Complete original/proxy PTS grids agree.",
        "",
        "Forty fresh diagnostic packages contain all 36 labels and four extra predictions, source-frame "
        "overlays, raw shuttle/player/pose observations, inferred contact events, logs and exact FSM "
        "transitions. The fresh observations replay to exactly 39 intervals/end reasons and 447 live "
        "contact timestamps. This establishes semantic reproduction; only one independent fresh GPU "
        "run was performed, so full model-inference determinism is not established. See "
        "fresh_image_exit_v1/post_run_validation.json and failure_cases/index.json for hashes and provenance.",
    ]
    lines += [
        "",
        "## Failure resolution and limitations",
        "",
        f"Fresh missed GT rows: {selected['missed_gt_rallies']}. "
        f"Unmatched predictions: {len(selected['unmatched_predictions'])}. "
        "See regression_report.md for every common/new match, worsened boundary and unresolved severe outlier. "
        "A newly matched partial interval can increase maximum conditional error; this is reported rather "
        "than hidden behind F1. remaining_failure_review.md records source-frame observations around "
        "the unresolved same-camera edit/preparation and mixed physical/model visibility losses. "
        "Visual diagnostics do not authorize changing the supplied annotations.",
        "",
        "The new cue is bounded by two observed moving brackets, top 10% image exit/re-entry, at most 2 seconds, "
        "existing speed bounds and the same temporal context. It cannot start an exchange, generate a "
        "contact, fill coordinates, cross a signaled discontinuity, or recover an already published interval. "
        "Its availability "
        "depends on actual future anchors within the existing 40-frame-minimum window; no future evidence "
        "was invented and no hidden lookahead increase occurred. Physical nonvisibility, poor model "
        "localization and uncertain annotation start semantics remain distinct limitations.",
        "",
        "OSNet/ReID remains explicitly unavailable at startup; no embeddings or named players were fabricated. "
        "All related analytics still execute, but no unlabeled contact, winner, score or shot accuracy is "
        "claimed. Real evidence here is singles footage; four-player tests establish contracts, not real "
        "doubles quality. Pretrained model training overlap with Test1 is unknown. "
        "No independent generalization is proven.",
        "",
        "## Runtime and reliability",
        "",
        f"Fresh whole-run inference time: {inference['elapsed_seconds']:.3f}s; "
        f"{inference['frames_per_second']:.4f} frames/s; final frame {inference['frontier_frame']}. "
        "The CPU regression suite overlapped startup, so baseline/fresh walltime is not an isolated "
        "algorithm-cost experiment. No speedup is claimed.",
        "",
        "Per-stage wall aggregates overlap and must not be summed:",
        "",
        "```json",
        json.dumps(inference["per_stage_seconds"], indent=2),
        "```",
        "",
        "Measured resource scopes and sampling:",
        "",
        "```json",
        json.dumps(inference["resources"], indent=2),
        "```",
        "",
        "Baseline CPU/RSS/GPU peaks and per-stage totals were not recorded and remain unavailable. "
        "Actual model runtime/fallback/checkpoint records are in inference.json and benchmark_metadata.json; "
        "TrackNet is CUDA FP16. ONNX session CUDA-provider ordering does not prove every graph node or "
        "tensor is CUDA FP16. Original and fresh source/proxy alignment audits remain separate from browser/HLS "
        "mux-origin observations.",
        "",
        "## Reproduction and next work",
        "",
        "```bash",
        "source ../gpu-env.sh",
        "python research/run_pipeline_experiment.py --output artifacts/benchmarking/experiments/NEW_RUN \\",
        "  --rally-implementation rally-evidence-v2 \\",
        '  --rally-params \'{"use_reconstruction":false,"motion_guard":false,"use_exit_recovery":true}\'',
        "```",
        "",
        "Use a new directory; existing runs are never overwritten. Tests and exact commands are in "
        "component_test_report.md. Predictions and all raw observations/events/resources/logs remain at "
        "artifacts/benchmarking/experiments/fresh_image_exit_v1/. Only small reports/results are versioned.",
        "",
        "Highest-impact next work: independently review the remaining hard-edit and start-convention cases; "
        "label shuttle visibility/location around early misses and static attractors; test background/context "
        "and candidate association independently; collect match-disjoint amateur/doubles/cut footage before "
        "promotion. Do not expand a generic merge budget or fit a temporal model on these 36 intervals and "
        "describe it as held-out performance. Main and the frozen baseline remain untouched.",
        "",
    ]
    (ROOT / "research/final_benchmark_report.md").write_text("\n".join(lines))
    print("Fresh report and immutable-evidence verification complete")


if __name__ == "__main__":
    main()
