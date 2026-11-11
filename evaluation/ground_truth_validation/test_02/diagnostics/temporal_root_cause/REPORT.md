# Test 2 temporal root causes and current significant-case review

This report analyzes the **completed current baseline**, not an old benchmark
or a tuned candidate. Original annotations, predictions and temporal parameters
are unchanged. All39 current significant cases appear in
[case_register.md](case_register.md), with exact reference/prediction frames and
seconds, signed boundary errors, publication frames, machine observations and
source limitations. Machine-readable evidence is in `case_register.json`,
`focused_transition_evidence.json` and `short_witness_gate_audit.json`.

## Evidence and evaluation scope

The genuine worker/parent completion guard verifies29,296 frames and489 original
cache chunks. The source is SHA256
`4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a`.
The own-source semantic replay has exact baseline parity and exactly29,296
ordered step calls; its118MB trace digest is checked against the replay manifest.
Read-only diagnostic replay is not fresh neural inference. No live SQLite was
opened for this review.

Against the unchanged73-row legacy-generated rally reference,75 predictions give
**68 TP /7 FP /5 FN**, precision0.906667, recall0.931507, F1 **0.918919**, mean
IoU0.848135. Matched start/end MAE are23.882353/21.161765 frames
(0.796078/0.705392s); duration MAE1.302451s. The separate75-row coarse reference
gives69 TP /6 FP /6 FN; it is a different reference population and does not replace
this primary result. Neither reference is newly adjudicated physical truth.

“Expected” below means the supplied benchmark interval. Internal segment maturity
counts endpoint samples inclusively; exports and the frozen evaluator use
half-open spans. That existing distinction is preserved, without adding frames
or padding short predictions to improve metrics. Unmatched intervals have no
fabricated boundary-error values.

The39 significant cases comprise32 reference-grouped cases and7 unmatched
predictions. Selection is unchanged: unmatched, matched boundary error exceeding
30frames, or matched IoU below0.75. Three historical source-review files were
reused only after their stored SHA256 values and shared original-video SHA256
matched. Their source interpretations remain **agent diagnostic drafts**, not
independent human labels. Current machine facts are recomputed from this run.

The subsequently published root causal helper was cross-checked independently:
all39 significant case identities and every available prediction's interval,
publication frame and terminal reason agree exactly with this compact register.
`causal_helper_crosscheck.json` retains the helper summary and per-case hashes.

## G69: raw availability gap becomes two published intervals

| Item | Supplied reference / actual current evidence |
|---|---|
|ReferenceG69|[26616,27668) =887.200000–922.266667s|
|Matched prediction|[26654,27325) =888.466667–910.833333s|
|Unmatched prediction071|[27349,27649) =911.633333–921.633333s|
|Matched errors|Start+38frames; end−343frames; duration−381frames/−12.7s; IoU0.637833|
|Raw unavailable|27326–27347 inclusive,22frames|
|First selected reacquisition|27348 /911.600000s, observed but adjacent speed unavailable|

The completed trace resolves the exact sequence:

1. At27335, the tenth missing observation moves IN_PLAY→ENDING and proposes
   end27325. At27340,15frames after that proposed end, the segment becomes CLOSED.
2. At27348 raw/associated observation returns, but speed is unavailable because
   its preceding compatible observation is missing. It does not build an
   observed-motion resume run.
3. The current merge setting is`round(0.75*30)=22`frames. Observation separation
   from last end27325 to27348 is23frames, beyond that existing gate. The step
   finalizes [26654,27325) at27348; this is an actual machine publication, not a
   guessed timestamp.
4. Compatible motion begins27349 and reaches the three-observation start gate
   at27351, opening a new interval from27349. Its later cut publication is27664,
   retaining end27649. That second interval is evaluator FP071 under one-to-one
   matching to the already-matchedG69 reference.

This run reacquires one raw frame earlier than the original historical27349
observation, but it still splits. Reacquisition on the publication frame is not
proof of an ordering defect: the current evidence lacks adjacent speed and is
already outside the defined observation-separation window. Calling22 missing
samples an automatic within-window resume would silently change the existing
contract. No global timeout extension is justified from this example alone.

