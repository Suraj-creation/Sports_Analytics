"""Read-only source-bound rally evaluation; JSON to stdout, never overwrites results.

Run from repository root after sourcing ../gpu-env.sh:
  .venv/bin/python research/evaluate_session.py --session ID --annotations labels.json
The annotation window must be exhaustively reviewed. Draft labels are rejected
unless --allow-draft is explicit; their reports cannot count as accuracy claims.
Reviewed labels must include a human-verification attestation. This is a statement
by the annotator, not independent proof of annotation quality or split isolation.
Schema v1 covers one exhaustive window. Unsupported partial-review or uncertain
existence fields are rejected; use separate exhaustive windows until a versioned
coverage extension is available. A null winner leaves the rally's outcome unknown
without making its existence unknown. The CLI verifies stored source/proxy bytes;
legacy annotations without a proxy digest remain explicitly proxy-unbound.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sqlite3
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from bai_engine.evaluation import Interval, evaluate_intervals
from bai_engine.schema.events import Event, EventStatus, current_view
from bai_engine.schema.session import Session
from bai_engine.store.sessions import MediaPaths

_ANNOTATION_FIELDS = frozenset(
    {
        "schema_version", "media_sha256", "timebase", "status", "split", "population", "exhaustive",
        "window_s", "rallies", "review", "boundary_uncertainty_s", "notes", "provenance",
        "session_id", "fps_num", "fps_den", "n_frames", "proxy_sha256",
    }
)
_RALLY_FIELDS = frozenset({"start_s", "end_s", "winner", "notes", "provenance", "boundary_uncertainty_s"})


def _hash(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _finite(value: object) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _winner(value: object) -> str | None:
    if value is not None and (not isinstance(value, str) or value not in ("P1", "P2")):
        raise ValueError("winner must be P1, P2 or null; null means unknown outcome")
    return value


def load_annotations(
    path: Path, session: Session, *, allow_draft: bool = False, raw_bytes: bytes | None = None
) -> dict:
    """Validate v1 labels; optional raw bytes let the CLI retain one parsed snapshot."""
    labels = json.loads(path.read_bytes() if raw_bytes is None else raw_bytes)
    if not isinstance(labels, dict):
        raise ValueError("annotation manifest must be a JSON object")
    extra = labels.keys() - _ANNOTATION_FIELDS
    if extra:
        raise ValueError(f"unsupported annotation fields in schema v1: {', '.join(sorted(extra))}")
    version = labels.get("schema_version")
    if isinstance(version, bool) or not isinstance(version, int) or version != 1:
        raise ValueError("unsupported annotation schema_version")
    if not _hash(labels.get("media_sha256")) or labels["media_sha256"] != session.source.sha256:
        raise ValueError("annotation media hash does not match session source")
    if labels.get("timebase") != "canonical_media_seconds":
        raise ValueError("annotations require canonical_media_seconds")
    if labels.get("status") not in ("reviewed", "draft"):
        raise ValueError("status must be reviewed or draft")
    if labels["status"] == "draft" and not allow_draft:
        raise ValueError("draft annotations require explicit --allow-draft; no accuracy claim permitted")
    review = labels.get("review")
    if labels["status"] == "reviewed" and (
        not isinstance(review, dict) or review.get("human_verified") is not True
    ):
        raise ValueError("reviewed labels require human verification")
    if labels.get("split") not in ("held_out", "development", "diagnostic"):
        raise ValueError("explicit evaluation split required")
    if labels.get("population") not in ("official_rallies", "all_exchanges"):
        raise ValueError("explicit event population required")
    if labels.get("exhaustive") is not True:
        raise ValueError("annotation window must exhaustively label the chosen population")
    bounds = labels.get("window_s")
    if not isinstance(bounds, list) or len(bounds) != 2 or not all(_finite(value) for value in bounds):
        raise ValueError("window_s must contain exactly two finite nonboolean numbers")
    window = Interval(*bounds)
    media = session.media
    if media is None or window.end_s > float(media.n_frames / media.fps) + 1e-6:
        raise ValueError("annotation window exceeds canonical media")
    if "session_id" in labels and (
        not isinstance(labels["session_id"], str) or labels["session_id"] != session.session_id
    ):
        raise ValueError("annotation session_id binding mismatch")
    for key in ("fps_num", "fps_den", "n_frames"):
        if key in labels and (
            isinstance(labels[key], bool) or not isinstance(labels[key], int) or labels[key] != getattr(media, key)
        ):
            raise ValueError(f"annotation {key} binding mismatch")
    if "proxy_sha256" in labels and not _hash(labels["proxy_sha256"]):
        raise ValueError("annotation proxy_sha256 must be a lowercase SHA-256 digest")
    rallies = labels.get("rallies")
    if not isinstance(rallies, list):
        raise ValueError("rallies must be a list")
    for row in rallies:
        if not isinstance(row, dict):
            raise ValueError("rally row must be a JSON object")
        extra = row.keys() - _RALLY_FIELDS
        if extra:
            raise ValueError(f"unsupported rally fields in schema v1: {', '.join(sorted(extra))}")
        if not _finite(row.get("start_s")) or not _finite(row.get("end_s")):
            raise ValueError("rally boundaries must be finite nonboolean numbers")
        interval = Interval(row["start_s"], row["end_s"], _winner(row.get("winner")))
        if interval.start_s < window.start_s or interval.end_s > window.end_s:
            raise ValueError("annotation lies outside reviewed window")
    return labels


def _file_sha256(path: Path, role: str) -> str:
    try:
        with path.open("rb") as stream:
            return hashlib.file_digest(stream, "sha256").hexdigest()
    except OSError as exc:
        raise ValueError(f"{role} media file is unavailable: {exc}") from exc


def verify_media_binding(data_dir: Path, session: Session, labels: dict) -> dict:
    """Verify actual bytes, without decoding or claiming independent annotation review.

    Use the catalogue's source URI or an unambiguous content-addressed source file
    after relocation. Source containers may have any stored extension. Hashing is
    streamed; the caller should evaluate an immutable session/media snapshot.
    """
    source_hash = session.source.sha256
    if not _hash(source_hash) or labels.get("media_sha256") != source_hash:
        raise ValueError("source media hash binding mismatch")
    paths = MediaPaths(data_dir.resolve() / "media" / source_hash)
    source_path = Path(session.source.uri)
    if not source_path.is_file():
        candidates = sorted(path for path in paths.root.glob("source.*") if path.is_file())
        if len(candidates) != 1:
            raise ValueError("source media file is missing or ambiguous")
        source_path = candidates[0]
    actual_source = _file_sha256(source_path, "source")
    if actual_source != source_hash:
        raise ValueError("source media hash mismatch")
    actual_proxy = _file_sha256(paths.proxy, "proxy")
    proxy_bound = "proxy_sha256" in labels
    if proxy_bound and (not _hash(labels["proxy_sha256"]) or labels["proxy_sha256"] != actual_proxy):
        raise ValueError("proxy media hash mismatch")
    return {
        "source_sha256": actual_source,
        "proxy_sha256": actual_proxy,
        "proxy_label_bound": proxy_bound,
    }


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
        annotation_bytes = args.annotations.read_bytes()
        labels = load_annotations(args.annotations, session, allow_draft=args.allow_draft, raw_bytes=annotation_bytes)
        media_verification = verify_media_binding(args.data_dir, session, labels)
    except (OSError, ValueError, KeyError, TypeError) as exc:
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
        try:
            winner = _winner(event.payload.get("winner"))
        except ValueError as exc:
            parser.error(f"prediction {event.event_id}: {exc}")
        predictions.append(Interval(float(max(start, a)), float(min(end, b)), winner))
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
        "n_frames": session.media.n_frames,
        "window_s": labels["window_s"],
        "population": labels["population"],
        "annotation_sha256": hashlib.sha256(annotation_bytes).hexdigest(),
        "annotation_status": labels["status"],
        "split": labels["split"],
        "review": labels.get("review"),
        "boundary_uncertainty_s": labels.get("boundary_uncertainty_s"),
        "media_verification": media_verification,
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
