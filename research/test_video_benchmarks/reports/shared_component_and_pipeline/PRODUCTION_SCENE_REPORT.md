# Production continuation: scene continuity and image validity

**Current completed checkpoint:** two fresh full-video runs at source `85993259a3a2838881ed2b18658a07967058d191` and their own-cache replays are complete. The optional scene run observes13 content barriers, retains36/36 IoU-qualified rally matches and changes7 interval rows relative to the prior selected candidate. Its actual fresh mean IoU is0.8710256650 and end MAE10.472222frames. The older cached screen below is historical semantic evidence, with a different four-row boundary result; it is not the fresh result. Full completed-run and independent parity details are appended below. The scene policy remains experimental.

This investigation starts from clean `Benchmarking` at `181cb91`. The complete
handoff, current H01–H28 inventory, three repository instruction files and latest
final/root-cause/validation reports were read. Existing experiments, annotations,
source video, model assets and deployment are preserved. The orchestrator owns
integration, perception order, content epochs, codecs and semantic validity; this
specialist owns `perception/scene_change.py`, `scene.py` if needed, and scene tests.

## Mechanism reproduced before changes

The existing `CutDetector` compares a single downscaled HSV histogram and applies
the old minimum gap. Moving both players between places in the same camera can
preserve that histogram. Original frames10603→10604 and10769→10770 show this
physical-content discontinuity while the court remains stable. Existing traces
keep the shot/context unchanged. Estimated contacts10601 and10769 consume
post-edit outgoing samples, manufacturing large pre-edit acceleration; a temporal
context barrier is needed independently of whether court projection stays valid.
These frame identifiers are offline evidence only and never enter the observer.

The new distinction is **image-content continuity versus camera/court continuity**.
A possible same-view content change is a hypothesis. It does not itself authorize
camera recalibration, a player reset, a rally end, a merge, or a new coordinate.
Root integration can test an explicit content-epoch barrier without discarding a
valid court merely because participant content changed. The historical full reset
on an established histogram cut remains unchanged.

GT28 exposes a different coupling. Wide source frame13054 contains a visible
upper streak and raw accepted point(424.9612,109.9435),support0.8012695,main view,
cam_lost=false. GeometryREACQUIRING causes `_usable_camera_pose` and temporal
admission to reject the first two samples; VALID resumes13056. Point13055 is
(425.0493,109.2412), only0.708px away, followed by no admitted point until13112.
Separating image evidence from uncertain floor projection repairs provenance but
does not make those two slow samples satisfy the existing onset contract. No
boundary backdating or threshold reduction follows from this observation.

## Prespecified causal observer

`SceneContinuityDetector.observe` consumes current BGR pixels, immediately previous
source-frame target-court regions, and explicit current/previous view validity.
It stores a detached grayscale image and bounded per-episode score history.
Episode keys are opaque tracker provenance, never player identity. Fresh,
carried/tracker-only and unknown detector provenance remain explicit. Current or
future detector boxes cannot be used as past regions.

Each region uses sparse forward/backward Lucas–Kanade matching. Patch residual
and one-analysis-pixel forward/backward consistency remain separate numerical
fields. Robust two-image photometric normalization controls exposure changes.
The background is measured separately from participant regions. A possible
content change requires reliable background support, a joint foreground intensity
change, and an abnormal change against **each** region's own prior-only history.
One occluder does not alone establish a multi-region change. Unknown view,
features, adjacent context or sufficient history abstains. Four regions are
retained; inadequate four-region background evidence remains unknown.

The initial diagnostic screen is frozen before the full-source scan: width480,
two previous frame-pair scores, adaptive ratio3, discontinuity floor15/255,
background consistency≥0.5, at least6features and one-analysis-pixel FB tolerance.
These are uncalibrated exploratory controls, not physical cut probabilities.
No threshold is selected from the two target edit frames or rally F1.
Every returned `SceneChangeEvidence.authoritative` is false. Even a positive
pixel-change hypothesis can represent multi-region occlusion and needs a separate
policy and validation before becoming a temporal barrier.

## Primary alternatives and licensing

