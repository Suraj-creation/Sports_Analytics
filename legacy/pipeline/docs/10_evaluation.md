# Stage 6 (part 2) — Evaluation Against Ground Truth

Files: `win_predictor/evaluate_predictions.py` (evaluation script),
`vk15b2/vk15b_dataset/<match>/<match>.csv` (ground truth).

This documents how `win_predictions.csv` output is scored against real
ground truth, and the current measured accuracy across all 8 labeled
matches in `vk15b_dataset/`.

---

## Ground truth source

`vk15b2/vk15b_dataset/` contains 8 matches (`Test1_Full, Test2_Full,
Test3_Full, Test4_Full, Test6_Full, Test7_Full, Test9_Full, Test10_Full`),
each with a hand-labeled `<match>.csv`:

```
start_time,end_time,win_point_player,win_reason,ball_types,lose_reason,roundscore_A,roundscore_B
0:08,0:24,Player B,Opponent Out of Bounds,Lift Shot,Hit Out of Bounds,0,1
```

`win_reason` uses free-text labels, mapped to the pipeline's 3-class
scheme with the same mapping `win_predictor/evaluate_rule.py` uses:

| GT label | Pipeline class |
|---|---|
| `Opponent Out of Bounds` | `out_of_bounds` |
| `Opponent Hit the Net` | `hits_net` |
| `Winner Shot` | `wins_by_landing` |
| `Opponent Failed to Return` | `wins_by_landing` |

Each match folder also has the supporting files `predict.py` needs
(`<match>_ball_filled.csv`, `<match>_court.json`, `<match>_rally.csv`,
`player_detections.csv`), so `win_predictions.csv` can be regenerated
fresh with the current code at any time — see
[06_win_prediction.md](06_win_prediction.md) for the run command.

## Matching predicted rallies to GT rallies

Predicted and GT rally counts don't line up exactly — rally detection
sometimes finds a different number of boundaries than the human-labeled
GT (e.g. Test9: 88 GT rallies vs 82 detected). Row-index comparison would
silently misalign every rally after the first mismatch, so rallies are
matched by **time overlap** instead:

```
IoU = overlap(pred_time, gt_time) / union(pred_time, gt_time)
```

Each predicted rally is greedily paired with the best-overlapping
*unused* GT rally, only if `IoU ≥ 0.3` (same threshold used by the
rally-detection evaluator, `analysis/Evaluate_rallies.py`). A predicted
or GT rally with no match above that threshold is dropped from the
accuracy calculation entirely — it's a rally-*detection* miss, not a
winner/reason classification error, so it shouldn't be scored as one.

For each matched pair, two fields are compared directly:
- `winner_correct = pred['winner'] == gt['win_point_player']`
- `reason_correct = pred['win_reason'] == mapped_gt_reason`

## Coverage (8 matches, current run)

| Match | GT rallies | Predicted | Matched (IoU≥0.3) | Unmatched GT | Unmatched pred |
|---|---|---|---|---|---|
| Test1_Full | 36 | 36 | 36 | 0 | 0 |
| Test2_Full | 75 | 73 | 72 | 3 | 1 |
| Test3_Full | 22 | 19 | 19 | 3 | 0 |
| Test4_Full | 45 | 41 | 39 | 6 | 2 |
| Test6_Full | 42 | 42 | 39 | 3 | 3 |
| Test7_Full | 31 | 30 | 30 | 1 | 0 |
| Test9_Full | 88 | 82 | 74 | 14 | 8 |
| Test10_Full | 101 | 93 | 90 | 11 | 3 |

399 total matched rallies used for the accuracy numbers below.

---

## Results (current pipeline code, all 8 matches on clean video)

| Metric | Accuracy |
|---|---|
| Win-reason accuracy | **85.7%** (342/399) |
| Winner accuracy | **68.9%** (275/399) |

### Win-reason confusion matrix (rows = GT, cols = predicted)

| GT \ Pred | OOB | HN | WBL | Class acc |
|---|---|---|---|---|
| **OOB** | 141 | 3 | 2 | 96.6% |
| **HN** | 7 | 102 | 11 | 85.0% |
| **WBL** | 12 | 7 | 99 | 83.9% |

