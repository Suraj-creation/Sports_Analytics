"""
train_cnn.py
============
Leave-one-match-out 3-class CNN (OOB / HN / WBL) using r3d-18.

Trains on clips produced by extract_clips.py.
Writes per-rally softmax probabilities to predictions_3c.csv — these
are used by evaluate_fusion.py to compute the fused accuracy.

Run:
    cd win_predictor
    python3 train_cnn.py
    python3 train_cnn.py --clips_dir clips/clips_3c \
                          --label_csv labels_3c.csv \
                          --out       predictions_3c.csv
"""

import os, sys, argparse
from collections import Counter

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision.models.video import r3d_18, R3D_18_Weights

from config import (
    CLASSES, EPOCHS, BATCH_SIZE, LR, SEED, CNN_MEAN, CNN_STD,
    CLIPS_20F_DIR, LABELS_20F,
)

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
MEAN   = np.array(CNN_MEAN, dtype=np.float32)
STD    = np.array(CNN_STD,  dtype=np.float32)


# ── dataset ────────────────────────────────────────────────────────────────

def _augment_clip(clip):
    if np.random.rand() < 0.5:
        clip = clip[:, :, ::-1, :].copy()
    clip = np.clip(clip + np.random.uniform(-0.1, 0.1), 0.0, 1.0)
    return clip


class ClipDataset(Dataset):
    def __init__(self, df, clips_dir, augment=False):
        self.df        = df.reset_index(drop=True)
        self.clips_dir = clips_dir
        self.augment   = augment

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row  = self.df.iloc[idx]
        clip = np.load(os.path.join(self.clips_dir, row['clip_file']))
        clip = clip.astype(np.float32) / 255.0  # (N, 112, 112, 3)

        if self.augment:
            clip = _augment_clip(clip)

        clip = (clip - MEAN) / STD
        clip = clip.transpose(3, 0, 1, 2)       # → (3, N, 112, 112)

        return (
            torch.from_numpy(clip.copy()),
            torch.tensor(int(row['label']), dtype=torch.long),
        )


# ── model ──────────────────────────────────────────────────────────────────

def build_model():
    model = r3d_18(weights=R3D_18_Weights.DEFAULT)
    for p in model.parameters():
        p.requires_grad = False
    for p in model.layer4.parameters():
        p.requires_grad = True
    model.fc = nn.Linear(model.fc.in_features, len(CLASSES))
    return model.to(DEVICE)


# ── training loop ──────────────────────────────────────────────────────────

def _run_epoch(model, loader, optimizer, criterion, train=True):
    model.train(train)
    total_loss, correct, n = 0.0, 0, 0
    for clips, labels in loader:
        clips, labels = clips.to(DEVICE), labels.to(DEVICE)
        if train:
            optimizer.zero_grad()
        with torch.set_grad_enabled(train):
            logits = model(clips)
            loss   = criterion(logits, labels)
        if train:
            loss.backward()
            nn.utils.clip_grad_norm_(
                [p for p in model.parameters() if p.requires_grad], 1.0)
            optimizer.step()
        total_loss += loss.item() * len(labels)
        correct    += (logits.argmax(1) == labels).sum().item()
        n          += len(labels)
    return total_loss / max(n, 1), correct / max(n, 1)


# ── leave-one-match-out CV ─────────────────────────────────────────────────

