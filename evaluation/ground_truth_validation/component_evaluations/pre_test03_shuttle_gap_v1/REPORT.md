# G69: image-boundary censoring, racket alias and rally split

The continuous source sequence supports an **out-of-frame flight hypothesis plus a moving racket distractor**, rather than22 independently established visible-shuttle misses. The raw gap is real; its interpretation as negative rally evidence is the weakness. This review establishes source-bound machine causes and agent visual diagnostics. Physical ground truth, FN count and physical accuracy remain **unavailable**, not zero. No production, annotation, model, threshold or current candidate was changed.

## Scope and source proof

The existing completed `Test2/improved_v1` worker/parent/catalogue and its exact own-parity semantic replay are verified. Source SHA `4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a`; analysis-proxy SHA `2841ee54fb0b6d28c2a57e89293ba4530173980635c21aa8d08f60f52931b6cd`. The original Test2video is absent: this is exact source-bound **proxy** review. TrackNet checkpoint SHA `df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a` is rehashed, never loaded.

Only64selected frames27312–27375 (910.400000–912.500000s at30fps) were retained/analysed. The H264decoder needs12additional prior-frame codec preroll; those were discarded without pixel review. Rational PTS, round-trip PNG equality, BGR and file hashes are retained for every selected frame. Two consumed closed cache segments match the completed catalogue; raw/association fields also exactly match the older snapshot independently bound to its completed run. No SQLite, neural inference, download or additional control-video decoding was used.

[Input bindings](attempt_v1/input_binding.json), [source pixel/PTS receipts](attempt_v1/source_receipts.json), [cache rows](attempt_v1/cache_window.json), [bounded FSM trace](attempt_v1/fsm_window.json), [all retained candidates](raw_candidates.csv), and [structured diagnosis](diagnosis.json) preserve the reproduction. The recorded source commit and actual executed source hashes are retained rather than replacing them with the new candidate's commit.

## What is visible

[All64upper-region source crops](attempt_v1/top_source_montage.png) and [near-player source crops](attempt_v1/body_source_montage.png) preserve the two branches separately from predictions. [Enlarged boundary sequence](visual_review_v1/top_edge_sequence.png) uses nearest-neighbour pixels and an external label strip. Full-frame review pages are [1](visual_review_v1/full_source_page_01.png), [2](visual_review_v1/full_source_page_02.png), [3](visual_review_v1/full_source_page_03.png), [4](visual_review_v1/full_source_page_04.png).

- 27313–27323: a bright upper object descends. At27324 the far athlete makes an overhead swing; exact impact/object-versus-racket separation is not adjudicated.27325shows a bright upward streak.
- 27326–27328: part of that bright object remains at the upper border. The model supplies only low-support candidates, not accepted coordinates.
- 27329–27352: the upper object is not visually resolved in the reviewed sequence, consistent with flight outside the image. This is a supported uncertainty hypothesis, not a physical absence label.27353has an uncertain upper-border re-entry candidate.27354is the first clearly visible descending upper return in this review.
- 27348–27353: the selected lower model coordinates follow the near blue athlete's visible racket head while that athlete prepares an overhead response. This is a source-supported alias diagnosis, not independent shuttle/contact annotation. The upper return later descends toward the near overhead swing around27371–27372; exact contact time/class remain unadjudicated.

The camera, player motion and displayed16:16 continue without an observed edit in this64-frame window. Main view, VALID geometry, camera shot11, content epoch33 and two returned people persist. No new pixel-ground-truth file is created: the per-frame `visibility_review` tags are explicitly agent diagnostics with `GroundTruth:null`.

## Raw selection and mask evidence

|Frame|Accepted raw(x,y), support|Retained competing peak / interpretation|
|---|---|---|
|27325|(788.869,56.927),0.635254|Last accepted pre-gap model point; fresh model observation is not calibrated physical truth.|
|27326|None|Rank1(787.5,57.5),0.188232 follows prior tail; rank2(807.5,2.5),0.176392 is near the visible upper edge. Lowering the threshold does not automatically choose the right branch.|
|27327/27328|None|Upper peaks(807.5,5),0.204346/0.220703; source partial edge object still visible.|
|27326–27347|None on22frames|15retained candidates across12frames;10frames have none above diagnostic floor0.1. All15peaks mask-allowed and below inference threshold0.5.|
|27348|(784.968,429.917),0.674805|First accepted reacquisition follows visible racket head, not a newly certified shuttle position.|
|27353|(806.018,449.495),0.685059|Upper rank3(852.5,2.5),0.117065; lower racket branch wins.|
|27354|(855.600,6.573),0.752441|Lower rank2(815,457.5),0.685303 still exceeds threshold. The global maximum switches branches.|

Exact accepted outputs and every retained top-eight candidate for27313–27327and27348–27354 are pinned in `diagnosis.json`, with support, mask flag, centroid/spread and selected status. Top-eight is a retention bound, not eight guaranteed candidates. No full heatmaps are retained. Below-floor responses and unseen mask values cannot be reconstructed or called absent. Detailed raw/masked maxima at27326/27327 agree and explicitly say `below_threshold`; later detailed diagnostics are sparse. The confirmed claim is no mask rejection of the **retained** candidates and no association veto of an accepted raw coordinate during the22-frame gap.

