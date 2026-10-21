"""
stitch_segments.py
-------------------
Remap per-segment detection CSVs (shuttle or player, frame-indexed 0..N
within each small extracted clip) back to the original broadcast video's
global frame numbers, and concatenate into one CSV -- so everything
downstream (fill_gaps.py, detect_rallies.py, win_predictor) sees a single
normal frame-indexed CSV, unaware that only part of the video was ever
actually processed.

Frames not covered by any segment are simply absent from the output --
fill_gaps.py's bounded gap thresholds already won't try to bridge a large
gap between segments, and detect_rallies.py's scene mask already defaults
missing frames to "not present."

Usage:
    python analysis/stitch_segments.py \\
        --manifest YourMatch/segments/manifest.csv \\
        --csv_glob "output_shuttle/seg_*_ball_clean.csv" \\
        --frame_col Frame \\
        --out output_shuttle/YourMatch_ball_clean.csv
"""
import argparse
import glob
import re

import pandas as pd


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", required=True,
                    help="manifest.csv from extract_segments.py")
    ap.add_argument("--csv_glob", required=True,
                    help="Glob pattern matching each segment's local CSV, "
                         "one file per seg_NNN clip (e.g. "
                         "'output_shuttle/seg_*_ball_clean.csv'). Matched "
                         "to manifest rows by the seg_NNN index in the filename.")
    ap.add_argument("--frame_col", default="Frame",
                    help="Frame-number column to offset (default: Frame; "
                         "use frame_no for player_detections-style CSVs)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    manifest = pd.read_csv(args.manifest)
    files = sorted(glob.glob(args.csv_glob))
    if not files:
        raise SystemExit(f"No files matched --csv_glob: {args.csv_glob}")

    seg_re = re.compile(r"seg_(\d+)")
    pieces = []
    for path in files:
        # Take the LAST "seg_NNN" match in the full path, not the first and
        # not basename-only. Shuttle CSVs carry the index in the FILENAME
        # (seg_000_ball_clean.csv); player CSVs carry it in the PARENT
        # DIRECTORY instead (segments/players/seg_000/player_detections.csv,
        # a fixed filename with no index in it at all) -- so neither
        # "first match in full path" nor "basename only" handles both.
        # The match folder name can ALSO look like "seg_NNN" (e.g. a match
        # named "seg_009" from a source file called seg_009.mp4), but that
        # always appears EARLIER in the path than the real segment
        # component, whichever form it takes -- so the last match is always
        # the right one, regardless of which of the two layouts this is.
        matches = list(seg_re.finditer(path))
        m = matches[-1] if matches else None
        if not m:
            print(f"  Skipping (no seg_NNN in filename): {path}")
            continue
        seg_idx = int(m.group(1))
        row = manifest[manifest["seg_idx"] == seg_idx]
        if row.empty:
            print(f"  Skipping (seg_idx {seg_idx} not in manifest): {path}")
            continue
        start_frame = int(row.iloc[0]["start_frame"])

        df = pd.read_csv(path)
        if args.frame_col not in df.columns:
            raise SystemExit(f"--frame_col '{args.frame_col}' not found in {path} "
                             f"(columns: {list(df.columns)})")
        df[args.frame_col] = df[args.frame_col].astype(int) + start_frame
        pieces.append(df)
        print(f"  seg_{seg_idx:03d}: {len(df)} rows, frame offset +{start_frame}")

    if not pieces:
        raise SystemExit("Nothing to stitch -- no matched segment files.")

    stitched = pd.concat(pieces, ignore_index=True)
    stitched = stitched.sort_values(args.frame_col).reset_index(drop=True)
    stitched.to_csv(args.out, index=False)
    print(f"  Stitched {len(stitched)} total rows -> {args.out}")


if __name__ == "__main__":
    main()
