import csv

import pytest

from scripts.benchmarking.evaluate_rallies import SCHEMA, read_csv, write_predictions


@pytest.mark.parametrize("fps", [25, 30, 30000 / 1001, 60])
def test_round_trip_exact_schema(tmp_path, fps):
    p = tmp_path / "pred.csv"
    write_predictions(p, [(243, 715)], fps)
    with p.open() as f:
        assert next(csv.reader(f)) == SCHEMA
    rows = read_csv(p, fps)
    assert rows[0].start_frame == 243
    assert rows[0].end == 715 / fps


@pytest.mark.parametrize(
    "field,value",
    [
        ("Start_Time_sec", ""),
        ("End_Time_sec", "nan"),
        ("Duration_sec", "inf"),
        ("Start_Frame", "243.1"),
        ("End_Time_sec", "24"),
        ("Start_Time", "00:09"),
        ("Duration_sec", "15.766666666666667"),
    ],
)
def test_invalid_values(tmp_path, field, value):
    p = tmp_path / "pred.csv"
    write_predictions(p, [(243, 715)], 30)
    with p.open() as f:
        rows = list(csv.DictReader(f))
    rows[0][field] = value
    with p.open("w", newline="") as f:
        w = csv.DictWriter(f, SCHEMA)
        w.writeheader()
        w.writerows(rows)
    with pytest.raises(ValueError):
        read_csv(p, 30)


@pytest.mark.parametrize("schema", [SCHEMA[::-1], SCHEMA[:-1], SCHEMA + ["shots"]])
def test_reject_other_schemas(tmp_path, schema):
    p = tmp_path / "pred.csv"
    p.write_text(",".join(schema) + "\n")
    with pytest.raises(ValueError):
        read_csv(p, 30)


def test_empty_predictions_valid_and_overwrite_refused(tmp_path):
    p = tmp_path / "pred.csv"
    write_predictions(p, [], 30)
    assert read_csv(p, 30) == []
    with pytest.raises(FileExistsError):
        write_predictions(p, [], 30)


def test_known_one_based_csv_requires_explicit_convention(tmp_path):
    p = tmp_path / "labels.csv"
    p.write_text(",".join(SCHEMA) + "\n1,31,0,1,1,00:00,00:01\n")
    with pytest.raises(ValueError):
        read_csv(p, 30)
    assert read_csv(p, 30, frame_base=1)[0].start_frame == 1


def test_known_timestamp_origin_is_explicit(tmp_path):
    p = tmp_path / "labels.csv"
    p.write_text(",".join(SCHEMA) + "\n0,30,5,6,1,00:05,00:06\n")
    with pytest.raises(ValueError):
        read_csv(p, 30)
    assert read_csv(p, 30, time_origin=5)[0].start == 5


def test_mismatched_rate_rejected_instead_of_silently_rescaled(tmp_path):
    p = tmp_path / "labels.csv"
    write_predictions(p, [(30, 90)], 30)
    with pytest.raises(ValueError):
        read_csv(p, 25)
