# Actual-pixel low-feature contract confirmation

**Confirmed on real current-run input: frame1510 reproduces the old validator’s defect; the fixed validator accepts the entire closed1560-frame prefix.** This is a bounded scene-component diagnostic of commit `2418ab8`, not a completed video evaluation and not literal recovery of the old process’s unavailable fatal frame.

The probe reads only the current run’s26 closed cache chunks covering0–1559, and the old failed run’s25 closed chunks covering0–1499. All1500 overlapping foreground records, stored content-evidence values including nulls, and replay/shot flags match exactly. The current native observer was then replayed chronologically using exact proxy pixels and the actual preceding current-run foreground regions and flags. It reproduced all343 retained non-null content records exactly. There are no substituted future boxes or assumed future replay flags in this probe. [Receipt](receipt.json), [overlap rows](old_current_overlap_comparison.json), [observer parity](current_retained_cc_parity.json).

The scene observer implementation is byte-identical between failed and fixed source. Its actual measurements are passed separately to the unchanged historical validator loaded from the preserved old source and to the fixed native validator. No checkpoint/model is loaded, no neural inference is performed, and no pipeline/evaluator source is edited.

|Actual current-run measurement at1510|Value|
|---|---:|
|Region|court-origin:4|
|Tracked features|5|
|Raw median patch residual|0.009708049707114697|
|Prior appearance mean|1.526803508400917|
|Supported appearance adaptive ratio|Unknown/null|
|Old validator|Rejects legitimate unknown|
|Fixed validator|Accepts legitimate unknown|

The raw residual is finite even though the current feature support is insufficient. The producer therefore emits an unknown ratio. The old validator incorrectly demands a numeric ratio from that residual and previous mean. The fixed validator preserves the residual and unknown supported value, with no threshold or tolerance change. The old validator rejects frame1510 only in this bounded current-input replay; the fixed validator accepts all1560 frames. [Exact counterfactual rejection](old_validator_current_input_rejections.json), [raw observer measurements](observer_raw_rows.jsonl).

A separate controlled mutation sets the unsupported ratio to its numerically consistent value0.006358414592118883. The old validator accepts that forged low-feature number; the fixed validator rejects it. This is a contract test, not a claim that the source video contained a forged observation or that the small ratio would establish a scene reset. [Forgery control](real_measurement_forgery_control.json).

Exact source PNGs1508–1511, source PTS/timebase, decoded BGR hashes and PNG hashes are preserved in [source evidence](source_evidence/) and [frame metadata](source_frames.json). Frame1510 was visually inspected as an ordinary court-view diagnostic; no contact, identity or outcome ground truth was inferred from it.

The actual current full pipeline has written the previously failing1500–1559 chunk. Its full17268-frame execution, all-reference evaluation, semantic parity and acceptance review remain separate pending work. The old precise fatal frame remains unknown in the sealed original failure record;1510 is explicitly an **old-validator/current-input counterfactual**. No precision, recall, F1, player/shuttle accuracy or generalisation claim is produced here. The previous sealed failure report and historical benchmark records are unchanged.
