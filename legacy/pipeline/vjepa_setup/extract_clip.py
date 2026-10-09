"""
Cut a short clip out of a video using OpenCV (no ffmpeg required).

Example:
    python extract_clip.py input.mp4 --start 8 --end 11 --out clip.mp4
"""

import argparse
import cv2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video", help="Path to source video file")
    parser.add_argument("--start", type=float, required=True, help="Clip start time (seconds)")
    parser.add_argument("--end", type=float, required=True, help="Clip end time (seconds)")
    parser.add_argument("--out", required=True, help="Output video path (.mp4)")
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        raise SystemExit(f"Could not open video: {args.video}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    start_frame = int(args.start * fps)
    end_frame = int(args.end * fps)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(args.out, fourcc, fps, (width, height))

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    frame_no = start_frame
    written = 0
    while frame_no < end_frame:
        ret, frame = cap.read()
        if not ret:
            break
        writer.write(frame)
        written += 1
        frame_no += 1

    cap.release()
    writer.release()
    print(f"Wrote {written} frames ({written / fps:.2f}s @ {fps:.1f}fps) to {args.out}")


if __name__ == "__main__":
    main()
