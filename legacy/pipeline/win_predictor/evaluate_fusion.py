"""
evaluate_fusion.py
==================
Compare rule engine vs CNN vs fused accuracy on labeled matches.

Requires:
  - A predictions CSV produced by train_cnn.py (default: predictions_3c.csv)
  - Match folders under dataset/vk15b_dataset with GT labels + ball + rally CSVs

Run:
    cd win_predictor
    python3 evaluate_fusion.py
    python3 evaluate_fusion.py --preds predictions_3c.csv \
                                --dataset dataset/vk15b_dataset
"""

import os, sys, argparse
import pandas as pd
import numpy as np
from collections import Counter

from evaluate_rule import run_match
from config import CLASSES, GLOBAL_THR

FPS     = 30.0
TOL_SEC = 2.0

HN_THR        = 0.60
PER_CLASS_THR = {
    'wins_by_landing': 0.55,
    'out_of_bounds':   0.65,
    'hits_net':        0.60,
}


def _build_rule_preds(dataset):
    matches = sorted(
        d for d in os.listdir(dataset)
        if d.startswith('Test') and os.path.isdir(os.path.join(dataset, d))
    )
    rows = []
    for m in matches:
        print(f'  Rule engine: {m}')
        results = run_match(os.path.join(dataset, m), FPS)
        for r in results:
            if r['gt_reason'] not in CLASSES:
                continue
            rows.append({
                'match':        m,
                'rally_idx':    r['rally'] - 1,
                'gt':           r['gt_reason'],
                'rule_pred':    r['pred_reason'],
                'rule_correct': int(r['reason_ok']),
            })
    return pd.DataFrame(rows)


def _load_merged(preds_csv, dataset):
    print('\nRunning rule engine on all matches...')
    rule = _build_rule_preds(dataset)
    print(f'  Rule engine: {len(rule)} rallies / '
          f'{rule["match"].nunique()} matches')

    cnn = pd.read_csv(preds_csv).rename(columns={
        'pred':     'cnn_pred_str',
        'prob_oob': 'cnn_prob_oob',
        'prob_hn':  'cnn_prob_hn',
        'prob_wbl': 'cnn_prob_wbl',
        'correct':  'cnn_correct',
    })
    print(f'  CNN preds  : {len(cnn)} rallies / '
          f'{cnn["match"].nunique()} matches')

    merged = cnn.merge(rule[['match', 'rally_idx', 'rule_pred', 'rule_correct']],
                       on=['match', 'rally_idx'])
    merged['cnn_conf'] = merged[['cnn_prob_oob', 'cnn_prob_hn', 'cnn_prob_wbl']].max(axis=1)
    print(f'  Merged     : {len(merged)} rallies\n')
    return merged


def _fuse_global(row, thr):
    return int(row['cnn_correct']) if row['cnn_conf'] >= thr \
           else int(row['rule_correct'])


def _fuse_hn_first(row):
    if row['cnn_prob_hn'] >= HN_THR:
        return int(row['cnn_pred_str'] == row['gt'])
    return int(row['rule_correct'])


def _fuse_agree_boost(row):
    if row['cnn_pred_str'] == row['rule_pred']:
        return int(row['cnn_correct'])
    if row['cnn_prob_hn'] >= HN_THR and row['cnn_pred_str'] == 'hits_net':
        return int(row['cnn_correct'])
    return int(row['rule_correct'])


def _fuse_per_class(row):
    thr = PER_CLASS_THR.get(row['cnn_pred_str'], 0.65)
    return int(row['cnn_correct']) if row['cnn_conf'] >= thr \
           else int(row['rule_correct'])


