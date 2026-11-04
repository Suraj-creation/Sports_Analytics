"""Independent Test 1 evaluation audit; never mutates production/baseline artifacts.

Run: source ../gpu-env.sh && python research/audit_a_benchmark.py
Default output must not already exist. The independent implementation uses exact
frame-span fractions and ordered dynamic programming, not the production matcher.
The production evaluator is separately reproduced into a fresh subdirectory.
"""

# Long prose findings are stored verbatim for the generated JSON/Markdown audit.
# ruff: noqa: E501

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import subprocess
import sys
from datetime import UTC, datetime
from fractions import Fraction
from itertools import pairwise
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "outputs/benchmarking/test1"
FIELDS = ["Start_Frame", "End_Frame", "Start_Time_sec", "End_Time_sec", "Duration_sec", "Start_Time", "End_Time"]


def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def read(path):
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == FIELDS
        result = list(reader)
    for row in result:
        for key in FIELDS[:2]:
            row[key] = int(row[key])
        for key in FIELDS[2:5]:
            row[key] = float(row[key])
        assert row["Start_Frame"] >= 0 and row["End_Frame"] > row["Start_Frame"]
        for prefix in ("Start", "End"):
            seconds = row[f"{prefix}_Time_sec"]
            assert math.isfinite(seconds)
            assert abs(seconds - row[f"{prefix}_Frame"] / 30) < 1e-12
            whole = math.floor(seconds)
            assert row[f"{prefix}_Time"] == f"{whole // 60:02d}:{whole % 60:02d}"
        assert abs(row["Duration_sec"] - (row["End_Time_sec"] - row["Start_Time_sec"])) < 1e-12
    assert all(a["End_Frame"] < b["Start_Frame"] for a, b in pairwise(result))
    return result


def intersection(a, b):
    return max(0, min(a["End_Frame"], b["End_Frame"]) - max(a["Start_Frame"], b["Start_Frame"]))


def iou(a, b):
    overlap = intersection(a, b)
    union = a["End_Frame"] - a["Start_Frame"] + b["End_Frame"] - b["Start_Frame"] - overlap
    return Fraction(overlap, union)


def ordered_exact_assignment(gt, pred):
    """Independent DP, valid here because both input lists are ordered/disjoint.

    Positive-overlap matches cannot cross for two ordered disjoint interval sets.
    Optimize pair count, then the documented IoU+tiny proximity objective exactly.
    """
    dp = [[(0, Fraction(0), ()) for _ in range(len(pred) + 1)] for _ in range(len(gt) + 1)]
    for i, a in enumerate(gt, 1):
        for j, b in enumerate(pred, 1):
            candidates = [dp[i - 1][j], dp[i][j - 1]]
            overlap = iou(a, b)
            if overlap >= Fraction(1, 2):
                count, score, pairs = dp[i - 1][j - 1]
                distance = abs(a["Start_Frame"] - b["Start_Frame"]) + abs(a["End_Frame"] - b["End_Frame"])
                preference = Fraction(30, 1_000_000_000 * (30 + distance))
                candidates.append((count + 1, score + overlap + preference, (*pairs, (i - 1, j - 1))))
            dp[i][j] = max(candidates, key=lambda x: (x[0], x[1]))
    return list(dp[-1][-1][2])


def linear_percentile(values, q):
    values = sorted(values)
    location = (len(values) - 1) * q
    left, right = math.floor(location), math.ceil(location)
    return values[left] + (values[right] - values[left]) * (location - left)


def stats(signed):
    absolute = list(map(abs, signed))
    return {
        "mae": statistics.mean(absolute),
        "median_absolute_error": statistics.median(absolute),
        "rmse": math.sqrt(statistics.mean(v * v for v in signed)),
        "max_absolute_error": max(absolute),
        "p90_absolute_error": linear_percentile(absolute, 0.9),
        "mean_signed_error": statistics.mean(signed),
        "median_signed_error": statistics.median(signed),
    }


def union_span(intervals):
    result = 0
    hi = -1
    for lo, end in sorted(intervals):
        result += max(0, end - max(lo, hi))
        hi = max(hi, end)
    return result


