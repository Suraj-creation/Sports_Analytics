# Analytics integrity audit — 23 October 2026

Scope: canonical badminton analytics, persisted track measurements and API product projections.
Metric version: **2**, spatial method **court_path_v2**. This inventory distinguishes
deterministic calculation checks from accuracy validation on annotated footage.

## Reproduced defects and changes

1. **Correction lineage:** rally payloads copied stroke labels, subtype, serve flags and player
   assignments. Correcting/retracting the stroke changed player counters but left rally length,
   serving tactics and highlight reasons stale. Rally reconstruction now resolves each embedded
   stroke ID through the current canonical correction chain, uses the replacement payload wholesale
   and drops missing/retracted/duplicate references. Legacy entries with no canonical ID remain
   readable; their provenance is weaker.
2. **Phase leakage:** corrected warm-up strokes acquired new IDs and bypassed the old exclusion
   list. Unsegmented stroke hypotheses also entered official totals. The persisted fold now requires
   membership in an official rally's resolved stroke sequence. The temporal integration applies the
   same official ownership policy to the live engine.
3. **Unsupported physical distance:** filtering nonfinite coordinates before integration bridged
   gaps; timestamps, tracker identity and camera quality were ignored. A stationary +/-0.02 m fixture
   reported 1.2 m in one second. A missing sample, a one-second gap and an identity switch each
   invented a one-metre path. All are regression cases.
4. **Mislabelled landing:** the incumbent engine's landing_court_xy was the receiver's feet.
   Receiver position is now explicitly represented and can populate targeting only. A shuttle
   landing map requires an explicit trajectory/human landing source plus valid camera evidence.
5. **Cache invalidation:** camera quality revisions did not invalidate analytics. Both player and
   camera track directory revisions now participate in the cache token.
6. **Grid edge:** integer truncation admitted a point just below the lower heatmap boundary.
   Floor indexing fixes the negative-boundary case. Low-level add_path preserves nonfinite breaks.

## Spatial policy and limits

A per-frame camera row must be visible, identify main camera 0, contain a finite nine-value
transform and have court-line quality >=0.6. A player row must be visible, have confidence >=0.5,
have finite court coordinates within doubles court plus 0.35 m sideline / 0.75 m end runoff,
and have a nonnegative tracker ID. Multiple rows assigning one player to the same frame are rejected.
Missing or low-quality camera evidence is unavailable, including older coordinate-only live buffers.

Paths require adjacent canonical frame IDs; any absent frame breaks continuity. Paths also break
at rejected observations, identity changes, non-increasing frame time,
gaps >0.25 s and raw speed >12 m/s. Three-sample coordinate medians with original endpoints are
sampled about every 0.2 s; displacement <0.05 m per accepted segment is suppressed. These thresholds
are a conservative, versioned **policy**, not a validated measurement-error bound. Slow small motion
may be suppressed; foot localization, carried detections, homography error and perspective distortion
remain sources of error. The canonical schema does not yet distinguish carried/predicted player boxes.

Public distance is null until at least one valid continuous segment exists; measured stillness is
zero with estimate status. distance_quality exposes accepted_samples, total_samples, coverage,
observed_s, segments, method, reason and status. Coverage is accepted sample frames divided by all
official-rally frames; it is **not** time coverage or an accuracy score. observed_s sums the accepted
measurement segment spans, including accepted stillness. Distance / observed_s is at most an estimated
average over observed segments, not full-match intensity. No gaps are interpolated.

A floor homography estimates court-plane feet positions, not airborne shuttle depth or 3D shuttle
speed. No physiological, calorie, fatigue or injury-risk inference is supported. Singles/two-slot
identity does not establish four individual doubles athletes.

## Metric inventory

Locations below use B = sports/badminton/src/bai_badminton/analytics and
API = apps/api/src/bai_api/product_analytics.py.
All numerical counts depend on accepted upstream events; deterministic tests do not establish
contact, classification, phase, player-attribution or outcome accuracy.

