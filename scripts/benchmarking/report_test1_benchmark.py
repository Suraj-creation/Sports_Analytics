"""Build the Test 1 report and diagnostic boundary evidence after real inference."""

from __future__ import annotations

import argparse
import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.benchmarking.evaluate_rallies import read_csv  # noqa: E402
from scripts.benchmarking.production_inference import dump  # noqa: E402


def number(value):
    return "unavailable" if value is None else f"{value:.6g}"


def build_report(output):
    import msgpack

    metadata = json.loads((output / "benchmark_metadata.json").read_text())
    if metadata["status"] != "completed":
        raise RuntimeError("a completed, verified inference run is required for a results report")
    metrics = json.loads((output / "metrics.json").read_text())
    inference = json.loads((output / "inference.json").read_text())
    fps = metadata["video_fps"]
    annotations = ROOT / metadata["ground_truth_path"]
    gt = read_csv(annotations, fps)
    with (output / "rally_comparison.csv").open() as stream:
        comparisons = list(csv.DictReader(stream))
    frames = {}
    for path in sorted((output / "runtime/sessions/BenchmarkTest1/perception").glob("*.msgpack")):
        chunk = msgpack.unpackb(path.read_bytes(), raw=False)
        frames.update({f["f"]: f for f in chunk["frames"]})
    if len(frames) != metadata["frame_count"]:
        raise RuntimeError("diagnostic perception evidence does not cover every source frame")
    diagnostics = []
    for i, rally in enumerate(gt):
        selected = [frames[f] for f in range(rally.start_frame, rally.end_frame + 1)]
        # Diagnostic raw perception only: not a reconstruction of the downstream
        # spike-filtered/coordinate-stabilized FSM observations or a second detector.
        visible = sum(f["s"] is not None for f in selected)
        views = dict(collections.Counter(f["v"] or "unspecified" for f in selected))
        overlapping = [
            e for e in inference["rally_events"] if e["start"] <= rally.end_frame and e["end"] >= rally.start_frame
        ]
        diagnostics.append(
            {
                "gt_rally": i + 1,
                "matching_status": comparisons[i]["matching_status"],
                "frames_inclusive": len(selected),
                "raw_shuttle_observed_frames": visible,
                "raw_shuttle_observed_fraction": visible / len(selected),
                "view_counts": views,
                "calibration_state_counts": dict(collections.Counter(f["cs"] or "unspecified" for f in selected)),
                "camera_lost_frames": sum(f["l"] for f in selected),
                "replay_flag_frames": sum(f["r"] for f in selected),
                "overlapping_production_segments": overlapping,
            }
        )
    dump(output / "boundary_diagnostics.json", diagnostics)
    d = metrics["detection"]
    lines = [
        "# Test 1 rally boundary benchmark",
        "",
        f"Real full-video production inference completed on `{metadata['active_branch']}` at production commit "
        f"`{metadata['git_commit_sha']}`. This report evaluates rally starts and ends only.",
        "",
        "## A. Dataset",
        "",
        f"Original: `{metadata['source_video_filename']}`, {metadata['resolution'][0]}×{metadata['resolution'][1]}, "
        f"{fps:g} FPS, {metadata['frame_count']} decoded frames, {metadata['duration_seconds']:g} seconds. "
        "The only downloaded video is the original Test 1 file (1,026,166,541 bytes). "
        "No original transcoding or trimming was performed.",
        "",
        f"Source SHA-256: `{metadata['source_video_sha256']}`.",
        "",
        f"Ground truth: `{metadata['ground_truth_path']}`, 36 manually annotated intervals as identified by the user. "
        f"SHA-256: `{metadata['ground_truth_sha256']}`. All seven columns were validated; annotations were not edited.",
        "",
        "`Start_Frame` and `End_Frame` are rally boundary frame indices; `Start_Time_sec` and `End_Time_sec` "
        "are the corresponding seconds; `Duration_sec` is end minus start; `Start_Time` and `End_Time` are "
        "MM:SS truncated to whole seconds. Source FPS was independently measured. Packet PTS and full decode "
        "establish a zero-origin CFR grid; the related Part2 shuttle file enumerates the same 0..17267 frames. "
        "No frame offset was fitted. Original annotation-tool history is unavailable, so a possible one-frame "
        "human labeling convention remains a limitation. Boundary-span IoU/duration use [start time,end time), "
        "without adding one inclusive frame.",
        "",
        "## B. Production configuration",
        "",
        "Entry point: `bai_engine.runtime.runner.SessionRunner._ensure_media()` and `_analyse()` in a fresh "
        "isolated repository. The host selects the existing badminton plugin, VOD TrackNetV3, and "
        "`rally-fsm-v1`. The normal 720p CFR proxy is analyzed. All current final `rally_end` events are exported, "
        "including non-official exchanges; outcomes, scoring and shot count never filter predictions.",
        "",
        f"Frozen profile: `{metadata['pipeline_configuration']['profile']}`; "
        f"SHA-256 `{metadata['pipeline_configuration']['profile_sha256']}`. "
        f"Actual full-video inference elapsed time: {inference['elapsed_seconds']:.1f} seconds. "
        f"Final processed frame: {inference['frontier_frame']}.",
        "",
        "TrackNetV3: 512×288, 8-frame non-overlapping windows, step 8, threshold 0.5, batch 4, "
        "CUDA FP16. RF-DETR Small, RTMPose M Body7 and geometric racket/contact evidence remain in the "
        "production composition. Format is inferred by the production layer. See `PIPELINE_TRACE.md` for "
        "the complete upstream path and gates.",
        "",
        "FSM defaults: start after 3 observed moving frames >3 px/frame or accepted contact; end after "
        "10 invisible frames or 7/10 stationary observations <3 px/frame; 15-frame lookahead; "
        "resume >6 px/frame; minimum duration 2 seconds; merge gap 0.75 seconds. "
        "The match engine uses 40-frame lookahead and 45-frame backward context. No tuning was performed.",
        "",
        "Actual execution backends from the loaded component runtime records "
        "(the legacy inspection helper could not unwrap the shuttle port):",
        "",
        "```json",
        json.dumps(
            {k: inference["perception_runtimes"].get(k) for k in ("shuttle", "player_detector", "pose")}, indent=2
        ),
        "```",
        "",
        "Model/checkpoint identifiers and actual runtime fingerprints are in `inference.json` and "
        "`benchmark_metadata.json`, including TrackNet checkpoint digest, RF-DETR/pose pins and OCR-stage hashes.",
        "",
        "Recorded degradation:",
        "",
        "```json",
        json.dumps(inference["degraded"], indent=2),
        "```",
        "",
        "## C. Results",
        "",
        "Matching was frozen before inference: maximum-cardinality one-to-one bipartite assignment of "
        "pairs with temporal IoU ≥0.5, then maximum total IoU with a tiny boundary-proximity preference. "
        "Rows are never matched by index. Boundary metrics condition on those eligible matches.",
        "",
        "| Ground truth | Predictions | Matched / TP | FP | FN | Precision | Recall | F1 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
        f"| {d['ground_truth_count']} | {d['predicted_count']} | {d['matched_count']} | {d['false_positives']} | "
        f"{d['false_negatives']} | {d['precision']:.4f} | {d['recall']:.4f} | {d['f1']:.4f} |",
        "",
        "Signed errors are prediction minus annotation. Timing errors use precise seconds, not MM:SS.",
        "",
        "| Boundary / unit | MAE | Median absolute | RMSE | Maximum absolute | P90 absolute |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for key in ("start_frame", "start_time_sec", "end_frame", "end_time_sec"):
        values = metrics["boundary_and_duration_errors"][key]
        lines.append(
            "| "
            + key
            + " | "
            + " | ".join(
                number(values[k])
                for k in ("mae", "median_absolute_error", "rmse", "max_absolute_error", "p90_absolute_error")
            )
            + " |"
        )
    duration = metrics["boundary_and_duration_errors"]["duration_sec"]
    lines += [
        "",
        f"Duration (seconds): MAE {number(duration['mae'])}; RMSE {number(duration['rmse'])}; "
        f"median absolute error {number(duration['median_absolute_error'])}; "
        f"mean signed error {number(duration['mean_signed_error'])}; "
        f"median signed error {number(duration['median_signed_error'])}.",
        "",
        "Interval overlap:",
        "",
        "```json",
        json.dumps(metrics["overlap"], indent=2),
        "```",
        "",
        "| Tolerance | Seconds | Starts within / matched | Start accuracy / all GT | "
        "Ends within / matched | End accuracy / all GT |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for start, end in zip(metrics["boundary_tolerances"]["start"], metrics["boundary_tolerances"]["end"], strict=True):
        lines.append(
            f"| ±{start['frames']} frames | {start['seconds']:.6g} | {start['within_count']}/{d['matched_count']} "
            f"({number(start['matched_accuracy'])}) | {number(start['all_gt_accuracy'])} | "
            f"{end['within_count']}/{d['matched_count']} ({number(end['matched_accuracy'])}) | "
            f"{number(end['all_gt_accuracy'])} |"
        )
    lines += [
        "",
        "## D. Failure analysis",
        "",
        f"Missed ground-truth rally IDs (one-based CSV rows): {metrics['missed_gt_rallies']}.",
        "",
        "Every label is represented in `rally_comparison.csv` with matched/missed status, signed and absolute "
        "frame errors, time errors, durations and IoU. False positives are listed below and separately in "
        "`metrics.json`; they are not discarded to force 36 rows.",
        "",
        "```json",
        json.dumps(metrics["unmatched_predictions"], indent=2),
        "```",
        "",
        "Matched boundaries exceeding ±15 frames:",
        "",
        "| GT rally | Pred rally | Start error (frames) | End error (frames) | IoU |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in comparisons:
        if (
            row["matching_status"] == "matched"
            and max(abs(float(row["start_frame_error"])), abs(float(row["end_frame_error"]))) > 15
        ):
            lines.append(
                f"| {row['gt_rally']} | {row['pred_rally']} | {row['start_frame_error']} | "
                f"{row['end_frame_error']} | {number(float(row['interval_iou']))} |"
            )
    lines += [
        "",
        "Per-label raw-perception diagnostic evidence:",
        "",
        "| GT rally | Match status | Raw observed shuttle fraction | Camera lost frames | "
        "Overlapping production segments / end reasons |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in diagnostics:
        segments = (
            "; ".join(f"{e['start']}–{e['end']} ({e['end_reason']})" for e in row["overlapping_production_segments"])
            or "none"
        )
        lines.append(
            f"| {row['gt_rally']} | {row['matching_status']} | {row['raw_shuttle_observed_fraction']:.3f} | "
            f"{row['camera_lost_frames']} | {segments} |"
        )
    reasons = dict(collections.Counter(e["end_reason"] for e in inference["rally_events"]))
    matched = [r for r in comparisons if r["matching_status"] == "matched"]
    late_starts = sum(float(r["start_frame_error"]) > 0 for r in matched)
    early_starts = sum(float(r["start_frame_error"]) < 0 for r in matched)
    early_ends = sum(float(r["end_frame_error"]) < 0 for r in matched)
    late_ends = sum(float(r["end_frame_error"]) > 0 for r in matched)
    fragmented = [r["gt_rally"] for r in diagnostics if len(r["overlapping_production_segments"]) > 1]
    missed_with_overlap = [
        r["gt_rally"] for r in diagnostics if r["matching_status"] == "missed" and r["overlapping_production_segments"]
    ]
    early_end_outliers = sorted(
        [(int(r["gt_rally"]), int(r["end_frame_error"])) for r in matched if float(r["end_frame_error"]) < 0],
        key=lambda pair: pair[1],
    )[:2]
    start_bias = metrics["boundary_and_duration_errors"]["start_time_sec"]["mean_signed_error"]
    lines += [
        "",
        f"Production end-reason counts: `{json.dumps(reasons, sort_keys=True)}`.",
        "",
        f"Among the {len(matched)} matched rallies, starts are late in {late_starts} and early in {early_starts}; "
        f"ends are early in {early_ends} and late in {late_ends}. Exact boundaries account for the remainder. "
        f"Ground-truth intervals overlapping multiple production segments: {fragmented}. "
        "Those overlaps identify possible fragmentation for review; the table preserves each segment's "
        "actual end gate rather than assigning a guessed perception failure.",
        "",
        f"{len(missed_with_overlap)} of {d['false_negatives']} policy-missed labels have some "
        "overlapping production segment: "
        f"{missed_with_overlap}. Thus these false negatives reflect inadequate interval agreement, "
        "not complete absence of detections throughout each such annotated rally. "
        "The table above gives the exact fragment boundaries; the diagnostic JSON records each "
        "label's main-view and camera-lost/replay coverage. "
        "These are observed associations, not proof that every dropout or split has the same cause.",
        "",
        "These recorded reasons locate the final segmentation gate (gap/stationary/cut/flush); they do not "
        "prove why perception lost the shuttle or whether a manual boundary is correct. "
        "`boundary_diagnostics.json` also records view/calibration/replay counts. Raw visibility is before "
        "the engine's spike removal and temporal validity gates, so it must not be treated as the FSM's "
        "observed-motion coverage. No model-output-derived annotation or causal claim substitutes for frame review.",
        "",
        "## E. Limitations",
        "",
        "One supplied video cannot establish generalization. The checkpoint training overlap with this "
        "source and any prior detector tuning exposure to Test 1/Part2 are unknown. This is a current-state "
        "baseline, not independently held-out validation. The user identifies the CSV as manual ground truth, "
        "but independent annotation "
        "review/tool provenance is unavailable. The older Part2 result tables use similar schemas and "
        "are not used to generate or correct predictions. Potential sub-frame/one-frame human labeling "
        "ambiguity remains; no data-driven offset correction is applied.",
        "",
        "The configured optional OSNet appearance checkpoint was unavailable; production degradation is "
        "retained above. Actual providers are reported separately from requested profile names. "
        "Raw inference runs on the production proxy rather than directly on original pixels, as the "
        "application does. Timeline audits prevent silent source/proxy frame-count or FPS mismatch. "
        "Boundary error statistics cover only IoU-qualified matched intervals; poor/non-overlapping "
        "segments are reflected in FP/FN rather than conditional MAE. No shot, player, outcome or score "
        "accuracy is measured.",
        "",
        "## F. Next steps",
        "",
        f"1. Prioritize interval continuity: review policy-missed labels {metrics['missed_gt_rallies']} and "
        f"the {len(fragmented)} labels overlapping multiple production segments. Inspect the recorded gap "
        "and stationary gates against original frames and postprocessing evidence before any threshold changes.",
        f"2. Prioritize late starts ({late_starts} of {len(matched)} matched) and the largest early ends "
        f"(GT row, signed frame error): {early_end_outliers}. "
        "Inspect observed motion, spike rejection and accepted-contact support "
        "around those exact boundaries. The recorded end reason locates a gate, not its root cause.",
        f"3. Review start runs/contact support against the {number(start_bias)}-second mean signed start error; "
        "obtain independent "
        "annotation-tool/frame-base confirmation before applying any offset.",
        "4. Keep this unchanged baseline. Any model restoration or threshold experiment must use a "
        "separate output, be marked exploratory on Test 1, and be validated on an independently held-out "
        "annotated source before claiming improvement in generalization.",
        "",
        "## Reproduction and evidence",
        "",
        "See `scripts/benchmarking/README.md` for commands and `PIPELINE_TRACE.md` for the inspected "
        "production path. `predicted_rallies.csv` has exactly the original seven columns. "
        "`metrics.json`, `metrics.md`, `rally_comparison.csv`, `benchmark_metadata.json`, source/annotation "
        "audits and this report are small review artifacts. Original media, isolated runtime, raw "
        "events and `execution.log` remain on disk and are ignored by Git. Main and production code "
        "remain unchanged. The synthetic evaluator suite passed before expensive inference.",
        "",
    ]
    (output / "BENCHMARK_REPORT.md").write_text("\n".join(lines))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/benchmarking/test1")
    build_report(parser.parse_args().output.resolve())
