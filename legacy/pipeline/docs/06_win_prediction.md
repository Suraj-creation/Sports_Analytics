# Stage 6 (part 1) — Win Prediction

Files: `win_predictor/predict.py`, `win_predictor/rule_engine.py`,
`win_predictor/traj_rf.py`, `win_predictor/config.py`.

This is the most complex stage in the pipeline — three separate prediction
mechanisms (a hand-written rule engine, a CNN video classifier, a
trajectory Random Forest) whose outputs get fused per-rally into a single
call. It's worth understanding *why* three mechanisms exist rather than
just the most accurate one: they were built in that order, over time,
each added because the previous one(s) had a specific, measured blind
spot, and the fusion logic is largely "trust whichever one is actually
strong for this kind of rally."

**Input per match:** `<name>_ball_filled.csv`, `<name>_rally.csv`,
`<name>_court.json`, `player_detections.csv`, optionally the video itself
(needed for CNN clips) and `<name>_shuttle_size.csv` (needed for the RF's
size features).

**Output:** `win_predictions.csv` — one row per rally: `rally_idx,
start_frame, end_frame, start_time, end_time, winner, loser, win_reason,
reason_src, fault_side, fault_src, cnn_class, cnn_conf, cnn_oob, cnn_hn,
cnn_wbl, score_<player_a>, score_<player_b>`.

`win_reason` is always one of exactly three classes
(`config.CLASSES = ['out_of_bounds', 'hits_net', 'wins_by_landing']`) —
this fixed 3-way schema is what the whole downstream fusion/report/webapp
layer is built around.

---

## Court geometry setup (`rule_engine.load_court_from_json`)

Reads `court.json`, derives everything the rest of the file needs:
- `court_poly_cv` — the 4 corners as an OpenCV-ready polygon, for
  `cv2.pointPolygonTest` in/out checks.
- `net_top_Y` (cable) and `net_ground_Y` (floor reference) kept
  **separate** — `net_top_Y` collapses to nearly the far baseline's pixel
  position in this camera's perspective, so depth alone can't reliably
  distinguish "near the net" from "near the far baseline"; `net_ground_Y`
  plus the net's actual X span (narrower than full court width — the net
  posts sit inside the doubles sidelines) is the reliable "near the net"
  test.
- `net_tol_px = 720 * 0.02 ≈ 18px` — a shared tolerance used throughout:
  a line belongs to the court/net it bounds (the actual badminton rule), so
  a point within `net_tol_px` of a boundary still counts as in/at it, not
  past it.
- `H_metric` — homography from image pixels to a top-down metric
  rectangle (singles: 5.18m × 13.4m), used everywhere a "how far outside
  the court, in real distance" answer is needed instead of a pixel-space
  guess.

## Player side assignment (`assign_player_sides`)

Solves the problem left open by player detection (see
[04_player_detection.md](04_player_detection.md)): `player_1`/`player_2`
are arbitrary per-frame detection slots, not semantically "far" or "near."
Averages each slot's Y position across the whole match, compares distance
to the near baseline (`court_bottom_y`) — whichever slot is *closer* on
average is NEAR (Player B); the other is FAR (Player A). One assignment
per match, computed once, not per-frame — a player doesn't switch court
ends mid-match.

---

## The rule engine (`analyze_rally_end`)

For each rally's `end_frame`, this looks at the shuttle's last ~3 seconds
(`ANALYSIS_SEC=3.0`) of trajectory and works through checks **in priority
order**, returning as soon as one fires:

```
CHECK 0  Shuttle stationary        (most reliable — the shuttle visibly stopped)
CHECK 1  Cable crossing            → wins_by_landing
CHECK 2  At cable + stopping       → hits_net
CHECK 2b Clear positional baseline OOB
CHECK 3  OOB via extrapolation
CHECK 4  Baseline proximity
CHECK 5  Above cable, in court     → wins_by_landing
CHECK 6  OOB fallback
CHECK 7  Final fallback            → wins_by_landing
```

