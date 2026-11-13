# Existing torso-HSV continuity: fixed source-feature investigation

The existing HSV descriptor is **not sufficient to restore all lost athlete hypotheses**. A predeclared online self-consistency screen supports22 of72 fresh source candidates in the seven Test1 loss groups, while mutual-nearest matching alone supports63 but also favors a reviewed official region. These are feature-diagnostic counts, not identity accuracy, TP/FP/FN or pipeline admissions. No production change, NN inference, checkpoint download, threshold tuning or new physical ground truth occurred.

## Fixed method and evidence

[CONFIG.json](CONFIG.json) was written before feature measurement. The experiment calls the actual existing `identity.hsv_signature`:8×8 hue/saturation histogram, L1-normalized, using rows20–55% of the raw bounding-box crop. It does not replace this descriptor, segment the shirt, resize metric inputs or reuse a neural cosine threshold. Primary distance is total variation (half L1); Hellinger is retained separately. Both lie on histogram-specific scales.

Each reference gallery is the last at-most32 **past** fresh raw-box observations of the same scene-only visual episode/context whose feet satisfy the unchanged CourtROI with `allow_runoff=False`. This is the strict target-court doubles-envelope geometry predicate, not independently measured physical location or named athlete identity. No outside appearance observation updates a gallery. Source cuts/context resets invalidate automatic continuity; a historical contrast across a cut remains diagnostic only. Eight hundred distinct selected gallery memberships were independently checked for fresh matching, strict geometry and past-only order: [gallery audit](gallery_memberships.json).

The reference mean is compared with the current histogram. The fixed envelope is the **maximum leave-one-out reference-to-other-reference-mean TV**, with at least2 samples. No percentile, margin or cutoff was selected from athlete/official outcomes. Mutual nearest requires the target bank to be the candidate's unique closest retained bank and that candidate to be the bank's unique closest retained candidate; it has no absolute similarity test. Neither diagnostic grants authority.

All2,028 descriptors,64 raw histogram bins, source frame/PTS/pixel hashes, original bbox/torso crop hashes, size/entropy, context and known freshness are preserved in [raw features](raw_features.jsonl). [Complete query results](results.json) retain all368 comparisons and competitors; [compact summary](summary.json) separates fresh/carry and context. Reference banks and source model records bind the actual RFDETR-small1.4.2 checkpoint SHA `fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e`. All retained Test2 model-input crop hashes were reproduced exactly. Test1 foreground positions are real current raw matches, but its complete proposal competition/crop digest/confidence is not serialized at most loss frames; newly measured source-crop hashes are not falsely presented as original worker fields.

## All seven Test1 coverage groups

These are the182 source-reviewed gross withheld-person rows from completed c585 output, not a new labelled detection dataset. Seventy-two rows retain a fresh raw matched image region;110 use carried boxes and cannot become fresh detection evidence. The five-frame7801–7805 group has no fresh model proposal under the original cadence. Six distinct recorded temporal/camera contexts are represented; these are not match-disjoint or doubles validation.

| Group / inclusive frames | All rows | Fresh raw candidates | Strict bank samples | Within fixed envelope (fresh) | Mutual nearest only (fresh) | TV fresh min / median / max |
|---|---:|---:|---:|---:|---:|---|
| 1: 753–800 | 48 | 24 | 32 | 13 | 24 | 0.308 / 0.400 / 0.476 |
| 2: 3413–3449 | 37 | 18 | 32 | 7 | 18 | 0.262 / 0.338 / 0.492 |
| 3: 6365–6381 | 17 | 8 | 32 | 0 | 0 | 0.630 / 0.676 / 0.715 |
| 4: 7801–7805 | 5 | 0 | 32 | 0 | 0 | N/A (carried only) |
| 5: 7812–7856 | 45 | 8 | 32 | 2 | 7 | 0.328 / 0.509 / 0.568 |
| 6: 8087–8105 | 19 | 9 | 3 | 0 | 9 | 0.239 / 0.252 / 0.383 |
| 7: 14103–14113 | 11 | 5 | 32 | 0 | 5 | 0.435 / 0.527 / 0.540 |

The envelope supports22/72 fresh rows;50/72 remain unsupported by this particular descriptor screen. This is **not** evidence that those50 people are officials or should be dropped. Group8087–8105 has only3 strict reference observations and a narrow pose range. Carried-row pixel features remain diagnostic; they never refresh model-observation time, gallery state or identity.

