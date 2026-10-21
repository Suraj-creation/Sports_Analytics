# Platform roadmap — gap analysis against the target architecture

Target: *Unified Sports Video Intelligence Platform* (badminton-first, sports-agnostic, pipeline-plugin based).
This document records where the codebase stands against that specification, what the court-geometry work
in this change delivers, and the ordered plan for the rest. Paths: `E/` = `engine/src/bai_engine/`,
`B/` = `sports/badminton/src/bai_badminton/`, `API/` = `apps/api/src/bai_api/`, `WEB/` = `apps/web/src/`.

## 1. Delivered in this change — court geometry for any broadcast (spec §9.1, §10, §11.1, §21.3)

**Problem.** A court calibration was one homography for one camera pose. Broadcasts (and most YouTube videos)
cut between several cameras, pan and zoom. Every new video needed a hand calibration, and the court overlay
was drawn over close-ups and other cameras. The mat-outline auto-proposal never found a court whose mat
extends past the lines (it proposed the crowd).

**Solution** — `B/perception/court_lines.py`:

| Stage | What it does |
|---|---|
| Line pixels | White top-hat of brightness ∧ low saturation; letters/specks dropped by size; centre ridge (a 12 px line counts once) |
| Line candidates | Hough → robust refit on own pixels → de-duplication |
| Families | Two strongest vanishing points (the second may not contain lines parallel to the first: net tape, board edges) |
| Search | Every line pair × line pair × ordered model-line pair → homography from 4 intersections, vectorised; filtered by **physics** (a real pinhole camera: one focal length, square pixels, above the floor, ≥ 3° elevation, inside the arena); sparse pre-score → coarse score (painted length − ½ unpainted) → ICP refinement of the best 8 |
| Quality gate | precision ≥ 0.6, support ≥ 0.9 frame widths, ≥ 2 lines per direction, court ≥ 4 % of the frame |
| Camera | Homography → focal length, rotation, optical centre (court metres); net-post tops projected exactly |
| Camera identity | **Rotation test**: a frame is the main camera iff `H_t·H_ref⁻¹` is a pure pan/tilt/zoom of the reference camera (`rotation_residual`, 0 for the same head at any zoom, ≥ 0.35 for another camera; robust to ±20 % focal error) |
| Tracking | still camera: thumbnail test (re-verified every 8 frames); moving: optical-flow prediction + ICP at 640 px with a *continuity* check (consecutive fits must be a pure rotation — rejects snapping onto the neighbouring line); undetected cuts (flow cannot connect the frames) trigger an immediate search; fluke runs < 4 frames dropped |

Measured on the Antonsen–Farhan broadcast (12 075 frames, 1280×720): main camera fitted at ~1 px
(precision 0.86–0.96), its optical centre at (−0.2, −21.6, 7.5) m — 21.6 m behind the near baseline, 7.5 m up;
a lower follow camera, two side cameras and close-ups are told apart; **8 ms/frame** average CPU cost
(1 ms on still frames). Synthetic ground truth (`B/testing/court_render.py`): 0.6 px (wide), 1.6 px (tight),
2.5 px (side-on), camera centre within 0.2 m, 1.4–2.6 px through fast pans and zooms.

**Integration.**

* Calibration modes (`B/perception/pipeline.py`): `lines` (measured every frame; only the main camera is
  analysed; other cameras are calibrated for display), `camera` (legacy background tracking when the lines
  cannot be followed), `static`.
* Automatic calibration at session start from 24 sampled frames (`BadmintonSession._auto_calibrate`): the
  camera seen most often is the main camera; its widest view is the reference. Falls back to the mat outline.
* A human calibration is *refined onto the painted lines* when they confirm it (≤ 3 % of the frame width);
  otherwise it is kept as clicked (`lines_check` explains why).
* **Calibration record** (`calibration` event): `mode`, `method`, `validity` (per_frame / tracked / whole_video),
  `calibration_id`, `quality` (precision, support, lines, area, rms), `camera` (focal, centre), `coverage`,
  `adjusted_px`, `net_top`, `frame_size`; confidence = measured line precision.
