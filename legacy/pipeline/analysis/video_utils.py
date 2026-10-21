"""
video_utils.py
---------------
Shared "make sure this video is actually something cv2 can decode and the
pipeline's assumptions hold" logic.

cv2.VideoCapture here can't reliably decode AV1 (common for YouTube
downloads -- yt-dlp often defaults to it) -- .read() just returns False on
every frame, no exception, so a script scanning frames for something (a
good annotation frame, court presence, shuttle detection) silently finds
nothing and only fails once it's exhausted its search, with a confusing
error miles away from the real cause. A source at the wrong resolution or
frame rate also silently breaks the pipeline's pixel-coordinate and
frame-count-based assumptions (court.json coordinates, rally duration
math) without ever raising an error at all.

run_full_pipeline.py already normalizes the video once, up front, before
any stage touches it. This module exists so a script run BY ITSELF --
analysis/annotate_court.py, auto_court.py, court_presence.py -- gets the
same guarantee instead of only working when invoked through the full
pipeline.

Usage:
    from video_utils import ensure_preprocessed
    video_path = ensure_preprocessed(args.video)   # use this path from here on
"""
import subprocess
import sys
from pathlib import Path


def probe_video(path):
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


def _matches(path, width, height, fps):
    codec, w, h, f = probe_video(path)
    return codec == "h264" and w == width and h == height and abs(f - fps) < 0.1


def ensure_preprocessed(video_path, width=1280, height=720, fps=30.0, cache_suffix="_prepared"):
    """
    Return a path to a version of video_path that's H.264 at width x height
    @ fps -- the source itself, unchanged, if it already matches; otherwise
    a cached transcoded copy next to it (named <stem><cache_suffix>.mp4),
    reused on subsequent calls instead of re-transcoding every time.
    """
    video_path = Path(video_path)
    if _matches(video_path, width, height, fps):
        return video_path

    cached = video_path.with_name(f"{video_path.stem}{cache_suffix}.mp4")
    if cached.exists() and _matches(cached, width, height, fps):
        return cached

    codec, w, h, src_fps = probe_video(video_path)
    print(f"  {video_path.name}: {w}x{h} @ {src_fps:.2f}fps, codec={codec} -- "
         f"doesn't match the pipeline's expected {width}x{height}@{fps}fps "
         f"H.264 -- transcoding to {cached.name}...")
    cmd = ["ffmpeg", "-y", "-i", str(video_path),
           "-vf", f"scale={width}:{height}", "-r", str(fps),
           "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-an",
           str(cached)]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        sys.exit(f"ERROR: ffmpeg preprocessing failed for {video_path}:\n"
                 f"{res.stderr.decode()[-2000:]}")
    print(f"  Prepared -> {cached}")
    return cached
