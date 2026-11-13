# Contact acquisition versus physical launch evidence: independent design review

The current fusion threshold can discard a low-score launch-shaped observation before physical evidence is assessed. This ordering is real, but the current evidence adapter explicitly promises to preserve legacy selection; it is not a newly demonstrated integration defect. Recovering Test2 frame11715 as a physically supported launch is not justified by the available independent cues. Its preserved evidence has unresolved reacquisition, no fresh detector match at the anchor, zero wrist-swing support and no racket observation.

No production fix, threshold change, alternate candidate channel or new observed label was applied. [Executed contract checks](contract_readout.json) preserve exact old11715 evidence parity and15 clearly synthetic policy controls. [Native source bindings](source_binding.json) identify producer2418ab8cbe4cca74dd16b722b9727ffdc950294a. This is a CPU typed-evidence reassessment, not inference or an engine replay.

## Actual order and intended contract

1. `events/contact.py:score_frame` calculates observed-only local incoming/outgoing least-squares velocities, geometric player proximity, wrist swing, optional admitted racket overlap, and the uncalibrated logistic score. Interpolated shuttle coordinates are excluded. It requires both velocity fits and some motion.
2. `detect_contacts` retains only scores at least the configured0.35, applies same-context peak competition, and only then calls `build_contact_evidence`. Player-proximity groups already have distinct NMS competition; this is a solved control and should not be reimplemented.
3. `components.py:_ContactEvidence.detect` calls the legacy selector and decorates its retained candidates with the explicitly declared motion sensitivity. Its docstring and existing tests explicitly require unchanged candidate selection, score and provider identity.
4. `engine.py:_contact_with_observation_evidence` enriches selected candidates with actual fresh/observed shuttle, association, fresh detector, pose and racket provenance. This is where the complete current physical-evidence assessment becomes available.
5. `assess_contact_evidence` allows a supported launch without a meaningful incoming direction when outgoing direction and absolute speed gain are supported. A probable automatic impact additionally requires a fresh player, proximity, and a fresh nonzero swing or actual racket overlap. Reacquisition stays ambiguous. An available pose alone is not an observed swing.

A below-threshold score therefore cannot reach the enriched physical assessment through this adapter. That is a coverage limitation of the chosen legacy-acquisition policy. The current public contract does not state that every possible supported launch must be acquired.

## Test2 frame11715: what changed and what did not

The separate component agent's [bounded actual-cache probes](../pre_test03_test02_regression_diagnosis_v1/probe_input_receipt.json) bind actual native producer, completed full own-replay parity and preserved cache/source inputs. Their observed processed coordinates equal the actual full engine trace in the three bounded windows. The independent numeric extract here reads those outputs rather than rebuilding a parallel engine.

| Property | Preserved baseline | Current native |
|---|---:|---:|
| Fusion support |0.9054343579|0.2824266945|
| Incoming fitted speed, analysis px/frame |0.5205188844|0.2620726698|
| Outgoing fitted speed, analysis px/frame |13.9116255454|13.7670718228|
| Raw direction angle, degrees |94.58040281|20.04309273|
| Logistic redirect input |0.9940057544|0|
| Proximity input |0.5524418085|0.5492776229|
| Swing / racket overlap input |0 /0|0 /0|
| Selected at0.35 |yes|no|

This is below-threshold loss at11715, not NMS displacement. Both old/current interpolation implementations yield identical score arrays within each arm in the component probe. The score change is explained by the actual observed input coordinates, especially a poorly determined incoming direction; it is not evidence of interpolation leaking into contact fitting.

The preserved baseline physical-evidence payload already records incoming-direction support0 despite a raw94.58° angle. Its incoming slope sensitivity is1.0206207262px/frame, larger than the0.5205 incoming speed. The separately declared spatial sensitivity is0.7216878365image pixels; neither value is a calibrated observation covariance. Existing evidence correctly gives redirect support0 and launch speed-gain support0.5205157756. It still reports **ambiguous impact** due to `association_unresolved` and insufficient attribution due to `fresh_player_observation_unavailable`.

