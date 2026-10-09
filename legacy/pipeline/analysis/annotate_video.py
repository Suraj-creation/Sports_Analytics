"""
annotate_video.py
------------------
Single visual sanity check for everything the pipeline detected: draws the
court boundary + net line, both players, and the shuttle (with a short
trail) on one output video.

By default renders the whole video (or --start/--end). Two purpose-built
modes for verifying rally detection itself, not just what was detected:

  --rallies_only   Trimmed + joined: skip straight to the detected rally
                    windows (from <name>_rally.csv), concatenated into one
                    short output. Fast, good for checking each DETECTED
                    rally really is one -- but a rally the model missed
                    entirely is just silently absent, nothing to see.

  --mark_rallies   Full-length, untrimmed: every frame of the original
                    video is kept, but a "RALLY DETECTED" marker (border +
                    label) only appears during frames inside a detected
                    rally window. Scrub the whole thing and any real rally
                    playing out WITHOUT the marker on screen is a missed
                    detection -- this is what --rallies_only structurally
                    can't show you. Court/net/player/shuttle overlays are
                    still drawn wherever data exists, marker or not.

Usage:
    python analysis/annotate_video.py --match_folder YourMatch
    python analysis/annotate_video.py --match_folder YourMatch --start 0 --end 900  # first 30s @30fps
    python analysis/annotate_video.py --match_folder YourMatch --rallies_only
    python analysis/annotate_video.py --match_folder YourMatch --mark_rallies
"""
import argparse
import json
import os
import subprocess

import cv2
import numpy as np
import pandas as pd