**Why this order:** each check is progressively less direct evidence.
"The shuttle visibly stopped and its position tells you everything" (CHECK
0) is unambiguous when it's available (real trajectory data very often
loses the shuttle right around actual ground contact — see the discussion
in this doc's "known limitation" section below — so CHECK 0 fires less
often in practice than its priority ranking suggests). Further down, checks
rely on increasingly indirect signals: extrapolating a still-moving
trajectory forward to guess where it would have gone (CHECK 3), or falling
back to whichever side of the net the last few frames happened to be on
(CHECK 7) when nothing more specific matched.

**CHECK 0 — stationary** (`static = vels[-6:] where speed < 15px/frame`,
need `>= 3` such samples): average their position, test against the court
polygon (with `net_tol_px` tolerance) and net proximity. This is the
highest-confidence path when the shuttle is genuinely at rest.

**CHECK 1/2 — cable crossing, via the *final segment* only.**
`_last_hit_index()` finds the most recent sharp direction change in
*smoothed* velocity (3-frame rolling average, so a slow net tap's
direction change isn't lost to pixel jitter, `angle_thresh_deg=60`) — this
isolates the shuttle's motion since the last racket contact, so an earlier
net exchange within the 3-second window can't be mistaken for the final
one. If the final segment crosses the cable height: distinguish a clean
winner that briefly touches cable-height in passing from a genuine net
fault by checking whether the trajectory *lingered* near cable height
(`frames_near_cable >= max(8, 40% of segment)`) rather than passing
through briefly — a real net fault drags along the tape, a clean net shot
doesn't.

**CHECK 3 — extrapolation** (`_extrapolate_exit`): if the trajectory
hasn't decelerated much (`decel_rate < 0.35`), project it forward at
constant velocity, frame by frame, up to 45 frames, until it exits the
court polygon. Guarded against a specific false-positive: if velocity
points backward through frames that were actually a *different*, earlier
shot within the analysis window, this would extrapolate through the net in
the wrong direction — detected and skipped (`_backward_extrap`).

**CHECK 7 — final fallback**, when nothing else matched. This is most
often a soft, dying net shot that never registered enough speed or
deceleration to trip the explicit net checks. Only called a clean winner
if the shuttle actually ended up away from the net's floor footprint
*and* its trajectory reached cable height at some point — if it landed far
from the net or never approached the cable at all, it's scored as a winner
by default rather than a fault.

### Fault-side determination

Separate from *which event* happened is *whose fault* it was — which
player hit the shuttle last. `_oob_fault_side()` uses which of the 4
boundary lines was crossed (past the near baseline → far player's fault;
past the far baseline → near player's fault; a sideline exit is split by
net-depth). `hits_net` fault side comes from **approach velocity** just
before the tape contact (which direction was it moving when it hit the
net), not landing position — because a net fault can bounce back onto
either side, making landing position an unreliable signal for who caused
it.

### Post-processing overrides (`apply_overrides`)

A cascade of narrower corrections applied *after* the main check, each
addressing one specific measured failure mode found in evaluation — named
so they're traceable in `reason_src`/debug output: `clip` (vertical net-clip
shape check — mostly-vertical fall + deceleration + resting near the net,
even if the main checks missed it), `prox` (landing lands inside the net's
height band), `oob-fault` (recompute fault side from final position once
event is confirmed OOB), `stable`/`stable2` (shuttle demonstrably stopped
well inside the court), `arc` (steep downward arc mid-flight, still
inside), `netfreeze` (shuttle froze at the net base for many frames —
different signal than a single stationary check), `plhs` (player-proximity
correction — which player was actually moving toward the shuttle, as a
fault-side tiebreaker), `cpf` (court-partition fault using the net's floor
line as a depth divider).

