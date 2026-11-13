# Identity/scoring architecture audit: deliberate separation, no reproduced integration defect

Read-only audit of candidate `c7cf871c81ccfd0b2bec888284bf9eb2f2f62e8a` while
its first full regression runs. No production, profile, annotation or checkpoint
change; no NN, Test3 access or live/session database access. All executable
checks below use private temporary synthetic stores. Their “human” assertions
are test inputs, **not real human-reviewed footage or benchmark ground truth**.

**Finding:** the legacy named resolver is normally gated off, but the existing
reviewed-individual and named-OCR scoring paths work without clearing that gate.
No executable failure of a supported reviewed identity configuration or contrary
public contract was found. Do not set the flag false to obtain names or scores.

## The apparently permanent latch

The engine has five direct assignments to
`_multi_person_identity_ambiguous`, all `True`: construction, format/reset,
participant/context loss, multiple-track ambiguity, and restore. Normal public
configuration/review APIs do not clear it. Consequently, the legacy
`identity.assign(...)` and geometric near/far-fault→P1/P2 winner branch are
unreachable in ordinary new runtime state. Names, valid geometry, two visible
people or configured singles are deliberately insufficient authorization.

`IdentityInference` still constructs a `named_resolver()` and also supplies the
**active** participant tracker and doubles team-hypothesis tracker. The latter
paths execute independently, producing episode evidence and anonymous geometry.
Calling the whole identity component dead would therefore be incorrect.
The `NamedIdentity.assign` protocol has no source/epoch-scoped verified-binding
input or authority result; selecting another named resolver is not an existing
public reviewed-binding mechanism. Its initial side-based assignments are
documented provisional hypotheses.

This leaves legacy/extension debt: there is no current automatic authoritative
track→roster binding admission interface. An implementation of that future
capability would require a typed reviewed/verified binding contract and reset,
epoch, ambiguity and regression behavior. The unreachable legacy branch does not
prove the already documented review product fails.

The test-only `synthetic_support.bind_labelled_synthetic_singles()` does clear
the private flag for explicitly labelled downstream unit fixtures. Its own
docstring forbids using it as a production review or demo-runtime API. That
controlled seam is not evidence of an available public setter.

Source anchors: [engine construction](/home/administrator/Desktop/sport-analytics/test03-pipeline-improvements-20261111/sports/badminton/src/bai_badminton/engine.py:354),
[assignment gate](/home/administrator/Desktop/sport-analytics/test03-pipeline-improvements-20261111/sports/badminton/src/bai_badminton/engine.py:1232),
[identity protocols](/home/administrator/Desktop/sport-analytics/test03-pipeline-improvements-20261111/sports/badminton/src/bai_badminton/components.py:55),
[provisional resolver](/home/administrator/Desktop/sport-analytics/test03-pipeline-improvements-20261111/sports/badminton/src/bai_badminton/identity.py:1),
[test-only labelled seam](/home/administrator/Desktop/sport-analytics/test03-pipeline-improvements-20261111/sports/badminton/tests/synthetic_support.py:1).

## What explicit review actually supports

The identity ledger's module contract explicitly says it is **not consumed by
shot attribution or match scoring**. A confirmed finite episode interval carries
`applied_to_attribution:false`. It validates roster membership, birth/track/
tracker epoch, overlaps, exits and reuse. The public API requires completed
analysis and the current analysis revision; it does not patch a running engine's
private buffers or accept stale episodes after reanalysis.

To credit an individual shot, a separate `stroke_participant_review` must match
the current machine stroke's original episode/birth/track evidence and a valid
identity interval. `build_individual_analytics` counts it once within an explicitly
official rally. The machine contact/stroke actor remains unchanged, as do its
estimated physical impact and class. Identity review is not a winner decision.
Revocation, correction lineage, missing births and conflicts invalidate attribution
rather than selecting a convenient person.

Available product views are intentionally separate:

| Path | Current supported behavior |
|---|---|
|`/identity-reviews`|Finite reviewed track-episode→roster participant association; no live automatic name assignment.|
|`/stroke-participant-reviews`|Explicit hitter review linked to that identity interval; class/impact evidence stays estimated.|
|`/individual-analytics`|Reviewed per-person/team shot accounting plus quality-gated reviewed motion/pair positions.|
|`/estimated-individual-analytics`|Separately labelled bounded continuity estimates from reviewed seeds; never added to reviewed totals.|
|Canonical legacy match analytics/heatmaps|Consumes canonical actor IDs and track provenance; identity reviews are not silently merged into machine actor fields. An empty named legacy view does not mean the reviewed-individual route is broken.|

The roster schema explicitly distinguishes participants, teams, P1/P2 score slots
and tracker episodes. Roster order/names do not imply a track mapping. Generic
event verification cannot create/rewrite tracker identity evidence; dedicated
review routes are required. Reviews are intentionally not carried across a new
analysis's possibly different births. Doubles also has separate explicit
service-setup/review folding; the two scoring slots are not its four athletes.

