"""Offline exposed-reference agreement for finished fresh runs; never inference.

The only reference rebinding is SID/source SHA/proxy SHA. Original labels and
fixed source translations are immutable. Published anchors are not independently
reviewed physical impacts. No sealed labels, offset fitting or outcome scoring.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DISCOVERY = (
    ROOT
    / "artifacts/benchmarking/experiments/prod_20261105_data_provenance_discovery_v1"
    / "additional_available_materials.json"
)
HELPER = ROOT / "data/research/pluggable-pipeline-20261103/bai-compare-quality-benchmarks.py"
HELPER_SHA = "2cdc3422f77b7595419f94930eda9c7bb8b989c3920588d8dbab3f57d8494529"
NATIVE12 = (
    "block",
    "clear",
    "cross_net",
    "drive",
    "drop",
    "lift",
    "long_serve",
    "net_shot",
    "push",
    "rush",
    "short_serve",
    "smash",
)
COUNTS = {"india": [24, 18, 19, 24], "denmark": [9, 22, 1, 7], "doubles": [13, 7, 6, 19]}
OFFSETS = {"india": -12001, "denmark": -13503, "doubles": -12000}
TEST7_FIELDS = [
    "start_time",
    "end_time",
    "win_point_player",
    "win_reason",
    "ball_types",
    "lose_reason",
    "roundscore_A",
    "roundscore_B",
]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result

    return json.loads(
        Path(path).read_text(),
        object_pairs_hook=pairs,
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonfinite JSON " + value)),
    )


def write_new(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def load_helper():
    require(digest(HELPER) == HELPER_SHA, "archived pure metric helper changed")
    spec = importlib.util.spec_from_file_location("frozen_external_reference_metrics", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def checked(entry, watches):
    path = (ROOT / entry["path"]).resolve(strict=True)
    require(digest(path) == entry["sha256"], "input digest mismatch: " + str(path))
    watches[str(path)] = entry["sha256"]
    return path


def derive_binding(document, sid, source_sha, proxy_sha):
    """Deep copy, preserving EVERY other field including shots and provenance."""
    require(sid != document["session_id"], "new isolated session ID required")
    result = copy.deepcopy(document)
    result.update(session_id=sid, media_sha256=source_sha, proxy_sha256=proxy_sha)
    require(
        {k: v for k, v in result.items() if k not in {"session_id", "media_sha256", "proxy_sha256"}}
        == {k: v for k, v in document.items() if k not in {"session_id", "media_sha256", "proxy_sha256"}},
        "reference rebinding changed annotation data",
    )
    return result


def composite_labels(documents, recording):
    require(recording in COUNTS and len(documents) == 4, "four declared partitions required")
    require([len(d["shots"]) for d in documents] == COUNTS[recording], "frozen annotation denominators changed")
    first = documents[0]
    same = (
        "session_id",
        "media_sha256",
        "proxy_sha256",
        "fps_num",
        "fps_den",
        "media_n_frames",
        "width",
        "height",
        "match_format",
        "split",
    )
    rate = Fraction(first["fps_num"], first["fps_den"])
    require(rate > 0, "invalid FPS")
    cursor, shots, ids = 0, [], set()
    for document in documents:
        require(all(document.get(k) == first[k] for k in same), "mixed media bindings")
        require(document["reference_provenance"] == first["reference_provenance"], "mixed external provenance")
        require(
            document["exhaustive"] is True and document["population"]["exhaustive_published_contacts"] is True,
            "exhaustive published scope required",
        )
        require(
            document["status"] == "draft" and document["review"]["human_verified"] is False,
            "draft review status must remain false",
        )
        mapping = document["reference_provenance"]["frame_mapping"]
        require(mapping["offset"] == OFFSETS[recording], "fixed alignment changed; fitting forbidden")
        lo, hi = document["window_frames"]
        require(lo == cursor and lo < hi <= first["media_n_frames"], "gapped or overlapping partitions")
        for shot in document["shots"]:
            frame = shot["frame_idx"]
            require(type(frame) is int and lo <= frame < hi, "anchor outside partition")
            require(shot["time_s"] == float(Fraction(frame, 1) / rate), "frame/time mismatch")
            require(shot["source_frame"] + OFFSETS[recording] == frame, "fixed source alignment mismatch")
            require(shot["annotation_id"] not in ids, "duplicate annotation ID")
            require(shot["family"] in (*NATIVE12, "unknown"), "unsupported reference family")
            ids.add(shot["annotation_id"])
            shots.append(copy.deepcopy(shot))
        cursor = hi
    require(cursor == first["media_n_frames"], "partitions do not cover full clip")
    shots.sort(key=lambda s: s["time_s"])
    require(len({s["frame_idx"] for s in shots}) == len(shots), "duplicate anchor frame")
    return {
        **copy.deepcopy(first),
        "window_frames": [0, cursor],
        "window_s": [0.0, float(Fraction(cursor, 1) / rate)],
        "shots": shots,
    }


def validate_finished(manifest, report, sid, expected):
    require(
        manifest.get("schema") == "fresh-real-video-run-v1"
        and report.get("schema") == "fresh-real-video-validation-v1",
        "unsupported harness export",
    )
    require(manifest.get("finished_utc") and report.get("finished_utc"), "unfinished run")
    require(manifest.get("exit_code") in (0, 2) and report.get("status") in ("complete", "partial"), "failed inference")
    require(
        any(
            item.get("session_id") == sid and item.get("status") == report["status"]
            for item in manifest.get("sessions", [])
        ),
        "manifest session incomplete",
    )
    require(report.get("session_id") == sid, "session mismatch")
    n = expected["media_n_frames"]
    require(
        report.get("frames_processed") == n
        and report.get("inference_window_frames") == [0, n]
        and report.get("prefix_truncated") is False,
        "full clip inference required",
    )
    require(
        report.get("cached_perception_used") is False and report.get("score_or_identity_reviews_seeded") is False,
        "fresh machine-only inference required",
    )
    media = report["media"]
    require(
        media.get("source_sha256") == expected["media_sha256"]
        and media.get("proxy_sha256") == expected["proxy_sha256"],
        "prepared upload source/proxy mismatch",
    )
    for key in ("n_frames", "fps_num", "fps_den", "width", "height"):
        require(
            media["canonical"][key] == expected["media_n_frames" if key == "n_frames" else key],
            "canonical grid mismatch",
        )


def validate_coverage(path, n_frames):
    frames = [json.loads(line)["frame"] for line in Path(path).read_text().splitlines() if line]
    require(
        all(type(frame) is int for frame in frames) and frames == list(range(n_frames)),
        "exported frame coverage is not exactly the full ordered clip",
    )


def extract_predictions(live, by_id, labels, root_event_id):
    """Archived extractor semantics: ALL live contacts, provisional included."""
    contacts = [e for e in live if e.type == "contact"]
    n, rate = labels["media_n_frames"], Fraction(labels["fps_num"], labels["fps_den"])
    require(all(0 <= e.frame_start < n for e in contacts), "contact outside full clip")
    roots = {root_event_id(e, by_id): e for e in contacts}
    require(len(roots) == len(contacts), "duplicate live contact revision")
    strokes = {}
    for event in live:
        if event.type != "stroke":
            continue
        contact = by_id.get(event.payload.get("contact_event_id"))
        require(contact is not None and contact.type == "contact", "orphan stroke")
        root = root_event_id(contact, by_id)
        require(root in roots and root not in strokes, "retracted/multiple stroke contact")
        require(event.frame_start == roots[root].frame_start, "contact/stroke frame mismatch")
        strokes[root] = event
    shots = []
    for root, event in roots.items():
        stroke = strokes.get(root)
        provisional = stroke is None or stroke.status.value == "provisional"
        family = "unknown" if provisional else stroke.payload.get("stroke", "unknown")
        require(family in (*NATIVE12, "unknown"), "unsupported predicted family; no forced mapping")
        # Fresh sessions contain no source-name binding. Scoring slots/track IDs
        # must not accidentally match published P1/P2 or A/B/C/D person labels.
        shots.append(
            {
                "event_id": event.event_id,
                "contact_root_id": root,
                "stroke_event_id": stroke.event_id if stroke else None,
                "frame_idx": event.frame_start,
                "time_s": float(Fraction(event.frame_start, 1) / rate),
                "family": family,
                "player_id": None,
                "raw_actor_id": event.actors.player_id,
                "contact_status": event.status.value,
                "physical_event_status": event.payload.get("physical_event_status", "unknown"),
                "named_actor_binding": "none supplied to inference or evaluation",
            }
        )
    shots.sort(key=lambda s: (s["time_s"], s["event_id"]))
    return {
        "schema_version": 1,
        "session_id": labels["session_id"],
        "media_sha256": labels["media_sha256"],
        "timebase": "canonical_media_seconds",
        "window_s": labels["window_s"],
        "shots": shots,
    }


def project_d9(machine, protocol):
    require(
        protocol.get("before_predictions") is True and protocol.get("strict_native12_retained") is True,
        "unfrozen D9 protocol",
    )
    mapping = protocol["platform_to_reference"]
    require(set(mapping) == set(NATIVE12) | {"unknown"}, "incomplete D9 projection")
    return {
        **machine,
        "shots": [{**s, "native12_family": s["family"], "family": mapping[s["family"]]} for s in machine["shots"]],
    }


def test7_intervals(path, rate, n_frames, expected_count=31):
    """Only the two coarse timestamp columns are consumed; no offset/rounding."""
    result = []
    with Path(path).open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        require(reader.fieldnames == TEST7_FIELDS, "expected primary eight-column reference")
        for row in reader:
            require(None not in row and all(v is not None for v in row.values()), "malformed CSV row")
            start, end = Fraction(row["start_time"]) * rate, Fraction(row["end_time"]) * rate
            require(start.denominator == end.denominator == 1, "nonintegral canonical frame; rounding forbidden")
            lo, hi = int(start), int(end)
            require(0 <= lo < hi <= n_frames, "coarse interval outside media")
            result.append((lo, hi))
    require(len(result) == expected_count, "all primary coarse rows required")
    return result


def run_shots(run_root, sid, recording, discovery, output):
    helper = load_helper()
    watches = {str(discovery): digest(discovery), str(HELPER): digest(HELPER), str(Path(__file__)): digest(__file__)}
    materials = read(discovery)
    entry = next(e for e in materials["additional_available_materials"] if e["recording"] == recording)
    # A finished report is established BEFORE any annotation values are read.
    manifest_path, report_path = run_root / "run.json", run_root / "results" / sid / "report.json"
    manifest, report = read(manifest_path), read(report_path)
    summary = entry["reference_summary"]
    expected = {
        **summary,
        "media_sha256": entry["proxy"]["sha256"],
        "proxy_sha256": entry["proxy"]["sha256"],
        "width": 1280,
        "height": 720,
    }
    validate_finished(manifest, report, sid, expected)
    for field in ("source_path", "proxy_path"):
        path = Path(report["media"][field]).resolve(strict=True)
        require(digest(path) == entry["proxy"]["sha256"], "actual upload/proxy bytes differ")
        watches[str(path)] = digest(path)
    live, by_id, exported = helper._events(run_root, sid, report)
    validate_coverage(exported["frame-coverage.jsonl"], expected["media_n_frames"])
    session = read(exported["session.json"])
    require(
        session["session_id"] == sid and session["source"]["sha256"] == expected["media_sha256"],
        "saved source binding mismatch",
    )
    require(session["roster"]["match_format"] == summary["match_format"], "saved format mismatch")
    require(
        session.get("frontier_frame") == expected["media_n_frames"] - 1
        and session.get("analysed_frames") == expected["media_n_frames"],
        "saved session full frontier/count mismatch",
    )
    for key in ("preparation", "label_binding", "raw_published_annotations"):
        checked(entry[key], watches)
    originals = [read(checked(e, watches)) for e in entry["derived_labels"]]
    documents = [derive_binding(d, sid, expected["media_sha256"], expected["proxy_sha256"]) for d in originals]
    labels = composite_labels(documents, recording)
    machine = extract_predictions(live, by_id, labels, helper._root_event_id)
    strict = [helper.timing_metrics(labels, machine, tolerance) for tolerance in (3, 6)]
    result = {
        "schema": "production-exposed-reference-agreement:v1",
        "recording": recording,
        "session_id": sid,
        "runtime_status": report["status"],
        "accuracy_claim_eligible": False,
        "scope": (
            "published anchor agreement on previously exposed footage; draft timeline binding; "
            "no physical-impact, blind or generalization accuracy claim"
        ),
        "prediction_population": {
            "all_live_contacts": len(machine["shots"]),
            "provisional_included": True,
            "GT_rally_filter": False,
            "contact_statuses": dict(Counter(s["contact_status"] for s in machine["shots"])),
            "physical_statuses": dict(Counter(s["physical_event_status"] for s in machine["shots"])),
            "raw_actor_ids": dict(Counter(str(s["raw_actor_id"]) for s in machine["shots"])),
            "named_actor_predictions": 0,
        },
        "metrics_native12_strict": strict,
        "reference_counts": dict(Counter(s["player_id"] for s in labels["shots"])),
        "original_source_and_crop": {
            k: entry[k] for k in ("original_source", "original_crop_binding", "annotation_to_proxy_frame_offset")
        },
        "original_source_hash_reverified_by_this_evaluator": False,
        "original_reference_files": entry["derived_labels"],
        "derived_binding_changed_fields_only": ["session_id", "media_sha256", "proxy_sha256"],
        "original_reference_provenance": originals[0]["reference_provenance"],
        "frozen_alignment_frames_before_crop": {"india": -1, "denmark": -3, "doubles": 0}[recording],
        "inference_provenance": {"manifest": manifest, "report": report},
    }
    projected = None
    if recording == "doubles":
        taxonomy_path = checked(entry["taxonomy_protocol"], watches)
        taxonomy = read(taxonomy_path)
        projected = project_d9(machine, taxonomy)
        result["taxonomy_protocol"] = taxonomy
        result["metrics_D9_projection"] = [helper.timing_metrics(labels, projected, tolerance) for tolerance in (3, 6)]
        require(
            [x["contact_detection"] for x in strict]
            == [x["contact_detection"] for x in result["metrics_D9_projection"]],
            "projection changed contact timing",
        )
    for path in (
        manifest_path,
        report_path,
        *exported.values(),
        ROOT / "research/shot_benchmark.py",
        ROOT / "sports/badminton/src/bai_badminton/events/stroke.py",
    ):
        watches[str(path)] = digest(path)
    require(not output.exists(), "output directory must be new")
    output.mkdir(parents=True)
    for old, document in zip(entry["derived_labels"], documents, strict=True):
        write_new(output / Path(old["path"]).name, document)
    write_new(output / "full_clip_reference.json", labels)
    write_new(output / "predictions_native12.json", machine)
    if projected is not None:
        write_new(output / "predictions_D9.json", projected)
    for path, expected_sha in watches.items():
        require(digest(path) == expected_sha, "input changed during evaluation")
    result["input_files_sha256"] = watches
    result["derived_files_sha256"] = {p.name: digest(p) for p in output.iterdir() if p.is_file()}
    write_new(output / "report.json", result)
    return result


def run_test7(run_root, discovery, output):
    """Production full-upload adapter, separate from the real-video clip harness."""
    from bai_engine.schema.events import Event, current_view
    from scripts.benchmarking.evaluate_rallies import evaluate, read_csv, write_predictions

    # The worker writes inference.json only after analysis/frontier/export success.
    inference_path = run_root / "inference.json"
    info = read(inference_path)
    require(
        info.get("status") == "completed"
        and info.get("frames_processed") == info["media"]["n_frames"]
        and info.get("frontier_frame") == info["media"]["n_frames"] - 1
        and info.get("cached_perception_used") is False,
        "unfinished full-upload run",
    )
    executor_path = run_root.with_suffix(".executor.json")
    executor = read(executor_path)
    require(
        executor.get("status") == "completed"
        and executor.get("worker_exit_code") == 0
        and executor.get("frozen_source_inputs_unchanged") is True,
        "unfinished/failed frozen worker",
    )
    materials = read(discovery)
    item = materials["test7"]
    require(info["source_sha256"] == item["source"]["sha256"], "Test7 source binding mismatch")
    source_video = next(s for s in item["source"]["probe"]["streams"] if s["codec_type"] == "video")
    require(info["media"]["n_frames"] == int(source_video["nb_frames"]), "Test7 full source frame count mismatch")
    rate = Fraction(info["media"]["fps_num"], info["media"]["fps_den"])
    require(
        rate == Fraction(source_video["avg_frame_rate"]),
        "source/proxy FPS differs",
    )
    watches = {
        str(p): digest(p)
        for p in (
            inference_path,
            executor_path,
            discovery,
            run_root / "events.jsonl",
            run_root / "session.json",
            run_root / "predicted_rallies.csv",
            Path(__file__),
        )
    }
    checked(item["source"], watches)
    proxy = run_root / "data/media" / info["source_sha256"] / "proxy.mp4"
    require(
        digest(proxy) == info["proxy_sha256"] == executor.get("output_proxy_sha256"),
        "actual canonical proxy bytes differ from finished worker",
    )
    watches[str(proxy)] = info["proxy_sha256"]
    reference = checked(item["primary_reference"], watches)
    n = info["media"]["n_frames"]
    session = read(run_root / "session.json")
    require(
        session["frontier_frame"] == n - 1
        and session.get("status") == "analysed"
        and session.get("media") == info["media"]
        and session["source"]["sha256"] == info["source_sha256"],
        "saved full-upload source/frontier mismatch",
    )
    all_events = [
        Event.model_validate_json(line) for line in (run_root / "events.jsonl").read_text().splitlines() if line
    ]
    require(
        len({e.event_id for e in all_events}) == len(all_events)
        and all(e.session_id == session["session_id"] for e in all_events),
        "event identity mismatch",
    )
    ends = sorted(
        (e for e in current_view(all_events) if e.type == "rally_end"), key=lambda e: (e.frame_start, e.frame_end)
    )
    predicted = read_csv(run_root / "predicted_rallies.csv", float(rate))
    require(
        [(r.start_frame, r.end_frame) for r in predicted] == [(e.frame_start, e.frame_end) for e in ends],
        "rally CSV differs from live event fold",
    )
    intervals = test7_intervals(reference, rate, n)
    require(not output.exists(), "output directory must be new")
    output.mkdir(parents=True)
    write_predictions(output / "coarse_primary_reference.csv", intervals, float(rate))
    truth = read_csv(output / "coarse_primary_reference.csv", float(rate))
    metrics, comparisons = evaluate(truth, predicted, float(rate), minimum_iou=0.5)
    result = {
        "schema": "production-Test7-coarse-agreement:v1",
        "accuracy_claim_eligible": False,
        "scope": (
            "all31 primary coarse hand-labelled spans; exact seconds×FPS; unchanged IoU.5 evaluator; "
            "no outcome labels consumed; previously exposed, disjointness unknown"
        ),
        "reference_rows": len(intervals),
        "metrics": metrics,
        "comparisons": comparisons,
        "inference": info,
        "input_files_sha256": watches,
        "evaluator_sha256": digest(ROOT / "scripts/benchmarking/evaluate_rallies.py"),
    }
    for path, expected_sha in watches.items():
        require(digest(path) == expected_sha, "input changed during evaluation")
    write_new(output / "report.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recording", required=True, choices=["india", "denmark", "doubles", "test7"])
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--session")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--discovery", type=Path, default=DISCOVERY)
    args = parser.parse_args()
    if args.recording == "test7":
        result = run_test7(
            args.run_root.resolve(strict=True), args.discovery.resolve(strict=True), args.output.resolve()
        )
    else:
        require(args.session, "--session required for fresh harness export")
        result = run_shots(
            args.run_root.resolve(strict=True),
            args.session,
            args.recording,
            args.discovery.resolve(strict=True),
            args.output.resolve(),
        )
    print(
        json.dumps(
            {
                "recording": args.recording,
                "output": str(args.output),
                "accuracy_claim_eligible": result["accuracy_claim_eligible"],
            }
        )
    )


if __name__ == "__main__":
    main()
