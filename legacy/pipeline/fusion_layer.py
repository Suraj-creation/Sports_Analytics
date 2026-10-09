"""
fusion_layer.py
===============
Merges Win Predictor (Stage 7) output with the shot-classifier extended CSV,
producing a unified rally view plus a BadmintonAnalysis-compatible CSV.

Sources
-------
1. win_predictions.csv        (Stage 7 / analysis/stage7_predict.py)
   -> canonical winner, win_reason, fault_side, detection_confidence
2. <match>_extended_v*.csv    (analysis/extract_features.py)
   -> shot classification (ball_types), winning-shot timestamps

Outputs
-------
merged_analysis.csv                full merged view + agreement flags
badminton_analysis_enhanced.csv    exact schema the BadmintonAnalysis
                                   Streamlit app consumes:
                                   start_time,end_time,win_point_player,
                                   win_reason,ball_types,lose_reason,
                                   roundscore_A,roundscore_B

Both systems stay untouched — this file only reads their outputs.

Usage:
    python fusion_layer.py --match_folder Test1_Full_rev
"""

import argparse
import os
from pathlib import Path

import pandas as pd


class DataFusionLayer:
    """
    Merges win_predictions.csv (Stage 7) with the extended shot CSV.

    Stage 7 is the canonical source for winner / win_reason / scores
    (user directive: Stage 7 is THE winner stage).  The extended CSV
    contributes the shot-type classification and winning-shot timing.
    """

    def __init__(self):
        self.win_pred_df = None
        self.shots_df = None
        self.merged_df = None

    # ── loading ──────────────────────────────────────────────────────────
    # win_predictor/predict.py (CNN version) emits a different schema than
    # stage7_predict.py; normalize it to the stage7 one the pipeline uses.
    _REASON_WIN = {"out_of_bounds": "opponent goes out of bounds",
                   "hits_net": "opponent hits the net",
                   "wins_by_landing": "wins_by_landing"}
    _REASON_LOSE = {"out_of_bounds": "goes out of bounds",
                    "hits_net": "hits the net",
                    "wins_by_landing": "opponent wins by landing"}

    def _normalize_schema(self, df):
        if "win_point_player" in df.columns:
            return df  # already stage7 format
        out = pd.DataFrame()
        out["start_time"] = df["start_time"]
        out["end_time"] = df["end_time"]
        out["win_point_player"] = df["winner"]
        out["win_reason"] = df["win_reason"].map(self._REASON_WIN).fillna(df["win_reason"])
        out["ball_types"] = df.get("cnn_class", pd.Series(["unknown"] * len(df)))
        out["lose_reason"] = df["win_reason"].map(self._REASON_LOSE).fillna(df["win_reason"])
        out["fault_side"] = df.get("fault_side", "")
        score_cols = [c for c in df.columns if c.startswith("score_")]
        if len(score_cols) >= 2:
            out["roundscore_A"] = df[score_cols[0]]
            out["roundscore_B"] = df[score_cols[1]]
        else:
            out["roundscore_A"] = out["roundscore_B"] = 0
        conf = pd.to_numeric(df.get("cnn_conf", pd.Series([1.0] * len(df))),
                             errors="coerce").fillna(1.0)
        out["detection_confidence"] = [
            "HIGH" if c >= 0.8 else "MEDIUM" if c >= 0.6 else "LOW" for c in conf]
        out["reason_src"] = df.get("reason_src", "RULE")
        print("  (normalized CNN-predictor schema -> stage7 format)")
        return out

    def load_win_predictions(self, csv_path):
        self.win_pred_df = self._normalize_schema(pd.read_csv(csv_path))
        print(f"  Loaded win_predictions: {len(self.win_pred_df)} rallies "
              f"({os.path.basename(csv_path)})")
        return self.win_pred_df

    def load_shot_analysis(self, csv_path):
        self.shots_df = pd.read_csv(csv_path)
        print(f"  Loaded shot analysis  : {len(self.shots_df)} rallies "
              f"({os.path.basename(csv_path)})")
        return self.shots_df

    # ── merging ──────────────────────────────────────────────────────────
    def merge(self):
        if self.win_pred_df is None:
            raise ValueError("win_predictions must be loaded before merging")

        wp = self.win_pred_df.reset_index(drop=True)

        if self.shots_df is None:
            # Degraded mode: Stage 7 only (its own ball_types column is a
            # trajectory guess, still usable).
            merged = wp.copy()
            merged["shot_source"] = "stage7"
            merged["prediction_agrees"] = pd.NA
            self.merged_df = merged
            print(f"  Merged (Stage 7 only): {len(merged)} rallies")
            return merged

        sh = self.shots_df.reset_index(drop=True)
        n = min(len(wp), len(sh))
        if len(wp) != len(sh):
            print(f"  NOTE: rally count differs (win_pred={len(wp)}, "
                  f"shots={len(sh)}) — aligning first {n} by index")
        wp, sh = wp.iloc[:n].copy(), sh.iloc[:n].copy()

        merged = wp.copy()  # Stage 7 columns are canonical

        # Shot classifier's ball_types replaces Stage 7's trajectory guess
        merged["ball_types"] = sh["ball_types"].values
        merged["shot_source"] = "shot_classifier"

        # Carry over winning-shot timing if present
        for col in ("winning_shot_time", "winning_shot_frame"):
            if col in sh.columns:
                merged[col] = sh[col].values

        # Cross-system comparison columns
        merged["clf_winner"] = sh["win_point_player"].values
        merged["clf_win_reason"] = sh["win_reason"].values
        merged["prediction_agrees"] = (
            merged["win_point_player"].astype(str).str.strip()
            == merged["clf_winner"].astype(str).str.strip()
        )

        self.merged_df = merged
        agree = merged["prediction_agrees"].mean()
        print(f"  Merged: {len(merged)} rallies | winner agreement "
              f"between systems: {agree:.0%}")
        return merged

    # ── stats ────────────────────────────────────────────────────────────
    def get_summary_stats(self):
        if self.merged_df is None:
            raise ValueError("merge() must run first")
        m = self.merged_df
        stats = {
            "total_rallies": len(m),
            "win_reason_counts": m["win_reason"].value_counts().to_dict(),
            "shot_counts": m["ball_types"].value_counts().to_dict(),
            "player_wins": m["win_point_player"].value_counts().to_dict(),
        }
        if "prediction_agrees" in m.columns and m["prediction_agrees"].notna().any():
            stats["winner_agreement"] = float(m["prediction_agrees"].mean())
        if "detection_confidence" in m.columns:
            stats["high_confidence"] = int((m["detection_confidence"] == "HIGH").sum())
        return stats

    # ── saving ───────────────────────────────────────────────────────────
    def save(self, output_path):
        if self.merged_df is None:
            raise ValueError("merge() must run first")
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.merged_df.to_csv(output_path, index=False)
        print(f"  Saved merged view -> {output_path}")
        return str(output_path)

    def save_badminton_format(self, output_path):
        """
        Write the exact 8-column schema the BadmintonAnalysis app loads:
        start_time,end_time,win_point_player,win_reason,ball_types,
        lose_reason,roundscore_A,roundscore_B
        """
        if self.merged_df is None:
            raise ValueError("merge() must run first")
        cols = ["start_time", "end_time", "win_point_player", "win_reason",
                "ball_types", "lose_reason", "roundscore_A", "roundscore_B"]
        missing = [c for c in cols if c not in self.merged_df.columns]
        if missing:
            raise ValueError(f"Merged data missing columns: {missing}")
        out = self.merged_df[cols].copy()
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        out.to_csv(output_path, index=False)
        print(f"  Saved BadmintonAnalysis-format CSV -> {output_path}")
        return str(output_path)