Source: [ledger contract](/home/administrator/Desktop/sport-analytics/test03-pipeline-improvements-20261111/sports/badminton/src/bai_badminton/identity_review.py:1),
[review API](/home/administrator/Desktop/sport-analytics/test03-pipeline-improvements-20261111/apps/api/src/bai_api/routes/identity_reviews.py:43),
[individual fold](/home/administrator/Desktop/sport-analytics/test03-pipeline-improvements-20261111/sports/badminton/src/bai_badminton/analytics/individual.py:36),
[individual API](/home/administrator/Desktop/sport-analytics/test03-pipeline-improvements-20261111/apps/api/src/bai_api/routes/sessions.py:247),
[estimated fold](/home/administrator/Desktop/sport-analytics/test03-pipeline-improvements-20261111/sports/badminton/src/bai_badminton/analytics/automatic_individual.py:1),
[roster contract](/home/administrator/Desktop/sport-analytics/test03-pipeline-improvements-20261111/engine/src/bai_engine/schema/session.py:99).

## Scoring names are independent of physical track names

`BadmintonSession` passes `session.players` P1/P2 scoring-label names into
`ScoreReconciler`; it does not infer them from roster ordering. A unique name
match can bind observed scoreboard rows to those scoring slots. Doubles matching
requires the complete partner pair when supplied, retaining ambiguity for
partial/overlapping names. It does not identify which of four visual players hit.

Even with the private latch true, a corroborated legal scoreboard increment can
produce a slot winner and accepted point when format, official-play eligibility,
unique source-transition association, score sequence and ownership checks pass.
Late reconciliation preserves its source evidence and bounded ledger; human
winner/official-play correction is another explicit route. Neither requires the
machine hitter to be named.

Conversely, without explicit uniquely matching score names the source board can
remain visible yet unmapped. The old geometry-vote bootstrap has no normal named
geometric winner while the latch stays true. Installing appearance weights or
adding an interval identity/hitter review does not silently populate that map.
An operator must configure scoring names or provide an explicit winner review;
that is separate from reviewing visual identity. Changing session display names
is not a public live track-binding command.

This explains current Test1/2 limitations without claiming all point logic is
blocked: unbound score labels, uncertain raw reads/layout/game columns, missing
or ambiguous source increments, fragmented candidates, official-play/format
gates and absent observed terminals remain distinct. A geometric landing
hypothesis cannot bypass them. Empty accepted points must remain unavailable,
not be presented as a verified0–0 or0% scoring accuracy.

Source: [session→OCR names](/home/administrator/Desktop/sport-analytics/test03-pipeline-improvements-20261111/sports/badminton/src/bai_badminton/plugin.py:114),
[name binding](/home/administrator/Desktop/sport-analytics/test03-pipeline-improvements-20261111/sports/badminton/src/bai_badminton/score_ocr.py:386),
[winner from board](/home/administrator/Desktop/sport-analytics/test03-pipeline-improvements-20261111/sports/badminton/src/bai_badminton/score_ocr.py:515),
[acceptance gates](/home/administrator/Desktop/sport-analytics/test03-pipeline-improvements-20261111/sports/badminton/src/bai_badminton/engine.py:2367).

## Executable evidence

[Probe source](architecture_probe.py), [exact result](architecture_probe_result.json)
and [output](architecture_probe.log) preserve the tested candidate and source
hashes. It instruments the resolver call count in its own process; it never
assigns the latch false. All stores are private temporary synthetic fixtures.

| Synthetic test | Result |
|---|---|
|17 calibrated first-view frames, configured singles/names|Latch true; named-resolver calls0; machine contact/stroke actors null.|
|Valid finite identity interval only|Reviewed attributed shot count0, as documented.|
|Additional explicit scoped hitter review|Reviewed individual shot count1; both machine actors still null; points0; latch still true.|
|Singles, matching scoring names, legal stable late OCR + cached eligible phase|One accepted P1 point with latch true; no identity/hitter review supplied.|
|Doubles, complete partner scoring names, same legal OCR contract|One accepted P1 team-slot point with latch true; no four-player binding inferred.|
|Either format, no scoring names|Zero accepted points; observed rows remain unmapped.|

The scoring fixture supplies synthetic cached phase/unknown terminal context and
exercises real OCR reconciliation, rules, correction and ledger code. It is not
video accuracy or a claim that all real source transitions are eligible.

Existing initial-unbound identity, ledger, individual accounting, late-scoring
and team-name/alias suites pass **76 tests in2.66s**; [log](architecture_existing_contracts.log).
They include four-person/team accounting, reset/revoke/lineage negatives and
unmapped-score controls. These software tests do not verify real physical IDs,
contact/hitter accuracy or the running NN result. The short CPU-only probe/tests
shared the host during that run; no controlled runtime speed claim follows.

## Decision

No pipeline fix is proposed from this audit. The safe initial absence in Test1/2
and the finite review product are deliberate and executable. The missing
automatic authoritative identity-admission interface and unused legacy named
resolver are genuine capability/architecture debt, not evidence to force a
private boolean false or to name players by side. Any future implementation
needs an explicit public binding/evidence contract and before/after tests; a
demonstrated supported-input failure should be reproduced before changing code.
Candidate/core, original reports and prior identity receipts remain unchanged.

The new [audit receipt](architecture_audit_receipt.json) binds this document,
probe/results/tests and source snapshot hashes. Existing `REVIEW.md` and identity
fix receipts were not overwritten.
