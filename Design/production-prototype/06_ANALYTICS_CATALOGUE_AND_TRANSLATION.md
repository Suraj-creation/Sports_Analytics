# 06 — Analytics Catalogue and Translation

**What this file is:** the complete list of what the amateur product may *say* about a match, how each number is defined, where it comes from in the engine, how it is shown, and under what evidence it may be shown at all. It also specifies the **insight ranking system**, the **rebuilt Moment (highlight) system**, the **report redesign**, the **Coach chat** (Ask) behaviour and the **narration contract**.
**Reads with:** file 00 (decisions D1–D18, vocabulary, readiness ladder §7, component names §6) and file 02 (what the engine produces today, gaps `G-xx`).
**Conventions**

| Symbol | Meaning |
|---|---|
| **A / P / N** | Readiness label per file 00 §7: **A**vailable · **P**review (shown with a *Preview* tag) · **N**ot yet (hidden, or a quiet "coming" note) |
| **Q / G / Adv** | Lowest Depth at which a metric appears: Quick · Guided · Advanced. `Q+` = Quick and everything above |
| **R E I C** | Preset visibility: **R**elax · **E**xplore · **I**mprove · **C**ompete (file 00 D3). A metric listed for a preset also needs its depth rule |
| `field` | A real field in the code today. `new` = needs backend work (see file 11) |
| illustrative | Any number in a worked example is invented to show the mechanism, not a measurement |

---

## 1. Design stance

### 1.1 Deterministic core, amateur presentation (D2, D6, D16)

> **Analytics stay professional. Presentation is built for an amateur. Presentation changes order, wording and density — never the factual standard.**

- Every number is computed by a **deterministic, versioned fold** over the event log (`MatchAnalytics`/`rebuild.build` today; the metric registry in §2 tomorrow). No model, and certainly no LLM, may produce, round or "improve" a number.
- Every displayed claim resolves to **evidence** (event ids → frame range → "Watch this") and to a **definition** (numerator, denominator, exclusions, sample size, coverage) one tap further (D16).
- Metrics we cannot stand behind are **withheld** (A/P/N, D10). "Not enough to say" is a designed, normal state — not an error.
- The default reference is **your own comparable history**, never other people (D6, D8).
- The scoreline is **context, not a verdict** (D6). Win/loss-centric numbers (`win_rate`, momentum, head-to-head) live in Deep dive → Story.

### 1.2 The metric contract (from Amateur v2 §5.2 and Spec v1 doc 05 §1)

A metric may be **player-facing** only if all of these are defined. If any is missing it stays internal or is labelled *experimental/Preview*.

| # | Contract field | Where it lives |
|---|---|---|
| 1 | Stable id and display name (`m.*`) | §2 |
| 2 | Plain-language definition | §2 |
| 3 | Formula / deterministic rule: **numerator** and **denominator** | §2 |
| 4 | Required source events | §2 "engine source" |
| 5 | Inclusion/exclusion rules (e.g. official rallies only; warm-up excluded) | §2 |
| 6 | Minimum sample | §2, §3.3 |
| 7 | Confidence & coverage logic (D5) | §3.4 |
| 8 | Calibration assumptions (court fit, camera class) | §2 "failure modes" |
| 9 | Known failure modes | §2 |
| 10 | Comparison eligibility | §3 |
| 11 | Evidence links (event ids) | `MetricValue.evidence_ids` (G-19) |
| 12 | Versioned implementation (`definition_version`) | `MetricValue` |
| 13 | User-facing explanation (`MetricPopover` copy) | §2 "copy" |
| 14 | A correction path (`FixSheet`) | file 05b |

### 1.3 `MetricValue` — the response shape every metric uses (new; G-07)

```json
{
  "metric_id": "m.session.longest_rally",
  "definition_version": 1,
  "scope": "player | match | pair",
  "value": 14,
  "unit": "shots",
  "numerator": null,
  "denominator": null,
  "sample_size": 22,
  "coverage": { "rallies_followed": 22, "rallies_total": 24, "court_valid_frac": 0.93 },
  "state": "available | preview | not_yet | insufficient | not_comparable",
  "check": "checked | looks_right | worth_a_look | none",
  "comparison": { "baseline": "your_last_comparable", "value": 11, "n_matches": 3, "eligible": true, "reason": null },
  "evidence_ids": ["01J…rally_end", "01J…stroke"],
  "limitations": ["shots are detected contacts, not classified strokes"],
  "generated_at": "ISO-8601"
}
```

Rules: `value: null` + a `state` is how *missing*, *zero*, *insufficient* and *not applicable* are kept apart (never render a missing value as 0). A rate always carries `numerator`, `denominator` and `sample_size`; the UI prints "41 of 47", not just "87 %".

### 1.4 Mapping engine evidence to the player's words (D5)

| Engine today | `check` (UI word) | Rule |
|---|---|---|
| `status ∈ {human_verified, corrected}` | **Checked** | Always shown; claim may use "your" and "first" |
| `band = confirmed` (conf ≥ 0.85) and `status = confirmed` | **Looks right** | Allowed for descriptive claims; **uncalibrated** (G-08) → surface-wide *Preview* tag until calibrated on target footage |
| `band = probable` (0.60–0.85) | **Worth a look** | Never in a headline; allowed in a list with a "check this" affordance |
| `band = uncertain/unknown`, `provisional`, `retracted` | **Not enough to say** | Hidden from the recap; listed in Review & fix |

Two facts from the code that this table must respect: **(a)** the rule classifier caps stroke confidence at `0.7` (`RuleStrokeClassifier.MAX_CONF`), so **no rule-classified shot can ever be "Looks right"** — shot claims are *Worth a look* until a person checks them; **(b)** `outcome_confidence` maps rule `HIGH` to 0.85 (→ *confirmed* band) while winner accuracy was measured at 61.5 % on the only real-video check, so "Looks right" for a **winner** is itself provisional until G-08 and G-11 land.

### 1.5 Definitions every metric shares

| Term | Definition |
|---|---|
| **Official rally** | A `rally_end` event with `payload.official ≠ false`. Warm-up/replay exchanges (`official:false`) are excluded from every metric; they appear only as a "not counted" note |
| **Shot (contact)** | A detected racket–shuttle contact attributable to a player (`stroke` event with `actors.player_id`). A *shot* is a **contact**, not necessarily a classified stroke type. `RallyRecord.n_shots = len(shots)` |
| **Rally length** | `n_shots` of an official rally (detected contacts), **not** seconds |
| **Active play** | Σ `RallyRecord.duration_s` over official rallies = "time the shuttle was in play". Not exercise time, not time on court |
| **Followed rally** | An official rally for which the court was valid and both players were tracked for its duration (new; part of coverage, G-20) |
| **Eligible attempt** | An observed event that creates a defined *opportunity* (e.g. an opponent attack that reached you). No opportunity → metric is **not applicable**, never 0 % |
| **Comparable match** | See §3.1 |

---

## 2. Metric registry (≈ 50 metrics)

Each group has a **definition table** (what it is, how computed, where from) and a **presentation table** (comparison, depth, presets, readiness, component, failure modes, copy). Copy uses `{}` placeholders and follows file 09 voice (observation before interpretation; counts with denominators; no trait language).

### 2.1 Match and session

**Definitions**

