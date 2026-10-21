"""
Train a YOLOv8-pose model to detect the 8 court/net keypoints
(TL, TR, BR, BL, NL, NR, CL, CR) from court_dataset.

Usage:
    python train_court_model.py
    python train_court_model.py --device 1   # use GPU 1 if GPU 0 is busy
"""

import argparse
import os
from ultralytics import YOLO

DATA_YAML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.yaml")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="yolov8n-pose.pt", help="base checkpoint (auto-downloaded)")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default="0", help="GPU index, or 'cpu'")
    args = parser.parse_args()

    model = YOLO(args.model)
    model.train(
        data=DATA_YAML,
        epochs=args.epochs,
        imgsz=args.imgsz,
        device=args.device,
        project="runs/pose",
        name="court_dataset",
    )


if __name__ == "__main__":
    main()
