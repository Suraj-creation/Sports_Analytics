"""Offline all-rally causal firsts, with bounded diagnostic acquisition coverage.

External rows are paired fresh TrackNet component inference, never silently
inserted into the fresh full pipeline's cached observations or event trace.
Ground truth groups this completed-evidence review only.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import msgpack
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.next_temporal_diagnose import sha, verify_trace_cache_identity  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--semantic", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--component-probe", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run, semantic, audit = args.run.resolve(), args.semantic.resolve(), args.audit.resolve()
    metadata = json.loads((run / "benchmark_metadata.json").read_text())
    paths = sorted(run.glob("runtime/sessions/*/perception/*.msgpack"))
    cache_hashes = verify_trace_cache_identity(metadata, semantic / "fsm_trace.jsonl", paths)
    audit_manifest = json.loads((audit / "manifest.json").read_text())
    assert audit_manifest["trace_sha256"] == sha(semantic / "fsm_trace.jsonl")
    observations = {}
    diagnostics = {}
    for path in paths:
        value = msgpack.unpackb(path.read_bytes(), raw=False)
        for raw in value["frames"]:
            observations[raw["f"]] = raw
            if raw.get("dg") is not None and raw["dg"].get("shuttle") is not None:
                diagnostics[raw["f"]] = {"diagnostic": raw["dg"]["shuttle"], "sources": ["fresh own-cache diagnostic"]}
    probe_provenance = []
    for probe_path in args.component_probe:
        probe = probe_path.resolve()
        manifest = json.loads((probe / "manifest.json").read_text())
        comparisons = json.loads((probe / "comparisons.json").read_text())
        assert manifest["status"] == "completed" and manifest["executor_sources_unchanged"] is True
        assert manifest["source_sha256"] == metadata["source_video_sha256"]
        assert Path(manifest["recorded_run"]).resolve() == run
        assert manifest["recorded_metadata_sha256"] == sha(run / "benchmark_metadata.json")
        assert manifest["cache_sha256"] and all(
            cache_hashes.get(name) == digest for name, digest in manifest["cache_sha256"].items()
        )
        rolling = [row for row in comparisons if row["variant"] == "rolling"]
        assert rolling and all(not row["rolling_reference_differences"] for row in rolling)
        row_count = 0
        literal_xy_differences = 0
        max_xy_difference = 0.0
        max_support_difference = 0.0
        for line in (probe / "candidates.jsonl").open():
            row = json.loads(line)
            if row["variant"] != "rolling":
                continue
            frame = row["frame_idx"]
            raw = observations[frame]
            assert (row["xy"] is None) == (raw["s"] is None)
            if row["xy"] is not None:
                np.testing.assert_allclose(row["xy"], raw["s"], rtol=0, atol=1e-5)
                difference = float(np.max(np.abs(np.asarray(row["xy"]) - np.asarray(raw["s"]))))
                literal_xy_differences += difference > 0
                max_xy_difference = max(max_xy_difference, difference)
            assert row["support"] == raw["c"]
            max_support_difference = max(max_support_difference, abs(row["support"] - raw["c"]))
            row_count += 1
            if row["diagnostic"] is None:
                continue
            source = f"paired fresh TrackNet component:{probe.name}"
            if frame in diagnostics:
                # Heatmap diagnostics of repeated paired inference must agree;
                # accepted-coordinate parity alone cannot establish this. A
                # different bounded top-k budget need not change shared peaks.
                existing = diagnostics[frame]["diagnostic"]
                current = row["diagnostic"]
                for key in (
                    "raw_peak",
                    "masked_peak",
                    "threshold",
                    "reason",
                    "window_votes",
                    "background_sha256",
                    "selected_masked_peak_xy",
                    "decoded_xy",
                ):
                    assert existing[key] == current[key], f"raw diagnostic {key} differs at{frame}"
                if existing["candidate_floor"] == current["candidate_floor"]:
                    shared = min(len(existing["candidates"]), len(current["candidates"]))
                    assert existing["candidates"][:shared] == current["candidates"][:shared]
                diagnostics[frame]["sources"].append(source)
            else:
                diagnostics[frame] = {"diagnostic": row["diagnostic"], "sources": [source]}
        assert row_count == manifest["selected_frames_per_variant"]
        probe_provenance.append(
            {
                "directory": str(probe),
                "manifest_sha256": sha(probe / "manifest.json"),
                "candidates_sha256": sha(probe / "candidates.jsonl"),
                "comparisons_sha256": sha(probe / "comparisons.json"),
                "paired_accepted_coordinate_and_support_differences": 0,
                "literal_xy_differences": literal_xy_differences,
                "maximum_absolute_xy_difference_px": max_xy_difference,
                "maximum_absolute_support_difference": max_support_difference,
                "selected_frames": row_count,
                "recorded_cache_subset_hashes_exact": True,
                "scope": manifest["scope"],
            }
        )
    traces = [json.loads(line) for line in (semantic / "fsm_trace.jsonl").open()]
    steps = {row["frame"]: row for row in traces if row["call"] == "step"}
    rows = json.loads((audit / "all_onsets_ends.json").read_text())
    results = []
    for row in rows:
        start, end = row["interval"]
        predicted_start, predicted_end = row["matched_interval"]
        # This label-derived window selects only completed offline review data.
        # It includes both the annotation onset and actual surviving onset.
        lo, hi = min(start, predicted_start), max(start, predicted_start)
        recorded = [(frame, diagnostics[frame]) for frame in range(lo, hi + 1) if frame in diagnostics]

        def first_peak(predicate, recorded=recorded):
            return next(
                (
                    {
                        "frame": frame,
                        "diagnostic": value["diagnostic"],
                        "sources": value["sources"],
                        "cached_scene_context": {
                            "view": observations[frame].get("v"),
                            "replay_or_excluded": observations[frame].get("r"),
                            "calibration": observations[frame].get("cs"),
                            "geometry_lost": observations[frame].get("l"),
                            "processed_context_valid": steps[frame].get("evidence", {}).get("context_valid"),
                        },
                    }
                    for frame, value in recorded
                    if predicate(value["diagnostic"])
                ),
                None,
            )

        proposal = next(
            (
                {"frame": trace["frame"], "call": trace["call"], "proposed_start": predicted_start}
                for trace in traces
                if trace["update"]["started"] == predicted_start
            ),
            None,
        )
        observation_first = next((frame for frame in range(lo, hi + 1) if observations[frame]["s"] is not None), None)
        counts = Counter(value["diagnostic"]["reason"] for _, value in recorded)
        result = {
            **row,
            "signed_start_error_frames": predicted_start - start,
            "signed_end_error_frames": predicted_end - end,
            "onset_review_half_open": [lo, hi + 1],
            "onset_scene_validity": {
                "excluded_scene_frames": sum(bool(observations[frame].get("r")) for frame in range(lo, hi + 1)),
                "invalid_processed_context_frames": sum(
                    steps[frame].get("evidence", {}).get("context_valid") is False for frame in range(lo, hi + 1)
                ),
                "first_cached_main_view_frame": next(
                    (frame for frame in range(lo, hi + 1) if observations[frame].get("v") == "main"), None
                ),
                "first_valid_processed_context_frame": next(
                    (
                        frame
                        for frame in range(lo, hi + 1)
                        if steps[frame].get("evidence", {}).get("context_valid") is True
                    ),
                    None,
                ),
                "scope": "recorded gating status, not an independently labeled camera/visibility truth",
            },
            "onset_model_diagnostic_coverage": {
                "recorded_frames": len(recorded),
                "review_frames": hi - lo + 1,
                "complete_for_this_review_window": len(recorded) == hi - lo + 1,
                "missing_frames": [frame for frame in range(lo, hi + 1) if frame not in diagnostics],
                "decision_counts": dict(counts),
            },
            "first_recorded_raw_model_peak_above_diagnostic_floor": first_peak(
                lambda diagnostic: diagnostic["raw_peak"] >= diagnostic["candidate_floor"]
            ),
            "first_recorded_raw_model_peak_above_inference_threshold": first_peak(
                lambda diagnostic: diagnostic["raw_peak"] >= diagnostic["threshold"]
            ),
            "first_accepted_provider_output_in_onset_review": observation_first,
            "surviving_start_proposal": proposal,
            "earlier_physical_onset_supported": "unknown unless separately reviewed original frames support it",
            "model_diagnostic_semantics": "uncalibrated heatmap response; not proof of a physical shuttle",
        }
        rally = row["gt_rally"]
        if rally in (5, 9, 15, 25, 33):
            group = "earlier supported candidate cancelled after sparse/missing evidence; later candidate survives"
        elif rally in (8, 14):
            group = "accepted points precede reliable adjacent motion; sparse/weak-motion onset evidence"
        elif rally == 4:
            group = "preannotation candidate retained through upper flight; serve-vs-return onset convention unresolved"
        elif rally == 22:
            group = "static-point/contact candidate crosses missed same-camera edit; scene/contact reliability open"
        elif rally == 23:
            group = "preparation/edit plus singleton-associated loss; mature continuity recovered without GT union"
        elif rally == 28:
            group = "first accepted provider point is invalid context; processed observations resume later"
        elif rally == 31:
            group = "initial close-up context excluded; first valid candidate retained after upstream mask repair"
        elif predicted_start < start:
            group = "candidate precedes annotation; physical onset convention and earlier footage unreviewed"
        else:
            group = "provider admission then motion/contact confirmation; compare raw model evidence and coverage"
        excluded = result["onset_scene_validity"]["excluded_scene_frames"]
        if excluded:
            group += f"; {excluded} review frames have excluded scene context"
        result["causal_group"] = group
        results.append(result)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    (output / "all36_model_temporal_firsts.json").write_text(json.dumps(results, indent=2, allow_nan=False) + "\n")
    lines = [
        "# Fresh all36 model and temporal firsts",
        "",
        "Offline diagnosis only. Raw model firsts cover the window between annotated and surviving onset; "
        "accepted/processed/motion/contact firsts from the temporal audit cover the annotated interval. "
        "External component rows have independently checked coordinate/support parity with these exact fresh caches. "
        "Heatmap responses and accepted contacts are hypotheses; physical visibility and onset convention "
        "remain separately reviewed.",
        "",
        "|GT|Start/end error|First recorded raw≥threshold / diagnostic coverage|"
        "Provider / processed / movement in GT span|Player/contact in GT span|"
        "Surviving proposal / cancellations|Terminal reason: proposal→close→finalize|Causal group|",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in results:
        raw = row["first_recorded_raw_model_peak_above_inference_threshold"]
        coverage = row["onset_model_diagnostic_coverage"]
        cancelled = ",".join(f"{c['start']}@{c['decision_frame']}" for c in row["candidate_cancellations"]) or "none"
        terminal = row["matched_terminal_chain"]
        lines.append(
            f"|{row['gt_rally']}|{row['signed_start_error_frames']:+d}/{row['signed_end_error_frames']:+d}|"
            f"{raw['frame'] if raw else 'unrecorded/none'} / {coverage['recorded_frames']}/{coverage['review_frames']}|"
            f"{row['first_raw_shuttle']}/{row['first_processed_observation']}/{row['first_adjacent_movement_over_start_speed']}|"
            f"{row['first_aligned_participant_motion']}/{row['first_accepted_contact']}|"
            f"{row['surviving_start_proposal']} / {cancelled}|"
            f"{terminal['reason']}:{terminal['end_proposal_frame']}→{terminal['closed_frame']}→{terminal['finalization_frame']}|"
            f"{row['causal_group']}|"
        )
    (output / "all36_model_temporal_firsts.md").write_text("\n".join(lines) + "\n")
    manifest = {
        "mode": "offline merged own-cache and paired component diagnostic review; not another full inference",
        "fresh_run": str(run),
        "own_semantic_trace_sha256": sha(semantic / "fsm_trace.jsonl"),
        "own_temporal_audit_manifest_sha256": sha(audit / "manifest.json"),
        "component_probes": probe_provenance,
        "distinct_frames_with_raw_model_diagnostics": len(diagnostics),
        "complete_onset_review_windows": sum(
            row["onset_model_diagnostic_coverage"]["complete_for_this_review_window"] for row in results
        ),
        "total_ground_truth_rows": len(results),
        "labels_usage": "completed offline grouping only, never supplied to inference",
        "script_sha256": sha(Path(__file__)),
        "output_sha256": sha(output / "all36_model_temporal_firsts.json"),
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (output / "executor.py").write_bytes(Path(__file__).read_bytes())
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
