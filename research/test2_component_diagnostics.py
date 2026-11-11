"""Source-bound technical component coverage, never sporting accuracy labels."""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import sys
from pathlib import Path

import msgpack
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.production_external_semantic_replay import load_finished_input, sha  # noqa: E402


def live_events(events):
    superseded = {e.get("supersedes") for e in events if e.get("supersedes")}
    return [e for e in events if e["event_id"] not in superseded and e["status"] != "retracted"]


def analyse(run: Path, output: Path):
    session = json.loads((run / "session.json").read_text())
    bound = load_finished_input(run, session["session_id"])
    consumed = {str(path): sha(path) for path in {*bound.input_paths, bound.events_path, bound.session_path}}
    consumed[str(Path(__file__).resolve())] = sha(Path(__file__))
    output.mkdir(parents=True, exist_ok=False)
    counters = collections.Counter()
    categories = collections.defaultdict(collections.Counter)
    samples = {"content_changes": [], "future_observations": [], "track_episodes": []}
    positions = collections.defaultdict(list)
    previous_tracks = set()
    with (output / "frame_component_coverage.csv").open("x") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "frame",
                "time_sec",
                "view",
                "calibration",
                "raw_shuttle",
                "association",
                "player_count",
                "detector_observed",
                "current_pose_count",
                "current_racket_count",
                "diagnostic_retained",
                "content_epoch",
            ]
        )
        expected = 0
        for path in sorted(bound.cache_directory.glob("*.msgpack")):
            data = path.read_bytes()
            if hashlib.sha256(data).hexdigest() != bound.expected_caches[path.name]:
                raise ValueError("source cache hash changed")
            consumed[str(path)] = bound.expected_caches[path.name]
            for frame in msgpack.unpackb(data, raw=False)["frames"]:
                f = frame["f"]
                if f != expected:
                    raise ValueError("noncontiguous source cache")
                expected += 1
                people = frame.get("p", [])
                association = frame.get("sa") or {}
                diagnostic = frame.get("dg") or {}
                counters.update(
                    {
                        "frames": 1,
                        "raw_shuttle_present": frame.get("s") is not None,
                        "association_present": bool(association),
                        "detector_ran_frames": bool(frame.get("do")),
                        "full_diagnostic_frames": bool(diagnostic),
                        "player_frames": bool(people),
                        "person_observations": len(people),
                        "candidate_observations": len(association.get("candidates", [])),
                    }
                )
                for key, value in [
                    ("view", frame.get("v")),
                    ("calibration", frame.get("cs")),
                    ("player_count", str(len(people))),
                    ("association_status", association.get("status")),
                    ("association_decision", association.get("association_status")),
                ]:
                    categories[key][str(value)] += 1
                categories["association_reason"].update(association.get("reasons", []))
                sd = diagnostic.get("shuttle") or {}
                if sd:
                    categories["sampled_shuttle_diagnostic_reason"][sd["reason"]] += 1
                if frame.get("cc"):
                    samples["content_changes"].append({"frame": f, "evidence": frame["cc"]})
                tracks = {p["t"] for p in people}
                if tracks != previous_tracks:
                    samples["track_episodes"].append({"frame": f, "tracks": sorted(tracks)})
                    previous_tracks = tracks
                pose_current, racket_current = 0, 0
                for person in people:
                    track = str(person["t"])
                    box = person["b"]
                    positions[track].append([f, (box[0] + box[2]) / 2, box[3]])
                    counters["detector_matched_persons"] += bool(person.get("dm"))
                    categories["identity_method"][str(person.get("im"))] += 1
                    for name, payload, stamp in [("pose", "k", "pf"), ("racket", "rk", "rf")]:
                        present = person.get(payload) is not None
                        current = present and person.get(stamp) == f
                        counters[f"{name}_present_persons"] += present
                        counters[f"{name}_current_persons"] += current
                        counters[f"{name}_carried_persons"] += present and not current
                        if person.get(stamp) is not None and person[stamp] > f:
                            samples["future_observations"].append({"frame": f, "track": track, "kind": name})
                        if name == "pose":
                            pose_current += current
                        else:
                            racket_current += current
                writer.writerow(
                    [
                        f,
                        f * bound.media["fps_den"] / bound.media["fps_num"],
                        frame.get("v"),
                        frame.get("cs"),
                        frame.get("s") is not None,
                        association.get("status"),
                        len(people),
                        frame.get("do"),
                        pose_current,
                        racket_current,
                        bool(diagnostic),
                        frame.get("ce"),
                    ]
                )
    if expected != bound.media["n_frames"]:
        raise ValueError("incomplete component cache coverage")
    all_events = [json.loads(line) for line in bound.events_path.open()]
    events = live_events(all_events)
    event_groups = collections.defaultdict(list)
    for event in events:
        if event["session_id"] != session["session_id"]:
            raise ValueError("foreign session event")
        event_groups[event["type"]].append(event)
    for event in event_groups["contact"]:
        payload = event["payload"]
        for key in ["physical_event_status", "contact_status", "attribution_reason", "temporal_role"]:
            categories[f"contact_{key}"][str(payload.get(key))] += 1
        physical = payload.get("physical_evidence") or {}
        for kind in ["trajectory", "impact", "attribution"]:
            evidence = physical.get(kind) or {}
            categories[f"contact_{kind}_reliability"][str(evidence.get("reliability"))] += 1
            categories[f"contact_{kind}_reasons"].update(evidence.get("reasons", []))
    for event in event_groups["stroke"]:
        categories["stroke_label"][str(event["payload"].get("stroke", "unknown"))] += 1
        categories["stroke_label_status"][str(event["payload"].get("classification_status", "legacy_unknown"))] += 1
    for event in event_groups["rally_end"]:
        categories["rally_end_reason"][str(event["payload"].get("end_reason"))] += 1
        categories["rally_classification"][str(event["payload"].get("rally_classification"))] += 1
    for name, value in [
        ("source_events", all_events),
        (
            "component_events",
            {
                kind: [{"frame": e["frame_start"], "id": e["event_id"], "payload": e["payload"]} for e in values]
                for kind, values in event_groups.items()
            },
        ),
        ("diagnostic_cases", samples),
        ("tracked_image_foot_positions", dict(positions)),
    ]:
        (output / f"{name}.json").write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    result = {
        "schema": "test2-technical-component-diagnostics:v1",
        "session_id": session["session_id"],
        "source_sha256": session["source"]["sha256"],
        "source_report_sha256": sha(run / "inference.json"),
        "consumed_files_sha256": consumed,
        "media": bound.media,
        "counters": dict(counters),
        "categories": dict(categories),
        "event_counts_live": {kind: len(values) for kind, values in event_groups.items()},
        "event_counts_append_only": dict(collections.Counter(e["type"] for e in all_events)),
        "capabilities": session.get("meta", {}).get("capabilities", {}),
        "roster": session["roster"],
        "future_observation_count": len(samples["future_observations"]),
        "cache_bytes": sum(p.stat().st_size for p in bound.cache_directory.glob("*.msgpack")),
        "accuracy_validated": False,
        "limits": [
            "Counts measure technical coverage only; no independent component annotations were loaded.",
            "Raw shuttle means decoder output before association; court masking has already been applied.",
            "Image foot positions are model box bottoms, not validated floor locations or physical speed.",
            "Track keys and reset episodes do not establish identity consistency, IDF1 or named athletes.",
            "Full heatmap/player diagnostics are sampled; all-frame selected observations and association retained.",
            "Shot/contact physical reliability states are system outputs, not externally calibrated accuracy.",
            "Summaries/highlights/API/frontend require separate transport checks; "
            "event coverage alone does not validate them.",
        ],
    }
    # A standalone chart of observed image locations, deliberately avoiding floor projection.
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 6))
    for key, points in positions.items():
        a = np.asarray(points)
        ax.scatter(a[:, 1], a[:, 2], s=1, alpha=0.25, label=f"local track {key}")
    ax.set(
        xlim=(0, bound.media["width"]),
        ylim=(bound.media["height"], 0),
        xlabel="Analysis image x (pixels)",
        ylabel="Box bottom y (pixels)",
        title="Test2 model player foot-position coverage (accuracy unvalidated)",
    )
    if len(positions) <= 12:
        ax.legend(markerscale=4)
    fig.tight_layout()
    fig.savefig(output / "player_image_positions.png", dpi=150)
    plt.close(fig)
    if any(sha(Path(path)) != digest for path, digest in consumed.items()):
        raise ValueError("component diagnostic input changed during analysis")
    result["inputs_unchanged_after_analysis"] = True
    (output / "component_diagnostics.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = analyse(args.run.resolve(), args.output.resolve())
    print(json.dumps({"counters": report["counters"], "events": report["event_counts_live"]}))
