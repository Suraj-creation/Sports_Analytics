# Optional singles BST adapter — 29 October 2026

The official BST-CG-AP checkpoint now has a working, explicitly invoked shadow
adapter. The application's default shot classifier remains `stroke_rules_v0`.
The first development comparison shows a small improvement with many false
contact labels; it does not justify claiming reliable shot classification.

## Artifact and architecture

The [official inference example](https://github.com/Va6lue/BST-Badminton-Stroke-type-Transformer/blob/c93acfa736ed784ba7bea4ec9d360001dea9b728/stroke_classification/main_on_shuttleset/bst_infer.py)
uses `bst_CG_AP_JnB_bone_between_2_hits_with_max_limits_seq_100_merged_2.pt`.
It was downloaded from the author's linked
[ShuttleSet weights folder](https://drive.google.com/drive/folders/1D4172WZDJWPvpJdpaHDhy_cA-s8F-zR5),
file ID `1snqpEEww-GG6xFUBzkuctYAPHcBP360B`. The artifact is 7,514,133 bytes,
SHA-256 `997f43e52b20cb47517132c71d3e147d7d717a2d9651cfbe7651a5003bd66809`.
The model registry now has the exact URL, size and digest. The cached weights
and download provenance remain outside Git.

The [official architecture](https://github.com/Va6lue/BST-Badminton-Stroke-type-Transformer/blob/c93acfa736ed784ba7bea4ec9d360001dea9b728/stroke_classification/model/bst.py)
has 1,866,447 parameters in this checkpoint. Strict loading verified the
101×100 temporal embedding and 25×400 final head. Inputs are a 100-frame
sequence of two people, 72 pose/bone features per person, two shuttle image
coordinates, two court coordinates per person, and a valid temporal length.
This checkpoint does not support doubles.

`events/_bst_network.py` retains the required official classes, parameter names,
and forward operations. It omits unused architectures, profiling code and
initialization overwritten by strict checkpoint loading. Production inference
uses the existing PyTorch dependency. Original `positional-encodings==6.0.4`
and `torchinfo==1.8.0` were installed only in `/tmp/bst-reference-deps` to verify
the unmodified reference architecture. The [MIT license](https://github.com/Va6lue/BST-Badminton-Stroke-type-Transformer/blob/c93acfa736ed784ba7bea4ec9d360001dea9b728/LICENSE)
is retained in `events/bst_LICENSE.txt` with source attribution.

## Input contract

The adapter follows [official preprocessing](https://github.com/Va6lue/BST-Badminton-Stroke-type-Transformer/blob/c93acfa736ed784ba7bea4ec9d360001dea9b728/stroke_classification/preparing_data/prepare_train_on_shuttleset.py):

- Normalize joints by the player's bounding-box diagonal, centered on the box.
  Missing coordinates follow the original centered zero-sentinel convention;
  no missing pose is interpolated or invented.
- Project both ankle points through the frame's court homography, then average
  them. Map left-to-right to `[0,1]` and far-to-near to `[0,1]`. This uses athlete
  feet on the court plane, never a shuttle ground-plane projection.
- Admit exactly two observed players inside the court's original 0.01 soft
  normalized boundary. Sort far/top before near/bottom. When unavailable, zero
  all three modalities for that frame, including shuttle, as training did.
- Normalize observed shuttle pixel coordinates by image width and height.

The [dataset helpers](https://github.com/Va6lue/BST-Badminton-Stroke-type-Transformer/blob/c93acfa736ed784ba7bea4ec9d360001dea9b728/stroke_classification/preparing_data/shuttleset_dataset.py)
define 19 COCO bone vectors and the exact stride/truncate/zero-pad rule to 100
frames; the adapter preserves both. The 25-class order is unknown, then top-side
and bottom-side versions of: net shot, block, smash, lift, clear, drive, drop,
push, rush, cross net, short serve, long serve. English ontology mapping is
explicit; Chinese class names are not passed to an English alias lookup. The
two sides' class probabilities are summed for stroke type, while side
probabilities remain separate and never create a durable player identity.

The [training clip generator](https://github.com/Va6lue/BST-Badminton-Stroke-type-Transformer/blob/c93acfa736ed784ba7bea4ec9d360001dea9b728/ShuttleSet/gen_my_dataset.py)
uses the preceding contact through the following contact plus about 0.25 s,
limited to about 1.5 s before and 1.75 s after the target. Without a neighbor it
uses about 0.5 s on that side. The adapter reproduces the original integer-frame
arithmetic. The shadow runner obtains neighbors only from detected machine
rallies. It never uses labelled hit timestamps to build model input. Windows
must be complete, contiguous and confined to one camera shot.

## Executed checks

Twenty-one focused tests pass: original-image and court normalization, player
ordering, bones, exact temporal selection, zero padding, missing/reused pose,
invalid ankles, mixed shots, unsupported doubles, contact bounds, all 25 class
positions, refusal of a wrong checkpoint digest, camera/reference composition,
static versus tracked calibration, and machine-rally contact boundaries. Exact comparisons against
the full original architecture on three seeded sequences (lengths 1, 61 and
100) produced finite logits with maximum absolute difference **0.0**. This is
functional equivalence, not labelled accuracy. Preprocessing was also compared
with the original NumPy helper functions on three real baseline cache windows
(40, 100 and 151 frames). Maximum pose, court-position and shuttle differences
were below 3×10⁻⁸ from float32 rounding, including the court-y direction and
151-to-76-frame sampling rule.

Evidence under `data/audit-20261029/perception/` includes
`bst-architecture-parity.json`, `bst-preprocessing-parity.json`,
`bst-research/source-manifest.json`, and
`bst-shadow-baseline-0044.json`, and `bst-shadow-candidate-0044.json`. All inference in this stage used two CPU
threads. The 90 real baseline stroke windows took 4.60 seconds of model calls;
this is descriptive local timing, not a GPU throughput benchmark.

## Initial development comparison

The completed frozen baseline recording 0044 contains 90 current confirmed
stroke events. All 90 had an eligible temporal window; 28 fall inside the
published annotated rally windows. None of those 28 was dropped from scoring.
The evaluated population is 41 published hit anchors, with 9 matched
predictions, 19 false positives and 32 misses at the fixed ±0.2 s tolerance.

| Same baseline observations and detected contacts | Existing rules | BST shadow |
| --- | ---: | ---: |
| Known-family macro F1, including false detections and misses | 0.04524 | 0.05568 |
| Correct family at a matched anchor | 2 | 3 |
| Unknown predictions | 18 / 28 | 3 / 28 |
| Correct contact + family + court side | 0 / 41 | 2 / 41 |
| False detections assigned a known family | 7 / 19 | 16 / 19 |

The extra classifications include many wrong events. These results support
continuing controlled comparison, not enabling BST on every session. The
16 false contacts assigned a known family have median model probability 0.696
and maximum 0.917; a high class score does not establish that contact occurred.
Recording 0046 remains reserved; no
threshold, class mapping or feature policy has been tuned on it.

The first frozen candidate 0044 run has source fingerprint
`446e77f52f46ac27b1527d036dfdb65a800006cac4c6aede9275c9531108c06d`.
On its observations, 89 of 90 current stroke windows were eligible; the one
without any observed two-player pose remained unknown and lies outside the
annotated windows. All 28 evaluated predictions remain in scoring. Contact
counts are unchanged from baseline.

| Same candidate-v1 observations and detected contacts | Repaired rules | BST shadow |
| --- | ---: | ---: |
| Known-family macro F1 | 0.05934 | 0.05500 |
| Correct family at a matched anchor | 3 | 3 |
| Unknown predictions | 20 / 28 | 3 / 28 |
| Correct contact + family + court side | 1 / 41 | 2 / 41 |
| False detections assigned a known family | 5 / 19 | 16 / 19 |

BST does not improve family F1 against this repaired default and assigns more
labels to false contacts, so it remains an explicit shadow adapter. Later
anonymous-contact and player-ROI repairs are outside this frozen candidate;
their event population must be compared separately without changing the BST
feature policy or scoring only matched events.

The reference is provider-refined FineBadminton hit anchors, not independently
verified physical racket contacts. Pretrained training overlap is unknown.
Pose coverage in the 28 evaluated windows ranges from 10.9% to 100% of sampled
frames (median 91.6%); the sparse schedules and RTMPose model differ from the
original dense MMPose preparation. A calibrated classification confidence,
four-player classifier and persistent person identity are not supplied by
this adapter.

Reproduce the read-only development comparison with:

```bash
.venv/bin/python -m research.evaluation.bst_shadow \
  --snapshot data/audit-20261029/evaluation/baseline-0044 \
  --output data/audit-20261029/perception/bst-shadow-baseline-0044-rerun.json
```

The output must be a new path. The runner verifies the completed session,
event-log snapshot, per-cache digests, reference bindings and checkpoint. It
does not modify source sessions or accept held-out manifests.

For a completed real singles session without reference labels, use:

```bash
.venv/bin/python -m research.evaluation.bst_shadow_session \
  --data-dir data --session SESSION_ID \
  --output data/audit-20261029/perception/SESSION_ID-bst-shadow.json
```

This command uses exactly the same inference policy as the development
comparison. It reads verified cached weights and writes a new diagnostic JSON
outside the session stores, binding source/proxy media, events, cache files,
adapter code and checkpoint digests. It never appends predictions to the
session and makes no accuracy claim. A completed baseline session smoke test
produced 90 predictions identical to the benchmark's shadow families and
probabilities; artifact `bst-session-command-smoke.json` retains the bindings.

The API's `stroke_shadow` capability reports `shadow_only` for singles and
`unsupported` for doubles, with no active model claimed. The default `stroke`
capability continues to identify the heuristic classifier. The combined BST,
cache geometry and capability test run passes 35 tests.
