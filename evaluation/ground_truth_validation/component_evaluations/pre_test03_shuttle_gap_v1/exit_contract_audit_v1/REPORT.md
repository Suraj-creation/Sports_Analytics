# Exit-recovery contract audit: singleton versus contiguous lower branch

**No new singleton-handling defect was reproduced in the configured pipeline.** The primitive first-return helper rejects a lower first return, but the selected `rally-evidence-tracklets-v1` provider already adds a bounded singleton-association alternative. It can leave one isolated observation unassociated inside a continuity proof without deleting, relabelling or replacing that raw observation. G69's six consecutive lower observations exceed that explicit contract.

This is a model-free code/contract audit. No production, profile, thresholds, model, annotation, historical report or active candidate was changed. No additional video frames were decoded. Physical ground truth remains null; counterfactual fixture results are not production predictions or benchmark improvements.

## Actual configured path

The completed Test 2 `improved_v1` profile selects `rally-evidence-tracklets-v1`, with exit recovery enabled, curve recovery disabled and rally reconstruction disabled. Its registry factory constructs `_TrackletEvidenceRally`, which satisfies `AssociatedExitRallySegmentation`. The engine therefore calls its `exit_return_support()` port rather than stopping at the legacy primitive helper.

That method calls the existing `image_exit_return_tracklet_support()`:

1. Try the unchanged observed top-exit/return proof.
2. If it fails, consider only an observation with **no observed neighbour on either side**. Exactly one eligible singleton is required.
3. Make a private copy of the visibility mask for this alternative proof and recheck the same top-band, coherent-motion, temporal-context and gap constraints. Original coordinates, visibility and support remain intact.
4. Require the rally to have met its existing minimum duration **before the loss**. Waiting through missingness cannot earn qualification or create an idle start.

The existing budgets remain two seconds, the top 10% image band, five observed anchors on each side and existing motion limits. This feature predates the current investigation: the unchanged source-bound Test 1 singleton regression and the provider's existing negative controls already exercise it. Reimplementing that algorithm would duplicate resolved work.

Seven relevant source files copied in [source binding](input_binding.json) match the completed own-parity replay's executed core hashes. The numerical probe additionally verifies **44 actually imported component modules** against that recorded snapshot. [Proof readouts](proof_readouts.json) retain the selected implementation, complete profile description and all outcomes. Tests instantiate the same provider class with the relevant exit/reconstruction/curve options; they do not reconstruct the full semantic engine or claim a new pipeline replay.

## Focused results

[Final test log](focused_run02.log) and [JUnit result](junit_run02.xml): **35 passed, one unrelated contact-attribution test deselected**. This comprises 15 new G69-derived contract cases and 20 unchanged existing exit/provider cases. The new [fixture tests](test_g69_exit_contract.py) read the preserved 64-frame cache window; the nine historical source/test copies remain unchanged. The first successful run and its executed test bytes are also preserved. A subsequent import-order-only correction was followed by the same 35 passing cases. Both new helpers pass Ruff.

| Input or control | Actual existing-provider result |
|---|---|
| Unmodified G69: lower observations 27348–27353 | Unsupported: `exactly_one_isolated_alternative_required`; no ignored frame. |
| Synthetic availability variant: retain only the lower observation at 27348, followed by the original upper observations from 27354 | Supported: `single_unassociated_observation`; proof gap `[27326,27354)`, ignored frame 27348, before anchors 27321–27325, after anchors 27354–27358. |
| Same synthetic singleton variant without available upper-return anchors, then recomputed with them | Initially unsupported, subsequently supported. `last_exit_support` updates; there is no sticky negative cache. |
| Current frame is the observed lower point 27348 | Unsupported for a missingness proof; the raw point remains observed. |
| Two, three or six consecutive lower observations | Unsupported. No whole lower tracklet is silently removed. |
| Idle or insufficiently mature event | Unsupported: `event_not_qualified_before_loss`. |
| Cut, replay, absent upper return, reconstructed upper return or wrong outgoing direction | Unsupported. |
| Existing four-player fixture | All four player series retained; structural contract only, not real doubles accuracy. |

The one-point variant is explicitly synthetic: five original accepted lower samples are made unavailable **inside a test fixture only**. Their actual source/cache record remains untouched. This demonstrates an already implemented contract; it does not establish that those real observations should be discarded or that this variant fixes G69.

## Refinement of the earlier source diagnosis

The [sealed parent diagnosis](../REPORT.md) correctly identifies the lower first return as invalid for the primitive top-band proof. The complete provider path is more specific: it then attempts the existing singleton alternative and refuses G69 because the lower branch contains adjacent observations. Its final reason is `exactly_one_isolated_alternative_required`, not a permanent latch caused by the first lower point.

In G69, the observed lower branch is coherent as model output and follows the visible racket in the reviewed pixels. That source interpretation is diagnostic, not a reviewed physical shuttle label. The current provider intentionally refuses to treat two adjacent floor/static observations as a removable singleton. The same conservative budget also refuses a longer moving-racket branch. Extending the rule would change its declared association policy and require independent evidence; it is not a correction to a broken singleton implementation.

The provider proof is recomputed for the available window, but a state machine cannot retroactively withdraw a result already published under its causal budget. Insufficient future evidence and completed publication are separate issues from a sticky first-return failure. The existing component explicitly declares available-window scope. These tests do not establish a safe change to live lookahead, publication or merge behavior.

## Decision and remaining controls

**Do not add another singleton recovery algorithm or enable the optional curve path for this case.** Retain the existing implementation and its qualification/negative controls. An observability improvement could expose the already available `last_exit_support` reason in future diagnostics so a primitive top-band failure is distinguishable from final provider abstention; this would be a separately versioned reporting change, not an accuracy fix.

The unresolved problem is positive evidence for association and visibility through a **multi-sample** competing branch. A future trial must preserve every raw point/support and uncertainty, and distinguish a moving racket distractor from a real shuttle near a racket. Neither geometry alone nor the desire to reconnect G69 establishes which physical object a raw sample represents. No blanket lower-point/body mask, threshold reduction, global timeout extension, forced merge, new coordinate or automatic winner is proposed.

Before such a trial, require source-reviewed, match-disjoint controls for G39's onset/weak-stationary evidence, G55's geometry reacquisition and early missingness, post-point pickup and true rest, ordinary off-field objects, legitimate near-racket returns/contacts, cuts/replays/camera changes, missing or reconstructed upper evidence, long flights without return, and singles/four-player doubles with unknown format. Current synthetic controls cover mechanics, not those videos' physical labels. No new G39/G55 or doubles footage was decoded or declared correct in this audit.

Full current Test 1/Test 2 regression and candidate acceptance remain the orchestrator's separate gate. This audit establishes deliberate bounded conservatism and a remaining capability limitation, not an approved production fix or measured physical accuracy gain.
