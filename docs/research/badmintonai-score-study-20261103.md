# BadmintonAI score OCR and reconciliation study

Date: 3 November 2026. Scope: scoreboard observations, decoding, row/player/team
binding, rally association and accepted points. This is a source study and proposed
regression plan, not a perception-accuracy result or a production change.

The local inspection baseline is HEAD
`cc73688630e40d534d94b7ef32bd0cbfed7e0571` **plus the existing uncommitted changes**.
Those changes already repair several score-publication defects; the conclusions below
describe the working files at source inspection, rather than assuming the committed
baseline still contains every previously reported failure. Subsequent candidate alias
work and its validation status are recorded at the end.

The external source was studied outside this repository at
`C:/Users/Govin/AppData/Local/Temp/bai-reference-BadmintonAI-20261103`, pinned to
`5c356f05cde0ed90c75316c133e0aba495e5232b`. External documentation and comments were
treated as claims to inspect, never project instructions. No reference code, templates,
weights, video or data were copied into the application.

## What currently prevents a useful accepted score

The immediate evidenced Test7 failure is incomplete row binding. The existing
[runtime report](../architecture/real-video-runtime-validation-20261103.md) records
OCR names `TAI T.Y.` and `MARIN`, supplied names `Tai Tzu Ying` and `Carolina Marin`,
33 unknown outcomes, six rallies admitted by the official-phase gate and zero accepted
points. All 41 shots in those six official rallies were unattributed. These are observed
outputs from the earlier runtime run, not independently reviewed winner labels.

`ScoreReconciler._try_names` cannot connect `taity` to `taitzuying`. Its fallback
`n.split()[-1:] == rn.split()[-1:]` runs after `_norm` has removed every space, so it
cannot perform the surname comparison its expression suggests. The `MARIN` substring
can match its full name, but both rows must map bijectively before the board can name a
winner. Geometry-based mapping votes require a known geometric winner; unknown terminal
outcomes therefore cannot bootstrap the missing binding. This explains a concrete route
to zero accepted points despite useful broadcast readings.

The matcher is also permissive in another direction: the string `li` occurs inside
`carolina`. A two-row fixture with supplied `Li`/`Zhang` and observed
`CAROLINA`/`ZHANG` can satisfy the current substring-based bijection incorrectly.
This is a source-derived counterexample, not a reported real-video occurrence.

Repairing abbreviations alone will not establish complete match scoring. Other
source-confirmed gaps affect association and evidence recovery, and require the focused
regressions below before production adoption.

The integration owner's subsequent read-only saved-session audit identified a different
failure for the user's Hylo video: configured score-slot names are the numeric strings
`1` and `2`, with two unnamed singles participants and no team binding. It found 65
`broadcast_score` events for `KJAERSFELDT` / `PUSARLA`, all mappings null: first stable
5–3 at canonical frame 3210 and last observed 12–21 at frames 20010–20070. There are
70 rally ends (64 unofficial, six official), 63 unknown terminal outcomes and no accepted
points. Those saved-output counts are diagnostic evidence supplied by the integration
owner, not a reviewed winner evaluation. A name-alias repair cannot legitimately map
these numeric labels to the broadcast athletes.

The existing `ScoreBug.tsx` already renders an unbound broadcast reading with source
names, numbers and age. Hylo therefore needs that observed-source projection to be
verified throughout the application, with accepted-score availability exposed separately
from initialized 0–0. It does not need a default top-row-to-P1 identity. An optional
reviewed/configured binding may link stable named source competitors to score slots,
without implying a physical track, court end or individual hitter.

## Current evidence-to-point path