A few explicitly **rejected** alternative designs are left as comments in
the code, with their A/B test results, specifically to stop them being
re-tried: extending the analysis window forward past `end_frame` (tested
at 1.0s and 1.5s, both regressed win-reason accuracy 64.9%→53-55%, because
a shuttle that's genuinely gone out keeps rolling further away —
"looking further forward" gives a *worse* read on where it landed, not
better); using last-hit-segment velocity direction instead of
`_fault_side()` for OOB fault (regressed 58.0%→53.4%).

---

## The CNN ensemble (`predict.py`)

**Architecture:** `r2plus1d_18` (torchvision video backbone), with the
final layer replaced by a small classifier head
(`BatchNorm1d → Linear(256) → ReLU → Dropout(0.3) → Linear(3)`), predicting
the 3 `CLASSES` directly from video.

**Two models, two temporal windows, averaged:** a 20-frame clip sampled
from a 1.5s window (`SEQ_LEN_20F=45` frames back) and a 16-frame clip from
a 3.0s window (`SEQ_LEN_16F=90` frames back) — both centered on the
shuttle's last known position (extrapolated forward along its recent
velocity if tracking was lost a few frames early, up to 15 frames of
extrapolation), cropped to `CROP_FRAC=44%` of frame height around that
point, resized to 112×112. Two temporal scales because a genuine
landing/fault event has both fast local dynamics (contact) and slower
context (the approach) — the ensemble averages both models' softmax
outputs.

Confidence: `cnn_conf = max(softmax)`, `cnn_class = argmax`.

## The trajectory Random Forest (`traj_rf.py`)

A meta-learner: **not** trained on raw video, but on 24 hand-engineered
features from the shuttle trajectory + the CNN's own probabilities.
Binary classifier — OOB vs WBL only (`hits_net` is handled entirely by
the CNN threshold gate below, never by the RF).

**Feature groups:**
- **Trajectory (11):** `margin_cm` (real-world distance from the nearest
  court boundary, via the same metric homography), average/absolute
  velocity, a stationary-pattern flag (`is_post`), point density near the
  end (`n_tight`), a fitted parabola's curvature and vertex-extrapolation
  distance (`para_a`, `para_extrap` — from `np.polyfit` on the last 25
  frames), distance from the far baseline, positional variance (`std_y`).
- **Shuttle apparent size (6):** mean/trend/ratio of the shuttle's
  detected pixel size near the end, from a separate `_shuttle_size.csv` —
  a shuttle growing larger as it approaches the camera/ground is a
  physical landing signal orthogonal to position.
- **CNN probabilities (3):** `prob_oob`, `prob_hn`, `prob_wbl` fed in
  directly — the RF can learn to trust or distrust the CNN differently
  depending on the trajectory context.
- **Net geometry (4):** normalized last position, distance to the net's
  floor line, whether the last X position is within the net's horizontal
  span.

## Fusion strategy — which prediction wins

Per rally, in order:

1. **HN gate first.** If `cnn_hn >= HN_THR (0.60)` — or the lower
   `NET_ZONE_HN_THR (0.45)` when the shuttle's last position is both
   within the net's X span and within `NET_ZONE_DIST=40px` of its floor
   line — the CNN's "hits net" call is trusted, **unless** the RF
   disagrees with high conviction: **Strategy E** — if the RF says WBL and
   the shuttle's `margin_cm` is positive (genuinely inside the court), the
   HN call is overridden to WBL (`reason_src = ML_STRAT_E`). Otherwise,
   hits_net stands (`ML_HN`, or `ML_HN_I` when the lowered net-zone
   threshold was what triggered it).
2. **Otherwise, if the RF has a prediction** (OOB or WBL): normally
   trusted directly (`ML_RF`) — **unless Strategy F** fires: RF says WBL,
   but the *rule engine* independently says OOB, **and** the trajectory
   shows fast lateral motion (`abs_vx > 2.0` and `speed > 4.0`) — a fast
   sideways shot is exactly the case where OOB is more likely correct than
   a size/position-based RF read, so the rule engine's OOB call wins here
   (`ML_STRAT_F`).
