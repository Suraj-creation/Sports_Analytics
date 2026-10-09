"""
evaluate_rule.py
================
Evaluates the rule engine accuracy vs ground truth labels.

Run:
    cd win_predictor
    python3 evaluate_rule.py --dataset dataset/vk15b_dataset
    python3 evaluate_rule.py --dataset dataset/vk15b_dataset --match Test1_Full
"""

import os, argparse
import pandas as pd

from rule_engine import (
    load_court_from_json,
    analyze_rally_end,
    apply_overrides,
    assign_player_sides,
    extract_player_features,
)

GT_REASON_MAP = {
    'Opponent Out of Bounds':    'out_of_bounds',
    'Opponent Hit the Net':      'hits_net',
    'Winner Shot':               'wins_by_landing',
    'Opponent Failed to Return': 'wins_by_landing',
}

PLAYER_A = 'Player A'
PLAYER_B = 'Player B'


def to_sec(val):
    val = str(val).strip()
    if ':' in val:
        p = val.split(':')
        return int(p[0]) * 60 + int(p[1])
    try:
        return float(val)
    except:
        return 0.0


def run_match(match_folder, fps):
    name        = os.path.basename(match_folder)
    csv_path    = os.path.join(match_folder, f'{name}.csv')
    shu_path    = os.path.join(match_folder, f'{name}_ball_filled.csv')
    crt_path    = os.path.join(match_folder, f'{name}_court.json')
    player_path = os.path.join(match_folder, 'player_detections.csv')
    rally_path  = os.path.join(match_folder, f'{name}_rally.csv')

    for p in [csv_path, shu_path, crt_path]:
        if not os.path.exists(p):
            print(f'  SKIP {name} — missing: {p}')
            return []

    gt_df      = pd.read_csv(csv_path)
    shuttle_df = pd.read_csv(shu_path)
    court      = load_court_from_json(crt_path)

    if not os.path.exists(rally_path):
        print(f'  SKIP {name} — missing rally CSV: {rally_path}')
        return []
    rally_df = pd.read_csv(rally_path)
    if 'End_Frame' not in rally_df.columns:
        print(f'  SKIP {name} — rally CSV has no End_Frame column')
        return []
    print(f'  {name}: {len(rally_df)} rallies, {len(gt_df)} GT rows')

    far_slot  = 'player_1'
    player_df = None
    if os.path.exists(player_path):
        player_df = pd.read_csv(player_path)
        far_slot, _ = assign_player_sides(player_path, court)

    TOL_SEC = 2.0
    gt_df['_end_sec'] = gt_df['end_time'].apply(
        lambda v: to_sec(v) if pd.notna(v) else None)
    valid_gt = gt_df['_end_sec'].notna()

    raw = []
    for _, rrow in rally_df.iterrows():
        ef    = int(rrow['End_Frame'])
        e_sec = to_sec(rrow.get('End_Time', rrow.get('End_Time_sec', 0)))
        s_sec = to_sec(rrow.get('Start_Time', rrow.get('Start_Time_sec', 0)))

        diffs    = (gt_df.loc[valid_gt, '_end_sec'] - e_sec).abs()
        best_loc = diffs.idxmin()
        if pd.isna(best_loc) or diffs[best_loc] > TOL_SEC:
            continue
        gt_row    = gt_df.loc[best_loc]
        gt_winner = str(gt_row.get('win_point_player', '')).strip()
        gt_reason = GT_REASON_MAP.get(str(gt_row.get('win_reason', '')).strip(), 'unknown')

        pf = extract_player_features(player_df, ef, far_slot) if player_df is not None else None
        event, fault_side, conf, feats = analyze_rally_end(shuttle_df, ef, court, fps, pf)
        event, fault_side = apply_overrides(
            event, fault_side, feats, shuttle_df, ef, court, fps,
            player_df=player_df, far_slot=far_slot)

        raw.append({'i': int(rrow.name), 's_sec': s_sec, 'e_sec': e_sec,
                    'event': event, 'fault_side': fault_side, 'conf': conf,
                    'last_hit_side': feats.get('last_hit_side', 'near'),
                    'gt_winner': gt_winner, 'gt_reason': gt_reason})

    def winner_for(fault_side, far_is_a):
        if fault_side == 'unknown':
            return 'unknown'
        far_name, near_name = (PLAYER_A, PLAYER_B) if far_is_a else (PLAYER_B, PLAYER_A)
        return far_name if fault_side == 'near' else near_name

    labeled       = [r for r in raw if r['gt_winner'] != '']
    score_normal  = sum(winner_for(r['fault_side'], True)  == r['gt_winner'] for r in labeled)
    score_flipped = sum(winner_for(r['fault_side'], False) == r['gt_winner'] for r in labeled)
    far_is_a      = score_normal >= score_flipped

    results = []
    for r in raw:
        pred_winner = winner_for(r['fault_side'], far_is_a)
        lh = r['last_hit_side']
        last_hitter = (PLAYER_A if far_is_a else PLAYER_B) if lh == 'far' else \
                      (PLAYER_B if far_is_a else PLAYER_A) if lh == 'near' else '?'
        results.append({
            'match': name, 'rally': r['i'] + 1,
            's_sec': r['s_sec'], 'e_sec': r['e_sec'],
            'pred_winner': pred_winner, 'gt_winner': r['gt_winner'],
            'pred_reason': r['event'], 'gt_reason': r['gt_reason'],
            'winner_ok': pred_winner == r['gt_winner'],
            'reason_ok': r['event'] == r['gt_reason'],
            'conf': r['conf'], 'fault_side': r['fault_side'],
            'last_hitter': last_hitter,
        })
    return results


def print_summary(all_results, label='OVERALL'):
    ev = [r for r in all_results if r['gt_winner'] != '']
    wc = sum(1 for r in ev if r['winner_ok'])
    rc = sum(1 for r in ev if r['reason_ok'])
    n  = len(ev)
    print(f'\n{"="*60}')
    print(f'  {label} — {n} rallies')
    print(f'{"="*60}')
    print(f'  Winner accuracy:     {wc}/{n} = {wc/n*100:.1f}%')
    print(f'  Win reason accuracy: {rc}/{n} = {rc/n*100:.1f}%')
    print(f'\n  Per-class win reason:')
    for cls in ['out_of_bounds', 'hits_net', 'wins_by_landing']:
        sub = [r for r in ev if r['gt_reason'] == cls]
        c   = sum(1 for r in sub if r['reason_ok'])
        if sub:
            print(f'    {cls:<20}: {c}/{len(sub)} = {c/len(sub)*100:.0f}%')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset', default='dataset/vk15b_dataset')
    ap.add_argument('--fps',     type=float, default=30.0)
    ap.add_argument('--match',   default=None)
    args = ap.parse_args()

    if args.match:
        folders = [os.path.join(args.dataset, args.match)]
    else:
        folders = sorted([
            os.path.join(args.dataset, d)
            for d in os.listdir(args.dataset)
            if d.startswith('Test') and os.path.isdir(os.path.join(args.dataset, d))
        ])

    all_results = []
    for folder in folders:
        results = run_match(folder, args.fps)
        if results:
            print_summary(results, os.path.basename(folder))
            all_results.extend(results)

    if len(folders) > 1 and all_results:
        print_summary(all_results)


if __name__ == '__main__':
    main()