| Boundary | Current behavior | Consequence |
|---|---|---|
| `perception/scoreboard.py:41`, `parse_scoreboard` | Groups OCR text boxes into exactly two named rows; takes each row's last 1–2 digit number as its current score; rejects numbers above 30. | Flexible general OCR, but it discards completed-game cell structure and ties point recognition to readable Latin names. `ScoreReading.games` exists but the parser does not populate it. |
| `perception/pipeline.py:517`, `_read_scoreboard` | Reads at the configured interval only when the whole chunk's `in_play` input is false; skips replay frames. | Missing OCR can be caused by scheduling even when the score graphic is visible. A chunk entering during play can cover the terminal dead-time without being scanned. This is a coverage risk to measure, not proof of Test7's complete failure. |
| `score_ocr.py:36`, `add` | Validates confidence/range/names/order; requires two matching observations for display; name changes clear row mapping and votes. | The original text/value observations are distinct from a named score decision. Changing abbreviations can repeatedly interrupt mapping. Distinct canonical frames are not sufficient to prove distinct source observations when CFR duplicates exist. |
| `engine.py:397`, `on_ocr` | Emits `broadcast_score` independently of row mapping. | Useful source scores are already available without inventing named points. It currently does not revisit previous unresolved rally decisions. |
| `score_ocr.py:142`, `_after_rally` | Searches after the rally within a bounded window, skips initial unchanged readings, rejects conflicting later changes and permits one completed-game reset. | The delayed-update repair already present should be retained. A stable numeric change is not necessarily a legal one-point transition. |
| `engine.py:1557`, `_finalize_pending` | Finalizes once `ocr_wait_s` has elapsed; default is 4 seconds once any OCR was seen. | A later valid update does not automatically recover the closed unknown/unchanged decision. Increasing this window alone creates more overlapping candidate associations. |
| `events/match_phase.py:162` | Any `board_change == changed` can confirm official play; `unchanged` rejects the candidate. | A stale graphic is currently treated as negative sporting evidence, while a stable incompatible score jump may still establish phase eligibility. |
| `engine.py:1577`, `_finalize_rally_once` | Combines phase, geometry and OCR mapping; only a known scoring slot reaches `apply_rally`; persists point/snapshot in the current score transaction. | Score arithmetic/publication safeguards are separate from whether the visual evidence was associated with the right rally. |
| `engine.py:2073`, `_refold_once` | Reuses each rally's stored `observed_winner` and phase evidence. | A later row binding or newly read board does not, by itself, re-decode earlier unknown winners. Human corrections remain explicit. |

The [existing integrity report](../architecture/event-score-integrity-20261103.md)
and [ledger](../architecture/event-score-integrity-ledger-20261103.md) already cover
transactions, orphan decisions, retry/idempotency, effective revisions, snapshots and
frontend projection. Replacing those repairs with a second scoring engine would lose
working integrity controls without solving the observation/association problems.

## What the reference actually implements

