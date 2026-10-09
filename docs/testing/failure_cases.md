# Failure Cases, Edge Cases & Defect Root-Cause Analysis

**Platform:** Real-Time Badminton Analytics Platform (`badminton-ai`)  
**Evaluation Date:** October 2026  
**Hardware:** NVIDIA GeForce RTX 4080 SUPER / Ubuntu Linux  

---

## Defect Summary Table

| Defect ID | Severity | Subsystem | Title / Failure Symptom | Status |
|---|---|---|---|---|
| **DEF-01** | **P0 (Critical)** | Context / State | Absence of Match-Phase Model leads to Warm-Up & Replay Contamination | **Open (Architecture Gap)** |
| **DEF-02** | **P0 (Critical)** | Ingest / Storage | YouTube Ingest Crashes on `ValueError: invalid media hash` prior to Download | **Resolved** |
| **DEF-03** | **P1 (Core)** | Perception / Scoring | Scoreboard OCR (`rapidocr_v4`) is Unwired in Pipeline, causing Geometric Winner Errors | **Open (Unwired)** |
| **DEF-04** | **P1 (Core)** | Agentic AI | Grounding Validator Regex Over-Rejection on Uncited Numbers in Abstentions | **Open (Validator Defect)** |
| **DEF-05** | **P1 (Core)** | Agentic AI | Local Small LLM (8B) Hallucinates Dummy Event References (`[[ev:P1_stats]]`) | **Open (Model Capability / Prompting)** |
| **DEF-06** | **P2 (Analytics)** | Perception / Scene | Court Presence Gate Fails on Non-Green Badminton Mats (Hardcoded HSV) | **Open (Domain Shift)** |
| **DEF-07** | **P2 (Analytics)** | Perception / Racket | Racket Pose Model (`racketvision_racketpose`) is Unwired in Ingestion Pipeline | **Open (Unwired Specialist)** |
| **DEF-08** | **P2 (Analytics)** | Event Segmentation | False Rally Over-Segmentation from Broadcast Cut Recovery (41 vs 36 rallies) | **Open (Tuning / FSM Gate)** |
| **DEF-09** | **P3 (Minor)** | Configuration | Profile Shape Mismatches on DETR Models (`rfdetr_small` 640→512, `rfdetr_medium` 640→576) | **Resolved** |

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