| Output | Definition, inputs and units | Denominator / missing behavior | Location; verification |
|---|---|---|---|
| rallies, unofficial_rallies | Counts of current rally_end records split by official decision | Zero for empty ledger; unknown phase remains upstream policy | B/rebuild.py, B/match.py; regression checked |
| active_play_s, unofficial_play_s | Sum of segmented rally duration_s, seconds, split by official decision | No inference of player time on court; segmented intervals may be incomplete | B/match.py; formula checked, boundaries unlabelled |
| avg_rally_shots, longest_rally_shots | Mean and max resolved canonical sequence length in official rallies | Mean null with no official rallies; max zero | B/match.py; correction/retraction regression checked |
| points_won, points_lost, win_rate | Known winner/loser counts from official rallies; won/(won+lost) | Unresolved outcomes excluded; rate null at zero denominator | B/match.py; deterministic synthetic checks; outcomes unlabelled |
| winners, errors_out, errors_net | Known official rally outcomes by semantic label | Unknown outcomes contribute none; no independent error attribution | B/match.py; aggregation tested, semantic accuracy unverified |
| strokes, smashes, jump_smashes | Resolved attributed stroke labels/subtypes owned by official rallies | Unsegmented/unofficial/retracted excluded; unknown labels remain unknown | B/rebuild.py, B/match.py; lineage regressions |
| smash_points | Known winning rallies whose last resolved shot is winner's smash | Count, not smash conversion rate | B/match.py; corrected subtype/actor regression |
| serves, serve_points_won | Serve-labelled official strokes; winning official rallies whose first resolved shot is winner's serve | Serve assignment depends on classifier and sequence completeness | B/match.py; correction regression |
| points_won_under_pressure | Wins where flags_before indicates game point or deuce | Requires valid deterministic score context | B/match.py; score tests elsewhere, real context unverified |
| distance_m | Sum accepted smoothed court-plane displacements, metres | Null without supported continuous segments; zero means observed stillness | B/spatial.py, B/match.py; synthetic gap/jitter/identity tests; physical error unmeasured |
| distance_quality | Method/status, accepted sample coverage, accepted segment seconds and count | Explicit unavailable reason, coverage denominator all official-rally frames | B/spatial.py, B/rebuild.py; regression checked |
| presence | Grid of accepted sampled player-feet endpoints, 0.25 m cells | Sample count, not calibrated dwell-time occupancy; empty without evidence | B/heatmaps.py, B/match.py; geometric regression |
| movement | Grid weighted by accepted path displacement, metres | Same continuity/quality restrictions as distance | B/spatial.py, B/match.py; synthetic regression |
| origin | Validated player feet at official contact frames | Empty without camera evidence; not exact racket impact location | B/match.py; quality gate implemented, location error unlabelled |
| targeting | Receiver position proxy, not shuttle landing | Requires camera evidence and known receiver; historical alias interpreted explicitly | B/match.py; no claimed shuttle localization accuracy |
| landing | Explicit trajectory/human landing coordinates with camera evidence | Legacy receiver-foot coordinates excluded; usually unavailable | B/match.py; false-landing regression |
| normalized heatmap values, total | Cell values / maximum cell value; raw total retained | All-zero grid remains zero; normalization is not a probability density | B/heatmaps.py; deterministic formula |
| score_timeline, score_after, game_no, score_available | Point state_after/state_before linked through rally ancestry; score_available requires canonical point | Missing point explicitly unavailable; compatibility dict remains 0:0 but omitted from score_timeline and comeback logic | B/rebuild.py, B/match.py; missing-point/scored-point regressions |
| momentum, leader, run, momentum_shifts | EWMA alpha0.3 of known outcomes (+P1/-P2); consecutive winner run; sign crossing with previous magnitude >0.25 | Two-slot heuristic, no sports-science validation | B/match.py; deterministic, not predictive accuracy |
| highlight score/categories/reasons | Bounded0–10 heuristic sum of shot length, variety, smash/jump, defence, net exchange, pressure, momentum and comeback | Ranks official rally evidence; top-k uses category diversity (MMR0.35), not confidence | B/match.py; canonical labels now propagate; ranking utility unvalidated |
| serve_rallies, serve_win_rate | Known-outcome rallies starting with player's observed serve; wins/count | Null rate with no qualifying rallies | API/_tactics; canonical resolved sequence; semantic accuracy unlabelled |
| returns, return_rallies, return_win_rate | Observed second-shot returns after an opponent serve, known-outcome subset; wins/subset count | Null rate at zero denominator; missing shots reduce observation coverage | API/_tactics; counting tested, completeness unmeasured |
| shot_distribution count/share | Official attributed stroke count / all attributed strokes for player | Unknown classes retained; no made-up class for missing evidence | API/_tactics; lineage regression |
| rally_length buckets | Known-outcome official rallies grouped1–4,5–8,9+ observed shots; wins/count | Null rate for empty bucket | API/_tactics; sequence corrections propagate |
| people/history totals | Sum canonical player-slot statistics grouped by explicit normalized session names | Blank/generic names ignored; matching names do not prove identity; missing metrics null | API/_people; synthetic API regression |
| people distance | Sum available estimated session distances | Partial evidence only; no missing sessions imputed as zero | API/_people; null behavior regression |
| progress totals/history | Sum available completed-recording rallies and active_play_s; chronological history | Analysing/failed/unsegmented recordings excluded | API/overview; API regression |
| progress records | Max observed rally shot count; max recording active_play_s | No record without qualifying evidence; no claim of personal all-time completeness | API/overview; API regression |
| overview scope/availability | Completed analytics and bounded session count/truncation, timestamp and event sequence | Missing evidence/partial recordings explicit | API; API regression |
| doubles, shot_speed, challenges | Declared capabilities false | Preserve unavailable UI; no invented individual/pair/speed/challenge numbers | API/Capabilities; API assertions |

