"""Compile source-reviewed G69 diagnostics without inference or pipeline edits."""

# Long strings are the generated report prose.
# ruff: noqa: E501
from __future__ import annotations

import csv
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent.parent
EXTRACT = ROOT / "attempt_v1"
REVIEW = ROOT / "visual_review_v1"
RUN_ROOT = Path(
    "/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261110/test_02/improved_v1"
)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, data):
    with Path(path).open("x") as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write("\n")


def main():
    for name in ["diagnosis.json", "raw_candidates.csv", "fsm_events.csv", "REPORT.md", "verification_receipt.json"]:
        assert not (ROOT / name).exists(), name
    cv2.setNumThreads(1)
    inputs = {str(Path(__file__).resolve()): sha(__file__)}

    def bind(path):
        path = Path(path).resolve()
        inputs[str(path)] = sha(path)
        return path

    extraction = read(bind(EXTRACT / "extraction_completion.json"))
    assert extraction["status"] == "completed_read_only_source_cache_extraction"
    for relative, digest in extraction["artifact_sha256"].items():
        assert sha(EXTRACT / relative) == digest, relative
    binding = read(bind(EXTRACT / "input_binding.json"))
    for path, digest in binding["inputs_sha256"].items():
        assert sha(path) == digest, path
        inputs[path] = digest
    frames = read(bind(EXTRACT / "frame_readout.json"))
    cache = {r["f"]: r for r in read(bind(EXTRACT / "cache_window.json"))}
    trace = read(bind(EXTRACT / "fsm_window.json"))
    assert [r["frame"] for r in frames] == list(range(27312, 27376))
    assert set(cache) == set(range(27312, 27376))
    for row in frames:
        original = cache[row["frame"]]
        assert original["s"] == row["raw_xy"]
        assert original["sa"]["candidates"] == row["candidates"]
        assert original["sh"] == 11 and original["r"] is False
    source_receipts = read(bind(EXTRACT / "source_receipts.json"))
    assert all(sha(EXTRACT / r["source_png"]) == r["source_png_sha256"] for r in source_receipts)
    manifest = read(RUN_ROOT / "diagnostic_replay/replay_manifest.json")
    source_dir = RUN_ROOT / "diagnostic_replay" / manifest["core_source_snapshot"]["directory"]
    for relative in [
        "sports/badminton/src/bai_badminton/engine.py",
        "sports/badminton/src/bai_badminton/events/rally_motion.py",
        "sports/badminton/src/bai_badminton/perception/shuttle_post.py",
    ]:
        path = bind(source_dir / relative)
        assert inputs[str(path)] == manifest["core_source_snapshot"]["sha256"][relative]

    # Review pages are derived from the64 already extracted frames. No video is
    # reopened and no additional source frames are decoded.
    for page in range(4):
        tiles = []
        for frame in range(27312 + page * 16, 27328 + page * 16):
            im = cv2.imread(str(EXTRACT / "source" / f"frame_{frame:05}.png"))
            tile = np.zeros((384, 640, 3), np.uint8)
            tile[24:] = cv2.resize(im, (640, 360))
            cv2.putText(tile, str(frame), (4, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            tiles.append(tile)
        path = REVIEW / f"full_source_page_{page + 1:02}.png"
        montage = np.vstack([np.hstack(tiles[i : i + 4]) for i in range(0, 16, 4)])
        if path.exists():
            assert np.array_equal(cv2.imread(str(path)), montage)
        else:
            assert cv2.imwrite(str(path), montage)
    write(
        REVIEW / "render_parameters.json",
        {
            "source_frames": "Only existing attempt_v1/source/frame_27312..27375 PNGs; no new decode",
            "top_edge_sequence": {
                "frames": [27323, 27324, 27325, 27326, 27327, 27328, 27329, 27352, 27353, 27354, 27355, 27356],
                "crop_xyxy": [740, 0, 920, 125],
                "resize": [540, 375],
                "interpolation": "nearest",
                "header_pixels": 25,
            },
            "full_pages": {"frames_per_page": 16, "columns": 4, "resize": [640, 360], "header_pixels": 24},
            "unscaled_source_unchanged": True,
        },
    )

    candidates, review = [], []
    for row in frames:
        frame = row["frame"]
        if frame == 27312:
            tag = "upper_boundary_appearance_uncertain"
        elif frame <= 27323:
            tag = "bright_upper_object_descends_source_supported"
        elif frame == 27324:
            tag = "far_overhead_swing_object_racket_vicinity_exact_impact_unadjudicated"
        elif frame == 27325:
            tag = "bright_outgoing_streak_rises"
        elif frame <= 27328:
            tag = "partial_upper_edge_bright_object_still_visible"
        elif frame <= 27352:
            tag = "upper_object_not_resolved_consistent_with_outside_fov_not_physical_absence_label"
        elif frame == 27353:
            tag = "upper_border_reentry_uncertain_lower_selected_branch_follows_racket"
        elif frame <= 27371:
            tag = "clear_upper_return_descends_near_player_prepares_overhead"
        else:
            tag = "near_overhead_swing_trajectory_redirect_exact_contact_unadjudicated"
        review.append(
            {
                "frame": frame,
                "agent_diagnostic_observation": tag,
                "GroundTruth": None,
                "lower_alias_observation": "selected point follows visible racket head"
                if 27348 <= frame <= 27353
                else None,
                "source_receipt": f"attempt_v1/source_receipts.json#frame={frame}",
            }
        )
        assert len(row["candidates"]) <= 8
        for candidate in row["candidates"]:
            candidates.append(
                {
                    "frame": frame,
                    "raw_x": None if row["raw_xy"] is None else row["raw_xy"][0],
                    "raw_y": None if row["raw_xy"] is None else row["raw_xy"][1],
                    "raw_support": row["support"],
                    "status": row["status"],
                    **candidate,
                }
            )
    gap = [r for r in frames if 27326 <= r["frame"] <= 27347]
    gap_candidates = [c for r in gap for c in r["candidates"]]
    assert len(gap) == 22 and all(r["raw_xy"] is None for r in gap)
    assert len(gap_candidates) == 15 and sum(not r["candidates"] for r in gap) == 10
    assert all(c["mask_allows_peak"] and not c["above_inference_threshold"] for c in gap_candidates)
    assert max(c["peak_support"] for c in gap_candidates) == 0.220703125
    assert {r["view"] for r in frames} == {"main"}
    assert {r["calibration_state"] for r in frames} == {"VALID"}
    assert {r["content_epoch"] for r in frames} == {33}
    assert {r["person_count"] for r in frames} == {2}
    with (ROOT / "raw_candidates.csv").open("x", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(candidates[0]))
        writer.writeheader()
        writer.writerows(
            {k: json.dumps(v) if isinstance(v, (list, dict)) else v for k, v in row.items()} for row in candidates
        )
    significant = [
        r
        for r in trace
        if r["call"] != "step" or r["before"]["state"] != r["after"]["state"] or any(r["update"].values())
    ]
    with (ROOT / "fsm_events.csv").open("x", newline="") as stream:
        fields = [
            "frame",
            "call",
            "state_before",
            "state_after",
            "tentative_end",
            "invisible_run",
            "observation",
            "update",
        ]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for r in significant:
            writer.writerow(
                {
                    "frame": r["frame"],
                    "call": r["call"],
                    "state_before": r["before"]["state"],
                    "state_after": r["after"]["state"],
                    "tentative_end": r["after"]["tentative_end"],
                    "invisible_run": r["after"]["invisible_run"],
                    "observation": json.dumps(r.get("observation")),
                    "update": json.dumps(r["update"]),
                }
            )
    events = []
    event_path = bind(RUN_ROOT / "downstream_exports/live_events.jsonl")
    with event_path.open() as stream:
        for line_number, line in enumerate(stream, 1):
            event = json.loads(line)
            if event["type"] in {"contact", "stroke", "rally_end", "rally_start"} and (
                27312 <= event["frame_start"] <= 27375 or 27312 <= (event.get("frame_end") or -1) <= 27375
            ):
                if event["type"] == "rally_end":
                    event["payload"] = {k: v for k, v in event["payload"].items() if k != "shots"}
                events.append({"source_line": line_number, "event": event})
    write(REVIEW / "downstream_events.json", events)

    csv_path = bind(BASE.parent.parent / "Part2/dataset/Test2_Full/Test2_Full_rally.csv")
    with csv_path.open() as stream:
        row69 = list(csv.DictReader(stream))[68]
    assert int(row69["Start_Frame"]) == 26616 and int(row69["End_Frame"]) == 27668
    controls = {}
    for number in [39, 55, 69]:
        path = bind(RUN_ROOT / f"causal_analysis/cases/gt_{number:03}.json")
        case = read(path)
        controls[str(number)] = {
            "reference_interval_half_open": case["reference_interval_half_open"],
            "machine_mechanism_tags": case["machine_mechanism_tags"],
            "physical_failure_classification": case["physical_failure_classification"],
            "review_requirements": case["review_requirements"],
        }

    diagnosis = {
        "schema": "G69-source-observability-diagnosis:v1",
        "scope": "Completed historic Test2improved_v1 source/cache diagnostic; not new candidate full inference",
        "GroundTruth": None,
        "physical_metrics": {"FN": None, "precision": None, "recall": None, "contact_accuracy": None},
        "window_inclusive": [27312, 27375],
        "fps": 30,
        "retained_reviewed_frames": 64,
        "codec_preroll_count": 12,
        "new_NN": False,
        "visibility_review": review,
        "accepted_raw_and_top8_candidates_pinned": [
            r for r in frames if 27313 <= r["frame"] <= 27327 or 27348 <= r["frame"] <= 27354
        ],
        "last_pre_gap_accepted_model_observation": next(r for r in frames if r["frame"] == 27325),
        "first_raw_reacquisition": next(r for r in frames if r["frame"] == 27348),
        "first_clear_agent_reviewed_upper_return": 27354,
        "raw_gap": {
            "inclusive": [27326, 27347],
            "frames": 22,
            "retained_candidates": 15,
            "frames_without_retained_candidate": 10,
            "max_candidate_support": 0.220703125,
            "all_retained_candidates_mask_allowed": True,
            "inference_threshold": 0.5,
            "diagnostic_retention_floor": 0.1,
            "raw_missing_is_not_physical_absence": True,
        },
        "confirmed_machine_chain": [
            "Below-threshold raw selection -> association missing, not rejection",
            "Missing -> gap counter; existing exit recovery fails lower-image first selected return",
            "27335 ending ->27340 closed(end27325) ->27348 final publication on lower model reacquisition",
            "Lower branch motion27349–51 ->new interval from27349;27353 branch switch participates in estimated contact",
            "27354 upper raw max replaces lower candidate; physical event remains unreviewed; unknown class/no winner retained",
        ],
        "significant_fsm_events": significant,
        "legacy_generated_benchmark_reference": {
            "csv_path": str(csv_path),
            "csv_sha256": inputs[str(csv_path)],
            "data_row": 69,
            "values": row69,
            "independent_shuttle_or_contact_GT": False,
        },
        "existing_control_metadata_no_new_source_decode": controls,
        "software_defect_established": False,
        "engineering_limitation": "Raw-model missingness lacks explicit observability context; moving racket alias becomes observed endpoint and defeats current top-exit return proof. Current static-only association and gap arithmetic follow their stated contracts.",
        "future_proposal": {
            "adoption_status": "design only; no change executed",
            "typed_visibility_hypothesis": "Keep raw_missing separate from source-supported outside_fov/competing_branch uncertainty; coordinates remainnull, never observed/interpolated as physical truth",
            "eligibility": "Already qualified rally; credible observed upward approach to image boundary, valid consistent scene/camera and bounded history; no start from absent evidence",
            "association": "Retain independent moving branches and provenance; do not turn low-support peaks into accepted observations or suppress all near-racket coordinates",
            "termination": "Use bounded qualified unknown visibility rather than treating every raw miss as negative end evidence; preserve cut/replay/accepted-terminal reset and existing global gap/merge/model thresholds",
            "gates_before_trial": "Independent source-reviewed visibility/branch/contact controls, match-disjoint evaluation, singles+doubles and format uncertainty, causal no-future-leak test, native cache/version proof",
            "negative_controls": [
                "G39[13427,13707): do not invent onset from missing/weak/stationary evidence",
                "G55[20061,20884): invalid geometry/onset missingness cannot acquire qualified outside-view continuity",
                "Post-point pickup/walking and true terminal rest: no persistent rally from player motion alone",
                "Ordinary off-field object, moving racket/body glare and crossing limbs: no named object identity from nearest geometry",
                "Cut/replay/camera change and missing calibration: reset or abstain",
                "Real shuttle near racket at impact: no blanket body/racket exclusion",
                "All preserved original references and fullTest1/Test2 regression; no policy fitted to G69",
            ],
        },
        "input_sha256": inputs,
    }
    write(ROOT / "diagnosis.json", diagnosis)
    report = [
        "# G69: image-boundary censoring, racket alias and rally split",
        "",
        "The continuous source sequence supports an **out-of-frame flight hypothesis plus a moving racket distractor**, rather than22 independently established visible-shuttle misses. The raw gap is real; its interpretation as negative rally evidence is the weakness. This review establishes source-bound machine causes and agent visual diagnostics. Physical ground truth, FN count and physical accuracy remain **unavailable**, not zero. No production, annotation, model, threshold or current candidate was changed.",
        "",
        "## Scope and source proof",
        "",
        "The existing completed `Test2/improved_v1` worker/parent/catalogue and its exact own-parity semantic replay are verified. Source SHA `4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a`; analysis-proxy SHA `2841ee54fb0b6d28c2a57e89293ba4530173980635c21aa8d08f60f52931b6cd`. The original Test2video is absent: this is exact source-bound **proxy** review. TrackNet checkpoint SHA `df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a` is rehashed, never loaded.",
        "",
        "Only64selected frames27312–27375 (910.400000–912.500000s at30fps) were retained/analysed. The H264decoder needs12additional prior-frame codec preroll; those were discarded without pixel review. Rational PTS, round-trip PNG equality, BGR and file hashes are retained for every selected frame. Two consumed closed cache segments match the completed catalogue; raw/association fields also exactly match the older snapshot independently bound to its completed run. No SQLite, neural inference, download or additional control-video decoding was used.",
        "",
        "[Input bindings](attempt_v1/input_binding.json), [source pixel/PTS receipts](attempt_v1/source_receipts.json), [cache rows](attempt_v1/cache_window.json), [bounded FSM trace](attempt_v1/fsm_window.json), [all retained candidates](raw_candidates.csv), and [structured diagnosis](diagnosis.json) preserve the reproduction. The recorded source commit and actual executed source hashes are retained rather than replacing them with the new candidate's commit.",
        "",
        "## What is visible",
        "",
        "[All64upper-region source crops](attempt_v1/top_source_montage.png) and [near-player source crops](attempt_v1/body_source_montage.png) preserve the two branches separately from predictions. [Enlarged boundary sequence](visual_review_v1/top_edge_sequence.png) uses nearest-neighbour pixels and an external label strip. Full-frame review pages are [1](visual_review_v1/full_source_page_01.png), [2](visual_review_v1/full_source_page_02.png), [3](visual_review_v1/full_source_page_03.png), [4](visual_review_v1/full_source_page_04.png).",
        "",
        "-27313–27323: a bright upper object descends. At27324 the far athlete makes an overhead swing; exact impact/object-versus-racket separation is not adjudicated.27325shows a bright upward streak.\n-27326–27328: part of that bright object remains at the upper border. The model supplies only low-support candidates, not accepted coordinates.\n-27329–27352: the upper object is not visually resolved in the reviewed sequence, consistent with flight outside the image. This is a supported uncertainty hypothesis, not a physical absence label.27353has an uncertain upper-border re-entry candidate.27354is the first clearly visible descending upper return in this review.\n-27348–27353: the selected lower model coordinates follow the near blue athlete's visible racket head while that athlete prepares an overhead response. This is a source-supported alias diagnosis, not independent shuttle/contact annotation. The upper return later descends toward the near overhead swing around27371–27372; exact contact time/class remain unadjudicated.",
        "",
        "The camera, player motion and displayed16:16 continue without an observed edit in this64-frame window. Main view, VALID geometry, camera shot11, content epoch33 and two returned people persist. No new pixel-ground-truth file is created: the per-frame `visibility_review` tags are explicitly agent diagnostics with `GroundTruth:null`.",
        "",
        "## Raw selection and mask evidence",
        "",
        "|Frame|Accepted raw(x,y), support|Retained competing peak / interpretation|",
        "|---|---|---|",
        "|27325|(788.869,56.927),0.635254|Last accepted pre-gap model point; fresh model observation is not calibrated physical truth.|",
        "|27326|None|Rank1(787.5,57.5),0.188232 follows prior tail; rank2(807.5,2.5),0.176392 is near the visible upper edge. Lowering the threshold does not automatically choose the right branch.|",
        "|27327/27328|None|Upper peaks(807.5,5),0.204346/0.220703; source partial edge object still visible.|",
        "|27326–27347|None on22frames|15retained candidates across12frames;10frames have none above diagnostic floor0.1. All15peaks mask-allowed and below inference threshold0.5.|",
        "|27348|(784.968,429.917),0.674805|First accepted reacquisition follows visible racket head, not a newly certified shuttle position.|",
        "|27353|(806.018,449.495),0.685059|Upper rank3(852.5,2.5),0.117065; lower racket branch wins.|",
        "|27354|(855.600,6.573),0.752441|Lower rank2(815,457.5),0.685303 still exceeds threshold. The global maximum switches branches.|",
        "",
        "Exact accepted outputs and every retained top-eight candidate for27313–27327and27348–27354 are pinned in `diagnosis.json`, with support, mask flag, centroid/spread and selected status. Top-eight is a retention bound, not eight guaranteed candidates. No full heatmaps are retained. Below-floor responses and unseen mask values cannot be reconstructed or called absent. Detailed raw/masked maxima at27326/27327 agree and explicitly say `below_threshold`; later detailed diagnostics are sparse. The confirmed claim is no mask rejection of the **retained** candidates and no association veto of an accepted raw coordinate during the22-frame gap.",
        "",
        "TrackNet's recorded decoder selects the global maximum component above0.5. The association provider's declared scope is co-observed **static** distractors; the coherent moving racket is not established static background. It preserves these fresh raw selections and emits no alternative physical coordinate. This is a capability limitation, not proof that changing a threshold, choosing the upper peak or masking all player/racket pixels would be safe.",
        "",
        "## How the missingness becomes two rallies",
        "",
        "The exact completed own-parity trace, not a new parallel FSM, records:",
        "",
        "|Frame|Machine transition|",
        "|---|---|",
        "|27325|Last accepted raw observation before gap.|",
        "|27335|Tenth missing observation: IN_PLAY→ENDING, proposed end27325.|",
        "|27340|Existing15-frame lookahead expires: CLOSED with end27325.|",
        "|27348|Lower model point returns; adjacent observed speed is unavailable. Observation separation23frames exceeds unchanged round(0.75×30)=22merge budget; publish[26654,27325).|",
        "|27349–27351|Three observed-motion samples on lower branch open a new interval from27349.|",
        "|27353|Branch switch vicinity contributes an estimated contact candidate.|",
        "|27354|Clearly visible upper return wins the heatmap; previous interval is already published.|",
        "",
        "`engine.py` maps absent accepted observations to MISSING (or marked reconstruction if available); `RallyEvidence.step_evidence()` increments the base gap counter unless independent continuation/exit support qualifies. `use_reconstruction=False` is the rally continuation flag, not permission to treat interpolated points as observed. `use_exit_recovery=True` is already enabled: `image_exit_return_supported()` requires the **first observed return bracket** in the top10% band with coherent upward/downward motion. Its actual first return is lower y429.917, outside the image's72px top-band boundary; this bracket cannot qualify. The raw source/candidate alias therefore defeats the existing boundary-recovery proof. No arithmetic/order bug or automatic within-budget recovery was established.",
        "",
        "[Downstream source events](visual_review_v1/downstream_events.json) show estimated contacts at27324,27353and27371. At27353the incoming motion uses lower27350–27353, while outgoing27353–27356crosses to the upper branch: fitted outgoing speed121.152px/frame and residual126.964px are not a coherent physical flight. The physical evidence status is **insufficient**, racket contact/overlap is false, and the stroke staysunknown. A high uncalibrated heuristic event support0.985997 is not physical contact confidence. No named winner or accepted point is established by this sequence. Unknown classification is appropriate uncertainty; the extra candidate still affects shot/rally analytics.",
        "",
        "Legacy generated referenceG69is[26616,27668), matched prediction[26654,27325) has IoU0.637832700, start+38frames/end−343frames/duration−381frames, with another prediction[27349,27649) unmatched under one-to-one matching. These are preserved benchmark-reference errors, not independently annotated shuttle/point truth. The later terminal outside this64-frame decode is not newly visually adjudicated here.",
        "",
        "## Reusable proposal and required controls",
        "",
        "The evidence supports a **versioned observation/association design trial**, not an immediate production fix. Preserve raw model missingness separately from a source-supported `outside_fov` or `competing_branches` visibility hypothesis. Coordinates staynull while visibility is unknown; no trajectory, contact, named identity or winner is fabricated. Eligibility requires a previously qualified rally, credible observed outgoing boundary motion, consistent scene/camera and bounded history. Missingness must never create a start or an indefinite extension.",
        "",
        "A moving-branch association provider must preserve independent raw alternatives and reject/abstain only with positive contradictory evidence. The current six-sample racket branch cannot be solved by the existing static-only rule or by a one-isolated-observation omission. Never promote0.1diagnostic peaks to accepted observations, select a convenient upper branch, or remove every near-racket point: genuine impacts occur near rackets. Visibility support should inform bounded end uncertainty without changing global gap/merge/model thresholds. Existing cuts, replays, invalid geometry and independently accepted terminal evidence must still end/reset incompatible state. Precise state semantics, causality/lookahead, provenance, source binding and cache versions require tests before integration.",
        "",
        "Required contrastive controls before any trial are: G39[13427,13707) (do not invent onset from missing/weak/stationary evidence), G55[20061,20884) (invalid/reacquiring geometry and early missingness cannot earn qualified continuation), post-point pickup/walking and true rest, normal off-field objects, camera/cut/replay changes, coherent/ambiguous moving racket branches, real near-racket contacts, long flights without timely return, uncertain format and four-player doubles. Only existing metadata forG39/G55was read; no new control frames were decoded. Their reference intervals are development controls, not new physical labels. Establish reviewed visibility/branch/contact labels and match-disjoint holdouts before claiming an accuracy gain.",
        "",
        "A new generic provider/schema could be justified after those controls, but no source-contract software defect or safe production policy is established by this one window. The immediate improvement is the diagnosis: do not report22visible-object false negatives, lower the detector threshold, extend global timeouts, force a rally merge, or claim D01 repaired G69. Full latest candidate Test1/Test2evaluation remains a separate unfinished gate.",
    ]
    # Keep the sequential observations as proper CommonMark list items.
    report = [line.replace("\n-", "\n- ").replace("-273", "- 273") for line in report]
    (ROOT / "REPORT.md").write_text("\n".join(report) + "\n")
    for path, digest in inputs.items():
        assert sha(path) == digest, path
    write(
        ROOT / "verification_receipt.json",
        {
            "status": "completed_read_only_G69_source_diagnosis",
            "sealed_utc": datetime.now(UTC).isoformat(),
            "retained_exact_proxy_frames": 64,
            "codec_preroll_frames": 12,
            "input_sha256": inputs,
            "input_hashes_unchanged": True,
            "artifact_sha256": {str(p.relative_to(ROOT)): sha(p) for p in ROOT.rglob("*") if p.is_file()},
            "ground_truth": None,
            "physical_accuracy_claimed": False,
            "new_NN": False,
            "production_models_annotations_and_prior_results_modified": False,
            "Test3_accessed": False,
        },
    )
    print(json.dumps({"status": "sealed", "frames": 64, "input_bindings": len(inputs), "events": len(events)}))


if __name__ == "__main__":
    main()