def run_loocv(clips_dir, labels_csv, out_csv):
    labels  = pd.read_csv(labels_csv)
    matches = sorted(labels['match'].unique())
    print(f'Loaded {len(labels)} clips from {clips_dir}')
    print(f'Class dist: {dict(Counter(labels["gt_reason"]))}')
    print(f'Device: {DEVICE}  |  epochs={EPOCHS}  lr={LR}')
    print(f'Unfreezing: layer4 + head\n')

    all_results = []

    for test_match in matches:
        torch.manual_seed(SEED)
        np.random.seed(SEED)

        train_df = labels[labels['match'] != test_match]
        test_df  = labels[labels['match'] == test_match]

        cnt   = Counter(train_df['label'])
        total = len(train_df)
        cw    = torch.tensor(
            [total / (len(CLASSES) * cnt.get(c, 1)) for c in range(len(CLASSES))],
            dtype=torch.float32, device=DEVICE)

        print(f'--- FOLD test={test_match} '
              f'(train={len(train_df)}, test={len(test_df)}) ---')

        train_ds = ClipDataset(train_df, clips_dir, augment=True)
        test_ds  = ClipDataset(test_df,  clips_dir, augment=False)
        train_dl = DataLoader(train_ds, batch_size=BATCH_SIZE,
                              shuffle=True,  num_workers=2, pin_memory=True)
        test_dl  = DataLoader(test_ds,  batch_size=BATCH_SIZE,
                              shuffle=False, num_workers=2, pin_memory=True)

        model     = build_model()
        criterion = nn.CrossEntropyLoss(weight=cw)
        optimizer = torch.optim.Adam(
            [p for p in model.parameters() if p.requires_grad],
            lr=LR, weight_decay=1e-4)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer, T_max=EPOCHS)

        best_loss, best_state = float('inf'), None
        for ep in range(1, EPOCHS + 1):
            tr_loss, tr_acc = _run_epoch(model, train_dl, optimizer, criterion)
            va_loss, va_acc = _run_epoch(model, test_dl,  optimizer, criterion,
                                         train=False)
            scheduler.step()
            if ep % 5 == 0 or ep == 1:
                print(f'  ep {ep:3d}  tr={tr_acc:.3f}/{tr_loss:.3f}'
                      f'  te={va_acc:.3f}/{va_loss:.3f}')
            if va_loss < best_loss:
                best_loss  = va_loss
                best_state = {k: v.clone() for k, v in model.state_dict().items()}

        model.load_state_dict(best_state)
        model.eval()
        preds, probs_list, gt_list = [], [], []
        with torch.no_grad():
            for clips, lbls in test_dl:
                logits = model(clips.to(DEVICE))
                probs  = torch.softmax(logits, dim=1).cpu().numpy()
                preds.extend(logits.argmax(1).cpu().tolist())
                probs_list.extend(probs.tolist())
                gt_list.extend(lbls.tolist())

        fold_acc = sum(p == g for p, g in zip(preds, gt_list))
        print(f'  Fold: {fold_acc}/{len(test_df)} = {fold_acc/len(test_df)*100:.1f}%\n')

        for j, row in enumerate(test_df.itertuples()):
            all_results.append({
                'match':     test_match,
                'rally_idx': row.rally_idx,
                'end_frame': row.end_frame,
                'gt':        CLASSES[gt_list[j]],
                'pred':      CLASSES[preds[j]],
                'label':     gt_list[j],
                'cnn_pred':  preds[j],
                'prob_oob':  round(probs_list[j][0], 4),
                'prob_hn':   round(probs_list[j][1], 4),
                'prob_wbl':  round(probs_list[j][2], 4),
                'correct':   int(preds[j] == gt_list[j]),
            })

    _report(all_results, out_csv)
    return all_results


def _report(results, out_csv):
    n       = len(results)
    correct = sum(r['correct'] for r in results)
    print(f'\n{"="*60}')
    print(f'  CNN 3-class — {n} rallies, '
          f'{len(set(r["match"] for r in results))} matches')
    print(f'{"="*60}')
    print(f'  Overall: {correct}/{n} = {correct/n*100:.1f}%\n')

    print('  Per-class:')
    for i, cls in enumerate(CLASSES):
        sub = [r for r in results if r['label'] == i]
        c   = sum(r['correct'] for r in sub)
        if sub:
            print(f'    {cls:<22}: {c}/{len(sub)} = {c/len(sub)*100:.0f}%')

    print('\n  Per-match:')
    for m in sorted(set(r['match'] for r in results)):
        sub = [r for r in results if r['match'] == m]
        c   = sum(r['correct'] for r in sub)
        print(f'    {m}: {c}/{len(sub)} = {c/len(sub)*100:.1f}%')

    pd.DataFrame(results).to_csv(out_csv, index=False)
    print(f'\nSaved → {out_csv}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--clips_dir', default=CLIPS_20F_DIR)
    ap.add_argument('--label_csv', default=LABELS_20F)
    ap.add_argument('--out',       default='predictions_3c.csv')
    args = ap.parse_args()

    run_loocv(args.clips_dir, args.label_csv, args.out)


if __name__ == '__main__':
    main()
