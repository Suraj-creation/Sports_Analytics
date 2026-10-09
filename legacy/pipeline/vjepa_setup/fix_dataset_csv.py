"""
fix_dataset_csv.py
-------------------
One-off patch for dataset/dataset.csv:

  Replaces the label columns (start_time, end_time, win_point_player,
  win_reason, ball_types, lose_reason, roundscore_A, roundscore_B) for
  Test3_Full_Rev rows with the corrected values from
  dataset/labels/Test3_Full_Rev.csv (which uses "Player A"/"Player B"
  instead of "Gemke"/"Ginting", and has real data for the rally that was
  previously blank), matched by row order.

Run on the GPU server, inside vjepa_setup/:
    python3 fix_dataset_csv.py

Writes dataset/dataset.csv in place (backs up the original to
dataset/dataset.csv.bak first).
"""

import csv
import shutil

DATASET_CSV = "dataset/dataset.csv"
TEST3_LABELS_CSV = "dataset/labels/Test3_Full_Rev.csv"
LABEL_COLUMNS = [
    "start_time", "end_time", "win_point_player", "win_reason",
    "ball_types", "lose_reason", "roundscore_A", "roundscore_B",
]


def main():
    shutil.copy(DATASET_CSV, DATASET_CSV + ".bak")
    print(f"Backed up {DATASET_CSV} -> {DATASET_CSV}.bak")

    with open(DATASET_CSV, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    fieldnames = list(rows[0].keys())

    # Replace Test3_Full_Rev label columns with corrected values
    with open(TEST3_LABELS_CSV, newline="", encoding="utf-8-sig") as f:
        test3_labels = list(csv.DictReader(f))

    test3_idx = [i for i, r in enumerate(rows) if r["video"] == "Test3_Full_Rev"]
    if len(test3_idx) != len(test3_labels):
        raise SystemExit(
            f"Row count mismatch: dataset.csv has {len(test3_idx)} "
            f"Test3_Full_Rev rows, {TEST3_LABELS_CSV} has {len(test3_labels)} rows. "
            "They must match 1:1 to patch by position."
        )

    for row_idx, label_row in zip(test3_idx, test3_labels):
        for col in LABEL_COLUMNS:
            rows[row_idx][col] = label_row[col]
    print(f"Patched {len(test3_idx)} Test3_Full_Rev rows with corrected labels")

    with open(DATASET_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows -> {DATASET_CSV}")


if __name__ == "__main__":
    main()
