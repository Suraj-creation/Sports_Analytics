"""Read-only changed-event review on completed fixed-perception regressions.

No neural inference, pipeline changes, original database access or GT metrics.
Nearby anchor pairing diagnoses potential temporal shifts, not physical identity.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path

import av
import cv2
import msgpack
import numpy as np
from scipy.optimize import linear_sum_assignment

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
EXTERNAL = ROOT.parent / "ground-truth-validation-artifacts-20261110"


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def live(path):
    events = [json.loads(row) for row in path.read_text().splitlines() if row.strip()]
    superseded = {event["supersedes"] for event in events if event.get("supersedes")}
    if len({e["event_id"] for e in events}) != len(events):
        raise ValueError("Duplicate original event IDs")
    return [e for e in events if e["event_id"] not in superseded and e["status"] != "retracted"]


def compact_event(event):
    payload = event["payload"]
    physical = payload.get("physical_evidence") or {}
    inputs = physical.get("inputs") or {}
    hypothesis = payload.get("participant_hypothesis") or {}
    return {
        "type": event["type"], "frame": event["frame_start"], "seconds": event["frame_start"] / 30,
        "confidence": event.get("confidence"), "event_status": event["status"],
        "actor_player_id": event.get("actors", {}).get("player_id"),
        "stroke": payload.get("stroke"), "classification_status": payload.get("classification_status"),
        "classification_context_source": payload.get("classification_context_source"),
        "classification_abstention_reason": payload.get("classification_abstention_reason"),
        "physical_event_status": payload.get("physical_event_status"),
        "attribution_reason": payload.get("attribution_reason"),
        "hypothesis_status": hypothesis.get("status"), "hypothesis_track_id": hypothesis.get("track_id"),
        "hypothesis_reason": hypothesis.get("reason"), "components": hypothesis.get("components"),
        "racket_evidence_method": payload.get("racket_evidence_method"),
        "racket_overlap_observed": payload.get("racket_overlap_observed"),
        "physical_player_observed": inputs.get("player_observed"),
        "physical_pose_observed": inputs.get("pose_observed"),
        "physical_racket_observed": inputs.get("racket_observed"),
        "physical_proximity_support": inputs.get("proximity_support"),
        "physical_swing_support": inputs.get("swing_support"),
        "physical_racket_overlap_support": inputs.get("racket_overlap_support"),
        "physical_association_status": inputs.get("association_status"),
        "physical_context_start": inputs.get("context_start"), "physical_context_stop": inputs.get("context_stop"),
        "physical_reliabilities": {key: physical[key] for key in ("trajectory", "impact", "attribution") if key in physical},
        "flight_time_s": payload.get("flight_time_s"), "speed_px_s": payload.get("speed_px_s"),
    }


def context(frame, rallies):
    matches = [index for index, e in enumerate(rallies, 1) if e["frame_start"] <= frame <= e["frame_end"]]
    return tuple(matches)


def compare_kind(old, new, kind, max_shift_frames=15):
    before = {e["frame_start"]: e for e in old if e["type"] == kind}
    after = {e["frame_start"]: e for e in new if e["type"] == kind}
    if len(before) != sum(e["type"] == kind for e in old) or len(after) != sum(e["type"] == kind for e in new):
        raise ValueError("Multiple same-kind events at one frame need an explicit association policy")
    missing, added = sorted(before.keys() - after.keys()), sorted(after.keys() - before.keys())
    old_rallies = sorted((e for e in old if e["type"] == "rally_end"), key=lambda e: e["frame_start"])
    new_rallies = sorted((e for e in new if e["type"] == "rally_end"), key=lambda e: e["frame_start"])
    if len(old_rallies) != len(new_rallies):
        raise ValueError("Different rally populations need a separate explicit context association")
    for a, b in zip(old_rallies, new_rallies, strict=True):
        intersection = max(0, min(a["frame_end"], b["frame_end"]) - max(a["frame_start"], b["frame_start"]))
        union = max(a["frame_end"], b["frame_end"]) - min(a["frame_start"], b["frame_start"])
        if not union or intersection / union < .5:
            raise ValueError("Chronological rally contexts lack unambiguous overlapping pairing")
    m, n = len(missing), len(added)
    cost = np.full((m + n, m + n), 1000.0)
    cost[m:, n:] = 0
    for i, a in enumerate(missing):
        for j, b in enumerate(added):
            cost[i, j] = abs(a - b) if abs(a - b) <= max_shift_frames and context(a, old_rallies) == context(b, new_rallies) else 1e9
    assignments = linear_sum_assignment(cost) if m + n else ([], [])
    shifts, used_old, used_new = [], set(), set()
    for i, j in zip(*assignments, strict=True):
        if i < m and j < n and cost[i, j] < 1000:
            a, b = missing[i], added[j]
            used_old.add(a)
            used_new.add(b)
            shifts.append({"before_frame": a, "after_frame": b, "shift_frames": b - a, "shift_seconds": (b - a) / 30,
                           "association": "nearby-anchor candidate shift, not adjudicated physical event identity",
                           "before": compact_event(before[a]), "after": compact_event(after[b])})
    same_anchor_changes = []
    semantic_fields = {"stroke", "classification_status", "classification_abstention_reason", "physical_event_status", "attribution_reason", "hypothesis_status", "hypothesis_track_id"}
    for frame in sorted(before.keys() & after.keys()):
        a, b = compact_event(before[frame]), compact_event(after[frame])
        changes = {key: {"before": a[key], "after": b[key]} for key in a if a[key] != b[key]}
        if changes:
            same_anchor_changes.append({"frame": frame, "seconds": frame / 30, "changes": changes,
                                        "key_semantic_change": bool(semantic_fields & changes.keys()), "before": a, "after": b})
    return {
        "before_count": len(before), "after_count": len(after), "before_absent_exact_anchors": missing,
        "after_new_exact_anchors": added, "candidate_shift_matching_max_frames": max_shift_frames,
        "candidate_shift_matching_context": "same chronological containing rally ordinal, after equal populations and all ordinal interval IoU>=.5 verified; maximum cardinality then minimum absolute frame distance",
        "candidate_temporal_shifts": shifts,
        "unpaired_removed": [compact_event(before[f]) for f in missing if f not in used_old],
        "unpaired_added": [compact_event(after[f]) for f in added if f not in used_new],
        "same_anchor_changes": same_anchor_changes,
    }


def draw(image, frame, withheld, title):
    result = image.copy()
    cv2.putText(result, title, (12, 24), cv2.FONT_HERSHEY_SIMPLEX, .6, (255, 255, 255), 2)
    for person in frame.get("p", []):
        bbox = tuple(round(x) for x in person["b"])
        cv2.rectangle(result, bbox[:2], bbox[2:], (50, 220, 50), 1)
        cv2.putText(result, f"track{person['t']}", (bbox[0], max(42, bbox[1] - 4)), cv2.FONT_HERSHEY_SIMPLEX, .45, (50, 220, 50), 1)
        kps = person.get("k")
        if kps is not None:
            for index in (0, 1, 2, 3, 4, 9, 10):
                point = kps[index]
                if np.isfinite(point).all() and point[2] >= .5:
                    cv2.circle(result, (round(point[0]), round(point[1])), 2, (255, 255, 0), -1)
        racket = person.get("rk")
        if racket:
            center = tuple(round(x) for x in racket["center"])
            axes = tuple(max(1, round(x / 2)) for x in racket["axes"])
            rejected = person["t"] in withheld
            color = (0, 215, 255) if rejected else (0, 0, 255)
            cv2.ellipse(result, center, axes, racket["angle"], 0, 360, color, 2)
            text = "AMBIGUOUS withheld" if rejected else "raw candidate"
            cv2.putText(result, text, (center[0] + 10, center[1]), cv2.FONT_HERSHEY_SIMPLEX, .4, color, 1)
    if frame.get("s") is not None:
        xy = tuple(round(x) for x in frame["s"])
        cv2.drawMarker(result, xy, (255, 0, 255), cv2.MARKER_CROSS, 15, 2)
    cv2.putText(result, f"frame{frame['f']} / {frame['f']/30:.6f}s; frozen predictions, not physical GT", (12, 705), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 1)
    return result


def main(test, output=None):
    cv2.setNumThreads(1)
    baseline = EXTERNAL / ("test_01/improved_v1" if test == 1 else "test_02/baseline_v1")
    experiment = EXTERNAL / f"test_02/test{test}_semantic_regression_v1"
    completion = read(experiment / "completion.json")
    if completion.get("status") != "completed_controlled_semantic_regression" or completion.get("test") != test:
        raise ValueError("Completed matching controlled regression required")
    output = (output or HERE / f"semantic_effect_evidence/test_{test:02d}").resolve()
    if (HERE / "semantic_effect_evidence").resolve() not in output.parents:
        raise ValueError("Review output must stay within owned diagnostic evidence directory")
    if output.exists():
        raise ValueError("Evidence output must be new")
    before_path, after_path = baseline / "run/events.jsonl", experiment / "replay/current-events.jsonl"
    manifest_path = experiment / "replay/replay_manifest.json"
    manifest = read(manifest_path)
    for path in (after_path, manifest_path):
        if completion["artifact_sha256"].get(str(path.relative_to(experiment))) != sha(path):
            raise ValueError("Controlled regression completion output changed")
    original, updated = live(before_path), live(after_path)
    input_hashes = {str(p): sha(p) for p in (before_path, after_path, manifest_path, experiment / "completion.json", Path(__file__))}
    contact, stroke = compare_kind(original, updated, "contact"), compare_kind(original, updated, "stroke")
    warnings = [e for e in updated if e["type"] == "racket_observation_ambiguity"]
    warning_by_frame = collections.defaultdict(list)
    for warning in warnings:
        warning_by_frame[warning["frame_start"]].append(warning)
    focus = {item["frame"] for item in contact["unpaired_removed"] + contact["unpaired_added"]}
    focus.update(item["frame"] for item in stroke["same_anchor_changes"] if item["key_semantic_change"])
    focus.update(item["frame"] for item in contact["same_anchor_changes"] if item["key_semantic_change"])
    for shift in contact["candidate_temporal_shifts"][:3]:
        focus.update((shift["before_frame"], shift["after_frame"]))
    unpaired_frames = {item["frame"] for item in contact["unpaired_removed"] + contact["unpaired_added"]}
    sample_frames = set(sorted(unpaired_frames)[:16])
    sample_frames.update(sorted(focus - sample_frames)[:max(0, 16 - len(sample_frames))])
    for item in contact["unpaired_removed"]:
        for nearby in (item["frame"] - 1, item["frame"] + 1, item["frame"] + 3):
            if nearby in warning_by_frame:
                sample_frames.add(nearby)
    sid = read(baseline / "run/session.json")["session_id"]
    raw_frames, raw_caches = {}, []
    for path in sorted((baseline / "run/data/sessions" / sid / "perception").glob("*.msgpack")):
        chunk = msgpack.unpackb(path.read_bytes(), raw=False)
        needed = [f for f in sample_frames if chunk["start"] <= f <= chunk["end"]]
        if needed:
            if sha(path) != manifest["cache_sha256"][path.name]:
                raise ValueError("Frozen raw cache differs from the controlled replay input")
            input_hashes[str(path)] = sha(path)
            raw_caches.append(str(path))
            raw_frames.update({row["f"]: row for row in chunk["frames"] if row["f"] in sample_frames})
    source_sha = read(baseline / "run/inference.json")["source_sha256"]
    proxy = baseline / "run/data/media" / source_sha / "proxy.mp4"
    input_hashes[str(proxy)] = sha(proxy)
    output.mkdir(parents=True)
    (output / "executed_review_helper.py").write_bytes(Path(__file__).read_bytes())
    images = []
    if sample_frames:
        with av.open(str(proxy)) as container:
            container.streams.video[0].thread_count = 1
            for index, frame in enumerate(container.decode(video=0)):
                if index in sample_frames:
                    image = frame.to_ndarray(format="bgr24")
                    raw = raw_frames[index]
                    withheld = {e["payload"]["owner_track_id"] for e in warning_by_frame[index]}
                    picture = np.concatenate((draw(image, raw, set(), "Original raw geometric racket candidates"),
                                              draw(image, raw, withheld, "New semantic admission (same raw pixels/observations)")), axis=1)
                    name = f"frame_{index:05d}_raw_vs_semantic.png"
                    cv2.imwrite(str(output / name), picture)
                    images.append({"frame": index, "seconds": index / 30, "proxy_pts": frame.pts, "time_base": str(frame.time_base),
                                   "source_pixels_sha256": hashlib.sha256(image.tobytes()).hexdigest(), "overlay": name,
                                   "overlay_sha256": sha(output / name), "withheld_owner_tracks": sorted(withheld)})
                    (output / f"frame_{index:05d}_raw_and_admission.json").write_text(json.dumps({"raw": raw, "ambiguity_events": warning_by_frame[index]}, indent=2) + "\n")
                if index >= max(sample_frames):
                    break
    changed_frames = {item["frame"] for item in contact["same_anchor_changes"] if item["key_semantic_change"]}
    changed_frames.update(f for shift in contact["candidate_temporal_shifts"] for f in (shift["before_frame"], shift["after_frame"]))
    changed_frames.update(item["frame"] for item in contact["unpaired_removed"] + contact["unpaired_added"])
    nearby = {str(frame): [{"frame": e["frame_start"], "owner_track_id": e["payload"]["owner_track_id"], "event_id": e["event_id"]}
                            for e in warnings if abs(e["frame_start"] - frame) <= 5] for frame in sorted(changed_frames)}
    result = {
        "test": test, "scope": "Independent read-only event comparison on fixed original perception; NOT fresh neural inference",
        "contact": contact, "stroke": stroke,
        "before_live_event_counts": dict(collections.Counter(e["type"] for e in original)),
        "after_live_event_counts": dict(collections.Counter(e["type"] for e in updated)),
        "before_stroke_labels": dict(collections.Counter(e["payload"].get("stroke") for e in original if e["type"] == "stroke")),
        "after_stroke_labels": dict(collections.Counter(e["payload"].get("stroke") for e in updated if e["type"] == "stroke")),
        "ambiguity_event_count": len(warnings), "nearby_admission_events": nearby,
        "sampled_images": images, "sampling": "Unpaired anchors prioritized, then key semantic changes/first three shifts; at most16primary frames plus adjacent emitted ambiguities",
        "requested_review_frames_without_visual": sorted(focus - sample_frames),
        "input_sha256": input_hashes, "raw_observations_modified": False, "pipeline_modified": False,
        "physical_precision_recall_or_class_accuracy_computed": False,
    }
    (output / "event_diff.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    cases = {"before_changed_contacts": [e for e in original if e["type"] == "contact" and e["frame_start"] in changed_frames],
             "after_changed_contacts": [e for e in updated if e["type"] == "contact" and e["frame_start"] in changed_frames],
             "nearby_complete_ambiguity_events": [e for e in warnings if any(abs(e["frame_start"] - f) <= 5 for f in changed_frames)]}
    (output / "complete_changed_event_evidence.json").write_text(json.dumps(cases, indent=2) + "\n")
    if any(sha(path) != expected for path, expected in input_hashes.items()):
        raise ValueError("Read-only review input changed")
    print(json.dumps({"status": "completed", "test": test, "candidate_shifts": len(contact["candidate_temporal_shifts"]),
                      "unpaired_removed": [x["frame"] for x in contact["unpaired_removed"]], "output": str(output)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test", type=int, choices=(1, 2), required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    main(args.test, args.output)
