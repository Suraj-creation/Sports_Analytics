"""Read-only, source-bound shot evaluation. See shot-annotation-protocol.md."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

from bai_engine.schema.events import Event, EventStatus, current_view
from bai_engine.schema.session import Session

VERSION = "shot-benchmark-v1"
MISSED, SPURIOUS = "__missed__", "__spurious__"


def _ratio(n: int, d: int) -> float | None:
    return n / d if d else None


def validate_inputs(labels: dict, predictions: dict, *, allow_draft: bool = False) -> None:
    for name, doc in (("labels", labels), ("predictions", predictions)):
        if doc.get("schema_version") != 1:
            raise ValueError(f"{name}: unsupported schema version")
        if not isinstance(doc.get("session_id"), str) or not doc["session_id"]:
            raise ValueError(f"{name}: session id required")
        sha = doc.get("media_sha256")
        if not isinstance(sha, str) or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
            raise ValueError(f"{name}: valid lowercase media hash required")
        if doc.get("timebase") != "canonical_media_seconds":
            raise ValueError(f"{name}: canonical media timebase required")
        window = doc.get("window_s")
        if (
            not isinstance(window, list)
            or len(window) != 2
            or any(not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v) for v in window)
            or window[0] < 0
            or window[0] >= window[1]
        ):
            raise ValueError(f"{name}: invalid window")
        if not isinstance(doc.get("shots"), list):
            raise ValueError(f"{name}: shots must be a list")
        ids = set()
        for row in doc["shots"]:
            if not isinstance(row, dict):
                raise ValueError(f"{name}: invalid shot")
            t, family = row.get("time_s"), row.get("family")
            if (
                not isinstance(t, (int, float))
                or isinstance(t, bool)
                or not math.isfinite(t)
                or not window[0] <= t < window[1]
            ):
                raise ValueError(f"{name}: shot outside window")
            if not isinstance(family, str) or not family or family in (MISSED, SPURIOUS):
                raise ValueError(f"{name}: invalid family")
            if row.get("player_id") is not None and (not isinstance(row["player_id"], str) or not row["player_id"]):
                raise ValueError(f"{name}: invalid player identity")
            if name == "predictions":
                eid = row.get("event_id")
                if not isinstance(eid, str) or not eid or eid in ids:
                    raise ValueError("predictions: missing or duplicate event id")
                ids.add(eid)
    for key in ("session_id", "media_sha256", "timebase", "window_s"):
        if labels[key] != predictions[key]:
            raise ValueError(f"{key}: labels and predictions differ")
    if labels.get("exhaustive") is not True:
        raise ValueError("labels must exhaustively cover the window")
    if labels.get("split") not in ("held_out", "development", "diagnostic"):
        raise ValueError("explicit split required")
    if labels.get("status") not in ("reviewed", "draft"):
        raise ValueError("status must be reviewed or draft")
    if labels["status"] == "draft" and not allow_draft:
        raise ValueError("reviewed labels required; draft requires explicit opt-in")
    review = labels.get("review")
    if labels["status"] == "reviewed" and (not isinstance(review, dict) or review.get("human_verified") is not True):
        raise ValueError("reviewed labels require human verification")


def _matches(gt: list[dict], pred: list[dict], tolerance_s: float) -> list[tuple[int, int]]:
    # Chronological matching, maximizing cardinality and then minimizing total absolute timing error.
    n, m = len(gt), len(pred)
    score = [[(0, 0.0)] * (m + 1) for _ in range(n + 1)]
    action = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            best, choice = score[i - 1][j], 1
            if score[i][j - 1] > best:
                best, choice = score[i][j - 1], 2
            error = abs(gt[i - 1]["time_s"] - pred[j - 1]["time_s"])
            if error <= tolerance_s + 1e-12:
                old = score[i - 1][j - 1]
                candidate = (old[0] + 1, old[1] - error)
                if candidate >= best:
                    best, choice = candidate, 3
            score[i][j], action[i][j] = best, choice
    i, j, pairs = n, m, []
    while i and j:
        choice = action[i][j]
        if choice == 3:
            pairs.append((i - 1, j - 1))
            i, j = i - 1, j - 1
        elif choice == 1:
            i -= 1
        else:
            j -= 1
    return list(reversed(pairs))


def evaluate(labels: dict, predictions: dict, *, tolerance_s: float = 0.2, allow_draft: bool = False) -> dict:
    validate_inputs(labels, predictions, allow_draft=allow_draft)
    if not math.isfinite(tolerance_s) or tolerance_s < 0:
        raise ValueError("tolerance must be finite and nonnegative")
    gt = sorted(labels["shots"], key=lambda r: r["time_s"])
    pred = sorted(predictions["shots"], key=lambda r: r["time_s"])
    pairs = _matches(gt, pred, tolerance_s)
    used_g, used_p = {i for i, _ in pairs}, {j for _, j in pairs}
    confusion: dict[str, Counter] = defaultdict(Counter)
    for i, j in pairs:
        confusion[gt[i]["family"]][pred[j]["family"]] += 1
    for i, row in enumerate(gt):
        if i not in used_g:
            confusion[row["family"]][MISSED] += 1
    for j, row in enumerate(pred):
        if j not in used_p:
            confusion[SPURIOUS][row["family"]] += 1
    classes = sorted({r["family"] for r in gt + pred})
    metrics = {}
    for c in classes:
        tp = confusion[c][c]
        truth_count = sum(r["family"] == c for r in gt)
        pred_count = sum(r["family"] == c for r in pred)
        precision, recall = _ratio(tp, pred_count), _ratio(tp, truth_count)
        f1 = _ratio(2 * tp, truth_count + pred_count)
        metrics[c] = {
            "support": truth_count,
            "predicted": pred_count,
            "true_positive": tp,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }
    labelled = [(gt[i], pred[j]) for i, j in pairs if gt[i].get("player_id") is not None]
    correct = sum(a["player_id"] == b.get("player_id") for a, b in labelled)
    resolved = sum(b.get("player_id") is not None for _, b in labelled)
    errors = [abs(gt[i]["time_s"] - pred[j]["time_s"]) for i, j in pairs]
    return {
        "evaluator_version": VERSION,
        "accuracy_claim_eligible": labels["status"] == "reviewed" and labels["split"] == "held_out",
        "session_id": labels["session_id"],
        "media_sha256": labels["media_sha256"],
        "window_s": labels["window_s"],
        "status": labels["status"],
        "split": labels["split"],
        "tolerance_s": tolerance_s,
        "truth_count": len(gt),
        "prediction_count": len(pred),
        "matched": len(pairs),
        "false_positives": len(pred) - len(pairs),
        "false_negatives": len(gt) - len(pairs),
        "detection_precision": _ratio(len(pairs), len(pred)),
        "detection_recall": _ratio(len(pairs), len(gt)),
        "per_class": metrics,
        "macro_f1": sum(m["f1"] for m in metrics.values()) / len(metrics) if metrics else None,
        "confusion": {k: dict(v) for k, v in confusion.items()},
        "unknown_prediction_fraction": _ratio(sum(r["family"] == "unknown" for r in pred), len(pred)),
        "attribution": {
            "labelled": len(labelled),
            "correct": correct,
            "unresolved": len(labelled) - resolved,
            "accuracy_all_labelled": _ratio(correct, len(labelled)),
            "accuracy_resolved": _ratio(correct, resolved),
        },
        "timestamp_mae_s": sum(errors) / len(errors) if errors else None,
        "matches": [
            {"truth_time_s": gt[i]["time_s"], "event_id": pred[j]["event_id"], "prediction_time_s": pred[j]["time_s"]}
            for i, j in pairs
        ],
    }


def predictions_from_session(data_dir: Path, session_id: str, labels: dict) -> dict:
    if not session_id.isalnum():
        raise ValueError("invalid session id")
    path = (data_dir / "sessions.sqlite").resolve()
    with sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True) as conn:
        row = conn.execute("SELECT body FROM sessions WHERE session_id=?", (session_id,)).fetchone()
    if row is None:
        raise ValueError("unknown session")
    session = Session.model_validate_json(row[0])
    if (
        session.media is None
        or session.source.sha256 != labels.get("media_sha256")
        or session.session_id != labels.get("session_id")
    ):
        raise ValueError("session or media binding mismatch")
    window = labels.get("window_s")
    if (
        not isinstance(window, list)
        or len(window) != 2
        or window[1] > session.media.n_frames / session.media.fps + 1e-6
    ):
        raise ValueError("window exceeds media")
    event_path = (data_dir / "sessions" / session_id / "events.sqlite").resolve()
    with sqlite3.connect(f"{event_path.as_uri()}?mode=ro", uri=True) as conn:
        rows = conn.execute("SELECT seq,body FROM events ORDER BY seq").fetchall()
    live = current_view([Event.model_validate_json(body).with_seq(seq) for seq, body in rows])
    shots = [
        {
            "time_s": float(event.frame_start / session.media.fps),
            "family": event.payload.get("stroke", "unknown"),
            "player_id": event.actors.player_id,
            "event_id": event.event_id,
            "confidence": event.confidence,
        }
        for event in live
        if event.type == "stroke"
        and event.status != EventStatus.PROVISIONAL
        and window[0] <= event.frame_start / session.media.fps < window[1]
    ]
    return {
        "schema_version": 1,
        "session_id": session_id,
        "media_sha256": session.source.sha256,
        "timebase": "canonical_media_seconds",
        "window_s": window,
        "shots": shots,
        "event_log_sha256": hashlib.sha256("\n".join(body for _, body in rows).encode()).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", required=True)
    parser.add_argument("--annotations", required=True, type=Path)
    parser.add_argument("--data-dir", default=Path("data"), type=Path)
    parser.add_argument("--tolerance-s", default=0.2, type=float)
    parser.add_argument("--allow-draft", action="store_true")
    args = parser.parse_args()
    try:
        raw = args.annotations.read_bytes()
        labels = json.loads(raw)
        predictions = predictions_from_session(args.data_dir, args.session, labels)
        result = evaluate(labels, predictions, tolerance_s=args.tolerance_s, allow_draft=args.allow_draft)
        result["provenance"] = {
            "annotations_sha256": hashlib.sha256(raw).hexdigest(),
            "event_log_sha256": predictions["event_log_sha256"],
        }
        print(json.dumps(result, indent=2, allow_nan=False))
    except (ValueError, KeyError, TypeError, OSError, sqlite3.Error) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
