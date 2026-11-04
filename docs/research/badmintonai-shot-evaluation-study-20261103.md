# BadmintonAI shot classification, evaluation and reuse study

Source review: 3 November 2026. Reference: [jayclim/BadmintonAI](https://github.com/jayclim/BadmintonAI/tree/5c356f05cde0ed90c75316c133e0aba495e5232b), commit `5c356f05cde0ed90c75316c133e0aba495e5232b` (25 September 2026). The source-only checkout is outside this application at `C:\Users\Govin\AppData\Local\Temp\bai-reference-BadmintonAI-20261103`. Repository contents were treated as evidence, not operating instructions.

This is a source and public-metadata study. No model, test, training, video decoder or external repository code was executed. No weights, dataset archives or videos were downloaded by this worker. The published numbers below are the reference's committed results, not reproduced measurements. GPU-server validation remains the integration owner's work. The integration owner restored server access during the later benchmark-selection stage; this worker did not access SSH.

## Recommendation

Study and reuse the **experimental method** before adopting the classifier: train on noisy detected-contact features, compare an unchanged baseline on the same observations, preserve every missed/false/unknown event, and reserve whole matches before tuning. The reference's stack is a useful singles research candidate, but it is neither a supplied standalone pretrained artifact nor validated four-player support. Its README accuracy cannot establish an improvement on this application's cameras, sparse pose schedule, multi-court scenes or doubles.

Keep the current rules and pinned BST-CG-AP shadow baseline. If a new experiment is justified, add an explicitly singles-only BST-0 shadow adapter as a separate component and compare it before adding a supervised stack. A future doubles component must consume four participant hypotheses and retain unknown attribution; selecting two of four players to fit a singles tensor is not an adaptation.

## What the reference actually runs

| Component | Actual contract and behavior | Consequence |
|---|---|---|
| Pretrained BST-0 | `bst_eval.py`: `BST_0(in_dim=72, n_class=25, seq_len=30, depth_tem=2, depth_inter=1)`. Inputs are two ordered people, COCO-17 joints plus 19 bones, normalized shuttle coordinates and temporal length. No court-position input to the network. | Different architecture and input contract from our 100-step BST-CG-AP; checkpoints are not interchangeable. |
| Temporal preparation | Fixed image-frame range `center-15` through `center+15`, then upstream sequence resizing to 30 steps. Top/far precedes bottom/near. The network receives length 30. Normalization uses the bbox top-left and diagonal; shuttle dimensions are hard-coded to 1280×720. | Noncausal context, approximately half a second on each side only at 30 fps. Preserve this exact recipe when reproducing the reference; a generalized fps/resolution recipe needs its own version and evaluation. |
| Pose/missing data | Reads stored keypoint coordinates, with zero-coordinate sentinels. It does not inspect per-joint confidence or an observed-versus-propagated pose flag. Any track ID other than `far` maps to the bottom slot. | Do not copy this loader for our evidence contracts or doubles. Dense YOLO-pose inputs and sparse RTMPose observations are different distributions. |
| Canonical output | Raw 25 scores are unknown plus side×12 merged stroke types. `canonical_prob_frame` sums sides and merges into ten reference classes, retains `p_unknown`, and records the maximum raw class score. Side is the raw 25-class argmax, not the marginalized side maximum. | A class score is not calibrated confidence or proof of contact. Keep raw, family and side scores separate. |
| Stacked classifier | HistGradientBoosting, 300 iterations, learning rate 0.08, at most 31 leaves, random state 0. Features: 14 geometry/timing values, estimated contact height and 12 BST-derived values (ten classes, unknown, maximum raw score). | It needs match-derived training data and upstream perception; it is not a ready-to-load shot detector. |
| Training feature generation | `stack_training_frame` calls the detector inside **labelled rally windows**, computes features at detected frames, and transfers labels with one-to-one greedy nearest matching within ±6 frames. Only matched, known-class rows become training rows. | This addresses noisy contact timing, but does not train on the full label-free segmentation distribution or teach rejection of unmatched false contacts. |
| Runtime training | `classify` excludes the target `match_id` from all database matches with ShuttleSet labels, rebuilds/reads their feature tables, and fits a new stack. | Training data and target-exclusion decisions are hidden runtime dependencies in the reference; use a frozen, versioned training manifest and saved artifact in our plugin. |
| Fallbacks | First fits a labelled-geometry classifier. Missing BST/dependencies returns geometry; failure to train a stack uses BST argmax for nonunknown outputs and otherwise retains geometry. | Reproduction must record the actual branch. A fallback cannot silently count as a successful stack experiment. |
| Hitter modification | Nonunknown BST side overrides wrist attribution and swaps raw hitter/receiver coordinates. Normalized geometry remains from before that swap. Training and runtime contact-height attribution also differ. | The reference's own accuracy audit identifies this inconsistency. Do not inherit it; any repair must change training and inference consistently and be evaluated as a separate candidate. |

Sources: [BST adapter](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/src/badminton/bst_eval.py), [geometry features/model](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/src/badminton/shotclass.py), [pipeline training/classification](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/src/badminton/pipeline.py#L144), [documented inconsistency](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/docs/ACCURACY_IMPROVEMENTS.md).

For intermediate strokes, the reference's “landing” feature is the **next hitter's feet**; only the final stroke attempts a trajectory floor point. The derived distance/time feature is therefore a court-geometry proxy, not a measured 3D shuttle speed. Estimated contact height is another monocular feature, not independently measured height. Waiting for the next contact is acceptable for an explicitly offline component but is incompatible with a claim of immediate causal classification. [Feature construction](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/src/badminton/pipeline.py#L77).

Our ontology separates `push`/`rush` and `net_shot`/`cross_net`; the reference merges them. Its `defensive shot` label also combines several original defensive stroke variants. Preserve original dataset labels and publish a versioned comparison mapping; a ten-class score must not be compared directly with our twelve-class score or used to invent finer predictions. [Reference mapping](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/src/badminton/shuttleset.py), local `sports/badminton/src/bai_badminton/ontology.yaml`.

## Published results and their denominators

The committed `showcase.json` metadata distinguishes saved **label-free pipeline** agreement from the separate detector experiment. All entries below are reported snapshot values. `N` is all labelled stroke rows, `P` all saved pipeline rows, and `M` one-to-one contact matches within ±6 video frames after the configured label/video offset. At 30 fps that tolerance is ±0.20 seconds. Matching in the reference is greedy nearest unused prediction in label order; our shot evaluator instead maximizes chronological match count and then minimizes timing error. Use one frozen matcher for paired comparisons.

| Singles match | N | P | M | Contact P=M/P | Contact R=M/N | Shot accuracy on matched known-class labels | Correct contact+shot / N | Correct contact+shot+side / N |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| India Open final | 1,071 | 1,214 | 952 | 78.4% | 88.9% | 75.7% | 67.0% | 65.4% |
| Denmark Open SF | 663 | 857 | 569 | 66.4% | 85.8% | 88.3% | 75.1% | 72.9% |
| All England SF | 1,377 | 1,709 | 1,219 | 71.3% | 88.5% | 80.6% | 71.0% | 69.1% |
| All England WS final | 796 | 932 | 718 | 77.0% | 90.2% | 77.4% | 69.7% | 69.5% |

Sources: [India snapshot](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/web/public/data/india_open_2022_final/showcase.json), [Denmark](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/web/public/data/denmark_open_2022_sf/showcase.json), [SF](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/web/public/data/all_england_2022_sf/showcase.json), [WS final](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/web/public/data/all_england_2022_ws_final/showcase.json), [exporter definitions](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/src/badminton/export_web.py#L449).

Interpretation limits:

- The README's detector F1 values (86.8–88.8%) come from `hits.validate`, which searches labelled rally windows. They do not describe whole-chain precision on the saved label-free rows above. Denmark has 288 unmatched pipeline predictions as well as 94 missed labels; 88.3% conditional shot accuracy does not describe those errors.
- `pipeline.evaluate.end_to_end_shot` and exported `agreement.e2e` count correct shot labels among temporally matched contacts over all labelled rows. They do **not** require the correct hitter and do **not** penalize extra predictions. `jointE2e` adds court-side correctness but remains a recovery/recall measure, not joint precision or F1.
- Published confusion counts include only matched known-family truth. Exported per-class `overallRecall` adds missed known labels to its denominator, but spurious predictions still do not enter that confusion table. Report per-class precision/F1 over all events as well.
- Micro accuracy hides class imbalance: India's matched short-serve recall is 34.2% (38 matched examples), with overall short-serve recovery 19.1% of 68 labels. Its high-serve conditional recall is 100% on five matched examples, with only nine labels total. Neither number establishes broad performance.
- Standalone `bst_eval.evaluate` is an **oracle-anchor classification diagnostic**: it builds windows centered on labelled contacts and scores known BST outputs separately from all labelled inputs. Its `end_to_end_class` does not include hit detection or rally discovery despite the name.
- Player court-position error selects the nearest available track at labelled hitter frames. Missing detections are excluded from the coordinate-error denominator; it is neither detection recall nor durable identity accuracy.
- Rally count versus decoded score total is a separate consistency check; equal counts do not prove correctly aligned rallies. Exact final scores do not certify each observed digit, accepted point or intermediate score. `--skip-slow` can retain older hit/segmentation fields while refreshing other showcase fields, so snapshot fields need independent run provenance.

The source makes useful corrections and reports regressions. Its [accuracy audit](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/docs/ACCURACY_IMPROVEMENTS.md) distinguishes label-side corrections from model gains, records extra false contacts, and reports a deployment gate allowing up to 0.5 percentage points of shot-recovery regression per match. These are valuable practices to carry forward.

## Match separation, base models and meta-learning

Excluding the target match from the HistGB training rows is a real safeguard. It is **not** a guarantee that all model selection, pretrained learning, calibration or threshold tuning is independent of that match.

1. `shotclass.evaluate` includes cross-match evaluation and pooled five-fold classification CV. The pooled call has no match/rally grouping, so the pooled number is not a new-match estimate. Adjacent shots share players, camera, geometry and overlapping context.
2. `data/models/bst_ft/stack.py` evaluates stacks on label-centered/label-derived features. The current pipeline then trains on noisy detected-contact features because its authors observed a substantial deployment gap. These two reported accuracies must stay separate.
3. `ft_bst.py` declares India+SF training, WS early stopping and Denmark test. `ft_folds.py` leaves each target match out, trains on two remaining matches and selects checkpoints on the third. These are reasonable declared match splits, but no supplied artifact/log independently proves which weights were used. The scripts do not set reproducible random seeds for training.
4. `stack_ft.py` fits the meta-learner on **pretrained** BST probabilities and swaps to held-out fine-tuned probabilities only at test time. It is a distribution-swap experiment, not a nested cross-fitted FT stack. Do not cite its small gain as evidence for a fully trained FT meta-learner.
5. If fine-tuned base predictions are used to train a meta-learner, the **outer test match must be absent from every inner base model**. Naively pooling one leave-one-match-out prediction file per match can leak an outer test match through base models used to create the outer training rows. Cross-fit only within the outer training partition, select hyperparameters on its inner validation matches, then evaluate once on the untouched outer match.
6. Official BST source at `c93acfa736ed784ba7bea4ec9d360001dea9b728` declares a 44-match 2018–2021 ShuttleSet manifest and match-ID train/validation/test lists. That supports a temporal separation hypothesis from these 2022 reference videos, but it is not checkpoint-specific proof. Record exact base-weight dataset membership and split before claiming a fully unseen test.
7. The reference's `heldOut` boolean is hard-coded for Denmark. Its later accepted deployment was evaluated against all four matches, including Denmark, with a per-match acceptance gate. Treat Denmark as an originally reserved/stage-specific test, not an untouched final selection holdout. Our own new consumer/amateur/doubles holdout must be independently reserved.

Sources: [fine-tune scripts and notes](https://github.com/jayclim/BadmintonAI/tree/5c356f05cde0ed90c75316c133e0aba495e5232b/data/models/bst_ft), [upstream clip split](https://github.com/Va6lue/BST-Badminton-Stroke-type-Transformer/blob/c93acfa736ed784ba7bea4ec9d360001dea9b728/ShuttleSet/gen_my_dataset.py#L218), [upstream match manifest](https://github.com/Va6lue/BST-Badminton-Stroke-type-Transformer/blob/c93acfa736ed784ba7bea4ec9d360001dea9b728/ShuttleSet/set/match.csv), [held-out flag/export](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/src/badminton/export_web.py#L549).

For a **frozen**, non-fine-tuned BST base model, cross-fitting a new base model is unnecessary, provided its training provenance is recorded and its preprocessing remains fixed. The supervised meta-learner, threshold/abstention choices and calibration still require independent match splits. Confidence calibration should use a separate calibration partition and be reported with coverage and reliability; softmax and HistGB maximum scores are not automatically calibrated.

## Artifacts, data and licenses

| Item | Verified availability / provenance | Reuse boundary |
|---|---|---|
| Reference application code | Root [MIT license](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/LICENSE), copyright Jayden Lim 2026. | Preserve notice for copied substantial code. This grant does not cover every model, library, annotation or broadcast. |
| Reference trained stack | No serialized HistGB artifact is committed. DB, track/shuttle data, feature caches and third-party directory are ignored. | Must reconstruct with a frozen licensed dataset and training manifest; do not promise fresh-clone Python inference. Static precomputed web outputs are a different delivery path. |
| Reference fine-tuned BST | README mentions `bst_ft20.pt` and per-fold probabilities; neither the checkpoint nor train/probability dumps is committed. Scripts point to an absent macOS scratch directory. | Historical claims and training recipes, not available pretrained releases. Do not treat a filename as an obtainable validated model. |
| Official BST-0 candidate | Author-linked [ShuttleSet weights folder](https://drive.google.com/drive/folders/1D4172WZDJWPvpJdpaHDhy_cA-s8F-zR5) lists `bst_0_JnB_bone_merged.pt`, file ID `1P0umD0r7nR8GAp085dMlbSCkHErZWZdV`; public listing says approximately 6.9 MB, modified 6 August 2025. Format expected by reference is a Torch state dictionary/archive. | No authoritative SHA-256 or exact byte length found in reference metadata. No file downloaded/loaded here. Verify exact structure with a restricted loader on the GPU server, compute/pin digest and bytes, and retain original source link and license evidence. |
| Our existing BST-CG-AP | Registry pins 7,514,133 bytes, SHA-256 `997f43e52b20cb47517132c71d3e147d7d717a2d9651cfbe7651a5003bd66809`, official file ID `1snqpEEww-GG6xFUBzkuctYAPHcBP360B`. | Already has strict digest loading, `weights_only=True`, observed-only preparation and a singles capability gate. Preserve it as a distinct baseline. |
| BST code/weights rights | Official [MIT source license](https://github.com/Va6lue/BST-Badminton-Stroke-type-Transformer/blob/c93acfa736ed784ba7bea4ec9d360001dea9b728/LICENSE); official README links datasets and weights. No separate checkpoint-specific model card/license statement was identified in the reviewed listing. | Record that distinction instead of promoting the code license into blanket clearance for each weight/training dataset. Checkpoint integrity and checkpoint rights are separate questions, including for noncommercial use. |
| ShuttleSet22 reference labels | Four match CSV groups are committed; upstream CoachAI has a [root MIT license](https://github.com/wywyWang/CoachAI-Projects/blob/main/LICENSE). | Preserve upstream provenance, raw labels, annotation revision and citation. BWF broadcast ownership and distribution rights remain separate. Verify source-video alignment, annotation uncertainty and model overlap before benchmarking. |
| YOLO11 pose / bundled tracker | Reference depends on Ultralytics; its license inventory flags AGPL-3.0. | The reference's MIT wrapper does not erase dependency/weight obligations. Keep our existing non-Ultralytics detection/pose adapters unless a separate decision justifies a switch. |
| Training/runtime dependencies | Reference requirements are mostly unpinned; model code and weights are expected in a hand-cloned third-party directory. | Do not install its environment or MPS patches into our Pascal CUDA/FFmpeg runtime. Record exact existing runtime versions and add only isolated, necessary compatible code. |

The reference loads BST with `torch.load(..., weights_only=False)` and its scratch scripts use NumPy `allow_pickle=True`. Do not copy those deserialization choices for a newly fetched artifact. An initial self-computed hash detects future changes but does not authenticate its origin. The source cache key includes source/configuration and weight size/mtime, but not label, track or shuttle content hashes; our cache must bind those actual inputs. [Artifact exclusions](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/.gitignore), [license inventory](https://github.com/jayclim/BadmintonAI/blob/5c356f05cde0ed90c75316c133e0aba495e5232b/LICENSES/README.md).

### Doubles labels: availability is more nuanced than the reference claims

- **S² Doubles:** the [official repository](https://github.com/HuangYuHsien/S2DoublesDataset/tree/c9168210e13f4869cbc8ebf47f9bc671b056cbab) contains three broadcast matches/six sets, with A/B/C/D hitter, stroke type, start/end frame, four players' feet, rally scores and winning team. Its current tree has no LICENSE/COPYING/terms file. This is a concrete annotation candidate after a permission/terms check, not a cleared training dataset. Its tracknet CSVs are predictions, not independent shuttle truth. Exact physical-contact meaning of shot start/end still needs review.
- **BFMD:** [official source](https://github.com/Ning-D/BFMD/tree/c7c7e8e4c815085dda42746f16e07f1172503312) describes a released subset with seven doubles matches carrying generic hit/bounce/net-hit timelines, without doubles shot-type or four-person annotations. The [dataset page](https://ning-d.github.io/BFMD-Dataset/) limits use to noncommercial academic research and disallows redistribution. It can inform a contact-label investigation within those terms; it is not a ready doubles classifier or reviewed four-person benchmark. Preserve manual labels separately from TrackNet and inferred outputs, and distinguish released counts from larger paper counts.
- **DShuttleNet:** its [September 2026 paper](https://arxiv.org/abs/2610.14016) links a doubles dataset through [DOI 10.34740/kaggle/dsv/16097938](https://doi.org/10.34740/kaggle/dsv/16097938). Kaggle access and dataset-specific terms were not verified in this study. Keep as an unverified lead, not an available cleared artifact.

These findings refute a blanket assumption that doubles labels do not exist. They do not supply a licensed pretrained four-player shot model. The reference's newer `doubles/strokes.py` and `doubles/shots.py` exist despite older README wording; their heuristic outputs must be assessed separately from the singles stack and from human labels.

## A fair experiment using the current application

Current code already supplies most of the evaluation skeleton: `research/shot_benchmark.py` keeps missed/spurious/unknown events and joint metrics; `research/participant_benchmark.py` requires independently reviewed episode-to-person bindings; `engine/src/bai_engine/evaluation.py` evaluates chronological interval matches. `research/evaluation/benchmark_reference_session.py` binds published labels to source/proxy metadata and explicitly limits its hitter metric to court side. Use these contracts rather than importing the reference DuckDB monolith.

1. Freeze an unchanged baseline session and source/proxy/event/cache hashes before any reanalysis. Use a fresh session or copied snapshot, preserve historical outputs and record actual component versions, model digests, device, format, configuration and calibration. All execution belongs on the existing GPU server after `source ../gpu-env.sh`, using its `.venv`.
2. Compare **only the classifier** first: fixed target-court perception, detected contacts, participant hypotheses and camera boundaries. Run rules, existing CG-AP and optional BST-0 on identical events; ineligible windows remain unknown with a reason. Preserve the default's outputs and source events. A separate oracle-contact diagnostic can measure classification potential but must never supply anchors to the end-to-end run.
3. Give BST-0 its own typed configuration/version and manifest entry. Reuse observed frame/pose evidence but implement its exact 30-step preprocessing independently from CG-AP. Strictly load the expected architecture and class order. Reject doubles or uncertain format, missing observations, incomplete future windows, cut/replay crossings and invalid output; retain raw class/side values and their provenance. Preprocessing parity is a functional check, not accuracy.
4. If stacking is pursued, first train a geometry-only ablation, then geometry+estimated height, then geometry+frozen BST values. Use noisy detections from **machine** rally segmentation on training matches; separately document an experiment using oracle training windows. Retain unmatched detections for an explicit contact/rejection evaluation instead of silently treating the known-class learner as a hit validator.
5. Freeze one feature table schema and recompute it consistently after any attribution change. Save the fitted estimator plus feature names/order, ontology mapping, train/calibration split digests, upstream model/artifact hashes, observed-feature policies, dependency versions and failure behavior. Cache keys need actual label/track/shuttle/input content, not only paths or mtimes.
6. Reserve whole-match development/calibration/test partitions for professional singles, amateur singles and four-player doubles before results. Include uncertain format, occlusion, same-kit crossings, side changes, replay/cuts, adjacent courts, weak shuttle observations and edited score jumps. Confidence intervals should resample whole matches rather than overlapping shot windows. With only a few matches, report paired per-match results and the narrow population honestly.
7. Apply identical matching/taxonomy/eligibility to every candidate, aggregate counts before pooled metrics, and publish per-match as well as pooled/class results. Fix acceptable accuracy, false-positive, abstention and resource budgets before opening the test reports. Changing policy after those results converts that test into development data.

The existing local historical 0044 study found only nine matched predictions, 19 false positives and 32 misses over 41 published anchors. Its repaired rules and CG-AP shadow produced similarly low all-event known-family F1; CG-AP assigned more known classes to false contacts. This is a prior diagnostic, not a fresh measurement or a comparable score against the reference's four-match benchmark. Local `docs/testing/bst-adapter-20261029.md` preserves the counts and limitations. `0046` was reserved in that historical workflow; confirm it has remained untouched before reusing the held-out designation. Part2 rally-level CSVs do not supply exhaustive per-contact, per-shot or four-player labels.

### Runnable bounded comparison path

The first executable experiment needs **no new reference stack, training dumps or dependency installation**. The existing session shadow command compares the currently available CG-AP component's output population with the default session, without changing that session. It runs on the GPU server but explicitly uses two CPU threads there; do not label its timing GPU throughput. Use the integration owner's verified completed session and its data root:

```bash
source ../gpu-env.sh
export PYTHONPATH="$PWD/engine/src:$PWD/sports/badminton/src:$PWD/apps/api/src:$PWD"
.venv/bin/python -m bai_api.cli models list
.venv/bin/python -m research.evaluation.bst_shadow_session \
  --data-dir /absolute/path/to/application-data \
  --session COMPLETED_CONFIRMED_SINGLES_SESSION_ID \
  --models "$PWD/models" \
  --output /absolute/path/to/new-audit/SESSION-bst-cg-ap-shadow.json
```

Before this command, explicitly establish singles from sustained observations or a confirmed roster. Current `run_session`/`infer_strokes` reject a doubles roster but allow an absent roster, then request singles preprocessing. That existing implicit assumption is a limitation, not permission to classify an uncertain or four-player recording. Do not change a session roster merely to bypass the gate. The command uses `fetch=False`; if the pinned CG-AP artifact is absent, use the authorized model-registry fetch on the server and verify its expected digest/size before rerunning. Never substitute the newly discovered BST-0 weight for that manifest entry.

The runner processes current `CONFIRMED` stroke events, including unknown-family strokes; count any other excluded event statuses separately. Its complete contiguous context must come from the same camera shot and detected machine-rally neighbors. Cached reused/propagated pose is excluded from observed pose support. It records usable-frame coverage, skipped windows/reasons, source frames, timing, hashes and side probabilities. Side outputs must remain hypotheses: a null canonical actor must stay null until independent identity evidence supports binding. Its `cross_net` comparison normalization is retained with `original_family`; preserve that distinction when comparing a native twelve-class report.

To score the **unchanged application baseline** against already converted, source-bound public reference windows:

```bash
.venv/bin/python -m research.evaluation.benchmark_reference_session \
  --annotations-dir /absolute/path/to/verified-reference-windows \
  --data-dir /absolute/path/to/application-data \
  --session COMPLETED_REFERENCE_SESSION_ID --tolerance-s 0.2 \
  --output /absolute/path/to/new-audit/SESSION-baseline-reference.json
```

For the previously frozen **development** snapshot, the existing paired rules/CG-AP report is runnable with:

```bash
.venv/bin/python -m research.evaluation.bst_shadow \
  --snapshot data/audit-20261029/evaluation/baseline-0044 \
  --models "$PWD/models" \
  --output /absolute/path/to/new-audit/0044-rules-cg-ap-comparison.json
```

These commands are source-checked recipes, not newly executed results, and all output paths must be new. The frozen snapshot must actually exist and match its manifest; do not manufacture it from a report alone. `bst_shadow` intentionally refuses held-out references. A new generic paired candidate report needs a frozen-policy, read-only adapter that joins shadow outputs by event ID to the same prediction population and passes them to the existing evaluator; it must retain skipped contexts as unknown and may not modify labels or model inputs. Do not relax the development-only guard merely to inspect a reserved test recording.

The optional BST-0 next step needs a **new adapter and manifest entry**, official checkpoint acquisition/digest/restricted-load verification and preprocessing parity first. No ready BST-0 CLI exists in this application today. The source-only study therefore supplies a bounded runnable existing-model comparison, not a claim that the reference stack can run here without implementation.

## Required metric matrix

Let N be independently labelled contacts in the evaluated exhaustive windows, P all predicted contacts, and M chronological one-to-one matches under a frozen time tolerance. Unknown/unobservable truth is excluded only for the property that cannot be labelled, with explicit counts. A missing denominator yields unavailable, not zero accuracy. Contact timing tolerance and rally IoU/boundary criteria must be preregistered; published hit-anchor agreement must remain labelled as such.

| Property | Stage-conditional measures | End-to-end/error measures and denominator | Required strata / evidence |
|---|---|---|---|
| Shuttle visibility/location | Visibility P/R/F1; median/p90 pixel error and normalized error on matched independently visible samples. | Missed visible samples, false visible samples, out-of-court/adjacent-court picks; localization success over **all labelled visible frames**, not only detections. | Visible/occluded/absent, real/duplicated proxy observations, interpolated estimates separately; no airborne metres from floor homography. |
| Contact detection/timing | Absolute/signed timing error, median/p90 and tolerance curve on M matched contacts. | TP=M, FP=P−M, FN=N−M; P/R/F1; false contacts per minute of exhaustively labelled live and no-play spans. | Serve/nonserve, singles/doubles, missing pose/shuttle, target/adjacent court, cuts/replays. |
| Hitter and team | Correct person among matched contacts with observable hitter; report both all-observable and resolved-only accuracy, abstention fraction and teammate confusion. Score court side, team and person separately. | Per-person/per-team event P/R/F1; missed, wrong, unknown and spurious assigned events; joint contact+hitter and contact+team. | Four real participant IDs with independently reviewed track bindings; after end changes, crossings, occlusion and track resets. Team agreement cannot certify athlete identity. |
| Shot class | Matched-known-truth top-1 accuracy, per-class P/R/F1, macro-F1, support/confusion; classifier coverage and unknown reasons; reliability only if calibrated on independent data. | All-event known-family P/R/F1 including `__missed__`/`__spurious__`; joint contact+family+person and contact+family+team P/R/F1; correct known family / all known truth as a separate recovery metric. | Native twelve-class and documented common-taxonomy comparison separately; serves, rare classes, unsupported doubles explicitly unavailable. |
| Rally boundaries | Start/end signed and absolute error, median/p90 on matched rallies. | Chronological interval P/R/F1 at frozen IoU and independent boundary tolerance, false/missed rallies, split/merge counts; full-rally recovery. | Live play versus practice/replay, short serves, missed final contacts, cuts and multi-court scenes. Equal score/rally counts are not alignment. |
| Point decision/outcome | Winner/team agreement on independently matched rallies with observable outcome; reason confusion only where labelled. | Correct accepted point / all labelled official points; wrong and invented accepted points, missed/unknown points, duplicate awards, unsupported rationale; winner-conditioned and full-chain counts. | Singles/two scoring slots versus four participants/two teams, legal faults, edited broadcasts, reviewed/unknown outcomes. |
| Score sequence | OCR digit/pair accuracy per **observed sampled scoreboard crop**, row/name mapping accuracy and coverage. Keep reconstructed transitions separate. | Exact intermediate score-pair agreement per labelled state; correct transition P/R; illegal/wrong/missing/duplicate transitions, first divergence and recovery delay; exact set finals **and** whole-sequence agreement. | End swaps, deciding-game 11, deuce/cap, missing graphics, score jumps, replay OCR. Plausible/exact finals cannot validate invented points. |
| Identity/format | Sustained four-person detection/track coverage, ID switches/fragmentations and supported format confusion/abstention. | Four-person identity and pair membership coverage over labelled time; incorrect forced-format duration; downstream joint results stratified by unresolved identity/format. | Do not score “all four detections present” as identity or shot correctness; never infer singles merely from temporary two-player visibility. |
| Operational cost | Cold/warm component latency, sampled temporal context, feature preparation and inference time. | End-to-end wall time, real-time factor, peak VRAM/RAM, decode/transfer/cache/storage, failures/retries and incomplete analyses. | Same canonical proxy, device/provider/precision, existing Pascal runtime and scheduler; do not disturb unrelated jobs. |

A candidate can improve conditional classification while worsening false contact labels or joint event precision. Adoption requires the predeclared stage **and** end-to-end gates, documented rights and reproducibility, plus explicit support or explicit abstention for doubles and uncertain format. No result in this source-only review crosses that gate.

## Concrete public benchmark: India Open 2022, set 1, rallies 1–4

Use **Lakshya Sen versus Loh Kean Yew, India Open final, 16 January 2022**, as a bounded **development/reference-agreement** benchmark. This is the same original broadcast underlying the reference's India result, but the input below is the dataset publisher's CSV, not showcase predictions, rendered clips or prior pipeline output. Reading these labels to select/debug a candidate makes this match development data for our subsequent experiments; reserve a different match for the final gate.

### Authoritative provenance and license evidence

Publisher: [CoachAI/NYCU official source](https://github.com/wywyWang/CoachAI-Projects/tree/45517f7d4cb936b03f3eabf939cc7959d39226fe), commit `45517f7d4cb936b03f3eabf939cc7959d39226fe`. The [dataset README](https://github.com/wywyWang/CoachAI-Projects/blob/45517f7d4cb936b03f3eabf939cc7959d39226fe/CoachAI-Challenge-IJCAI2023/ShuttleSet22/README.md) identifies the official release and field meanings. The [publisher's paper](https://www.ijcai.org/proceedings/2024/1042.pdf) describes expert annotation of public BWF footage. The dataset match manifest identifies this as match 8, A=match winner **Lakshya Sen**, B=**Loh Kean Yew**.

| Publisher file | Exact bytes | SHA-256 |
|---|---:|---|
| `CoachAI-Challenge-IJCAI2023/ShuttleSet22/set/Lakshya_SEN_LOH_Kean_Yew_YONEX_SUNRISE_India_Open_2022_ Finals/set1.csv` | 61,845 | `920f5e18885c38a00b2c0d78c84a3942272328ae3d0573bc26f21b358854e49c` |
| `CoachAI-Challenge-IJCAI2023/ShuttleSet22/set/match.csv` | 9,674 | `95260cc5ee102e0ef72ddb54114f13638357e58d68be1e7f3cac06388b7deb34` |
| `CoachAI-Challenge-IJCAI2023/ShuttleSet22/README.md` | 3,463 | `4cac736cc8bb17dcec86a9d796bc9bd8170535a4aa0adad9b790d8c9e5462b3b` |
| Publisher root `LICENSE` | 1,069 | `2ff939aee5c1dbce2051c009933dc0ca17f75e75b26c844b73780f2498b33164` |

Immutable [annotation download](https://raw.githubusercontent.com/wywyWang/CoachAI-Projects/45517f7d4cb936b03f3eabf939cc7959d39226fe/CoachAI-Challenge-IJCAI2023/ShuttleSet22/set/Lakshya_SEN_LOH_Kean_Yew_YONEX_SUNRISE_India_Open_2022_%20Finals/set1.csv), [match manifest](https://raw.githubusercontent.com/wywyWang/CoachAI-Projects/45517f7d4cb936b03f3eabf939cc7959d39226fe/CoachAI-Challenge-IJCAI2023/ShuttleSet22/set/match.csv), [license text](https://raw.githubusercontent.com/wywyWang/CoachAI-Projects/45517f7d4cb936b03f3eabf939cc7959d39226fe/LICENSE).

**Precise license finding:** the dataset publisher itself commits its original annotation files in its MIT-licensed repository (Wei-Yao Wang, 2022), with no nested ShuttleSet22 license or third-party data override found. This is the actual evidence for annotation reuse, stronger than BadmintonAI's separate MIT license. The reviewed publisher README/paper does not separately state an annotation-specific license grant; retain that scope limitation rather than claiming an additional document exists. It does not grant rights to BWF video. Do not redistribute the source video or infer model-weight rights from this annotation release.

If a dataset-specific explicit license field is required, the already supported [Finebadminton-20K publisher card](https://huggingface.co/datasets/iLearn-Lab/Finebadminton-20K/blob/72cae601e08c83ee8ec7e19f8fd7850e9158af7d/README.md) explicitly declares Apache-2.0 for its dataset release. Existing 0044 imports cover four rallies and have pinned hashes in `research/README-finebadminton-reference.md`. They lack independent scoreboard/score-sequence labels and an identified original BWF URL in the inspected JSON, so India is the more complete cross-stage candidate. Underlying broadcast rights remain separate in either case.

### Original video, timebase and bounded window

Original, undecorated [BWF TV broadcast](https://www.youtube.com/watch?v=7_O5r9CLOVw). BWF's own [oEmbed response](https://www.youtube.com/oembed?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D7_O5r9CLOVw&format=json) confirms the Sen–Loh India Open 2022 final and channel BWF TV. The video ID is corroborated by the reference's pinned `config/matches.yaml`; the dataset's own match CSV does not contain a YouTube-URL column. Title/channel agreement proves match identity, not that every re-encoded copy shares the same decode frame alignment.

Select source decode frames `[12000,16800)` **only after confirming the downloaded original has the expected 30 fps timeline**. This corresponds to source time `[400,560)` seconds, 06:40–09:20, contains four complete labelled contact spans and excludes rally 5's first anchor at frame 17275. It produces a 4,800-frame, 160-second clip. Hash the exact downloaded source and derived clip; a BWF video ID alone is not a content digest.

The reference's established mapping for this video is `zero_based_source_frame = ShuttleSet22.frame_num - 1`. With the proposed crop, `clip_frame = ShuttleSet22.frame_num - 12001`. This is a documented starting alignment, **not independently verified by this worker**. On the server, inspect the first serve/contact, at least one later contact in each rally, court/athlete positions and post-rally scoreboard. Freeze any correction from video/annotation evidence before looking at model errors. Do not optimize a time shift against predicted contacts. If the actual video frame rate/origin differs, preserve an explicit source-to-proxy mapping instead of forcing these formulas.

| Rally | Published first→last frame | Contact rows | Proposed clip first→last frame | Stored CSV score A:B | Published point winner |
|---|---|---:|---|---|---|
| 1 | 12420→13116 | 24 | 419→1115 | 0:1 | B / Loh |
| 2 | 13570→14099 | 18 | 1569→2098 | 0:2 | B / Loh |
| 3 | 14715→15262 | 19 | 2714→3261 | 1:2 | A / Sen |
| 4 | 15737→16420 | 24 | 3736→4419 | 2:2 | A / Sen |
| Total | | **85** | | | |

All 85 selected rows have a known raw stroke type and hitter A/B, and none has a nonblank `flaw` flag. The selected score values are constant within each rally and are consistent with after-rally scores; verify that convention on video before scoring point transitions. Coarse `time` strings omit fractional seconds, so use `frame_num`, not parsed `time`, for matching.

**Available independent label properties:** contact/hit-time anchors, hitter A/B and match-level named mapping, eighteen-way raw stroke vocabulary, stroke order/serve fields, rally membership, score values, point winner, final win/lose reason, feet coordinates and contact-image coordinates in **81 of the 85** rows. These are expert-published annotations, with no independent per-contact uncertainty bounds identified. The four first/serve rows have blank contact-image coordinates; keep those missing values explicit.

**Not supplied by this selected CSV:** dense shuttle visibility/location truth, independently labelled rally down/end timestamps, negative/no-play contact labels over the whole 160 seconds, scoreboard crop digit truth at every time, per-frame persistent track identity, four-player evidence or a source-video content hash. First/last hit frames define a contact span, not a true rally-end boundary. The 81 contact-image points can support a separately declared hit-frame localization diagnostic after source-resolution/alignment checks; they do not supply dense trajectory truth or 3D airborne positions. A scored frame/time/shot/hitter benchmark can proceed as published-reference agreement; physical-contact accuracy, full rally boundaries and whole score-sequence accuracy require the additional review/labels specified above.

### GPU-only fetch, prepare and evaluation recipe

Run from the authorized isolated server checkout using its existing environment. The new output root is `../pluggable-pipeline-research-20261103`; keep media/labels/results outside Git. Use a new leaf directory so prior files cannot be overwritten.

```bash
source ../gpu-env.sh
export PYTHONPATH="$PWD/engine/src:$PWD/sports/badminton/src:$PWD/apps/api/src:$PWD"
task_bench="$(realpath ../pluggable-pipeline-research-20261103)/shuttleset22-india-r1-4-v1"
mkdir "$task_bench"
curl --fail --location \
  'https://raw.githubusercontent.com/wywyWang/CoachAI-Projects/45517f7d4cb936b03f3eabf939cc7959d39226fe/CoachAI-Challenge-IJCAI2023/ShuttleSet22/set/Lakshya_SEN_LOH_Kean_Yew_YONEX_SUNRISE_India_Open_2022_%20Finals/set1.csv' \
  --output "$task_bench/set1.csv"
printf '%s  %s\n' \
  920f5e18885c38a00b2c0d78c84a3942272328ae3d0573bc26f21b358854e49c \
  "$task_bench/set1.csv" | sha256sum --check -
.venv/bin/python -m yt_dlp --no-playlist --no-overwrites --write-info-json \
  -f 'bestvideo[height=720][fps=30]' --remux-video mp4 \
  -o "$task_bench/original.%(ext)s" 'https://www.youtube.com/watch?v=7_O5r9CLOVw'
ffprobe -v error -select_streams v:0 -show_streams -show_format \
  -of json "$task_bench/original.mp4" > "$task_bench/original-probe.json"
sha256sum "$task_bench/original.mp4" > "$task_bench/original.sha256"
```

Use installed yt-dlp only if available; a missing package, unavailable 720p/30 stream or access failure is a recorded failure, not permission to replace the managed environment or silently use a different source. Before the next command, inspect the probe and verify frame indexing/rate. Keep the source's decode/timestamp provenance. Frame-count-based trim avoids an unrecorded keyframe-seek offset:

```bash
ffmpeg -nostdin -n -i "$task_bench/original.mp4" \
  -vf 'trim=start_frame=12000:end_frame=16800,setpts=N/(30*TB)' \
  -an -fps_mode passthrough -c:v libx264 -preset fast -crf 18 \
  "$task_bench/india-r1-4.mp4"
ffprobe -v error -select_streams v:0 -count_frames -show_streams -show_format \
  -of json "$task_bench/india-r1-4.mp4" > "$task_bench/clip-probe.json"
sha256sum "$task_bench/india-r1-4.mp4" > "$task_bench/clip.sha256"
```

Require 1280×720, 30/1 fps and 4,800 decoded frames for this exact mapping; otherwise stop and establish a new mapping. Review alignment/boundaries and select calibration without model predictions. Analyze a **new isolated session**, preserving the same current baseline profile and model hashes as the candidate comparison; use the existing API to set explicit singles and the correct court calibration. The simple CLI also supports an isolated data root (`BAI_DATA_DIR`) and `bai_api.cli analyse ... --profile gpu-rtx4000`, but its default roster must not be mistaken for observed format evidence. Record the resulting session ID and actual proxy metadata before building labels.

There is currently no ShuttleSet22-specific importer in this application. Do not pass this CSV to the FineBadminton importer or alter that importer's frozen dataset checks. The existing `research.shot_benchmark` can consume a straightforward JSON normalization. The following server-only standard-library preparation writes **draft, development** manifests, preserving raw rows and the assumed transform. It does not assert a new human review, independent rally boundaries or pristine holdout status. Set `TASK_BENCH`, `TASK_DATA` and `TASK_SESSION` to the verified paths/session first:

```bash
export TASK_BENCH="$task_bench"
export TASK_DATA=/absolute/path/to/new-benchmark-application-data
export TASK_SESSION=ACTUAL_COMPLETED_BENCHMARK_SESSION_ID
.venv/bin/python - <<'PY'
import csv, hashlib, io, json, os, sqlite3
from fractions import Fraction
from pathlib import Path

bench, data = Path(os.environ['TASK_BENCH']), Path(os.environ['TASK_DATA'])
sid = os.environ['TASK_SESSION']
assert sid.isalnum(), 'invalid session ID'
raw = (bench / 'set1.csv').read_bytes()
expected = '920f5e18885c38a00b2c0d78c84a3942272328ae3d0573bc26f21b358854e49c'
assert hashlib.sha256(raw).hexdigest() == expected, 'annotation digest mismatch'
with sqlite3.connect((data / 'sessions.sqlite').resolve().as_uri() + '?mode=ro', uri=True) as con:
    row = con.execute('SELECT body FROM sessions WHERE session_id=?', (sid,)).fetchone()
assert row is not None, 'session not found'
session = json.loads(row[0])
media = session['media']
assert Fraction(media['fps_num'], media['fps_den']) == 30, 'unexpected proxy timebase'
assert (media['width'], media['height'], media['n_frames']) == (1280, 720, 4800)
source_sha = session['source']['sha256']
assert hashlib.sha256((bench / 'india-r1-4.mp4').read_bytes()).hexdigest() == source_sha
mapping = {
    '放小球':'net_shot', '擋小球':'block', '殺球':'smash', '點扣':'smash',
    '挑球':'lift', '防守回挑':'lift', '長球':'clear', '平球':'drive',
    '小平球':'drive', '後場抽平球':'drive', '切球':'drop',
    '過渡切球':'drop', '過度切球':'drop', '推球':'push', '撲球':'rush',
    '防守回抽':'drive', '勾球':'cross_net', '發短球':'short_serve', '發長球':'long_serve',
}
rows = list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
out = bench / 'draft-labels'
out.mkdir()
counts = []
for rally in range(1, 5):
    group = sorted((r for r in rows if int(r['rally']) == rally), key=lambda r:int(r['ball_round']))
    counts.append(len(group))
    frames = [int(r['frame_num']) - 12001 for r in group]
    # Derived diagnostic margins, not independently labelled rally boundaries.
    lo, hi = frames[0] - 20, frames[-1] + 21
    document = {
        'schema_version':1, 'session_id':sid, 'media_sha256':source_sha,
        'timebase':'canonical_media_seconds', 'window_s':[lo/30, hi/30],
        'status':'draft', 'split':'development', 'exhaustive':True,
        'review':{'human_verified':False, 'our_human_reviewed':False,
                  'method':'Published expert stroke rows; draft crop alignment and derived margins require video review.'},
        'reference_provenance':{
            'dataset':'CoachAI-ShuttleSet22', 'revision':'45517f7d4cb936b03f3eabf939cc7959d39226fe',
            'annotations_sha256':expected, 'source_video_url':'https://www.youtube.com/watch?v=7_O5r9CLOVw',
            'mapping_version':'shuttleset22-native12-draft-v1', 'source_crop_frames':[12000,16800],
            'label_to_clip_frame':'frame_num - 12001', 'rally':rally,
            'window_basis':'first/last published hit anchor with 20-frame margins; diagnostic only',
            'exhaustive_scope':'published official rally contacts; margins and all-physical-hit exhaustiveness not independently reviewed',
        },
        'shots':[{'time_s':f/30, 'frame_idx':f, 'family':mapping.get(r['type'],'unknown'),
                  'player_id':{'A':'lakshya_sen','B':'loh_kean_yew'}.get(r['player']),
                  'source_row':r} for r,f in zip(group,frames)],
    }
    with (out / f'rally-{rally}.json').open('x', encoding='utf-8') as stream:
        json.dump(document, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')
assert counts == [24,18,19,24], counts
print(json.dumps({'status':'draft','rows':sum(counts),'output':str(out)}))
PY
for task_labels in "$task_bench"/draft-labels/rally-*.json; do
  .venv/bin/python -m research.shot_benchmark \
    --data-dir "$TASK_DATA" --session "$TASK_SESSION" \
    --annotations "$task_labels" --tolerance-s 0.2 --allow-draft \
    > "${task_labels%.json}-baseline-report.json"
done
```

Here `exhaustive=true` is the required draft schema assertion for the published official-contact population; the explicit draft status and scope record prevent it from being presented as our independently verified all-physical-hit ground truth. Review the margins/alignment and every evaluated contact/window before creating a **new reviewed** manifest version. Unknown truth, ambiguous timing and nonofficial practice contacts require documented treatment. Keep named reference IDs independent of prediction identity: current unbound machine actors score unresolved, and source labels must not be used to bind them opportunistically. Native `cross_net` is preserved in this preparation; use a separately versioned common-family mapping for comparisons with the existing shadow runner.

`research.evaluation.benchmark_reference_session` is intentionally FineBadminton-specific and will reject this dataset provenance; use the generic shot/participant/interval evaluators instead. The loop emits per-rally reports. Pool TP/FP/FN and per-class confusion counts before computing combined metrics; do not average four F1 values. A generic candidate-shadow-to-label join is still required for paired classification, as described above. This recipe is not an executed result and cannot certify exact rally ends, dense shuttle performance or full score-sequence accuracy.

### Concrete Hylo shadow invocation and exact BST license boundary

The integration owner identifies Hylo session `01M6GC737FR6Z4PDA74BPEZX4H` as explicit singles, with data root `/home/administrator/Desktop/sport-analytics/cloudflare-empty-preview-20261103T084904Z/data`. The reported 676 stroke candidates, 473 unknown labels, null canonical actors and absent canonical points are diagnostic counts supplied by that owner, not independently scored accuracy. The current two typed display names `1`/`2` do not establish athlete or scoreboard-row identity. Use the existing pinned model without promoting side hypotheses into actors:

```bash
source ../gpu-env.sh
export PYTHONPATH="$PWD/engine/src:$PWD/sports/badminton/src:$PWD/apps/api/src:$PWD"
.venv/bin/python -m research.evaluation.bst_shadow_session \
  --data-dir /home/administrator/Desktop/sport-analytics/cloudflare-empty-preview-20261103T084904Z/data \
  --session 01M6GC737FR6Z4PDA74BPEZX4H --models "$PWD/models" \
  --output ../pluggable-pipeline-research-20261103/hylo-bst-cg-ap-shadow.json
```

For **new BST-0 acquisition**, the exact publisher evidence is the [MIT LICENSE](https://raw.githubusercontent.com/Va6lue/BST-Badminton-Stroke-type-Transformer/c93acfa736ed784ba7bea4ec9d360001dea9b728/LICENSE), 1,072 bytes, SHA-256 `2c42235c975d942f9b3d95028aea579a876b6870181a1086e6edbcb31890f918`, copyright Jing-Yuan Chang 2025. It grants rights to software/documentation. The [official README](https://github.com/Va6lue/BST-Badminton-Stroke-type-Transformer/blob/c93acfa736ed784ba7bea4ec9d360001dea9b728/README.md) links the author's Drive folder containing the identified BST-0 artifact. Neither that README nor the inspected public Drive listing states an additional checkpoint-specific license. No publisher checksum/model card was found. Therefore code reuse has an MIT source basis; **the separate weight-license scope is unverified**, including for noncommercial research. Do not write “publisher explicitly licensed BST-0 weights MIT” from this evidence. The reference project's license table is a secondary assertion, not that missing grant. Keep a new BST-0 adoption conditional on clarification or explicit artifact terms; it does not block the unchanged baseline/public-label comparison or already available CG-AP diagnostics.

## Review scope and outstanding evidence

Read the reference classifier, pipeline, taxonomy, fine-tune/stack scripts, exporter, validation sources, accuracy notes, third-party license inventory and exact public showcase JSON at the pinned revision. Inspected our rules/BST adapter, model registry, annotation protocols, participant/shot/reference evaluators and historical development notes. Checked official BST source/license/split metadata and public doubles-dataset metadata. Authored only this report; production, model registry, labels and preserved user files were not modified.

Not performed: GPU inference, tests, media review, checkpoint download/deserialization, new accuracy measurements, independent annotation adjudication, exact BST-0 hash/bytes or checkpoint-specific rights confirmation, dataset archive inspection, Kaggle license verification or any commercial-use clearance. These are recorded gaps, not implied successes.
