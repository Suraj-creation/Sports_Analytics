"""
setup_models.py
===============
One-time training: trains the CNN on ALL labeled clips (no holdout)
and saves models/model_20f.pt for use by predict.py on new videos.

Run AFTER extract_clips.py has populated clips/clips_3c/:

    cd win_predictor
    python3 setup_models.py
"""

import os, sys, argparse
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision.models.video import (
    r3d_18, R3D_18_Weights,
    r2plus1d_18, R2Plus1D_18_Weights,
)
from collections import Counter

from config import (
    DIR, MODELS_DIR, EPOCHS, BATCH_SIZE, LR, SEED,
    CNN_MEAN, CNN_STD, CLASSES,
    LABELS_20F, CLIPS_20F_DIR,
    LABELS_16F, CLIPS_16F_DIR,
    MODEL_20F_PT, MODEL_16F_PT,
    MODEL_RF_PKL,
)

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
MEAN   = np.array(CNN_MEAN, dtype=np.float32)
STD    = np.array(CNN_STD,  dtype=np.float32)


class _ClipDataset(Dataset):
    def __init__(self, df, clips_dir, augment=False):
        self.df        = df.reset_index(drop=True)
        self.clips_dir = clips_dir
        self.augment   = augment

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row  = self.df.iloc[idx]
        clip = np.load(os.path.join(self.clips_dir, row['clip_file'])).astype(np.float32) / 255.0
        if self.augment:
            if np.random.rand() < 0.5:
                clip = clip[:, :, ::-1, :].copy()
            alpha = np.random.uniform(0.8, 1.2)
            beta  = np.random.uniform(-0.12, 0.12)
            clip  = np.clip(clip * alpha + beta, 0.0, 1.0)
            if np.random.rand() < 0.35:
                clip[np.random.randint(0, clip.shape[0])] = 0.0
            if np.random.rand() < 0.35:
                h, w = clip.shape[1], clip.shape[2]
                rh = np.random.randint(h // 6, h // 3)
                rw = np.random.randint(w // 6, w // 3)
                ry = np.random.randint(0, h - rh)
                rx = np.random.randint(0, w - rw)
                clip[:, ry:ry + rh, rx:rx + rw, :] = 0.0
        clip = (clip - MEAN) / STD
        clip = clip.transpose(3, 0, 1, 2)
        return torch.from_numpy(clip.copy()), torch.tensor(int(row['label']), dtype=torch.long)


def _build_model():
    model = r2plus1d_18(weights=R2Plus1D_18_Weights.DEFAULT)
    for p in model.parameters():
        p.requires_grad = False
    for p in model.layer3.parameters():   # layer3 at LR/5 via differential LR
        p.requires_grad = True
    for p in model.layer4.parameters():
        p.requires_grad = True
    in_f = model.fc.in_features
    model.fc = nn.Sequential(
        nn.BatchNorm1d(in_f),
        nn.Linear(in_f, 256),
        nn.ReLU(inplace=True),
        nn.Dropout(0.30),
        nn.Linear(256, len(CLASSES)),
    )
    return model.to(DEVICE)


def _make_optimizer(model, lr):
    layer3_params = list(model.layer3.parameters())
    layer3_ids    = set(id(p) for p in layer3_params)
    other_params  = [p for p in model.parameters()
                     if p.requires_grad and id(p) not in layer3_ids]
    return torch.optim.Adam([
        {'params': layer3_params, 'lr': lr / 5},
        {'params': other_params,  'lr': lr},
    ], weight_decay=1e-4)


def _train(labels_csv, clips_dir, out_path, tag):
    if not os.path.exists(labels_csv):
        print(f'  SKIP {tag} — labels not found: {labels_csv}')
        print('  Run extract_clips.py first.')
        return False

    labels = pd.read_csv(labels_csv)
    if labels.empty:
        print(f'  SKIP {tag} — empty labels file')
        return False

    cnt   = Counter(labels['label'])
    total = len(labels)
    cw    = torch.tensor(
        [total / (len(CLASSES) * cnt.get(c, 1)) for c in range(len(CLASSES))],
        dtype=torch.float32, device=DEVICE)

    dl = DataLoader(
        _ClipDataset(labels, clips_dir, augment=True),
        batch_size=BATCH_SIZE, shuffle=True,
        num_workers=2, pin_memory=True, drop_last=True)

    model     = _build_model()
    criterion = nn.CrossEntropyLoss(weight=cw)
    optimizer = _make_optimizer(model, LR)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)

    print(f'\n  Training {tag}  ({len(labels)} clips, {EPOCHS} epochs, device={DEVICE})')
    for ep in range(1, EPOCHS + 1):
        model.train()
        total_loss, correct, seen = 0.0, 0, 0
        for clips, lbls in dl:
            clips, lbls = clips.to(DEVICE), lbls.to(DEVICE)
            optimizer.zero_grad()
            logits = model(clips)
            loss   = criterion(logits, lbls)
            loss.backward()
            nn.utils.clip_grad_norm_(
                [p for p in model.parameters() if p.requires_grad], 1.0)
            optimizer.step()
            total_loss += loss.item() * len(lbls)
            correct    += (logits.argmax(1) == lbls).sum().item()
            seen       += len(lbls)
        scheduler.step()
        if ep % 5 == 0 or ep == EPOCHS:
            print(f'    ep {ep:02d}  loss={total_loss/seen:.3f}  '
                  f'acc={correct/seen*100:.1f}%')

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    torch.save(model.state_dict(), out_path)
    print(f'  Saved → {out_path}')
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--clips_20f',   default=CLIPS_20F_DIR,
                    help='Directory of 20-frame .npy clips  (default: clips/clips_3c)')
    ap.add_argument('--labels_20f',  default=LABELS_20F,
                    help='Labels CSV for 20f clips  (default: labels_3c.csv)')
    ap.add_argument('--clips_16f',   default=CLIPS_16F_DIR,
                    help='Directory of 16-frame .npy clips  (default: clips/clips_16f)')
    ap.add_argument('--labels_16f',  default=LABELS_16F,
                    help='Labels CSV for 16f clips  (default: labels_16f.csv)')
    ap.add_argument('--cnn_preds',   default=None,
                    help='CNN ensemble predictions CSV (e.g. vk15b2/netcnn/ens_20r2_16r2.csv). '
                         'Required to train the trajectory RF meta-learner.')
    ap.add_argument('--dataset',     default=os.path.join(DIR, 'dataset', 'vk15b_dataset'),
                    help='Dataset dir with <match>/<match>_ball_filled.csv etc.')
    args = ap.parse_args()

    print('=' * 60)
    print('  win_predictor — Deployment Model Training')
    print(f'  Device : {DEVICE}')
    print('=' * 60)

    torch.manual_seed(SEED)
    np.random.seed(SEED)

    ok20 = _train(
        labels_csv=args.labels_20f,
        clips_dir =args.clips_20f,
        out_path  =MODEL_20F_PT,
        tag       ='20-frame model',
    )

    torch.manual_seed(SEED)
    np.random.seed(SEED)

    ok16 = _train(
        labels_csv=args.labels_16f,
        clips_dir =args.clips_16f,
        out_path  =MODEL_16F_PT,
        tag       ='16-frame model',
    )

    print()
    if ok20 and ok16:
        print('  Both CNN checkpoints ready (model_20f.pt + model_16f.pt).')
    elif ok20:
        print('  model_20f.pt ready.  model_16f.pt not saved (labels_16f.csv missing?).')
        print('  Run extract_clips.py with --seq_len 90 to build the 16f clip set.')
    else:
        print('  WARNING: checkpoints not saved — see errors above.')

    # ── Trajectory RF meta-learner ─────────────────────────────────────────────
    if args.cnn_preds:
        if not os.path.exists(args.cnn_preds):
            print(f'\n  WARNING: --cnn_preds file not found: {args.cnn_preds}')
        elif not os.path.isdir(args.dataset):
            print(f'\n  WARNING: --dataset dir not found: {args.dataset}')
        else:
            print('\n  Training trajectory RF meta-learner...')
            from traj_rf import train_rf, save_rf
            rf = train_rf(args.cnn_preds, args.dataset)
            save_rf(rf, MODEL_RF_PKL)
            print('  RF meta-learner ready.')
    else:
        print('\n  NOTE: Skipping RF training (no --cnn_preds given).')
        print('  To enable trajectory RF, re-run with:')
        print('    python3 setup_models.py --cnn_preds ../vk15b2/netcnn/ens_20r2_16r2.csv \\')
        print('                            --dataset   ../vk15b2/vk15b_dataset')

    print('\n  Next: run predict.py on a new match folder:')
    print('    python3 predict.py --match_folder /path/to/TestN_Full \\')
    print('                        --video /path/to/TestN_Full.mp4')


if __name__ == '__main__':
    main()