def report(df):
    n  = len(df)
    rc = int(df['rule_correct'].sum())
    cc = int(df['cnn_correct'].sum())

    f_gl = sum(_fuse_global(r, GLOBAL_THR)  for _, r in df.iterrows())
    f_pc = sum(_fuse_per_class(r)            for _, r in df.iterrows())
    f_hn = sum(_fuse_hn_first(r)             for _, r in df.iterrows())
    f_ag = sum(_fuse_agree_boost(r)          for _, r in df.iterrows())
    best = max(f_gl, f_pc, f_hn, f_ag)

    oracle = sum(1 for _, r in df.iterrows()
                 if r['rule_correct'] or r['cnn_correct'])

    print(f'\n{"="*65}')
    print(f'  Fusion — {n} rallies, {df["match"].nunique()} matches')
    print(f'{"="*65}')
    print(f'  Rule engine only         : {rc}/{n} = {rc/n*100:.1f}%')
    print(f'  CNN only                 : {cc}/{n} = {cc/n*100:.1f}%  (Δ{cc-rc:+d})')
    print(f'  ── Fusion ──')
    print(f'  Global conf≥{GLOBAL_THR:.2f} ★       : {f_gl}/{n} = {f_gl/n*100:.1f}%  (Δ{f_gl-rc:+d})')
    print(f'  Per-class threshold      : {f_pc}/{n} = {f_pc/n*100:.1f}%  (Δ{f_pc-rc:+d})')
    print(f'  HN-first (HN_THR={HN_THR})  : {f_hn}/{n} = {f_hn/n*100:.1f}%  (Δ{f_hn-rc:+d})')
    print(f'  Agree-boost              : {f_ag}/{n} = {f_ag/n*100:.1f}%  (Δ{f_ag-rc:+d})')
    print(f'  Best fusion              : {best}/{n} = {best/n*100:.1f}%')
    print(f'  Oracle (rule OR cnn)     : {oracle}/{n} = {oracle/n*100:.1f}%')

    print(f'\n  Per-class (Rule / CNN / Global-fuse / HN-first):')
    print(f'  {"Class":<22}  {"Rule":>8}  {"CNN":>8}  {"Global":>8}  {"HN-1st":>8}')
    print(f'  {"-"*68}')
    for cls in CLASSES:
        sub  = df[df['gt'] == cls]
        r_   = int(sub['rule_correct'].sum())
        c_   = int(sub['cnn_correct'].sum())
        fgl_ = sum(_fuse_global(r, GLOBAL_THR) for _, r in sub.iterrows())
        fhn_ = sum(_fuse_hn_first(r)           for _, r in sub.iterrows())
        nn   = len(sub)
        if nn:
            print(f'  {cls:<22}  {r_}/{nn}={r_/nn*100:3.0f}%'
                  f'   {c_}/{nn}={c_/nn*100:3.0f}%'
                  f'   {fgl_}/{nn}={fgl_/nn*100:3.0f}%'
                  f'   {fhn_}/{nn}={fhn_/nn*100:3.0f}%')

    print(f'\n  Per-match (Rule / CNN / Global-fuse):')
    print(f'  {"Match":<16}  {"Rule":>8}  {"CNN":>8}  {"Global":>8}')
    print(f'  {"-"*50}')
    for m in sorted(df['match'].unique()):
        sub  = df[df['match'] == m]
        r_   = int(sub['rule_correct'].sum())
        c_   = int(sub['cnn_correct'].sum())
        fgl_ = sum(_fuse_global(r, GLOBAL_THR) for _, r in sub.iterrows())
        nn   = len(sub)
        if nn:
            print(f'  {m:<16}  {r_}/{nn}={r_/nn*100:5.1f}%'
                  f'   {c_}/{nn}={c_/nn*100:5.1f}%'
                  f'   {fgl_}/{nn}={fgl_/nn*100:5.1f}%')

    print(f'\n  Agreement overlap:')
    br = int(((df['rule_correct'] == 1) & (df['cnn_correct'] == 1)).sum())
    ro = int(((df['rule_correct'] == 1) & (df['cnn_correct'] == 0)).sum())
    co = int(((df['rule_correct'] == 0) & (df['cnn_correct'] == 1)).sum())
    bw = int(((df['rule_correct'] == 0) & (df['cnn_correct'] == 0)).sum())
    print(f'    Both right : {br}  |  Rule only: {ro}  |  CNN only: {co}  |  Both wrong: {bw}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preds',   default='predictions_3c.csv')
    ap.add_argument('--dataset', default='dataset/vk15b_dataset')
    ap.add_argument('--fps',     type=float, default=FPS)
    args = ap.parse_args()

    df = _load_merged(args.preds, args.dataset)
    report(df)


if __name__ == '__main__':
    main()