3. **No RF prediction available** (model not loaded, or not enough
   trajectory to build features): fall back to the rule engine's own
   `event` directly (`reason_src = RULE`).

**Fault side**, computed *separately* from win_reason: for `wins_by_landing`,
directly from the median shuttle Y in the last 10 visible frames vs.
`net_ground_Y` (`WBL_Y` — position at landing is the most direct evidence
for who's side it landed on); for other reasons, the rule engine's own
fault computation stands.

**`CNN_FIRST_THR = 0.55`** exists in config but the actual fusion logic
above is the HN-gate/RF-first design (Strategies E/F/I/J) that superseded
a simpler "trust CNN if confident enough, else rule engine" scheme — kept
for backward compatibility/reference, not the active decision path.

---

## Known limitation — the stationary-shuttle detector often finds nothing

CHECK 0 (the rule engine's most reliable path) needs the shuttle to be
*tracked* while at rest. In practice, TrackNetV3 frequently loses the
shuttle entirely right around actual ground contact — it was trained to
spot a small fast-moving object against contrast, and a stationary shuttle
sitting on a green court blends into the background. Verified on real
match data: a rally's shuttle trajectory can be falling smoothly and
steadily right up to the very last tracked frame (no visible slowdown at
all), then tracking drops to `Visibility=0` and never resumes for the rest
of the rally. When this happens, the `vels[-6:]` window CHECK 0 examines
is really "the tail of a still-falling arc," not a genuine at-rest
position — the resulting average lands a few frames *before* the true
landing spot.

This is a structural limitation of the detector, not a tuning gap — you
can't find a stationary shuttle in frames where it was never tracked. The
improvement worth building (not yet implemented): extrapolate the last
several *valid* tracked points' falling trend forward through the same
per-rally homography until it crosses the ground plane, and use that
projected crossing as the landing frame/position instead of whatever the
tracker happened to see last. See the win-predictor Random Forest's
`margin_cm`/net-geometry features for the existing homography-based
real-world distance mechanism this would build on.

---

## Parameters reference

| Parameter | Default | File | Meaning |
|---|---|---|---|
| `ANALYSIS_SEC` | 3.0s | rule_engine | Trajectory window examined before `end_frame` |
| `net_tol_px` | ~18px (720×0.02) | rule_engine | Shared boundary tolerance |
| `HIGH_SPEED` / `MED_SPEED` | 350 / 150 px/frame | rule_engine | Speed classification thresholds |
| `RELIABLE_SPD_MIN` | 40 px/frame | rule_engine | Min speed counted as a "reliable" velocity sample |
| `VERTICAL_RATIO` | 1.5 | rule_engine | `_vertical_net_clip_override` vy/vx ratio |
| `VERTICAL_DECEL` | 0.25 | rule_engine | Deceleration fraction for the net-clip override |
| `COURT_W_M` / `COURT_H_M` | 5.18 / 13.4m | rule_engine | Singles court metric dimensions |
| `CLIP_FRAMES` | 20 | config | Frames sampled per CNN clip |
| `SEQ_LEN_20F` / `SEQ_LEN_16F` | 45 / 90 frames | config | CNN look-back windows (1.5s / 3.0s) |
| `CROP_FRAC` | 44% of height | config | CNN clip crop size |
| `OUT_SIZE` | 112px | config | CNN input resolution |
| `HN_THR` / `NET_ZONE_HN_THR` | 0.60 / 0.45 | config | CNN hits-net probability gate (Strategy I) |
| `NET_ZONE_DIST` | 40px | config | Net-zone proximity for the lowered HN gate |
| `CNN_FIRST_THR` | 0.55 | config | Legacy threshold, superseded by HN-gate fusion |
