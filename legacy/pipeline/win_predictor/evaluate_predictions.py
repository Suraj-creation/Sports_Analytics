"""
evaluate_predictions.py
========================
Scores win_predictions.csv (from predict.py) against real ground truth in
vk15b_dataset/<match>/<match>.csv: winner + win_reason accuracy, confusion
matrix, per-decision-path breakdown, per-match table. See
docs/10_evaluation.md for full methodology and the current baseline.

Run:
    cd win_predictor
    python3 evaluate_predictions.py [--dataset /path/to/vk15b_dataset]
"""

import argparse
import os
import pandas as pd

GT_REASON_MAP = {
    'Opponent Out of Bounds':    'out_of_bounds',
    'Opponent Hit the Net':      'hits_net',
    'Winner Shot':               'wins_by_landing',
    'Opponent Failed to Return': 'wins_by_landing',
}
SHORT = {'out_of_bounds': 'OOB', 'hits_net': 'HN', 'wins_by_landing': 'WBL'}


def to_sec(val):
    val = str(val).strip()
    if ':' in val:
        p = val.split(':')
        return int(p[0]) * 60 + int(p[1])
    return float(val)


def evaluate(match, dataset_dir):
    """Match predicted rallies to GT rallies by time-overlap (IoU>=0.3),
    not row order -- detected and GT rally counts don't always agree."""
    gt   = pd.read_csv(os.path.join(dataset_dir, match, f'{match}.csv'))
    pred = pd.read_csv(os.path.join(dataset_dir, match, 'win_predictions.csv'))

    gt['s'] = gt['start_time'].apply(to_sec)
    gt['e'] = gt['end_time'].apply(to_sec)
    gt['gt_reason'] = gt['win_reason'].map(lambda x: GT_REASON_MAP.get(str(x).strip(), 'unknown'))
    gt['gt_winner'] = gt['win_point_player'].astype(str).str.strip()

    pred['s'] = pred['start_time'].apply(to_sec)
    pred['e'] = pred['end_time'].apply(to_sec)

    rows = []
    used_gt = set()
    for _, p in pred.iterrows():
        best_iou, best_idx = 0.0, None
        for gi, g in gt.iterrows():
            if gi in used_gt:
                continue
            ov    = max(0.0, min(p['e'], g['e']) - max(p['s'], g['s']))
            union = max(p['e'], g['e']) - min(p['s'], g['s'])
            iou   = ov / union if union > 0 else 0.0
            if iou > best_iou:
                best_iou, best_idx = iou, gi
        if best_idx is not None and best_iou >= 0.3:
            used_gt.add(best_idx)
            g = gt.loc[best_idx]
            rows.append({
                'match': match, 'pred_start': p['start_time'], 'pred_end': p['end_time'],
                'iou': round(best_iou, 3),
                'pred_winner': p['winner'], 'gt_winner': g['gt_winner'],
                'pred_reason': p['win_reason'], 'gt_reason': g['gt_reason'],
                'reason_src': p['reason_src'],
                'winner_correct': p['winner'] == g['gt_winner'],
                'reason_correct': p['win_reason'] == g['gt_reason'],
            })
    n_gt_unmatched   = len(gt) - len(used_gt)
    n_pred_unmatched = len(pred) - len(rows)
    return pd.DataFrame(rows), n_gt_unmatched, n_pred_unmatched, len(gt), len(pred)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset', default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        '..', 'vk15b2', 'vk15b_dataset'))
    ap.add_argument('--out', default=None,
                    help='Optional path to save per-rally detailed CSV')
    args = ap.parse_args()

    matches = sorted(d for d in os.listdir(args.dataset)
                     if d.startswith('Test') and os.path.isdir(os.path.join(args.dataset, d))
                     and os.path.exists(os.path.join(args.dataset, d, 'win_predictions.csv')))

    all_dfs, coverage = [], []
    for m in matches:
        df, unmatched_gt, unmatched_pred, n_gt, n_pred = evaluate(m, args.dataset)
        all_dfs.append(df)
        coverage.append((m, n_gt, n_pred, len(df), unmatched_gt, unmatched_pred))

    combined = pd.concat(all_dfs, ignore_index=True)
    if args.out:
        combined.to_csv(args.out, index=False)

    print(f"=== Match coverage (GT rallies vs predicted vs matched@IoU>=0.3) ===")
    print(f"{'Match':<12}{'GT':>5}{'Pred':>6}{'Matched':>9}{'UnmatchedGT':>13}{'UnmatchedPred':>15}")
    for m, ng, npd, nm, ug, up in coverage:
        print(f"{m:<12}{ng:>5}{npd:>6}{nm:>9}{ug:>13}{up:>15}")

    n = len(combined)
    print(f"\n=== OVERALL ({n} matched rallies across {len(matches)} matches) ===")
    print(f"Win-reason accuracy: {combined['reason_correct'].mean()*100:.1f}%  ({combined['reason_correct'].sum()}/{n})")
    print(f"Winner accuracy:     {combined['winner_correct'].mean()*100:.1f}%  ({combined['winner_correct'].sum()}/{n})")

    print("\n=== Decision-path breakdown (reason_src) ===")
    print(combined['reason_src'].value_counts())
    print("\nWinner / win-reason accuracy per decision path:")
    for src, grp in combined.groupby('reason_src'):
        print(f"  {src:<15} winner={grp['winner_correct'].mean()*100:5.1f}%  "
              f"reason={grp['reason_correct'].mean()*100:5.1f}%  rallies={len(grp)}")

    print("\n=== Win-reason confusion matrix (rows=GT, cols=Predicted) ===")
    combined['gt_short']   = combined['gt_reason'].map(SHORT)
    combined['pred_short'] = combined['pred_reason'].map(SHORT)
    order = ['OOB', 'HN', 'WBL']
    ct = pd.crosstab(combined['gt_short'], combined['pred_short']).reindex(
        index=order, columns=order, fill_value=0)
    print(ct)
    for cls in order:
        tot, correct = ct.loc[cls].sum(), ct.loc[cls, cls]
        print(f"{cls} acc: {correct}/{tot} = {correct/tot*100:.1f}%")

    print("\n=== Failure attribution (of rallies where winner is WRONG) ===")
    wrong = combined[~combined['winner_correct']]
    wrong_reason = wrong[~wrong['reason_correct']]
    right_reason = wrong[wrong['reason_correct']]
    print(f"Total winner failures: {len(wrong)}")
    if len(wrong):
        print(f"  Wrong reason -> wrong winner: {len(wrong_reason)} ({len(wrong_reason)/len(wrong)*100:.0f}%)")
        print(f"  Right reason but wrong winner (fault-side error): {len(right_reason)} ({len(right_reason)/len(wrong)*100:.0f}%)")

    print("\n=== Per-match accuracy ===")
    print(f"{'Match':<12}{'N':>4}{'WinnerAcc':>11}{'ReasonAcc':>11}")
    for m, grp in combined.groupby('match'):
        print(f"{m:<12}{len(grp):>4}{grp['winner_correct'].mean()*100:>10.1f}%{grp['reason_correct'].mean()*100:>10.1f}%")


if __name__ == '__main__':
    main()