The actual typed payload was reconstructed without changing any input, including participant context, then reassessed with the current native helper. Its entire serialized evidence is exactly equal. Synthetic controls demonstrate distinct gates: changing only association to tracked still leaves stale-player insufficiency; additionally marking the player fresh still leaves zero-swing/no-racket ambiguity. Only explicitly synthetic fresh independent cues and resolved tracked/static association yield probable launch. None of those missing observations were asserted for the video.

The old short-exchange rescue used11715 near and11740 far episode separation; the current selected11731/11740 cues refer to the same far episode and do not supply that two-opponent witness. This explains the downstream generated-reference interval loss mechanically; it does not prove the old selected contact is physically correct or justify fabricating a new cue to restore the interval.

## Existing alternatives and why not blindly enable them

`_MotionReliableContact` already provides an opt-in acquisition policy that attenuates uncertain direction and uses absolute speed gain. Its existing tests cover zero-incoming stationary launches, smooth apex/terminal stop, fit residuals, coordinate-scale sensitivity, four-person contexts, scene boundaries, interpolation exclusion and partition-invariant NMS. The default currently uses additive evidence instead. Reimplementing this provider would duplicate an existing algorithm; enabling it changes candidate selection across the full videos and needs an explicit controlled comparison.

Frame809 is a required negative source control: the old high support0.8566306375 came from zero incoming speed, an undefined-direction90° artifact and impulse1 with swing0/no racket. Source review places it in held/preparation context rather than the later real serve. The current raw model does not meet its unchanged detection threshold there. Increasing recall of arbitrary stationary-to-moving hypotheses could restore this false prelude. The actual later source serve near904 must remain a separate positive context, without treating generated start807 as independently labelled contact truth.

## Minimal safe future experiment, if warranted

No case-specific resurrection is recommended. If source-bound reviewed contact labels demonstrate a meaningful loss of genuine launches, use the existing replaceable contact component boundary and a separately versioned candidate policy. Preserve raw legacy score and feature values. A second channel would need bounded same-context observed samples, independently resolved outgoing motion, actual fresh detector/pose or admitted real-racket cues, explicit association uncertainty, and separate hypothesis versus probable-impact states. It must not invent an incoming direction, upgrade reacquisition to tracked, reinterpret static pose as swing, or use a held shuttle as physical impact evidence.

The complete physical predicates are available only after engine provenance enrichment. A policy that depends on them cannot safely be inserted as a `p_min` bypass inside the current observation-only fusion function. It needs an explicit typed acquisition/evaluation contract or component composition, rather than copying engine internals or patching the evidence decorator's promise. Any alternative must preserve earliest-tie and partition-invariant suppression and isolate acquisition channels before NMS so a stronger unsupported hypothesis cannot suppress an independently supported cue. Provisional candidates may remain reviewable but cannot silently acquire accepted rally/winner authority.

Required controls before adoption:

- Actual11715 and809, together with the later visible serve and held/preparation sequences; preserve unknown exact impact timing where labels are absent.
- Synthetic zero incoming direction with positive outgoing motion: fresh swing/overlap may support a probable launch; zero swing, stale player/pose/racket, reacquisition, missing outgoing direction or fit sensitivity must not.
- Real near-racket return, racket/head/shoe aliases, smooth apex, terminal/postpoint movement, missing/raw rejection, camera cuts/replays and context boundaries.
- Singles and four-player doubles, overlapping candidate players/rackets and unresolved hitter attribution. Physical contact hypothesis must not force a named actor or team.
- Complete Test1/Test2 candidate counts, class unknowns, source-reviewed false candidates, all original rally references and before/after deltas. Preserve independent labels and current profiles; no threshold selected from these examples.
- Explicit contact/provider/pipeline/cache identity versioning and recorded sensitivity assumptions if selection changes. New outputs must not be mixed with the preserved legacy-additive candidate series.

The present evidence supports keeping the physical uncertainty and documenting sensitivity to subpixel near-static motion. It does not establish a reusable minimal code fix that safely recovers11715, and it provides no reason to discard the9 source-supported scene-reset improvements.