* **Scene state** per frame (`FramePerception.view/head/court_q`) and a **scene timeline**
  (`B/events/scene.py`, `scene` events: main / alt / none segments with flicker absorption, emitted only when
  final). Camera track rows carry the camera id (`track_id`) and fit precision (`conf`); the wire format adds
  `cam.h`, `cam.q`.
* UI: the court overlay follows every frame, is dimmed/dashed on other cameras and hidden without a court;
  a scene chip ("Other camera · not analysed", "No court in view"); header shows *Court: auto*; the
  calibration page detects the court on the exact frame shown, explains the current mode and offers
  "Re-detect automatically for the whole video" (`POST /api/sessions/{id}/calibration/auto`).
* Correctness fixes: singles rallies are judged in/out against the **singles** sidelines (the doubles polygon
  was used); `MatchConfig.discipline` introduced. The `index -235` crash fix (rally finalised after the
  shuttle window moved) is in `c3f7b0b`.

## 2. Gap matrix (spec area → state → next step)

| # | Area | Exists | Missing / weak | Next step | Pri |
|---|---|---|---|---|---|
| 1 | Plugin contract | `E/sport.py` Protocols, entry points, `B/plugin.py`, `ontology.yaml` | no manifest (stages, capabilities, calibration needs, limitations, eval suites); untyped dict commands; API/agents import `bai_badminton` directly | `PipelineManifest` from `SportPlugin.manifest()`; plugin-provided calibration API, analytics fold and agent tools; typed commands | P1 |
| 2 | Profiles | hardware/model profiles, multi-rate strides | no singles/doubles × static/broadcast × VOD/live axes; 9 profile fields never read | split `HardwareProfile` / `PipelineProfile` stored on `Session`; delete or wire unused fields | P1 |
| 3 | Media & timeline | CFR proxy, exact `Fraction` timeline, decode once | proxy→source PTS map not kept (VFR traceability); live adapters | persist the PTS map at transcode; live adapters later | P2 |
| 4 | Runtime | one runner per session, preview cursor, perception cache | a perception exception fails the whole session; checkpoints never read; random event ids (re-analysis not idempotent) | per-segment failure → `degraded` event + continue; deterministic event ids; producer/consumer split with bounded queue | P1 |
| 5 | Scene state | **delivered**: view/head per frame, scene timeline | slow-motion / replay-logo detection on the main camera; scene states for scoreboard/graphics | replay classifier (frame-rate cadence, logo wipes) feeding match phase | P1 |
| 6 | Calibration lifecycle | **delivered**: record with mode/validity/quality/camera, per-frame validity | per-camera calibrations for alt cameras are display-only; lens distortion not modelled | calibrations per camera head (analyse other cameras when needed); radial distortion term in ICP | P2 |
| 7 | Geometric quality gates | `RallyEvidence.calibrated`, scene gating | metre analytics (distance, heatmaps) not gated by fit quality; foot jitter summed into distance | tag player samples with `calib_id`/`court_q`; analytics only on validated frames; smooth foot tracks; report coverage | **P0** |
| 8 | Observation contract | `TrackSample` + Arrow schema | no coordinate-system id; interpolated shuttle / Kalman-carried boxes not flagged | `coord_sys`, `origin` (observed/interpolated/predicted), `quality_flags` columns | P1 |
| 9 | Doubles | `MatchConfig.discipline` (in/out court) | `PlayerId = Literal["P1","P2"]` everywhere (rules, identity, contact alternation, engine buffers, API, ~20 web files) | roster of sides/teams with string ids; `DoublesRules` (BWF Law 11 service courts); identity up to 2 per half; role assignment separate from tracking; roster-generic UI | P2 (P1 if near-term) |
| 10 | Event lifecycle | append-only log, supersedes, provisional/confirmed/corrected/retracted/human_verified | no candidate/validated/rejected; status conflated with "look-ahead finished"; `rally_start` never resolved | add states with a transition table in the `Event` validator; promote via quality gates | P1 |
| 11 | Correction propagation | `_refold`, `carry_over` | `rally_end.payload.shots` copies stroke labels; `verify_event` does not update them | reference strokes by lineage root; resolve through `current_view` | P2 |
| 12 | Contact & shot | contact fusion, rule classifier, rally FSM, outcome cascade | `landing_court_xy` is the receiver's feet; px/s speeds; flat taxonomy; racket model unwired | true landing point from the trajectory; hierarchical taxonomy in `ontology.yaml`; metric speeds where geometry allows | P2 |
| 13 | Rules & phase | pure BWF fold, match-phase tracker, OCR seeding | no between-rallies/interval/suspended phases; unknown server only in payloads | unknown fields in `MatchState`; phase transitions from scene + BWF transitions | P2 |
| 14 | Analytics & metrics | `MatchAnalytics` fold with evidence ids | no metric registry (unit, denominator, n, validity); two folds (engine vs API) can disagree | `metrics.yaml` + `MetricValue{value, unit, n, denominator, coverage, status, evidence_ids}`; one fold | P1 |
| 15 | Agentic layer | strict tools, citation/number validator, separate KB | badminton tools in the platform package; data-quality tool reads events never emitted | plugin-supplied toolset; data-quality tool over calibration records, scene timeline, metric status | P2 |
| 16 | Observability | Prometheus rate/frontier/queue gauges | GPU gauges declared but unset; no analytical health (shuttle visibility, ID switches, court coverage) | NVML poller; per-segment quality record (court_q, scene coverage, shuttle visibility) in status + System page | P1 |
| 17 | Frontier & UI | single frontier, timeline shading | per-stage frontiers; `SEMANTIC_LEAD_S = 3` too short with OCR wait; evidence drawer; scene strip on the timeline | `SportSession.frontiers()`; shade provisional vs final; render `scene` events as a timeline strip | P1 |
| 18 | Evaluation & governance | synthetic golden tests, sha256 model registry, passphrase auth | no frozen annotated datasets / CI eval; provenance lacks pipeline/ontology versions; any entry point loads | `eval/` package with dataset manifests and thresholds per version; extend `Provenance`; plugin allowlist | P1 |

