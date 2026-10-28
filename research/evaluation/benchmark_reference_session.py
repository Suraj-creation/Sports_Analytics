"""Compare a machine-only application snapshot with published singles references.

Timestamp metrics measure agreement with published hit anchors, whose exact
physical racket-contact precision has not been independently verified. The
hitter metric evaluates top/bottom court side only. It never maps a tracker,
score slot or actor name to a durable person. All scores cover the explicitly
annotated rally windows, using current non-provisional stroke candidates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sqlite3
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

from bai_engine.schema.events import Event, current_view
from bai_engine.schema.session import Session, SessionStatus
from research.finebadminton_reference import DATASET, DATASET_REVISION, MAPPING_VERSION
from research.participant_benchmark import automatic_predictions_from_session
from research.shot_benchmark import _matches, evaluate

VERSION = "published-reference-session-v1"
NORMALIZATION = "cross_net_to_net_shot_with_cross_court_placement_v1"


def _ratio(n: int | float, d: int) -> float | None:
    return n / d if d else None


def _digest(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def _catalogue(data: Path, session_id: str) -> str:
    path = (data / "sessions.sqlite").resolve()
    with sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True) as connection:
        row = connection.execute("SELECT body FROM sessions WHERE session_id=?", (session_id,)).fetchone()
    if row is None:
        raise ValueError("unknown session")
    return row[0]


def _event_rows(data: Path, session_id: str) -> list[tuple[int, str]]:
    path = (data / "sessions" / session_id / "events.sqlite").resolve()
    with sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True) as connection:
        return connection.execute("SELECT seq,body FROM events ORDER BY seq").fetchall()


def _source_binding(labels: dict, session: Session) -> tuple[int, int]:
    if labels.get("session_id") != session.session_id or labels.get("media_sha256") != session.source.sha256:
        raise ValueError("reference source/session binding mismatch")
    for key, attribute in (
        ("fps_num", "fps_num"),
        ("fps_den", "fps_den"),
        ("media_n_frames", "n_frames"),
        ("width", "width"),
        ("height", "height"),
    ):
        value = labels.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value != getattr(session.media, attribute):
            raise ValueError(f"reference media binding mismatch: {key}")
    window = labels.get("window_frames")
    if (
        not isinstance(window, list)
        or len(window) != 2
        or any(not isinstance(value, int) or isinstance(value, bool) for value in window)
        or not 0 <= window[0] < window[1] <= session.media.n_frames
    ):
        raise ValueError("invalid reference frame window")
    rate = Fraction(session.media.fps_num, session.media.fps_den)
    if labels.get("window_s") != [float(window[0] / rate), float(window[1] / rate)]:
        raise ValueError("reference frame/time window mismatch")
    provenance, review = labels.get("reference_provenance"), labels.get("review")
    if (
        not isinstance(provenance, dict)
        or provenance.get("dataset") != DATASET
        or provenance.get("dataset_revision") != DATASET_REVISION
        or provenance.get("mapping_version") != MAPPING_VERSION
        or not isinstance(provenance.get("annotations_sha256"), str)
        or not re.fullmatch(r"[0-9a-f]{64}", provenance["annotations_sha256"])
        or provenance.get("source_media_sha256") != session.source.sha256
    ):
        raise ValueError("unsupported or inconsistent published reference provenance")
    if (
        not isinstance(review, dict)
        or review.get("origin") != "published_human_refined_reference"
        or review.get("provider_human_verified") is not True
        or review.get("our_human_reviewed") is not False
    ):
        raise ValueError("explicit provider review provenance required")
    if labels.get("split") == "held_out" and review.get("held_out_reserved_before_tuning") is not True:
        raise ValueError("held-out recording reservation required")
    for shot in labels.get("shots", []):
        frame = shot.get("frame_idx")
        if (
            not isinstance(frame, int)
            or isinstance(frame, bool)
            or not window[0] <= frame < window[1]
            or shot.get("time_s") != float(frame / rate)
        ):
            raise ValueError("reference shot frame/time mismatch")
        if shot.get("source_hitter") not in ("top", "bottom", None):
            raise ValueError("unsupported source hitter side")
    return tuple(window)


def _prediction_side(payload: dict) -> tuple[str | None, str]:
    if payload.get("classification_context_source") not in ("named_player", "provisional_track_episode"):
        return None, "unsupported_or_missing_classification_context"
    xy = payload.get("hitter_court_xy")
    if (
        not isinstance(xy, (list, tuple))
        or len(xy) != 2
        or any(
            not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) for value in xy
        )
    ):
        return None, "missing_or_nonfinite_court_position"
    if xy[1] == 0:
        return None, "court_position_on_net_plane"
    return ("top" if xy[1] > 0 else "bottom"), "supported_event_context_and_finite_court_position"


def _counts(tp: int, truth: int, predicted: int) -> dict:
    return {
        "truth_count": truth,
        "prediction_count": predicted,
        "true_positives": tp,
        "false_positives": predicted - tp,
        "false_negatives": truth - tp,
        "precision": _ratio(tp, predicted),
        "recall": _ratio(tp, truth),
        "f1": _ratio(2 * tp, truth + predicted),
    }


def _classes(reports: list[dict]) -> dict:
    counts = defaultdict(Counter)
    for report in reports:
        for family, values in report.items():
            counts[family].update({key: values[key] for key in ("support", "predicted", "true_positive")})
    result = {}
    for family, values in sorted(counts.items()):
        tp, truth, pred = values["true_positive"], values["support"], values["predicted"]
        result[family] = {
            "support": truth,
            "predicted": pred,
            "true_positive": tp,
            "precision": _ratio(tp, pred),
            "recall": _ratio(tp, truth),
            "f1": _ratio(2 * tp, truth + pred),
        }
    return result


def _court_side(result: dict, truth: list[dict], predictions: list[dict], tolerance_s: float) -> dict:
    pairs = _matches(truth, predictions, tolerance_s)
    used_pred = {j for _, j in pairs}
    attribution = result["attribution"]
    total = sum(shot.get("player_id") is not None for shot in truth)
    resolved = attribution["labelled"] - attribution["unresolved"]
    return {
        "labelled_truth": total,
        "matched_labelled_truth": attribution["labelled"],
        "unmatched_labelled_truth": total - attribution["labelled"],
        "correct": attribution["correct"],
        "wrong": resolved - attribution["correct"],
        "unresolved_matched": attribution["unresolved"],
        "resolved_matched": resolved,
        "spurious_assigned_predictions": sum(
            j not in used_pred and p.get("player_id") is not None for j, p in enumerate(predictions)
        ),
        "per_side": result["end_to_end"]["per_person"],
    }


def _aggregate(reports: list[dict]) -> dict:
    def total(key: str) -> int:
        return sum(report["contact_detection"][key] for report in reports)

    matched, truth, predicted = total("matched"), total("truth_count"), total("prediction_count")
    contacts = {
        "truth_count": truth,
        "prediction_count": predicted,
        "matched": matched,
        "false_positives": predicted - matched,
        "false_negatives": truth - matched,
        "precision": _ratio(matched, predicted),
        "recall": _ratio(matched, truth),
        "f1": _ratio(2 * matched, truth + predicted),
    }
    confusion = defaultdict(Counter)
    for report in reports:
        for actual, values in report["shot_family"]["confusion"].items():
            confusion[actual].update(values)
    classes = _classes([report["shot_family"]["per_class"] for report in reports])
    known = _classes([report["shot_family"]["known_family"]["per_class"] for report in reports])
    known_total = sum(report["shot_family"]["known_family"]["truth_support"] for report in reports)
    known_summary = {
        "truth_support": known_total,
        "per_class": known,
        "macro_f1": sum(value["f1"] for value in known.values()) / len(known) if known and known_total else None,
    }
    for key in ("excluded_unknown_truth", "excluded_predictions_on_unknown_truth"):
        known_summary[key] = sum(report["shot_family"]["known_family"][key] for report in reports)
    sides = {
        key: sum(report["court_side"][key] for report in reports)
        for key in (
            "labelled_truth",
            "matched_labelled_truth",
            "unmatched_labelled_truth",
            "correct",
            "wrong",
            "unresolved_matched",
            "resolved_matched",
            "spurious_assigned_predictions",
        )
    }
    per_side = {}
    for side in ("top", "bottom"):
        values = [report["court_side"]["per_side"].get(side, {}) for report in reports]
        per_side[side] = _counts(
            sum(value.get("true_positives", 0) for value in values),
            sum(value.get("truth_count", 0) for value in values),
            sum(value.get("prediction_count", 0) for value in values),
        )
    sides.update(
        {
            "per_side": per_side,
            "accuracy_all_labelled_truth": _ratio(sides["correct"], sides["labelled_truth"]),
            "accuracy_resolved_matched": _ratio(sides["correct"], sides["resolved_matched"]),
            "resolved_fraction_matched": _ratio(sides["resolved_matched"], sides["matched_labelled_truth"]),
        }
    )
    joint_rows = [report["joint_contact_family_court_side"] for report in reports]
    joint = _counts(
        sum(row["true_positives"] for row in joint_rows),
        sum(row["truth_count"] for row in joint_rows),
        sum(row["prediction_count"] for row in joint_rows),
    )
    for key in ("excluded_ambiguous_truth", "excluded_predictions_on_ambiguous_truth"):
        joint[key] = sum(row[key] for row in joint_rows)
    return {
        "contact_detection": contacts,
        "shot_family": {
            "per_class": classes,
            "macro_f1_including_unknown": sum(value["f1"] for value in classes.values()) / len(classes)
            if classes
            else None,
            "known_family": known_summary,
            "confusion": {key: dict(value) for key, value in confusion.items()},
            "unknown_prediction_fraction": _ratio(
                sum(report["shot_family"]["unknown_predictions"] for report in reports), predicted
            ),
        },
        "court_side": sides,
        "joint_contact_family_court_side": joint,
        "timestamp_mae_s": _ratio(
            sum((report["timestamp_mae_s"] or 0) * report["contact_detection"]["matched"] for report in reports),
            matched,
        ),
    }


def benchmark_session(
    data_dir: Path, session_id: str, annotations_dir: Path, *, tolerance_s: float = 0.2, allow_draft: bool = False
) -> dict:
    if not isinstance(session_id, str) or not session_id.isalnum():
        raise ValueError("invalid session id")
    data = data_dir.resolve()
    catalogue = _catalogue(data, session_id)
    session = Session.model_validate_json(catalogue)
    if session.session_id != session_id or session.media is None or not session.source.sha256:
        raise ValueError("session media/source binding unavailable")
    if session.status != SessionStatus.ANALYSED:
        raise ValueError("completed application analysis required before evaluation")
    annotation_paths = sorted(annotations_dir.resolve().glob("*.json"))
    if not annotation_paths:
        raise ValueError("no reference annotation JSON files")
    inputs = [(path, path.read_bytes()) for path in annotation_paths]
    references = [(path, raw, json.loads(raw)) for path, raw in inputs]
    references.sort(key=lambda item: item[2].get("window_frames", [-1])[0])
    previous_end, source_key, ids = -1, None, set()
    for _, _, labels in references:
        start, end = _source_binding(labels, session)
        if start < previous_end:
            raise ValueError("overlapping reference windows")
        previous_end = end
        if session.frontier_frame < end - 1:
            raise ValueError("reference window exceeds contiguous analysed frontier")
        provenance = labels["reference_provenance"]
        key = (
            provenance["dataset_revision"],
            provenance["annotations_sha256"],
            provenance["annotations_url"],
            labels["split"],
        )
        if source_key is not None and key != source_key:
            raise ValueError("mixed source recording, revision or split")
        source_key = key
        for shot in labels["shots"]:
            identity = shot.get("annotation_id")
            if not isinstance(identity, str) or not identity or identity in ids:
                raise ValueError("missing or duplicate source annotation id")
            ids.add(identity)
    media_dir = data / "media" / session.source.sha256
    media_paths = [media_dir / "source.mp4", media_dir / "proxy.mp4"]
    media_hashes = {str(path): _digest(path) for path in media_paths}
    if media_hashes[str(media_paths[0])] != session.source.sha256:
        raise ValueError("actual source file hash mismatch")
    rows = _event_rows(data, session_id)
    event_hash = hashlib.sha256("\n".join(body for _, body in rows).encode()).hexdigest()
    events = [Event.model_validate_json(body).with_seq(seq) for seq, body in rows]
    if any(event.session_id != session_id for event in events):
        raise ValueError("event session binding mismatch")
    live = {event.event_id: event for event in current_view(events)}
    reports = []
    for path, raw, labels in references:
        machine = automatic_predictions_from_session(data, session_id, labels)
        if machine["event_log_sha256"] != event_hash or _catalogue(data, session_id) != catalogue:
            raise ValueError("application snapshot changed during extraction")
        truth = sorted(
            [{**shot, "player_id": shot.get("source_hitter")} for shot in labels["shots"]],
            key=lambda shot: shot["time_s"],
        )
        predictions = []
        for prediction in machine["shots"]:
            event = live.get(prediction["event_id"])
            if event is None:
                raise ValueError("event snapshot changed during extraction")
            side, reason = _prediction_side(event.payload)
            family = prediction["family"]
            predictions.append(
                {
                    **prediction,
                    "original_family": family,
                    "family": "net_shot" if family == "cross_net" else family,
                    "placement": "cross_court" if family == "cross_net" else event.payload.get("placement"),
                    "player_id": side,
                    "court_side": side,
                    "court_side_reason": reason,
                    "hitter_court_xy": event.payload.get("hitter_court_xy"),
                    "classification_context_source": event.payload.get("classification_context_source"),
                }
            )
        predictions.sort(key=lambda shot: shot["time_s"])
        result = evaluate(
            {**labels, "shots": truth},
            {**machine, "shots": predictions},
            tolerance_s=tolerance_s,
            allow_draft=allow_draft,
        )
        report = {
            "annotation_file": str(path),
            "annotation_sha256": hashlib.sha256(raw).hexdigest(),
            "window_frames": labels["window_frames"],
            "window_s": labels["window_s"],
            "source_reference": labels,
            "predictions": [{key: value for key, value in shot.items() if key != "player_id"} for shot in predictions],
            "contact_detection": {
                key: result[key]
                for key in ("truth_count", "prediction_count", "matched", "false_positives", "false_negatives")
            },
            "shot_family": {key: result[key] for key in ("per_class", "known_family", "confusion")},
            "court_side": _court_side(result, truth, predictions, tolerance_s),
            "joint_contact_family_court_side": result["end_to_end"]["joint_contact_family_hitter"],
            "timestamp_mae_s": result["timestamp_mae_s"],
        }
        report["shot_family"]["unknown_predictions"] = sum(shot["family"] == "unknown" for shot in predictions)
        reports.append(report)
    if catalogue != _catalogue(data, session_id) or rows != _event_rows(data, session_id):
        raise ValueError("application snapshot changed during evaluation")
    if annotation_paths != sorted(annotations_dir.resolve().glob("*.json")) or any(
        path.read_bytes() != raw for path, raw in inputs
    ):
        raise ValueError("annotation snapshot changed during evaluation")
    if media_hashes != {str(path): _digest(path) for path in media_paths}:
        raise ValueError("media snapshot changed during evaluation")
    provider_review = all(
        labels["status"] == "reviewed" and labels["review"].get("human_verified") is True for _, _, labels in references
    )
    metric_label = f"agreement with published hit anchors at ±{tolerance_s:g} s"
    aggregate = _aggregate(reports)
    aggregate["contact_detection"]["metric_label"] = metric_label
    for report in reports:
        report["contact_detection"]["metric_label"] = metric_label
    return {
        "evaluator_version": VERSION,
        "scope": "published_singles_rally_windows_with_court_side_only",
        "session_id": session_id,
        "media_sha256": session.source.sha256,
        "tolerance_s": tolerance_s,
        "durable_person_accuracy_evaluated": False,
        "physical_contact_accuracy_claim_eligible": False,
        "metric_semantics": {
            "comparison_kind": "published_hit_anchor_agreement",
            "metric_label": metric_label,
            "reference_timestamp_field": "hitting.start_frame",
            "reference_time_conversion": "source frame / canonical media fps, without retiming",
            "matching_tolerance_s": tolerance_s,
            "matching_tolerance_frames": float(tolerance_s * session.media.fps),
            "physical_contact_frames_independently_verified": False,
            "event_population": "current_nonprovisional_machine_stroke_candidates",
            "timestamp_mae_s": "timestamp error relative to published hit anchors, not verified physical contacts",
            "court_side": "top/bottom agreement for anchor-matched events; not durable person accuracy",
        },
        "pretrained_training_overlap": "unknown",
        "published_reference_review_accepted": provider_review,
        "held_out_for_this_project": all(labels["split"] == "held_out" for _, _, labels in references),
        "general_accuracy_claim_eligible": False,
        "family_normalization": NORMALIZATION,
        "aggregate": aggregate,
        "rallies": reports,
        "provenance": {
            "catalogue_sha256": hashlib.sha256(catalogue.encode()).hexdigest(),
            "event_log_sha256": event_hash,
            "media_files": media_hashes,
            "annotation_files": [
                {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest()} for path, raw in inputs
            ],
            "published_source_json_sha256": references[0][2]["reference_provenance"]["annotations_sha256"],
            "published_reference": references[0][2]["reference_provenance"],
        },
        "limitations": [
            "Court side is not durable person identity, four-player attribution or player-name accuracy.",
            "Only annotated source rally windows are evaluated; unlabelled spans are excluded.",
            "Published hitting.start_frame anchors are external reference timestamps; "
            "their exact physical racket-contact precision and uncertainty were not independently verified.",
            "The tolerance is a declared anchor-matching criterion, not a validated physical-contact error bound.",
            "Predictions outside the half-open reference windows are excluded, including early boundary candidates.",
            "Contact detection here uses current confirmed machine stroke candidates, not all raw contact proposals.",
            "Side uses supported stored event context and finite court XY; "
            "cached pixel geometry is not independently revalidated.",
            "Provider labels include machine assistance and reported human refinement, not our own human review.",
            "Pretrained model training overlap is unknown; project reservation does not prove model-level holdout.",
            "Professional singles results do not establish amateur or four-player identity performance.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations-dir", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--session", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tolerance-s", type=float, default=0.2)
    parser.add_argument("--allow-draft", action="store_true")
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise ValueError("output already exists")
        result = benchmark_session(
            args.data_dir,
            args.session,
            args.annotations_dir,
            tolerance_s=args.tolerance_s,
            allow_draft=args.allow_draft,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as output:
            output.write(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
        print(json.dumps({"output": str(args.output.resolve()), "scope": result["scope"]}))
    except (ValueError, KeyError, TypeError, OSError, sqlite3.Error) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
