# Additional authorized local data discovery — 5 November 2026

Related local badminton data can be investigated and evaluated within the user's existing mission. An absent per-recording rights checkbox is not a new permission requirement for this read-only analysis. Unknown redistribution/training rights remain factual provenance limits; genuine held-out seals and unrelated sources remain protected. The earlier12-entry metadata snapshot was a restricted inventory, not an exhaustive statement that no other usable references exist locally.

**Available now:** the complete Test7 recording and a legacy documented hand-labelled31-rally primary CSV; three continuous prepared clips with published human shot anchors/classes (India85, Denmark39, men's doubles45). These are previously exposed development/comparison materials. They support transparently qualified frozen-profile stress/reference-agreement evaluation; none is a new blind test. FineBadminton0044/0046 original media was not found in the current working data/recovery/research tree or known retired checkout paths. No download or archive recovery was attempted.

This discovery reads relevant provenance, import/evaluation code, Git history, filenames, headers, exposed-reference metadata and existing Test1 diagnostic JPEGs. It hashes the Test7 source, three small proxies and relevant annotation/manifest files. Container-header FFprobe reads establish current media properties; no frames are newly decoded and no model, encode, GPU job, service or deployment is started. No genuine sealed-test label values are opened. Original media, annotations, sessions, published taxonomy and historical roles remain untouched. The integration owner controls new sessions/jobs and readiness-manifest changes.

## Part2: human references and generated artifacts are different families

The user supplied Part2 through the earlier task. `docs/testing/task2/progress-20261028.md` records60 transferred annotation/reference files verified against the Windows originals. Commit `3cc74e241b00f98beb25e76cc109f492d29248c4` first adds all eight dataset directories and four reference DOCX documents; Git history does not provide a named annotator, row-level review or independent adjudication trail.

`legacy/pipeline/docs/10_evaluation.md` explicitly describes the eight primary `<match>.csv` tables as hand-labelled ground truth. The reference quick guide and model history likewise describe eight hand-labelled matches, previously reused across several model experiments. That is **documented legacy human origin**, not independently reverified label quality or proof of an untouched test split.

| File family | Documented/observed origin | Appropriate use |
| --- | --- | --- |
| `<match>.csv` | Hand-labelled rally times, winner/reason, one ball-type entry and scores; eight columns | Coarse legacy rally-reference agreement, with known version/identity/precision limits. Not exhaustive per-shot/contact/identity labels. |
| `<match>_rally.csv`, `_T.csv`, `_T4.csv` | Legacy `analysis/detect_rallies.py` writes this seven-column family; counts can differ from primary human rows | Model proposal/variant comparison unless an individual reviewed origin is documented. Do not infer human review from suffix or numeric precision. |
| `*_ball_filled.csv` | TrackNet observations plus filling/interpolation | Generated perception, not independent visibility/location truth. |
| `player_detections.csv` | Person detector position-slot outputs | Generated boxes, not four-person identity GT. |
| `win_predictions.csv` | RF/CNN/rule prediction fields | Earlier model estimates, not independent winner/score truth. |

The current task explicitly designates `Part2/dataset/Test1_Full/Test1_Full_rally.csv` as the immutable Test1 benchmark reference. That user-defined contract remains unchanged; family-level provenance is not permission to replace or relabel it. For an additional Test7 evaluation, select its primary `Test7_Full.csv`, not the30-row generated `_rally.csv`.

| Recording | Primary nonblank rally rows | Generated `_rally.csv` rows | Current full source in inspected project data |
| --- | ---: | ---: | --- |
| Test1 |36|36|Available, preserved benchmark input|
| Test2 |75|73|Not found|
| Test3 |22|19|Not found|
| Test4 |45|41|Not found|
| Test6 |42|42|Not found|
| Test7 |31|30|Available and hash verified|
| Test9 |78|82|Not found|
| Test10 |96|93|Not found|

Test9/Test10 primary files also contain blank records; their structural inventory is recorded rather than silently treating blanks as labelled rallies. Test5 exists in the historical video download manifest but has no Part2 annotation directory; Test8 is not listed there. Historical Windows download success does not establish current server availability. No absent source is declared inaccessible merely because its rights attestation is unset.

## Test7: immediately usable coarse-reference stress recording

- Source: `data/task2-review/Test7_Full.mp4`, **664,899,136 bytes**; newly verified SHA256 `1ad1eac44150a0a23e2bad1f3d4204bd41f2d257ff6b35156234d38cfa2b9d9c`.
- Current headers: H.264,1920×1080,30/1 FPS,10,725 frames,357.5 seconds; source start0. The encoder tag is Clipchamp. Header inspection is not a complete source-to-proxy correspondence measurement.
- Primary reference: `Part2/dataset/Test7_Full/Test7_Full.csv`, SHA256 `5f1ebabcc0a66dae579bf7ad35ddc48a97e88d1277cc7afa5e7d369a3fcbd9ea`,31 nonblank rows with seconds-valued start/end fields.
- Preserve conflicting legacy reference separately: `legacy/pipeline/vjepa_setup/dataset/labels/Test7_Full.csv`, SHA256 `f4eb326b2021882ec99f33bb439e2aac43bb4f67f124c72f379c654910fc1f1e`.

Historical visual review identifies Tai Tzu-ying and Carolina Marín and an edited broadcast timeline. The opening primary/legacy winner labels disagree despite matching time and score fields, and A/B identity convention remains unresolved. This does not prevent coarse boundary-reference agreement, but excludes reliable winner/score/contact/shot conclusions. Whole-second annotation conventions do not support claiming one-frame precision.

**Match independence from Test1 is unproved.** Different filenames/digests establish different recording bytes, not different matches. A newly inspected existing Test1 source image at12766 visibly reads `AN S.Y.` / `INTANON`; the integration owner also inspected10769/10770. Historical Test7 review reports Tai/Marín. That is bounded evidence of different competitors in those reviewed windows, not an independent identity seal for every edited frame of either recording. Test7 may proceed as an exposed-recording stress test; whole-recording match-disjointness remains unproved. No name or match ID is injected into inference.

The evaluation adapter should preserve raw reference bytes, declare its seconds→canonical-frame conversion and half-open convention before predictions, and use the unchanged rally evaluator at IoU0.5 with all rows/unmatched predictions and both boundary denominators. It must pass no rally intervals, winner labels or reference-derived boundaries to inference. No offset is fitted to the new run.

## Three available continuous published-reference clips

All paths below are relative to `data/research/pluggable-pipeline-20261103/`. Proxy digests were newly verified and match their preparation manifests. Actual headers confirm1280×720,30 FPS and the listed frame count. Original whole-source files also exist at the paths recorded in the discovery JSON; their large-file hashes are recorded from existing preparation metadata, **not newly rehashed in this discovery**.

| Recording | Prepared directory | Frames | Published anchors | Original source decode crop | Frozen label→clip offset |
| --- | --- | ---: | ---: | --- | ---: |
| India Open2022 final, Sen–Loh | `benchmarks/india/prepared-v1` |4800|85 across4 partitions|[12000,16800)|−12001|
| Denmark Open2022 semifinal, Lee–Loh | `benchmarks/denmark/prepared-v2` |3300|39 across4 partitions|[13500,16800)|−13503|
| Indonesia Masters2022 men's doubles final, Liang/Wang–Alfian/Ardianto | `dshuttlenet-v7/prepared-v1` |3600|45 across4 partitions|[12000,15600)|−12000|

Proxy SHA256 values:

```text
India   018df5d81dbb60c692805acf558992554e4a24b29fc8e64ea28fd0857bd1ac49
Denmark d6c1e907ed0a2997f044957ae4a2f520d75af86ce911a72748db6404d72c41e6
Doubles dbb07d82af5574d96d4d4363870fe674c9804c6c09733e5c31dce6eb833161e1
```

Each prepared directory contains `proxy.mp4`, `session.json` and `preparation.json`. India/Denmark labels are in `labels-after-alignment-v1/`, with `labels-after-alignment-v1-binding.json`. Denmark's `prepared-v1` is incomplete; use **prepared-v2**. Doubles uses `labels-draft-v1/`, `labels-binding.json`, `full-clip-reference.json` and its separate `taxonomy-protocol-v1.json` one directory above.

India/Denmark raw `set1.csv` files are pinned to CoachAI commit `45517f7d4cb936b03f3eabf939cc7959d39226fe`. Their source annotation hashes are respectively `920f5e18885c38a00b2c0d78c84a3942272328ae3d0573bc26f21b358854e49c` and `2616d6a2fbd3894158754ab2a442d3ccbc8f3d7c2e953739afb9c5091855da8d`. Doubles uses DShuttleNet publisher version7 with `shot.csv` SHA256 `c5242f8f183ce73142e7f3bbf297f69685360f33ff53bd2619cbdc1cd528b9b2` and separate published `rally.csv`. The doubles importer describes the latter as manual serve/start→dead-bird/end spans, with source binding still draft.

The publisher-human annotation origin stays distinct from the project's **draft/agent-reviewed source alignment**. India assumes source offset−1, Denmark−3 and doubles0 before subtracting the fixed crop start. These are existing frozen import choices, not new fitted offsets or independently verified physical-contact uncertainty bounds. Preserve them unchanged and disclose their source-frame-index mapping limit; original source PTS was not reconstructed by these historical crops.

The named men's singles/doubles sources differ from the reviewed women's Test1 windows; the complete edited Test1 file has no independently verified match-identity ledger. They nevertheless were previously evaluated and used in upstream selection, including the previously reserved Denmark comparison. They supply new *current-profile measurements on exposed external material*, not newly blind or pretrained-model-independent generalization. Published anchors/classes/hitters support their stated reference-agreement tasks; they do not supply dense four-person tracking, 3D trajectories, physically certified contact timing or complete score sequences.

## Safe new inference and offline identity rebinding

The existing prepared `session.json` files point at retired paths and identify the **whole original source hash**. They also explicitly record full-original VOD background seeding. Reusing them without adaptation would change the intended clip-only scope or fail after workspace consolidation.

The integration owner's proposed plan is suitable: upload the **verified prepared proxy as the new source**, with a new Session ID and source SHA equal to that proxy. Infer the entire contiguous clip, including gaps, with the already frozen profile. Use format/roster declarations only; no human track identity, published hitter, reference court, external-corner calibration or rally windows are inference inputs. Do not inherit whole-original warm-start metadata. This is a different auxiliary condition from older full-original-seeded runs and must be labelled as such rather than inheriting old performance claims.

Create derived evaluation-only label bindings in a new output directory. Change only session/source identity and the explicit identity mapping within the unchanged clip grid. Preserve every old annotation, source/crop/CSV digest, mapping, frame/time value, class, hitter, status, split/exposure history and review flag under provenance. The original crop belongs under original-source provenance; it is not a current-file transform when the uploaded source is already the clip. `human_verified=false`/draft must remain false/draft. The new runs' lack of known physical player bindings must remain unknown in scoring.

## Existing evaluators and invocation limits

`research/validate_real_video_runtime.py` is the existing fresh, isolated full-clip harness. It supports `--session-json`, `--proxy-path`, explicit `--profiles-dir`/`--profile`, `--output-dir` and `--retain-perception`. It starts inference at0 and records partial prefixes explicitly. Fresh execution is owned by the orchestrator after its GPU leases become free; no invocation was made here.

Offline evaluators must keep their established populations and matching semantics:

- The private `bai-compare-quality-benchmarks.py` supports `freeze` and `compare --protocol ... --labels-dir ... --run name=... --output-dir ...`. It reuses `research.shot_benchmark._matches/evaluate`, chronological maximum-cardinality/minimum-error matching at±3/±6 frames, over all live contact hypotheses across the entire clip, including provisional and unknown candidates. Its full-clip partitions cover gaps; GT rally windows do not filter inference.
- `dshuttlenet-v7/compare-selected-window.py` supports the same freeze/compare pattern and preserves its primary native9 projection, separate native12 view, named-hitter/team versus geometric-side distinction and declared rally IoU thresholds.
- Both archived ops helpers retain retired checkout/output guards and old source/session binding assumptions. Do not edit their bytes or pretend their historical protocol hashes describe a new executor. A new source-bound adapter can reuse their pure extraction/metric functions and the unchanged repository evaluators with explicit new bindings.
- `research/evaluation/benchmark_reference_session.py` is **FineBadminton-specific**: it checks dataset revision/mapping and published provider-review conventions. It is not a generic ShuttleSet/DShuttle evaluator.
- `research/shot_benchmark.py --data-dir NEW_DATA --session NEW_SID --annotations NEW_BOUND_LABELS --allow-draft --tolerance-s 0.1` is a generic alternative for its declared finalized-stroke population. At30 FPS0.1s/0.2s correspond to3/6 frames. That CLI population is not automatically identical to the older all-contact protocol; do not conflate their rates or change populations after seeing outputs.
- Do not use `research/evaluate_session.py` defaults (IoU0.2) as a replacement for the unchanged Test1 rally evaluator at IoU0.5. Declare the additional-reference protocol before outputs are inspected.

The source/time/class/hitter bindings and any new adapter must be frozen before fresh inference results guide changes. Unknown classifications, misses, spurious candidates, false intervals and partial source coverage remain visible. None of the planned runs is represented here as completed or promoted.

## Source-bound discovery evidence

`artifacts/benchmarking/experiments/prod_20261105_data_provenance_discovery_v1/` contains:

- `additional_available_materials.json`: exact current paths, byte lengths and SHA256 values for proxies, sessions, preparation, bindings, raw/derived annotations and doubles taxonomy/rally metadata; original crop/source mappings and review limits.
- `test7_source_metadata.json`: newly verified original source hash and actual FFprobe headers/command, with no frame decode.
- `part2_reference_metadata.json`: all16 primary/generated table schemas, nonblank counts, hashes and first Git commit.
- Extracted plain text from all four user-supplied reference DOCX files for provenance inspection. Text extraction makes no page-layout or image-review claim.

No readiness-manifest roles, historical reservation, annotation values or reviewed flags were rewritten. The12-entry metadata snapshot's zero-new-blind conclusion remains valid for its stated scope; it must not be used as a blanket prohibition or as an exhaustive count of available exposed validation material.
