# Confirmed blockwise semantic-to-perception cadence feedback

The sparse current observations during visible Test2 play at25689–25736are caused by an actual blockwise scheduling decision from the delayed rally FSM. The current run is IDLE at the exact state snapshot used to acquire frames25680–25739; the original run is ENDING. The same unchanged profile therefore gives current pose stride6/detector stride6, versus original pose stride1/detector stride2, for that entire60-frame packet. This is confirmed from source contracts, completed packet metadata and parity-bound full FSM traces.

It is not a model failure on frames where no model ran, excluded geometry, a changed stride threshold, or a proof that all current boxes are wrong. No new inference, engine replay, code/profile edit or contact promotion was performed.

## Exact execution contract

The actual upload session records60frames per HLS/analysis segment in both runs. This differs from any model microbatch parameter; source `SessionRunner` decodes a whole segment, calls `sport.perceive`, and only afterward calls `sport.ingest`.

`BadmintonSession.perceive` passes `self.in_play` once to `BadmintonPerception.process`. That property is exactly `engine.fsm.state is not IDLE`; neither general activity nor an uncertainty/acquisition hint participates. `pipeline.process` chooses detector/pose rates before its per-frame loop. An extra scene-layout probe can add detector acquisition, but does not change the packet's selected pose stride.

After appending an entire packet, `_ingest_chunk` advances the temporal engine only through `last_frame - max(lookahead40, round(0.2*fps)+5)`. At30fps the40-frame lookahead dominates. Before acquiring a chunk beginning atF, the latest folded FSM frame is thereforeF−41, even though perception has already coveredF−1. This is the deliberate bounded semantic context contract, with a real sampling feedback cost.

[Boundary-state proof](boundary_states.json), [complete packet cadence](packet_cadence.json), [600arm/frame cadence rows](frame_cadence.csv), [source bindings](source_binding.json), [actual FSM transitions](actual_fsm_transitions.json).

## What happened in this sequence

| Next acquired source frames | Last folded source frame | Original state | Current state | Original/current pose stride | Original/current detector-observed frames |
|---|---:|---|---|---|---|
|25500–25559|25459|IDLE|IDLE|6 /6|10 /11|
|25560–25619|25519|IDLE|IDLE|6 /6|10 /11|
|25620–25679|25579|IDLE|IDLE|6 /6|10 /10|
|25680–25739|25639|ENDING(start25626)|IDLE|1 /6|30 /11|
|25740–25799|25699|IN_PLAY(start25650)|IN_PLAY(start25650)|1 /1|30 /30|

The extra current detector frames are explicit scene-acquisition calls, not a different profile. In25680–25739current has10normal stride6observations plus25705off-cadence acquisition. Original supplies120fresh keypoint payload rows for two people over60frames; current supplies20. A fresh keypoint payload count is execution coverage, not pose accuracy. These frames are main/VALID, so absent current pose is actual sparse scheduling, not suppression by unavailable geometry.

Both arms recognize the same observed-motion start25650when processing25652: three adjacent moving observations above the unchanged start threshold. They do so only after acquisition of the whole packet through25739. At that point current cannot retroactively improve the already completed earlier observations. Its next packet25740–25799uses the dense rate. The source review documents visible near-blue overhead/lateral play and carried-box lag, including25720/21maximum common-pair reference-error increase and class abstention at25736. [Sealed194-frame visual review](../../regression_tests/pre_test03_contract_v1/visual_test02_pending_v2_batch_03_04_review_v1/REPORT.md).

## Upstream divergence: cancellation, not simply a delayed first start

The current source-confirmed edit25521creates a new content epoch and clears incompatible state. The pipeline passes combined shot/content epoch keys to TrackNet; its background reservoir and temporal windows are keyed by those values. This observed-context reset is required and must not be undone simply to reproduce a previous benchmark number.

Retained diagnostics25577–25606show different exact background hashes:

- Original: `0a429a93ef1fbc60114e089e0e572b9df6e9ac7883a97c176774e89f8ab758e5`.
- Current: `153e68ac9387de9e9055d6e5b9ec52f2d6324eccf9bf23a2bab32f4be74e6099`.