The completed perception review separately proves that this gap starts upstream
of association: no accepted raw coordinate exists, all15 retained peak candidates
are below0.5 and mask-allowed, and10 gap frames have no retained candidate. Main
view/VALID geometry/epoch33/two tracks persist. At27348–27353 the lower selected
branch lies around the near player's racket/head/hand region, followed by an
upper/lower competing selection at27354. The lower branch is a probable equipment
distractor in sampled source review, not an adjudicated physical shuttle error.
See `../current_scene_and_ocr_review/g69_gap_extended/REVIEW.md`.

Source panels support ongoing player action at displayed16:16 through the gap;
the later visible edit near27664 limits the reference terminal convention. The
largest measured end discrepancy therefore deserves priority, while an invented
flight trajectory, forced upper candidate or unconditional interval merge would
conceal rather than solve the perception conflict.

## Short-exchange controls: admission and benchmark matching are different

| Reference case | Current candidate / publication | Exact admission result | Benchmark consequence |
|---|---|---|---|
|G31 [11714,11830),390.466667–394.333333s|[11715,11751), published11774|37internal samples accepted by witnesses11715/11740|Only36/116 interval overlap, IoU0.310345; G31 remainsFN and prediction032 remainsFP|
|G32 [11860,11942),395.333333–398.066667s|[11873,11926), published11949|54samples accepted by witnesses11899/11922|Matched IoU0.646341, start+13/end−16frames|
|G56 [20947,21045),698.233333–701.500000s|[20943,20994]52samples canceled21017; [21033,21035]3samples canceled21058|No sufficient short-exchange witness pair|FN retained|
|G58 [21736,21809),724.533333–726.966667s|[21741,21779]39samples canceled21802|Same-actor contacts fail opposite-episode proof|FN retained; walking/handling negative control remains rejected|
|G63 [23879,24012),795.966667–800.400000s|[23908,23920]13samples canceled23943; [23956,24013]58samples canceled24036|Stable opposite-episode proof fails|FN retained|

The short-exchange witness gate was recomputed using the exact original contact
evidence consumed by this FSM, rather than later sanitized public contact
payloads. It requires an observed-motion span, disjoint bounded motion windows,
one probable/confirmed trajectory or impact cue, and simultaneous stable opposite
episodes with matching birth/track provenance in both source contexts. Different
track IDs alone do not certify different physical people.

- **G31 andG32:** all tested pair gates pass. Their short intervals are genuinely
  retained by the implemented opt-in mechanism; it would be wrong to describe
  G31 as having no detected exchange. Source11740 shows net play,11758 relaxation
  and11802 retrieval. Its long reference tail is not proven continuous airborne
  play. A separate motion candidate11802–11823 is canceled at11846. Padding the
  accepted37-sample interval to fill that tail would merely fit a label.
- **G56:** targets are opposite stable episodes, but both relevant contact
  trajectory/impact assessments are ambiguous; the required probable cue is
  absent. Source20947/20970 supports a short active sequence, while20994 shows
  relaxation/walking. Accepting the first short candidate alone would still have
  only47/102 overlap with the reference, below0.5; lowering maturity is not even
  guaranteed to recover this reference match.
- **G58:** both21759 and21771 candidates target the same episode despite probable
  trajectory assessments. The opposite-actor gate correctly fails. Reviewed
  source21745/21759/21775/21795 shows relaxed walking/handling. Its canceled
  candidate would geometrically overlap the reference above0.5 if admitted;
  improving that numerical score by accepting walking would be a bad fix.
- **G63:** trajectory can be probable despite insufficient impact; insufficient
  impact alone is not the gate explanation. At23968 the participant pair is
  episodes1/2, but24009 observes1/3 after the far-side track/birth changes. The
  same opposite episode pair cannot be established in both contexts, so the
  typed proof fails. Source23960/23985 supports action, with relaxation/grounded
  shuttle by24013; physical identity and exact boundaries remain unreviewed.

These controls argue for better perception/episode continuity and reviewed
contact evidence, not globally reducing the60-sample duration threshold. The
existing strong short-proof feature already recovers the cases it can support.

## Missed11346 edit: separate scene acquisition from early contact admission