# ── helpers for callers ────────────────────────────────────────────────────

def find_extended_csv(match_folder):
    """Pick the newest *_extended*.csv in the match folder (v3 > v2 > base)."""
    folder = Path(match_folder)
    candidates = sorted(folder.glob("*_extended*.csv"),
                        key=lambda p: p.stat().st_mtime, reverse=True)
    return str(candidates[0]) if candidates else None


def main():
    ap = argparse.ArgumentParser(description="Fuse Stage 7 + shot classifier outputs")
    ap.add_argument("--match_folder", required=True)
    ap.add_argument("--win_pred", default=None,
                    help="win_predictions.csv (default: <match_folder>/win_predictions.csv)")
    ap.add_argument("--shots", default=None,
                    help="extended CSV with shot types (default: newest *_extended*.csv)")
    ap.add_argument("--out_dir", default=None,
                    help="output dir (default: <match_folder>/unified)")
    args = ap.parse_args()

    folder = Path(args.match_folder)
    win_pred = args.win_pred or str(folder / "win_predictions.csv")
    shots = args.shots or find_extended_csv(folder)
    out_dir = Path(args.out_dir) if args.out_dir else folder / "unified"

    print("=" * 60)
    print("  DATA FUSION LAYER")
    print("=" * 60)

    fusion = DataFusionLayer()
    fusion.load_win_predictions(win_pred)
    if shots and os.path.exists(shots):
        fusion.load_shot_analysis(shots)
    else:
        print("  No extended shot CSV found — Stage 7 only mode")
    fusion.merge()

    stats = fusion.get_summary_stats()
    print(f"\n  Rallies        : {stats['total_rallies']}")
    print(f"  Player wins    : {stats['player_wins']}")
    print(f"  Win reasons    : {stats['win_reason_counts']}")
    if "winner_agreement" in stats:
        print(f"  Winner agreement (Stage7 vs classifier): {stats['winner_agreement']:.0%}")

    fusion.save(out_dir / "merged_analysis.csv")
    fusion.save_badminton_format(out_dir / "badminton_analysis_enhanced.csv")


if __name__ == "__main__":
    main()
