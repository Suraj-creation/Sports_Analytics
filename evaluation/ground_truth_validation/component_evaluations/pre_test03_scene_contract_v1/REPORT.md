# V4 low-feature evidence contract failure

**Confirmed code defect; narrow fix passes focused tests. Full fresh validation remains pending.** The failed Test1 run is preserved as an incomplete runtime result, with1500 cached frames0–1499. It has no completed evaluation matrix and supports no precision/recall/F1 or physical accuracy claim.

The raw optical-flow observer deliberately separates a finite patch residual from supported adaptive evidence. With fewer than six features, it retains the raw `median_patch_error` and may retain the prior appearance mean, while emitting `appearance_adaptive_ratio=None` and `discontinuity=None`. Those unknown supported values clear the corresponding history; fresh observations must rebuild it.

The new V4 validator mistakenly reconstructed appearance eligibility from the raw finite patch error alone. When an earlier mean existed, it demanded a finite ratio despite insufficient current features. This rejected a legitimate unknown observation and stopped perception serialization. Conversely, the old validator could accept a fabricated finite appearance ratio at five features because its arithmetic was numerically consistent even though feature support was insufficient.

The root-owned fix in commit `2418ab8` makes the arithmetic use the same feature eligibility as the actual producer. It preserves raw residual telemetry and legitimate unknowns, and explicitly rejects finite supported discontinuity/adaptive/appearance values when features are below six. Six-feature arithmetic and thresholds remain unchanged; this is not a looser ratio tolerance, model change or evaluation adjustment. [Exact source versions](source_contract_versions.json).

## Reproduction and source-bound evidence

- The actual observer/control regression tests fail **6 cases and pass1** against the untouched failed `a146953` source. This includes valid unknown observations at0/1/5 features and the forged-ratio admission weakness. [RED log](old_actual_source_RED.log).
- The same seven tests pass against the root’s fixed native source. They retain the six-feature boundary, reject forged supported evidence, and verify history clearing/rebuilding. [GREEN log](fixed_actual_source_GREEN.log), [portable test source](test_scene_low_feature_evidence.py).
- A chronological CPU scene-component replay decoded the exact retained proxy, used the actual recorded preceding foreground regions and view/cut flags for frames0–1499, and replayed through1500. It reproduced **343/343 retained raw observer records exactly**, including channel measurements, histories, witness keys and status. [Parity rows](retained_observer_parity.json), [source replay receipt](source_replay_receipt.json).
- There was **no validation failure through frame1500** in that source probe. Frame1500 uses actual preceding-frame1499 regions and an explicitly declared non-replay current-view assumption. No future foreground/player observations were fabricated. [Raw observer rows](source_reconstructed_raw.jsonl), [source PNG/PTS/pixel hashes](source_frames.json), [source images](source_evidence/).

The exact fatal frame is therefore **unavailable** from retained output. The failing unreturned chunk spans1500–1559; its current player/foreground updates were lost with the failed process. The1500 cached frames do not establish that1500 itself failed. We did not substitute historical baseline boxes for later current-run boxes: cadence differences make that substitution insufficiently exact. No new neural inference was performed to fill the gap. The fixed full fresh run must demonstrate progress beyond the failed chunk and eventually satisfy all normal completion/evaluation guards.

The original failure log, preflight, plan and parent receipt are preserved under [preserved_failed_run/](preserved_failed_run/). The source video, proxy, partial segment bytes, original source files, ground truth and historical benchmark reports were not modified. The component probe verifies source identity and partial extent without pretending to pass a completed-run guard.

## Rejected secondary hypothesis

The proposed same-key history leak across a content reset is **not present in the inspected implementation**. `CourtForegroundMemory.reset()` clears observations but preserves `_next`; `PlayerPerception.on_cut()` retains the same memory object. A contiguous-frame lifecycle control produced keys0/1 before reset and2/3 after reset. The observer had no old means for the new keys and rebuilt history normally. [Lifecycle control](key_lifecycle_control.json).

An initial lifecycle probe skipped an observer frame and was unsuitable as proof of history isolation. It is retained as `initial_nonadjacent_key_lifecycle_control.json`; the final cited control uses consecutive observer frames0–6. No speculative lifecycle fix was added.

This report concerns a runtime/evidence contract, not sporting ground truth. All physical metrics remain unavailable. The separate acceptance-review preparation was paused when the full run failed; original/v2 reports remain untouched.