The completed cache/source review proves a visible same-camera edit11345→11346
(378.166667→378.200000s) with abrupt player relocation and displayed4:0→5:1.
The selected raw observer has only one prior region, so no raw edit hypothesis
or detector-layout decision is acquired; content epoch13 remains unchanged.
The detector does run11346, but no person track is returned until two new
episodes appear11348. This is not proof that the raw detector ran unsuccessfully
or that same-camera court geometry is wrong.

The actual FSM is **IDLE** at the visible edit. It does not merge an existing
active rally across that cut. At11353, an estimated contact with **insufficient
impact and insufficient trajectory** opens a new candidate through
`legacy_candidate_contact_policy`. A stationary tentative end11361 closes11376;
another accepted ambiguous/insufficient contact at11380 reopens it. A11394
contact resumes/retains the candidate, and the final [11353,11657) publishes11680.
The suppliedG30 interval is[11394,11661),379.800000–388.700000s; current output
starts41frames early, ends4frames early, IoU0.853896.

The early boundary is therefore an actual contact-admission/preparation chain.
Some first post-edit observations and contact contexts are already wholly after
the cut. A hypothetical scene reset at11346 is not established to remove the
later11353 candidate. Source arrangement/serve versus preparation still requires
physical adjudication. Distinguish the verified missed acquisition from the
unproven claim that fixing that cut alone fixes all41 boundary frames.

The root-owned semantic racket-admission candidate remains a separate pending
experiment. No result from that unintegrated candidate is included in this
baseline report or used to rewrite the baseline's contact/rally counts.

## All other significant cases and reference controls

The case register preserves the remaining onset, terminal and gap mechanisms
without discarding inconvenient references. Particularly useful controls are:

- G11/reference[3863,4215) spans visibly different scoring/play contexts. Extra
  prediction011[3877,3936) contains earlier play; the later matched start4030 is
  not automatically a false split within one physical point.
- Prediction047[15451,15609) contains substantial source-supported net,
  overhead and diving activity. It remains an evaluator FP, with reference
  omission concern recorded instead of tuning the activity away.
- G39 has no qualifying one-to-one match while predictions040/041 overlap its
  activity. G55 and extra prediction058 expose separate raw-availability and
  continuity conflicts; their recorded candidates and source caveats remain.
- Several reference onsets/ends include service preparation, pickup, walking or
  an edit. Raw absence in those spans is not automatically a physical shuttle
  false negative. Model coordinate presence is likewise not proof of a hit.

All seven unmatched predictions remain in the denominator and all five missed
references remain misses. The39-case register includes every matched significant
error and the full unmatched population; none was removed after source review.

## Ranked improvement and regression priorities

1. **Perception continuity and competing shuttle branches:** G69's−343-frame
   matched end error is the largest observed terminal discrepancy. Review raw
   candidates against source-bound visibility labels; retainG39/G55 and true
   post-point gaps as controls. Improve justified observation/association evidence
   before considering any temporal policy change. Do not substitute low-support
   upper coordinates or airborne floor projections as truth.
2. **Contact/equipment semantics and admission:** verify whether a purported
   racket observation is physical equipment or pose-derived geometry before
   allowing it to substantiate a contact. Test source11353 preparation, true
   short exchangesG31/G32, walkingG58 and post-point pickup. Root owns the
   current candidate and its before/after/regression evidence.
3. **Scene acquisition beyond existing raw candidates:**11346 remains visible
   but unacquired. Develop an independently supported cue with continuous lunge
   controls7703, walking23639, true edit22946, occlusion, missing geometry and
   doubles. Lowering the required region count alone is not a supported fix.
4. **Anonymous episode continuity:** G63 demonstrates why track replacement
   cannot be silently equated with a stable athlete. Improve current observation
   and episode linking with explicit uncertainty; retain the same-actorG58
   control and birth/epoch restrictions.
5. **Reference adjudication:** independently label serve/contact/terminal frames,
   activity versus retrieval, omitted points and cross-edit completeness. Resolve
   named-player/score-row conventions separately. Better labels are necessary
   to rank physical accuracy improvements beyond agreement with legacy proposals.

The Test 1 recovery-frontier, source-score-vote and foot-projection repairs stay
in place. No new temporal defect requiring a blind threshold patch was proven
by this review. Existing policy/source tests and source-derived regression cases
remain useful, but passing them does not establish physical contact, identity,
stroke or winner accuracy. No production code or original data was changed.
