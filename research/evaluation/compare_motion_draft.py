"""Compare component hypotheses against non-exhaustive AI motion windows, not labels.

The draft intervals are review prompts, not confirmed contacts. Outputs are descriptive
and are never precision, recall, shot accuracy, or a replacement for reviewed ground truth.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _draft_inputs(draft: dict) -> tuple[str, float, list[float], list[tuple[float, float]]]:
    if (
        draft.get("schema_version") != "ai-motion-review-v1"
        or draft.get("status") != "draft"
        or draft.get("human_reviewed") is not False
        or draft.get("exhaustive") is not False
        or draft.get("evaluation_eligible") is not False
    ):
        raise ValueError("only non-exhaustive unreviewed AI drafts are supported")
    media = draft.get("media")
    if not isinstance(media, dict):
        raise ValueError("draft media is missing")
    sha = media.get("sha256")
    num, den = media.get("fps_num"), media.get("fps_den")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
        raise ValueError("draft requires a source SHA-256")
    if not _finite(num) or not _finite(den) or num <= 0 or den <= 0:
        raise ValueError("draft requires a valid frame rate")
    fps = num / den
    window = draft.get("review_window_s")
    if (
        not isinstance(window, list)
        or len(window) != 2
        or not all(map(_finite, window))
        or not 0 <= window[0] < window[1]
    ):
        raise ValueError("invalid draft review window")
    motion = draft.get("candidate_motion_windows")
    if not isinstance(motion, list) or not motion:
        raise ValueError("draft motion windows are missing")
    windows = []
    for row in motion:
        if not isinstance(row, dict) or row.get("contact_confirmed") is not False:
            raise ValueError("motion windows cannot be confirmed contacts")
        t = row.get("time_range_s")
        if (
            not isinstance(t, list)
            or len(t) != 2
            or not all(map(_finite, t))
            or not window[0] <= t[0] <= t[1] <= window[1]
        ):
            raise ValueError("invalid motion window")
        windows.append((t[0], t[1]))
    return sha, fps, window, windows


def _describe_probe(probe: dict, sha: str, fps: float, window: list[float], ranges: list[tuple[float, float]]) -> dict:
    frames = probe.get("source_frames")
    for key, required in (
        ("model_sha256", {"tracknet", "detector", "pose"}),
        ("implementation_sha256", {"diagnostic", "contact", "stroke"}),
    ):
        hashes = probe.get(key)
        if (
            not isinstance(hashes, dict)
            or not required.issubset(hashes)
            or any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value) for value in hashes.values())
        ):
            raise ValueError(f"probe {key} provenance is missing or invalid")
    if probe.get("source_video_sha256") != sha:
        raise ValueError("probe source digest differs from draft")
    if not _finite(probe.get("fps")) or not math.isclose(probe["fps"], fps, rel_tol=0, abs_tol=1e-8):
        raise ValueError("probe frame rate differs from draft")
    if (
        not isinstance(frames, list)
        or len(frames) != 2
        or any(not isinstance(f, int) or isinstance(f, bool) for f in frames)
        or frames[0] < 0
        or frames[1] < frames[0]
        or not math.isclose(frames[0] / fps, window[0], rel_tol=0, abs_tol=1e-6)
        or not math.isclose((frames[1] + 1) / fps, window[1], rel_tol=0, abs_tol=1e-6)
    ):
        raise ValueError("probe coverage differs from draft review window")
    rows = probe.get("contact_candidates")
    if not isinstance(rows, list):
        raise ValueError("probe contact candidates missing")
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("invalid contact candidate")
        f, t, family = row.get("frame"), row.get("t_s"), row.get("shot_family")
        if (
            not isinstance(f, int)
            or isinstance(f, bool)
            or f in seen
            or not frames[0] <= f <= frames[1]
            or not _finite(t)
            or not math.isclose(t, f / fps, rel_tol=0, abs_tol=1e-6)
            or not isinstance(family, str)
            or not family
        ):
            raise ValueError("invalid, duplicate or out-of-window contact candidate")
        seen.add(f)
    rows = sorted(rows, key=lambda row: row["frame"])
    return {
        "hypothesis_count": len(rows),
        "unknown_family_count": sum(row["shot_family"] == "unknown" for row in rows),
        "hypotheses_in_windows": [[row["frame"] for row in rows if a <= row["t_s"] <= b] for a, b in ranges],
        "hypotheses_outside_windows": [
            row["frame"] for row in rows if not any(a <= row["t_s"] <= b for a, b in ranges)
        ],
        "implementation": probe.get("implementation_sha256"),
        "model_sha256": probe.get("model_sha256"),
    }


def compare_draft(draft: dict, before: dict, after: dict | None = None) -> dict:
    sha, fps, window, ranges = _draft_inputs(draft)
    before_result = _describe_probe(before, sha, fps, window, ranges)
    after_result = _describe_probe(after, sha, fps, window, ranges) if after is not None else None
    if after is not None and before.get("model_sha256") != after.get("model_sha256"):
        raise ValueError("probe model hashes differ; comparison would confound model changes")
    return {
        "version": "motion-window-diagnostic-v1",
        "accuracy_claim_eligible": False,
        "review_exhaustive": False,
        "note": "AI motion windows are unconfirmed and incomplete; outside-window hypotheses are not false positives.",
        "source_video_sha256": sha,
        "fps": fps,
        "review_window_s": window,
        "motion_windows_s": ranges,
        "before": before_result,
        "after": after_result,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--draft", type=Path, required=True)
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path)
    args = parser.parse_args()
    try:
        draft = json.loads(args.draft.read_text(encoding="utf-8"))
        before = json.loads(args.before.read_text(encoding="utf-8"))
        after = json.loads(args.after.read_text(encoding="utf-8")) if args.after else None
        result = compare_draft(draft, before, after)
        if file_sha256(args.video) != result["source_video_sha256"]:
            raise ValueError("provided video bytes do not match the draft source")
        result["provenance"] = {
            "draft_sha256": file_sha256(args.draft),
            "before_sha256": file_sha256(args.before),
            "after_sha256": file_sha256(args.after) if args.after else None,
            "video_sha256_verified": True,
        }
        print(json.dumps(result, indent=2, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
