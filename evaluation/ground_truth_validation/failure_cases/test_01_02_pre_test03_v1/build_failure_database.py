"""Read-only Test1/2 evidence consolidation; writes only beside this script.

No inference, reference modification, new accuracy labels, or Test3 access.
Run with the repository .venv Python. Original case/source bytes are hashed.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
WORK = ROOT / "evaluation/ground_truth_validation"
INPUTS: dict[str, dict] = {}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def bind(path):
    path = Path(path).resolve()
    assert "test_03" not in str(path) and "Test3" not in str(path)
    if str(path) not in INPUTS:
        INPUTS[str(path)] = {"sha256": sha(path), "bytes": path.stat().st_size}
    return {"path": str(path), **INPUTS[str(path)]}


def read(path):
    bind(path)
    return json.loads(Path(path).read_text())


def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def metrics(test, arm):
    run = WORK / f"test_{test:02d}" / arm
    p = run / "bound_reference_diagnostics/component_reference_metrics.json"
    if not p.exists():
        p = run / "all_reference_components/component_reference_metrics.json"
    doc = read(p)
    refs = doc["interval_reference_comparisons"]
    if test == 2:
        detail = read(p.parent / "reference_row_comparisons.json")
        refs = {k: {**v, **detail[k]} for k, v in refs.items()}
    return doc, refs, p


def exact_iou(row):
    s, e = row.get("pred_start_frame"), row.get("pred_end_frame")
    if s is None or e is None:
        return None
    gs, ge = row["gt_start_frame"], row["gt_end_frame"]
    return Fraction(max(0, min(e, ge) - max(s, gs)), max(e, ge) - min(s, gs))


def fraction_record(value):
    return None if value is None else {"fraction": str(value), "value": float(value)}


def compact_summary(summary):
    return {k: ({"count": len(v), "first": v[0] if v else None,
                  "last": v[-1] if v else None} if isinstance(v, list) else v)
            for k, v in summary.items()}


def record_population(raw):
    return len(raw)


def make_database():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "visual_review").mkdir(exist_ok=True)
    annotations, comparisons, ref_metrics, mixed, cases, sheet_entries = [], [], [], [], [], []
    all_runs = {}
    for test in (1, 2):
        prior_path = WORK / ("test_01/diagnostics/temporal_root_cause/significant_case_gate_audit.json" if test == 1 else "test_02/diagnostics/temporal_root_cause/case_register.json")
        prior_doc = read(prior_path)
        prior_cases = {(x["case"]["case_id"] if test == 1 else x["case_id"]): x for x in prior_doc["cases"]}
        for arm in ("baseline_v1", "improved_v1"):
            all_runs[test, arm] = metrics(test, arm)
        baseline, before, beforepath = all_runs[test, "baseline_v1"]
        improved, after, afterpath = all_runs[test, "improved_v1"]
        assert baseline["source_sha256"] == improved["source_sha256"]
        assert len(after) == (6 if test == 1 else 3)
        for annotation in improved["annotation_applicability"]:
            p = ROOT / f"Part2/dataset/Test{test}_Full" / annotation["file"]
            evidence = bind(p)
            assert evidence["sha256"] == annotation["sha256"]
            info = {"test": test, **annotation, "original": evidence,
                    "physical_gt_adjudicated": False}
            if p.suffix == ".csv":
                with p.open(newline="", encoding="utf-8-sig") as stream:
                    reader = csv.DictReader(stream)
                    rows = list(reader)
                    info.update(columns=reader.fieldnames, raw_data_row_count=len(rows))
            else:
                info["actual_content"] = read(p)
            annotations.append(info)
        for name, ref in after.items():
            b = before[name]
            assert len(b["comparison"]) == len(ref["comparison"])
            count = len(ref["comparison"])
            ref_metrics.append({"test": test, "reference": name, "role": ref["role"],
                                "physical_accuracy": False, "before": b["metrics"],
                                "after": ref["metrics"], "before_source": bind(beforepath),
                                "after_source": bind(afterpath), "valid_rows": count,
                                "invalid_rows": ref["invalid_rows"],
                                "matching_policy": ref["matching_policy"]})
            changed = []
            for br, ar in zip(b["comparison"], ref["comparison"]):
                assert br["reference_data_row"] == ar["reference_data_row"]
                assert br["matching_status"] == ar["matching_status"]
                assert br.get("pred_rally") == ar.get("pred_rally")
                row = ar["reference_data_row"]
                entry = {"id": f"test{test:02d}:{name}:row{row}", "test": test,
                         "reference": name, "reference_role": ref["role"],
                         "source_data_row": row, "csv_line": row + 1,
                         "reference_original": bind(ROOT / f"Part2/dataset/Test{test}_Full" / name),
                         "original_values": ref["raw_rows"][row - 1],
                         "before": br, "after": ar,
                         "physical_ground_truth": False}
                comparisons.append(entry)
                bi, ai = exact_iou(br), exact_iou(ar)
                if bi is not None and ai is not None:
                    assert abs(float(bi) - br["interval_iou"]) < 1e-10
                    assert abs(float(ai) - ar["interval_iou"]) < 1e-10
                if bi != ai:
                    assert test == 2
                    changed.append({**entry, "exact_iou_before": fraction_record(bi),
                                    "exact_iou_after": fraction_record(ai),
                                    "exact_iou_delta": fraction_record(ai - bi),
                                    "start_delta_frames": ar["pred_start_frame"] - br["pred_start_frame"],
                                    "end_delta_frames": ar["pred_end_frame"] - br["pred_end_frame"]})
            if test == 2:
                assert len(changed) == 6
                denominator = ref["metrics"]["detection"]["matched_count"]
                exact_delta = sum((Fraction(x["exact_iou_delta"]["fraction"]) for x in changed), Fraction()) / denominator
                mb = b["metrics"]["overlap"]["mean_iou"]
                ma = ref["metrics"]["overlap"]["mean_iou"]
                assert abs(float(exact_delta) - (ma - mb)) < 1e-12
                mixed.append({"reference": name, "role": ref["role"],
                              "matched_denominator": denominator, "mean_iou_before": mb,
                              "mean_iou_after": ma, "exact_mean_delta": fraction_record(exact_delta),
                              "unchanged_assignment_and_detection_counts": True,
                              "changed_matched_rows": changed})
        packages = {}
        for arm in ("baseline_v1", "improved_v1"):
            root = WORK / f"test_{test:02d}" / arm / "visual_failure_package"
            index = read(root / "failure_case_index.json")
            manifest = read(root / "manifest.json")
            assert manifest["source_sha256"] == improved["source_sha256"]
            assert manifest["original_source_pts_exact"] and manifest["full_perception_and_trace_coverage_verified"]
            assert len(index) == (14 if test == 1 else 39)
            packages[arm] = (root, {r["case_id"]: r for r in index}, manifest)
        assert set(packages["baseline_v1"][1]) == set(packages["improved_v1"][1])
        for case_id in packages["improved_v1"][1]:
            observations = {}
            for arm, (root, index, manifest) in packages.items():
                record = index[case_id]
                p = root / record["case_json"]
                raw = read(p)
                summary = raw["diagnostic_summary"]
                gs, ge = record.get("gt_start_frame"), record.get("gt_end_frame")
                signal = None
                if gs is not None and ge is not None:
                    steps = [x for x in raw["semantic_trace"] if x.get("call") == "step" and gs <= x["frame"] < ge]
                    observations_in_span = [x for x in raw["raw_perception"] if gs <= x["f"] < ge]
                    source_refs = all_runs[test, arm][1][f"Test{test}_Full_rally.csv"]
                    predictions = {x["pred_rally"]: (x["pred_start_frame"], x["pred_end_frame"]) for x in source_refs["comparison"] if x.get("pred_rally") is not None}
                    predictions.update({x["pred_rally"]: (x["start_frame"], x["end_frame"]) for x in source_refs["metrics"]["unmatched_predictions"]})
                    overlaps = [{"pred_rally": pid, "start_frame": s, "end_frame": e,
                                 "exact_iou": fraction_record(Fraction(min(e, ge) - max(s, gs), max(e, ge) - min(s, gs)))}
                                for pid, (s, e) in sorted(predictions.items()) if min(e, ge) > max(s, gs)]
                    signal = {"reference_half_open": [gs, ge], "raw_frames": len(observations_in_span),
                              "raw_shuttle_available_frames": sum(x.get("s") is not None for x in observations_in_span),
                              "step_count": len(steps),
                              "step_observation_kinds": dict(Counter(x.get("observation", {}).get("kind", "unknown") for x in steps)),
                              "fsm_after_step_states": dict(Counter(x.get("after", {}).get("state", "unknown") for x in steps)),
                              "overlapping_prediction_intervals": overlaps,
                              "source_role": "generated reference span; signal counts are diagnostics, not physical visibility/contact truth"}
                observation = {"case_record": record, "raw_case_evidence": bind(p),
                               "package_manifest": bind(root / "manifest.json"),
                               "source_sha256": raw["source_sha256"], "proxy_sha256": raw["proxy_sha256"],
                               "context_half_open": raw["context_half_open"],
                               "replay_windows_half_open": raw["replay_windows_half_open"],
                               "diagnostic_summary": compact_summary(summary),
                               "raw_perception_rows": len(raw["raw_perception"]),
                               "trace_operations": len(raw["semantic_trace"]),
                               "reference_span_signal": signal,
                               "event_counts": dict(Counter(x.get("type", x.get("event_type", "unknown")) for x in raw["events"])),
                               "source_images": []}
                if arm == "improved_v1":
                    candidates = [record.get("gt_start_frame"), record.get("pred_start_frame", record.get("start_frame")),
                                  record.get("gt_end_frame"), record.get("pred_end_frame", record.get("end_frame"))]
                    candidates = list(dict.fromkeys(x for x in candidates if x is not None))
                    available = sorted(int(p.stem) for p in (root / "frames").glob("*.jpg"))
                    chosen = candidates[:2] if len(candidates) > 1 else candidates
                    for frame in chosen:
                        selected = min(available, key=lambda n: abs(n - frame))
                        p = root / "frames" / f"{selected}.jpg"
                        ev = bind(p)
                        assert ev["sha256"] == manifest["image_sha256"][p.name]
                        observation["source_images"].append({"requested_frame": frame, "decoded_frame": selected,
                                                            "exact_requested_frame": selected == frame,
                                                            "time_seconds": selected / 30, **ev})
                    sheet_entries.append((test, case_id, record, observation["source_images"]))
                observations[arm] = observation
            record = observations["improved_v1"]["case_record"]
            categories = []
            if record["matching_status"] != "matched":
                categories.append(record["matching_status"] + "_under_generated_reference_policy")
            else:
                for field, negative, positive in (("start_frame_error", "early_start", "late_start"),
                                                   ("end_frame_error", "early_end", "late_end")):
                    value = record.get(field, 0)
                    if value:
                        categories.append(positive if value > 0 else negative)
            d = observations["improved_v1"]["diagnostic_summary"]
            first, start = d["first_processed_observation_frame"], record.get("gt_start_frame")
            hypotheses = []
            if start is not None and first is not None and first > start:
                hypotheses.append({"observation": "first processed observation is later than reference start",
                                   "delta_frames": first - start,
                                   "candidate_modules": ["engine.py", "rally_fsm.py", "calibration/view admission"],
                                   "causal_status": "association_only; inspect eligibility and original pixels"})
            if d["camera_lost_frames"]:
                hypotheses.append({"observation": "camera-lost frames occur somewhere in case context",
                                   "count": d["camera_lost_frames"], "causal_status": "not proof of boundary cause"})
            if d["content_change_frames"]["count"]:
                hypotheses.append({"observation": "content epoch decision occurs in context",
                                   **d["content_change_frames"], "causal_status": "hypothesis event; not labelled physical cut"})
            prior = prior_cases[case_id]
            if test == 2:
                prior_summary = {key: prior.get(key) for key in ("expected_reference", "actual_prediction", "metrics", "reference_or_prediction_observation_counts", "raw_provider_absent_frames", "association_withheld_frames", "invalid_temporal_context_frames", "content_epochs", "historical_source_diagnostic_reused", "physical_failure_classification", "new_temporal_software_defect_established_by_this_register")}
                for key in ("prediction_finalization", "context_candidate_cancellations", "context_terminal_proposals"):
                    values = prior.get(key)
                    values = values if isinstance(values, list) else [values] if values else []
                    prior_summary[key] = [{"frame": x["frame"], "call": x["call"], "update": x.get("update"), "exchange_admission": x.get("exchange_admission"), "end_reason": x.get("after", {}).get("end_reason")} for x in values]
            else:
                prior_summary = {}
                for key in ("start_disagreement", "end_disagreement", "start_context", "end_context"):
                    value = prior.get(key, {})
                    prior_summary[key] = {k: value.get(k) for k in ("range", "observations", "states_before", "content_epochs", "camera_shots", "association_reasons", "contacts", "discontinuities", "state_transition_frames")}
            cases.append({"id": f"test{test:02d}:{case_id}", "test": test, "packaged_case_id": case_id,
                          "reference": f"Test{test}_Full_rally.csv", "reference_role": "legacy_generated_reference_agreement",
                          "original_causal_classification": "unreviewed", "physical_gt": False,
                          "component": "rally segmentation and upstream evidence admission",
                          "candidate_modules": ["sports/badminton/src/bai_badminton/engine.py",
                                                "sports/badminton/src/bai_badminton/events/rally_fsm.py"],
                          "observed_categories": categories, "context_hypotheses": hypotheses,
                          "confirmed_pipeline_defect": False,
                          "priority": "P1_review" if record["matching_status"] != "matched" else "P2_review",
                          "root_cause_status": "unresolved; generated interval disagreement alone cannot establish defect",
                          "validation_needed": "Independently review serve/contact/end/cut visibility on full synchronized windows; inspect gate trace; add negative/ordinary/doubles controls before code changes.",
                          "prior_baseline_diagnostic": {"source": bind(prior_path), "arm": "baseline_v1", "review_status": "agent diagnostic evidence, not physical GT; original helper/gate interpretation retained", "summary": prior_summary},
                          "observations": observations})
    assert len(comparisons) == 422
    assert len(cases) == 53
    assert len([x for x in annotations if x["test"] == 2]) == 7
    assert len([x for x in annotations if x["test"] == 1]) == 9
    save("annotation_inventory.json", annotations)
    save("reference_metrics.json", ref_metrics)
    save("mixed_iou_exact.json", mixed)
    for name, values in (("reference_rows.jsonl", comparisons), ("failure_database.jsonl", cases)):
        (OUT / name).write_text("".join(json.dumps(v, ensure_ascii=False) + "\n" for v in values))
    with (OUT / "failure_index.csv").open("w", newline="") as stream:
        fields = ["id", "test", "status", "reference_start", "reference_end", "predicted_start_before", "predicted_end_before", "predicted_start_after", "predicted_end_after", "start_error_after", "end_error_after", "iou_after", "root_cause_status"]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for case in cases:
            b = case["observations"]["baseline_v1"]["case_record"]
            a = case["observations"]["improved_v1"]["case_record"]
            writer.writerow(dict(zip(fields, [case["id"], case["test"], a["matching_status"], a.get("gt_start_frame"), a.get("gt_end_frame"), b.get("pred_start_frame", b.get("start_frame")), b.get("pred_end_frame", b.get("end_frame")), a.get("pred_start_frame", a.get("start_frame")), a.get("pred_end_frame", a.get("end_frame")), a.get("start_frame_error"), a.get("end_frame_error"), a.get("interval_iou"), case["root_cause_status"]])))
    sheets = []
    for test in (1, 2):
        group = [x for x in sheet_entries if x[0] == test]
        for offset in range(0, len(group), 4):
            chunk = group[offset:offset + 4]
            canvas = Image.new("RGB", (1280, len(chunk) * 400), "white")
            draw = ImageDraw.Draw(canvas)
            for row, (_, cid, record, images) in enumerate(chunk):
                for col, evidence in enumerate(images):
                    im = Image.open(evidence["path"]).convert("RGB")
                    im.thumbnail((640, 360))
                    canvas.paste(im, (col * 640, row * 400 + 40))
                    draw.text((col * 640 + 5, row * 400 + 5), f"Test{test} {cid} {record['matching_status']} source frame {evidence['decoded_frame']}", fill="black")
                    draw.text((col * 640 + 5, row * 400 + 20), f"start/end error {record.get('start_frame_error')}/{record.get('end_frame_error')}f; diagnostic only", fill="black")
            path = OUT / "visual_review" / f"test{test:02d}_cases_{offset + 1:02d}_{offset + len(chunk):02d}.jpg"
            canvas.save(path, quality=85)
            sheets.append({"path": str(path), "sha256": sha(path),
                           "cases": [f"test{test:02d}:{x[1]}" for x in chunk],
                           "images": [ev for x in chunk for ev in x[3]],
                           "purpose": "boundary source thumbnails, agent diagnostic review; not human GT"})
    save("visual_review/contact_sheet_manifest.json", sheets)
    # Rehash every consumed immutable evidence file after all work.
    for path, evidence in INPUTS.items():
        assert sha(path) == evidence["sha256"], path
    save("input_provenance.json", {"schema": "test01-test02-failure-review-inputs:v1", "files": INPUTS,
                                  "builder_sha256": sha(__file__), "test3_access": False,
                                  "counts": {"annotation_files": len(annotations), "references": len(ref_metrics),
                                             "reference_rows": len(comparisons), "unique_packaged_cases": len(cases),
                                             "case_arm_observations": 2 * len(cases), "contact_sheets": len(sheets)},
                                  "all_input_bytes_unchanged": True})
    print(json.dumps({"rows": len(comparisons), "cases": len(cases), "sheets": len(sheets), "inputs": len(INPUTS)}))


if __name__ == "__main__":
    make_database()
