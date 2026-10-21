# Failure Cases, Edge Cases & Defect Root-Cause Analysis

**Platform:** Real-Time Badminton Analytics Platform (`badminton-ai`)  
**Evaluation Date:** October 2026  
**Hardware:** NVIDIA GeForce RTX 4080 SUPER / Ubuntu Linux  

---

## Defect Summary Table

| Defect ID | Severity | Subsystem | Title / Failure Symptom | Status |
|---|---|---|---|---|
| **DEF-01** | **P0 (Critical)** | Context / State | Absence of Match-Phase Model leads to Warm-Up & Replay Contamination | **Fixed — CPU/synthetic verified; real-video re-run pending** |
| **DEF-02** | **P0 (Critical)** | Ingest / Storage | YouTube Ingest Crashes on `ValueError: invalid media hash` prior to Download | **Resolved** |
| **DEF-03** | **P1 (Core)** | Perception / Scoring | Scoreboard OCR (`rapidocr_v4`) is Unwired in Pipeline, causing Geometric Winner Errors | **Fixed — wired; real RapidOCR verified on rendered board; broadcast accuracy not yet measured** |
| **DEF-04** | **P1 (Core)** | Agentic AI | Grounding Validator Regex Over-Rejection on Uncited Numbers in Abstentions | **Fixed** |
| **DEF-05** | **P1 (Core)** | Agentic AI | Local Small LLM (8B) Hallucinates Dummy Event References (`[[ev:P1_stats]]`) | **Mitigated (repair + prompt); re-run with the 8B model pending** |
| **DEF-06** | **P2 (Analytics)** | Perception / Scene | Court Presence Gate Fails on Non-Green Badminton Mats (Hardcoded HSV) | **Fixed — synthetic mats verified** |
| **DEF-07** | **P2 (Analytics)** | Perception / Racket | Racket Pose Model (`racketvision_racketpose`) is Unwired in Ingestion Pipeline | **Open (Unwired Specialist)** |
| **DEF-08** | **P2 (Analytics)** | Event Segmentation | False Rally Over-Segmentation from Broadcast Cut Recovery (41 vs 36 rallies) | **Partially fixed (post-cut rallies without a serve are not scored); segmentation itself unchanged** |
| **DEF-09** | **P3 (Minor)** | Configuration | Profile Shape Mismatches on DETR Models (`rfdetr_small` 640→512, `rfdetr_medium` 640→576) | **Resolved** |
| **DEF-10** | **P1 (Core)** | Scoring / OCR | OCR winner logic compared the board with the engine's own score — useless whenever the video starts mid-match | **Fixed** |
| **DEF-11** | **P1 (Core)** | Scoring / OCR | Row→player mapping needed 3 *unanimous* geometry votes; one wrong vote (geometry is ~62% right) blocked it forever | **Fixed** |
| **DEF-12** | **P2 (Analytics)** | Analytics | Re-fold after a winner correction left rally `score_after` stale and dropped distance/heatmap data from live analytics | **Fixed** |
| **DEF-13** | **P1 (Core)** | Agentic AI | Tool calls written as JSON text were shown as the answer (Q6, Q7); identical calls repeated (Q2); aggregate stats had no citable id | **Fixed** |
| **DEF-14** | **P2 (Process)** | Testing | Report states `score_ocr.py` is unit-tested in isolation — it had no tests; `agents/` had no tests at all | **Fixed (tests added)** |
| **DEF-15** | **P1 (Core)** | Context / State | Video starting mid-game: score always assumed to start at 0–0 | **Fixed when OCR maps the rows (names or votes); otherwise reported as `score_basis` to the agent** |

---

## Detailed Failure Analysis

### DEF-01: Absence of Match-Phase Model (P0 Critical)
- **Symptom:** In the 8-minute match video, pre-match warmup exchanges and practice shots were segmented into 5 separate rallies and scored by the BWF state machine, advancing Game 1 to 0-21 prematurely.
- **Root Cause:** The `RallyFSM` is binary (`IDLE` vs `IN_PLAY`). There is no higher-level semantic state machine distinguishing:
  * `PRE_MATCH` (introductions, equipment checks, coin toss)
  * `WARM_UP` (players hitting across the net before umpire calls "play")
  * `MATCH_PLAY` (official play after umpire announcement)
  * `INTERVAL` (official 60s/120s breaks)
  * `POST_MATCH`
