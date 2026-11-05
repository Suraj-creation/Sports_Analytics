"""Build bounded offline HTML replay from exact-PTS original frames and evidence.

Ground truth is optional visualization data only. No inference is run, and all
source images remain unobscured beneath independently toggleable canvas marks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

import av
import cv2
import msgpack
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bai_badminton.court import COURT_LINES  # noqa: E402
from research.next_temporal_diagnose import verify_trace_cache_identity  # noqa: E402

HTML = Path(__file__).with_name("next_temporal_replay_template.html").read_text()


def project(matrix, xy):
    point = np.asarray(matrix, dtype=float).reshape(3, 3) @ np.r_[xy, 1]
    return (point[:2] / point[2]).tolist()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--ranges", type=json.loads, required=True, help="JSON object mapping case names to [first,last] inclusive"
    )
    parser.add_argument("--stride", type=int, default=1)
    parser.add_argument("--max-frames", type=int, default=2000)
    parser.add_argument(
        "--component-probe", type=Path, help="Optional external component diagnostic directory; explicitly labeled"
    )
    parser.add_argument("--probe-variant", default="rolling")
    args = parser.parse_args()
    output = args.output.resolve()
    if args.stride < 1:
        raise ValueError("stride must be positive")
    cases = {name: list(range(start, end + 1, args.stride)) for name, (start, end) in args.ranges.items()}
    selected = sorted({frame for frames in cases.values() for frame in frames})
    if len(selected) > args.max_frames:
        raise ValueError("frame budget exceeded")
    output.mkdir(parents=True, exist_ok=False)
    (output / "frames").mkdir()
    metadata = json.loads((args.run / "benchmark_metadata.json").read_text())
    with args.source.open("rb") as stream:
        source_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    if source_hash != metadata["source_video_sha256"]:
        raise ValueError("requested original source differs from the selected run")
    component_probe = {}
    if args.component_probe is not None:
        probe_manifest = json.loads((args.component_probe / "manifest.json").read_text())
        if probe_manifest["source_sha256"] != source_hash:
            raise ValueError("component diagnostic belongs to a different original source")
        if args.probe_variant not in probe_manifest["configuration"]["variants"]:
            raise ValueError("requested component diagnostic variant is not recorded")
        for line in (args.component_probe / "candidates.jsonl").open():
            row = json.loads(line)
            if row["variant"] == args.probe_variant and row["frame_idx"] in selected:
                component_probe[row["frame_idx"]] = row
    observations = {}
    cache_paths = sorted(args.run.glob("runtime/sessions/*/perception/*.msgpack"))
    cache_hashes = verify_trace_cache_identity(metadata, args.trace, cache_paths)
    for path in cache_paths:
        record = msgpack.unpackb(path.read_bytes(), raw=False)
        observations.update({row["f"]: row for row in record["frames"] if row["f"] in selected})
    traces = [json.loads(line) for line in args.trace.open()]
    by_frame = {row["frame"]: row for row in traces if row["call"] == "step"}
    calls = {}
    for row in traces:
        if row["frame"] in selected and (
            row["call"] != "step" or row["before"]["state"] != row["after"]["state"] or any(row["update"].values())
        ):
            calls.setdefault(row["frame"], []).append({k: row[k] for k in ["call", "before", "after", "update"]})
    events = [json.loads(line) for line in (args.run / "events.jsonl").open()]
    superseded = {event["supersedes"] for event in events if event.get("supersedes")}
    live_contacts = [
        event
        for event in events
        if event["type"] == "contact" and event["event_id"] not in superseded and event["status"] != "retracted"
    ]
    all_contacts = [event for event in events if event["type"] == "contact"]
    calibration = next(event["payload"] for event in events if event["type"] == "calibration")
    inferred = json.loads((args.run / "inference.json").read_text())["rally_events"]
    finalized = sorted(
        (
            row["update"]["finalized"]["start"],
            row["update"]["finalized"]["end"],
            row["update"]["finalized"]["reason"],
        )
        for row in traces
        if row["update"]["finalized"]
    )
    assert finalized == sorted((x["start"], x["end"], x["end_reason"]) for x in inferred)
    import csv

    with (args.run / "rally_comparison.csv").open() as stream:
        gt = [
            {"id": int(row["gt_rally"]), "start": int(row["gt_start_frame"]), "end": int(row["gt_end_frame"])}
            for row in csv.DictReader(stream)
        ]
    data = {"fps": 30, "cases": cases, "frames": {}, "gt": gt, "predictions": inferred}
    container = av.open(str(args.source))
    stream = container.streams.video[0]
    assert stream.average_rate == Fraction(30, 1), (
        "This exact index equality diagnostic requires verified CFR30; no fitted mapping is allowed"
    )
    data["source_size"] = [stream.width, stream.height]
    data["source_time_base"] = str(stream.time_base)
    for name, indices in cases.items():
        wanted = set(indices)
        start, end = min(indices), max(indices)
        container.seek(int(Fraction(start, 30) / stream.time_base), stream=stream, backward=True)
        for frame in container.decode(stream):
            index = Fraction(frame.pts) * stream.time_base * 30
            assert index.denominator == 1
            f = int(index)
            if f > end:
                break
            if f not in wanted:
                continue
            assert Fraction(frame.pts) * stream.time_base == Fraction(f, 30)
            target = output / "frames" / f"{f}.jpg"
            if not target.exists():
                pixels = frame.to_ndarray(format="bgr24")
                pixels = cv2.resize(pixels, (960, 540), interpolation=cv2.INTER_AREA)
                assert cv2.imwrite(str(target), pixels, [cv2.IMWRITE_JPEG_QUALITY, 88])
            raw, semantic = observations[f], by_frame[f]
            diagnostic = raw.get("dg")
            shuttle_diagnostic = diagnostic.get("shuttle") if diagnostic else None
            player_diagnostic = diagnostic.get("players") if diagnostic else None
            external_probe = component_probe.get(f)
            candidate_diagnostic = shuttle_diagnostic or (external_probe.get("diagnostic") if external_probe else None)
            association = raw.get("sa")
            candidates = (
                association["candidates"]
                if association is not None
                else (candidate_diagnostic.get("candidates", []) if candidate_diagnostic else [])
            )
            xy = [semantic.get("x"), semantic.get("y")]
            matrix = raw.get("g") or np.eye(3).reshape(-1).tolist()
            court_lines = []
            # Per-frame G maps reference calibration into current image pixels.
            # Gate display to the same reference rather than inventing geometry
            # for another shot/invalid view.
            if raw.get("cs") == "VALID" and not raw.get("l"):
                mapped = np.asarray(matrix).reshape(3, 3) @ np.asarray(calibration["H"])
                court_lines = [[project(mapped, a), project(mapped, b)] for a, b in COURT_LINES]
            data["frames"][f] = {
                "source_frame": f,
                "proxy_frame": f,
                "timestamp_s": f / 30,
                "source_pts": frame.pts,
                "alignment": "exact source PTS=f/30; verified source/proxy index correspondence",
                "raw_xy": raw.get("s"),
                "raw_support": raw.get("c"),
                "confidence_semantics": "uncalibrated raw provider support",
                "processed_raw_xy": project(matrix, xy) if None not in xy else None,
                "kind": semantic.get("evidence", {}).get("kind", "unknown"),
                "shot": raw.get("sh"),
                "content_epoch": raw.get("ce", 0),
                "content_change": raw.get("cc"),
                "shuttle_association": association,
                "view": raw.get("v"),
                "calibration": raw.get("cs"),
                "players": [
                    {
                        "t": p["t"],
                        "b": p["b"],
                        "k": p.get("k"),
                        "detector_matched": p.get("dm"),
                        "detector_observed": raw.get("do"),
                        "identity_method": p.get("im"),
                    }
                    for p in raw.get("p", [])
                ],
                "court_lines": court_lines,
                "court_geometry_scope": "cached G applied to reference floor homography; not airborne shuttle geometry",
                "contacts": [
                    {
                        "frame": e["frame_start"],
                        "payload": e["payload"],
                        "evidence": e["evidence"],
                        "status": e["status"],
                    }
                    for e in live_contacts
                    if e["frame_start"] == f
                ],
                "contact_lifecycle": [
                    {"status": e["status"], "seq": e["seq"], "supersedes": e["supersedes"]}
                    for e in all_contacts
                    if e["frame_start"] == f
                ],
                "fsm": semantic["after"],
                "evidence": semantic.get("evidence"),
                "transitions": calls.get(f, []),
                "exit_proof": semantic.get("exit_proof"),
                "perception_diagnostic": diagnostic,
                "external_component_probe": external_probe,
                "candidate_source": (
                    "selected run's own bounded association candidates"
                    if association is not None
                    else "selected run's own frame diagnostic"
                    if shuttle_diagnostic
                    else "external controlled TrackNet component inference with recorded scene/mask context"
                    if external_probe
                    else "unavailable"
                ),
                "shuttle_candidates": candidates,
                "shuttle_rejection": candidate_diagnostic.get("reason") if candidate_diagnostic else None,
                "rejected_player_boxes": player_diagnostic.get("roi_rejected", []) if player_diagnostic else [],
                "top_k_candidates": (
                    "recorded raw heatmap components above diagnostic floor; not calibrated probabilities"
                    if association is not None or candidate_diagnostic
                    else "not recorded for this frame (legacy cache or unselected diagnostic window)"
                ),
                "rejected_candidates": (
                    "recorded candidates retain threshold/mask/selection flags"
                    if association is not None or candidate_diagnostic
                    else "not recorded for this frame"
                ),
            }
        print(f"rendered {name}: {len(indices)} exact-PTS source frames", flush=True)
    container.close()
    assert set(map(int, data["frames"])) == set(selected)
    serialized = json.dumps(data, allow_nan=False, separators=(",", ":")).replace("</", "<\\/")
    (output / "index.html").write_text(HTML.replace("__DATA__", serialized))
    manifest = {
        "mode": "offline original-frame replay; no model inference",
        "run": str(args.run.resolve()),
        "trace": str(args.trace.resolve()),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "template_sha256": hashlib.sha256(
            Path(__file__).with_name("next_temporal_replay_template.html").read_bytes()
        ).hexdigest(),
        "trace_sha256": hashlib.sha256(args.trace.read_bytes()).hexdigest(),
        "original_source_sha256": source_hash,
        "external_component_probe": (
            {
                "directory": str(args.component_probe.resolve()),
                "variant": args.probe_variant,
                "manifest_sha256": hashlib.sha256((args.component_probe / "manifest.json").read_bytes()).hexdigest(),
                "candidates_sha256": hashlib.sha256(
                    (args.component_probe / "candidates.jsonl").read_bytes()
                ).hexdigest(),
                "scope": "external fresh component inference; not selected run's own perception",
            }
            if args.component_probe is not None
            else None
        ),
        "ranges": args.ranges,
        "stride": args.stride,
        "frame_count": len(selected),
        "original_pts_asserted": True,
        "interval_parity": True,
        "trace_cache_bytes_and_source_identity_exact": True,
        "cache_sha256": cache_hashes,
        "source_pixels": "1920x1080 exact-PTS decode, review resize960x540 JPEG88; no labels cover pixels",
        "limits": [
            "GT offline visualization only",
            "Top-k/rejection detail appears only for frames whose versioned diagnostic was recorded",
            "Normalized detector-query rejects lack crop size; displayed as metadata, never invented image boxes",
            "No human pixel/contact labels added",
        ],
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (output / "executor.py").write_bytes(Path(__file__).read_bytes())
    (output / "next_temporal_replay_template.html").write_bytes(
        Path(__file__).with_name("next_temporal_replay_template.html").read_bytes()
    )


if __name__ == "__main__":
    main()