def findings():
    return [
        {
            "id": "A01",
            "classification": "verified calculation correctness",
            "confidence": "high",
            "observed_symptom": "Poor baseline scores might be caused by evaluator arithmetic or matching defects.",
            "supporting_evidence": "Exact-rational ordered dynamic programming returns the same 30 pairs; independent arithmetic matches every recorded boundary/duration statistic and tolerance; fresh production evaluator JSON and comparison bytes match frozen artifacts.",
            "source_functions": [
                "scripts/benchmarking/evaluate_rallies.py:54 read_csv",
                "scripts/benchmarking/evaluate_rallies.py:98 interval_iou",
                "scripts/benchmarking/evaluate_rallies.py:103 match_rallies",
                "scripts/benchmarking/evaluate_rallies.py:123 error_stats",
                "scripts/benchmarking/evaluate_rallies.py:149 evaluate",
            ],
            "hypothesized_cause": "No arithmetic, assignment, sign or frame-unit defect explains this baseline.",
            "alternative_explanations": [
                "Annotation ambiguity or physical observation failures can exist despite correct arithmetic."
            ],
            "causal_experiment": "Replay exactly frozen predictions through the unchanged evaluator and independently recompute pairs and errors; completed successfully.",
            "proposed_action": "Freeze the existing matching protocol; use supplementary diagnostics rather than changing scores.",
            "expected_metric_effect": "None from evaluator repairs: no baseline score defect was found.",
            "regression_risk": "Changing matching, endpoints or tolerance denominators would break baseline comparability.",
        },
        {
            "id": "A02",
            "classification": "proven diagnostic interpretation issue",
            "confidence": "high",
            "observed_symptom": "GT2/19 matched starts are +179/+202 frames late; GT20/27 matched ends are -442/-218 frames early.",
            "supporting_evidence": "GT2/19 first fragments start only +4 frames late. GT20/27 later fragments reach -20/-12 frames before the labeled end. The selected eligible interval excludes those other fragments.",
            "source_functions": [
                "scripts/benchmarking/evaluate_rallies.py:103 match_rallies",
                "scripts/benchmarking/evaluate_rallies.py:156 per-GT comparison loop",
                "outputs/benchmarking/test1/predicted_rallies.csv",
                "outputs/benchmarking/test1/rally_comparison.csv",
            ],
            "hypothesized_cause": "One-to-one assignment correctly measures whole-interval agreement, while fragmentation makes selected-fragment errors look like first-onset/final-offset detector errors.",
            "alternative_explanations": [
                "Other single-fragment rallies have real multi-second onset delay; fragmentation does not explain all start errors.",
                "Ground-truth endpoint conventions remain physically unverified.",
            ],
            "causal_experiment": "Compare selected-match errors with earliest/latest positive-overlap boundaries without changing primary predictions; completed as supplementary diagnostics. Replay exact FSM decisions to establish why each split occurred.",
            "proposed_action": "Prioritize continuity mechanisms for GT2/19/20/27; diagnose standalone onset delays separately.",
            "expected_metric_effect": "Recovering a continuous supported interval can improve FP/FN, selected-boundary errors, duration and IoU together; numeric gain requires inference/replay evidence.",
            "regression_risk": "Naively unioning all GT-overlapping predictions leaks labels and can join distinct rallies.",
        },
        {
            "id": "A03",
            "classification": "proven error taxonomy",
            "confidence": "high",
            "observed_symptom": "Nineteen false-positive intervals may be mistaken for movement/noise between rallies.",
            "supporting_evidence": "All 19 unmatched predictions have positive temporal overlap with at least one GT interval; zero predicted intervals have no GT overlap. All six unmatched labels have partial predicted coverage.",
            "source_functions": [
                "scripts/benchmarking/evaluate_rallies.py:208 TP/FP/FN counts",
                "outputs/benchmarking/test1/predicted_rallies.csv",
                "research/audit_a_benchmark.py:intersection",
            ],
            "hypothesized_cause": "Policy false positives are predominantly unmatched fragments/truncated intervals here; there is no evidence that suppressing inter-rally movement is the principal remedy.",
            "alternative_explanations": [
                "A false interval may overlap genuine play yet have wrong boundaries; positive overlap does not establish semantic correctness."
            ],
            "causal_experiment": "Trace gap/stationary closures and continuation evidence at fragment pairs; compare controlled recovery against closely spaced separate-rally controls.",
            "proposed_action": "Retain FP=19 under the frozen protocol; add the no-overlap FP count and per-GT segment/coverage diagnostics.",
            "expected_metric_effect": "Taxonomy improves causal targeting; it does not reduce the official FP count.",
            "regression_risk": "Dropping unmatched fragments without restoring intervals can hide failures and worsen recall.",
        },
        {
            "id": "A04",
            "classification": "proven near-threshold sensitivity",
            "confidence": "high",
            "observed_symptom": "GT29 is unmatched despite an almost half-length prediction.",
            "supporting_evidence": "Best fragment is frames13686..13843 within GT13679..13994: exact boundary-span IoU157/315=0.4984126984, correctly below0.5. Adding one frame to both spans gives158/316=0.5 and would change the result.",
            "source_functions": [
                "scripts/benchmarking/evaluate_rallies.py:98 interval_iou",
                "scripts/benchmarking/evaluate_rallies.py:115 eligibility",
                "Part2/dataset/Test1_Full/Test1_Full_rally.csv:30",
            ],
            "hypothesized_cause": "Real fragment truncation lies immediately below the fixed eligibility threshold, not floating-point misclassification.",
            "alternative_explanations": [
                "A physically justified annotation correction could alter this case, but independent review is unavailable and no correction is authorized as benchmark tuning."
            ],
            "causal_experiment": "Exact-fraction threshold comparison completed. Inspect shuttle/segmentation evidence around13843..13883 to explain the split, not tune IoU eligibility.",
            "proposed_action": "Preserve GT and [start,end) timestamp spans; report exact best-fragment IoU for unmatched labels.",
            "expected_metric_effect": "No score change without a real predictive boundary improvement.",
            "regression_risk": "An inclusive-end convention switch manufactures a TP and violates baseline semantics.",
        },
        {
            "id": "A05",
            "classification": "proven cross-rally overlap caveat",
            "confidence": "high",
            "observed_symptom": "An earliest-overlapping-start diagnostic can suggest an unrealistically early start for GT23.",
            "supporting_evidence": "Prediction27 spans10601..10737 and matches GT22; it overlaps only4 frames at the start of GT23(10733..11078). Thus GT23's earliest-overlapping start is-132 frames, not evidence that this rally began at10601.",
            "source_functions": [
                "research/audit_a_benchmark.py:per_rally overlap diagnostics",
                "outputs/benchmarking/test1/predicted_rallies.csv",
                "outputs/benchmarking/test1/rally_comparison.csv",
            ],
            "hypothesized_cause": "Any-positive-overlap fragmentation counts include minor cross-boundary spillovers.",
            "alternative_explanations": [
                "A true merged interval could cross rallies, but this overlap alone cannot establish one."
            ],
            "causal_experiment": "Review original frames and temporal evidence at10708..10769; separately tag minimal spillovers and substantive fragments in supplementary diagnostics.",
            "proposed_action": "Use positive-overlap counts as diagnostics, never as an automatic GT-conditioned merging/backdating algorithm.",
            "expected_metric_effect": "Prevents misleading causal conclusions; no change to primary metrics.",
            "regression_risk": "Naive overlap-based reconstruction can merge distinct legitimate rallies.",
        },
        {
            "id": "A06",
            "classification": "verified export and provenance with explicit limits",
            "confidence": "high for arithmetic/export; unresolved for human frame semantics",
            "observed_symptom": "Index/FPS/serialization or inclusive production duration payload might explain errors.",
            "supporting_evidence": "Both seven-column CSVs validate; every GT timestamp equals frame/30 and duration=end-start. All49 current rally_end events from independently folded raw log match prediction frames exactly. All recorded artifact/source hashes and86 production source fingerprints match. Existing source/proxy audits report17268 CFR frames at30FPS.",
            "source_functions": [
                "scripts/benchmarking/production_inference.py:77 event selection",
                "scripts/benchmarking/production_inference.py:115 export",
                "scripts/benchmarking/evaluate_rallies.py:85 write_predictions",
                "legacy/pipeline/analysis/detect_rallies.py:140 format_time",
                "legacy/pipeline/analysis/detect_rallies.py:598 CSV export",
            ],
            "hypothesized_cause": "No serialized offset, duration-rounding or dropped-row defect explains baseline boundary errors.",
            "alternative_explanations": [
                "Numerical consistency does not prove the unavailable manual tool's physical frame numbering or label rationale.",
                "Content/frame correspondence needs the independent video audit, not metadata alone.",
            ],
            "causal_experiment": "Independent raw-event fold, hash/source verification and evaluator reproduction completed; physical boundary/frame review remains the temporal auditor's task.",
            "proposed_action": "Preserve exact CSV bytes and annotations. Keep explicit frame conventions and separate observation-end index from interval-span duration.",
            "expected_metric_effect": "No systematic offset correction is justified by this audit.",
            "regression_risk": "Blind one-frame or FPS corrections can alter near-threshold matches and hide perception defects.",
        },
        {
            "id": "A07",
            "classification": "verified general edge-case hardening opportunity, not baseline cause",
            "confidence": "high",
            "observed_symptom": "An empty GT input produces an empty comparison file with no CSV header.",
            "supporting_evidence": "save_evaluation opens rally_comparison.csv, but writer/header creation is inside if rows. read_csv also rejects one-frame/zero-span intervals by design; no such interval exists here.",
            "source_functions": ["scripts/benchmarking/evaluate_rallies.py:265 save_evaluation"],
            "hypothesized_cause": "Comparison schema is inferred from the first row rather than defined independently.",
            "alternative_explanations": [
                "A no-GT benchmark may intentionally be unsupported, but that constraint is not enforced."
            ],
            "causal_experiment": "Call save_evaluation in a temporary directory with empty GT and prediction inputs, then assert a header; not needed to explain the36-label baseline.",
            "proposed_action": "Optional future evaluator hardening: fixed comparison schema/header for empty inputs, without changing matching.",
            "expected_metric_effect": "None on Test1; improves artifact robustness only.",
            "regression_risk": "Low if limited to empty export behavior; do not bundle with matching-policy changes.",
        },
    ]


