"""Evaluate automatic episode candidates against exhaustive independent labels.

Person attribution is conditional on a separately reviewed episode-to-person
map. It is not an evaluation of automatic re-identification. No session data is
modified. See research/shot-annotation-protocol.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any

from bai_engine.schema.events import Event, EventStatus, current_view
from research.shot_benchmark import _matches, evaluate, predictions_from_session, validate_inputs

_EPISODE = re.compile(r"participant-[A-Za-z0-9]+-[0-9]{6}\Z")


def _finite(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _ratio(n: int, d: int) -> float | None:
    return n / d if d else None


def validate_bindings(labels: dict, bindings: dict, *, allow_draft: bool = False) -> None:
    if bindings.get("schema_version") != 1:
        raise ValueError("bindings: unsupported schema version")
    for key in ("session_id", "media_sha256", "timebase", "window_s"):
        if bindings.get(key) != labels.get(key):
            raise ValueError(f"bindings: {key} mismatch")
    digest = bindings.get("event_log_sha256")
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError("bindings: valid event log hash required")
    if bindings.get("status") not in ("reviewed", "draft"):
        raise ValueError("bindings: reviewed or draft status required")
    if bindings["status"] != "reviewed" and not allow_draft:
        raise ValueError("bindings: reviewed mapping required")
    review = bindings.get("review")
    if not isinstance(review, dict) or review.get("independent_of_shot_labels") is not True:
        raise ValueError("bindings: independent track-to-person review required")
    if bindings["status"] == "reviewed" and (
        review.get("human_verified") is not True or review.get("exhaustive_for_window") is not True
    ):
        raise ValueError("bindings: reviewed mapping requires human verification and exhaustive episode review")
    entries = bindings.get("bindings")
    if not isinstance(entries, list):
        raise ValueError("bindings: list required")
    window = labels["window_s"]
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError("bindings: invalid entry")
        episode, person, track = entry.get("participant_id"), entry.get("player_id"), entry.get("track_id")
        start, end = entry.get("start_s"), entry.get("end_s")
        if (
            not isinstance(episode, str)
            or not _EPISODE.fullmatch(episode)
            or not isinstance(person, str)
            or not person
            or isinstance(track, bool)
            or not isinstance(track, int)
            or track < 0
            or not _finite(start)
            or not _finite(end)
            or not window[0] <= start < end <= window[1]
        ):
            raise ValueError("bindings: invalid episode, player, track or interval")
        for previous in entries[:i]:
            if (
                start < previous["end_s"]
                and previous["start_s"] < end
                and (
                    episode == previous["participant_id"]
                    or person == previous["player_id"]
                    or track == previous["track_id"]
                )
            ):
                raise ValueError("bindings: conflicting overlapping intervals")


def _candidate_person(row: dict, bindings: list[dict]) -> str | None:
    hypothesis = row.get("participant_hypothesis")
    if hypothesis is None:
        return None
    if not isinstance(hypothesis, dict) or hypothesis.get("status") not in ("provisional", "unresolved"):
        raise ValueError("prediction: automatic provisional or unresolved hypothesis required")
    if hypothesis["status"] == "unresolved":
        if hypothesis.get("participant_id") is not None or hypothesis.get("track_id") is not None:
            raise ValueError("prediction: unresolved hypothesis must not name an episode or track")
        return None
    episode, track = hypothesis.get("participant_id"), hypothesis.get("track_id")
    if (
        not isinstance(episode, str)
        or not _EPISODE.fullmatch(episode)
        or isinstance(track, bool)
        or not isinstance(track, int)
        or track < 0
    ):
        raise ValueError("prediction: invalid automatic episode or track")
    matched = [
        b
        for b in bindings
        if b["participant_id"] == episode and b["track_id"] == track and b["start_s"] <= row["time_s"] < b["end_s"]
    ]
    return matched[0]["player_id"] if len(matched) == 1 else None


def evaluate_participants(
    labels: dict, predictions: dict, bindings: dict, *, tolerance_s: float = 0.2, allow_draft: bool = False
) -> dict[str, Any]:
    validate_inputs(labels, predictions, allow_draft=allow_draft)
    validate_bindings(labels, bindings, allow_draft=allow_draft)
    if predictions.get("event_log_sha256") != bindings["event_log_sha256"]:
        raise ValueError("bindings: event log hash mismatch; track episodes may belong to another analysis")
    # Never reuse the score-slot actor or any person value from a prediction.
    resolved = [{**row, "player_id": _candidate_person(row, bindings["bindings"])} for row in predictions["shots"]]
    base = evaluate(labels, {**predictions, "shots": resolved}, tolerance_s=tolerance_s, allow_draft=allow_draft)
    gt = sorted(labels["shots"], key=lambda row: row["time_s"])
    pred = sorted(resolved, key=lambda row: row["time_s"])
    pairs = _matches(gt, pred, tolerance_s)
    labelled = [(gt[i], pred[j]) for i, j in pairs if gt[i].get("player_id") is not None]
    truth_total = sum(row.get("player_id") is not None for row in gt)
    correct = sum(a["player_id"] == b["player_id"] for a, b in labelled)
    decided = sum(b["player_id"] is not None for _, b in labelled)
    reasons = Counter(
        "unresolved" if b["player_id"] is None else "correct" if a["player_id"] == b["player_id"] else "wrong"
        for a, b in labelled
    )
    return {
        "version": "participant-benchmark-v2",
        "accuracy_claim_eligible": (
            base["accuracy_claim_eligible"]
            and bindings["status"] == "reviewed"
            and truth_total > 0
            and bool(bindings["bindings"])
        ),
        "counting_scope": "automatic_episode_hypotheses_conditioned_on_external_identity_bindings",
        "identity_binding_status": bindings["status"],
        "session_id": labels["session_id"],
        "media_sha256": labels["media_sha256"],
        "window_s": labels["window_s"],
        "tolerance_s": tolerance_s,
        "shot_detection": {
            key: base[key]
            for key in (
                "truth_count",
                "prediction_count",
                "matched",
                "false_positives",
                "false_negatives",
                "detection_precision",
                "detection_recall",
            )
        },
        "shot_classification": {
            key: base[key]
            for key in ("per_class", "macro_f1", "confusion", "unknown_prediction_fraction", "known_family")
        },
        "end_to_end": base["end_to_end"],
        "metric_eligibility": {
            key: value and bindings["status"] == "reviewed" for key, value in base["metric_eligibility"].items()
        },
        "participant": {
            "labelled_truth": truth_total,
            "matched_labelled_truth": len(labelled),
            "unmatched_labelled_truth": truth_total - len(labelled),
            "correct": correct,
            "wrong": reasons["wrong"],
            "unresolved": reasons["unresolved"],
            "resolved_fraction_matched": _ratio(decided, len(labelled)),
            "accuracy_all_labelled_truth": _ratio(correct, truth_total),
            "accuracy_resolved_matched": _ratio(correct, decided),
        },
        "limitations": [
            "Person identities depend on an independently reviewed episode map; "
            "this does not measure automatic re-identification.",
            "Accuracy requires exhaustive held-out human-reviewed shot labels and independently reviewed bindings.",
        ],
    }


def automatic_predictions_from_session(data_dir: Path, session_id: str, labels: dict) -> dict:
    session_db = (data_dir / "sessions.sqlite").resolve()
    with sqlite3.connect(f"{session_db.as_uri()}?mode=ro", uri=True) as conn:
        first_row = conn.execute("SELECT body FROM sessions WHERE session_id=?", (session_id,)).fetchone()
    if first_row is None:
        raise ValueError("unknown session")
    predictions = predictions_from_session(data_dir, session_id, labels)
    event_path = (data_dir / "sessions" / session_id / "events.sqlite").resolve()
    with sqlite3.connect(f"{event_path.as_uri()}?mode=ro", uri=True) as conn:
        rows = conn.execute("SELECT seq,body FROM events ORDER BY seq").fetchall()
    if hashlib.sha256("\n".join(body for _, body in rows).encode()).hexdigest() != predictions["event_log_sha256"]:
        raise ValueError("event log changed during evaluation; use a stable snapshot")
    events = [Event.model_validate_json(body).with_seq(seq) for seq, body in rows]
    # Reject corrected *and retracted* shot/contact evidence, including events
    # that disappeared from current_view. Silence would bias the comparison.
    with sqlite3.connect(f"{session_db.as_uri()}?mode=ro", uri=True) as conn:
        session_row = conn.execute("SELECT body FROM sessions WHERE session_id=?", (session_id,)).fetchone()
    if session_row != first_row:
        raise ValueError("session changed during evaluation; use a stable snapshot")
    from bai_engine.schema.session import Session

    session = Session.model_validate_json(session_row[0])
    for event in events:
        t = float(event.frame_start / session.media.fps)
        in_window = labels["window_s"][0] <= t < labels["window_s"][1]
        if (
            in_window
            and event.type in ("stroke", "contact")
            and (
                event.provenance.model == "human"
                or event.status == EventStatus.HUMAN_VERIFIED
                or (event.type == "stroke" and event.status == EventStatus.CORRECTED)
            )
        ):
            raise ValueError("automatic evaluation requires an uncorrected machine-only event snapshot")
    live = {e.event_id: e for e in current_view(events)}
    for row in predictions["shots"]:
        event = live[row["event_id"]]
        if (
            event.status in (EventStatus.HUMAN_VERIFIED, EventStatus.CORRECTED)
            or event.supersedes
            or event.provenance.model == "human"
        ):
            raise ValueError("automatic evaluation requires an uncorrected machine-only event snapshot")
        row["participant_hypothesis"] = event.payload.get("participant_hypothesis")
    return predictions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", required=True)
    parser.add_argument("--annotations", required=True, type=Path)
    parser.add_argument("--bindings", required=True, type=Path)
    parser.add_argument("--data-dir", default=Path("data"), type=Path)
    parser.add_argument("--tolerance-s", default=0.2, type=float)
    parser.add_argument("--allow-draft", action="store_true")
    args = parser.parse_args()
    try:
        annotation_raw, binding_raw = args.annotations.read_bytes(), args.bindings.read_bytes()
        labels, bindings = json.loads(annotation_raw), json.loads(binding_raw)
        predictions = automatic_predictions_from_session(args.data_dir, args.session, labels)
        result = evaluate_participants(
            labels, predictions, bindings, tolerance_s=args.tolerance_s, allow_draft=args.allow_draft
        )
        result["provenance"] = {
            "annotations_sha256": hashlib.sha256(annotation_raw).hexdigest(),
            "bindings_sha256": hashlib.sha256(binding_raw).hexdigest(),
            "event_log_sha256": predictions["event_log_sha256"],
        }
        print(json.dumps(result, indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, sqlite3.Error) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
