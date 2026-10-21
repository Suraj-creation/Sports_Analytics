"""
Train simple linear probes on top of mean-pooled V-JEPA 2.1 embeddings to
predict the rally winner and the win reason, evaluated with
leave-one-video-out cross-validation (train on 3 videos, test on the 4th).

This is a pilot/sanity check: with only 132 labeled rallies across 4 videos,
it tells us whether V-JEPA embeddings carry useful signal at all - not a
final accuracy number.

Notes / assumptions:
  - win_point_player values differ per video ("Player A"/"Player B" vs
    "Gemke"/"Ginting"). Since the model can't know real player identities,
    each video's two players are mapped to 0/1 by sorted name order
    (assumes the labeling convention is consistent, e.g. "Player A" /
    alphabetically-first name = the same court side across videos).
  - win_reason strings are normalized into 3 canonical classes: "winner",
    "out_of_bounds", "net".

Usage:
    python train_probe.py                    # global mean-pool (baseline)
    python train_probe.py --pooling spatial  # keep coarse spatial grid of last frames
"""

import argparse
import csv
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline

DATASET_CSV = "dataset/dataset.csv"

# V-JEPA token grid: 32 time-steps x 24x24 spatial patches x 768 channels
TIME_STEPS = 32
GRID = 24

REASON_MAP = {
    "shot landed as winner": "winner",
    "winner": "winner",
    "in hit": "winner",
    "opponent hit out of bounds": "out_of_bounds",
    "opponent hit out": "out_of_bounds",
    "opponent hit the net": "net",
    "opponent hit net": "net",
    "opponent failed to clear net": "net",
    "opponent failed to cross net": "net",
}


def normalize_reason(s):
    key = s.strip().lower()
    return REASON_MAP.get(key, key)


def pool_spatial(emb, last_n=8, out_grid=3):
    """Pool a (1, 18432, 768) embedding into a small spatial-grid feature.

    1. Reshape to (time=32, h=24, w=24, dim=768).
    2. Keep only the last `last_n` time-steps (end of the rally) and
       average over time -> (24, 24, 768).
    3. Downsample the 24x24 grid to out_grid x out_grid by average-pooling
       cells -> (out_grid, out_grid, 768), then flatten.
    """
    emb = emb.reshape(TIME_STEPS, GRID, GRID, -1)
    emb = emb[-last_n:].mean(axis=0)  # (24, 24, dim)

    h, w, dim = emb.shape
    cell_h, cell_w = h // out_grid, w // out_grid
    pooled = np.zeros((out_grid, out_grid, dim), dtype=emb.dtype)
    for i in range(out_grid):
        for j in range(out_grid):
            block = emb[i * cell_h:(i + 1) * cell_h, j * cell_w:(j + 1) * cell_w]
            pooled[i, j] = block.mean(axis=(0, 1))
    return pooled.reshape(-1)  # (out_grid*out_grid*dim,)


