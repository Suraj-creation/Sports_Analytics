"""
Merge a "times" CSV (rally, start, end, ...) with a "labels" CSV
(index/rally, win_point_player, win_reason, ball_types, roundscore_A,
roundscore_B, ...) into one CSV in the format build_clips.py expects.

The two files must have the same number of rows, in the same rally order
(matched by row position, not by any ID column).

Usage:
    python merge_labels.py --times dataset/labels/Test1_Full_rev_GT.csv \
                            --labels "dataset/labels/Test1_Full1(Sheet1).csv" \
                            --out dataset/labels/Test1_Full_rev.csv
"""

import argparse
import csv


TIME_START_KEYS = ["start", "Start (sec)", "start_time"]
TIME_END_KEYS = ["end", "End (sec)", "end_time"]


def first_present(row, keys):
    for k in keys:
        if k in row and row[k] not in (None, ""):
            return k
    raise KeyError(f"None of {keys} found in columns: {list(row.keys())}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--times", required=True, help="CSV with rally start/end times")
    parser.add_argument("--labels", required=True, help="CSV with winner/reason/ball type/scores")
    parser.add_argument("--out", required=True, help="Output merged CSV (dataset/labels/<video_basename>.csv)")
    args = parser.parse_args()

    with open(args.times, newline="", encoding="utf-8-sig") as f:
        time_rows = list(csv.DictReader(f))
    with open(args.labels, newline="", encoding="utf-8-sig") as f:
        label_rows = list(csv.DictReader(f))

    if len(time_rows) != len(label_rows):
        raise SystemExit(
            f"Row count mismatch: {args.times} has {len(time_rows)} rows, "
            f"{args.labels} has {len(label_rows)} rows. They must match 1:1."
        )

    start_key = first_present(time_rows[0], TIME_START_KEYS)
    end_key = first_present(time_rows[0], TIME_END_KEYS)

    out_rows = []
    for t_row, l_row in zip(time_rows, label_rows):
        out_row = {"start_time": t_row[start_key], "end_time": t_row[end_key]}
        for k, v in l_row.items():
            if k.lower() not in ("index", "rally"):
                out_row[k] = v
        out_rows.append(out_row)

    fieldnames = list(out_rows[0].keys())
    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Wrote {len(out_rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
