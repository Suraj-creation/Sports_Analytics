"""Validate a source-bound reviewer CSV without writing to sessions or inventing labels.

A complete CSV is still reviewer-provided evidence, not verified accuracy.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

ACTIVITIES = {
    "rally",
    "between_rallies",
    "warmup",
    "casual_practice",
    "break_or_rest",
    "conversation_or_inactive",
    "court_setup",
    "unknown",
}
MATCH_STATES = {"match", "non_match", "unknown"}


def _number(value: object) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("timestamps must be finite numeric seconds") from exc
    if not result.is_finite():
        raise ValueError("timestamps must be finite numeric seconds")
    return result


def validate_review(csv_path: Path, manifest_path: Path) -> dict:
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("timebase") != "canonical_media_seconds":
        raise ValueError("unsupported manifest schema or timebase")
    expected = {}
    for item in manifest.get("clips", []):
        name, sid, digest = item.get("clip"), item.get("session_id"), item.get("media_sha256")
        if (
            not isinstance(name, str)
            or Path(name).name != name
            or name in expected
            or not isinstance(sid, str)
            or not sid.isalnum()
            or not isinstance(digest, str)
            or re.fullmatch(r"[0-9a-f]{64}", digest) is None
        ):
            raise ValueError("invalid or duplicate clip identity in manifest")
        start, end = _number(item.get("canonical_start_s")), _number(item.get("canonical_end_s"))
        if start < 0 or end <= start:
            raise ValueError("invalid source window")
        expected[name] = (sid, digest, start, end)
    if not expected:
        raise ValueError("manifest contains no clips")
    grouped = defaultdict(list)
    with Path(csv_path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {
            "clip",
            "session_id",
            "media_sha256",
            "canonical_start_s",
            "canonical_end_s",
            "clip_start_s",
            "clip_end_s",
            "activity",
            "match_status",
            "reviewer",
        }
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("review CSV is missing required columns")
        for row in reader:
            name = row.get("clip", "").strip()
            if name not in expected:
                raise ValueError("review contains unknown clip")
            sid, digest, origin, end = expected[name]
            if (
                row.get("session_id", "").strip() != sid
                or row.get("media_sha256", "").strip() != digest
                or _number(row.get("canonical_start_s")) != origin
                or _number(row.get("canonical_end_s")) != end
            ):
                raise ValueError("review source does not match manifest")
            a, b = _number(row.get("clip_start_s")), _number(row.get("clip_end_s"))
            activity, match = row.get("activity", "").strip().lower(), row.get("match_status", "").strip().lower()
            reviewer = row.get("reviewer", "").strip()
            if (
                a < 0
                or b <= a
                or b > end - origin
                or activity not in ACTIVITIES
                or match not in MATCH_STATES
                or not reviewer
            ):
                raise ValueError("invalid or incomplete review interval")
            grouped[name].append(
                (
                    a,
                    b,
                    activity,
                    match,
                    reviewer,
                    row.get("participant_changes", "").strip(),
                    row.get("notes", "").strip(),
                )
            )
    out = []
    for name, (sid, digest, origin, end) in expected.items():
        rows = sorted(grouped[name], key=lambda row: row[0])
        cursor = Decimal(0)
        intervals = []
        for a, b, activity, match, reviewer, changes, notes in rows:
            if a != cursor:
                raise ValueError("review intervals must cover the entire clip without gaps or overlaps")
            intervals.append(
                {
                    "canonical_start_s": float(origin + a),
                    "canonical_end_s": float(origin + b),
                    "activity": activity,
                    "match_status": match,
                    "reviewer": reviewer,
                    "participant_changes": changes,
                    "notes": notes,
                }
            )
            cursor = b
        if cursor != end - origin:
            raise ValueError("review intervals do not cover the entire clip")
        out.append({"clip": name, "session_id": sid, "media_sha256": digest, "intervals": intervals})
    return {
        "status": "reviewer_provided",
        "timebase": "canonical_media_seconds",
        "clips": out,
        "note": "Completeness is validated; reviewer identity and label correctness are not verified.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = validate_review(args.csv, args.manifest)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
