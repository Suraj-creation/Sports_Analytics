import os
import argparse
import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm

import torch
from torch.utils.data import DataLoader

from dataset import Video_IterableDataset
from test import predict_location
from utils.general import *

# =========================================================
# SHUTTLE PREDICTION LOGIC
# =========================================================
def predict(indices, y_pred, img_scaler):
    """
    Convert TrackNet heatmaps to (x, y, visibility)
    """

    pred = {'Frame': [], 'X': [], 'Y': [], 'Visibility': []}

    CONF_TH = 0.26  # heatmap confidence threshold

    y_pred = (y_pred > 0.5).cpu().numpy()
    y_pred = to_img_format(y_pred)
    indices = indices.cpu().numpy()

    for n in range(indices.shape[0]):
        for f in range(indices.shape[1]):
            frame_id = int(indices[n][f][1])
            heatmap = y_pred[n][f]

            if heatmap.max() >= CONF_TH:
                bbox = predict_location(to_img(heatmap))
                cx = int((bbox[0] + bbox[2] / 2) * img_scaler[0])
                cy = int((bbox[1] + bbox[3] / 2) * img_scaler[1])
                vis = 1
            else:
                cx, cy, vis = 0, 0, 0

            pred['Frame'].append(frame_id)
            pred['X'].append(cx)
            pred['Y'].append(cy)
            pred['Visibility'].append(vis)

    return pred


# =========================================================
# MAIN
# =========================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video_file', required=True)
    parser.add_argument('--tracknet_file', required=True)
    parser.add_argument('--save_dir', default='output_shuttle')
    parser.add_argument('--batch_size', type=int, default=1)
    args = parser.parse_args()

    os.makedirs(args.save_dir, exist_ok=True)

    # -----------------------------------------------------
    # DEVICE
    # -----------------------------------------------------
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device:", device)

    # -----------------------------------------------------
    # LOAD MODEL
    # -----------------------------------------------------
    ckpt = torch.load(args.tracknet_file, map_location=device)

    seq_len = ckpt['param_dict']['seq_len']
    bg_mode = ckpt['param_dict']['bg_mode']

    model = get_model('TrackNet', seq_len, bg_mode)
    model.load_state_dict(ckpt['model'])
    model = model.to(device)
    model.eval()

    # -----------------------------------------------------
    # VIDEO INFO
    # -----------------------------------------------------
    cap = cv2.VideoCapture(args.video_file)
    if not cap.isOpened():
        raise RuntimeError("❌ Cannot open video")

    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    img_scaler = (w / WIDTH, h / HEIGHT)

    print(f"Video size: {w}x{h}")
    print(f"Total frames: {total_frames}")

    # -----------------------------------------------------
    # DATASET (STREAMING → NO MEDIAN FREEZE)
    # -------------------a----------------------------------
    dataset = Video_IterableDataset(
        args.video_file,
        seq_len=seq_len,
        sliding_step=1,
        bg_mode=bg_mode
    )

    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False
    )

    pred_all = {'Frame': [], 'X': [], 'Y': [], 'Visibility': []}

    # -----------------------------------------------------
    # INFERENCE
    # -----------------------------------------------------
    with torch.no_grad():
        for indices, x in tqdm(loader, desc="Tracking shuttle"):
            x = x.float().to(device)
            y_pred = model(x)

            out = predict(indices, y_pred, img_scaler)
            for k in pred_all:
                pred_all[k].extend(out[k])

    # -----------------------------------------------------
    # SAVE CSV
    # -----------------------------------------------------
    df = pd.DataFrame(pred_all)
    df = df.sort_values("Frame").reset_index(drop=True)

    out_csv = os.path.join(
        args.save_dir,
        os.path.basename(args.video_file).replace(".mp4", "_ball.csv")
    )

    df.to_csv(out_csv, index=False)

    print("✅ DONE")
    print("Saved:", out_csv)


if __name__ == "__main__":
    main()

