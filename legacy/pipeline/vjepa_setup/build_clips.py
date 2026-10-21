"""
Cut a clip for every rally listed in each ground-truth CSV in dataset/labels/,
matching it to the video with the same base filename in dataset/videos/.

Each label CSV must have a "start" and "end" column (either MM:SS, H:MM:SS,
or plain seconds), plus whatever label columns you have (win_point_player,
win_reason, ball_types, lose_reason, roundscore_A, roundscore_B, ...). Those
extra columns are carried through unchanged into clips_index.csv.

Usage:
    python build_clips.py
"""

import argparse
import csv
import os
import re
import cv2


START_KEYS = ["start_time", "start", "Start (sec)", "Start"]
END_KEYS = ["end_time", "end", "End (sec)", "End"]
VIDEO_EXTS = [".mp4", ".mov", ".avi", ".mkv"]


def parse_time(value):
    value = str(value).strip()
    if re.match(r"^\d+(\.\d+)?$", value):
        return float(value)
    parts = [float(p) for p in value.split(":")]
    seconds = 0.0
    for p in parts:
        seconds = seconds * 60 + p
    return seconds


def first_present(row, keys):
    for k in keys:
        if k in row and row[k] not in (None, ""):
            return k
    raise KeyError(f"None of {keys} found in columns: {list(row.keys())}")


def cut_clip(video_path, start, end, out_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    start_frame = int(start * fps)
    end_frame = int(end * fps)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(out_path, fourcc, fps, (w, h))

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    frame_no = start_frame
    while frame_no < end_frame:
        ret, frame = cap.read()
        if not ret:
            break
        writer.write(frame)
        frame_no += 1

    cap.release()
    writer.release()
    return frame_no - start_frame


def find_video(videos_dir, base):
    for ext in VIDEO_EXTS:
        cand = os.path.join(videos_dir, base + ext)
        if os.path.exists(cand):
            return cand
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--videos", default="dataset/videos")
    parser.add_argument("--labels", default="dataset/labels")
    parser.add_argument("--out", default="dataset/clips")
    parser.add_argument("--index", default="dataset/clips_index.csv")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    rows_out = []

    label_files = sorted(f for f in os.listdir(args.labels) if f.lower().endswith(".csv"))
    if not label_files:
        raise SystemExit(f"No CSV files found in {args.labels}")

    for label_file in label_files:
        base = os.path.splitext(label_file)[0]
        video_path = find_video(args.videos, base)
        if video_path is None:
            print(f"WARNING: no video found for label '{label_file}' (looked for {base}{VIDEO_EXTS}), skipping")
            continue

        out_dir = os.path.join(args.out, base)
        os.makedirs(out_dir, exist_ok=True)

        with open(os.path.join(args.labels, label_file), newline="") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, 1):
                start_key = first_present(row, START_KEYS)
                end_key = first_present(row, END_KEYS)
                start = parse_time(row[start_key])
                end = parse_time(row[end_key])

                clip_path = os.path.join(out_dir, f"rally_{i:03d}.mp4").replace("\\", "/")
                frames = cut_clip(video_path, start, end, clip_path)
                if frames <= 0:
                    print(f"WARNING: 0 frames for {base} rally {i} ({start}-{end}s), skipping")
                    continue

                out_row = dict(row)
                out_row["video"] = base
                out_row["rally"] = i
                out_row["clip_path"] = clip_path
                rows_out.append(out_row)
                print(f"{base} rally {i}: {start:.1f}-{end:.1f}s -> {clip_path} ({frames} frames)")

    if not rows_out:
        raise SystemExit("No clips were produced - check dataset/videos and dataset/labels.")

    fieldnames = list(rows_out[0].keys())
    with open(args.index, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)
    print(f"\nWrote index with {len(rows_out)} clips to {args.index}")


if __name__ == "__main__":
    main()