### Accuracy by decision path (`reason_src`)

| Path | What it means | Rallies | Winner acc | Reason acc |
|---|---|---|---|---|
| `ML_RF` | Trajectory RF called it directly | 283 | 70.7% | 84.8% |
| `ML_HN` | CNN net-hit gate fired (standard threshold) | 23 | 69.6% | 78.3% |
| `ML_HN_I` | CNN net-hit gate fired via the lowered net-zone threshold (Strategy I) | 90 | 63.3% | 93.3% |
| `ML_STRAT_F` | RF said WBL but rule engine + fast lateral velocity overrode to OOB | 3 | 66.7% | 0.0% |

### Per-match

| Match | N | Winner acc | Reason acc |
|---|---|---|---|
| Test1_Full | 36 | 77.8% | 100.0% |
| Test2_Full | 72 | 65.3% | 93.1% |
| Test3_Full | 19 | 89.5% | 78.9% |
| Test4_Full | 39 | 61.5% | 84.6% |
| Test6_Full | 39 | 82.1% | 92.3% |
| Test7_Full | 30 | 66.7% | 76.7% |
| Test9_Full | 74 | 58.1% | 77.0% |
| Test10_Full | 90 | 71.1% | 83.3% |

### Failure attribution (winner errors only)

Of the 124 rallies where the predicted winner was wrong:
- 31% (39) had the wrong `win_reason`, which propagated to the wrong winner
- 69% (85) had the *correct* `win_reason` but the fault-side/winner call
  was still wrong — a separate, not-yet-fixed problem (see below)

---

## Strategy E removal (fixed — see `predict.py`)

The pipeline previously had a "Strategy E" override: when the CNN's
net-hit gate fired (`cnn_hn >= eff_hn_thr`), it could still be overridden
back to `wins_by_landing` if the trajectory RF said `wins_by_landing` and
the shuttle's last position had positive court margin.

This was measured live and found to be actively harmful: it fired on
~90/380 rallies and was correct only ~8% of the time, collapsing HN-class
accuracy to 20%. Root cause: the trajectory RF is trained as a binary
`out_of_bounds` vs `wins_by_landing` classifier only (HN excluded from
training — see [06_win_prediction.md](06_win_prediction.md)), so for a
genuine net-hit rally it is structurally incapable of saying "hits_net"
and is forced to guess between the two classes it knows. Net-hit shuttles
typically land just inside the court near the net, so `margin_cm > 0` was
true for most real HN rallies too — the override fired on real net-hits
almost as often as on genuine misclassifications.

The 81.8%/~69% figures previously cited for this strategy (e.g. in
`win_predictor/README.md`, `INSTALL_AND_RUN.md`) came from
`vk15b2/netcnn/traj_classifier.py`'s offline LOMO-CV benchmark, which
builds its dataset by filtering to `GT ∈ {out_of_bounds, wins_by_landing}`
**before** training or predicting — so the trajectory prediction is
`None` for every real HN rally in that benchmark, by construction, using
information (the true label) that isn't available at real inference time.
That's why the benchmark showed ~88% HN accuracy for this path while live
inference showed ~20%: the two are not measuring the same thing.

**Fix:** once the CNN's HN gate fires, trust it — the RF no longer gets a
vote. This raised win-reason accuracy on the 6 matches tested before/after
from 62.9% to 82.1%, and across the full 8-match set from 68.7% to 85.7%,
with winner accuracy essentially unchanged (67.2% → 68.9%, since the
override rarely flipped the *winner*, only the *reason*).

## Known remaining issue: fault-side errors

69% of current winner errors have the correct `win_reason` but the wrong
fault-side (i.e. wrong winner despite correctly classifying how the rally
ended). This is unrelated to Strategy E and not yet investigated — the
next place to look is the fault-side logic in `predict.py` (`WBL` uses
shuttle-Y vs net floor line; `HN`/`OOB` use the rule engine's geometric
partition — see [06_win_prediction.md](06_win_prediction.md)).
