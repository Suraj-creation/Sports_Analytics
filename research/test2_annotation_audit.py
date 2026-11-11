"""Immutable offline annotation audit and explicit optional coarse conversion.

Neither filename nor seven-column precision establishes independent annotation
provenance. This audit reports compatibility, never a verified match identity.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.benchmarking.evaluate_rallies import SCHEMA, human_time, read_csv, write_predictions  # noqa: E402

COARSE_SCHEMA = [
    "start_time",
    "end_time",
    "win_point_player",
    "win_reason",
    "ball_types",
    "lose_reason",
    "roundscore_A",
    "roundscore_B",
]


def seconds(value: str) -> Fraction:
    """Parse seconds/MM:SS/HH:MM:SS without fitting an offset or frame base."""
    parts = value.strip().split(":")
    if not 1 <= len(parts) <= 3 or any(not part.strip() for part in parts):
        raise ValueError("invalid coarse timestamp")
    values = [Fraction(part) for part in parts]
    if any(part < 0 for part in values) or any(part >= 60 for part in values[1:]):
        raise ValueError("negative timestamp or noncanonical clock field")
    if any(value.denominator != 1 for value in values[:-1]):
        raise ValueError("fractional clock prefix")
    return sum((value * 60 ** (len(values) - index - 1) for index, value in enumerate(values)), Fraction(0))


def inventory(intervals: list[dict], frame_count: int) -> dict:
    duplicates, overlaps, out_of_range, out_of_order = [], [], [], []
    seen = {}
    for index, row in enumerate(intervals):
        start, end, number = row["start_frame"], row["end_frame"], row["csv_row"]
        key = start, end
        if key in seen:
            duplicates.append([seen[key], number])
        seen.setdefault(key, number)
        if not 0 <= start < end <= frame_count:
            out_of_range.append(number)
        if index and start < intervals[index - 1]["start_frame"]:
            out_of_order.append(number)
        for previous in intervals[:index]:
            if min(end, previous["end_frame"]) > max(start, previous["start_frame"]):
                overlaps.append([previous["csv_row"], number])
    return {
        "duplicate_interval_csv_row_pairs": duplicates,
        "positive_overlap_csv_row_pairs": overlaps,
        "out_of_range_csv_rows": out_of_range,
        "out_of_order_csv_rows": out_of_order,
    }


def audit(path: Path, fps: Fraction, frame_count: int) -> dict:
    if fps <= 0 or type(frame_count) is not int or frame_count <= 0:
        raise ValueError("positive source rate and frame count required")
    original = path.read_bytes()
    rows_reader = csv.DictReader(io.StringIO(original.decode("utf-8-sig")))
    columns, rows = rows_reader.fieldnames, list(rows_reader)
    schema = (
        "seven-column-rally" if columns == SCHEMA else "coarse-legacy" if columns == COARSE_SCHEMA else "unsupported"
    )
    result = {
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(original).hexdigest(),
        "bytes": len(original),
        "columns": columns,
        "schema": schema,
        "csv_data_rows": len(rows),
        "fps": str(fps),
        "video_frame_count": frame_count,
        "video_duration_seconds": float(Fraction(frame_count, 1) / fps),
        "fully_blank_csv_rows": [],
        "missing_field_csv_rows": [],
        "malformed_rows": [],
        "intervals": [],
        "raw_rows": [],
        "independently_reviewed_ground_truth_established": False,
        "match_identity_verified": False,
        "provenance_limit": (
            "Existing project audit identifies _rally.csv as generated proposals unless separately reviewed. "
            "Coarse primary files have legacy manual-label claims but no source-bound independent review ledger."
        ),
    }
    for csv_row, row in enumerate(rows, 2):
        result["raw_rows"].append({"csv_row": csv_row, "values": row})
        if all(value in (None, "") for key, value in row.items() if key is not None):
            result["fully_blank_csv_rows"].append(csv_row)
        if None in row or any(value is None or value == "" for value in row.values()):
            result["missing_field_csv_rows"].append(csv_row)
        try:
            if schema == "seven-column-rally":
                if None in row or any(value is None or value == "" for value in row.values()):
                    raise ValueError("missing or extra seven-column values")
                start_frame, end_frame = int(row[SCHEMA[0]]), int(row[SCHEMA[1]])
                start, end, duration = (float(row[key]) for key in SCHEMA[2:5])
                if not all(math.isfinite(value) for value in (start, end, duration)):
                    raise ValueError("nonfinite timestamp/duration")
                if not 0 <= start_frame < end_frame or not 0 <= start < end:
                    raise ValueError("nonpositive or negative interval")
                if (
                    max(
                        abs(start - start_frame / float(fps)),
                        abs(end - end_frame / float(fps)),
                        abs(duration - (end - start)),
                    )
                    > 1e-6
                ):
                    raise ValueError("frame/time/duration inconsistent with zero-origin source rate")
                if [row[key] for key in SCHEMA[5:]] != [human_time(start), human_time(end)]:
                    raise ValueError("MM:SS display does not truncate exact seconds")
            elif schema == "coarse-legacy":
                if None in row or row.get("start_time") in (None, "") or row.get("end_time") in (None, ""):
                    raise ValueError("missing or extra coarse interval values")
                start, end = seconds(row["start_time"]), seconds(row["end_time"])
                if not 0 <= start < end:
                    raise ValueError("nonpositive coarse interval")
                first, last = start * fps, end * fps
                if first.denominator != 1 or last.denominator != 1:
                    raise ValueError("coarse boundary is not on source frame grid; rounding forbidden")
                start_frame, end_frame = int(first), int(last)
            else:
                raise ValueError("unsupported CSV schema")
            result["intervals"].append(
                {
                    "csv_row": csv_row,
                    "start_frame": start_frame,
                    "end_frame": end_frame,
                    "start_seconds": float(start),
                    "end_seconds": float(end),
                }
            )
        except (ValueError, TypeError, ZeroDivisionError) as exc:
            result["malformed_rows"].append({"csv_row": csv_row, "reason": str(exc)})
    result.update(inventory(result["intervals"], frame_count))
    if schema == "seven-column-rally":
        try:
            parsed = read_csv(path, float(fps))
            result["unchanged_benchmark_parser"] = {"status": "passed", "interval_count": len(parsed)}
        except ValueError as exc:
            result["unchanged_benchmark_parser"] = {"status": "failed", "reason": str(exc)}
    result["valid_interval_count"] = len(result["intervals"])
    result["time_units"] = "seconds; display MM:SS" if schema == "seven-column-rally" else "parsed legacy clock seconds"
    result["frame_index_convention"] = (
        "Numeric seconds verify zero-origin frame/fps; original human-tool indexing history unavailable."
        if schema == "seven-column-rally"
        else "No frame labels supplied; derived frame=exact legacy seconds*source FPS."
    )
    result["end_convention"] = (
        "Benchmark [start,end) boundary span, duration=end-start, no inclusive-frame addition. "
        "Original legacy human endpoint interpretation remains unverified."
    )
    result["temporal_compatibility"] = not result["malformed_rows"] and not result["out_of_range_csv_rows"]
    result["original_bytes_unchanged"] = path.read_bytes() == original
    if not result["original_bytes_unchanged"]:
        raise ValueError("annotation bytes changed during audit")
    return result


def convert_coarse(path: Path, output: Path, fps: Fraction, frame_count: int) -> dict:
    """Separate versioned sensitivity reference; never replaces primary labels."""
    result = audit(path, fps, frame_count)
    if result["schema"] != "coarse-legacy" or not result["temporal_compatibility"]:
        raise ValueError("valid source-compatible coarse reference required")
    if result["fully_blank_csv_rows"] or len(result["intervals"]) != result["csv_data_rows"]:
        raise ValueError("every original interval row must be preserved; blank/malformed rows require explicit review")
    write_predictions(output, [(r["start_frame"], r["end_frame"]) for r in result["intervals"]], float(fps))
    return {
        "schema": "explicit-coarse-reference-conversion-v1",
        "source_audit": result,
        "converted_path": str(output.resolve()),
        "converted_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "row_mapping": [
            {"converted_csv_row": i + 2, "original_csv_row": r["csv_row"]} for i, r in enumerate(result["intervals"])
        ],
        "conversion": "start/end frame = exact source FPS * original seconds; no offset, rounding or interval change",
        "reported_precision_limit": (
            "Original clock precision retained; integer MM:SS values have one-second displayed resolution. "
            "No finer physical ground truth inferred."
        ),
        "usage": (
            "Separate legacy coarse-reference sensitivity only; does not replace requested seven-column benchmark."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--fps", type=Fraction, required=True)
    parser.add_argument("--frame-count", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--convert-coarse", type=Path)
    args = parser.parse_args()
    result = (
        convert_coarse(args.csv, args.convert_coarse, args.fps, args.frame_count)
        if args.convert_coarse
        else audit(args.csv, args.fps, args.frame_count)
    )
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")


if __name__ == "__main__":
    main()
