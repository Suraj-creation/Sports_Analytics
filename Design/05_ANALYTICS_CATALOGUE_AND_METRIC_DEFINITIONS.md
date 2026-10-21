# 05 --- Analytics Catalogue and Metric Contracts

## 1. Metric governance

A metric is not ready for production merely because a model can emit a
number. Each metric must have: - Stable metric ID and display name. - A
plain-language definition. - A formula or deterministic computation
rule. - Required source events. - Inclusion/exclusion rules. - Minimum
sample requirements. - Confidence and coverage logic. - Calibration
assumptions. - Known failure modes. - Comparison eligibility rules. -
Evidence links. - Versioned implementation. - A user-facing
explanation. - A correction/reporting path.

## 2. Evidence levels

Recommended event status: - `verified`: passed defined validation
checks. - `estimated`: useful but relies on approximate measurement. -
`needs_review`: ambiguous identity, event, or outcome. - `rejected`:
failed validation. - `unavailable`: required source evidence does not
exist.

Never silently turn `estimated` or `needs_review` into a verified claim.

## 3. Core event families

### Session events

Session created, upload started, upload complete, processing stage
updated, processing failed, session completed.

### Match events

Match format, game/set, point, score state, server if known, point
outcome, score verification.

### Rally events

Rally start/end, shot count, duration, participants, outcome, key
moments.

### Shot events

Shot type, timestamp, player, side, court region, shuttle
trajectory/landing region, response, confidence.

### Movement events

Player position, court-zone presence, path segment, estimated
speed/distance only when calibrated, coverage and tracking confidence.

### Highlight events

Candidate moment, selection reason, clip range, participants,
verification status, share permissions.

### Social events

Favorite, player-approved celebration clip, pair memory, share action,
consent status. Do not infer private emotion or intent.

## 4. Highlight catalogue

Possible categories: - Best verified rally. - Longest verified rally. -
Best smash / drop / clear / drive / net shot. - Defensive recovery. -
Unexpected successful return. - Cross-court placement. - Rally-saving
shot. - Match-point save (only if score is verified). - Comeback
sequence (only if scoring data supports it). - Shot discovery. -
Personal-best rally. - Doubles teamwork. - Partner rescue. - Coordinated
attack. - Joint defence. - Approved celebration. - Approved funny
moment. - Favorite memory.

Highlight ranking should balance: - Evidence confidence. - Relevance to
the player's chosen goals. - Clip quality and complete context. -
Novelty relative to prior clips. - Variety across players and event
types. - Fairness across winners and losers. - Consent eligibility.

Do not rank only by explosive movement or winning shots; this can
systematically exclude defensive and beginner moments.

## 5. Metric catalogue

### A. Session summary

-   `session_duration`: recording duration or detected playable
    duration; specify which.
-   `active_rally_time`: sum of verified rally intervals; not the same
    as total exercise time.
-   `verified_rally_count`: count of rallies passing segmentation
    checks.
-   `verified_point_count`: count of points with reliable outcome.
-   `scoreline`: only if scoring and game boundaries are sufficiently
    verified.
-   `processing_coverage`: percentage of video/time for which required
    tracking and analysis were available, with method documented.

### B. Rally metrics

-   `rally_shot_count`: number of classifiable shot/contact events in a
    verified rally.
-   `rally_duration`: end timestamp minus start timestamp under a
    defined boundary rule.
-   `long_rally_count`: number of rallies meeting a configurable shot
    threshold.
-   `rally_length_distribution`: distribution of verified rally shot
    counts.
-   `player_rally_participation`: rallies in which a player was observed
    participating, not a rating of contribution quality.
-   `rally_outcome_rate`: outcomes per valid opportunity; must define
    whether denominator is points, rallies, or shots.

### C. Shot metrics

-   `observed_shot_repertoire`: unique shot types detected with
    sufficient confidence.
-   `shot_count_by_type`: classifiable events by shot category.
-   `shot_type_share`: shot-type count divided by all classifiable shot
    events; show the denominator.
-   `valid_return_rate`: successful observed returns divided by
    classifiable eligible return attempts; never use when
    eligibility/outcome is uncertain.
-   `placement_distribution`: verified landing/target regions by court
    zone.
-   `shot_sequence_frequency`: observed consecutive shot-type pairs or
    short sequences.
-   `shot_outcome_association`: descriptive association only; do not
    claim causal effectiveness without a suitable design.

### D. Movement metrics

-   `court_zone_coverage`: distinct or weighted zones visited during
    valid tracking intervals.
-   `movement_path`: observed path under calibrated court mapping and
    validated tracking.
