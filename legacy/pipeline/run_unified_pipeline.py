"""
run_unified_pipeline.py
=======================
Unified orchestrator: Stage 7 Win Predictor + shot classifier fusion +
AI match commentary (LM Studio / Phi-3) + PDF report via BadmintonAnalysis.

Phases
------
1. Win Predictor   — reuse <match>/win_predictions.csv, or run
                     analysis/stage7_predict.py to create it
2. Data Fusion     — fusion_layer.py merges Stage 7 + extended shot CSV
3. AI Commentary   — LM Studio (port 1234) generates a match summary;
                     graceful fallback to a stats-based summary if offline
4. PDF Report      — BadmintonAnalysis pdf_generator (reportlab)

Neither existing system is modified.

Usage:
    python run_unified_pipeline.py --match_folder Test1_Full_rev \
        --player_a "AN Se Young" --player_b "Intanon"
"""

import argparse
import datetime
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
BADMINTON_SRC = PROJECT_ROOT / "BadmintonAnalysis" / "src"

# LM Studio (OpenAI-compatible local server)
LM_STUDIO_URL = os.environ.get("LM_STUDIO_BASE_URL", "http://127.0.0.1:1234/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "phi-3.1-mini-128k-instruct")
LLM_TIMEOUT = 240  # Phi-3 on a laptop GPU can be slow

sys.path.insert(0, str(PROJECT_ROOT))
from fusion_layer import DataFusionLayer, find_extended_csv


# ────────────────────────────────────────────────────────────────────────────
# Phase 1 — Win Predictor (Stage 7)
# ────────────────────────────────────────────────────────────────────────────
def ensure_win_predictions(match_folder, player_a, player_b):
    """
    Return path to win_predictions.csv. If missing, regenerate by running
    win_predictor/predict.py -- with --video for the full CNN+rule ensemble
    when the match video is available, or without it (rule engine + traj RF
    only, CNN probs default to uniform) when it isn't.
    """
    match_folder = Path(match_folder)
    wp = match_folder / "win_predictions.csv"
    if wp.exists():
        print(f"  Reusing existing {wp}")
        return str(wp)

    video = match_folder / f"{match_folder.name}.mp4"
    cmd = [sys.executable, "predict.py",
           "--match_folder", str(match_folder.resolve()),
           "--player_a", player_a, "--player_b", player_b,
           "--no_frames"]
    if video.exists():
        print("  win_predictions.csv not found — running CNN + rule win predictor...")
        cmd += ["--video", str(video.resolve())]
    else:
        print("  win_predictions.csv not found (no video) — running rule engine + traj RF only...")
    res = subprocess.run(cmd, cwd=str(PROJECT_ROOT / "win_predictor"))
    if res.returncode != 0 or not wp.exists():
        raise RuntimeError("Win predictor failed — cannot continue")
    return str(wp)


# ────────────────────────────────────────────────────────────────────────────
# Phase 3 — AI commentary (LM Studio, graceful fallback)
# ────────────────────────────────────────────────────────────────────────────
def _rally_seconds(row):
    def sec(t):
        p = str(t).split(":")
        return int(p[0]) * 60 + int(p[1]) if len(p) == 2 else 0
    return sec(row["end_time"]) - sec(row["start_time"])


def load_player_context(*player_names, max_chars=350):
    """
    Pull short factual bio excerpts from BadmintonAnalysis's knowledge base
    (input/badminton/*.txt) for each player — lightweight RAG grounding.
    """
    bio_dir = PROJECT_ROOT / "BadmintonAnalysis" / "input" / "badminton"
    out = []
    if not bio_dir.exists():
        return ""
    for name in player_names:
        tokens = {t.lower() for t in name.replace(".", " ").split() if len(t) > 2}
        for f in bio_dir.glob("*.txt"):
            fname_tokens = {t.lower() for t in f.stem.replace("_", " ").split()}
            if tokens & fname_tokens:
                text = f.read_text(encoding="utf-8", errors="ignore")[:max_chars]
                # cut at last sentence end for cleanliness
                cut = text.rfind(".")
                out.append(f"- {name}: {text[:cut + 1] if cut > 50 else text}")
                break
    return "\n".join(out)


def build_match_semantics(df, player_a, player_b):
    """Compact rally-by-rally text plus verified aggregates."""
    lines = []
    for i, r in df.iterrows():
        shot = str(r.get("ball_types", "unknown"))
        lines.append(
            f"Rally {i+1} ({r['start_time']}-{r['end_time']}): "
            f"{r['win_point_player']} won ({r['win_reason']}); "
            f"final shot: {shot}; score {r['roundscore_A']}-{r['roundscore_B']}"
        )

    wins = df["win_point_player"].value_counts().to_dict()
    durs = df.apply(_rally_seconds, axis=1)
    longest_idx = int(durs.idxmax())
    lr = df.loc[longest_idx]

    # per-player win-reason breakdown (verified aggregates)
    reason_by_player = (
        df.groupby("win_point_player")["win_reason"]
        .value_counts().to_dict()
    )
    reason_lines = "; ".join(
        f"{p} won {n} rallies via '{r}'" for (p, r), n in reason_by_player.items()
    )

    header = (
        f"Match: {player_a} vs {player_b}. {len(df)} rallies total.\n"
        f"Rally wins: {wins}. "
        f"Final recorded score: {df.iloc[-1]['roundscore_A']}-{df.iloc[-1]['roundscore_B']}.\n"
        f"Win-reason breakdown: {reason_lines}.\n"
        f"Longest rally: Rally {longest_idx + 1} "
        f"({lr['start_time']}-{lr['end_time']}, {int(durs.max())} seconds), "
        f"won by {lr['win_point_player']} ({lr['win_reason']})."
    )
    return header + "\n\nRALLY LOG:\n" + "\n".join(lines)


def stats_summary(df, player_a, player_b):
    """
    Deterministic factual summary — every number computed in code.
    Used directly as the fallback, and as the verified core the LLM
    is asked to restyle (rewrite, never compose) in llm_commentary.
    """
    wins = df["win_point_player"].value_counts()
    shots = df["ball_types"].value_counts()
    durs = df.apply(_rally_seconds, axis=1)
    li = int(durs.idxmax())
    lr = df.loc[li]

    # natural-language clauses for each win_reason string
    REASON_CLAUSE = {
        "opponent goes out of bounds": "her opponent sent the shuttle out of bounds",
        "opponent hits the net":       "her opponent hit the shuttle into the net",
        "shot landed as winner":       "her shot landed in as a winner",
    }

    def clause(reason):
        return REASON_CLAUSE.get(str(reason), str(reason))

    def top_reason_for(player):
        sub = df[df["win_point_player"] == player]["win_reason"].value_counts()
        return (sub.idxmax(), int(sub.max())) if len(sub) else ("unknown", 0)

    ra, na = top_reason_for(player_a)
    rb, nb = top_reason_for(player_b)
    wa = int(wins.get(player_a, 0))
    wb = int(wins.get(player_b, 0))
    leader, margin = (player_a, wa - wb) if wa >= wb else (player_b, wb - wa)

    return (
        f"{player_a} faced {player_b} across {len(df)} rallies, and {leader} "
        f"came out on top {max(wa, wb)}-{min(wa, wb)}, a margin of {margin} rallies. "
        f"{player_a} won {wa} rallies, most often when {clause(ra)} "
        f"({na} rallies). "
        f"{player_b} won {wb} rallies, most often when {clause(rb)} "
        f"({nb} rallies). "
        f"The longest rally was Rally {li + 1}, lasting {int(durs.max())} seconds "
        f"({lr['start_time']} to {lr['end_time']}); {lr['win_point_player']} "
        f"took the point when {clause(lr['win_reason'])}, and the rally ended "
        f"on a {lr.get('ball_types', 'shot')}. "
        f"The most frequent rally-ending shot overall was the {shots.idxmax()} "
        f"({int(shots.max())} of {len(df)} rallies). "
        f"The final recorded score was "
        f"{df.iloc[-1]['roundscore_A']}-{df.iloc[-1]['roundscore_B']}."
    )


def llm_commentary(df, player_a, player_b):
    """
    Ask LM Studio (Phi-3) for a narrative match summary.
    Returns (text, source) where source is 'LLM' or 'STATS'.
    """
    import requests

    factual_core = stats_summary(df, player_a, player_b)
    player_context = load_player_context(player_a, player_b)

    prompt = f"""You are a professional badminton broadcast writer. Your ONLY task is to rewrite the factual report below in an engaging broadcast style.

PLAYER BACKGROUND (for tone only — you may reference playing style, nothing else):
{player_context if player_context else '(no background available)'}
Both players are women — always use "she/her".

FACTUAL REPORT (every fact you are allowed to state):
{factual_core}

REWRITE RULES:
1. Keep EVERY number, name, rally number, and score EXACTLY as written — do not change, recompute, or add any.
2. Write all numbers as digits (e.g. "20", not "twenty"). Never spell numbers out.
3. Do NOT add new events, rallies, momentum swings, crowd reactions, venues, or match durations.
4. You may reorder sentences and improve flow, vocabulary, and energy.
5. Output 150-200 words as one cohesive narrative, no bullet points, no headers.

Rewrite it now."""

    import re

    def numbers_verified(text):
        """
        Every integer in the LLM text must appear in the factual core
        (timestamps compared as their parts). Spelled-out numbers are
        forbidden by the prompt; this catches digit hallucinations.
        """
        allowed = set(re.findall(r"\d+", factual_core))
        found = re.findall(r"\d+", text)
        bad = [n for n in found if n not in allowed]
        if bad:
            print(f"  Verification failed — invented numbers: {bad}")
        return not bad

    for attempt, temp in ((1, 0.2), (2, 0.0)):
        try:
            r = requests.post(
                f"{LM_STUDIO_URL}/chat/completions",
                json={
                    "model": LLM_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temp,
                    "max_tokens": 512,
                },
                timeout=LLM_TIMEOUT,
            )
            r.raise_for_status()
            text = r.json()["choices"][0]["message"]["content"].strip()
            if len(text) < 40:
                raise ValueError("LLM returned an unusably short response")
            if numbers_verified(text):
                return text, "LLM"
            print(f"  Attempt {attempt}: LLM styled text failed number check"
                  f"{' — retrying at temperature 0' if attempt == 1 else ''}")
        except Exception as e:
            print(f"  LM Studio unavailable/failed ({e})")
            break

    print("  Using verified deterministic summary (every number computed in code)")
    return factual_core, "STATS-VERIFIED"


def pick_highlights(df, n=5):
    """Top-n rallies by duration (longest exchanges = natural highlights)."""
    def dur(row):
        def sec(t):
            p = str(t).split(":")
            return int(p[0]) * 60 + int(p[1]) if len(p) == 2 else 0
        return sec(row["end_time"]) - sec(row["start_time"])

    d = df.copy()
    d["_dur"] = d.apply(dur, axis=1)
    top = d.nlargest(n, "_dur").sort_index()
    out = []
    for _, r in top.iterrows():
        out.append({
            "start_time": r["start_time"],
            "end_time": r["end_time"],
            "win_point_player": r["win_point_player"],
            "ball_types": str(r.get("ball_types", "")),
            "ai_reasoning": (f"{int(r['_dur'])}s exchange — "
                             f"{r['win_point_player']} won it "
                             f"({r['win_reason']}), finishing with a "
                             f"{r.get('ball_types', 'shot')}."),
        })
    return out


# ────────────────────────────────────────────────────────────────────────────
# Phase 4 — PDF via BadmintonAnalysis (untouched module)
# ────────────────────────────────────────────────────────────────────────────
def generate_pdf(player_names, highlights, summary_text, out_dir):
    sys.path.insert(0, str(BADMINTON_SRC))
    from utils.pdf_generator import generate_pdf_report

    return generate_pdf_report(
        sport_name="Badminton",
        player_names=player_names,
        selected_highlights=highlights,
        generation_text=summary_text,
        is_summary=True,
        return_bytes=False,
        output_dir=str(out_dir),
    )


# ────────────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────────────
def run_unified_pipeline(match_folder, player_a, player_b, out_dir=None,
                         use_shots=True):
    match_folder = Path(match_folder)
    out_dir = Path(out_dir) if out_dir else match_folder / "unified"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    print("=" * 70)
    print("  UNIFIED BADMINTON ANALYSIS PIPELINE")
    print("=" * 70)
    print(f"  Match  : {match_folder}")
    print(f"  Players: {player_a} (far) vs {player_b} (near)")
    print(f"  Output : {out_dir}")

    # Phase 1 — Stage 7
    print("\n[1/4] Win Predictor (Stage 7)")
    win_pred_csv = ensure_win_predictions(match_folder, player_a, player_b)
    results["win_pred_csv"] = win_pred_csv

    # Phase 2 — Fusion
    print("\n[2/4] Data fusion")
    fusion = DataFusionLayer()
    fusion.load_win_predictions(win_pred_csv)
    shots_csv = find_extended_csv(match_folder) if use_shots else None
    if not use_shots:
        print("  --no_shots: skipping shot classifier, using Stage 7 ball_types")
    if shots_csv:
        fusion.load_shot_analysis(shots_csv)
    merged = fusion.merge()
    results["merged_csv"] = fusion.save(out_dir / "merged_analysis.csv")
    results["badminton_csv"] = fusion.save_badminton_format(
        out_dir / "badminton_analysis_enhanced.csv")

    # Phase 3 — Commentary
    print("\n[3/4] AI match commentary")
    if len(merged) == 0:
        # stats_summary/llm_commentary/build_match_semantics all assume at
        # least one rally (idxmax(), .iloc[-1], value_counts().idxmax() --
        # all crash on an empty frame). A genuinely rally-free clip (wrong
        # video, a slice that's all pre-match footage, camera never on the
        # court) is a real possibility from user-uploaded input, not just a
        # theoretical case -- report it plainly instead of a traceback.
        summary_text = (
            f"No rallies were detected for {player_a} vs {player_b}. This "
            f"usually means the clip doesn't contain rally play the pipeline "
            f"recognized -- check the court annotation and the input video, "
            f"or trim to a range that includes actual points being played."
        )
        source = "STATS"
    else:
        summary_text, source = llm_commentary(merged, player_a, player_b)
    print(f"  Commentary source: {source}")

    report_txt = out_dir / "analysis_report.txt"
    with open(report_txt, "w", encoding="utf-8") as f:
        f.write(f"Players : {player_a} vs {player_b}\n")
        f.write(f"Sport   : Badminton\n")
        f.write(f"Source  : {source} commentary\n")
        f.write(f"Generated: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}\n")
        f.write("\n" + "=" * 50 + "\n\n")
        f.write(summary_text + "\n")
    results["report_txt"] = str(report_txt)
    print(f"  Saved -> {report_txt}")

    # Phase 4 — PDF
    print("\n[4/4] PDF report (BadmintonAnalysis generator)")
    highlights = pick_highlights(merged, n=5)
    pdf_path = generate_pdf(f"{player_a} vs {player_b}", highlights,
                            summary_text, out_dir)
    results["pdf"] = pdf_path
    print(f"  Saved -> {pdf_path}")

    print("\n" + "=" * 70)
    print("  PIPELINE COMPLETE")
    print("=" * 70)
    for k, v in results.items():
        print(f"  {k:14}: {v}")
    print(f"\n  Match summary ({source}):\n")
    print("  " + summary_text.replace("\n", "\n  "))
    return results


def main():
    ap = argparse.ArgumentParser(description="Unified badminton analysis pipeline")
    ap.add_argument("--match_folder", required=True)
    ap.add_argument("--player_a", default="Player A", help="FAR player")
    ap.add_argument("--player_b", default="Player B", help="NEAR player")
    ap.add_argument("--output", default=None)
    ap.add_argument("--no_shots", action="store_true",
                    help="Skip the shot classifier; use Stage 7's own ball_types")
    args = ap.parse_args()
    run_unified_pipeline(args.match_folder, args.player_a, args.player_b,
                         args.output, use_shots=not args.no_shots)


if __name__ == "__main__":
    main()
