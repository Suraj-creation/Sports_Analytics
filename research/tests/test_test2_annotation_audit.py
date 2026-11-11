"""Immutable schema/timebase audits and justified explicit conversion controls."""

import csv
from fractions import Fraction

import pytest

from research.test2_annotation_audit import COARSE_SCHEMA, audit, convert_coarse, seconds
from scripts.benchmarking.evaluate_rallies import SCHEMA, read_csv, write_predictions


def coarse(tmp_path, intervals):
    path = tmp_path / "legacy.csv"
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(COARSE_SCHEMA)
        for start, end in intervals:
            writer.writerow([start, end, "A", "unknown", "unknown", "unknown", "0", "0"])
    return path


def test_seven_column_contract_keeps_original_bytes_and_flags_all_topology_issues(tmp_path):
    path = tmp_path / "seven.csv"
    write_predictions(path, [(0, 100), (90, 110), (0, 100), (150, 201)], 30)
    original = path.read_bytes()
    result = audit(path, Fraction(30), 200)
    assert result["unchanged_benchmark_parser"]["status"] == "passed"
    assert result["duplicate_interval_csv_row_pairs"] == [[2, 4]]
    assert result["out_of_range_csv_rows"] == [5]
    assert result["out_of_order_csv_rows"] == [4]
    assert len(result["positive_overlap_csv_row_pairs"]) == 3
    assert result["match_identity_verified"] is False
    assert path.read_bytes() == original


def test_missing_malformed_nonfinite_and_wrong_timebase_rows_all_reported(tmp_path):
    path = tmp_path / "bad.csv"
    with path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(SCHEMA)
        writer.writerows(
            [
                [0, 30, 0, 1, 1, "00:00", "00:01"],
                [30, 60, "nan", 2, 1, "00:01", "00:02"],
                [60, 90, 2, 3, 1, "00:02", ""],
                [90, 120, 4, 5, 1, "00:04", "00:05"],
            ]
        )
    result = audit(path, Fraction(30), 200)
    assert [row["csv_row"] for row in result["malformed_rows"]] == [3, 4, 5]
    assert result["missing_field_csv_rows"] == [4]
    assert result["unchanged_benchmark_parser"]["status"] == "failed"


def test_optional_coarse_conversion_preserves_all_rows_order_hashes_and_exact_boundaries(tmp_path):
    path = coarse(tmp_path, [("00:02", "00:05"), ("1:00", "1:04")])
    original = path.read_bytes()
    converted = tmp_path / "coarse_seven.csv"
    receipt = convert_coarse(path, converted, Fraction(30), 2000)
    parsed = read_csv(converted, 30)
    assert [(r.start_frame, r.end_frame) for r in parsed] == [(60, 150), (1800, 1920)]
    assert receipt["row_mapping"] == [
        {"converted_csv_row": 2, "original_csv_row": 2},
        {"converted_csv_row": 3, "original_csv_row": 3},
    ]
    assert receipt["source_audit"]["independently_reviewed_ground_truth_established"] is False
    assert path.read_bytes() == original
    with pytest.raises(FileExistsError):
        convert_coarse(path, converted, Fraction(30), 2000)


@pytest.mark.parametrize("value", ["1:60", "-1", "1.5:02", "00::02", "nan"])
def test_invalid_clocks_cannot_silently_convert(value):
    with pytest.raises((ValueError, ZeroDivisionError)):
        seconds(value)


def test_coarse_off_grid_conversion_cannot_round_labels(tmp_path):
    path = coarse(tmp_path, [("0.01", "1.01")])
    with pytest.raises(ValueError, match="valid source-compatible"):
        convert_coarse(path, tmp_path / "converted.csv", Fraction(30), 100)


def test_clock_units_seconds_and_hours_are_exact():
    assert seconds("63") == Fraction(63)
    assert seconds("1:03") == Fraction(63)
    assert seconds("01:02:03.5") == Fraction(7447, 2)