Mutual-nearest supports63/72 fresh rows, but Test1 comparisons can use only retained foreground candidates rather than every pre-ROI proposal. Its apparent uniqueness is conditional on that incomplete competition. Group6365–6381 supplies no mutual-nearest positive; one7812–7856 candidate is ambiguous with another bank. No difficult group is excluded, no missing score is imputed, and no complete182-row restoration is claimed.

## Test2 official handover: every retained negative query

The original reviewed official-region box at5958 selects the stationary background-region candidate spatially at the unchanged0.3 IoU query gate. This is **diagnostic case selection**, not a production position blacklist or an appearance-based label. Every matching retained raw candidate through6492 is included:186 distinct source frames, with full current proposal competition and actual uncalibrated detector scores. Each is compared to the fixed pre-handover court-origin gallery, which contains32 strict fresh athlete-region observations ending5908. No official appearance enters that bank.

The official TV distance is0.429408–0.554674 (median0.485530), outside its bank's predeclared LOO maximum0.351803 on all186 queries. Hellinger is0.4888–0.5769. Of these comparisons,77 remain in the same recorded context before6151;109 follow the6151/6307 resets and are historical out-of-context contrasts, **ineligible for automatic admission**.

Mutual-nearest nevertheless favors the official twice:6018 in-context (TV0.436752) and6210 after a reset (TV0.434714). In both cases the official is nearer to the old gallery than every current competitor, despite a substantial absolute feature mismatch. The fixed envelope rejects feature support in both. Thus relative/mutual matching alone cannot prevent the measured official handover. Conversely, the observed separation of this one blue-shirt/black-shirt contrast cannot establish general official rejection or justify a universal HSV cutoff.

## Source interpretation and uncertainty

[Source-crop controls](source_crop_controls.png) show first/middle/last past strict-bank examples and first/middle/last fresh candidates for every group (or explicit carried candidates where none is fresh). The negative row includes5958/6492 and **both** mutual-nearest counterexamples. Exact panel inputs/hashes are in the summary; the chronological preview correction is disclosed in [render note](render_order_note.md). No success-based example selection was used.

The raw rectangles include background as well as clothing. Green-court versus red-runoff pixels, front/back views, raised arms, torso scale and pose change the histogram for the **same visibly continuing athlete**. The white-shirt6365–6381 group and the sparse3-reference8087–8105 group demonstrate this strongly. Therefore an outside-envelope HSV result is not a safe hard contradiction that revokes an athlete origin. A within-envelope result likewise does not certify athlete identity, especially with similarly dressed people or doubles teammates.

### Confirmed evidence versus unknown authority

- Confirmed: raw descriptor values, exact source/crop metadata,800 fresh strict past gallery memberships,72 fresh candidate locations, fixed diagnostic outcomes and explicit6018/6210 relative-matching counterexamples.
- Supported only as a feature observation:22 fresh athlete-region histograms fall within their own historical variation envelope. They are not newly verified named participants or physical identity matches.
- Unknown: role/identity for any proposed automatic continuation; positive coherence for50 other fresh cases; fresh evidence on110 carry rows; complete Test1 background competition and most current foreground confidence values.
- No new physical GT/AP/IDF1/HOTA/winner/point metric: source-agent roles remain diagnostic. Current raw detector confidence is null where unavailable, never copied from the historical accepted person.

## Engineering implication

Do not adopt this HSV-only policy as a target-participant admission or rejection gate, and do not widen its envelope to fit these seven groups. It offers useful appearance contrast in some cases, but the measured positive cost and mutual-only negative examples contradict treating it as reliable identity evidence. A source-fresh motion/association hypothesis must remain separate from roster/name/team/scoring authority; outside observations must never self-train their own appearance gallery.

If appearance is retained as an optional uncalibrated cue, ambiguous or low-evidence cases must stay unknown. A future foreground-aware/pose-aware descriptor or pinned learned appearance model would be a **new** component trial requiring independent held-out real-athlete/official, pose, lighting, same-uniform and four-player controls. This study does not authorize such a replacement or a new NN download. The orchestrator will assess independent motion/association evidence before proposing any minimal reusable fix.
