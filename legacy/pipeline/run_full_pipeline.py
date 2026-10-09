"""
run_full_pipeline.py
=====================
True end-to-end entry point: give it a raw match video, get back the final
report.

Default (pre-trimmed rally-only clip) order:
  * (before 0) preprocess video to 1280x720/30fps H.264 (also fixes
    AV1/VP9/HEVC inputs cv2 can't decode -- common for YouTube downloads)
  0. TrackNetV3/predict.py           -- shuttle detection (whole video)
  1. TrackNetV3/filter_trajectory.py -- remove spike/teleport/post-smash noise
  2. analysis/auto_court.py OR analysis/annotate_court.py -- court + net geometry
  3. analysis/player_detection.py    -- YOLO11 player boxes (whole video)
  4. TrackNetV3/fill_gaps.py         -- gap-fill the cleaned shuttle track
  5. analysis/detect_rallies.py      -- rally segmentation
  6. run_unified_pipeline.py         -- Stage 7 winner/win-reason + fusion +
                                         AI/stats commentary + PDF summary
  7. analysis/annotate_video.py      -- combined court+net+players+shuttle
                                         verification video, full video with
                                         "RALLY DETECTED" markers (a missed
                                         rally shows up as unmarked footage,
                                         not silently-trimmed-away)

--broadcast order (full broadcast video with intro/crowd cutaways/replays
mixed in -- the camera angle is NOT constant throughout, only during actual
rally play):
  2. Court + net geometry            -- first; everything else needs it.
                                         --court_mode manual uses a
                                         centered/margin-scored wide search
                                         (frame_picker.py) for the reference
                                         frame shown to click on, since a
                                         fixed early frame is usually still
                                         intro/graphics on a full broadcast
  2b. analysis/court_presence.py     -- per-frame: does this frame match the
                                         annotated camera angle? (the "only
                                         the centered, standard-angle frames
                                         are real rally play" signal)
  2c. analysis/extract_segments.py   -- cut out just the court-present time
                                         ranges as short clips
  2d. Per segment: TrackNetV3 predict + filter_trajectory + player_detection
                                      -- run the expensive stages ONLY on
                                         those clips, not the full broadcast
  2e. analysis/stitch_segments.py    -- remap each clip's local frame
                                         numbers back to the original
                                         video's frame numbers, concatenate
  4. TrackNetV3/fill_gaps.py         -- same as default, on the stitched CSVs
  5. analysis/detect_rallies.py      -- same, additionally gated by the
                                         court-presence mask
  6. run_unified_pipeline.py         -- same
  7. analysis/annotate_video.py      -- same

Either way, each stage is skipped if its output already exists, so a
failed/interrupted run can just be re-invoked and it picks up where it
left off.

Usage:
    python run_full_pipeline.py --video /path/to/YourMatch.mp4 \\
        --player_a "Player A" --player_b "Player B"

    # Higher-accuracy court geometry (interactive, one-time per camera angle):
    python run_full_pipeline.py --video /path/to/YourMatch.mp4 \\
        --player_a "Player A" --player_b "Player B" --court_mode manual

    # Full YouTube broadcast, not a pre-trimmed clip:
    python run_full_pipeline.py --video /path/to/Broadcast.mp4 \\
        --player_a "Player A" --player_b "Player B" \\
        --court_mode manual --broadcast
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent


def _probe_video(path):
    """(codec, width, height, fps) via ffprobe."""
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=codec_name,width,height,r_frame_rate",
         "-of", "default=noprint_wrappers=1", str(path)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    info = dict(line.split("=", 1) for line in res.stdout.strip().splitlines() if "=" in line)
    codec  = info.get("codec_name", "")
    width  = int(info.get("width", 0) or 0)
    height = int(info.get("height", 0) or 0)
    num, _, den = info.get("r_frame_rate", "0/1").partition("/")
    fps = float(num) / float(den) if den and float(den) != 0 else 0.0
    return codec, width, height, fps


def _preprocess_video(source_video, match_video, target_width, target_height,
                      target_fps=30.0):
    """
    Normalize the input video to what the whole pipeline actually assumes --
    H.264, target_width x target_height, target_fps, no audio -- BEFORE
    anything (court annotation, TrackNetV3, player detection, court-
    presence) touches it. Mirrors this project's existing video_raw/ ->
    video_fixed/ convention:

        ffmpeg -i video_raw/X.mp4 -vf scale=W:H -r FPS \\
            -c:v libx264 -preset fast -crf 23 -an video_fixed/X_Full.mp4

    This is more than the AV1-decode fix alone: a source video at, say,
    1920x1080 or 60fps would decode fine but silently violate every
    resolution/frame-rate assumption downstream (win_predictor thresholds,
    annotated court.json pixel coordinates, rally-duration-in-frames
    math) -- normalizing once up front is the actual fix, not just making
    cv2.VideoCapture not crash. Skips the ffmpeg pass entirely if the
    source already matches (fast path for already-prepared video_fixed/
    videos).
    """
    def matches(path):
        codec, w, h, fps = _probe_video(path)
        return (codec == "h264" and w == target_width and h == target_height
                and abs(fps - target_fps) < 0.1)

    if match_video.exists() or match_video.is_symlink():
        if matches(match_video):
            return
        print(f"  {match_video.name} exists but doesn't match the pipeline's "
              f"expected {target_width}x{target_height}@{target_fps}fps H.264 "
              f"format -- re-processing")
        match_video.unlink()

    if matches(source_video):
        try:
            match_video.symlink_to(source_video)
        except OSError:
            shutil.copy(source_video, match_video)
        return

    codec, w, h, fps = _probe_video(source_video)
    print(f"  Source video is {w}x{h} @ {fps:.2f}fps, codec={codec} -- "
          f"normalizing to {target_width}x{target_height} @ {target_fps}fps, "
          f"H.264, no audio...")
    cmd = ["ffmpeg", "-y", "-i", str(source_video),
           "-vf", f"scale={target_width}:{target_height}", "-r", str(target_fps),
           "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-an",
           str(match_video)]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        sys.exit(f"ERROR: ffmpeg preprocessing failed:\n{res.stderr.decode()[-2000:]}")
    print(f"  Preprocessed -> {match_video}")


def _run(cmd, cwd, step):
    print(f"\n{'='*70}\n  {step}\n{'='*70}")
    print("  $ " + " ".join(str(c) for c in cmd))
    res = subprocess.run(cmd, cwd=str(cwd))
    if res.returncode != 0:
        sys.exit(f"\n[FAILED] {step} (exit {res.returncode}) -- fix the error "
                  f"above and re-run this script; completed steps are skipped.")


def _ensure_court(match_video, court_json, court_mode, court_type, step_label,
                  wide_search=False, search_step_sec=5.0, search_start_frame=None):
    if court_json.exists():
        print(f"\n[skip] Court annotation -- {court_json} exists")
        return
    if court_mode == "manual":
        cmd = [sys.executable, "analysis/annotate_court.py",
               "--video", str(match_video), "--out", str(court_json)]
        if wide_search:
            # A fixed early default frame is usually still intro/graphics on
            # a full broadcast (verified: frame 90 was the arena exterior
            # drone shot on a real match) -- search for one instead.
            cmd += ["--auto_frame", "--search_step_sec", str(search_step_sec)]
            if search_start_frame is not None:
                cmd += ["--search_start_frame", str(search_start_frame)]
        _run(cmd, PROJECT_ROOT, f"{step_label}  Court + net annotation "
                                "(manual -- click 4 corners + net on the frame shown)")
        return
    cmd = [sys.executable, "analysis/auto_court.py",
           "--video", str(match_video), "--out", str(court_json),
           "--court_type", court_type]
    if wide_search:
        cmd += ["--wide_search", "--search_step_sec", str(search_step_sec)]
        if search_start_frame is not None:
            cmd += ["--search_start_frame", str(search_start_frame)]
    _run(cmd, PROJECT_ROOT, f"{step_label}  Court + net detection (auto, {court_type} -- "
                           "see analysis/auto_court.py docstring)")
    with open(court_json) as f:
        if not json.load(f).get("court_type_matched", True):
            print(f"\n  *** WARNING: auto-detection could not confirm the "
                  f"{court_type} sideline for this video -- {court_json} "
                  f"is the cruder green-mask approximation. Delete it and "
                  f"re-run with --court_mode manual for an accurate one. ***")


def _run_segmented(match_folder, name, match_video, output_shuttle, clean_csv,
                   player_csv, court_json, width, height, player_model):
    """Full broadcast: only run shuttle/player detection on the time ranges
    where the annotated court is actually confirmed on screen."""
    court_mask_csv = match_folder / f"{name}_court_presence.csv"
    if court_mask_csv.exists():
        print(f"\n[skip] Court-presence mask -- {court_mask_csv} exists")
    else:
        _run([sys.executable, "analysis/court_presence.py",
              "--video", str(match_video), "--court_json", str(court_json),
              "--out", str(court_mask_csv)],
             PROJECT_ROOT, "2b/7  Court-presence mask")

    seg_dir = match_folder / "segments"
    manifest_path = seg_dir / "manifest.csv"
    if manifest_path.exists():
        print(f"\n[skip] Segment extraction -- {manifest_path} exists")
    else:
        _run([sys.executable, "analysis/extract_segments.py",
              "--court_presence_csv", str(court_mask_csv),
              "--video", str(match_video), "--out_dir", str(seg_dir)],
             PROJECT_ROOT, "2c/7  Extract court-present segments")

    manifest = pd.read_csv(manifest_path)

    seg_shuttle_raw   = seg_dir / "shuttle_raw"
    seg_shuttle_clean = seg_dir / "shuttle_clean"
    seg_players       = seg_dir / "players"
    seg_shuttle_clean.mkdir(parents=True, exist_ok=True)

    if clean_csv.exists() and player_csv.exists():
        print(f"\n[skip] Per-segment shuttle+player detection -- "
              f"{clean_csv} and {player_csv} exist")
    else:
        for _, row in manifest.iterrows():
            idx, clip = int(row["seg_idx"]), row["clip_path"]
            tag = f"seg_{idx:03d}"
            print(f"\n  --- segment {idx+1}/{len(manifest)} ({tag}) ---")

            raw_seg = seg_shuttle_raw / f"{tag}_ball.csv"
            if not raw_seg.exists():
                _run([sys.executable, "TrackNetV3/predict.py",
                      "--video_file", clip,
                      "--tracknet_file", "ckpts/TrackNet_best.pt",
                      "--save_dir", str(seg_shuttle_raw)],
                     PROJECT_ROOT, f"2d/7  [{tag}] Shuttle detection")
                # TrackNetV3 names output after the clip file, not our tag --
                # rename to keep the seg_NNN pattern stitch_segments.py matches on.
                produced = seg_shuttle_raw / (Path(clip).stem + "_ball.csv")
                if produced.exists() and produced != raw_seg:
                    produced.rename(raw_seg)

            clean_seg = seg_shuttle_clean / f"{tag}_ball_clean.csv"
            if not clean_seg.exists():
                _run([sys.executable, "TrackNetV3/filter_trajectory.py",
                      "--input", str(raw_seg), "--output", str(clean_seg),
                      "--video_width", str(width), "--video_height", str(height)],
                     PROJECT_ROOT, f"2d/7  [{tag}] Trajectory filtering")

            player_seg_dir = seg_players / tag
            if not (player_seg_dir / "player_detections.csv").exists():
                _run([sys.executable, "analysis/player_detection.py",
                      "--match_folder", str(player_seg_dir),
                      "--video", clip, "--court_file", str(court_json),
                      "--model", player_model, "--no_video"],
                     PROJECT_ROOT, f"2d/7  [{tag}] Player detection")

        _run([sys.executable, "analysis/stitch_segments.py",
              "--manifest", str(manifest_path),
              "--csv_glob", str(seg_shuttle_clean / "seg_*_ball_clean.csv"),
              "--frame_col", "Frame", "--out", str(clean_csv)],
             PROJECT_ROOT, "2e/7  Stitch shuttle segments")

        _run([sys.executable, "analysis/stitch_segments.py",
              "--manifest", str(manifest_path),
              "--csv_glob", str(seg_players / "seg_*" / "player_detections.csv"),
              "--frame_col", "frame_no", "--out", str(player_csv)],
             PROJECT_ROOT, "2e/7  Stitch player segments")

    return court_mask_csv


def run_full_pipeline(video, match_name=None, player_a="Player A", player_b="Player B",
                      width=1280, height=720, fps=30.0, court_mode="auto", court_type="singles",
                      player_model="yolo11x.pt", broadcast_mode=False,
                      court_search_step_sec=5.0, court_search_start_frame=None,
                      make_annotated_video=True):
    video = Path(video).resolve()
    if not video.exists():
        sys.exit(f"ERROR: video not found: {video}")

    name = match_name or video.stem
    match_folder = PROJECT_ROOT / name
    match_folder.mkdir(exist_ok=True)

    match_video = match_folder / f"{name}.mp4"
    _preprocess_video(video, match_video, width, height, fps)

    output_shuttle = PROJECT_ROOT / "output_shuttle"
    output_shuttle.mkdir(exist_ok=True)
    raw_csv     = output_shuttle / f"{name}_ball.csv"
    clean_csv   = output_shuttle / f"{name}_ball_clean.csv"
    filled_csv  = match_folder / f"{name}_ball_filled.csv"
    player_csv  = match_folder / "player_detections.csv"
    court_json  = match_folder / f"{name}_court.json"
    rally_csv   = match_folder / f"{name}_rally.csv"

    court_mask_csv = None
    if broadcast_mode:
        # Court geometry must exist BEFORE the court-presence scan / segment
        # extraction that everything else in broadcast mode depends on.
        # wide_search=True: a fixed early reference frame is usually still
        # intro/graphics on a full broadcast, so search the whole video for
        # a frame that actually shows the standard court view instead.
        _ensure_court(match_video, court_json, court_mode, court_type, "2/7",
                     wide_search=True, search_step_sec=court_search_step_sec,
                     search_start_frame=court_search_start_frame)
        court_mask_csv = _run_segmented(match_folder, name, match_video,
                                        output_shuttle, clean_csv, player_csv,
                                        court_json, width, height, player_model)
    else:
        if raw_csv.exists():
            print(f"\n[skip] Shuttle detection -- {raw_csv} exists")
        else:
            _run([sys.executable, "TrackNetV3/predict.py",
                  "--video_file", str(match_video),
                  "--tracknet_file", "ckpts/TrackNet_best.pt",
                  "--save_dir", str(output_shuttle)],
                 PROJECT_ROOT, "0/7  Shuttle detection (TrackNetV3)")

        if clean_csv.exists():
            print(f"\n[skip] Trajectory filtering -- {clean_csv} exists")
        else:
            _run([sys.executable, "TrackNetV3/filter_trajectory.py",
                  "--input", str(raw_csv), "--output", str(clean_csv),
                  "--video_width", str(width), "--video_height", str(height)],
                 PROJECT_ROOT, "1/7  Trajectory filtering")

        _ensure_court(match_video, court_json, court_mode, court_type, "2/7")

        if player_csv.exists():
            print(f"\n[skip] Player detection -- {player_csv} exists")
        else:
            _run([sys.executable, "analysis/player_detection.py",
                  "--match_folder", str(match_folder),
                  "--video", str(match_video),
                  "--court_file", str(court_json),
                  "--model", player_model, "--no_video"],
                 PROJECT_ROOT, "3/7  Player detection")

    # ── 4. Gap-fill (same for both modes -- consumes clean_csv/player_csv
    #      at their normal final paths regardless of how they were built) ──
    if filled_csv.exists():
        print(f"\n[skip] Gap-filling -- {filled_csv} exists")
    else:
        _run([sys.executable, "TrackNetV3/fill_gaps.py",
              "--input", str(clean_csv), "--output", str(filled_csv),
              "--player_csv", str(player_csv),
              "--video_width", str(width), "--video_height", str(height)],
             PROJECT_ROOT, "4/7  Gap-filling")

    # ── 5. Rally segmentation ───────────────────────────────────────────
    if rally_csv.exists():
        print(f"\n[skip] Rally segmentation -- {rally_csv} exists")
    else:
        cmd = [sys.executable, "analysis/detect_rallies.py",
               "--match_folder", str(match_folder)]
        if court_mask_csv is not None:
            cmd += ["--court_mask_csv", str(court_mask_csv)]
        _run(cmd, PROJECT_ROOT, "5/7  Rally segmentation")

    # ── 6. Stage 7 + fusion + commentary + PDF ──────────────────────────
    _run([sys.executable, "run_unified_pipeline.py",
          "--match_folder", str(match_folder),
          "--player_a", player_a, "--player_b", player_b],
         PROJECT_ROOT, "6/7  Win prediction + fusion + commentary + PDF")

    # ── 7. Annotated verification video (court + net + players + shuttle,
    #      one file) -- --mark_rallies renders the FULL original video with
    #      a "RALLY DETECTED" marker only during detected windows, rather
    #      than trimming to just those windows. The rally model isn't
    #      100% accurate; a trimmed (--rallies_only) video would make a
    #      missed rally silently disappear, whereas the full video with a
    #      marker lets you scrub past a real rally with no marker on it
    #      and immediately see it was missed. ──
    annotated_video = match_folder / f"{name}_annotated.mp4"
    if not make_annotated_video:
        pass
    elif annotated_video.exists():
        print(f"\n[skip] Annotated verification video -- {annotated_video} exists")
    else:
        _run([sys.executable, "analysis/annotate_video.py",
              "--match_folder", str(match_folder), "--mark_rallies"],
             PROJECT_ROOT, "7/7  Annotated verification video "
                           "(court + net + players + shuttle)")

    out_dir = match_folder / "unified"
    print(f"\n{'='*70}\n  DONE -- {out_dir}\n{'='*70}")
    return out_dir


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", required=True, help="Path to the raw match video")
    ap.add_argument("--match_name", default=None,
                    help="Match folder name (default: video filename without extension)")
    ap.add_argument("--player_a", default="Player A", help="FAR player (top of frame)")
    ap.add_argument("--player_b", default="Player B", help="NEAR player (bottom of frame)")
    ap.add_argument("--width", type=int, default=1280,
                    help="Target width -- the source video is scaled to this "
                         "(ffmpeg) if it doesn't already match, before anything "
                         "else runs. Matches this pipeline's video_fixed/ convention.")
    ap.add_argument("--height", type=int, default=720, help="Target height, see --width")
    ap.add_argument("--fps", type=float, default=30.0,
                    help="Target frame rate -- the source video is resampled "
                         "to this if it doesn't already match (default 30.0)")
    ap.add_argument("--court_mode", choices=["auto", "manual"], default="auto",
                    help="auto = zero-click white-line detection (see "
                         "analysis/auto_court.py -- snaps to the actual "
                         "painted boundary, not just the green floor). "
                         "manual = click 4 corners + net cable once (slower, "
                         "matches this pipeline's benchmarked accuracy).")
    ap.add_argument("--court_type", choices=["singles", "doubles"], default="singles",
                    help="Which sideline pair --court_mode auto should snap "
                         "to (default: singles). No effect on --court_mode "
                         "manual -- you click whichever lines you want there.")
    ap.add_argument("--player_model", default="yolo11x.pt",
                    help="YOLO11 weights for player detection")
    ap.add_argument("--broadcast", action="store_true", dest="broadcast_mode",
                    help="Full broadcast video with intro/crowd cutaways/replays "
                         "mixed in, not a pre-trimmed rally-only clip. Scans for "
                         "the court-present time ranges first, then runs shuttle "
                         "and player detection ONLY on those (see "
                         "analysis/extract_segments.py) instead of the whole "
                         "video. Off by default -- it's extra up-front work "
                         "(the presence scan + ffmpeg cuts) with no benefit if "
                         "the camera angle is already constant throughout.")
    ap.add_argument("--court_search_step_sec", type=float, default=5.0,
                    help="--broadcast: candidate spacing in seconds when "
                         "searching for a reference frame that shows the "
                         "court (default 5.0)")
    ap.add_argument("--court_search_start_frame", type=int, default=None,
                    help="--broadcast: try this frame first instead of the "
                         "video midpoint -- use if you already know roughly "
                         "where play starts")
    ap.add_argument("--no_annotated_video", action="store_false", dest="make_annotated_video",
                    help="Skip generating the final court+net+players+shuttle "
                         "verification video (analysis/annotate_video.py "
                         "--mark_rallies). On by default.")
    args = ap.parse_args()

    run_full_pipeline(args.video, args.match_name, args.player_a, args.player_b,
                      args.width, args.height, args.fps, args.court_mode, args.court_type,
                      args.player_model, args.broadcast_mode,
                      args.court_search_step_sec, args.court_search_start_frame,
                      args.make_annotated_video)


if __name__ == "__main__":
    main()