def markdown(report):
    lines = [
        "# Independent benchmark and evaluation audit",
        "",
        "## Scope and immutable evidence",
        "",
        f"Audit at `{report['audit_git_sha']}`; production baseline `{report['production_commit']}`. "
        "No production evaluator/source, original media, GT or frozen baseline artifact was modified. "
        "This audit reran evaluation only; it did not rerun video inference.",
        "",
        "Read the full benchmark report, README, pipeline trace, seven-column CSVs, metrics, "
        "metadata, diagnostics, inference records, raw events, execution log and relevant export/evaluator source. "
        "Evidence hashes and all36 per-rally records are in `research/benchmark_audit.json`.",
        "",
        "## Independent reproduction",
        "",
        "```bash",
        "source ../gpu-env.sh",
        "python research/audit_a_benchmark.py --output artifacts/benchmarking/investigation/audit_a_final",
        "```",
        "",
        "The production evaluator was reproduced into a new output directory. Its complete metrics JSON "
        "is value-identical and comparison CSV byte-identical to the frozen baseline. Independently, an "
        "exact-fraction ordered dynamic program recovered the same30 pair assignments. Ordered DP is valid "
        "for these two disjoint, sorted interval lists because positive-overlap matches cannot cross; it "
        "is not a replacement for the general bipartite matcher. Independent Python statistics and linear "
        "percentiles reproduce all stored errors/tolerances within1e-10. Raw-event folding independently "
        "recovers exactly the49 exported intervals. Video/CSV and recorded evidence hashes match; all86 "
        "production source hashes match the recorded production Git objects.",
        "",
        "| Metric | Independently verified baseline |",
        "| --- | --- |",
        "| GT / predictions / matched | 36 / 49 / 30 |",
        "| TP / FP / FN | 30 / 19 / 6 |",
        "| Precision / recall / F1 | 0.612244898 / 0.833333333 / 0.705882353 |",
        "| Start MAE / RMSE / median absolute, frames | 49.433333 / 75.253128 / 23 |",
        "| End MAE / RMSE / median absolute, frames | 40.4 / 96.463119 / 7 |",
        "| Start / end signed bias, frames | +48.033333 / -33.4 |",
        "| Duration MAE / RMSE / bias, seconds | 2.845556 / 4.346378 / -2.714444 |",
        "| Matched mean / median IoU | 0.763314890 / 0.767948002 |",
        "",
        "## Seven-column semantics",
        "",
        "`Start_Frame`/`End_Frame` are zero-based boundary indices under the adopted arithmetic convention; "
        "`Start_Time_sec`/`End_Time_sec` equal their index divided by independently recorded30FPS. "
        "`Duration_sec` is the difference of those timestamps. `Start_Time`/`End_Time` truncate to whole "
        "seconds and format MM:SS. Both CSVs have exactly the seven columns in the required order. "
        "No numeric drift or missing/invalid row was found. Source/proxy timestamp audits agree, but "
        "the numerical checks do not recover the unavailable human annotation-tool history. The raw "
        "labels remain authoritative as supplied; no offset is fitted.",
        "",
        "Production event endpoints identify inclusive observations; this benchmark measures spans "
        "between their timestamps, [start,end), exactly matching annotated durations. It correctly "
        "does not copy the rounded inclusive production payload duration. No one-frame adjustment is warranted.",
        "",
        "## Matching and interpretation",
        "",
        "Eligibility is IoU>=0.5; a pair can be used once. The cardinality bonus2*(min(Ngt,Npred)+1) "
        "dominates every possible total secondary score, so maximum eligible count is prioritized. "
        "The secondary objective matches the documented IoU plus1e-9/(1+boundary-distance-seconds). "
        "Strict 'exceeds' coverage percentages use >, while eligibility uses >=. Frame tolerance checks "
        "include equality and correctly report both matched-only and all-GT denominators. Nothing in "
        "the audit justifies changing the frozen protocol.",
        "",
        "The central diagnostic distinction is **selected-fragment boundary error versus first/last "
        "available evidence**. GT2 and19 have initial fragments beginning only4frames late, but matching "
        "selects later fragments with179/202frame start errors. GT20/27 have later fragments reaching "
        "20/12frames before the labeled end, while selected fragments end442/218frames early. "
        "Those are real whole-interval benchmark failures, yet they do not independently prove an "
        "equally large first-onset/final-offset delay. No improved prediction or score is claimed from "
        "this GT-dependent diagnostic union.",
        "",
        "All19 policy-FP predictions overlap GT, and all6 FN labels have partial coverage. Eleven "
        "labels overlap multiple predictions. Therefore inter-rally hallucination suppression is not "
        "the primary explanation for this particular FP count. Positive overlap still does not prove "
        "a semantically correct interval. GT23 includes a4frame spillover from the previous matched "
        "rally; automatic earliest-overlap backdating would join distinct rallies.",
        "",
        "GT29's best single IoU is exactly157/315=0.4984126984. Inclusive counting would give158/316=0.5 "
        "and manufacture a policy TP. Its existing FN is not floating precision error. The correct "
        "investigation target is the observed split, not the evaluator threshold/end convention.",
        "",
        "## Per-rally independent error and coverage analysis",
        "",
        "The last two columns are supplementary earliest/latest *positive-overlap* diagnostics, "
        "not replacement predictions or evaluation results. In particular, GT23's negative earliest "
        "start comes from preceding-rally spillover. Errors are predicted minus annotated frames.",
        "",
        "| GT | Matched pred | Overlap segments | Best single IoU | Union coverage | Matched start err | Matched end err | Earliest start err | Latest end err |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report["per_rally"]:
        values = [
            row["gt_rally"],
            row["matched_pred_rally"],
            row["positive_overlap_segment_count"],
            f"{row['best_single_prediction_iou']:.6f}",
            f"{row['union_coverage_fraction']:.6f}",
            row["start_error_frames"],
            row["end_error_frames"],
            row["earliest_overlapping_start_error_frames"],
            row["latest_overlapping_end_error_frames"],
        ]
        lines.append("| " + " | ".join("unmatched" if v is None else str(v) for v in values) + " |")
    lines += ["", "## Evidence-backed findings and causal experiments", ""]
    for finding in report["findings"]:
        lines += [f"### {finding['id']}: {finding['classification']}", ""]
        for key in [
            "observed_symptom",
            "supporting_evidence",
            "source_functions",
            "hypothesized_cause",
            "alternative_explanations",
            "confidence",
            "causal_experiment",
            "proposed_action",
            "expected_metric_effect",
            "regression_risk",
        ]:
            value = finding[key]
            if isinstance(value, list):
                value = "; ".join(value)
            lines += [f"**{key.replace('_', ' ').capitalize()}:** {value}", ""]
    lines += [
        "## Runtime/provenance limitations and acceptance",
        "",
        "Recorded total inference time1469.237seconds implies11.753processedframes/second over17268frames. "
        "This elapsed interval covers production ingest/analysis, not source download, all audits or post-reporting. "
        "The frozen inference record does not provide per-stage time, peak GPU memory or a CPU utilization "
        "series. Hardware capacity is not measured peak usage; absent metrics must remain unavailable. "
        "Future experiments should instrument those signals without inventing baseline values.",
        "",
        "Baseline publication separated initial evaluator code from additive final reporting fields. "
        "The archived execution scripts, final-script hashes and production hashes make this explicit. "
        "The legacy helper's null shuttle inspection is independently contradicted by the actual loaded "
        "component runtime and execution log (CUDA FP16); it is a reporting wrapper limitation, not "
        "evidence that shuttle inference did not run.",
        "",
        "Accept an experimental change only with unchanged seven-column semantics and matching, complete "
        "prediction/event provenance, full-video metrics, severe-outlier review, FP/FN accounting and "
        "separate raw-observation/segmentation experiments. Retain these current baseline numbers. "
        "Test1 remains exploratory development evidence; no held-out generalization is established.",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/benchmarking/investigation/audit_a")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    gt_path = ROOT / "Part2/dataset/Test1_Full/Test1_Full_rally.csv"
    pred_path = BASE / "predicted_rallies.csv"
    metadata = json.loads((BASE / "benchmark_metadata.json").read_text())
    frozen_metrics = json.loads((BASE / "metrics.json").read_text())
    gt, pred = read(gt_path), read(pred_path)
    source_probe = json.loads((BASE / "source_probe.json").read_text())
    assert metadata["video_fps"] == 30 and source_probe["streams"][0]["avg_frame_rate"] == "30/1"
    assert len(gt) == 36 and len(pred) == 49
    assert sha(gt_path) == metadata["ground_truth_sha256"]
    assert sha(pred_path) == metadata["prediction_sha256"]
    evidence_hashes = {p.name: sha(p) for p in BASE.iterdir() if p.is_file()}
    for name, expected in metadata["artifact_hashes"].items():
        assert sha(BASE / name) == expected, name
    fingerprint_mismatches = []
    for name, expected in metadata["production_source_hashes"].items():
        blob = subprocess.check_output(["git", "show", f"{metadata['git_commit_sha']}:{name}"], cwd=ROOT)
        if hashlib.sha256(blob).hexdigest() != expected:
            fingerprint_mismatches.append(name)
    assert not fingerprint_mismatches
    video = ROOT / "data/benchmarking/test1/Test1_Full_rev.mp4"
    assert sha(video) == metadata["source_video_sha256"]
    pairs = ordered_exact_assignment(gt, pred)
    lookup = dict(pairs)
    used = {j for _, j in pairs}
    errors = {key: [] for key in ["start_frame", "end_frame", "start_time_sec", "end_time_sec", "duration_sec"]}
    overlaps = []
    per_rally = []
    with (BASE / "rally_comparison.csv").open() as f:
        comparison = list(csv.DictReader(f))
    assert [(int(r["gt_rally"]) - 1, int(r["pred_rally"]) - 1) for r in comparison if r["pred_rally"]] == pairs
    for i, a in enumerate(gt):
        intersections = [(j, b) for j, b in enumerate(pred) if intersection(a, b) > 0]
        covered = union_span(
            [(max(a["Start_Frame"], b["Start_Frame"]), min(a["End_Frame"], b["End_Frame"])) for _, b in intersections]
        )
        earliest = min((b["Start_Frame"] for _, b in intersections), default=None)
        latest = max((b["End_Frame"] for _, b in intersections), default=None)
        per = {
            "gt_rally": i + 1,
            "gt_start": a["Start_Frame"],
            "gt_end": a["End_Frame"],
            "matched_pred_rally": lookup[i] + 1 if i in lookup else None,
            "overlapping_prediction_ids": [j + 1 for j, _ in intersections],
            "positive_overlap_segment_count": len(intersections),
            "best_single_prediction_iou": float(max((iou(a, b) for _, b in intersections), default=Fraction(0))),
            "union_coverage_fraction": covered / (a["End_Frame"] - a["Start_Frame"]),
            "earliest_overlapping_start_error_frames": earliest - a["Start_Frame"] if earliest is not None else None,
            "latest_overlapping_end_error_frames": latest - a["End_Frame"] if latest is not None else None,
            "start_error_frames": None,
            "end_error_frames": None,
            "duration_error_seconds": None,
        }
        if i in lookup:
            b = pred[lookup[i]]
            values = [
                b["Start_Frame"] - a["Start_Frame"],
                b["End_Frame"] - a["End_Frame"],
                b["Start_Time_sec"] - a["Start_Time_sec"],
                b["End_Time_sec"] - a["End_Time_sec"],
                b["Duration_sec"] - a["Duration_sec"],
            ]
            for key, value in zip(errors, values, strict=True):
                errors[key].append(value)
            overlaps.append(float(iou(a, b)))
            per.update(start_error_frames=values[0], end_error_frames=values[1], duration_error_seconds=values[-1])
        per_rally.append(per)
    counts = dict(
        ground_truth_count=len(gt),
        predicted_count=len(pred),
        matched_count=len(pairs),
        true_positives=len(pairs),
        false_positives=len(pred) - len(pairs),
        false_negatives=len(gt) - len(pairs),
        precision=len(pairs) / len(pred),
        recall=len(pairs) / len(gt),
        f1=2 * len(pairs) / (len(gt) + len(pred)),
    )
    assert counts == frozen_metrics["detection"]
    independently_computed = {k: stats(v) for k, v in errors.items()}
    discrepancies = {}
    for key, values in independently_computed.items():
        for metric, value in values.items():
            reference = frozen_metrics["boundary_and_duration_errors"][key][metric]
            if not math.isclose(value, reference, abs_tol=1e-10, rel_tol=1e-12):
                discrepancies[f"{key}.{metric}"] = [value, reference]
    assert not discrepancies
    assert math.isclose(statistics.mean(overlaps), frozen_metrics["overlap"]["mean_iou"], abs_tol=1e-12)
    assert math.isclose(statistics.median(overlaps), frozen_metrics["overlap"]["median_iou"], abs_tol=1e-12)
    assert math.isclose(min(overlaps), frozen_metrics["overlap"]["minimum_iou"], abs_tol=1e-12)
    for threshold, expected in frozen_metrics["overlap"]["percent_strictly_exceeding"].items():
        assert math.isclose(100 * sum(v > float(threshold) for v in overlaps) / len(pairs), expected, abs_tol=1e-10)
    for name in ["start", "end"]:
        values = errors[f"{name}_frame"]
        for entry in frozen_metrics["boundary_tolerances"][name]:
            n = sum(abs(v) <= entry["frames"] for v in values)
            assert n == entry["within_count"]
            assert n / len(pairs) == entry["matched_accuracy"]
            assert n / len(gt) == entry["all_gt_accuracy"]
    fp_details = []
    for j, b in enumerate(pred):
        if j not in used:
            hits = [(i + 1, float(iou(a, b)), intersection(a, b)) for i, a in enumerate(gt) if intersection(a, b)]
            fp_details.append(
                {
                    "pred_rally": j + 1,
                    "start_frame": b["Start_Frame"],
                    "end_frame": b["End_Frame"],
                    "overlapping_gt": hits,
                    "overlaps_no_gt": not hits,
                }
            )
    raw = [json.loads(s) for s in (BASE / "raw_events.jsonl").read_text().splitlines()]
    superseded = {e["supersedes"] for e in raw if e.get("supersedes")}
    ends = sorted(
        (e for e in raw if e["type"] == "rally_end" and e["status"] != "retracted" and e["event_id"] not in superseded),
        key=lambda e: (e["frame_start"], e["frame_end"], e["seq"]),
    )
    assert [(e["frame_start"], e["frame_end"]) for e in ends] == [(r["Start_Frame"], r["End_Frame"]) for r in pred]
    reproduced = output / "production_evaluator_reproduction"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/benchmarking/evaluate_rallies.py"),
            "--ground-truth",
            str(gt_path),
            "--predictions",
            str(pred_path),
            "--fps",
            "30",
            "--output",
            str(reproduced),
        ],
        cwd=ROOT,
        check=True,
    )
    assert json.loads((reproduced / "metrics.json").read_text()) == frozen_metrics
    assert (reproduced / "rally_comparison.csv").read_bytes() == (BASE / "rally_comparison.csv").read_bytes()
    for name, expected in evidence_hashes.items():
        assert sha(BASE / name) == expected, f"baseline artifact changed during audit: {name}"
    report = {
        "audit_date_utc": datetime.now(UTC).isoformat(),
        "audit_git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=ROOT).strip(),
        "production_commit": metadata["git_commit_sha"],
        "baseline_commit": "b773e20c62d1c398cddc3d23510bd4adf823325b",
        "checks": {
            "schema": True,
            "annotation_arithmetic": True,
            "ordered_disjoint_inputs": True,
            "independent_exact_assignment_matches": True,
            "independent_metrics_match": True,
            "production_evaluator_json_equal": True,
            "comparison_bytes_equal": True,
            "event_export_exact": True,
            "all_recorded_artifact_hashes_match": True,
            "video_hash_matches": True,
            "ground_truth_hash_matches": True,
            "production_commit_fingerprints_match": True,
            "baseline_unchanged": True,
        },
        "schema": FIELDS,
        "detection": counts,
        "independent_error_metrics": independently_computed,
        "evidence_hashes": evidence_hashes,
        "ground_truth_sha256": sha(gt_path),
        "source_sha256": sha(video),
        "per_rally": per_rally,
        "unmatched_predictions": fp_details,
        "fragmentation": {
            "gt_overlapping_multiple_predictions": [
                r["gt_rally"] for r in per_rally if r["positive_overlap_segment_count"] > 1
            ],
            "unmatched_gt_with_partial_coverage": [
                r["gt_rally"]
                for r in per_rally
                if r["matched_pred_rally"] is None and r["positive_overlap_segment_count"] > 0
            ],
            "predictions_with_no_positive_gt_overlap": [r["pred_rally"] for r in fp_details if r["overlaps_no_gt"]],
        },
        "limitations": [
            "No annotation tool/reviewer provenance; numerical alignment cannot prove human frame labels.",
            "Baseline conditional boundary metrics select one eligible fragment, not earliest/latest evidence.",
            "Ordered independent DP is valid for this disjoint input and is not a general replacement matcher.",
            "No threshold, matching policy, prediction, ground truth or baseline artifact was changed.",
        ],
        "findings": findings(),
    }
    (output / "independent_audit.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    (ROOT / "research/benchmark_audit.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    (ROOT / "research/benchmark_audit.md").write_text(markdown(report))
    print(
        json.dumps(
            {"checks": report["checks"], "detection": counts, "fragmentation": report["fragmentation"]}, indent=2
        )
    )


if __name__ == "__main__":
    main()