- **Impact:** Canonical event store contains false points, false rallies, and incorrect match scores.
- **Remediation:** Introduce an explicit `MatchPhase` state machine combining Scoreboard OCR visibility (a score bug appears only during official play), audio umpire call detection, and player activity clustering.

---

### DEF-02: YouTube Ingestion Crash on `invalid media hash` (P0 Critical)
- **Symptom:** Submitting any YouTube URL caused immediate failure: `Analysis failed: invalid media hash. Fix the cause (see the server log), then choose 'Analyse again'`.
- **Root Cause:** In `bai_engine/runtime/runner.py`, `_ensure_media()` called `self.repo.media_paths(s.source.sha256 or "")` at line 151 unconditionally before downloading the YouTube video. Because YouTube sessions begin with `sha256=None`, this passed an empty string to `media_paths("")`. `media_paths` validated `len(sha256) == 64` and raised `ValueError("invalid media hash")`.
- **Resolution:** Modified `_ensure_media()` in `runner.py` to only execute the fast-path check if `s.source.sha256` is non-empty and 64 characters long. Defer `media_paths()` resolution until after the download completes. Verified: YouTube videos now download, transcode, and analyze cleanly.

---

### DEF-03: Scoreboard OCR Unwired in Execution Pipeline (P1 Core)
- **Symptom:** Rally winner attribution accuracy on real broadcast video is only 61.5% because geometric shuttle landing estimation alone frequently confuses near vs far player court boundaries on steep drops and net shots.
- **Root Cause:** While `ScoreReconciler` exists in `score_ocr.py` and `rapidocr_v4` is listed in `manifest.yaml` and `gpu-rtx4000.yaml`, the perception pipeline in `pipeline.py` never instantiates an OCR reader, never crops the scoreboard, and never calls `engine.on_ocr()`.
- **Impact:** The system misses its primary broadcast cross-check oracle, causing score divergence against the visible scoreboard.
- **Remediation:** Wire `RapidOCR` into `pipeline.py` on a low-frequency schedule (e.g., once every 1–2 seconds, or event-triggered 2 seconds post-rally). Reconcile geometric outcomes with the scoreboard text before finalizing points.

---

### DEF-04: Grounding Validator False Positives on Abstentions (P1 Core)
- **Symptom:** When the AI analyst gave accurate negative answers, such as:
  * *"The tool call did not provide data for the 50th rally, likely because it is not part of the provided tool output data"*
  * *"A total of 41 rallies were played in this match"*
  the validator marked them as `grounded: False` with issues like `"uncited number in: The tool call did not provide data for the 50th rally..."`.
- **Root Cause:** In `bai_agents/agent.py`, `validate()` splits text into sentences and searches for any digit:
  ```python
  if re.search(r"\d", plain) and not CITE.search(s) and not re.fullmatch(r"\s*[-*]?\s*\d+[.)]\s*", plain):
      issues.append(f"uncited number in: {plain.strip()[:80]}")
  ```
  It does not distinguish between **factual claims** ("Player 1 hit 15 smashes") and **ordinal qualifiers or abstention statements** ("rally 50", "game 3", "0 points were scored").
- **Remediation:** Update `validate()` to exempt negative assertion contexts, or require citations specifically on metric claims rather than arbitrary sentences containing digits.

---

### DEF-05: Small Local LLM Citation Hallucination (P1 Core)
- **Symptom:** On complex queries, Llama 3.1 8B Q4 produced citations with fabricated reference IDs such as `[[ev:P1_stats]]` rather than the exact UUID event IDs returned in `evidence_ids`.
- **Root Cause:** An 8B parameter quantized model occasionally abstracts the prompt instructions ("cite each one as `[[ev:EVENT_ID]]`") by inserting semantic placeholders like `P1_stats` instead of copying the verbatim UUID string from the JSON tool response.
- **Remediation:** 
  1. Add few-shot in-context examples in `SYSTEM` prompt demonstrating copying exact UUIDs.
  2. Implement an automated repair pass in `agent.py` that maps semantic placeholders (e.g. `[[ev:P1_stats]]`) to the actual `evidence_ids` returned by the tool if unambiguous.

---

### DEF-06: Green Mat Assumption in Court Presence Gate (P2 Analytics)
- **Symptom:** On courts with blue mats (e.g., Olympic tournaments), purple mats (French Open), or wood surfaces, `CourtPresence.is_main_camera()` returns False for all frames, marking every frame as `replay: True`. This halts player and shuttle perception completely.
- **Root Cause:** In `sports/badminton/src/bai_badminton/perception/scene.py`:
  ```python
  HSV_LOWER_COURT = np.array([30, 35, 35])
  HSV_UPPER_COURT = np.array([90, 255, 255])
  ```
  The HSV range strictly bounds green hues.
