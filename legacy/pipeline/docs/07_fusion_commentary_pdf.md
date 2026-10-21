# Stage 6 (part 2) — Fusion, Commentary, and PDF Report

Files: `fusion_layer.py`, `run_unified_pipeline.py`.

Runs immediately after win prediction (Stage 6, part 1) finishes writing
`win_predictions.csv`. `run_unified_pipeline.py` is the actual entry point
`run_full_pipeline.py` calls for this whole step; `fusion_layer.py` is one
piece it uses internally.

## `fusion_layer.py` — merging with the shot classifier

**Input:** `win_predictions.csv` (canonical winner/reason/score — Stage 7
per the code's own naming, "Stage 7 is THE winner stage" is an explicit
design directive preserved in a comment) + optionally a separate
`*_extended*.csv` shot classifier output (`find_extended_csv` picks the
newest one present by file mtime).

**Schema normalization** (`_normalize_schema`): `predict.py`'s CNN-era
output uses different column names (`winner`, `win_reason` as the raw
class string) than an older "stage7" convention
(`win_point_player`, `win_reason` as a full sentence like "opponent goes
out of bounds"). Since `win_point_player` not being present is exactly the
signal for "this needs normalizing," the function checks for that column
first and passes through unchanged if it's already in the older format —
supporting both without needing to know in advance which one it's looking
at. Also derives `detection_confidence` (`HIGH >= 0.8, MEDIUM >= 0.6,
else LOW` from `cnn_conf`) and picks the two `score_*` columns
positionally for `roundscore_A`/`roundscore_B`.

**Merging:** if no shot-classifier CSV exists, "degraded mode" — the
merged view is just Stage 7's own data, `shot_source="stage7"`. If one
does exist, its `ball_types` (a real shot-type classification — smash, net
shot, clear, etc.) replaces Stage 7's own trajectory-based guess, and a
`prediction_agrees` column records whether the two systems' independent
winner calls match — useful as a cross-check, not something later code
branches on.

**Two output files:** `merged_analysis.csv` (everything, plus the
agreement columns) and `badminton_analysis_enhanced.csv` — an externally
fixed 8-column schema (`start_time, end_time, win_point_player,
win_reason, ball_types, lose_reason, roundscore_A, roundscore_B`) that a
separate downstream viewer (the "BadmintonAnalysis" Streamlit app,
referenced but outside this pipeline's scope) consumes directly.

## `run_unified_pipeline.py` — the actual orchestration

Four phases, in order:

**[1/4] Win Predictor.** `ensure_win_predictions()` — runs Stage 6 part 1
if `win_predictions.csv` doesn't already exist (same skip-if-done pattern
as everything else).

**[2/4] Data fusion.** Calls `fusion_layer.DataFusionLayer` as above,
saves both output CSVs.

**[3/4] AI match commentary.** Two-layer design: a **deterministic**
factual summary computed entirely in code (`stats_summary`), which an LLM
is then asked to *restyle* — never to invent or recompute any fact.

`stats_summary(df, player_a, player_b)` computes, purely from the merged
data: total rallies, per-player win counts and each player's single most
common win reason (with count), the single longest rally (via
`_rally_seconds` on each row, `idxmax`), that rally's own winner/reason/
final shot type, the single most common rally-ending shot type overall,
and the final recorded score. All of it assembled into one paragraph —
this exact text is also the **fallback** output if the LLM step fails or
is unavailable.

`llm_commentary(df, player_a, player_b)` sends that factual paragraph, plus
optional player background text (`load_player_context` — matches player
names against `.txt` bio files by token overlap, truncated to a sentence
boundary) to a local LM Studio instance (Phi-3, via a plain HTTP request —
`import requests` is local to this function since it's an optional
dependency), with an explicit instruction set: keep every number, name,
rally number, and score *exactly* as written, rewrite style only. Falls
back to the raw `stats_summary` text (`source='STATS'`) if the LLM call
fails for any reason — the report is never blocked on an external service
being reachable.

**Zero-rally guard.** `stats_summary`/`build_match_semantics`/
`llm_commentary` all assume at least one rally exists — `idxmax()` on an
empty Series, `.iloc[-1]` on an empty frame, `value_counts().idxmax()` on
an empty result all raise. A genuinely rally-free clip (wrong video, a
slice that's all pre-match footage, the camera never actually on the
court) is a real possibility with user-uploaded input, not just a
theoretical edge case — found and fixed via the web app's live testing
(see [09_web_review_app.md](09_web_review_app.md)). `run_unified_pipeline`
checks `len(merged) == 0` before calling into the summary functions at all
and substitutes a plain "No rallies were detected..." message
(`source='STATS'`) instead of letting the pipeline crash on the last step.

**[4/4] PDF report.** `pick_highlights(df, n=5)` — top-5 rallies by
duration (parsed from `start_time`/`end_time` strings), sorted back into
chronological order for the summary. `generate_pdf()` hands off to an
external `BadmintonAnalysis` project's `pdf_generator.generate_pdf_report`
(outside this pipeline's own code, loaded via a `sys.path` insert) with
the player names, the 5 highlights, and the final commentary text.

**Written outputs** (`<match>/unified/`): `merged_analysis.csv`,
`badminton_analysis_enhanced.csv`, `analysis_report.txt` (player names +
source + generation timestamp header, then the commentary text),
`<players>_badminton_highlights_<timestamp>.pdf`.

## Parameters / config reference

| Item | Value | Meaning |
|---|---|---|
| Highlight count | 5 | Top-N rallies by duration selected for the PDF |
| LLM rewrite rule | facts frozen | Every number/name/score must appear unchanged in the LLM's output |
| Commentary fallback | `stats_summary` text | Used whenever the LLM call fails or is unreachable |
| `source` field | `'LLM'` or `'STATS'` | Recorded in the report so it's clear which path produced the text |
