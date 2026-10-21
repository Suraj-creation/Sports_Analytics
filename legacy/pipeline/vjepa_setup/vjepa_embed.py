"""
Load V-JEPA 2.1 ViT-B/16 (384) via torch.hub and extract an embedding for a
short video clip (or a time range of a longer video).

Examples:
    # whole file is the clip
    python vjepa_embed.py clip.mp4 --out clip_embedding.npy

    # a 3s window from a longer video
    python vjepa_embed.py full_match.mp4 --start 8 --end 11 --out rally1.npy
"""

import argparse
import numpy as np
import cv2
import torch


def load_video_frames(video_path, start_sec, end_sec, num_frames, crop_box=None):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise SystemExit(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if end_sec is None:
        end_sec = total_frames / fps

    start_frame = int(start_sec * fps)
    end_frame = max(int(end_sec * fps), start_frame + 1)

    indices = set(np.linspace(start_frame, end_frame - 1, num_frames).astype(int).tolist())

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    frames = []
    frame_no = start_frame
    while frame_no < end_frame:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_no in indices:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if crop_box is not None:
                x1, y1, x2, y2 = crop_box
                rgb = rgb[y1:y2, x1:x2]
            frames.append(rgb)
        frame_no += 1
    cap.release()

    if not frames:
        raise SystemExit("No frames read from the requested range.")

    while len(frames) < num_frames:
        frames.append(frames[-1])

    return frames[:num_frames]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video", help="Path to video file")
    parser.add_argument("--start", type=float, default=0.0, help="Clip start time (seconds)")
    parser.add_argument("--end", type=float, default=None, help="Clip end time (seconds, default = end of file)")
    parser.add_argument("--frames", type=int, default=64, help="Number of frames to sample for the model")
    parser.add_argument("--out", default="embedding.npy", help="Output .npy path")
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    print("Loading V-JEPA 2.1 ViT-B/16 (384) from torch.hub (this downloads weights on first run)...")
    model, _ = torch.hub.load("facebookresearch/vjepa2", "vjepa2_1_vit_base_384")
    model.eval().to(device)

    print("Loading V-JEPA preprocessor...")
    processor = torch.hub.load("facebookresearch/vjepa2", "vjepa2_preprocessor", crop_size=384)

    print(f"Reading frames from {args.video} ({args.start}s - {args.end if args.end is not None else 'end'})...")
    frames = load_video_frames(args.video, args.start, args.end, args.frames)
    print(f"Loaded {len(frames)} frames, each {frames[0].shape}")

    video_tensor = processor(frames)
    if isinstance(video_tensor, (list, tuple)):
        video_tensor = video_tensor[0]
    if video_tensor.dim() == 4:
        video_tensor = video_tensor.unsqueeze(0)
    video_tensor = video_tensor.to(device)

    print(f"Model input tensor shape: {tuple(video_tensor.shape)}")

    with torch.no_grad():
        output = model(video_tensor)

    if isinstance(output, (list, tuple)):
        output = output[0]

    print(f"Output embedding shape: {tuple(output.shape)}")
    np.save(args.out, output.cpu().numpy())
    print(f"Saved embedding to {args.out}")


if __name__ == "__main__":
    main()