- **Remediation:** Compute the mat color distribution dynamically from the initial calibrated court polygon region during the first IDR frame, rather than hardcoding static green HSV thresholds.

---

### DEF-07: Racket Pose Model Unwired (P2 Analytics)
- **Symptom:** Profile `gpu-rtx4000.yaml` specifies `racket: model: racketvision_racketpose`, but racket inference never executes.
- **Root Cause:** In `BadmintonPerception`, no `_load_racket` loader was implemented. `contact_fusion_v0` relies entirely on wrist keypoint distance and velocity without validating racket head orientation or collision.
- **Remediation:** Add event-triggered specialist execution for `racketvision_racketpose` around candidate contact frames (±3 frames) to filter out fake swings and body occlusions.

---

## Remediation log (October 2026, `upgrading` branch)

Verified on the Windows CPU development machine with the deterministic synthetic match generator
and unit tests (`uv run pytest`: 147 passed; `apps/web`: tsc clean, vitest 23 passed). **Not yet
re-measured:** the GPU host, the 8-minute broadcast ground-truth match (`Test1_Full_rev.csv`) and
the Llama 3.1 8B agent run — the accuracy numbers in the main report predate these changes.

### DEF-01 — match phase (`sports/badminton/src/bai_badminton/events/match_phase.py`)
Every finished rally is decided *official* or not, from evidence in order of authority:
1. reviewer marks (`POST /corrections` `kind: "official"` per rally, `kind: "match_start"` marker);
2. scoreboard: a stable reading unchanged across the rally ⇒ not scored (warm-up, let, replay);
   changed ⇒ scored — independent of the row→player mapping;
3. BWF serve formation (Laws 9.1): server and receiver set (feet spread ≤ 0.75 m over 1 s) in
   diagonally opposite service courts, plus a pause ≥ 4 s since the previous exchange to *start*
   the match. Missing players never start the match.

In play, rallies count unless the board says otherwise or a rally starts ≤ 3 s after a camera
cut/replay without a serve formation (DEF-08 replay tails). Unofficial rallies stay on the timeline
(`official: false`, `rally_no: null`, `observed_winner`, `phase_reason`) but give no point, no
highlight and no stroke/presence statistics; `match_phase` events record transitions. All
corrections share one re-fold that re-emits only what changed and survives restart/re-analysis.
Known ceiling: the formation test needs a calibrated court and both players' feet; a warm-up rally
that happens to start from a legal serve set-up after a pause will start the match (reviewer
marker or scoreboard corrects it).

### DEF-03 / DEF-10 / DEF-11 / DEF-15 — scoreboard OCR
`perception/scoreboard.py` reads the score bug with RapidOCR between rallies only, searching the
four frame corners one per call and locking onto the board region. The winning row is read from
the board delta (+1, or reset to 0–0 from game point). When the rows are mapped to players and the
first reading is not 0–0, the base score is taken from the board and the match re-folded
(`match_phase` event with `base_state`). Measured cost on this CPU: ~1.2 s per read (locked crop),
i.e. ~0.6 s compute per second of between-rally video on `cpu-dev` (`ocr_every_s: 2`). Existing
perception caches have no OCR readings — re-perceive to use it.

### DEF-04 / DEF-05 / DEF-13 — agent
The validator now checks that every number stated appears in some tool result (percent/rounding
renderings allowed); references ("rally 50", "game 3", "50th") and numbers from the question are
not claims; negative/abstaining sentences need no citation. Tool calls written as JSON text are
executed and fed back; identical calls are answered from cache; placeholder citations are mapped
to the evidence of the named tool call or dropped; raw tool JSON is never returned as an answer.
Tools expose the match phase, official vs unofficial rallies, the observation window and
`score_basis`, `get_rally(rally_no=…)`, and citable `score_event_id` / `smash_event_ids`.

### DEF-06 — court colour
`propose_corners` tries green, blue, purple/red and wood mat families; `CourtPresence` learns the
mat hue (±12) from keyframes inside the calibrated court. Known ceiling: hue-only — on wood floors a
skin-tone close-up can pass the gate (the cut detector still separates shots).

### Still open
DEF-07 (racket model unwired — no weights on this machine), stroke transformer (weights), true-live
latency, and a re-run of the GPU / ground-truth / 8B-agent evaluations against this branch.
