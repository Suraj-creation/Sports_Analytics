"""Technical/resource audit of strictly completed or explicitly recovered inference.

No ground-truth CSV is accepted or loaded. Original failed parent receipts stay
failed; this tool writes a separate, source-bound analysis after recovery proof.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

import msgpack

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.pipeline_repair_performance import summarize_stage_samples  # noqa: E402
from research.test2_resource_report import worker_gpu_memory  # noqa: E402
from scripts.benchmarking.evaluate_rallies import interval_iou, match_rallies, read_csv  # noqa: E402


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path: Path):
    return json.loads(path.read_text())


def dump(path: Path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def canonical(value):
    # Stable comparison only; no non-finite coordinates are exported/invented.
    return json.dumps(value, sort_keys=True, allow_nan=True, separators=(",", ":"))


def select_live_events(events: list[dict], session_id: str) -> list[dict]:
    ids = [e["event_id"] for e in events]
    if len(ids) != len(set(ids)) or any(e["session_id"] != session_id for e in events):
        raise ValueError("duplicate or foreign-session event ledger")
    superseded = {e["supersedes"] for e in events if e.get("supersedes")}
    return [e for e in events if e["event_id"] not in superseded and e["status"] != "retracted"]


def event_summary(events: list[dict], session_id: str) -> dict:
    live = select_live_events(events, session_id)
    categories = defaultdict(Counter)
    details = defaultdict(list)
    for event in live:
        kind, payload = event["type"], event.get("payload", {})
        categories["event_status"][str(event.get("status"))] += 1
        if kind in {"contact", "stroke"}:
            categories[f"{kind}_actor"]["named" if event.get("actors", {}).get("player_id") else "unknown"] += 1
            for key in (
                "physical_event_status",
                "contact_status",
                "classification_status",
                "stroke",
                "attribution_reason",
                "classification_abstention_reason",
            ):
                if key in payload:
                    categories[f"{kind}_{key}"][str(payload[key])] += 1
            for component in ("trajectory", "impact", "attribution"):
                evidence = (payload.get("physical_evidence") or {}).get(component) or {}
                if evidence:
                    categories[f"{kind}_{component}_reliability"][str(evidence.get("reliability"))] += 1
                    categories[f"{kind}_{component}_reasons"].update(evidence.get("reasons", []))
        if kind == "rally_end":
            for key in (
                "end_reason",
                "phase",
                "official",
                "match_format_known",
                "match_format",
                "winner",
                "score_transition_status",
            ):
                categories[f"rally_{key}"][str(payload.get(key))] += 1
            admission = payload.get("rally_admission") or {}
            categories["rally_admission_reason"][str(admission.get("reason"))] += 1
            details["rallies"].append(
                {
                    "event_id": event["event_id"],
                    "start": event["frame_start"],
                    "end": event["frame_end"],
                    "official": payload.get("official"),
                    "winner": payload.get("winner"),
                    "admission": admission,
                }
            )
        if kind in {"format_decision", "identity_ambiguity", "point"}:
            details[kind].append({"event_id": event["event_id"], "frame": event["frame_start"], "payload": payload})
    return {
        "append_only_counts": dict(Counter(e["type"] for e in events)),
        "live_counts": dict(Counter(e["type"] for e in live)),
        "categories": dict(categories),
        "details": dict(details),
        "physical_accuracy_validated": False,
    }


def audit_frames(frames: list[dict], expected_frames: int) -> tuple[dict, list[list]]:
    if [f["f"] for f in frames] != list(range(expected_frames)):
        raise ValueError("fresh cache frames must cover each canonical source frame exactly once")
    counts, categories = Counter(), defaultdict(Counter)
    scenes = []
    rows, previous_epoch = [], None
    for frame in frames:
        f, people = frame["f"], frame.get("p", [])
        raw, decision = frame.get("cc"), frame.get("cd")
        hypothesis = bool(raw and raw.get("hypothesis"))
        epoch = frame.get("ce", 0)
        barrier = previous_epoch is not None and epoch > previous_epoch
        epoch_reset = previous_epoch is not None and epoch < previous_epoch
        previous_epoch = epoch
        counts.update(
            {
                "frames": 1,
                "raw_shuttle_present": frame.get("s") is not None,
                "detector_executed_frames": frame.get("do") is True,
                "person_rows": len(people),
                "scene_telemetry_present": raw is not None,
                "scene_raw_hypotheses": hypothesis,
                "actual_content_epoch_increments": barrier,
                "content_epoch_decreases": epoch_reset,
                "detailed_diagnostic_frames": frame.get("dg") is not None,
            }
        )
        for key, value in (
            ("view", frame.get("v")),
            ("calibration_state", frame.get("cs")),
            ("player_population", len(people)),
            ("association_status", (frame.get("sa") or {}).get("status")),
        ):
            categories[key][str(value)] += 1
        categories["association_reason"].update((frame.get("sa") or {}).get("reasons", []))
        if raw is not None:
            categories["scene_raw_status"][str(raw.get("status"))] += 1
        if decision is not None:
            counts["scene_decision_records"] += 1
            categories["scene_decision"][decision["decision"]] += 1
            categories["scene_decision_reason"][decision["reason"]] += 1
            counts["scene_positive_correspondence_vetoes"] += decision["decision"] == "no_barrier"
            counts["scene_current_detector_probes"] += decision.get("detector_frame") is not None
            if decision["decision"] == "no_barrier" and barrier:
                raise ValueError("no_barrier decision contradicted by actual content epoch")
            if decision["decision"] in {"barrier", "unknown"} and hypothesis and not barrier:
                raise ValueError("selected scene reset/fallback missing its actual content epoch")
        if barrier and not hypothesis:
            raise ValueError("content epoch reset lacks raw source hypothesis")
        if hypothesis or decision is not None or barrier or epoch_reset:
            scenes.append(
                {
                    "frame": f,
                    "raw_hypothesis": hypothesis,
                    "actual_barrier": barrier,
                    "epoch": epoch,
                    "raw": raw,
                    "decision": decision,
                }
            )
        pose_current, racket_current = 0, 0
        for person in people:
            matched = person.get("dm")
            categories["person_detector_match"][str(matched)] += 1
            categories["person_identity_method"][str(person.get("im"))] += 1
            counts["person_current_detector_matches"] += matched is True
            counts["person_propagated_or_unmatched"] += matched is False
            for name, payload, stamp in (("pose", "k", "pf"), ("racket", "rk", "rf")):
                source = person.get(stamp)
                if source is not None and (type(source) is not int or source > f or source < 0):
                    raise ValueError("future or malformed component source timestamp")
                present = person.get(payload) is not None
                current = present and source == f
                counts[f"{name}_present_rows"] += present
                counts[f"{name}_current_source_rows"] += current
                counts[f"{name}_present_without_current_source"] += present and not current
                counts[f"{name}_current_on_propagated_box"] += current and matched is False
                if name == "pose":
                    pose_current += current
                else:
                    racket_current += current
        rows.append(
            [
                f,
                frame.get("v"),
                frame.get("cs"),
                len(people),
                frame.get("do"),
                pose_current,
                racket_current,
                hypothesis,
                barrier,
                decision["decision"] if decision else None,
                epoch,
            ]
        )
    return {
        "counts": dict(counts),
        "categories": dict(categories),
        "scene_records": scenes,
        "limits": [
            "Counts are technical coverage, not reviewed component accuracy.",
            "Raw shuttle is pre-association decoder output that already passed court masking.",
            "Current pose execution and current box/person association are separate.",
            "Content epochs measure actual tracking action; raw hypotheses remain separate.",
        ],
    }, rows


def ocr_summary(chunks: list[dict]) -> dict:
    labels, contexts = Counter(), Counter()
    readouts = []
    for chunk in chunks:
        for row in chunk.get("ocr", []):
            labels.update(str(item[0]) for item in row.get("r", []))
            contexts[canonical(row.get("ctx"))] += 1
            readouts.append(row)
    known_logo = {key: count for key, count in labels.items() if key.strip().upper() in {"SXFI", "LIVE"}}
    return {
        "readout_count": len(readouts),
        "label_counts": dict(labels),
        "context_counts": dict(contexts),
        "previously_source_reviewed_branding_strings": known_logo,
        "readouts": readouts,
        "accuracy_validated": False,
        "limit": (
            "Observed labels are not verified athlete identities/scores. "
            "Known branding-string absence does not certify OCR accuracy."
        ),
    }


def resource_summary(
    parent: dict, samples: list[dict], stages: dict, frames: int, worker_info: dict | None = None
) -> dict:
    elapsed = parent.get("elapsed_s")
    if type(elapsed) not in (int, float) or not math.isfinite(elapsed) or elapsed <= 0:
        raise ValueError("original parent elapsed scope is unavailable")
    parsed, gpu, rss, cpu, ram = [], [], [], [], []
    for row in samples:
        if "elapsed_s" not in row:
            continue
        memory = worker_gpu_memory(row.get("rows", ""), parent["allocated_gpu_uuid"], parent["worker_pid"])
        if memory is not None:
            gpu.append(memory)
        if row.get("worker_tree_rss_bytes") is not None:
            rss.append(row["worker_tree_rss_bytes"])
        if row.get("worker_tree_cpu_seconds") is not None:
            cpu.append(row["worker_tree_cpu_seconds"])
        if row.get("system_available_ram_bytes") is not None:
            ram.append(row["system_available_ram_bytes"])
        parsed.append(
            {
                "elapsed_s": row["elapsed_s"],
                "worker_gpu_mib": memory,
                "worker_tree_rss_bytes": row.get("worker_tree_rss_bytes"),
                "worker_tree_cpu_seconds": row.get("worker_tree_cpu_seconds"),
            }
        )
    result = {
        "original_parent_status": parent.get("status"),
        "worker_exit_code": parent.get("worker_exit_code"),
        "physical_gpu_index": parent.get("physical_gpu_index"),
        "allocated_gpu_uuid": parent["allocated_gpu_uuid"],
        "worker_pid": parent["worker_pid"],
        "parent_failure_inclusive_elapsed_s": elapsed,
        "parent_failure_inclusive_source_fps": frames / elapsed,
        "neural_only_throughput_fps": None,
        "model_loading_time_s": None,
        "media_ready_time_s": None,
        "model_staging_time_s": None,
        "worker_final_cpu_s": None,
        "worker_maxrss_bytes": None,
        "sampled_worker_tree_peak_rss_bytes": max(rss, default=None),
        "sampled_worker_gpu_peak_mib": max(gpu, default=None),
        "sampled_cpu_seconds_max_observed": max(cpu, default=None),
        "sampled_cpu_seconds_last_observed": cpu[-1] if cpu else None,
        "sampled_system_available_ram_min_bytes": min(ram, default=None),
        "sample_count": len(samples),
        "resource_rows": len(parsed),
        "sampling_error_count": sum("sampling_error" in row or "resource_sampling_error" in row for row in samples),
        "stage_latency": summarize_stage_samples(stages),
        "resource_series": parsed,
        "limits": [
            "Parent elapsed includes initialization, media preparation, neural processing, "
            "postprocessing and the final reporting failure.",
            "Original final inference.json was not written; lost initialization/worker-final timings stay unavailable.",
            "Stage invocations are wall scopes, may overlap and must not be summed to infer neural runtime.",
            "GPU peaks use the allocated GPU UUID and worker PID only; sampling can miss short peaks.",
            "Tree RSS may double-count shared pages; CPU snapshots omit exited children "
            "and are not final worker CPU usage.",
            "Other workers may share host CPU/RAM/storage; establish actual overlap from parent start/end times "
            "and PID receipts before comparing performance.",
        ],
    }
    result["parent_completed_elapsed_s"] = None
    result["parent_completed_source_fps"] = None
    result["worker_elapsed_s"] = None
    result["worker_source_fps"] = None
    result["component_initialization_including_models_s"] = None
    result["visible_torch_devices"] = None
    if worker_info is not None:
        if (
            worker_info.get("status") != "completed"
            or parent.get("status") != "completed"
            or parent.get("worker_exit_code") != 0
            or worker_info.get("cached_perception_used") is not False
        ):
            raise ValueError("normal resource scopes require completed fresh worker and parent")
        worker_elapsed = worker_info.get("elapsed_s")
        if type(worker_elapsed) not in (int, float) or not math.isfinite(worker_elapsed) or worker_elapsed <= 0:
            raise ValueError("completed worker elapsed must be finite positive seconds")
        result.update(
            parent_failure_inclusive_elapsed_s=None,
            parent_failure_inclusive_source_fps=None,
            parent_completed_elapsed_s=elapsed,
            parent_completed_source_fps=frames / elapsed,
            worker_elapsed_s=worker_elapsed,
            worker_source_fps=frames / worker_elapsed,
            media_ready_time_s=worker_info.get("media_ready_s"),
            model_staging_time_s=worker_info.get("model_staging_s"),
            component_initialization_including_models_s=worker_info.get("runner_stage_seconds", {}).get(
                "component_initialization_including_models_s"
            ),
            worker_final_cpu_s=worker_info.get("worker_cpu_s"),
            worker_maxrss_bytes=worker_info["worker_maxrss_kib"] * 1024
            if worker_info.get("worker_maxrss_kib") is not None
            else None,
            runner_stage_seconds=worker_info.get("runner_stage_seconds", {}),
            visible_torch_devices=worker_info.get("visible_torch_devices"),
        )
        result["limits"] = [
            "Normal completed worker/parent timing scopes remain separate; "
            "they include initialization/media/postprocessing.",
            "Component initialization includes model construction and is not isolated model-loading latency.",
            "Pure neural-only throughput remains unavailable; saved stage wall scopes can overlap.",
            *result["limits"][3:],
        ]
    return result


def prediction_changes(baseline, current) -> dict:
    matches = match_rallies(baseline, current, 0.5)
    paired = []
    for a, b in matches:
        old, new = baseline[a], current[b]
        paired.append(
            {
                "baseline_index": a + 1,
                "current_index": b + 1,
                "iou": interval_iou(old, new),
                "baseline": [old.start_frame, old.end_frame],
                "current": [new.start_frame, new.end_frame],
                "start_shift_frames": new.start_frame - old.start_frame,
                "end_shift_frames": new.end_frame - old.end_frame,
                "duration_shift_frames": new.end_frame - new.start_frame - (old.end_frame - old.start_frame),
            }
        )
    old_used, new_used = {a for a, _ in matches}, {b for _, b in matches}
    graph = [
        (a + 1, b + 1)
        for a, old in enumerate(baseline)
        for b, new in enumerate(current)
        if min(old.end, new.end) > max(old.start, new.start)
    ]
    return {
        "scope": "Prediction-to-prediction changes only; baseline is not ground truth; no detection accuracy metric.",
        "matching": "existing maximum-cardinality then total IoU at0.5",
        "paired": paired,
        "baseline_count": len(baseline),
        "current_count": len(current),
        "unpaired_baseline_indices": [i + 1 for i in range(len(baseline)) if i not in old_used],
        "unpaired_current_indices": [i + 1 for i in range(len(current)) if i not in new_used],
        "overlap_graph": graph,
        "baseline_overlapping_multiple_current": [a for a, count in Counter(a for a, _ in graph).items() if count > 1],
        "current_overlapping_multiple_baseline": [b for b, count in Counter(b for _, b in graph).items() if count > 1],
    }


def compare_frame_fields(baseline: list[dict], current: list[dict]) -> dict:
    if [r["f"] for r in baseline] != [r["f"] for r in current]:
        raise ValueError("perception comparison requires exactly the same canonical frame population")
    fields = ("s", "c", "sa", "p", "g", "l", "v", "h", "q", "cs", "do", "ps", "ce", "cc", "cd")
    result = {}
    for field in fields:
        changed, absent_old, absent_new = [], 0, 0
        for old, new in zip(baseline, current, strict=True):
            absent_old += field not in old
            absent_new += field not in new
            if field in old and field in new and canonical(old[field]) != canonical(new[field]):
                changed.append(old["f"])
        result[field] = {
            "baseline_field_absent_frames": absent_old,
            "current_field_absent_frames": absent_new,
            "different_when_both_present": len(changed),
            "first_different_frames": changed[:30],
        }
    return {
        "scope": (
            "Exact stored field comparison, without physical-identity normalization or accuracy labels. "
            "Legacy absent fields remain unknown."
        ),
        "frames": len(current),
        "fields": result,
    }


def load_chunks(directory: Path, expected: dict[str, str] | None, consumed: dict) -> tuple[list[dict], list[dict]]:
    chunks, frames = [], []
    paths = sorted(directory.glob("*.msgpack"))
    if not paths or (expected is not None and {p.name for p in paths} != set(expected)):
        raise ValueError("perception cache population differs from bound catalogue")
    for path in paths:
        digest = sha(path)
        if expected is not None and digest != expected[path.name]:
            raise ValueError("perception cache hash changed")
        consumed[str(path)] = digest
        chunk = msgpack.unpackb(path.read_bytes(), raw=False)
        chunks.append(chunk)
        frames.extend(chunk["frames"])
    return chunks, frames


def track_summary(run: Path, session_id: str, frames: list[dict], consumed: dict) -> dict:
    import pyarrow.parquet as pq

    counts = Counter()
    invalid = {row["f"] for row in frames if row.get("cs") != "VALID" or row.get("v") != "main" or row.get("l")}
    categories = defaultdict(Counter)
    violations = []
    for path in sorted((run / "data/sessions" / session_id / "tracks").glob("*/*.parquet")):
        consumed[str(path)] = sha(path)
        kind = path.parent.name
        for row in pq.read_table(path).to_pylist():
            counts[f"{kind}_rows"] += 1
            if kind != "player":
                continue
            frame = row["frame_idx"]
            if not 0 <= frame < len(frames):
                raise ValueError("foreign source frame in player export")
            if frame in invalid:
                violations.append({"frame": frame, "track_id": row.get("track_id")})
            categories["player_id"][str(row.get("player_id"))] += 1
            categories["detector_matched"][str(row.get("detector_matched"))] += 1
            present = row.get("court_x") is not None and row.get("court_y") is not None
            projected = present and all(math.isfinite(row[key]) for key in ("court_x", "court_y"))
            counts["nonfinite_projected_court_rows"] += present and not projected
            counts["player_projected_court_rows"] += projected
            counts["projected_court_on_propagated_box"] += projected and row.get("detector_matched") is False
    return {
        "counts": dict(counts),
        "categories": dict(categories),
        "invalid_geometry_frame_count": len(invalid),
        "player_rows_on_invalid_geometry": violations,
        "limit": (
            "Anonymous projected positions and detector flags are evidence coverage, "
            "not physical identity or metric accuracy."
        ),
    }


def load_baseline(run: Path, source_sha: str, media: dict, consumed: dict):
    info_path = run / "inference.json"
    info = read(info_path)
    consumed[str(info_path)] = sha(info_path)
    metadata_path = run / "benchmark_metadata.json"
    metadata = read(metadata_path) if metadata_path.exists() else {}
    if metadata_path.exists():
        consumed[str(metadata_path)] = sha(metadata_path)
    identity = info.get("source_sha256", metadata.get("source_video_sha256"))
    if identity != source_sha or info.get("status") not in {"analysed", "completed"} or info["media"] != media:
        raise ValueError("baseline source/media completion does not correspond to this recording")
    events_path, predictions_path = run / "events.jsonl", run / "predicted_rallies.csv"
    events = [json.loads(line) for line in events_path.open()]
    sessions = {event["session_id"] for event in events}
    if len(sessions) != 1:
        raise ValueError("baseline event session is ambiguous")
    sid = next(iter(sessions))
    live = select_live_events(events, sid)
    rate = media["fps_num"] / media["fps_den"]
    predictions = read_csv(predictions_path, rate)
    actual = sorted((e["frame_start"], e["frame_end"]) for e in live if e["type"] == "rally_end")
    if [(r.start_frame, r.end_frame) for r in predictions] != actual:
        raise ValueError("baseline CSV differs from its actual live rally ledger")
    if metadata.get("prediction_sha256") not in (None, sha(predictions_path)):
        raise ValueError("frozen baseline prediction hash changed")
    for path in (events_path, predictions_path):
        consumed[str(path)] = sha(path)
    choices = [run / prefix / "sessions" / sid / "perception" for prefix in ("data", "runtime")]
    directory = next((p for p in choices if p.exists()), None)
    if directory is None:
        raise ValueError("baseline perception cache unavailable")
    _, frames = load_chunks(directory, None, consumed)
    if [row["f"] for row in frames] != list(range(media["n_frames"])):
        raise ValueError("baseline perception is incomplete")
    return predictions, frames


def load_analysis_input(run: Path, completion: Path | None) -> dict:
    """Choose explicit recovery or strict normal full-upload completion only."""
    if completion is not None:
        from research.pipeline_repair_completion import verify_completion_receipt

        bound = verify_completion_receipt(run, completion)
        return {**bound, "completion_mode": "independent_recovery", "worker_info": None}
    from research.production_external_semantic_replay import load_finished_input

    session = read(run / "session.json")
    finished = load_finished_input(run, session["session_id"])
    info, parent = read(finished.report_path), read(run.with_suffix(".executor.json"))
    if (
        finished.layout != "production-full-upload"
        or finished.cache_catalogue_receipt is None
        or info.get("status") != "completed"
        or info.get("cached_perception_used") is not False
        or parent.get("status") != "completed"
        or parent.get("worker_exit_code") != 0
        or parent.get("frozen_source_inputs_unchanged") is not True
        or info.get("frames_processed") != finished.media["n_frames"]
        or info.get("frontier_frame") != finished.media["n_frames"] - 1
    ):
        raise ValueError("normal analysis requires completed fresh source-guarded upload with original cache catalogue")
    source = Path(session["source"]["uri"])
    proxy = run / "data/media" / info["source_sha256"] / "proxy.mp4"
    return {
        "completion_mode": "normal_completed_worker",
        "worker_info": info,
        "session_id": session["session_id"],
        "media": finished.media,
        "profile": finished.profile,
        "session_path": finished.session_path,
        "events_path": finished.events_path,
        "receipt_path": finished.report_path,
        "plan_path": finished.manifest_path,
        "cache_dir": finished.cache_directory,
        "cache_sha256": finished.expected_caches,
        "input_paths": (*finished.input_paths, source, proxy),
        "source_sha256": info["source_sha256"],
        "proxy_sha256": info["proxy_sha256"],
        "prediction_sha256": sha(run / "predicted_rallies.csv"),
        "original_parent_status": parent["status"],
        "degraded": info.get("degraded", []),
    }


def analyse(run: Path, completion: Path | None, output: Path, baseline_run: Path | None = None) -> dict:
    # Both gates validate actual original completion evidence. No inference.json
    # is fabricated and original failed executor receipts are never rewritten.
    bound = load_analysis_input(run, completion)
    consumed = {str(path): sha(path) for path in bound["input_paths"]}
    consumed[str(Path(__file__).resolve())] = sha(Path(__file__).resolve())
    session_path, events_path = Path(bound["session_path"]), Path(bound["events_path"])
    session = read(session_path)
    media, sid = bound["media"], bound["session_id"]
    n = media["n_frames"]
    if (
        session["session_id"] != sid
        or session.get("status") != "analysed"
        or session.get("analysed_frames") != n
        or session.get("frontier_frame") != n - 1
    ):
        raise ValueError("actual session differs from strict recovered completion")
    chunks, frames = load_chunks(Path(bound["cache_dir"]), bound["cache_sha256"], consumed)
    frame_report, csv_rows = audit_frames(frames, n)
    events = [json.loads(line) for line in events_path.open()]
    event_report = event_summary(events, sid)
    current_predictions = read_csv(run / "predicted_rallies.csv", media["fps_num"] / media["fps_den"])
    if [(r.start_frame, r.end_frame) for r in current_predictions] != sorted(
        (r["start"], r["end"]) for r in event_report["details"].get("rallies", [])
    ):
        raise ValueError("actual prediction CSV differs from its live source rally ledger")
    ocr = ocr_summary(chunks)
    tracks = track_summary(run, sid, frames, consumed)
    stage_path = run / "stage_latency_samples.json"
    parent_path = run.with_suffix(".executor.json")
    samples_path = run.with_suffix(".gpu_process_samples.jsonl")
    predictions_path = run / "predicted_rallies.csv"
    for path in (session_path, events_path, stage_path, parent_path, samples_path, predictions_path):
        consumed[str(path)] = sha(path)
    parent = read(parent_path)
    if parent.get("status") != bound["original_parent_status"]:
        raise ValueError("original parent receipt changed after recovery")
    samples = [json.loads(line) for line in samples_path.open()]
    resources = resource_summary(parent, samples, read(stage_path), n, bound["worker_info"])
    model_sets, runtime_sets = {}, {}
    for chunk in chunks:
        for target, value in ((model_sets, chunk["models"]), (runtime_sets, chunk["ci"].get("runtimes", {}))):
            key = canonical(value)
            if key not in target:
                target[key] = {
                    "value": value,
                    "frames": 0,
                    "canonical_sha256": hashlib.sha256(key.encode()).hexdigest(),
                }
            target[key]["frames"] += len(chunk["frames"])
    models_verified = None
    if bound["completion_mode"] == "normal_completed_worker":
        from research.pipeline_repair_completion import verify_models

        declarations = {
            "loaded_models": {key: row["value"] for key, row in model_sets.items()},
            "runtimes": {key: row["value"] for key, row in runtime_sets.items()},
        }
        models_verified = verify_models(run, declarations, bound["profile"])
        for group in models_verified.values():
            for model in group.values():
                for name in ("source_path", "staged_path", "path"):
                    if name in model:
                        consumed[model[name]] = sha(Path(model[name]))
        for path in (run / "models").rglob("*"):
            if path.is_file():
                consumed[str(path)] = sha(path)
    baseline = None
    if baseline_run is not None:
        old_predictions, old_frames = load_baseline(baseline_run, bound["source_sha256"], media, consumed)
        baseline = {
            "run": str(baseline_run),
            "prediction_changes": prediction_changes(old_predictions, current_predictions),
            "perception_field_changes": compare_frame_fields(old_frames, frames),
        }
    disk = Counter()
    for path in run.rglob("*"):
        if path.is_file() and not path.is_symlink():
            stat = path.stat()
            disk["regular_files"] += 1
            disk["logical_bytes"] += stat.st_size
            disk["allocated_bytes"] += stat.st_blocks * 512
            if path.is_relative_to(Path(bound["cache_dir"])):
                disk["perception_cache_bytes"] += stat.st_size
            if path.is_relative_to(run / "models"):
                disk["staged_model_bytes"] += stat.st_size
    if any(sha(Path(path)) != digest for path, digest in consumed.items()):
        raise ValueError("source evidence changed while analysing completed run")
    result = {
        "schema": "pipeline-repair-posthoc-run-analysis:v2",
        "status": "technical_analysis_after_strict_posthoc_completion_proof"
        if bound["completion_mode"] == "independent_recovery"
        else "technical_analysis_after_verified_normal_completion",
        "completion_mode": bound["completion_mode"],
        "original_parent_status": parent["status"],
        "run": str(run),
        "session_id": sid,
        "completion_receipt": str(bound["receipt_path"]),
        "completion_receipt_sha256": sha(Path(bound["receipt_path"])),
        "frames": n,
        "frontier_frame": session["frontier_frame"],
        "media": media,
        "source_sha256": bound["source_sha256"],
        "proxy_sha256": bound["proxy_sha256"],
        "prediction_sha256": bound["prediction_sha256"],
        "profile_canonical_sha256": hashlib.sha256(canonical(bound["profile"]).encode()).hexdigest(),
        "selected_components": bound["profile"].get("components", {}),
        "model_sets_from_actual_caches": list(model_sets.values()),
        "runtime_declarations_from_actual_caches": list(runtime_sets.values()),
        "component_coverage": frame_report,
        "events": event_report,
        "ocr": ocr,
        "track_exports": tracks,
        "resources": resources,
        "disk": dict(disk),
        "session_players": session.get("players"),
        "session_roster": session.get("roster"),
        "session_degraded": bound.get(
            "degraded", bound.get("completion_receipt", {}).get("original_session_degraded", [])
        ),
        "models_verified_during_analysis": models_verified,
        "baseline_comparison": baseline,
        "consumed_files_sha256": consumed,
        "inputs_unchanged_after_analysis": True,
        "ground_truth_loaded": False,
        "accuracy_validated": False,
        "limits": [
            "This is posthoc analysis; no neural inference, replay or prediction edits are performed.",
            "Explicit recovery does not change an original failed receipt; "
            "normal runs require original worker/parent success.",
            "Only saved measurements are used; unavailable fields stay null and model-only timing is not invented.",
            "Prediction-to-prediction matching and exact cache changes are not sporting accuracy.",
            "Node placement, API/frontend behavior, highlight accuracy and summaries need separate validation.",
            "A prepared canonical clip source is the actual input; "
            "older long-match/VFR derivation mapping is not inferred.",
        ],
    }
    output.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(Path(__file__), output / "executed_analysis_source.py")
    with (output / "frame_component_coverage.csv").open("x", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "frame",
                "view",
                "calibration",
                "player_count",
                "detector_executed",
                "current_pose_count",
                "current_racket_count",
                "raw_scene_hypothesis",
                "actual_content_barrier",
                "scene_decision",
                "content_epoch",
            ]
        )
        writer.writerows(csv_rows)
    dump(output / "technical_analysis.json", result)
    if baseline is not None:
        dump(output / "prediction_changes.json", baseline["prediction_changes"])
        dump(output / "perception_field_changes.json", baseline["perception_field_changes"])
    dump(
        output / "analysis_manifest.json",
        {
            "schema": "pipeline-repair-run-analysis-publication:v1",
            "run": str(run),
            "completion_receipt_sha256": result["completion_receipt_sha256"],
            "script_sha256": sha(Path(__file__)),
            "output_artifact_sha256": {path.name: sha(path) for path in sorted(output.iterdir()) if path.is_file()},
            "ground_truth_loaded": False,
            "original_artifacts_modified": False,
        },
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument(
        "--completion",
        type=Path,
        help="Recovery directory for a preserved reporting failure; omit only for normal completed workers.",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--baseline-run", type=Path)
    args = parser.parse_args()
    result = analyse(
        args.run.resolve(),
        args.completion.resolve() if args.completion else None,
        args.output.resolve(),
        args.baseline_run.resolve() if args.baseline_run else None,
    )
    print(json.dumps({"status": result["status"], "frames": result["frames"]}))


if __name__ == "__main__":
    main()