At25577original peak0.434814is below unchanged0.5threshold; current peak0.545898is accepted. The current earlier provisional contact start25580actually precedes original25582. Thus a simple narrative of “background reset delayed all shuttle motion” is false here.

The original provisional25582interval cancels25622, then a selected contact opens25626. It reaches ENDING by25635and is still ENDING at25639. Current starts25580, reopens with a candidate25612, subsequently closes and cancels25635, and is IDLE at25639. No current25626contact counterpart opens another event. At25639original observed speed4.220201and current2.816400also differ. These are the actual state differences the scheduling property consumes. The later shared motion start25650does not arrive soon enough to alter acquisition of the packet containing it.

[Literal raw/selected comparison](raw_readout_comparison.json) records actual equality counts. All accepted/null raw coordinates/support through25559match, but both missing records do not establish equal hidden heatmaps. Subsequent raw observations differ; their existence, background digests and state changes establish context sensitivity. This review did not run an isolated background-only or D01-only neural counterfactual. The broader before/current intervention contains scene/perception and temporal changes, so exact attribution of each upstream candidate difference to background alone is **inferred**, not proven by these comparisons.

## General activity does not currently solve this window

The independent `ActivityTracker` does not feed `Session.in_play`. Its emitted interval is UNKNOWN from25495through25710in the original, and through25713current. ACTIVE_PLAYbegins25711/25714respectively, well after the state snapshot governing acquisition25680. Therefore merely replacing the FSM bit with the existing general activity state would not recover this exact packet. [Observed activity intervals](activity_intervals.json).

The pipeline already has independent image continuity and off-cadence detector-probe boundaries. Those acquire fresh evidence without asserting a rally or point, but currently address scene change only. No existing typed request was found for current unfinalized moving-projectile/player activity to raise sampling demand during an idle-looking semantic snapshot. Conversely, “the semantic state is IDLE” does not independently establish observed physical inactivity.

## Scientific and implementation limits

This is a verified feedback mechanism and coverage tradeoff in the selected default composition, rather than a contradiction of the current documented `in_play` implementation. It can make semantic uncertainty reduce the fresh evidence later needed to resolve contact/hitter/class uncertainty. Current25736unknownis appropriately reported given the evidence actually acquired; inventing a fresh player or class would hide the upstream issue.

A future controlled sampling-demand policy should remain separate from accepted rally, physical contact, identity, team or score state. It should consume explicit recent observed/unknown evidence through replaceable sport/plugin stage contracts and retain reason/provenance. The existing independent activity and acquisition components are starting points; an additional parallel rally engine or ground-truth-specific hold is not warranted.

Before any policy adoption, measure actual model latency/resource cost and source-bound coverage for held/pickup/walking, ordinary off-field movement, aliases, stale tracks, cuts/replays, featureless or missing geometry, singles, doubles and uncertain format. Preserve the current profile thresholds and compare complete Test1/Test2 outputs. An automatically prolonged in-play bit, a copied lookahead FSM, altered gap timeout, or a new delay fitted to this source interval is not justified. Reducing segment length would also alter neural windows/background batching and cannot be treated as a free numerical no-op.

## Reproducibility and failed assumption

Actual native2418source files were matched to their recorded producer plan. The original plan truthfully records commita53f95fwith a dirty engine patch; its dirty engine SHA is4068e87f62b52b81505408bac2c617d0628d16c072625e47f52c78b4682be3d2. The first read-only audit attempt incorrectly assumed that every recorded original file must equal the clean recorded commit blob and failed before publishing outputs. [Preserved failed attempt](failed_attempt_01/failure.json).

The retry binds the actual archived source bytes with the exact recorded SHA, also identical to the laterdacc05eGit blob. It preserves the originala53+dirty metadata; no original ROOT, plan, report, cache or source record is rewritten. Other reviewed original source blobs match their actual recorded hashes directly. Both saved full semantic traces retain their own complete-worker parity proofs. Physical ground truth remains null; source observations and model/FSM hypotheses are separate.