TrackNet's recorded decoder selects the global maximum component above0.5. The association provider's declared scope is co-observed **static** distractors; the coherent moving racket is not established static background. It preserves these fresh raw selections and emits no alternative physical coordinate. This is a capability limitation, not proof that changing a threshold, choosing the upper peak or masking all player/racket pixels would be safe.

## How the missingness becomes two rallies

The exact completed own-parity trace, not a new parallel FSM, records:

|Frame|Machine transition|
|---|---|
|27325|Last accepted raw observation before gap.|
|27335|Tenth missing observation: IN_PLAY→ENDING, proposed end27325.|
|27340|Existing15-frame lookahead expires: CLOSED with end27325.|
|27348|Lower model point returns; adjacent observed speed is unavailable. Observation separation23frames exceeds unchanged round(0.75×30)=22merge budget; publish[26654,27325).|
|27349–27351|Three observed-motion samples on lower branch open a new interval from27349.|
|27353|Branch switch vicinity contributes an estimated contact candidate.|
|27354|Clearly visible upper return wins the heatmap; previous interval is already published.|

`engine.py` maps absent accepted observations to MISSING (or marked reconstruction if available); `RallyEvidence.step_evidence()` increments the base gap counter unless independent continuation/exit support qualifies. `use_reconstruction=False` is the rally continuation flag, not permission to treat interpolated points as observed. `use_exit_recovery=True` is already enabled: `image_exit_return_supported()` requires the **first observed return bracket** in the top10% band with coherent upward/downward motion. Its actual first return is lower y429.917, outside the image's72px top-band boundary; this bracket cannot qualify. The raw source/candidate alias therefore defeats the existing boundary-recovery proof. No arithmetic/order bug or automatic within-budget recovery was established.

[Downstream source events](visual_review_v1/downstream_events.json) show estimated contacts at27324,27353and27371. At27353the incoming motion uses lower27350–27353, while outgoing27353–27356crosses to the upper branch: fitted outgoing speed121.152px/frame and residual126.964px are not a coherent physical flight. The physical evidence status is **insufficient**, racket contact/overlap is false, and the stroke staysunknown. A high uncalibrated heuristic event support0.985997 is not physical contact confidence. No named winner or accepted point is established by this sequence. Unknown classification is appropriate uncertainty; the extra candidate still affects shot/rally analytics.

Legacy generated referenceG69is[26616,27668), matched prediction[26654,27325) has IoU0.637832700, start+38frames/end−343frames/duration−381frames, with another prediction[27349,27649) unmatched under one-to-one matching. These are preserved benchmark-reference errors, not independently annotated shuttle/point truth. The later terminal outside this64-frame decode is not newly visually adjudicated here.

## Reusable proposal and required controls

The evidence supports a **versioned observation/association design trial**, not an immediate production fix. Preserve raw model missingness separately from a source-supported `outside_fov` or `competing_branches` visibility hypothesis. Coordinates staynull while visibility is unknown; no trajectory, contact, named identity or winner is fabricated. Eligibility requires a previously qualified rally, credible observed outgoing boundary motion, consistent scene/camera and bounded history. Missingness must never create a start or an indefinite extension.

A moving-branch association provider must preserve independent raw alternatives and reject/abstain only with positive contradictory evidence. The current six-sample racket branch cannot be solved by the existing static-only rule or by a one-isolated-observation omission. Never promote0.1diagnostic peaks to accepted observations, select a convenient upper branch, or remove every near-racket point: genuine impacts occur near rackets. Visibility support should inform bounded end uncertainty without changing global gap/merge/model thresholds. Existing cuts, replays, invalid geometry and independently accepted terminal evidence must still end/reset incompatible state. Precise state semantics, causality/lookahead, provenance, source binding and cache versions require tests before integration.

Required contrastive controls before any trial are: G39[13427,13707) (do not invent onset from missing/weak/stationary evidence), G55[20061,20884) (invalid/reacquiring geometry and early missingness cannot earn qualified continuation), post-point pickup/walking and true rest, normal off-field objects, camera/cut/replay changes, coherent/ambiguous moving racket branches, real near-racket contacts, long flights without timely return, uncertain format and four-player doubles. Only existing metadata forG39/G55was read; no new control frames were decoded. Their reference intervals are development controls, not new physical labels. Establish reviewed visibility/branch/contact labels and match-disjoint holdouts before claiming an accuracy gain.

A new generic provider/schema could be justified after those controls, but no source-contract software defect or safe production policy is established by this one window. The immediate improvement is the diagnosis: do not report22visible-object false negatives, lower the detector threshold, extend global timeouts, force a rally merge, or claim D01 repaired G69. Full latest candidate Test1/Test2evaluation remains a separate unfinished gate.