def load_dataset(pooling="mean", dataset_csv=DATASET_CSV):
    with open(dataset_csv, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    # per-video mapping of player name -> 0/1, by sorted order
    players_per_video = {}
    for row in rows:
        video = row["video"]
        player = row["win_point_player"].strip()
        players_per_video.setdefault(video, set()).add(player)

    player_to_label = {}
    for video, players in players_per_video.items():
        for i, p in enumerate(sorted(players)):
            player_to_label[(video, p)] = i

    X, y_winner, y_reason, groups, meta = [], [], [], [], []
    for row in rows:
        emb = np.load(row["embedding_path"])  # (1, 18432, 768)
        if pooling == "spatial":
            feat = pool_spatial(emb)
        else:
            feat = emb.mean(axis=1).reshape(-1)   # (768,)
        X.append(feat)

        video = row["video"]
        player = row["win_point_player"].strip()
        y_winner.append(player_to_label[(video, player)])
        y_reason.append(normalize_reason(row["win_reason"]))
        groups.append(video)
        meta.append({
            "video": video,
            "rally": row.get("rally", ""),
            "win_point_player": player,
            "win_reason": row["win_reason"].strip(),
            "ball_types": row.get("ball_types", "").strip(),
        })

    return np.array(X), np.array(y_winner), np.array(y_reason), np.array(groups), meta


def run_loso(X, y, groups, label_name, pca_components=None, meta=None, label_names=None,
             show_errors=False, balanced=False):
    print(f"\n=== {label_name} (leave-one-video-out) ===")
    logo = LeaveOneGroupOut()
    accs = []
    base_accs = []
    errors = []
    for train_idx, test_idx in logo.split(X, y, groups):
        test_video = groups[test_idx][0]

        steps = [StandardScaler()]
        # PCA needs n_components <= min(n_samples, n_features); cap it so
        # high-dim spatial features (e.g. 6912-d) get reduced for the
        # small training sets used here.
        if pca_components is not None:
            n_comp = min(pca_components, len(train_idx), X.shape[1])
            steps.append(PCA(n_components=n_comp, random_state=0))
        clf_kwargs = {"max_iter": 5000}
        if balanced:
            clf_kwargs["class_weight"] = "balanced"
        steps.append(LogisticRegression(**clf_kwargs))
        clf = make_pipeline(*steps)

        clf.fit(X[train_idx], y[train_idx])
        preds = clf.predict(X[test_idx])
        acc = accuracy_score(y[test_idx], preds)
        accs.append(acc)

        # Majority-class baseline: predict the most common TRAINING label
        # for every test sample in this fold, and score that.
        majority_label = np.bincount(y[train_idx]).argmax()
        base_preds = np.full_like(y[test_idx], majority_label)
        base_acc = accuracy_score(y[test_idx], base_preds)
        base_accs.append(base_acc)

        print(f"  test={test_video:20s} n={len(test_idx):3d}  acc={acc:.3f}  "
              f"majority_baseline={base_acc:.3f}")

        if show_errors and meta is not None:
            for idx, true_label, pred_label in zip(test_idx, y[test_idx], preds):
                if true_label != pred_label:
                    m = meta[idx]
                    true_name = label_names[true_label] if label_names is not None else true_label
                    pred_name = label_names[pred_label] if label_names is not None else pred_label
                    errors.append((m, true_name, pred_name))
    print(f"  mean acc: {np.mean(accs):.3f}  (majority-baseline mean: {np.mean(base_accs):.3f})")

    if show_errors and errors:
        print(f"  --- {len(errors)} misclassified ---")
        for m, true_name, pred_name in errors:
            print(f"    {m['video']:20s} rally {m['rally']:>3}  "
                  f"true={true_name!s:12s} pred={pred_name!s:12s}  "
                  f"win_reason='{m['win_reason']}' ball_types='{m['ball_types']}'")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pooling", choices=["mean", "spatial"], default="mean",
        help="'mean' = global average over all tokens (baseline). "
             "'spatial' = average the last 8 time-steps but keep a 3x3 "
             "spatial grid, then PCA-reduce before the classifier.",
    )
    parser.add_argument(
        "--dataset", default=DATASET_CSV,
        help="path to the dataset csv (default: dataset/dataset.csv)",
    )
    parser.add_argument(
        "--errors", action="store_true",
        help="print misclassified rallies (video, rally, true/pred label, win_reason, ball_types)",
    )
    parser.add_argument(
        "--balanced", action="store_true",
        help="use class_weight='balanced' in LogisticRegression",
    )
    args = parser.parse_args()

    X, y_winner, y_reason, groups, meta = load_dataset(pooling=args.pooling, dataset_csv=args.dataset)
    print(f"Pooling: {args.pooling}")
    print(f"Loaded {len(X)} samples, feature dim {X.shape[1]}")
    print(f"Videos: {sorted(set(groups))}")

    le = LabelEncoder()
    y_reason_enc = le.fit_transform(y_reason)
    print(f"Reason classes: {dict(zip(le.classes_, range(len(le.classes_))))}")

    # PCA only needed for the high-dim spatial features
    pca_components = 30 if args.pooling == "spatial" else None

    run_loso(X, y_winner, groups, "win_point_player (0/1 by sorted name)", pca_components,
             meta=meta, label_names={0: "player_0", 1: "player_1"}, show_errors=args.errors,
             balanced=args.balanced)
    run_loso(X, y_reason_enc, groups, "win_reason", pca_components,
             meta=meta, label_names=le.classes_, show_errors=args.errors,
             balanced=args.balanced)


if __name__ == "__main__":
    main()
