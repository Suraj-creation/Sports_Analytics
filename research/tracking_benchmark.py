"""Source-bound sampled-frame localization and global identity evaluation.

Identity names are matched once over the whole window, never per frame or per
episode. Sparse labels measure sampled agreement, not continuous-frame accuracy.
The evaluator reads JSON and never changes sessions or identity review records.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment


def _hash(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _ratio(n: int, d: int) -> float | None:
    return n / d if d else None


def _boxes(document: dict, *, labels: bool) -> dict[int, list[dict]]:
    rows = document.get("frames")
    if not isinstance(rows, list):
        raise ValueError("frames must be a list")
    out = {}
    for row in rows:
        if not isinstance(row, dict) or not _integer(row.get("frame_idx")):
            raise ValueError("invalid frame")
        frame = row["frame_idx"]
        if frame not in document["sampled_frames"] or frame in out:
            raise ValueError("duplicate or unrequested frame")
        if labels and row.get("exhaustive") is not True:
            raise ValueError("every sampled frame must exhaustively label visible people")
        persons = row.get("persons")
        if not isinstance(persons, list):
            raise ValueError("persons must be a list")
        ids = set()
        for person in persons:
            if not isinstance(person, dict):
                raise ValueError("invalid person")
            box = person.get("bbox")
            if (
                not isinstance(box, list)
                or len(box) != 4
                or any(not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v) for v in box)
                or not 0 <= box[0] < box[2] <= document["width"]
                or not 0 <= box[1] < box[3] <= document["height"]
            ):
                raise ValueError("invalid in-frame bbox")
            key = person.get("person_id" if labels else "identity_key")
            if key is not None:
                if not isinstance(key, str) or not key or key in ids:
                    raise ValueError("duplicate or invalid identity in frame")
                ids.add(key)
        out[frame] = persons
    if labels and set(out) != set(document["sampled_frames"]):
        raise ValueError("labels must cover every declared sampled frame")
    return out


def validate_inputs(labels: dict, predictions: dict, *, allow_draft: bool = False) -> tuple[dict, dict]:
    keys = (
        "schema_version",
        "session_id",
        "media_sha256",
        "proxy_sha256",
        "fps_num",
        "fps_den",
        "width",
        "height",
        "window_frames",
        "timebase",
        "sampled_frames",
    )
    for key in keys:
        if key not in labels or labels[key] != predictions.get(key):
            raise ValueError(f"source binding mismatch: {key}")
    if labels["schema_version"] != 1 or labels["timebase"] != "analysis_proxy_frames":
        raise ValueError("unsupported schema or timebase")
    if not isinstance(labels["session_id"], str) or not labels["session_id"]:
        raise ValueError("session id required")
    if not _hash(labels["media_sha256"]) or not _hash(labels["proxy_sha256"]):
        raise ValueError("source and proxy hashes required")
    if any(not _integer(labels[k]) or labels[k] <= 0 for k in ("fps_num", "fps_den", "width", "height")):
        raise ValueError("positive integer media dimensions and fps required")
    window = labels["window_frames"]
    if (
        not isinstance(window, list)
        or len(window) != 2
        or not all(_integer(v) for v in window)
        or not 0 <= window[0] < window[1]
    ):
        raise ValueError("invalid half-open frame window")
    sampled = labels["sampled_frames"]
    if (
        not isinstance(sampled, list)
        or not sampled
        or not all(_integer(f) and window[0] <= f < window[1] for f in sampled)
        or sampled != sorted(set(sampled))
    ):
        raise ValueError("explicit sorted unique sampled frames required")
    if labels.get("status") not in ("reviewed", "draft") or labels.get("split") not in (
        "held_out",
        "development",
        "diagnostic",
    ):
        raise ValueError("explicit review status and split required")
    if labels["status"] == "draft" and not allow_draft:
        raise ValueError("draft requires explicit opt-in")
    review = labels.get("review")
    if not isinstance(review, dict) or review.get("blind_to_predictions") is not True:
        raise ValueError("independent visual review required")
    if labels["status"] == "reviewed" and review.get("human_verified") is not True:
        raise ValueError("reviewed labels require human verification")
    if not isinstance(predictions.get("analysis_generation"), str) or not predictions["analysis_generation"]:
        raise ValueError("analysis generation required")
    if not _hash(predictions.get("event_log_sha256")):
        raise ValueError("event log hash required")
    chunks = predictions.get("track_chunks")
    if not isinstance(chunks, list) or not chunks:
        raise ValueError("evaluated track chunk hashes required")
    paths = set()
    for chunk in chunks:
        if (
            not isinstance(chunk, dict)
            or not isinstance(chunk.get("path"), str)
            or not chunk["path"]
            or chunk["path"] in paths
            or not _hash(chunk.get("sha256"))
        ):
            raise ValueError("invalid or duplicate track chunk hash")
        paths.add(chunk["path"])
    return _boxes(labels, labels=True), _boxes(predictions, labels=False)


def _overlaps(truth: list[dict], predictions: list[dict]) -> np.ndarray:
    if not truth or not predictions:
        return np.zeros((len(truth), len(predictions)), dtype=float)
    a = np.asarray([row["bbox"] for row in truth], dtype=float)
    b = np.asarray([row["bbox"] for row in predictions], dtype=float)
    lo = np.maximum(a[:, None, :2], b[None, :, :2])
    hi = np.minimum(a[:, None, 2:], b[None, :, 2:])
    area = np.prod(np.maximum(hi - lo, 0), axis=2)
    union = np.prod(a[:, 2:] - a[:, :2], axis=1)[:, None] + np.prod(b[:, 2:] - b[:, :2], axis=1)[None, :] - area
    return area / union


def box_matches(truth: list[dict], predictions: list[dict], threshold: float) -> list[tuple[int, int]]:
    iou = _overlaps(truth, predictions)
    if not iou.size:
        return []
    valid = iou >= threshold
    # One extra valid match outweighs every possible IoU tie-break improvement.
    score = valid * (min(len(truth), len(predictions)) + 1 + iou)
    ii, jj = linear_sum_assignment(score, maximize=True)
    return [(int(i), int(j)) for i, j in zip(ii, jj, strict=True) if valid[i, j]]


def evaluate_tracking(
    labels: dict, predictions: dict, *, iou_threshold: float = 0.5, allow_draft: bool = False
) -> dict:
    gt, pred = validate_inputs(labels, predictions, allow_draft=allow_draft)
    if isinstance(iou_threshold, bool) or not math.isfinite(iou_threshold) or not 0 < iou_threshold <= 1:
        raise ValueError("IoU threshold must be in (0, 1]")
    truth_count = prediction_count = matched_count = known_count = ambiguous = identity_prediction_count = 0
    four_visible = four_localized = four_distinct = switches = fragments = assignment_ambiguous = 0
    cooccurrence = Counter()
    previous = {}
    interrupted = set()
    identities = defaultdict(set)
    for frame in labels["sampled_frames"]:
        a, b = gt[frame], pred.get(frame, [])
        pairs = box_matches(a, b, iou_threshold)
        compatible = _overlaps(a, b) >= iou_threshold
        truth_count += len(a)
        prediction_count += len(b)
        matched_count += len(pairs)
        unknown_truth_matched = {
            j
            for j in range(len(b))
            if any(compatible[i, j] and p.get("person_id") is None for i, p in enumerate(a))
            and not any(compatible[i, j] and p.get("person_id") is not None for i, p in enumerate(a))
        }
        identity_prediction_count += len(b) - len(unknown_truth_matched)
        if len(a) == 4:
            four_visible += 1
            four_localized += int(len(pairs) == 4)
            keys = [b[j].get("identity_key") for _, j in pairs]
            four_distinct += int(len(keys) == 4 and None not in keys and len(set(keys)) == 4)
        # A gap in observable truth cannot establish whether a switch occurred.
        visible_known = {p["person_id"] for p in a if p.get("person_id") is not None}
        for person in set(previous) - visible_known:
            previous.pop(person, None)
            interrupted.discard(person)
        for i, person in enumerate(a):
            pid = person.get("person_id")
            if pid is None:
                ambiguous += 1
                continue
            known_count += 1
            identities[pid]  # include a never-matched known player in support reporting
            possible = [j for j in range(len(b)) if compatible[i, j]]
            for j in possible:
                key = b[j].get("identity_key")
                if key is not None:
                    cooccurrence[pid, key] += 1
                    identities[pid].add(key)
            # Global identity overlap counts use all IoU-compatible pairs. Local
            # box tie-breaking must not fabricate identity switches at overlap.
            if len(possible) > 1 or (possible and int(compatible[:, possible[0]].sum()) > 1):
                assignment_ambiguous += 1
                previous.pop(pid, None)
                interrupted.discard(pid)
                continue
            key = b[possible[0]].get("identity_key") if possible else None
            if key is None:
                if pid in previous:
                    interrupted.add(pid)
                continue
            if pid in previous:
                switches += int(previous[pid] != key)
                fragments += int(pid in interrupted)
            previous[pid] = key
            interrupted.discard(pid)
    people = sorted({p for p, _ in cooccurrence})
    keys = sorted({k for _, k in cooccurrence})
    counts = np.array([[cooccurrence[p, k] for k in keys] for p in people], dtype=int)
    mapping = {}
    idtp = 0
    if people and keys:
        ii, jj = linear_sum_assignment(counts, maximize=True)
        mapping = {people[i]: keys[j] for i, j in zip(ii, jj, strict=True) if counts[i, j] > 0}
        idtp = sum(cooccurrence[p, k] for p, k in mapping.items())
    eligible = labels["status"] == "reviewed" and labels["split"] == "held_out"
    return {
        "evaluator_version": "sampled-tracking-v1",
        "accuracy_claim_eligible": eligible,
        "metric_eligibility": {"localization": eligible and truth_count > 0, "identity": eligible and known_count > 0},
        "scope": "sampled_tracking_box_agreement_not_person_detector_accuracy",
        "session_id": labels["session_id"],
        "media_sha256": labels["media_sha256"],
        "proxy_sha256": labels["proxy_sha256"],
        "window_frames": labels["window_frames"],
        "sampled_frames": labels["sampled_frames"],
        "status": labels["status"],
        "split": labels["split"],
        "iou_threshold": iou_threshold,
        "missing_prediction_frames": len(set(gt) - set(pred)),
        "localization": {
            "truth_count": truth_count,
            "prediction_count": prediction_count,
            "true_positives": matched_count,
            "false_positives": prediction_count - matched_count,
            "false_negatives": truth_count - matched_count,
            "precision": _ratio(matched_count, prediction_count),
            "recall": _ratio(matched_count, truth_count),
        },
        "identity": {
            "labelled_truth": known_count,
            "ambiguous_truth_boxes": ambiguous,
            "prediction_support": identity_prediction_count,
            "idtp": idtp,
            "idfp": identity_prediction_count - idtp,
            "idfn": known_count - idtp,
            "idf1": _ratio(2 * idtp, known_count + identity_prediction_count),
            "sampled_switches": switches,
            "sampled_fragments": fragments,
            "ambiguous_assignment_truth_boxes": assignment_ambiguous,
            "switch_scope": "uniquely_localizable_sample_pairs_only",
            "global_mapping": mapping,
            "distinct_compatible_keys_per_person": {p: len(v) for p, v in identities.items()},
        },
        "four_player": {
            "four_visible_frames": four_visible,
            "all_localized_frames": four_localized,
            "four_distinct_identity_frames": four_distinct,
            "distinct_matched_fraction": _ratio(four_distinct, four_visible),
        },
        "limitations": [
            "Sparse sampled frames cannot validate continuity between samples.",
            "AI draft agreement does not establish human-reviewed accuracy.",
            "Detector provenance is frame-level and does not prove an individual person was detected.",
        ],
    }


def predictions_from_session(data_dir: Path, session_id: str, labels: dict) -> dict:
    """Read a stable snapshot; birth IDs namespace reused numeric track IDs.

    Source/proxy bytes, media metadata, selected latest Parquet revisions and
    event bodies are checked. No inferred or reviewed person mapping is used.
    """
    from bai_engine.schema import Event, EventStatus, TrackObject
    from bai_engine.schema.events import current_view
    from bai_engine.schema.session import Session
    from bai_engine.store import TrackStore

    if not isinstance(session_id, str) or not session_id.isalnum():
        raise ValueError("invalid session id")
    data_dir = data_dir.resolve()
    session_db = data_dir / "sessions.sqlite"
    with sqlite3.connect(f"{session_db.as_uri()}?mode=ro", uri=True) as conn:
        row = conn.execute("SELECT body FROM sessions WHERE session_id=?", (session_id,)).fetchone()
    if row is None:
        raise ValueError("unknown session")
    session = Session.model_validate_json(row[0])
    if (
        session.media is None
        or session.session_id != labels.get("session_id")
        or session.source.sha256 != labels.get("media_sha256")
    ):
        raise ValueError("source/session binding mismatch")
    for name in ("fps_num", "fps_den", "width", "height"):
        if getattr(session.media, name) != labels.get(name):
            raise ValueError(f"media binding mismatch: {name}")
    window = labels.get("window_frames")
    if not isinstance(window, list) or len(window) != 2 or not 0 <= window[0] < window[1] <= session.media.n_frames:
        raise ValueError("window exceeds source media")
    media = data_dir / "media" / session.source.sha256

    def digest(path: Path) -> str:
        value = hashlib.sha256()
        with path.open("rb") as file:
            for block in iter(lambda: file.read(1024 * 1024), b""):
                value.update(block)
        return value.hexdigest()

    if digest(media / "source.mp4") != labels["media_sha256"]:
        raise ValueError("source file hash mismatch")
    if digest(media / "proxy.mp4") != labels.get("proxy_sha256"):
        raise ValueError("proxy file hash mismatch")
    directory = data_dir / "sessions" / session_id
    event_db = directory / "events.sqlite"

    def read_events() -> list:
        with sqlite3.connect(f"{event_db.as_uri()}?mode=ro", uri=True) as conn:
            return conn.execute("SELECT seq,body FROM events ORDER BY seq").fetchall()

    events = read_events()
    event_hash = hashlib.sha256("\n".join(body for _, body in events).encode()).hexdigest()
    live = current_view([Event.model_validate_json(body).with_seq(seq) for seq, body in events])
    boundaries = [event for event in live if event.type in ("identity_ambiguity", "participant_observation")]
    births = {event.event_id: event for event in boundaries if event.type == "participant_observation"}

    def valid_birth_at(birth: Event | None, track_id: int, frame: int) -> bool:
        if (
            birth is None
            or birth.status != EventStatus.PROVISIONAL
            or birth.provenance.model != "participant_tracker_v1"
        ):
            return False
        participant = birth.payload.get("participant_id")
        match = (
            re.fullmatch(r"participant-([A-Za-z0-9]+)-[0-9]{6}", participant) if isinstance(participant, str) else None
        )
        if (
            not match
            or birth.frame_start > frame
            or birth.payload.get("track_id") != track_id
            or birth.payload.get("kind") not in ("PARTICIPANT_FIRST_OBSERVED", "PLAYER_ENTERED")
        ):
            return False
        for other in boundaries:
            if other.event_id == birth.event_id or not birth.frame_start <= other.frame_start <= frame:
                continue
            kind = other.payload.get("kind")
            if (
                other.type == "participant_observation"
                and kind in ("PARTICIPANT_FIRST_OBSERVED", "PLAYER_ENTERED")
                and other.payload.get("track_id") == track_id
                and other.event_id != birth.event_id
            ):
                return False
            if other.frame_start == birth.frame_start and (other.seq or 0) < (birth.seq or 0):
                continue
            if other.type == "identity_ambiguity" and (
                other.payload.get("reason")
                in ("visual_tracker_reset", "calibration_changed", "prolonged_coverage_loss")
                or other.payload.get("tracker_instance") not in (None, match.group(1))
            ):
                return False
            if kind == "PLAYER_EXITED" and other.payload.get("participant_id") == participant:
                return False
        return True

    if not (directory / "tracks/player").is_dir():
        raise ValueError("track snapshot unavailable")
    tracks = TrackStore(directory / "tracks")
    files = [
        (start, end, path)
        for start, end, path in tracks._latest(TrackObject.PLAYER)
        if start < window[1] and end >= window[0]
    ]
    manifest = [{"path": str(path.relative_to(directory)), "sha256": digest(path)} for _, _, path in files]
    generation = hashlib.sha256(json.dumps([event_hash, manifest], sort_keys=True).encode()).hexdigest()
    selected = set(labels.get("sampled_frames", []))
    frames: dict[int, list] = {f: [] for f in selected if any(start <= f <= end for start, end, _ in files)}
    exclusions = Counter()
    for sample in tracks.read([TrackObject.PLAYER], window[0], window[1] - 1).to_pylist():
        frame = sample["frame_idx"]
        if frame not in selected:
            continue
        if sample["visible"] is not True or sample.get("bbox") is None:
            exclusions["invisible_or_missing_box"] += 1
            continue
        box = sample["bbox"]
        if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in box):
            raise ValueError("nonfinite stored track box")
        clipped = [max(0, box[0]), max(0, box[1]), min(session.media.width, box[2]), min(session.media.height, box[3])]
        if clipped[2] <= clipped[0] or clipped[3] <= clipped[1]:
            exclusions["outside_image"] += 1
            continue
        if clipped != box:
            exclusions["clipped_to_image"] += 1
        observation_id = sample.get("participant_observation_id")
        birth = births.get(observation_id)
        valid_birth = valid_birth_at(birth, sample["track_id"], frame)
        frames.setdefault(frame, []).append(
            {
                "bbox": clipped,
                "track_id": sample["track_id"],
                "identity_key": f"{generation}:{observation_id}" if valid_birth else None,
                "participant_observation_id": observation_id,
                "detector_observed": sample.get("detector_observed"),
            }
        )
    current_files = [
        (start, end, path)
        for start, end, path in tracks._latest(TrackObject.PLAYER)
        if start < window[1] and end >= window[0]
    ]
    if events != read_events() or manifest != [
        {"path": str(path.relative_to(directory)), "sha256": digest(path)} for _, _, path in current_files
    ]:
        raise ValueError("snapshot changed during evaluation")
    with sqlite3.connect(f"{session_db.as_uri()}?mode=ro", uri=True) as conn:
        if row != conn.execute("SELECT body FROM sessions WHERE session_id=?", (session_id,)).fetchone():
            raise ValueError("session changed during evaluation")
    common = {
        key: labels[key]
        for key in (
            "schema_version",
            "session_id",
            "media_sha256",
            "proxy_sha256",
            "fps_num",
            "fps_den",
            "width",
            "height",
            "window_frames",
            "timebase",
            "sampled_frames",
        )
    }
    return {
        **common,
        "analysis_generation": generation,
        "event_log_sha256": event_hash,
        "track_chunks": manifest,
        "extraction_counts": dict(exclusions),
        "frames": [{"frame_idx": frame, "persons": persons} for frame, persons in sorted(frames.items())],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", required=True, type=Path)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--predictions", type=Path)
    inputs.add_argument("--data-dir", type=Path)
    parser.add_argument("--session")
    parser.add_argument("--allow-draft", action="store_true")
    parser.add_argument("--iou-threshold", type=float, default=0.5)
    args = parser.parse_args()
    try:
        raw_a = args.annotations.read_bytes()
        labels = json.loads(raw_a)
        predictions = (
            json.loads(args.predictions.read_bytes())
            if args.predictions
            else predictions_from_session(args.data_dir, args.session, labels)
        )
        raw_p = json.dumps(predictions, sort_keys=True).encode()
        result = evaluate_tracking(labels, predictions, iou_threshold=args.iou_threshold, allow_draft=args.allow_draft)
        result["provenance"] = {
            "annotations_sha256": hashlib.sha256(raw_a).hexdigest(),
            "predictions_sha256": hashlib.sha256(raw_p).hexdigest(),
        }
        result["input_manifest"] = {
            key: predictions[key] for key in ("analysis_generation", "event_log_sha256", "track_chunks")
        }
        print(json.dumps(result, indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, sqlite3.Error) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
