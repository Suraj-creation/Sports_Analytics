"""
Run on the GPU machine. Reads dataset/clips_index.csv (produced by
build_clips.py), extracts a V-JEPA 2.1 ViT-B/16 (384) embedding for every
clip, and writes dataset/dataset.csv mapping each embedding file back to its
labels (winner, reason, ball type, scores, ...).

Usage:
    python extract_embeddings.py
"""

import argparse
import csv
import os
import cv2
import numpy as np
import torch

from vjepa_embed import load_video_frames
from court_crop import load_crop_box, COURT_JSON


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default="dataset/clips_index.csv")
    parser.add_argument("--out_dir", default="dataset/embeddings")
    parser.add_argument("--out_csv", default="dataset/dataset.csv")
    parser.add_argument("--frames", type=int, default=64)
    parser.add_argument("--videos_dir", default="dataset/videos",
                         help="folder containing the full source videos, used to size crop boxes")
    parser.add_argument("--no_crop", action="store_true",
                         help="disable court-based cropping (use full frames)")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    crop_boxes = {}
    if not args.no_crop:
        for video, court_json in COURT_JSON.items():
            video_path = os.path.join(args.videos_dir, f"{video}.mp4")
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"Warning: could not open {video_path}, skipping crop for {video}")
                continue
            frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            crop_boxes[video] = load_crop_box(court_json, frame_w, frame_h)
            print(f"Crop box for {video}: {crop_boxes[video]} (frame {frame_w}x{frame_h})")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    print("Loading V-JEPA 2.1 ViT-B/16 (384) from torch.hub...")
    model, _ = torch.hub.load("facebookresearch/vjepa2", "vjepa2_1_vit_base_384")
    model.eval().to(device)

    print("Loading V-JEPA preprocessor...")
    processor = torch.hub.load("facebookresearch/vjepa2", "vjepa2_preprocessor", crop_size=384)

    with open(args.index, newline="") as f:
        rows = list(csv.DictReader(f))

    out_rows = []
    for n, row in enumerate(rows, 1):
        clip_path = row["clip_path"]
        crop_box = crop_boxes.get(row["video"])
        frames = load_video_frames(clip_path, 0.0, None, args.frames, crop_box=crop_box)

        video_tensor = processor(frames)
        if isinstance(video_tensor, (list, tuple)):
            video_tensor = video_tensor[0]
        if video_tensor.dim() == 4:
            video_tensor = video_tensor.unsqueeze(0)
        video_tensor = video_tensor.to(device)

        with torch.no_grad():
            output = model(video_tensor)
        if isinstance(output, (list, tuple)):
            output = output[0]

        emb_name = f"{row['video']}_rally_{int(row['rally']):03d}.npy"
        emb_path = os.path.join(args.out_dir, emb_name)
        np.save(emb_path, output.cpu().numpy())

        out_row = dict(row)
        out_row["embedding_path"] = emb_path
        out_rows.append(out_row)
        print(f"[{n}/{len(rows)}] {row['video']} rally {row['rally']}: "
              f"embedding shape {tuple(output.shape)} -> {emb_path}")

    fieldnames = list(out_rows[0].keys())
    with open(args.out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"\nWrote dataset csv with {len(out_rows)} rows to {args.out_csv}")


if __name__ == "__main__":
    main()
