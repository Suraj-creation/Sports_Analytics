"""
compare_predictors_gt.py
========================
Scores win-predictor variants against the user's manually-watched ground
truth for Test1_Full_rev (35 labeled rallies, chat transcript 2026-07).

GT convention: user rally N == pipeline rally N (user re-aligned numbering,
rally 21 left unlabeled, no rally 36).

Compares:
  v1   — old rule-engine output  (win_predictions_v1.csv)
  new  — new CNN+RF+strategies   (win_predictions.csv)
  cnn  — new run's raw CNN ensemble class (cnn_class column)

Usage:  python analysis/compare_predictors_gt.py
"""
import pandas as pd
from pathlib import Path

MATCH = Path(__file__).resolve().parent.parent / "Test1_Full_rev"

# rally -> (event, winner)   event: HN|OOB|WBL   winner: AN|INT|None
GT = {
    1:  ("OOB", None), 2:  ("HN",  None), 3:  (None,  None), 4:  ("OOB", None),
    5:  ("WBL", None), 6:  ("HN",  "AN"), 7:  ("OOB", None), 8:  ("HN",  "AN"),
    9:  ("WBL", "INT"), 10: ("WBL", None), 11: ("OOB", "AN"), 12: ("HN", "AN"),
    13: ("OOB", "AN"), 14: ("WBL", "AN"), 15: ("WBL", "INT"), 16: ("OOB", "INT"),
    17: ("OOB", "AN"), 18: ("HN",  "AN"), 19: ("HN",  "AN"), 20: ("OOB", "INT"),
    21: (None,  None), 22: ("HN",  "AN"), 23: ("HN",  "AN"), 24: ("HN",  "AN"),
    25: ("HN",  "AN"), 26: ("HN",  "AN"), 27: ("WBL", "INT"), 28: ("HN", "INT"),
    29: ("OOB", "AN"), 30: ("HN",  "AN"), 31: ("OOB", "INT"), 32: ("HN", "AN"),
    33: ("WBL", "AN"), 34: ("HN",  "AN"), 35: ("HN",  "AN"), 36: (None, None),
}

def norm_event(x):
    x = str(x).lower()
    if "net" in x or x == "hn":
        return "HN"
    if "out" in x or "oob" in x:
        return "OOB"
    if "land" in x or "wbl" in x or "winner" in x:
        return "WBL"
    return "?"

def norm_winner(x):
    x = str(x).lower()
    if "an" in x and "intanon" not in x:
        return "AN"
    if "intanon" in x:
        return "INT"
    return "?"

def score(name, events, winners):
    ev_ok = ev_n = wn_ok = wn_n = hn_ok = hn_n = 0
    rows = []
    for r in range(1, 37):
        gt_ev, gt_wn = GT[r]
        pe, pw = events.get(r), winners.get(r)
        mark_ev = mark_wn = "-"
        if gt_ev and pe:
            ev_n += 1
            hit = pe == gt_ev
            ev_ok += hit
            mark_ev = "OK" if hit else f"{pe}!={gt_ev}"
            if gt_ev == "HN":
                hn_n += 1
                hn_ok += hit
        if gt_wn and pw:
            wn_n += 1
            hit = pw == gt_wn
            wn_ok += hit
            mark_wn = "OK" if hit else f"{pw}!={gt_wn}"
        rows.append((r, mark_ev, mark_wn))
    print(f"\n=== {name} ===")
    print(f"  event accuracy : {ev_ok}/{ev_n} = {ev_ok/ev_n:.0%}")
    print(f"  net-hit recall : {hn_ok}/{hn_n} = {hn_ok/hn_n:.0%}")
    if wn_n:
        print(f"  winner accuracy: {wn_ok}/{wn_n} = {wn_ok/wn_n:.0%}")
    return rows

# v1 (old rule engine)
v1 = pd.read_csv(MATCH / "win_predictions_v1.csv")
v1_ev = {i + 1: norm_event(r) for i, r in enumerate(v1["win_reason"])}
v1_wn = {i + 1: norm_winner(r) for i, r in enumerate(v1["win_point_player"])}

# new (CNN+RF+strategies)
nw = pd.read_csv(MATCH / "win_predictions.csv")
nw_ev = {i + 1: norm_event(r) for i, r in enumerate(nw["win_reason"])}
nw_wn = {i + 1: norm_winner(r) for i, r in enumerate(nw["winner"])}

# raw CNN ensemble class from the new run
cn_ev = {i + 1: norm_event(r) for i, r in enumerate(nw["cnn_class"])}

r1 = score("v1  OLD rule engine", v1_ev, v1_wn)
r2 = score("NEW CNN+RF+strategies", nw_ev, nw_wn)
r3 = score("NEW raw CNN ensemble (event only)", cn_ev, {})

print("\nPer-rally event calls (rally: v1 | new | cnn  vs GT):")
for r in range(1, 37):
    gt_ev, _ = GT[r]
    if not gt_ev:
        continue
    print(f"  R{r:2}  GT={gt_ev:3}  v1={v1_ev.get(r,'-'):3}  "
          f"new={nw_ev.get(r,'-'):3}  cnn={cn_ev.get(r,'-'):3}")
