# G69 current perception prefix27290–27400

This read-only snapshot contains published cache rows only. It is not a finished
run or an independently annotated shuttle trajectory. No live event database was
opened, no observation was replaced and no rally terminal/FSM result is claimed
before the completed source-bound semantic trace is available.

## Raw absence precedes association

Current raw provider coordinates are present through27325, absent on
**27326–27347 inclusive (22 frames)**, then reacquired at27348. Every missing row
has association status`missing`, association decision`unknown`, reason
`no_accepted_raw_observation`, and no selected coordinate. This is not a case of
the association stage rejecting a currently accepted raw coordinate.

Across the22-frame missing span, the candidate catalogue retains15 candidates
over12 frames;10 frames have no retained candidate. All15 candidate peaks are
below the unchanged0.5 inference threshold, with maximum support0.220703125.
All retained candidate peaks are allowed by the mask. Thus the recorded
candidate evidence supports a provider/threshold coverage limitation, not an
established mask rejection or association veto. No retained candidates does not
mean there was literally no heatmap response below the retention floor.

Main view, VALID calibration, content epoch33 and two returned person tracks
persist throughout the missing span. Geometry invalidation or an observed scene
barrier does not explain this particular raw gap. Detailed passive heatmap
diagnostics explicitly say`below_threshold` at27326/27327; later full tensors
are not retained and their absent detailed reason fields must not be invented.

## Reacquisition and competing branch

| Frame | Raw/selected coordinate in720p image | Machine evidence |
|---|---|---|
|27325|(788.869,56.927)|Observed/tracked, support0.635254|
|27326–27347|Unavailable|No accepted raw observation|
|27348|(784.968,429.917)|Observed/reacquisition, support0.674805|
|27349|(789.138,433.504)|Observed/tracked, support0.668457|
|27353|(806.018,449.495)|Lower branch selected, support0.685059; upper candidate near855,2.5 has support0.117065|
|27354|(855.600,6.573)|Upper branch selected, support0.752441; lower candidate near814,456 remains above threshold at0.685303|
|27355|(855.291,24.662)|Upper branch continues|

The association record says`fresh_selection_retained` for these selected
coordinates. The first reacquisition is27348 in this run, whereas the original
historical record described27349. That one-frame difference alone is not a
completed rally-boundary improvement and must not be substituted into historical
metrics.

The abrupt selected-branch change at27354 and simultaneous above-threshold lower
candidate establish a concrete raw-selection ambiguity to investigate. They do
not establish the physical shuttle position. In particular, selecting the earlier
upper0.117 candidate merely to extend a high-flight hypothesis would violate the
unchanged decoder threshold and invent evidence.

## Source review

Exact original-source frames27320/27335/27345/27348/27355 were decoded with one
thread and retained with rational PTS, original pixel hashes and720p panel hashes
under `source_panels/`. Original-source27325/27349 panels from the annotation
review were reused; current cache overlays preserve their source hashes. The
additional overlay receipt is separate from the immutable prefix snapshot.

The selected source images show active player movements including overhead
preparation/high-clear response, with displayed current16:16 and no visible edit
between these samples. At27348–27353 the selected lower coordinate lies around
the near blue athlete's racket/head/hand region: this supports a **probable
equipment distractor** interpretation, not a newly adjudicated per-frame shuttle
label. The later upper selected point and continued player action need a fuller
motion-window review before physical contact or visibility can be certified.

Source-supported ongoing activity makes the gap worth investigating; it does not
permit fabricating an interpolated trajectory, globally extending timeouts or
unconditionally merging intervals. The root orchestrator will inspect actual
completed FSM/contact/cancellation events and final predictions separately.

## Reproducibility and next gate

`prefix_snapshot.json` retains all111 frames27290–27400, complete source-bound
association candidates/reasons, person freshness, calibration/view/epochs, OCR
readouts and consumed-cache hashes. OCR27310/27340/27370/27400 reads16:16; this is
technical text agreement, not an accepted point/identity label.

The window must be bound against the genuine completed catalogue together with
the other five snapshots. Until that separate guard succeeds, all findings here
remain prefix diagnostics. No production change or threshold experiment was
performed.