def load_court(path):
    with open(path) as f:
        data = json.load(f)
    c = data["corners"]
    if isinstance(c, dict):
        pts = np.array([c["TL"], c["TR"], c["BR"], c["BL"]], dtype=np.int32)
    else:
        pts = np.array(c, dtype=np.int32)
    net_Y = data.get("net", {}).get("net_Y")
    return pts, net_Y


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--match_folder", required=True)
    ap.add_argument("--video", default=None, help="Default: <match_folder>/<name>.mp4")
    ap.add_argument("--shuttle_csv", default=None,
                    help="Default: <match_folder>/<name>_ball_filled.csv")
    ap.add_argument("--player_csv", default=None,
                    help="Default: <match_folder>/player_detections.csv")
    ap.add_argument("--court_json", default=None,
                    help="Default: <match_folder>/<name>_court.json")
    ap.add_argument("--court_presence_csv", default=None,
                    help="Default: <match_folder>/<name>_court_presence.csv (from "
                         "analysis/court_presence.py, --broadcast mode only). If "
                         "found, the court/net overlay is only drawn on frames "
                         "marked court_present -- otherwise it'd be drawn over "
                         "every frame including crowd shots/replays/cutaways "
                         "where the court genuinely isn't there. Missing file "
                         "(e.g. a pre-trimmed rally-only clip, not --broadcast) "
                         "means the whole video is assumed to be court footage, "
                         "same as before -- always drawn.")
    ap.add_argument("--out", default=None,
                    help="Default: <match_folder>/<name>_annotated.mp4")
    ap.add_argument("--trail", type=int, default=10,
                    help="Shuttle trail length in frames (default: 10)")
    ap.add_argument("--start", type=int, default=0, help="First frame (default: 0)")
    ap.add_argument("--end", type=int, default=None,
                    help="Last frame, exclusive (default: whole video)")
    ap.add_argument("--rallies_only", action="store_true",
                    help="Skip non-rally footage entirely -- only render the "
                         "frame windows from <name>_rally.csv (padded by "
                         "--rally_pad_sec each side), concatenated. Overrides "
                         "--start/--end. Mutually exclusive with --mark_rallies.")
    ap.add_argument("--mark_rallies", action="store_true",
                    help="Render the WHOLE original video, unshortened, with a "
                         "\"RALLY DETECTED\" marker only during frames inside a "
                         "detected rally window -- lets you spot rallies the "
                         "model missed entirely (see module docstring). "
                         "Mutually exclusive with --rallies_only.")
    ap.add_argument("--rallies_csv", default=None,
                    help="Default: <match_folder>/<name>_rally.csv")
    ap.add_argument("--rally_pad_sec", type=float, default=1.0,
                    help="Padding around each rally window in seconds (default 1.0)")
    args = ap.parse_args()
    if args.rallies_only and args.mark_rallies:
        raise SystemExit("--rallies_only and --mark_rallies are mutually exclusive "
                         "(one trims the video, the other deliberately doesn't)")

    match_folder = args.match_folder.rstrip("/")
    name = os.path.basename(match_folder)
    video       = args.video       or os.path.join(match_folder, f"{name}.mp4")
    shuttle_csv = args.shuttle_csv or os.path.join(match_folder, f"{name}_ball_filled.csv")
    player_csv  = args.player_csv  or os.path.join(match_folder, "player_detections.csv")
    court_json  = args.court_json  or os.path.join(match_folder, f"{name}_court.json")
    out_path    = args.out         or os.path.join(match_folder, f"{name}_annotated.mp4")
    presence_csv = args.court_presence_csv or os.path.join(match_folder, f"{name}_court_presence.csv")

    court_pts, net_Y = (None, None)
    if os.path.exists(court_json):
        court_pts, net_Y = load_court(court_json)
        print(f"  Court: {court_pts.tolist()}  net_Y={net_Y}")
    else:
        print(f"  No court file at {court_json} -- skipping court/net overlay")

    # None = no presence data -- draw the overlay on every frame (matches old
    # behaviour, correct for a pre-trimmed rally-only clip that's all court
    # footage). A set = only draw on frames actually confirmed court-present,
    # so the overlay doesn't get superimposed over crowd shots/replays/cutaways.
    present_frames = None
    if os.path.exists(presence_csv):
        pres_df = pd.read_csv(presence_csv)
        present_frames = set(pres_df.loc[pres_df["court_present"] == 1, "frame_no"].astype(int))
        print(f"  Court-presence mask: {presence_csv} -- overlay limited to "
              f"{len(present_frames)} confirmed court-present frame(s)")
    else:
        print(f"  No court-presence CSV at {presence_csv} -- overlay drawn on "
              f"every frame (assuming the whole video is court footage)")

    shuttle_map = {}
    if os.path.exists(shuttle_csv):
        df = pd.read_csv(shuttle_csv)
        vis_col = "Visibility" if "Visibility" in df.columns else None
        for _, r in df.iterrows():
            vis = int(r[vis_col]) if vis_col is not None and pd.notna(r[vis_col]) else 1
            shuttle_map[int(r["Frame"])] = (float(r["X"]), float(r["Y"]), vis)
        print(f"  Shuttle: {len(shuttle_map)} frames loaded")
    else:
        print(f"  No shuttle CSV at {shuttle_csv} -- skipping shuttle overlay")

    player_map = {}
    if os.path.exists(player_csv):
        pdf = pd.read_csv(player_csv)
        for _, r in pdf.iterrows():
            pts = []
            for i in (1, 2):
                x, y = r.get(f"player_{i}_x"), r.get(f"player_{i}_y")
                if pd.notna(x) and pd.notna(y):
                    pts.append((float(x), float(y)))
            player_map[int(r["frame_no"])] = pts
        print(f"  Players: {len(player_map)} frames loaded")
    else:
        print(f"  No player CSV at {player_csv} -- skipping player overlay")

    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video}")
    fps   = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w     = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h     = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # windows: list of (start_frame, end_frame_exclusive) to render. Default
    # is one window (--start/--end, or the whole video). --rallies_only
    # replaces it with one window per detected rally, padded, so non-rally
    # footage is never even decoded. --mark_rallies always renders the
    # single (0, total) window -- rally_marker_windows (below) is the
    # separate, inclusive-frame-range list used only to decide when to draw
    # the marker, kept unpadded so it reflects exactly what was detected.
    rally_marker_windows = None
    if args.rallies_only or args.mark_rallies:
        rallies_csv = args.rallies_csv or os.path.join(match_folder, f"{name}_rally.csv")
        if not os.path.exists(rallies_csv):
            raise SystemExit(f"--rallies_only/--mark_rallies need {rallies_csv} "
                             f"(run analysis/detect_rallies.py first)")
        rdf = pd.read_csv(rallies_csv)

    if args.rallies_only:
        pad = int(args.rally_pad_sec * fps)
        windows = [
            (max(0, int(r["Start_Frame"]) - pad), min(total, int(r["End_Frame"]) + pad + 1))
            for _, r in rdf.iterrows()
        ]
        print(f"  --rallies_only: {len(windows)} rally window(s) from {rallies_csv} "
              f"(+/-{args.rally_pad_sec}s padding)")
    elif args.mark_rallies:
        windows = [(0, total)]
        rally_marker_windows = sorted(
            (int(r["Start_Frame"]), int(r["End_Frame"])) for _, r in rdf.iterrows())
        print(f"  --mark_rallies: rendering the full {total}-frame video, "
              f"marking {len(rally_marker_windows)} detected rally window(s) "
              f"from {rallies_csv}")
    else:
        end = args.end if args.end is not None else total
        windows = [(args.start, end)]

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    # cv2.VideoWriter's mp4v fourcc (MPEG-4 Part 2) plays fine in VLC/most
    # desktop players and OpenCV itself, but no modern browser's <video> tag
    # supports it -- only H.264/VP9/AV1, so this file would just be a black
    # box with no error if played in a browser (e.g. the webapp review UI).
    # Write with cv2 to a temp file (the only writer backend reliably
    # available), then transcode to real H.264 via ffmpeg for the actual
    # output -- same encoding convention as video_utils.py elsewhere in
    # this pipeline.
    raw_path = os.path.splitext(out_path)[0] + "_raw.mp4"
    writer = cv2.VideoWriter(raw_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

    net_x_min = int(court_pts[:, 0].min()) if court_pts is not None else 0
    net_x_max = int(court_pts[:, 0].max()) if court_pts is not None else w
    player_colors = [(255, 0, 0), (0, 128, 255)]  # BGR: blue=P1(far-slot), orange=P2

    total_written = 0
    rw_ptr = 0  # pointer into rally_marker_windows -- frames are visited in
                # increasing order across the whole pass, so this only moves forward
    for win_idx, (win_start, win_end) in enumerate(windows):
        cap.set(cv2.CAP_PROP_POS_FRAMES, win_start)
        trail = []
        frame_idx = win_start
        print(f"  Writing frames [{win_start}, {win_end}) -> {out_path}"
              + (f"  (window {win_idx+1}/{len(windows)})" if len(windows) > 1 else ""))
        while frame_idx < win_end:
            ret, frame = cap.read()
            if not ret:
                break

            court_here = present_frames is None or frame_idx in present_frames
            if court_pts is not None and court_here:
                cv2.polylines(frame, [court_pts], True, (0, 255, 0), 2)
                for pt in court_pts:
                    cv2.circle(frame, tuple(int(v) for v in pt), 5, (0, 255, 255), -1)
            if net_Y is not None and court_here:
                cv2.line(frame, (net_x_min, int(net_Y)), (net_x_max, int(net_Y)), (0, 0, 255), 2)

            for i, (x, y) in enumerate(player_map.get(frame_idx, [])):
                color = player_colors[i % 2]
                cv2.circle(frame, (int(x), int(y)), 8, color, -1)
                cv2.putText(frame, f"P{i+1}", (int(x) + 10, int(y) - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            if frame_idx in shuttle_map:
                trail.append(shuttle_map[frame_idx])
            trail = trail[-args.trail:]
            n = len(trail)
            for j, (sx, sy, vis) in enumerate(trail):
                if not vis:
                    continue
                radius = max(2, int(6 * (j + 1) / max(n, 1)))
                cv2.circle(frame, (int(sx), int(sy)), radius, (0, 255, 255), -1)

            in_rally = False
            if rally_marker_windows is not None:
                while (rw_ptr < len(rally_marker_windows)
                      and frame_idx > rally_marker_windows[rw_ptr][1]):
                    rw_ptr += 1
                in_rally = (rw_ptr < len(rally_marker_windows)
                           and rally_marker_windows[rw_ptr][0] <= frame_idx
                           <= rally_marker_windows[rw_ptr][1])
            if in_rally:
                # Thick green border -- the whole point is to be impossible to
                # miss while scrubbing, so a real rally with no border on
                # screen jumps out as a missed detection.
                cv2.rectangle(frame, (0, 0), (w - 1, h - 1), (0, 255, 0), 8)
                cv2.putText(frame, "RALLY DETECTED", (20, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            label = f"Frame {frame_idx}/{total}"
            if len(windows) > 1:
                label += f"  Rally {win_idx+1}/{len(windows)}"
            cv2.putText(frame, label, (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            writer.write(frame)
            frame_idx += 1
            total_written += 1
            if frame_idx % 1000 == 0:
                print(f"    {frame_idx}/{win_end}")

    cap.release()
    writer.release()
    if args.rallies_only:
        print(f"  {total_written} frames written (skipped the rest of a "
              f"{total}-frame video)")
    elif args.mark_rallies:
        marked = sum(min(e, total - 1) - s + 1 for s, e in rally_marker_windows)
        print(f"  {total_written} frames written, full video kept -- "
              f"{marked} of them ({100*marked/max(total_written,1):.1f}%) fall "
              f"inside a detected rally window and are marked")

    print(f"  Transcoding to browser-compatible H.264...")
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", raw_path,
         "-c:v", "libx264", "-preset", "fast", "-crf", "23",
         "-pix_fmt", "yuv420p", out_path],
        check=True,
    )
    os.remove(raw_path)
    print(f"  Saved -> {out_path}")


if __name__ == "__main__":
    main()
