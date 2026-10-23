"""Read-only source-bound rally evaluation; JSON to stdout, never overwrites results.

Run from repository root after sourcing ../gpu-env.sh:
  .venv/bin/python research/evaluate_session.py --session ID --annotations labels.json
The annotation window must be exhaustively reviewed. Draft labels are rejected
unless --allow-draft is explicit; their reports cannot count as accuracy claims.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from bai_engine.evaluation import Interval, evaluate_intervals
from bai_engine.schema.events import Event, EventStatus, current_view
from bai_engine.schema.session import Session


def load_annotations(path: Path, session: Session, *, allow_draft: bool = False) -> dict:
    labels = json.loads(path.read_text())
    if labels.get("schema_version") != 1:
        raise ValueError("unsupported annotation schema_version")
    if labels.get("media_sha256") != session.source.sha256 or not session.source.sha256:
        raise ValueError("annotation media hash does not match session source")
    if labels.get("timebase") != "canonical_media_seconds":
        raise ValueError("annotations require canonical_media_seconds")
    if labels.get("status") != "reviewed" and not allow_draft:
        raise ValueError("draft annotations require explicit --allow-draft; no accuracy claim permitted")
    if labels.get("split") not in ("held_out", "development", "diagnostic"):
        raise ValueError("explicit evaluation split required")
    if labels.get("population") not in ("official_rallies", "all_exchanges"):
        raise ValueError("explicit event population required")
    if labels.get("exhaustive") is not True:
        raise ValueError("annotation window must exhaustively label the chosen population")
    window = Interval(*labels["window_s"])
    if session.media is None or window.end_s > float(session.media.n_frames / session.media.fps) + 1e-6:
        raise ValueError("annotation window exceeds canonical media")
    for row in labels["rallies"]:
        interval = Interval(row["start_s"], row["end_s"], row.get("winner"))
        if interval.start_s < window.start_s or interval.end_s > window.end_s:
            raise ValueError("annotation lies outside reviewed window")
    return labels


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--session", required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--min-iou", type=float, default=0.2)
    parser.add_argument("--boundary-tolerance-s", type=float, default=1.0)
    parser.add_argument("--allow-draft", action="store_true")
    args = parser.parse_args()
    if not args.session.isalnum():
        parser.error("invalid session id")
    catalogue = (args.data_dir / "sessions.sqlite").resolve()
    with sqlite3.connect(f"{catalogue.as_uri()}?mode=ro", uri=True) as connection:
        row = connection.execute("SELECT body FROM sessions WHERE session_id=?", (args.session,)).fetchone()
    if row is None:
        parser.error("unknown session")
    session = Session.model_validate_json(row[0])
    try:
        labels = load_annotations(args.annotations, session, allow_draft=args.allow_draft)
    except (ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    assert session.media is not None
    event_path = (args.data_dir / "sessions" / args.session / "events.sqlite").resolve()
    with sqlite3.connect(f"{event_path.as_uri()}?mode=ro", uri=True) as connection:
        rows = connection.execute("SELECT seq,body FROM events ORDER BY seq").fetchall()
    raw = [Event.model_validate_json(body).with_seq(seq) for seq, body in rows]
    live = current_view(raw)
    start, end = labels["window_s"]
    fps = session.media.fps
    predictions, ids = [], []
    for event in live:
        if event.type != "rally_end" or event.status == EventStatus.PROVISIONAL:
            continue
        if labels["population"] == "official_rallies" and event.payload.get("official") is not True:
            continue
        # Event frame_end is inclusive; evaluation intervals are half-open.
        a, b = event.frame_start / fps, (event.frame_end + 1) / fps
        if b <= start or a >= end:
            continue
        predictions.append(Interval(float(max(start, a)), float(min(end, b)), event.payload.get("winner")))
        ids.append(event.event_id)
    truth = [Interval(item["start_s"], item["end_s"], item.get("winner")) for item in labels["rallies"]]
    result = evaluate_intervals(
        truth, predictions, min_iou=args.min_iou, boundary_tolerance_s=args.boundary_tolerance_s
    )
    result["provenance"] = {
        "session_id": session.session_id,
        "media_sha256": session.source.sha256,
        "fps_num": session.media.fps_num,
        "fps_den": session.media.fps_den,
        "window_s": labels["window_s"],
        "population": labels["population"],
        "annotation_sha256": hashlib.sha256(args.annotations.read_bytes()).hexdigest(),
        "annotation_status": labels["status"],
        "split": labels["split"],
        "review": labels.get("review"),
        "boundary_uncertainty_s": labels.get("boundary_uncertainty_s"),
        "accuracy_claim_eligible": labels["status"] == "reviewed" and labels["split"] == "held_out",
        "event_log_sha256": hashlib.sha256("\n".join(e.model_dump_json() for e in raw).encode()).hexdigest(),
        "event_log_last_seq": rows[-1][0] if rows else 0,
        "prediction_event_ids": ids,
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "git_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], text=True)),
        "timestamp_utc": datetime.now(UTC).isoformat(),
    }
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