The reference scoreboard is a specialized BWF-graphics reader, not a drop-in replacement
for RapidOCR. It locates a gray strip using fixed 720p image regions, reads bright digit
glyphs, and matches templates harvested using labeled scores. Its scan samples every
30 frames. Two matching sampled values produce an event whose timestamp is the first
appearance. It retains the number of score cells for game detection and warns that
graphics can update more than 15 seconds late. Name recognition is not required for
digit recognition. [Pinned `scoreboard.py`](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/src/badminton/scoreboard.py#L190)

Its pure `score_seq` module drops some contradictory observations and expands score
jumps. Missing mixed-side point order is filled by a fixed convention; reconstructed
entries carry no reading reference. `complete` then gives up to three points to the last
observed leader to reach a legal final. That tail is a heuristic hypothesis: the laws do
not determine that the leader wins the unseen points. A truncated video at 20–17 is a
counterexample to using this as accepted match truth. [Pinned `score_seq.py`](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/src/badminton/score_seq.py#L85)

The offline singles builder greedily assigns each score event to the latest ended,
unassigned rally. It fits end mapping from next-serve votes, fills some missing winners
using server side and service-court parity, and can overwrite the last detected rally's
score/winner with the decoded game final. It identifies A as the match-winning row.
Its snapshot rebuild carries existing side information when unavailable. The useful
pattern is replayable score processing; greedy binding and final padding must not become
our accepted evidence policy. [Pinned `labelfree.py`](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/src/badminton/labelfree.py#L108)

The reference's doubles points code assumes scoreboard rows stay fixed by team on its
studied broadcast and needs a configured top-team anchor, defaulting to A. Reconstructed
points have no rally duration/window. This illustrates the need to distinguish scoring
teams from court ends and physical participants. Its own reliability report still lists
unconfirmed raw-score resets and OCR cache keys that omit templates/calibration as open
risks. [Pinned doubles points](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/src/badminton/doubles/points.py),
[reliability findings](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/docs/RELIABILITY_IMPROVEMENTS.md#L91)

## What its evaluation establishes, and what it does not

The source-free decoder tests compare four committed OCR snapshots with committed
ShuttleSet final scores; they assert final scorelines, point counts, legal single-point
steps and artifact consistency. They do not require video/models/DB. This is a strong
reproducibility pattern, but these assertions do not test a unique correct winner at
each actual rally time. [Pinned score tests](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/tests/test_score_seq.py#L168)

The published Denmark report is marked held out and retains three unknown winners in
each game despite an exact final-score claim. Its OCR artifact contains a 3–8 to 3–0
contradiction in game two. Thus “exact scoreline” and complete observed point attribution
are different outcomes in the reference itself. [Pinned held-out artifact](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/web/public/data/denmark_open_2022_sf/showcase.json)

Further limits follow from the validation code: score-aligned winner comparison can
confirm a score's increment direction without proving the increment belongs to the
correct video interval; order alignment drifts when segmentation inserts/drops rallies.
Neither substitutes for source-bound interval labels. Registration requires configured
player order `[loser, winner]`, 720p footage and manual court calibration. “No inference
labels” therefore does not mean no setup/outcome metadata. [Registration runbook](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/docs/ADD_A_MATCH.md)

No reference test, OCR scan or model run was executed in this study. The GPU connection
was unavailable during this pass. Read source and checked-in claims are separated from
independently reproduced results. The held-out claim for another stage does not establish
a match-disjoint evaluation of score-tail heuristics.

## Proposed failing regressions, in priority order

These are source-derived cases to reproduce on the GPU before modifying production.
The initial 12 focused cases were authored in
`sports/badminton/tests/test_score_alias_transition_integrity.py`; they cover initials,
full-name controls, misleading substrings/initials, complete versus partial doubles pair
labels, shared transitions and distinct-transition controls. Their GPU RED/GREEN results
are recorded separately from this source-derived expectation below. The follow-up file
has 19 cases after accent, reversed-name/partner, hyphen, flattened-pair, ambiguous-name
and numeric-label controls were added.

| Priority / case | Minimal fixture and expected policy | Gap in current coverage |
|---|---|---|
| P1: broadcast initials | Names `Tai Tzu Ying` / `Carolina Marin`; two stable `TAI T.Y.` / `MARIN` readings around a single +1. Unique surname-plus-initial evidence may bind; observed row text is retained. | Current abbreviation failure is evidenced in Test7. Existing tests use exact/substring-friendly aliases. |
| P1: misleading substring and shared surname | Supplied `Li` / `Zhang`, observed `CAROLINA` / `ZHANG`; also two different Lees with observed `LEE`. Both must abstain without unique token/alias support. | Current substring matching can create a false bijection; no collision test. |
| P1: one update, two distinct candidate rallies | Stable 3–2 at frames 0/5 and 205/210; R1 100–200, R2 240–280; stable 4–2 at 300/305; 120-frame wait. One transition must never award two points. Leave competing association unresolved unless more evidence chooses one. | Both current reconciliations see the same +1. Identical-interval dedup does not cover two different intervals. This is not yet runtime-reproduced. |
| P1: update after 4 seconds | Stable old board through end+120, then one stable +1 at end+180/+210. A closed unknown candidate should be reconsiderable within an explicit association policy; stale old board must not be permanently asserted to prove non-play. | Current delayed-OCR test places the update inside its waiting window. |
| P1: mapping becomes known later | An early valid score delta is unmapped; a later corroborated name/explicit binding resolves the same identity episode. Replay must recover only uniquely supported earlier decisions, retain review overrides and avoid duplicate points. | `_refold` retains old unknown observed winners; no late-mapping recovery fixture. |
| P1: illegal stable delta | 3–2 to 8–2 or 3–2 to 2–2 with no game evidence. Store the observation, withhold a one-rally accepted point and do not use mere difference as confirmation of official play. | Current ambiguity test uses multiple incompatible changes, rather than a single stable illegal change plus a geometric winner. |
| P1: missing game final / mixed jump | 20–17 then EOF; 4–4 to 5–5 with two candidate rallies. No invented game-winning point; preserve the unresolved point order. | Prevents copying the reference's tail completion and convention-driven ordering into accepted history. |
| P2: game metadata and reset | Keep completed-game cells across reset, reordered rows, deciding-game end change and a clip beginning mid-game. A reset alone must not assign unseen points whose number/winner is unresolved. | Current `games` field is unpopulated and absent from perception-cache serialization. |
| P2: configured format | Repeat legal-step/reset cases for a configured 15-point game/cap and defaults. | Rules use `MatchConfig`; reconciler still hardcodes 21/30. Existing ledger already identifies this risk. |
| P2: doubles names/team anchor | Four roster participants, two scoring teams, row swaps, same surname/identical kit and an unknown team anchor. Team points must not require an individual hitter or silently choose a default anchor. | Existing score tests are principally P1/P2 singles fixtures. |
| P2: source duplication / lifecycle | Distinct CFR indices from one source observation, cut/replay graphics, restart and format/calibration change. Duplicate observations cannot corroborate themselves; compatible replay must preserve transition identity. | Current `ScoreReading` cannot express source observation identity or layout/identity episode. |

Retain existing delayed-change, completed-game reset, historical-row seeding, rejected
confidence, transactional rollback, retry, correction, restoration and browser projection
regressions. They protect different failure modes.

## Adaptation within the platform contract

Use the existing host/sport entry point, score store and transaction/refold machinery.
The configured badminton pipeline should declare replaceable score observation,
reconciliation/association and rule components, with factories/injection that can actually
replace implementations. A second offline monolith is unnecessary. Generic media,
canonical/source time mapping, scheduling, persistence, transport and artifact execution
stay in `engine/`; BWF score grammar, row/team interpretation and acceptance stay in
`sports/badminton/`.

The minimum boundary should make four outputs distinguishable:

1. **Observed board:** original row text, all recognized score cells, crop/frame evidence,
   recognition support and actual model/artifact version. Missing names must not discard
   otherwise interpretable digits. Display can remain row-based while identity is unknown.
2. **Binding hypothesis:** row-to-scoring-slot/team candidates, basis, identity/layout
   episode and ambiguity. Tokenized surname-plus-initial matching needs a unique bijection;
   explicit reviewed aliases are stronger. Physical track IDs are separate.
3. **Score transition:** before/after observation references, game context, legal delta,
   first/confirmed appearance frames and an opaque stable transition identity. A jump
   records unresolved missing transitions rather than fabricated event order.
4. **Rally association / point decision:** supporting transition and rally IDs, accepted or
   unresolved status, mapping basis, rejection reason and review precedence. Enforce that
   one transition cannot be counted twice. Reconsider only affected unresolved decisions
   as evidence arrives; accepted human corrections remain authoritative.

Every component needs typed input/output, canonical/source timeline and coordinate
conventions, supported singles/doubles/graphics/score formats, parameters, version,
failure/unknown behavior and reset/restore. Fingerprints must bind source/proxy digest,
OCR artifacts, layout/calibration, format, binding configuration and downstream decoder
versions. Changes invalidate dependent results after backing up current evidence.

A source-free score replay bundle is the most valuable reference adaptation: raw parsed
readings (including rejected candidates and their reasons), candidate rally bounds,
binding evidence, configuration and hashes. It must not require inference to replay an
association regression. Its expected accepted decisions must come from reviewed labels
or explicitly synthetic software contracts, rather than copying the decoder's own output.

Prioritize narrow abbreviation/collision regressions first, transition uniqueness and
late-evidence replay next, then structured game cells and configuration parity. Evaluate a
BWF glyph-reader adapter only if current OCR crop-level error analysis shows it is needed.
Keep RapidOCR as the preserved baseline. No new weights/dependency are needed to test the
mapping/association diagnoses.

## Evaluation and licensing gate

For singles and doubles, report board reading accuracy/coverage separately from legal
transition accuracy, row/team binding coverage, time-bound rally association precision/
recall, accepted point accuracy, abstention, score-path edits and complete final scores.
Include latency to first/confirmed board and accepted point, replay/cut/occlusion/adjacent
court slices and resource cost. Match intervals one-to-one at a stated canonical-frame
tolerance, bind labels to source/proxy hashes and preserve a match-disjoint baseline.
Final-score equality alone cannot validate rally timing, missing contacts or shot quality.

The pinned repository's own source license is MIT; substantial copied source would
require its copyright/license notice. This study copies no implementation. Its license
inventory separately identifies Ultralytics/its bundled tracker as AGPL and describes
TrackNet/BST/data licenses. Those declarations are not a substitute for checking the
actual pinned upstream code, model-weight distribution terms, dataset and broadcast
rights before reuse, including noncommercial use. The harvested digit `.npz` needs its
own provenance, source split and artifact hash; a root source license alone does not
establish rights to broadcast-derived assets. [Pinned license](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/LICENSE),
[component inventory](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/LICENSES/README.md)

Before any promotion, reproduce focused failures and passes on the GPU with
`source ../gpu-env.sh` and the existing `.venv`, then run the current score/integrity
suites and a backed-up real-video replay. No tests, inference or media processing were
run on Windows. Production repair and end-to-end scoring quality remain unverified by
this source-study artifact.

## Candidate alias repair and validation status — 4 November

The integration owner ran the initial regression file on the GPU. Its score subset had
seven behavior failures and five passes: the three initials cases, misleading `Li`
substring, complete doubles-pair alias and both shared-transition cases failed as
predicted. The combined `quality-red.log` also included separate contact tests. This
reproduces synthetic software defects; it does not label the real footage's winners.

The assigned candidate in `score_ocr.py` changes only name comparison helpers and
`_try_names`. It compares whole name tokens and complete compatible initials, removes
combining accents for comparison, permits reversed full names and demands one direct
candidate per row. Paired team labels require support for both partners with one unique
partner order/partition, including flattened OCR labels. Numeric score-slot names remain
unbound, and original OCR row text is preserved. Stable-reading, reset, geometry-vote,
point and transition-association behavior is unchanged by this candidate.

GPU validation of the expanded 17 alias/control cases is pending at this record. The two
shared-transition cases remain assigned to integration work, with no transition claims
or consumption introduced by the alias patch. No local tests, inference or media
processing were run. No real-video accuracy gain is claimed.

### Accepted association contract refinement

The original two overlapping-query regressions combined evidence eligibility with point
acceptance. That contract was too strong: `winner_from_ocr` is a repeatable evidence
query, so two candidate intervals may legitimately retrieve the same supported source
winner. The defect is accepting that source change twice at the engine's point boundary.
The revised tests explicitly claim an immutable source-transition reference on behalf of
an accepted rally, rather than making observation queries consume their own evidence.
A separate engine fixture in `test_score_transition_association.py` exercises actual
point publication from two candidate intervals; its GPU RED result is pending.

The proposed reference records version, source-frame pairs and original named row values
in canonical competitor order. Its content identity derives from the globally first
corroborated before/after observation runs, not the candidate's query-local baseline or
after sample. Thus the same unchanged board read at frames 5 and 210 cannot manufacture
different source changes. Canonical row reorder and duplicate delivery retain identity.
The payload validates its schema, bounds, legal delta and content identity on restoration.

`source_transition` remains a query. `claim_transition(ref, owner)` is explicit and
idempotent for the same stable owner, while rejecting another accepted owner.
`clear_transition_claims` supports rebuilding accepted associations during restore/refold;
the existing scoring transaction already deep-copies the reconciler for rollback. Only
the engine's official, supported point boundary may claim. Unofficial candidates and
unbound numeric slot labels must not consume evidence or become named point decisions.