## Stored-record diagnostic replay (read-only)

All four existing event databases were opened with SQLite mode=ro; existing Parquet files were
read without reanalysis or source-media processing. FPS was read from each session's stored
media metadata (30,25,25,30), not assumed globally. The following compares the old raw-displacement
formula on the same currently official intervals with the new policy. Lower values do not establish
greater physical accuracy; there are no measured reference distances.

| Session | FPS | Official / unofficial rallies | Official attributed strokes | Old raw path P1/P2 m | New estimate P1/P2 m | Sample coverage P1/P2 |
|---|---:|---:|---:|---:|---:|---:|
| 01M55MFY9GQF6ZXP2SQPQ8X1KG |30|0/1|0|unavailable|unavailable|unavailable|
| 01M55NQMRAS0ATB73XE3XA6S74 |25|24/1|261|545.0/601.4|380.5/354.0|0.989/0.987|
| 01M56T2EED5Z7W9VTGG19FHNTF |25|24/4|176|170.2/195.2|115.3/125.8|0.993/0.997|
| 01M5EXGZNEVGYAJ3AR6CJS5ZG9 |30|50/14|216|136.8/105.1|90.7/77.9|1.000/1.000|

The read-only fold plus old-formula comparison took 9.207 s across the four sessions in this run.
Accepted observation seconds P1/P2 were 245.36/240.24, 133.4/138.28, 179.7/188.333 respectively.
High sample coverage is compatible with wrong player identity or inaccurate foot localization;
it is not a labelled tracking or distance accuracy score.

## Verification and remaining work

- 15 new analytics regressions first failed before their fixes, then passed: canonical correction,
  unofficial correction exclusion, retraction, orphan strokes, grid/missing breaks, calibration
  rejection, timestamp gap, missing coordinates, tracker switch, stationary jitter, continuous
  motion, false landing, dropped frame row and missing/scored-point availability. A separate
  camera-revision regression failed before cache repair.
- 46 focused analytics/engine/restore/API cases passed before score availability (two existing
  Starlette deprecation warnings). The final 48-case run had 45 passes and 3 API startup failures
  while the concurrent frontend build temporarily removed dist/assets. After the build completed,
  all 3 failures plus the 16 analytics/cache regressions passed (19 tests). Changed analytics/API
  files pass Ruff and git diff --check.
- Temporal integration owns live official stroke gating; persisted reconstruction is authoritative
  for API, agents and exports. Coordinate-only legacy live buffers withhold physical metrics.
- Missing point evidence now explicitly sets score_available=false; score_timeline and comeback
  highlights omit unsupported scores. Existing score_after dict shape remains compatible.
- Receiver time has no dedicated camera-quality reference in older stroke payloads; targeting is
  a proxy with weaker temporal provenance than player paths.
- Pre-phase legacy logs without an official field retain the prior official=true interpretation;
  this compatibility behavior is not proof that the footage contains official play.
- Phase, shot type, contact timing, event boundaries and four-player identity need manually reviewed
  held-out labels. This audit makes claims reproducible and abstention explicit; it does not supply
  missing accuracy ground truth or promote a replacement model.
