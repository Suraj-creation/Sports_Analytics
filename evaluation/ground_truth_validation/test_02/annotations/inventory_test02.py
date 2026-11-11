"""Read only the seven original Test2 files; write independent inventory evidence."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "Part2/dataset/Test2_Full"
OUT = Path(__file__).resolve().parent


def number(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def seconds(value):
    parts = str(value).strip().split(":")
    return sum(float(v) * 60**i for i, v in enumerate(reversed(parts)))


def main():
    entries = []
    tables = {}
    for path in sorted(SOURCE.iterdir()):
        if not path.is_file():
            continue
        data = path.read_bytes()
        entry = {"path": str(path.relative_to(ROOT)), "bytes": len(data),
                 "sha256": hashlib.sha256(data).hexdigest()}
        if path.suffix == ".json":
            entry["content"] = json.loads(data)
            entry["schema"] = {k: type(v).__name__ for k, v in entry["content"].items()}
        else:
            reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig")))
            rows = list(reader)
            tables[path.name] = rows
            entry.update(columns=reader.fieldnames, data_rows=len(rows),
                         blank_rows=[i+1 for i, row in enumerate(rows)
                                     if all(not str(v or "").strip() for v in row.values())],
                         missing_counts={k: sum(not str(r[k] or "").strip() for r in rows)
                                         for k in reader.fieldnames},
                         sample_first=rows[:2], sample_last=rows[-2:])
            frame_col = next((k for k in ("Frame", "frame_no") if k in reader.fieldnames), None)
            if frame_col:
                frames = [int(r[frame_col]) for r in rows]
                entry["frame_population"] = {"min": min(frames), "max": max(frames),
                    "unique": len(set(frames)), "duplicates": len(frames)-len(set(frames)),
                    "missing": sorted(set(range(max(frames)+1))-set(frames)),
                    "strictly_contiguous_zero_based": frames == list(range(len(frames)))}
        entries.append(entry)

    def get(name):
        return next(e for e in entries if Path(e["path"]).name == name)

    coarse = tables["Test2_Full.csv"]
    previous = [0, 0]
    nonunit = []
    unit_disagree = []
    intervals = []
    for i, row in enumerate(coarse, 1):
        interval = [seconds(row["start_time"]), seconds(row["end_time"])]
        intervals.append(interval)
        current = [number(row["roundscore_A"]), number(row["roundscore_B"])]
        delta = [current[j]-previous[j] for j in range(2)]
        record = {"data_row": i, "csv_line": i+1, "interval_seconds": interval,
                  "previous_score": previous, "score": current, "delta": delta,
                  "winner": row["win_point_player"]}
        if delta not in ([1, 0], [0, 1]):
            nonunit.append(record)
        elif row["win_point_player"].strip() != ("Player A" if delta == [1, 0] else "Player B"):
            unit_disagree.append(record)
        previous = current
    get("Test2_Full.csv")["analysis"] = {
        "categorical_counts": {key: dict(Counter(r[key] for r in coarse))
            for key in ("win_point_player", "win_reason", "ball_types", "lose_reason")},
        "time_range_seconds": [min(s for s, e in intervals), max(e for s, e in intervals)],
        "nonpositive_interval_rows": [i+1 for i, (s, e) in enumerate(intervals) if e <= s],
        "adjacent_overlap_rows": [i+1 for i in range(1, len(intervals))
                                  if intervals[i][0] < intervals[i-1][1]],
        "nonunit_score_transitions": nonunit,
        "nonunit_score_transition_count": len(nonunit),
        "unit_score_winner_disagreements": unit_disagree,
        "score_a_decrease_rows": [x["data_row"] for x in nonunit if x["delta"][0] < 0],
        "score_b_decrease_rows": [x["data_row"] for x in nonunit if x["delta"][1] < 0],
    }

    for name in ("Test2_Full_ball_filled.csv", "Test2_Full_Rev_ball_filled.csv"):
        rows = tables[name]
        outside = [int(r["Frame"]) for r in rows
                   if not (0 <= float(r["X"]) < 1280 and 0 <= float(r["Y"]) < 720)]
        visible_low = [int(r["Frame"]) for r in rows
                       if int(r["Visibility"]) == 1 and float(r["Confidence"]) < .5]
        get(name)["analysis"] = {
            "visibility_counts": dict(Counter(r["Visibility"] for r in rows)),
            "visible_confidence_below_0_5_count": len(visible_low),
            "visible_confidence_below_0_5_example_frames": visible_low[:20],
            "outside_1280x720_count": len(outside), "outside_1280x720_frames": outside,
            "invisible_nonzero_xy_count": sum(int(r["Visibility"]) == 0 and
                        (float(r["X"]) != 0 or float(r["Y"]) != 0) for r in rows),
            "visible_zero_xy_count": sum(int(r["Visibility"]) == 1 and
                        float(r["X"]) == float(r["Y"]) == 0 for r in rows),
        }

    players = tables["player_detections.csv"]
    both = [r for r in players if number(r["player_1_y"]) is not None
            and number(r["player_2_y"]) is not None]
    flips = []
    for a, b in zip(both, both[1:]):
        if int(b["frame_no"]) == int(a["frame_no"])+1 and (
            float(a["player_1_y"]) > float(a["player_2_y"])) != (
            float(b["player_1_y"]) > float(b["player_2_y"])):
            flips.append(int(b["frame_no"]))
    get("player_detections.csv")["analysis"] = {
        "both_slots_present_rows": len(both),
        "slot1_lower_in_image_rows": sum(float(r["player_1_y"]) > float(r["player_2_y"]) for r in both),
        "slot2_lower_in_image_rows": sum(float(r["player_2_y"]) > float(r["player_1_y"]) for r in both),
        "consecutive_relative_y_order_flips_count": len(flips),
        "consecutive_relative_y_order_flips_example_frames": flips[:30],
        "note": "Image-order reversals are diagnostic slot instability, not reviewed athlete ID-switch counts.",
    }

    rallies = tables["Test2_Full_rally.csv"]
    wins = tables["win_predictions.csv"]
    get("Test2_Full_rally.csv")["analysis"] = {
        "frame_range": [min(int(r["Start_Frame"]) for r in rallies), max(int(r["End_Frame"]) for r in rallies)],
        "time_range_seconds": [min(float(r["Start_Time_sec"]) for r in rallies), max(float(r["End_Time_sec"]) for r in rallies)],
        "frame_time_inconsistent_at_30fps_rows": [i+1 for i, r in enumerate(rallies)
            if abs(int(r["Start_Frame"])/30-float(r["Start_Time_sec"])) > 1e-6
            or abs(int(r["End_Frame"])/30-float(r["End_Time_sec"])) > 1e-6],
        "duration_inconsistent_rows": [i+1 for i, r in enumerate(rallies)
            if abs(float(r["End_Time_sec"])-float(r["Start_Time_sec"])-float(r["Duration_sec"])) > 1e-6],
    }
    get("win_predictions.csv")["analysis"] = {
        "categorical_counts": {key: dict(Counter(r[key] for r in wins))
             for key in ("winner", "win_reason", "reason_src", "fault_side", "fault_src", "cnn_class")},
        "frame_pairs_equal_rally_rows": sum(int(w["start_frame"]) == int(r["Start_Frame"])
             and int(w["end_frame"]) == int(r["End_Frame"]) for w, r in zip(wins, rallies)),
        "same_population_as_rally": len(wins) == len(rallies),
        "final_generated_score": [wins[-1]["score_Player A"], wins[-1]["score_Player B"]],
    }
    output = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "repository_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_directory": str(SOURCE.relative_to(ROOT)),
        "scope": "Test2 local originals only; inventory/diagnosis, no inference or annotation modification",
        "remote_source_revalidation": "Not performed by annotation agent; orchestrator owns video/download pairing",
        "files": entries,
        "byte_identical_groups": [[Path(e["path"]).name for e in entries if e["sha256"] == sha]
            for sha, count in Counter(e["sha256"] for e in entries).items() if count > 1],
        "missing_requested_annotation_families": ["Full2", "reviewed bounding boxes and persistent IDs",
            "reviewed pose/keypoint labels", "reviewed contact times and hitter IDs",
            "exhaustive stroke sequence", "reviewed highlight/analytics values"],
        "source_preservation": "All original files read only; hashes recorded before downstream evaluation",
    }
    (OUT / "annotation_inventory.json").write_text(json.dumps(output, indent=2)+"\n")
    print(json.dumps({"files": len(entries), "rows": {k: len(v) for k, v in tables.items()},
        "nonunit_scores": len(nonunit), "unit_disagree": len(unit_disagree),
        "order_flips": len(flips), "identical": output["byte_identical_groups"]}, indent=2))


if __name__ == "__main__":
    main()