## 3. Ordered plan

1. **Geometry gates for metric analytics** (P0, S–M) — use `court_q` and the scene view per frame: distance,
   heatmaps, zones and `hitter_court_xy` only from validated main-camera frames; publish coverage.
2. **Replay / slow-motion detection on the main camera** (P1, M) — cadence (duplicated frames), wipes/logos;
   feeds `scene` (`replay`) and match phase, so replays never create rallies.
3. **Per-stage frontiers + scene strip in the UI** (P1, S) — decode / perception / temporal-final /
   scoring-final; draw `scene` events under the timeline; drop the hard-coded semantic lead.
4. **Failure isolation** (P1, S–M) — a failing segment becomes a `degraded` event and a gap, not a failed session.
5. **Event lifecycle states + deterministic ids** (P1, M) — candidate/validated/rejected; idempotent re-analysis.
6. **Metric registry, single analytics fold** (P1, M).
7. **Pipeline manifest + profile axes; remove `bai_badminton` imports from API/agents** (P1, M).
8. **Evaluation harness** (P1, M) — frozen annotated clips (court corners per camera, rally boundaries,
   winners); court-line accuracy and camera classification are already measurable from the synthetic renderer.
9. **Doubles data model, then doubles rules/identity** (P2, L).
10. **Live mode** (P2–P3, L) — causal profile, latency budget, late-correction policy.

## 4. How to verify the court geometry

```bash
uv run pytest sports/badminton/tests/test_court_lines.py sports/badminton/tests/test_plugin_court_lines.py
```

On a real video: the `calibration` event's `mode` should be `lines` with `quality.precision` ≳ 0.8; `scene`
events list the camera segments; in the player, the court overlay stays on the lines through pans and zooms,
is dashed on other cameras and absent on close-ups.