| id | Plain label | Definition | Numerator / denominator | Exclusions · min sample | Engine source |
|---|---|---|---|---|---|
| `m.session.duration` | Video length | Length of the analysed recording | — | — · n/a | `Session.media.duration_us` |
| `m.session.active_play_s` | Shuttle in play | Σ duration of official rallies | — | Official only · ≥ 3 rallies | `analytics.active_play_s`, `RallyRecord.duration_s` |
| `m.session.rally_count` | Rallies | Count of official rallies | — | Official only · ≥ 1 | `analytics.rallies` |
| `m.session.longest_rally` | Longest rally | Max `n_shots` among official rallies | — | Official only; shots = detected contacts · ≥ 5 rallies | `analytics.longest_rally_shots` |
| `m.session.avg_rally` | Typical rally | **Median** `n_shots` (switch from today's mean `avg_rally_shots` — one 30-shot outlier distorts a mean) | — | Official only · ≥ 8 rallies | `new` (median of `RallyRecord.n_shots`); today `analytics.avg_rally_shots` is a mean |
| `m.session.rally_length_dist` | How long your rallies ran | Histogram of `n_shots` in bins 1–3, 4–6, 7–9, 10–14, 15+ | count per bin / official rallies | Official only · ≥ 8 rallies | `new` from `RallyRecord.n_shots` |
| `m.session.rallies_followed` | What we could see | Followed rallies / all detected rallies | followed / detected | — · always shown | `new` (G-20) from `scene`, `calibration.coverage`, tracks |
| `m.session.not_counted` | Not counted | Count of `official:false` rallies and why (`phase_reason`) | — | — · always shown if > 0 | `analytics.unofficial_rallies`, `payload.phase_reason` |
| `m.session.court_found` | Court found | Fraction of frames with a valid main-camera court fit | valid frames / analysed frames | — · always shown | `calibration.quality`, `scene` events (`court_quality`) — `new` aggregate (G-20) |

**Presentation**

| id | Comparison eligibility | Depth · presets | Label | Component | Failure modes | Copy template |
|---|---|---|---|---|---|---|
| `m.session.duration` | n/a | Q+ · R E I C | A | `MatchCard`, `RecapHeader` | VFR sources (proxy is CFR) | "{mm:ss} of video" |
| `m.session.active_play_s` | Same match type, ≥ 80 % rallies followed | Q+ · R E I C | A | `FactTrio` | Rally over-segmentation (DEF-08: 41 predicted vs 36 true) inflates it; warm-up leakage | "The shuttle was in play for {mm} min of this {mm}-min video." |
| `m.session.rally_count` | Same match type & discipline | Q+ · R E I C | A | `FactTrio`, `MatchCard` | Over/under-segmentation; replays | "{n} rallies" (never "{n} points" — that needs a verified score) |
| `m.session.longest_rally` | §3.1; needs ≥ 5 rallies both matches | Q+ · R E I C | A | `HeroMoment` (as a Moment), `FactTrio`, `PersonalBestCard` | False-positive contacts inflate it (G-27); phrase as "{n} shots detected" in `MetricPopover` | "Your longest rally was {n} shots. Watch it." |
| `m.session.avg_rally` | §3.1 | G+ · E I C | A | `FactTrio` (Guided), `ProgressCard` | Small n; multimodal (many short + a few long) | "A typical rally ran {n} shots (middle value of {N} rallies)." |
| `m.session.rally_length_dist` | §3.1 | G+ · E I C | A | `RallyTimeline` (strip) + small histogram in `ProgressCard` | Bin edges are arbitrary — show counts, not percentages | "{a} short, {b} medium and {c} long rallies." |
| `m.session.rallies_followed` | n/a (it *is* coverage) | Q+ · R E I C | A | `CoverageBar` | Over-reporting if tracking gaps are not counted | "We followed {k} of {N} rallies." |
| `m.session.not_counted` | n/a | Q+ (if > 0) · R E I C | A | `ReviewBanner` | Wrongly dropped casual rallies | "{n} rallies weren't counted ({reason}). Count them?" |
| `m.session.court_found` | n/a | G+ · E I C | P | `CoverageBar` (detail) | Behind-baseline/high/side-on phone angles untested (G-11) | "We could see the court on {pct}% of the video." |

### 2.2 Moments

**Definitions**

| id | Plain label | Definition | Numerator / denominator | Exclusions · min sample | Engine source |
|---|---|---|---|---|---|
| `m.moment.count` | Moments found | Number of eligible Moments after lens, fairness and consent filtering | — | Consent-ineligible removed · n/a | `new` (§7); today `highlight` events |
| `m.moment.per_player` | A moment for everyone | For each participant: count of Moments where they are credited (shared or exclusive) | — | — · each participant ≥ 1 or an honest *why-not* (D17) | `new` |
| `m.moment.lens_strength` | (internal) | Per-lens strength ∈ [0,1] before reliability weighting | — | Internal; never shown as a number | `new` (§7.3) |

**Presentation**

| id | Comparison | Depth · presets | Label | Component | Failure modes | Copy |
|---|---|---|---|---|---|---|
| `m.moment.count` | n/a | Q+ · R E I C | A (rally-based lenses) / P (shot-based lenses) | `MomentStrip`, `MomentCard` | Too few rallies → fewer Moments | "{n} moments from this match" |
| `m.moment.per_player` | n/a | Q+ · R E I C | A | `RecapHeader` (per-person tabs), `NotEnoughToSay` | Attribution wrong (identity swaps) | "Here's a moment for {name}" / "We couldn't find a moment for {name} we're sure about — {reason}." |

### 2.3 Shots (all **Preview** — shot classification is rule-based, max 0.7 confidence)

**Definitions**

| id | Plain label | Definition | Numerator / denominator | Exclusions · min sample | Engine source |
|---|---|---|---|---|---|
| `m.shot.repertoire` | Shots spotted | **Set** of distinct stroke types with ≥ 2 contacts **or** ≥ 1 human-Checked contact; `unknown` excluded | count of types | Official rallies · ≥ 10 classified contacts | `PlayerStats.strokes` (excl. `unknown`), `stroke.payload.stroke` |
| `m.shot.count_by_type` | Shots by type | Count of contacts per stroke type | — | Official only; `unknown` shown separately as "unclassified" | `PlayerStats.strokes` |
| `m.shot.share_by_type` | Shot mix | Type count / all classified contacts of that player | count_type / classified contacts | `unknown` excluded; show the denominator · ≥ 15 classified | `PlayerStats.strokes` |
| `m.shot.first_seen` | First | First **spotted** occurrence of a stroke type in the player's history | — | Needs history coverage ≥ 3 prior matches *or* "first on record"; `Checked` or player confirm for the headline | `new` (history, G-02) from `stroke` events |
| `m.shot.observed_not_mastered` | (copy rule) | A repertoire entry is *observed*, never *mastered*; no skill level is derived | — | Rule, not a number | — |
| `m.shot.classified_share` | How many shots we could name | Classified contacts / all contacts | classified / contacts | — · always shown with shot panels | `PlayerStats.strokes` (`unknown` vs rest) |
| `m.shot.smash_count` | Smashes spotted | `strokes["smash"]` (incl. `jump_smash` subtype shown separately) | — | Official only | `PlayerStats.smashes`, `jump_smashes` |
| `m.shot.sequence_pairs` | Shot sequences | Frequency of consecutive (own shot → opponent reply type) pairs | pair count / all pairs | ≥ 30 classified pairs; both shots ≥ *Worth a look* | `new` from `RallyRecord.shots` order |
| `m.shot.net_duel_len` | Net exchange length | Longest run of consecutive `net`-family shots in a rally | — | `net` family = `rush, net_shot, cross_net` | `new` (family via `ontology.yaml`) |

**Presentation**

| id | Comparison | Depth · presets | Label | Component | Failure modes | Copy |
|---|---|---|---|---|---|---|
| `m.shot.repertoire` | Same discipline, classifier version | G+ · E I C (Relax: only inside a Moment) | P | `ShotRepertoireGrid`, `ShotMix` | Misclassified contacts add phantom types; Preview | "We spotted {k} kinds of shot: {list}." |
| `m.shot.count_by_type` | Same | Adv · I C | P | `ShotMix` (table) | Same | "{n} {type}s spotted ({u} we couldn't name)." |
| `m.shot.share_by_type` | Same, ≥ 15 classified in both | Adv · I C | P | `ShotMix` | Frequency ≠ effectiveness | "About {x} of {y} shots were {type}s." |
| `m.shot.first_seen` | History | G+ · E I C | P | `FirstBadge`, `JourneyTimeline` | A false first is the worst error — gate hard | "First time we've spotted a {type}. Was that one? Yes / No" (asks, doesn't assert) |
| `m.shot.observed_not_mastered` | — | all | — | `ShotRepertoireGrid` footnote | — | "Spotted in video — not a skill grade." |
| `m.shot.classified_share` | n/a | G+ · E I C | P | `CoverageBar` (shots) | Low share ⇒ suppress shot panels | "We could name {a} of {b} shots." |
| `m.shot.smash_count` | Same | Adv · I C | P | `ShotMix` | Smash assessment uses speed/above-head/jump features; often wrong from low angles | "{n} smashes spotted." |
| `m.shot.sequence_pairs` | Same | Adv · C | P | Deep dive → Shots (table) | Sparse | "After your {a}, your opponent most often replied with a {b} ({k} of {n})." |
| `m.shot.net_duel_len` | Same | G+ · E I C | P | `MomentCard` (lens Net duel) | Net shots hard to classify from behind | "A {n}-shot net exchange." |

### 2.4 Rally-keeping and defence (opportunity-adjusted; only where the denominator is defensible)

**Definitions**

| id | Plain label | Definition | Numerator / denominator | Exclusions · min sample | Engine source |
|---|---|---|---|---|---|
| `m.rally.long_share` | Longer rallies | Official rallies of ≥ *T* shots / all official rallies. *T* defaults to **8**, or the player's own median + 3 once ≥ 3 matches exist | rallies ≥ T / rallies | Official only · ≥ 8 rallies | `RallyRecord.n_shots` |
| `m.rally.kept_alive` | Shots that kept it going | The player's contacts that were **followed by an opponent contact** in the same rally / the player's contacts in rallies whose ending is known (`outcome ≠ unknown`) **minus** the final contact of each rally | followed / eligible | Last contact of each rally excluded (it is by definition not followed); `unknown` outcome rallies excluded · **≥ 20 eligible contacts** | `new` from ordered `RallyRecord.shots[].player_id` |
| `m.rally.kept_alive_vs_attack` | Returned when attacked | Opponent **attack-family** shots (`smash, drop, drive, rush`, per `ontology.yaml`) that the player **reached with a contact** / opponent attack shots after which a contact **or** a rally end occurred with the player as receiver | reached / attacks received | Needs opponent shot classification ≥ *Worth a look*; unclassified excluded · **≥ 8 attacks received** | `new`; `receiver_id` in `stroke.payload` |
| `m.rally.recovery_after_long` | Pressed and still in it | Rallies in which the player made ≥ 4 `lift/defence`-family shots **and** the rally continued ≥ 3 further contacts | such rallies / rallies | Classification-dependent · ≥ 8 rallies | `new` (feeds lens *Saved it*) |

**Presentation**

| id | Comparison | Depth · presets | Label | Component | Failure modes | Copy |
|---|---|---|---|---|---|---|
| `m.rally.long_share` | §3.1 | G+ · E I C | A (thresholded on contacts) | `ProgressCard`, `TrendSmallMultiples` | Threshold arbitrary — show the threshold | "{k} of {N} rallies ran {T}+ shots." |
| `m.rally.kept_alive` | §3.1, same discipline | G+ · I C (E: inside a Moment only) | P | `ProgressCard` | Contact false positives/negatives; two players' contacts mis-attributed on identity swaps | "{a} of {b} of your shots kept the rally going." |
| `m.rally.kept_alive_vs_attack` | §3.1, ≥ 8 in both | Adv · I C | P | `InsightCard` | Opportunity changes with opponent; **no opportunities ⇒ "not applicable", never 0 %** | "You returned {a} of the {b} attacking shots that reached you. (Small sample.)" |
| `m.rally.recovery_after_long` | §3.1 | G+ · E I C | P | `MomentCard` (Saved it) | Depends on shot families | "You kept this one alive through {n} defensive shots." |

> **Not built (and why):** a "winner/error ratio", "unforced errors", "smash success %", and any "shot effectiveness %" — the denominators (what was *forced*, what the opponent *could* return) are not observable from the current evidence (D10; see file 02 R-1, R-2).

### 2.5 Placement and landing

**Definitions**

| id | Plain label | Definition | Numerator / denominator | Exclusions · min sample | Engine source |
|---|---|---|---|---|---|
| `m.place.opponent_met_map` | Where your opponent met the shuttle | Heat grid of the **receiver's feet position at their next contact** after the player's shot | — | Valid court frames only (G-09) · ≥ 25 shots | `HeatmapSet` kind `landing` (= `stroke.payload.landing_court_xy`) — **honest rename**, see file 02 §3.4 |
| `m.place.landing_zone_share` | Where your shots landed | Share of the player's shots whose **landing point** falls in each of the 3×3 court zones (`ontology.yaml: court_zones`) of the *opponent's half* | shots in zone / shots with a known landing | Needs a true landing estimate (G-10) | `new` — **not available today** |
| `m.place.zone_variety` | Court explored | Number of distinct opponent-half zones receiving ≥ 2 landings | count of zones (0–9) | Needs G-10 | `new` |

**Presentation**

| id | Comparison | Depth · presets | Label | Component | Failure modes | Copy |
|---|---|---|---|---|---|---|
| `m.place.opponent_met_map` | Same camera class, calibrated | Adv · I C | P | `CourtMap` + `HeatmapKindTabs` | Receiver position ≠ landing; occluded feet | "Where your opponent was when they played your shot back." |
| `m.place.landing_zone_share` | n/a | — | **N** | — | — | (hidden; "coming" note only on Explore → Court Explorer) |
| `m.place.zone_variety` | n/a | — | **N** | `ChallengeCard` (Court Explorer) when available | — | — |

> The current `targeting` heatmap is dropped: it adds the same point as `landing` (file 02 finding 6, G-17).

### 2.6 Presence and coverage on court

**Definitions**

| id | Plain label | Definition | Numerator / denominator | Exclusions · min sample | Engine source |
|---|---|---|---|---|---|
| `m.court.presence_map` | Where you stood | Heat grid of the player's foot positions during official rallies (subsampled ≈ 5 Hz), normalised to the busiest cell | — | **Only valid main-camera frames** (G-09) · ≥ 200 samples | `HeatmapSet` kind `presence`; `analytics.on_presence` |
| `m.court.zone_coverage` | Court you used | Share of 3×3 zones of the player's own half in which they spent ≥ 5 % of presence time | zones ≥ 5 % / 9 | Same validity rule · ≥ 200 samples | `new` from the `presence` grid |
| `m.court.front_rear_split` | Front / back split | Presence share in front third vs rear third of own half | — | Same | `new` from the `presence` grid |

**Presentation**

| id | Comparison | Depth · presets | Label | Component | Failure modes | Copy |
|---|---|---|---|---|---|---|
| `m.court.presence_map` | Same camera class + calibration quality ≥ gate | G+ · E I C (one map in "My game") | P | `CourtMap` | Camera moved; foot jitter; two players' tracks swapped | "Where you stood while the shuttle was in play." |
| `m.court.zone_coverage` | Same | Adv · I C | P | `ProgressCard` | Narrow tracking window | "You spent time in {k} of 9 areas of your half." |
| `m.court.front_rear_split` | Same | Adv · I C | P | `CourtMap` caption | Perspective bias | "More time near the back than the front this match." |

### 2.7 Distance, speed, intensity — **Not yet**

| id | Plain label | Why not | Gate to move up | Engine source |
|---|---|---|---|---|
| `m.move.distance_m` | Distance covered | Per-sample path with no smoothing and no `court_q` gate; foot jitter is summed (`heatmaps.add_path`, ROADMAP #7) | Geometry gates + smoothing + coverage (G-09) | `PlayerStats.distance_m` (**hidden**) |
| `m.move.speed` | Movement speed | Needs time sync + validated scale | Same | `new` |
| `m.move.intensity_proxy` | Effort proxy | Video-derived proxy, not physiology | Validation study | `new` |

Never shown as a number to players. Not exported in the Match story. Keep in the analyst PDF only after the gate.

### 2.8 Serve

**Definitions**

| id | Plain label | Definition | Numerator / denominator | Exclusions · min sample | Engine source |
|---|---|---|---|---|---|
| `m.serve.count` | Serves | Contacts with `is_serve = true` by the player | — | Official only | `PlayerStats.serves` |
| `m.serve.short_long_split` | Short vs long serves | `short_serve` / (`short_serve` + `long_serve`) | short / classified serves | Classified serves only · ≥ 8 | `PlayerStats.strokes` |
| `m.serve.points_won_on_serve` | Points after your serve | Rallies you served and won / rallies you served | won / served | Scored matches only; winner Checked | `PlayerStats.serve_points_won` (numerator), `serves` (denominator) |

**Presentation**

| id | Comparison | Depth · presets | Label | Component | Failure modes | Copy |
|---|---|---|---|---|---|---|
| `m.serve.count` | n/a | Adv · I C | A | Deep dive → Shots | Serve detection = first contact of rally | "{n} serves." |
| `m.serve.short_long_split` | Same | Adv · I C | P | `ShotMix` | Short/long confusion | "{a} short and {b} long serves spotted." |
| `m.serve.points_won_on_serve` | Same, scored | Adv · C | P | `HeadToHead` | Server identity depends on BWF fold; opponent-fault winners | "You won {a} of {b} rallies you served." |

### 2.9 Pressure and close finishes (scored matches only)

| id | Plain label | Definition | Numerator / denominator | Exclusions · min sample | Engine source | Depth · presets | Label | Component | Failure modes | Copy |
|---|---|---|---|---|---|---|---|---|---|---|
| `m.pressure.points_won` | Points at game point/deuce | Points won when `flags_before.game_point` or `deuce` / points played in those states | won / played | Scored matches with **Checked** score; ≥ 4 pressure points | `PlayerStats.points_won_under_pressure`; `payload.flags_before` | Adv · C | P | `ScoreStory` | A mid-game clip starting at 0–0 fabricates pressure flags (G-04, DEF-15) | "At game point or deuce you won {a} of {b}." |
| `m.pressure.close_finish` | Close finish (Moment lens) | A game that ended within 2 points **or** went to deuce | — | Scored + Checked | `flags_before.deuce/game_point/match_point` | G+ · E I C (as a Moment only) | P | `MomentCard` | Same | "A close finish — {a}–{b}." |
| `m.story.comeback` | Comeback (Moment lens) | Winner trailed ≥ 5 in the game then levelled/led (`_is_comeback_point`) | — | Scored + Checked | `score_timeline`, `match._is_comeback_point` | G+ · E I C (Moment only, framed neutrally) | P | `MomentCard` | Same | "A game that swung back from {n} points down." |

### 2.10 Score and story (D6)

| id | Plain label | Definition | Numerator / denominator | Exclusions · min sample | Engine source | Depth · presets | Label | Component | Failure modes | Copy |
|---|---|---|---|---|---|---|---|---|---|---|
| `m.story.scoreline` | Score (context chip) | Final games/points from the verified fold | — | Scored match only; winners Checked or marked Preview | `score_timeline[-1].score`, `state.completed_games` | Q+ · all (chip, never headline) | P → A once Checked | `RecapHeader` chip, `ScoreStory` | Winner accuracy (finding 4); mid-game start | "Final score {a}–{b}{ (preview)}" |
| `m.story.games` | Games | `completed_games` list | — | Scored only | `MatchState.completed_games` | G+ · E I C | P | `ScoreStory` | Same | "{g1}, {g2}…" |
| `m.story.points_won` | Points won (head-to-head) | `points_won` per player | — | Official, Checked winners | `PlayerStats.points_won/points_lost`, `win_rate` | Adv · C | P | `HeadToHead` | Win-centric; D6 | "{a} of {b} points." (no `%`, no crown) |
| `m.story.momentum_series` | Momentum | EWMA (α 0.3) of ±1 per point; shifts when sign flips and |prev| > 0.25 | — | Scored + Checked · ≥ 10 points | `analytics.momentum`, `momentum_shifts` | Adv · C | P | `MomentumChart` | Implies who is "winning"; truncated to last 60 in `to_public()` (G-21) | "Runs of points: {player} took {n} in a row." |
| `m.story.longest_run` | Longest run of points | Max consecutive points by one player | — | Scored + Checked | `analytics.momentum[].run` | Adv · C | P | `ScoreStory` | Same | "{n} points in a row." |

### 2.11 Personal bests, firsts and comparable-session change

**Definitions**

| id | Plain label | Definition | Numerator / denominator | Exclusions · min sample | Engine source |
|---|---|---|---|---|---|
| `m.pb.longest_rally` | Personal best: longest rally | Max `n_shots` in any **comparable** official rally in the player's history; a PB is declared only when the new value > previous max **and** ≥ 3 comparable prior matches *or* the claim says "longest so far" | — | Comparable (§3.1); ≥ 3 prior matches for "personal best", else "longest so far" | `new` (history, G-02) |
| `m.pb.rally_variety` | Personal best: most shot types in one rally | Max distinct classified types by the player in one rally | — | Preview; Checked or ≥ *Looks right* contacts | `new` |
| `m.pb.longest_session_play` | Personal best: longest play | Max `active_play_s` among comparable matches | — | Same match type | `new` |
| `m.progress.delta` | Since last time | Value now − value in the **last comparable match** for a metric `m` with a defined smallest meaningful change | — | §3.2 tiers; both matches eligible | `new` |
| `m.progress.n_comparable` | Matches we can compare | Count of comparable matches in the window | — | — · always shown beside any delta | `new` |
| `m.progress.pattern` | Pattern across matches | A direction held across ≥ 4 comparable matches over ≥ 3 weeks, with each match-level value (not rally-level) as the unit | — | §3.2 tier 2 | `new` |

**Presentation**

| id | Comparison | Depth · presets | Label | Component | Failure modes | Copy |
|---|---|---|---|---|---|---|
| `m.pb.longest_rally` | History, §3.1 | Q+ · all | P (needs history) | `PersonalBestCard`, `HeroMoment` | A PB from a false-positive contact; camera/format change | "A new personal best: your longest rally yet — {n} shots (previous {p})." / "Your longest rally so far — {n} shots." |
| `m.pb.rally_variety` | History | G+ · E I C | P | `PersonalBestCard` | Classification | "Most kinds of shot in one rally so far: {k}." |
| `m.pb.longest_session_play` | History | G+ · E I C | P | `PersonalBestCard` | Over-segmentation | "Most time in play in a match so far: {mm}." |
| `m.progress.delta` | §3.2 tier 1 | G+ · E I C | P | `ProgressCard`, `ComparabilityNote` | One-off good/bad match; regression to the mean | "Compared with your last similar match: {x}. Early signal — {n} matches so far." |
| `m.progress.n_comparable` | n/a | G+ · E I C | P | `ComparabilityNote` | — | "We can compare {n} of your matches." |
| `m.progress.pattern` | §3.2 tier 2 | G+ · E I C | P | `TrendSmallMultiples` | Practice, partner, venue, camera confounds; never "caused by" | "Over {n} matches your {metric} has been {rising/steady/lower}. Many things change from match to match." |

### 2.12 Self-reported (asked, never inferred — D5, V2 §4.2)

| id | Plain label | Definition | Engine source | Depth · presets | Label | Component | Copy |
|---|---|---|---|---|---|---|---|
| `m.self.enjoyment` | How was it? | Optional 1-of-5 faces after a match; skippable | `new` (G-01) | Q+ · all | A | `ReflectionPrompt` | "How was this one? (skip any time)" |
| `m.self.energy` | Energy | Optional "easy / ok / tough" | `new` | G+ · E I C | A | `ReflectionPrompt` | "How did it feel physically?" |
| `m.self.recap_useful` | Recap feedback | "Was this recap useful?" yes/no | `new` | Q+ · all | A | `RecapFeedback` | "Was this useful?" |
| `m.self.checked_share` | (quality) | Share of shown claims a person Checked | `new` (internal) | — | — | telemetry only | — |

Self-report is the **only** source for enjoyment, energy and confidence. Nothing is inferred from posture, celebration or facial expression.

### 2.13 Doubles and pair (**Not yet** — `PlayerId` generalisation, G-03)

| id | Plain label | Definition | Gate | Component (when built) | Copy rule |
|---|---|---|---|---|---|
| `m.pair.shared_rally_count` | Rallies you both played | Rallies where both partners have ≥ 1 contact | G-03 | `PairMemoryCard` | "Both of you were in {n} rallies." |
| `m.pair.joint_participation_rate` | Both in the rally | Shared rallies / pair rallies | G-03 | `PairMemoryCard` | counts with denominator |
| `m.pair.partner_support_event` | A save for your partner | Sequence: partner out of position (rear/corner) then the other returns | G-03 + position validity | `MomentCard` (Partner moment) | "A great cover — you reached it for {name}." (event, not intent; never blame) |
| `m.pair.coordinated_attack_event` | A good attack combo | Rear-court attack followed by front-court interception, explicit pattern | G-03 + classification | `MomentCard` | Observation only |
| `m.pair.pair_pb` | Pair best | Best shared event under a stable definition for the pair | G-02, G-03 | `PersonalBestCard` | scoped to the pair |
| `m.pair.coverage_balance` | Court shared | Presence split across the pair's half | G-03 + G-09 | `CourtMap` | "No blame from aggregates" |

Doubles pages remain *designed but gated*: single-camera doubles has heavy occlusion; every pair event is confidence-rated and never a fact about who was responsible for a point (D17, V2 §5.5).

### 2.14 Activity (**Not yet — and never from video alone**)

| id | Plain label | Rule |
|---|---|---|
| `m.activity.sessions_per_week` | Matches this month | Count of matches the player added. A neutral count, no target, no streak (D7). **A** (derivable from the library) |
| `m.activity.active_play_trend` | Time in play across matches | Same as `m.pb.longest_session_play` series; Preview |
| `m.activity.calories` | — | **Never.** Cannot be derived from video |
| `m.activity.fitness`, `m.activity.recovery`, `m.activity.injury_risk` | — | **Never.** Out of scope (D10, V2 §1.5) |
| `m.activity.self_energy` | = `m.self.energy` | Self-reported only |

### 2.15 Data-quality metrics the *player* sees (coverage is a feature, D5/D10)

| id | Shows | Component |
|---|---|---|
| `m.quality.followed_rallies` | `m.session.rallies_followed` | `CoverageBar` |
| `m.quality.classified_shots` | `m.shot.classified_share` | `CoverageBar` (shots) |
| `m.quality.court_found` | `m.session.court_found` | `CoverageBar` (detail) |
| `m.quality.checked_claims` | "{k} of {n} things on this page you've checked" | `ReviewBanner` |
| `m.quality.not_counted` | `m.session.not_counted` | `ReviewBanner` |

**Count:** 9 (session) + 3 (moments) + 9 (shots) + 4 (rally) + 3 (placement) + 3 (presence) + 3 (distance) + 3 (serve) + 3 (pressure/story flags) + 5 (story) + 6 (PB/progress) + 4 (self) + 6 (pair) + 5 (activity) + 5 (quality) = **71 registry rows**, of which **about 50 can be player-facing today** (Available or Preview, at some depth); the rest are **Not yet**, internal, or telemetry. Of the 50, roughly 20 are **Available** (rally/session/self-report/quality) and 30 are **Preview** (shots, positions, history-dependent, score-dependent).

---

## 3. Comparison eligibility and minimum evidence

### 3.1 When are two matches *comparable*? (hard rules — all must hold)

| # | Rule | Why |
|---|---|---|
| E1 | Same **metric definition version** (`definition_version`) | A redefinition is a break, not a trend (V2 §8.4) |
| E2 | Same **match type**: Match (scored) ↔ Match; Social game ↔ Social game; Practice ↔ Practice (D12) | Rally structure differs |
| E3 | Same **discipline**: singles ↔ singles (doubles ↔ doubles when built) | Court size and contact patterns differ |
| E4 | **Identity**: the player is the same person in both (Checked via `PickYourself`, G-01) | Track ≠ person |
| E5 | **Camera class** matches for spatial metrics (`presence`, `zone_coverage`, `opponent_met_map`): same *view class* (behind-baseline-high / behind-baseline-low / side-on) and `calibration.quality.precision` ≥ gate in both | Perspective changes spatial error |
| E6 | **Coverage**: ≥ 80 % of detected rallies followed in both; court valid ≥ 80 % of frames for spatial metrics | A match we saw half of is not comparable with one we saw fully |
| E7 | **Sample**: each match meets the metric's minimum (§3.3) | Noise |
| E8 | **Classifier version** equal for shot-level metrics | The classifier is the instrument |
| E9 | **No unresolved data-quality flag** that could reverse the sign (e.g. `degraded` event for the shuttle stage, un-Checked winner for a score-dependent metric) | Honesty |
| E10 | Not separated by a **model/rule break** (`provenance` version change) unless the older match is re-analysed (`/reanalyse`) | Version breaks drawn in charts |

If any rule fails the UI says **"Not directly comparable"** and gives the *first failed rule in plain words* ("Different camera angle", "Last match was a social game") with an action ("Compare with {other match}", "Start a fresh baseline").

### 3.2 Tiers of change language (D6, FE §7.11)

| Tier | Condition | Allowed words | Forbidden |
|---|---|---|---|
| **0 — This match** | one match | descriptive: "had", "kept", "spotted" | any trend or improvement word |
| **1 — Since last time** | 2 comparable matches, change ≥ the metric's **smallest meaningful change** (SMC, below) | "higher than", "lower than", "early signal" + n | "improved", "better", "worse" |
| **2 — Pattern** | ≥ 4 comparable matches over ≥ 3 weeks; direction holds in ≥ 3 of the last 4 pairs; **unit = match-level value** (rallies cluster inside matches) | "has been rising / steady / lower over {n} matches" | "because of", "caused by", "mastered", "you are improving" without the n |
| **After a break (> 6 weeks)** | gap since last comparable match | "Start a fresh baseline?" — never a regression alarm | "You've dropped off" |

**Smallest meaningful change (SMC) — starting values to validate in research (X-series experiments, file 12):**

| Metric | SMC |
|---|---|
| `m.session.longest_rally` | ≥ 3 shots |
| `m.session.avg_rally` (median) | ≥ 1 shot |
| `m.rally.long_share` | ≥ 10 percentage points |
| `m.rally.kept_alive` | ≥ 7 percentage points, with `n ≥ 40` in both |
| `m.court.zone_coverage` | ≥ 2 zones |
| `m.shot.repertoire` | ≥ 1 new type (with first-seen rules) |

### 3.3 Minimum evidence (floor below which the metric is **Not enough to say**)

| Metric class | Floor |
|---|---|
| Counts of rallies/duration | ≥ 3 official rallies (single match); ≥ 8 for distributions |
| Longest/personal-best claims | ≥ 5 rallies this match; PB wording needs ≥ 3 comparable prior matches, else "longest so far" |
| Rates | denominator ≥ **20** eligible contacts (`kept_alive`) or ≥ **8** eligible opportunities (`vs_attack`); always print numerator and denominator |
| Shot mix / repertoire | ≥ 10 classified contacts (repertoire), ≥ 15 (mix), and `classified_share` ≥ 50 % |
| Spatial maps | ≥ 200 valid foot samples (`presence`), ≥ 25 shots (`opponent_met_map`), court valid ≥ 80 % |
| Firsts | History coverage ≥ 3 prior matches **or** explicit "first on record"; headline needs *Checked* or a player confirmation |
| Progress delta | Tier 1 needs both matches ≥ floor and E1–E10 |
| Pattern | Tier 2 needs ≥ 4 comparable matches |
| Tactical tendency (Advanced) | ≥ 30 relevant events; "in the rallies we observed" wording |

### 3.4 What each state looks like (never a blank chart, never a zero)

| `state` | Rendering | Component |
|---|---|---|
| `available` | Normal | — |
| `preview` | Normal + `PreviewTag` with one-line reason on tap | `PreviewTag` |
| `not_yet` | Hidden, or a single quiet line "Not available yet" in Deep dive | `EmptyState` |
| `insufficient` | "Not enough to say yet — {n} of {floor} needed" and the clips we do have | `NotEnoughToSay` |
| `not_comparable` | "Not directly comparable — {first failed rule}" + action | `ComparabilityNote` |
| missing coverage | Hatched gap with `CoverageBar` explanation | `CoverageBar` |

---

## 4. The insight system

### 4.1 Insight types

| Type | Purpose | Example (illustrative) | May use evidence of |
|---|---|---|---|
| **Observation** | Bounded fact about this match | "The longest rally was 14 shots." | Looks right or better |
| **Comparison** | Change vs a comparable baseline | "That's longer than your last similar match (11)." | Tier 1/2, E1–E10 |
| **Milestone** | PB/first | "Your longest rally so far." | Checked or Looks right + history rule |
| **Opportunity** (hypothesis) | A pattern worth looking at — never a diagnosis | "Several long rallies ended after a short return to the middle. Worth a look?" | ≥ 2 independent examples, ≥ Looks right on position/shot data |
| **Suggestion** | An optional experiment | "If you'd like something to try next time: …" | Only if a *Focus* is accepted or the preset is Improve; evidence-linked or labelled "general guidance" |
| **Coverage note** | What we could not see | "We followed 22 of 24 rallies." | Always allowed |
| **Question** | Ask instead of assert | "Was that a cross-court net shot?" | Used when a claim fails a hard gate but is probably interesting |

### 4.2 `InsightCard` contract (extends FE §8.1 and V2 §7.2)

```json
{
  "insight_id": "…",
  "claim": "You kept this rally going for 14 shots.",
  "claim_type": "observation | comparison | milestone | opportunity | suggestion | coverage | question",
  "metric_id": "m.session.longest_rally",
  "metric_definition_version": 1,
  "evidence_refs": [{ "event_id": "…", "frames": [3120, 3780] }],
  "coverage": { "rallies_followed": 22, "rallies_total": 24 },
  "sample_size": 22,
  "reliability_state": "checked | looks_right | worth_a_look",
  "limitations": ["Shots are detected contacts."],
  "comparison_context": { "baseline": "your_last_comparable", "n_matches": 3, "eligible": true },
  "alternatives": ["Fewer long rallies this match", "A different opponent"],
  "next_action": { "kind": "watch | save | focus | question | none", "label": "Watch this" },
  "visibility": "private | shared_named | approved_public",
  "purpose_tags": ["keep_moments", "understand"],
  "response": null,
  "generated_at": "ISO-8601",
  "model_version": "narration_v1 | template_only"
}
```

If any required field cannot be filled (metric id, evidence, reliability), the card is **withheld, weakened to a Question, or replaced by `NotEnoughToSay`**. A card may never carry a number that is not in its metric's `MetricValue`.

**Anatomy (file 07 `InsightCard`):** type tag → headline claim → one-line evidence ("22 rallies") → thumbnails (play) → `CheckChip` → optional "Why it may matter / What else could explain it" (conditional wording) → action row *Watch this · That seems right · Fix this · Not useful · Save*.

### 4.3 Ranking algorithm

**Step 1 — hard gates (eligibility).** A candidate that fails any gate never competes:

| Gate | Rule |
|---|---|
| G1 Evidence | Its `check` ≥ minimum for its claim type: observation/comparison ≥ *Looks right*; milestone ≥ *Looks right* **and** history rule (or *Checked*); opportunity ≥ *Looks right* with ≥ 2 independent examples; *Worth a look* items may only become **Questions** |
| G2 Minimum sample | §3.3 floors |
| G3 Comparability | §3.1 for any comparison/milestone/pattern |
| G4 Consent / visibility | No clip or name beyond its `visibility` |
| G5 Not contradicted | No counterexample hidden (a metric that has a stronger opposing value in the same match is shown together or not at all) |
| G6 Purpose floor | Relevance R ≥ 0.2 for the active purposes (a "Just play" match shows no insights at all) |

**Step 2 — score.**

```
S = R × E × ( 0.40·A + 0.35·N + 0.25·L ) × (1 − C)
```

| Term | Range | Meaning | How computed |
|---|---|---|---|
| **R** purpose relevance | 0–1 | Fit to the player's chosen purposes (D2). Keep-the-moments: Moment/milestone claims 0.9, factual 0.5, opportunity 0.1. Understand: factual/comparison 0.8, opportunity 0.7. Practise: opportunity/suggestion 0.9. Compete: tactical 0.9. Multiple purposes: max | rule table |
| **E** evidence factor | 0–1 | `Checked` 1.0 · `Looks right` 0.85 · `Worth a look` 0.5 (Question only) × coverage factor (followed fraction, floor 0.7) × sample factor (min(1, n / 2·floor)) | formula |
| **A** actionability | 0–1 | Is there a feasible action or good reason to inspect? Watch-only 0.2; save/share 0.4; question 0.4; focus/experiment 0.8 | rule |
| **N** novelty vs baseline | 0–1 | New relative to this player's history (first, PB 0.9; repeated fact 0.2; unchanged 0.1) | history |
| **L** salience | 0–1 | Magnitude relative to the SMC of the metric (§3.2), capped at 1 | formula |
| **C** emotional-cost risk | 0–1 | Framing risk of the claim: neutral/positive 0; first appearance of a deficit/opportunity 0.35; deficit repeated after a loss 0.5; any claim comparing the player unfavourably with others 1.0 (blocked); after a loss in a scored match opportunities are demoted below strengths unless the player chose *Choose something to practise* | rule |

**Step 3 — budget by depth and preset.** Quick/Relax: **1 hero + ≤ 3 facts + ≤ 1 question**; Guided/Explore: hero + 3 facts + ≤ 1 opportunity + ≤ 1 suggestion; Improve: hero + 1 strength + 1 opportunity (≤ 1) + 1 optional Focus; Compete/Advanced: no budget — the Deep dive lists all passing gates with filters. A *strength* (positive, verified) is always placed before an *opportunity* (D6, FE §7.8). If no opportunity passes the gates, the card is simply absent (FE §7.8 "never invent criticism").

**Step 4 — ties and diversity.** Break ties by (a) claim type diversity (don't show three observations), (b) evidence age (newest), (c) lower C. No more than one card per `metric_id`.

### 4.4 Worked example (illustrative — invented numbers)

Alex played a social game (unscored) against Sam. Purposes: *Keep the moments* + *Understand my game*. History: 3 prior comparable social games.

| Candidate | Claim type | R | `check` → E | A | N | L | C | Gate result |
|---|---|---|---|---|---|---|---|---|
| **a.** Longest rally 14 shots, previous best 11 (`m.session.longest_rally`, `m.pb.longest_rally`) | milestone | 0.9 | Looks right 0.85 × coverage 1.0 (22/24 → 0.92) × sample 1.0 → **0.78** | 0.2 | 0.9 | 0.9 | 0 | pass |
| **b.** 41 of 47 of Alex's shots kept the rally going (`m.rally.kept_alive`) | observation | 0.6 | Worth a look (Preview) → blocked as a headline; as an observation needs *Looks right* → fail G1 | — | — | — | — | **fails G1** → demoted to Deep dive |
| **c.** "Short returns to the middle ended 4 of 9 long rallies" | opportunity | 0.1 (Keep moments) / 0.7 (Understand) → **0.7** | Worth a look 0.5 | 0.8 | 0.6 | 0.6 | 0.35 | **fails G1** (an opportunity needs ≥ *Looks right* and ≥ 2 independent examples with reliable position data) → not shown; listed under *Not enough to say* in Deep dive |
| **d.** First cross-court net shot spotted (`m.shot.first_seen`) | question | 0.7 | Worth a look → 0.5 × 0.92 × 1.0 → **0.46** | 0.4 | 0.9 | 0.6 | 0 | converted to **Question** (hard gate for "first") |
| **e.** Court coverage up vs last match | comparison | 0.8 | — | — | — | — | — | **fails G3** (different camera class, E5) → `ComparabilityNote` only |

Scores (S = R·E·(0.40A+0.35N+0.25L)·(1−C)):

- **a:** inner = 0.40·0.2 + 0.35·0.9 + 0.25·0.9 = 0.08 + 0.315 + 0.225 = **0.62** → S = 0.9 × 0.78 × 0.62 × 1 = **0.435**
- **d:** inner = 0.40·0.4 + 0.35·0.9 + 0.25·0.6 = 0.16 + 0.315 + 0.15 = **0.625** → S = 0.7 × 0.46 × 0.625 × 1 = **0.201**

Result (Relax/Quick budget): **Hero** = *a* ("A new personal best: your longest rally yet — 14 shots"), **Question** = *d* ("Was that a cross-court net shot? Yes / No"), facts = three descriptive facts from §2.1 (rallies, shuttle-in-play, longest). *b* and *c* are held for Deep dive / Review; *e* shows "Not directly comparable — different camera angle".

### 4.5 Suppression rules (nothing is shown if…)

1. Evidence gate fails (G1) — the claim becomes a Question or is dropped.
2. Coverage < 70 % followed rallies → no claim above the *Observation* tier; recap leads with the **coverage note**.
3. The only supporting events are `provisional/uncertain` or `retracted`.
4. Two metrics point opposite ways and only one is shown (counterexample concealment).
5. The claim would compare the player with another named person (never, D6/D8).
6. Preset *Relax/Just play* and the player has not asked for analysis.
7. The same claim was dismissed ("Not useful") in this or the last two comparable matches.
8. The score is not Checked and the claim depends on it (pressure, comeback, win-rate).
9. After a loss in a **scored** match, opportunities are demoted below strengths unless the player chose *Choose something to practise* (FE §3.4).

### 4.6 `NotEnoughToSay` — when and how

| Situation | Copy (file 09 owns final wording) | Offers |
|---|---|---|
| Below §3.3 floor | "There aren't enough {things} here yet to say anything reliable — {n} of {floor}." | Watch the clips we have · Add another match |
| Coverage low | "We could only follow {k} of {N} rallies, so we're keeping this short." | Why? · Re-place your court · Record tips |
| Shots unclassified | "We couldn't name most of the shots in this video, so the shot breakdown is left out." | See which · Fix this |
| No comparable match | "Not directly comparable — {reason}." | Compare another · Start a fresh baseline |
| No opportunity found | "Nothing stands out as something to work on here." | Keep the moments · Explore |
| No moment for a player | "We couldn't find a moment for {name} we're confident about — {reason}." | Pick one yourself |

`NotEnoughToSay` is **never red**, never an apology, never blames the footage or the player; it states the limit and offers the next step.

---

## 5. Metric → screen map (quick lookup)

| Screen (file 00 route) | Metrics shown (by depth) |
|---|---|
| **Recap — Moments** | `m.moment.*`, `m.pb.longest_rally`, `m.shot.first_seen` (as a question) |
| **Recap — My game** | `m.session.rally_count`, `active_play_s`, `longest_rally`, `m.court.presence_map` (G+), `m.session.rally_length_dist` (G+), `m.progress.delta` (G+, if eligible), coverage |
| **Recap — Together** | `m.pair.*` (Not yet) — until then: shared Moments only |
| **Deep dive → Story** | `m.story.*`, `m.pressure.*`, `HeadToHead` (Compete) |
| **Deep dive → Rallies** | rally list, `m.session.not_counted`, `m.rally.*` |
| **Deep dive → Shots** | `m.shot.*`, `m.serve.*` |
| **Deep dive → Court** | `m.court.*`, `m.place.opponent_met_map` |
| **Deep dive → Compare** | `m.progress.*`, eligibility (§3) |
| **Progress / Records / Shots / My story** | `m.progress.*`, `m.pb.*`, `m.shot.repertoire`, `m.shot.first_seen`, `m.activity.sessions_per_week` |

---

## 6. Definition of done for any metric or insight (from Amateur v2 §16)

A metric or insight ships to players only when every applicable box is true:

- [ ] The player's purpose makes it relevant (or it is a coverage/limits note).
- [ ] Event and player identity are reliable enough for the claim (§1.4, G1).
- [ ] It has a versioned definition with numerator, denominator and exclusions (§1.2).
- [ ] Its evidence opens in one tap ("Watch this") and its definition one tap further (`MetricPopover`).
- [ ] Coverage and uncertainty are visible in plain words (`CoverageBar`, `CheckChip`).
- [ ] Wording describes the observation before any interpretation; no causal claim (§10.4).
- [ ] Any recommendation is optional and feasible; any comparison passes E1–E10 (§3.1).
- [ ] Privacy/visibility allows this display and sharing scope.
- [ ] The player can fix, dismiss, hide or ask about it (`FixSheet`, "Not useful").
- [ ] A fix visibly updates every dependent number and says what changed (G-14).
- [ ] Empty, insufficient, not-comparable, partial and failed states are designed (§3.4).
- [ ] It has a user-value hypothesis, a harm test and a kill criterion (file 12).

---

## 6a. Reading the numbering

§7 (Moments), §8 (reports), §9 (Coach chat) and §10 (narration) keep the numbers that files 00 and 02 cite.

---

## 7. The Moment (highlight) system, rebuilt for amateurs (D4, D6, D17)

### 7.1 Critique of today's ranker (`analytics/match.py: score_rally`, `highlights`)

| # | What the code does | Why it fails for amateurs |
|---|---|---|
| H-1 | `highlights(player=…)` keeps `r.winner == player`; `Highlight.player = r.winner` | **The loser gets no highlights** — violates D17 and the "every player matters" rule |
| H-2 | Score = Σ reasons (length ≤ 3, variety ≤ 1.5, smash_winner 1.5, jump_smash 1.2, defence ≤ 1.5, net_play ≤ 1.2, pressure 1.4/2.0, deuce 1.0, momentum 1.0, comeback 1.5), capped at 10 | Favours **competitive** structure (pressure, deuce, momentum) that is absent or fabricated in casual play |
| H-3 | `longest_rally` needs `n_shots ≥ max(12, longest)` and `== longest` | Threshold tuned on broadcast matches; typical amateur rallies are shorter, so the label never fires |
| H-4 | `best_defence` requires the **winner** and ≥ 4 `lift/defence`-family shots | A defender who lost the rally gets no credit; "defence" family includes `clear` (family `lift`) which is not necessarily defensive |
| H-5 | `smash_winner` and `jump_smash` add points | Rewards power; rule classifier is `probable` at best (R-2); jump smash relies on pose heuristics |
| H-6 | `pressure/deuce/momentum/comeback` use `flags_before` and the EWMA | Need a verified BWF score; on an unscored or mid-game clip they are **invented** (G-04) |
| H-7 | MMR diversity over *category sets* | Good idea (kept), but categories are the pro list above |
| H-8 | Output is a numeric 0–10 `score` shown in the UI and PDF | False precision (D5); invites comparison between moments |
| H-9 | No consent, no clip entity, no per-person credit | G-05, G-06 |
| H-10 | Ranking is per-match only | No novelty vs the player's history, so "first/PB" cannot be a lens (G-02) |

Keep from today: the **reasons decomposition** (explainability), **MMR diversity**, rally-level candidates, and the `evidence` links.

### 7.2 Moment lenses (what a Moment *is*)

A Moment is a clip (frame range) + a **lens** + **credited participants** + a one-line, evidence-grounded reason. Lenses replace categories.

| Lens (player's word) | Definition | Eligibility evidence | Credit | Label | Needs score? | Presets |
|---|---|---|---|---|---|---|
| **Longest** | A rally in the top 10 % by `n_shots` for this match **or** a personal best | Rally boundaries Looks right; ≥ 5 rallies | Shared (both participants) | A | No | R E I C |
| **Saved it** | The player made ≥ 4 defensive-family shots (`lift`, `block`, `push`) in a rally of ≥ 6 shots **and** the rally continued ≥ 3 more contacts — **regardless of who won** | Shot families ≥ *Worth a look*; shown with Preview | The defender (exclusive) | P | No | R E I C |
| **Net duel** | A rally containing a run of ≥ 4 consecutive `net`-family shots | Same | Shared | P | No | E I C |
| **Best variety** | Rally in which one player used ≥ 4 distinct stroke types | Same | That player (exclusive) | P | No | E I C |
| **Close finish** | A game that ended within 2 points or at deuce; the deciding rally | Verified (Checked) score | Shared | P | **Yes** | I C (E when scored & Checked) |
| **Comeback** | Winner trailed ≥ 5 then levelled/led | Verified score | The comeback side (credited neutrally: "a swing back") | P | **Yes** | I C |
| **First** | First spotted occurrence of a shot type in the player's history | History + Checked or player confirm | That player | P | No | E I C |
| **Personal best** | New PB under §2.11 | History rule | That player | P | No | R E I C |
| **Fun (approved)** | Player-approved lucky/funny clip; a *blooper only* with explicit approval (D15) | **Only** player approval; never auto-labelled | The approver | A | No | R E I C |
| **Partner moment** | A shared rally or save in doubles | G-03 | Both | **N** | No | — |
| **Your pick** | Anything the player chooses from the rally list or timeline | n/a | The picker | A | No | all |

`jump_smash` and `smash_winner` are **not lenses**. A smash may appear *inside* a Moment's description ("the rally ended with your smash") only when *Looks right* — it never earns a Moment by itself (H-5).

### 7.3 Lens strength `s ∈ [0,1]` (internal; never shown)

| Lens | Formula | Notes |
|---|---|---|
| Longest | `percentile_rank(n_shots)` among the player's last ≤ 30 comparable rallies (this match if fewer); `+0.10` (cap 1) if a new PB | Percentiles remove the pro-threshold problem (H-3) |
| Saved it | `min(1, defensive_shots / 6)` | Credit independent of rally result |
| Net duel | `min(1, longest_net_run / 6)` | |
| Best variety | `min(1, distinct_types / 6)` | |
| Close finish | `1 − min(1, final_margin / 3)`; +0.15 if deuce (cap 1) | Scored + Checked only |
| Comeback | `min(1, max_deficit / 8)` | Scored + Checked only |
| First | 1.0 if confirmed; else 0.6 (asked as a Question) | |
| Personal best | `min(1, relative_gain)` where gain = (new − old)/max(old,1) | |

**Reliability weighting.** Effective strength `s* = s × w`, `w` = 1.0 *Checked* · 0.9 *Looks right* · 0.75 *Worth a look* (shot-based lenses are always ≤ 0.75 until Checked).

### 7.4 Selection algorithm (fair by construction)

1. **Build candidates** from official rallies; compute each lens `s*`; drop lenses failing eligibility or consent (G4).
2. **Hero:** highest `s*`; ties → prefer the candidate that credits more participants.
3. **Fairness pass.** For every participant, if any eligible Moment exists where they are credited **exclusively or shared**, ensure ≥ 1 selected Moment credits them. If a participant would otherwise only be credited by a *shared* Moment, that is sufficient (D17). If *no* eligible Moment credits them, record an **honest why-not** (`m.moment.per_player`), never a fabricated clip.
4. **Fill remaining slots** by Maximal Marginal Relevance over lenses:
   `pick = argmax [ (1 − d)·s* − d·overlap ]`, `d = 0.35` (today's default `diversity`), `overlap = Jaccard(lens set, chosen lens sets)` (0 or 1 here).
5. **Per-participant exclusive guarantee when slots are scarce** (≤ 2 non-hero slots, e.g. Quick on a phone): prefer one exclusive Moment per participant over a shared one.
6. **Consent filter last:** private by default; a funny clip never leaves the owner without approval; clips containing a non-consenting participant are suppressed from shareable outputs (V2 §5.1).
7. **Explain** each Moment with the top reason from the lens (kept from today's `reasons`), in words, never a score.

### 7.5 Worked example (illustrative — invented numbers)

A 24-rally social game, Alex vs Sam, unscored (so no Close finish/Comeback). Rally shots → lens strengths (before weighting), credits and reliability:

| Cand. | Rally | Lens | Facts | `s` | Reliability `w` | `s*` | Credit |
|---|---|---|---|---|---|---|---|
| c1 | #12 | Longest | 14 shots; new PB (prev 11); percentile 0.92 + 0.10 | **1.00** (cap) | Looks right 0.9 | **0.90** | Alex + Sam (shared) |
| c5 | #9 | Longest | 11 shots; percentile 0.85 | 0.85 | 0.9 | **0.77** | Shared |
| c2 | #7 | Saved it | Alex: 5 defensive shots, 9-shot rally, continued 4 more | 5/6 = 0.83 | Worth a look 0.75 | **0.62** | Alex (excl.) — *he lost the rally* |
| c3 | #15 | Net duel | 5-shot net run | 5/6 = 0.83 | 0.75 | **0.62** | Shared |
| c4 | #3 | Best variety | Sam used 4 types | 4/6 = 0.67 | 0.75 | **0.50** | Sam (excl.) |

**Hero:** c1 (0.90). Fairness: shared c1 already credits both players ✓.
**Fill (3 slots, d = 0.35):** chosen lens set so far = {Longest}.

| Cand. | `(1 − 0.35)·s*` | `− 0.35·overlap` | MMR |
|---|---|---|---|
| c5 (Longest) | 0.65 × 0.77 = 0.50 | − 0.35 × 1 | **0.15** |
| c2 (Saved it) | 0.65 × 0.62 = 0.40 | − 0 | **0.40** |
| c3 (Net duel) | 0.65 × 0.62 = 0.40 | − 0 | **0.40** |
| c4 (Variety) | 0.65 × 0.50 = 0.325 | − 0 | **0.33** |

With 3 free slots the picks are **c2, c3, c4** (c5 is the same lens as the hero and drops out). Final order for a *Guided* recap: **c1 Longest · c2 Saved it (Alex) · c3 Net duel · c4 Best variety (Sam).**

**If only 2 non-hero slots exist (Quick on a phone):** step 5 applies — each player gets an *exclusive* Moment before a shared one: c2 (Alex) and c4 (Sam) are chosen, **c3 (shared, 0.40 > 0.33) is dropped** even though it scored higher than c4. Result: **c1, c2, c4.** This is the fairness override working as designed.

**Honest why-not example:** if Sam had no eligible exclusive Moment and only c1 credited him, the recap says "Here's a moment you both made" (shared credit is a genuine positive moment), and the **Together** panel notes: "We couldn't find a solo moment for Sam we're sure about — pick one yourself." No fabricated clip.

### 7.6 Moment object and consent (new; G-06)

```json
{
  "moment_id": "…", "match_id": "…", "rally_event_id": "…",
  "frames": [3120, 3780], "lens": "saved_it",
  "credited": [{ "player": "alex", "exclusive": true }],
  "reason_text": "You kept this alive through 5 defensive shots.",
  "evidence_ids": ["…"], "check": "worth_a_look",
  "visibility": "private | shared_named | public_link",
  "approval": { "required": false, "approved_by": [], "approved_at": null },
  "favourite": false, "audio": "kept | stripped"
}
```

Rules: Fun/funny Moments `approval.required = true`; sharing never changes analysis/training consent (D15); a `public_link` needs every credited participant's approval; audio defaults to **stripped** for shared clips (file 02 G-28).

---

## 8. Report redesign: from analyst PDF to "Match story"

### 8.1 What exists (file 02 §3.6) and what changes

| Today | Audience | Production role |
|---|---|---|
| `report.pdf`: players table (10 rows incl. distance), highlights table with a 0–10 score, every rally with winner/outcome/score | Analyst | **Advanced export "Analyst report"**. Changes: remove distance and numeric highlight score; add coverage + Preview legend; replace "Winner" column with "Winner (checked / auto)" |
| `rallies.csv`, `events.jsonl`, `summary.json` | Analyst/data | Advanced exports and **data portability** under Settings → Data (G-05) |
| `legacy.csv` | Old Streamlit | Drop from the player UI |
| `clip.mp4` | Anyone | **Moment file** — add consent check, audio strip option, optional end-card |

### 8.2 New default: Match story

| Deliverable | Format | Contents (top to bottom) | Rules |
|---|---|---|---|
| **Match story card** (share image) | 1080 × 1350 PNG (WhatsApp/Instagram portrait) + 1080 × 1080 | Hero Moment thumbnail with play badge → one line ("14-shot rally — your longest yet") → three facts (`FactTrio`: rallies, shuttle in play, longest) → date + match type → small footer "Auto-detected · Preview" | Name = **nickname** by default; no score for unscored matches; no opponent name unless approved; no `%`; no distance; one accent colour = *you* |
| **Match story PDF** | A4 portrait, 1–2 pages | p1: Moments strip (3), My game (facts, one court map, one insight), Together (if any) · p2: What we could see (coverage), definitions (3 lines), "How to read this" · footer with Preview legend and QR/link back to the match | Same content as the Recap at **Guided** depth; every claim carries its `CheckChip` word; no numbers without denominators |
| **Moment share** | Short MP4 (≤ 20 s) + poster; optional "story end-card" with the lens and nickname | One Moment | Audio stripped by default; consent per participant; `SharePreviewDialog` before creation (file 05c) |
| **Analyst report (Advanced)** | A4 PDF (existing) | As today with the changes in §8.1 | Available only at Depth = Advanced |
| **Data export** | CSV/JSONL/JSON | As today | Settings → Data |

### 8.3 Match story content rules

1. Lead with a **Moment**, not a table (D4, V2 §6).
2. Maximum three facts and one insight (§4.3 Quick budget).
3. No red/green, no trophies, no rank, no "winner" language (D6, D7).
4. Every number prints its unit and, for rates, numerator and denominator.
5. A single coverage line is always present ("We followed 22 of 24 rallies").
6. If the score is unverified, omit it from the card; show it in the PDF with *Preview*.
7. Text is generated by the **narration contract** (§10) or by fixed templates — never free-form.

---

## 9. Coach chat — the Ask agent for amateurs

The existing `AskTab`/agent (grounded tools, `[[ev:ID]]` citations, validator, abstention) stays. Surface and prompts change (D2, D6, D16).

### 9.1 Tools by depth (allowlist)

| Tool (today) | Quick/Relax | Guided | Advanced/Compete | Note |
|---|---|---|---|---|
| `match_overview` | ✓ | ✓ | ✓ | Always first; supplies coverage and `score_basis` |
| `list_rallies` | ✓ (no winner filter) | ✓ | ✓ (+ winner) | Add participant filter (G-25) |
| `get_rally` | ✓ | ✓ | ✓ | |
| `find_strokes` | — | ✓ (Preview wording) | ✓ | |
| `top_highlights` | → replaced by `top_moments` (lenses, fairness) | ✓ | ✓ | G-18 |
| `player_stats` | — | limited fields | ✓ | Win-centric |
| `momentum` | — | — | ✓ | |
| `rules_and_background` | ✓ | ✓ | ✓ | Rules/terms only; never match facts |

### 9.2 Suggested questions by preset (chips)

| Preset | Starter chips (≤ 4) |
|---|---|
| **Relax** | "Show me my best rally" · "What was the longest rally?" · "Find a rally where I saved a tough shot" · "Which shots did I use?" *(Preview)* |
| **Explore** | "What new shots did I try?" *(Preview)* · "How long were my rallies compared with last time?" · "Where did I spend most time on court?" *(Preview)* · "What happened in the rally at 12:40?" |
| **Improve** | "Which rallies were close calls I could learn from?" · "When did I get pulled out of position?" *(Preview)* · "What's one thing worth trying next time?" *(evidence-linked or labelled general)* · "Show me examples of my best defence" |
| **Compete** | "List rallies of 10+ shots" · "Show every rally that ended at the net" · "What did my opponent do most after my drop?" *(Preview)* · "Compare game 1 and game 2 rally lengths" |

Replace today's chips ("How did X win most of their points?", "What should X change in the next game?") — win-centric and prescriptive (file 02 V-6).

### 9.3 Answer style

| Aspect | Rule |
|---|---|
| Shape | **Headline sentence** (the answer) → ≤ 3 bullets (evidence) → **one limits line** → optional next action. ≤ 120 words |
| Voice | Warm, plain; second person "you" for the signed-in player; never trait language (file 09) |
| Evidence | Every match fact has a citation chip that opens the exact frame range ("Watch this"); chips show a number, not an id |
| Numbers | Only numbers present in tool output (existing validator); rates with n of N |
| Uncertainty | If any cited item is *Worth a look*, say so in the limits line; never in the headline |
| Comparison | Only against the player's own comparable history; others only if the player opts in |
| Abstain | Allowed and preferred to guessing; uses `NotEnoughToSay` copy |
| Length of history | Last 5 turns (as today) |
| Offline provider | If no LLM is configured, answers are **template-based from tool output** with the same chips (no `.env` language in the UI) |

### 9.4 Refuse / abstain / redirect rules

| User asks | Response |
|---|---|
| "Why did I lose?" | Present candidate observations (rally lengths, how rallies ended) and ask a question; no single cause (FE §9.4 attribution table) |
| "Am I good?" / "What level am I?" | Declines to grade; offers personal bests and comparable-match change; no universal rating (V2 §1.4) |
| "What should I train? / drills / how many reps" | If a Focus exists or preset = Improve: offers one editable experiment linked to evidence; otherwise "general guidance" clearly labelled; **no training load, no medical, no injury advice** |
| "Am I tired / out of shape / will I get injured?" | Declines; self-reported energy only; suggests warm-up education page, not diagnosis |
| "How many calories / km did I run?" | "We can't measure that reliably from video." |
| "Was my partner worse than me?" / "Who's to blame?" | Declines blame; offers shared Moments and pair coverage when available |
| "Compare me with {named person} / pros" | Only if the player has enabled peer/expert comparison (D6); else declines |
| "What was my opponent thinking / were they angry?" | Declines (no emotional inference) |
| "Delete / share this clip" | Routes to the proper dialog (`SharePreviewDialog`/`DeleteConfirmDialog`); the agent has no write tools |
| Rules/terms question | Answers from `rules_and_background` (background only) |
| Anything needing events not in tool output | "I can't see that in this match's data." |

### 9.5 Prompt guardrails (system-side, not shown)

Strict tools; evidence-only numbers; no scoring authority; refuse list above; banned-phrase lint (file 09); output must include `claim_type` per paragraph (internal) so the UI can render `Observation` vs `Suggestion` blocks visibly distinct (FE §9.1 epistemic layers: measurement / classification / interpretation / recommendation).

---

## 10. Narration contract (aligned with Spec v1 doc 05 §8 and V2 §7.2)

### 10.1 Principle

> **The LLM explains validated evidence. It does not compute, decide, or decorate.** Deterministic services pick *what* to say; the narrator only chooses *how* to say it, within a template and a banned-phrase policy.

### 10.2 Evidence packet (the **only** input)

```json
{
  "player": { "display_label": "Alex", "pronoun_free": true },
  "tone": "direct | balanced | coach_guided",
  "purposes": ["keep_moments", "understand"],
  "depth": "quick | guided | advanced",
  "selected_insights": [ { "insight_id": "…", "claim_type": "milestone", "metric_id": "m.pb.longest_rally",
                            "value": 14, "unit": "shots", "baseline": { "value": 11, "n_matches": 3 },
                            "check": "looks_right", "evidence_ids": ["…"], "limitations": ["…"] } ],
  "coverage": { "rallies_followed": 22, "rallies_total": 24 },
  "allowed_claim_types": ["observation", "milestone", "question"],
  "prohibited": ["causal", "diagnosis", "emotion", "comparison_with_others", "streak", "grade"],
  "privacy": { "names_ok": ["Alex"], "partner_names_ok": false }
}
```

No raw video, no unverified model outputs, no other users' data, no free-text from the player except what they typed *this* turn.

### 10.3 The narrator **may**

- Summarise the selected, verified observations in plain words (≤ the depth's word budget).
- Explain a metric definition using the registry's text.
- Point to a clip ("Watch the recovery at the end.").
- Offer a gentle, optional next step *drawn from* `next_action`.
- Convert a failed-gate claim into a **question**.
- State limits and coverage.

### 10.4 The narrator **may not**

| Prohibited | Enforcement |
|---|---|
| Change a score, count, rate or date; round differently from the packet | **Number-grounding validator**: every numeral/ordinal must exist in the packet (extends today's `validate()` — DEF-04) |
| Invent an event, Moment, PB, first, partner, opponent or location | **ID check**: every cited `event_id`/`insight_id` must be in the packet; unknown ids rejected (DEF-13 repair pass retained) |
| Assert causality ("because of", "that's why you lost") or diagnosis | Banned-phrase + claim-type lint; only `claim_type` in `allowed_claim_types` |
| Infer emotion, confidence, fitness, injury, communication, intent | Lint list: *frustrated, angry, nervous, confident, tired, unfit, injured, lazy, clumsy, choked* … |
| Compare the player with others, rank, or label ("elite", "beginner") | Lint; comparison only if the packet includes an opted-in baseline |
| Use streak/guilt/pressure language ("don't lose", "you must") | Lint: *streak, must, should have, falling behind, don't break* |
| Present *Worth a look* items as fact | Template slot requires `check` ≥ *Looks right* for assertive verbs; otherwise "may", "looks like", or a question |
| Reveal partner/opponent names or private partner data | `privacy.names_ok` |
| Write about score-dependent claims when the score isn't Checked | `prohibited` includes `score_claims` in that case |

### 10.5 Output contract

```json
{
  "paragraphs": [
    { "text": "A new personal best — you kept one rally going for 14 shots. [[ev:01J…]]",
      "claim_type": "milestone",
      "insight_id": "…",
      "cited": ["01J…"] }
  ],
  "limits_line": "Shots are detected contacts; we followed 22 of 24 rallies.",
  "next_actions": [{ "kind": "watch", "ref": "01J…" }]
}
```

The UI renders the **deterministic value separately** from the narration (`FactTrio`/`MetricPopover` use `MetricValue`, never the LLM text) so a model error cannot alter a displayed metric.

### 10.6 Validation pipeline (every narration)

1. **Schema** — output parses; `claim_type` in the allowed list.
2. **Grounding** — numbers, ordinals, names ⊆ packet; citation ids ⊆ packet (existing validator extended).
3. **Policy lint** — banned phrases and tone word list (file 09).
4. **Check-level lint** — assertive wording only when `check` allows.
5. **Length/density** — per depth budget.
6. **Fallback** — on any failure: one repair attempt; then **template-only text** (`model_version: "template_only"`); log `harm_signal`/`narration_rejected` (no content, ids only).

### 10.7 Where narration is used / not used

| Surface | Narration |
|---|---|
| Recap `StoryParagraph`, Match story card/PDF line | LLM *or* template (default template at Relax/Quick) |
| `InsightCard` headline | **Template** (deterministic) — LLM may only add the optional "why it may matter" sentence |
| Coach chat | LLM within §9 |
| Moment captions | Template per lens |
| Errors, empty states, consent text | **Never** LLM — fixed copy (file 09) |

---

## 11. Open items handed to other files

| Item | Goes to |
|---|---|
| Exact copy for every template in §2 | 09 |
| `InsightCard`, `CoverageBar`, `CheckChip`, `PreviewTag`, `MomentCard` anatomy | 07 |
| Where each metric sits on each screen | 05a / 05b / 05c |
| New fields: `MetricValue`, Moment, history store, coverage API, participant-centric (`me`) aggregation | 11 (G-02, G-06, G-07, G-19, G-20, G-25) |
| SMC thresholds, Tier-2 rule, floors, lens parameters validation | 12 (experiments + validation set, G-11) |
| Calibrating bands so *Looks right* means something | 11 (G-08), 12 |