The official [PySceneDetect adaptive detector documentation](https://www.scenedetect.com/docs/latest/api/detectors.html)
uses rolling adjacent-frame content differences, with default ratio3 and floor15.
Its symmetric temporal window uses later frames and buffers the decision; blindly
copying that contract would violate an immediate causal claim. This observer uses
only prior scores, a different foreground LK metric, and makes no equivalence or
performance claim. The numerical defaults are a diagnostic starting point, not
validated transfer of an HSV calibration.

Primary implementation and BSD3-Clause license were pinned at commit
`c5ce29c73751e77139e838bd9ce9ab66a8e71a23`. The installed OpenCV5.0.0.93 distributions
declare Apache2.0, also checked against the official5.0.0 license. Raw source and
license hashes are under`prod_20261105_scene_initial_controls/external_sources/`.
No PySceneDetect dependency, external source code, new model or dataset was
installed/adopted. The existing OpenCV LK implementation remains the runtime.

## Executed controls and pending screen

Initial missing-module tests fail before the new feature exists. Eleven focused
tests then pass in1.54s: causal adjacency; stale ROI rejection; invalid view;
natural motion/pan; exposure; one-person occlusion; unknown features; opaque
four-region retention; reset/checkpoint/restore; detached source pixels; and an
abrupt two-region content change retained only as a hypothesis. The first stronger
four-region positive assertion fails because background correspondence is
insufficient; its log is preserved and the final control asserts truthful
abstention rather than reducing thresholds to force support. These software
controls do not establish real cut/occlusion/doubles accuracy.

`production_scene_probe.py` runs on all17268canonical frames using the exact
HLS `SegmentDecoder`, recorded prior-frame boxes/view context and the unchanged
histogram comparator. It reads no rally labels, runs no model, changes no event,
and saves bounded numerical evidence with source/cache/pixel provenance in
`prod_20261105_scene_fullscreen_v1/`. Source hashes and exact executing source
copies are preserved. The scan completed325.52seconds with unchanged executing
source:540unknown,16717measured and11positive-hypothesis frames. Every authority
flag remains false. No GPU or model inference occurred.

The initial weighted score detects10604but misses10770. At10770the first ROI has
FBconsistency0.878while its median patch residual is26.31. Multiplying by the
inconsistent fraction discounts this mismatch to3.21; the other ROI contributes
19.69and the mean11.45fails the unchanged15intensity floor. Reversible optical
flow is not appearance or identity confidence, so this multiplication cannot be
the sole scene-change signal. This negative result is retained; no floor is lowered.

`production_scene_raw_residual.py` tests one separate causal hypothesis on the
same measured source-pair evidence: retain raw median patch residual without the
FBdiscount, and give it its own prior-only adaptive history. All images, boxes,
photometric normalization, background/context gates and3×/15limits stay fixed.
It proposes10frames, adding10770and15579but losing4837,10023and15985. This is a
scalar counterfactual, not a new vision inference or proof that raw-only dominates.

The two independent hypotheses have a13-frame union:
2195,4837,7503,7857,8106,10023,10604,10770,11903,15579,15985,16446,17069.
All65unobscured original frames around these automatically proposed locations
were rendered in`prod_20261105_scene_auto_review/`, with four pre/post sheets.
Agent visual inspection finds abrupt participant jumps in all13pairs, usually
with independent venue/broadcast scoreboard jumps as well. None appears to be
ordinary continuous motion, exposure or a single occluder. These are diagnostic
reviews of automatic proposals, not independent cut labels or a recall denominator.
Eleven proposals were found beyond the two originally supplied edit locations.

Version`foreground-scene-hypothesis:v2`therefore exposes separate correspondence
and raw-appearance fields and histories, and ORs them only into a hypothesis.
It still returns authoritative=falseand retains all rejection/unknown information.
Two explicit regression tests fail onv1: reversible-but-different appearance is
suppressed, and the independent hypotheses cannot be inspected. All13focused
tests pass onv2in1.53seconds. Thresholds remain unchanged. The full canonical
pixelv2screen completed326.79seconds on all17268frames with unchanged executing
source,540unknown,16715measured and13hypotheses. Its exact frame set equals the
independent scalar union. Both priority edits are proposed and the entire515-frame
GT27fast-action control contains zero hypotheses. This is a measurement of this
source-bound screen, not independently labelled cut precision/recall. The
originalv1and scalar-counterfactual results remain immutable.

## Optional provider, bounded cache and lifecycle

`perception/content.py`adds a weightless provider registered explicitly in
`perception/components.py`as kind`content_continuity`, implementation
`foreground-content-continuity-v1`, contractversion1and output
`foreground-scene-hypothesis:v2`. Ordinary profiles select no content provider.
The default provider mode`diagnostic`cannot activate a barrier. The separately
requested experimental mode`barrier_hypothesis_v1`exposes`barrier_enabled=true`to
the integrating pipeline; the underlying evidence remains authoritative=false.
Policy mode is immutable after construction and affects the registry fingerprint.
The orchestrator owns any content-epoch change, player reset, pre-TrackNet order
and semantic consumer behavior. No scene/court camera reset is added here.

The provider accepts an independently replaceable structural port and declares
CPUbackend/no weights, formats singles/doubles/unknown, current/prior frame
requirements, image coordinates, uncertainty, bounded diagnostics and lifecycle.
Checkpoint/restore is owner-bound; a foreign/config-incompatible checkpoint has
an explicit failing pre-fix control. Close is idempotent and later observations
fail explicitly. The observer retains bounded frame/history state.

`scene_change_to_dict`and`scene_change_from_dict`validate the exact schema and
source basis, canonical frame identity, frame-1region provenance, finite numeric
values, fresh/carried/unknown detector flags, status/hypothesis consistency,
authority=falseand maximum8regions/8reasons/160-character provenance strings.
Unsupported fields/version, malformed boxes, future regions, boolean frame aliases,
nonfinite scores and unbounded payloads are rejected. No image or point array is
stored in scene telemetry. Root integration stores selected diagnostic frames and
hypotheses only, with independent content epochs on all frames.

Post-screen edits only bind checkpoint ownership and tighten source-key/portable
float guards, plus add the separate registry/codec adapter. The exact ASTs of
`_flow`, `observe`and`reset`match the frozen full-pixelv2executor. All33618input
boxes were already Python floats and every episode key meets the new bound.
`prod_20261105_scene_final_validation/`pins both source hashes, this difference
audit and final source snapshots. This is not represented as another vision run.

Latest focused validation:

-47observer/provider/codec controls pass;14observer cases include arithmetic,
  lifecycle and causal evidence;33provider/codec cases include registry injection,
  formats, fingerprints, strict bounds and unknown handling.
-62tests pass including existing perception selection/construction cleanup.
-72tests pass on the frozen integration interface, including court proposals,
  camera recovery, shuttle scene barriers, contact boundaries and the new controls.
  These scopes overlap and are not summed.

An intermediate expanded run had34passes/4failures because the integration owner
was temporarily passing an unsupported keyword from engine to shuttle processing.
The original failing log remains preserved; the frozen72-test rerun confirms the
owning integration fix. All changed/new specialist Python files pass Ruff. The
orchestrator owns the broader suite and full-pipeline effect evaluation.

## Independent pipeline integration controls

`test_content_pipeline_integration.py` exercises independent, controlled ports
and the real eight-frame TrackNet window construction, with a weightless forward
function. Nine controls pass in 2.23 seconds. They verify immediately previous
source-frame regions for two and four tracks, per-frame fresh/carried detector
provenance, continuity across a chunk seam, abstention after a seek gap, court and
camera retention across a same-camera content barrier, and the barrier being
established before any eight-frame network window is assembled. No constructed
network window crosses that barrier. With the optional provider absent, the old
shuttle-first order and shot inputs remain unchanged.

Two integration defects were demonstrated by failing controls before the owning
orchestrator fixed them. Diagnostic mode initially replaced ordinary shot keys
with composite keys even though no barrier was enabled. It now preserves the
original keys. Independently injected future-frame, authoritative or unsupported
source-basis scene evidence could initially affect context, or be silently
discarded without validation. Strict typed round-trip validation now runs before
epoch increments, player reset or shuttle inference. All three invalid-provider
controls fail before any shuttle window is consumed. The unchanged red logs and
the green rerun are under `prod_20261105_scene_initial_controls/`.

These tests establish ordering, ownership and schema contracts. Their controlled
pixel arrays do not establish sporting or real scene-change accuracy.

## Cached event-effect audit

The independently checked semantic counterfactuals use the historical fresh run's
own caches and the production event engine. They are not fresh perception runs:
changed network windows, player resets and detector cadence still require the
orchestrator's full pipeline validation. The scene inputs come from the frozen
causal all-source pixel screen, and rally labels enter only the offline comparison.
`prod_20261105_scene_final_validation/cached_effect_review.json` records the
source-bound comparison.

Association alone retains the exact 36 intervals and CSV bytes while reducing
live contacts from 457 to 453. Adding the explicit content barriers retains
36 TP, zero FP and zero FN; start MAE changes from 29.1389 to 28.2500 frames and
mean IoU from 0.867622 to 0.871347. End MAE worsens from 10.3333 to 10.4167 frames.
All other 32 rows remain exact. The four changed half-open intervals are:

| GT | Previous interval | Scene counterfactual | Boundary effect |
|---|---|---|---|
| 16 | [7006, 7499) | [7006, 7502) | End error +41 → +44; worsens 3 frames |
| 22 | [10578, 10737) | [10605, 10737) | Start error −29 → −2; improves 27 frames |
| 23 | [10769, 11085) | [10777, 11085) | Start error +36 → +44; worsens 8 frames |
| 34 | [15983, 16385) | [16000, 16385) | Start error −15 → +2; improves 13 absolute frames |

GT23's later start is consistent with refusing to derive a pre-edit contact from
post-edit motion. It remains a measured boundary regression relative to the
annotation and must not be hidden by the aggregate improvement. GT16's later end
also remains a regression. Neither result authorizes manually restoring the old
boundaries or crossing the content edit.

## Read-only association cross-review

The new association source was reviewed without edits. Initial concerns were
stale co-observation witnesses, net-displacement evidence from a single jump,
gap/reacquisition status and caller registration epochs. The integration owner
subsequently time-pruned samples, expired witnesses under the existing2-second
budget, required three adjacent bounded directionally coherent steps, and marked
diagnostic-unavailable gaps as reacquisition. Raw observation coordinates now stay
in analysis-image pixels with a separate association-coordinate basis. Changes of
camera registration reference still require an epoch boundary from the caller.
These source-level checks do not establish physical association accuracy.

Original frames around12553,12660,12679and12744were inspected in a74-frame exact-PTS
replay at`prod_20261105_association_source_review/`. Every flagged raw selection is
the same painted-T footprint. At12553a competing0.517component near(417.5,395)
continues the source-visible descending left track between12552and12554. At12660–63
the Tpeak wins while weaker near-player/flight hypotheses remain, including a
0.543alternative at12662. No physical contact time is assigned. At12679the Tpeak
replaces a previous upper-edge observation, with a0.402upper alternative; the
out-of-view position remains unknown. At12744the Tis the sole retained component
above0.1, so there is no justified replacement coordinate. These examples support
retaining explicit ambiguity, not inventing a track or declaring a verified landing.

## Disposition

The causal observer, bounded codec and optional injectable provider are ready for
the orchestrator's explicit experimental content-barrier test. No default or
production promotion follows from source-pair inspection, synthetic tests or an
unreviewed cut-count. Fresh full-pipeline perception feedback, all-rally comparisons,
real multiregion occlusion/fast-motion controls and independently reviewed
match-disjoint footage remain required before a stronger accuracy claim.

## Completed fresh-source and own-cache reconciliation

Fresh `prod_20261105_fresh_association_v1` and `prod_20261105_fresh_association_scene_v1` completed all17,268 frames at source8599325. Each uses its own288 newly inferred cache20 segments. Both retain36TP/0FP/0FN under the unchanged evaluator. Association-only retains exact prior selected intervals, mean IoU0.8676224676, start MAE29.138889frames and end MAE10.333333frames. The scene run has mean IoU0.8710256650, start MAE28.25 and end MAE10.472222. Its small aggregate start improvement does not conceal GT16's worse end or GT23's later start.

Compared with the prior selected fresh candidate, the actual scene inference changes these7 rows; the other29 interval pairs remain exact:

| GT | Prior selected interval | Actual fresh scene interval |
|---|---|---|
|16|[7006,7499)|[7006,7502)|
|17|[7535,7731)|[7537,7731)|
|19|[8110,8627)|[8111,8627)|
|21|[10250,10539)|[10249,10538)|
|22|[10578,10737)|[10605,10738)|
|23|[10769,11085)|[10775,11085)|
|34|[15983,16385)|[16000,16385)|

The older cached scene experiment changed4rows versus prior selected, while fresh changes7. Fresh versus that older cached scene result differs in5rows (GT17start+2,GT19start+1,GT21start/end−1/−1,GT22end+1,GT23start−2), with31 rows exact. That comparison uses different perception streams; scene-induced model-window/background/pose/detector context can feed back into observations. It must not be attributed to a new threshold or misreported as replay nondeterminism. The root-boundary workstream retains the detailed source/cache and stage evidence.

Own-cache source digests independently verify13 content-epoch increments at2195,4837,7503,7857,8106,10023,10604,10770,11903,15579,15985,16446,17069. Association-only has0 content increments. Observations at10604/10770 support the previously source-inspected same-camera edits;13 barriers do not establish scene precision/recall, and the earlier source inspection is diagnostic rather than an independently reviewed exhaustive cut label set.

The completed scene run has446live contacts/strokes versus453association-only. Physical policy2 produces82probable/136ambiguous/228insufficient and **0automatic confirmed** scene contacts; a reduced count is not labelled physical precision. The T-to-flight contact12766 is absent in both runs, whose raw modelT is retained as `ambiguous/static_candidate` with no selected physical coordinate. Typed cue-frame freshness and cache provenance independently audit without violations.

Independent final semantic parity evidence `prod_20261105_association_scene_replay_parity_audit_v4` validates all93 executed-source hashes and288 cache digests,17,268 ordered steps, final flush/frontier17267, all446contact/stroke numerical and physical/classification payloads, and all36 rally interval/reason payloads. The corresponding association-only audit likewise reproduces453 contacts/strokes and36 interval/reason payloads. It reads no annotations and invokes no inference. The remaining full-export differences are explained session-bound tracker namespaces and the replay's explicit recorded-format producer provenance; raw differences are retained, not erased. These are cached semantic replays of finished inference, not fresh GPU repetitions.

This completes the previously pending full-pipeline/replay check on the exposed development video. It does not complete independent scene/contact/trajectory/generalization validation. No default or production promotion is recommended from this scene result alone. Failed external-stress v1 runs are preserved as runtime failures and have not been scored as completed inference.