-   `estimated_distance`: only if perspective calibration and scale
    conversion are validated.
-   `estimated_speed`: only if time synchronization, scale, and tracking
    accuracy are validated.
-   `movement_intensity_proxy`: explicitly label as a video-derived
    proxy, not physiological intensity.
-   `active_rally_duration`: not equivalent to calories, cardiovascular
    load, or total exercise duration.

### E. Personal progress

-   `personal_best_rally`: longest verified rally under a consistent
    event definition.
-   `personal_best_shot_count`: maximum valid count for a specified shot
    type, if meaningful.
-   `new_shot_observed`: first verified observation of a shot category
    in the player's available history.
-   `session_to_session_change`: difference or relative change between
    comparable sessions, with baseline and sample sizes.
-   `trend_confidence`: confidence that the observed difference is
    interpretable given data coverage and comparability.

### F. Doubles and partnership

-   `pair_rally_count`: verified rallies involving the pair.
-   `joint_participation_rate`: rallies in which both partners have
    verified contributions, with clear event definition.
-   `partner_support_event`: a validated sequence in which a partner
    returns play after a difficult position; label as event, not intent.
-   `coordinated_attack_event`: verified sequence satisfying an explicit
    tactical pattern definition.
-   `pair_personal_best`: best verified pair event under a stable
    definition.
-   `pair_comparison`: only across comparable partners, format, sample,
    and recording conditions.

### G. Optional activity summaries

-   `detected_playing_time`: time in detected play segments.
-   `session_frequency`: number of recorded sessions in a chosen window.
-   `participation_streak`: avoid as default; if present, make optional
    and never shame absence.
-   `self_reported_energy`: explicitly player-provided, not inferred
    from video.
-   `self_reported_enjoyment`: explicitly player-provided.

## 6. Comparison eligibility

Only compare sessions when the relevant conditions are sufficiently
similar: - Same metric definition/version. - Sufficient event count. -
Comparable singles/doubles format. - Similar camera setup and
calibration for spatial metrics. - Similar recording coverage. -
Reliable player identity. - Relevant filters and score context. - No
unresolved data-quality issue that would reverse the interpretation.

If conditions fail, say "Not directly comparable" and explain why.

## 7. Confidence and coverage UX

Confidence is not a universal percentage unless it is calibrated and
interpretable. Prefer a categorical state with a tooltip: - Verified:
passed the metric's defined checks. - Good coverage: enough valid
observations for the stated purpose. - Estimate: approximate
measurement; treat as directional. - Needs review: one or more key
labels are uncertain. - Insufficient evidence: not enough valid
observations.

If a numeric confidence score is exposed, document calibration, meaning,
and validation. Never present raw model confidence as real-world
probability without calibration.

## 8. AI narration contract

LLM input should be a controlled evidence packet, not unrestricted raw
video or a bag of unverified model outputs. Packet fields: -
Player/session identifiers scoped to permission. - Verified metrics and
definitions. - Approved evidence event IDs. - Comparison baseline and
period. - Sample sizes and coverage. - Confidence/verification states. -
Player-selected tone and experience mode. - Prohibited claims and
privacy restrictions.

The LLM may: - Summarize verified observations. - Explain metric
definitions. - Suggest a supported clip to review. - Offer a gentle
optional next step.

The LLM may not: - Change scores or metric values. - Invent an event,
highlight, or personal record. - Claim causal improvement from
descriptive data. - Diagnose health/injury or infer emotional state. -
Reveal private partner data without permission. - Convert low-confidence
events into certainty. - Make a recommendation that depends on
unavailable evidence.

## 9. Minimum evidence rules

Define metric-specific minimums in implementation. Examples: - A
personal-best label requires a stable definition and enough historical
coverage to know the available baseline. - A trend requires at least two
comparable observations; more may be necessary for a meaningful trend. -
A shot effectiveness rate requires valid eligible attempts and verified
outcomes. - A tactical tendency requires enough examples to avoid
overgeneralizing from a few rallies. - A movement map requires valid
player tracking and court calibration. - A social/celebration highlight
requires event evidence and clip-level consent.

## 10. Analytics page mapping

-   Recap: 1--3 high-value facts, one hero clip, one positive personal
    recognition when supported.
-   Rally timeline: segmentation, shot count, duration, outcome.
-   Shots: repertoire, counts, valid outcomes, sequences, placement.
-   Movement: coverage, calibrated path, optional activity.
-   Progress: comparable-session deltas and records.
-   Journey: verified milestones and saved memories.
-   Doubles: pair and individual views separated.
-   Advanced: filters, evidence tables, exports, model/data quality.
