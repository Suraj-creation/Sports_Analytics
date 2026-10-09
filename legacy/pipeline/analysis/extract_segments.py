"""
extract_segments.py
--------------------
Turn a court_presence.py CSV into a small number of short video clips
covering only the time ranges where the main broadcast camera angle is
actually on screen -- so the expensive stages (TrackNetV3 shuttle
detection, YOLO player detection) run on minutes of footage instead of a
full broadcast's worth of intro/crowd/replay cutaways.

Pipeline:
  1. Find contiguous court_present==1 runs.
  2. Merge runs separated by a short gap (a brief cutaway/graphic mid-rally
     shouldn't split one segment into two).
  3. Pad each merged run (rally starts/ends often dip near the presence
     threshold as players cross the boundary).
  4. Drop anything still too short to be a real rally after padding.
  5. Cut each final segment out with ffmpeg (frame-accurate -- uses the
     `select` filter, not -ss/-to timestamp seeking, so segment N's local
     frame 0 is exactly global frame `start_frame`).

Output: <out_dir>/seg_NNN.mp4 for each segment, plus manifest.csv
(seg_idx, start_frame, end_frame, n_frames, clip_path) that
run_full_pipeline.py and stitch_segments.py use to map local frame numbers
in each clip's outputs back to the original video's frame numbers.

Usage:
    python analysis/extract_segments.py \\
        --court_presence_csv YourMatch/YourMatch_court_presence.csv \\
        --video YourMatch/YourMatch.mp4 \\
        --out_dir YourMatch/segments
"""
import argparse
import os
import subprocess
import sys

import cv2
import pandas as pd


def find_segments(df, fps, min_gap_sec=2.0, pad_sec=1.5, min_duration_sec=3.0,
                  total_frames=None):
    df = df.sort_values("frame_no").reset_index(drop=True)
    present = df["court_present"].values
    frames  = df["frame_no"].values

    # 1. Contiguous runs of court_present == 1
    runs = []
    i = 0
    n = len(present)
    while i < n:
        if present[i] == 1:
            j = i
            while j < n and present[j] == 1:
                j += 1
            runs.append([int(frames[i]), int(frames[j - 1])])
            i = j
        else:
            i += 1
    if not runs:
        return []

    # 2. Merge runs separated by a short gap
    min_gap_frames = min_gap_sec * fps
    merged = [runs[0]]
    for start, end in runs[1:]:
        if start - merged[-1][1] <= min_gap_frames:
            merged[-1][1] = end
        else:
            merged.append([start, end])

    # 3. Pad, clamped to valid range
    max_frame = int(total_frames - 1) if total_frames else int(frames[-1])
    pad_frames = int(pad_sec * fps)
    padded = [[max(0, s - pad_frames), min(max_frame, e + pad_frames)] for s, e in merged]

    # Re-merge in case padding caused adjacent segments to overlap
    padded.sort()
    final = [padded[0]]
    for start, end in padded[1:]:
        if start <= final[-1][1]:
            final[-1][1] = max(final[-1][1], end)
        else:
            final.append([start, end])

    # 4. Drop too-short segments
    min_dur_frames = min_duration_sec * fps
    final = [(s, e) for s, e in final if (e - s) >= min_dur_frames]

    return final


def extract_clip(video_path, start_frame, end_frame, out_path):
    """Frame-accurate cut via the select filter (decodes+re-encodes, but
    that's still far cheaper than running TrackNetV3/YOLO on the same
    span -- correctness of the frame count matters more here than speed)."""
    n_frames = end_frame - start_frame + 1
    vf = f"select='between(n\\,{start_frame}\\,{end_frame})',setpts=PTS-STARTPTS"
    af_needed = False  # shuttle/player detection don't need audio
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", vf, "-an", "-vsync", "0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        out_path,
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        raise RuntimeError(f"ffmpeg failed for {out_path}:\n{res.stderr.decode()[-2000:]}")
    return n_frames


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--court_presence_csv", required=True)
    ap.add_argument("--video", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--min_gap_sec", type=float, default=2.0,
                    help="Merge runs separated by less than this (default 2.0s)")
    ap.add_argument("--pad_sec", type=float, default=1.5,
                    help="Pad each segment by this much on both sides (default 1.5s)")
    ap.add_argument("--min_duration_sec", type=float, default=3.0,
                    help="Drop segments shorter than this after padding (default 3.0s)")
    args = ap.parse_args()

    cap = cv2.VideoCapture(args.video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    df = pd.read_csv(args.court_presence_csv)
    segments = find_segments(df, fps, args.min_gap_sec, args.pad_sec,
                             args.min_duration_sec, total_frames)

    if not segments:
        sys.exit("ERROR: no court-present segments found -- nothing to extract. "
                 "Check --threshold on court_presence.py, or whether the court "
                 "annotation actually matches this video's camera angle.")

    os.makedirs(args.out_dir, exist_ok=True)
    rows = []
    total_seg_frames = 0
    print(f"  {len(segments)} segment(s) after merge/pad/filter "
          f"(covers {sum(e-s+1 for s,e in segments)/fps:.1f}s of "
          f"{total_frames/fps:.1f}s total)")
    for idx, (start_f, end_f) in enumerate(segments):
        clip_path = os.path.join(args.out_dir, f"seg_{idx:03d}.mp4")
        print(f"  [{idx+1}/{len(segments)}] frames {start_f}-{end_f} "
              f"({(end_f-start_f+1)/fps:.1f}s) -> {clip_path}")
        n_frames = extract_clip(args.video, start_f, end_f, clip_path)
        total_seg_frames += n_frames
        rows.append({"seg_idx": idx, "start_frame": start_f, "end_frame": end_f,
                     "n_frames": n_frames, "clip_path": clip_path})

    manifest = pd.DataFrame(rows)
    manifest_path = os.path.join(args.out_dir, "manifest.csv")
    manifest.to_csv(manifest_path, index=False)
    print(f"  Saved -> {manifest_path}")
    print(f"  Total: {total_seg_frames} frames to process instead of "
          f"{total_frames} ({100*total_seg_frames/total_frames:.1f}%)")


if __name__ == "__main__":
    main()
