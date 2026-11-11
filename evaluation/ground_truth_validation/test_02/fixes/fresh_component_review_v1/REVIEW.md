# Independent fresh Test2 component review

This read-only review consumed the **completed actual fresh Test2 neural worker**
and its guarded component diagnostics. The enclosing parity/visual/causal/report
orchestration is a separate completion scope. No production source, annotation,
original prediction or active runner helper was changed by this review.

The normal completed-run guard validates the exact source, worker/parent success,
full original perception catalog and unchanged frozen sources. All29,296
canonical1280×720 frames at30fps were freshly processed; `cached_perception_used`
is false. This review performs no further neural inference.

[Independent audit JSON](review.json) contains input hashes and detailed values;
[exact executed review](executed_review.py) preserves the audit implementation.
Original evidence: [fresh inference receipt](../../improved_v1/run/inference.json),
[executor receipt](../../improved_v1/run.executor.json),
[bound component metrics](../../improved_v1/bound_reference_diagnostics/component_reference_metrics.json),
[technical analysis](../../improved_v1/analysis/technical_analysis.json).

## Comparison with original perception and controlled semantic replay

All489 fresh cache chunks and corresponding original-baseline cache hashes were
validated. Every decoded raw frame observation matches the original baseline:
**29,296 equal frames; zero differing frames or fields**. This is an actual fresh
neural result, not reuse of the old perception cache.

| Compared output | Fresh versus completed controlled semantic replay |
|---|---|
| All816 contact compact semantic records | Exactly equal, including frame, support, class context and physical/attribution fields retained by audit. |
| All816 stroke compact semantic records | Exactly equal, including labels, provisional track, status and flight-time values retained by audit. |
| All4239 ambiguity payloads and frame ranges | Exactly equal. |
| All75 rally boundaries | Exactly equal. |
| Live highlight boundaries/selected score fields | Exactly equal; five selected events. |
| All saved metrics for all three interval references | Exactly equal, including boundary distributions/tolerances retained in component JSON. |

No unexpected semantic or raw-perception difference was found in these explicit
comparisons. Provenance event IDs differ between executions and are not physical
metrics. The controlled replay's missing schedule witness at119 remains unknown
in its own historical receipt. The fresh run now provides independent complete
execution evidence with the same raw observations and selected outputs; that
does not retroactively invent the missing historical witness.

The preserved [semantic effect review](../semantic_effect_review.md) describes
all original-before versus changed-engine differences. The fresh result confirms
those observed effects:16 nearby contact shifts, six unpaired removals, three
unpaired additions, six changed rally boundaries, and mixed reference-IoU
changes. It does not certify any removed contact as false or any new contact as true.

## Actual annotation-reference metrics

All seven Test2 annotation/supporting files are accounted for. The two shuttle
CSV files are byte-identical and represent one diagnostic reference population.
Player points and filled shuttle coordinates are generated legacy estimates;
coordinate binding permits disagreement measurements, not independent physical
accuracy. Coarse rally labels, generated rally intervals and generated winner
intervals remain separate references.

| Interval reference | TP / FP / FN | Precision | Recall | F1 | Mean IoU | Start MAE s | End MAE s | Duration MAE s |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Test2_Full.csv | 69 / 6 / 6 | 0.920000 | 0.920000 | 0.920000 | 0.830665 | 0.820290 | 0.584541 | 1.126570 |
| Test2_Full_rally.csv | 68 / 7 / 5 | 0.906667 | 0.931507 | 0.918919 | 0.849311 | 0.805392 | 0.695588 | 1.300980 |
| win_predictions.csv | 68 / 7 / 5 | 0.906667 | 0.931507 | 0.918919 | 0.849311 | 0.805392 | 0.695588 | 1.300980 |

All three F1 scores equal the preserved before-fix baseline. Coarse mean IoU
changes0.833215→0.830665, while generated rally/winner-interval mean IoU
changes0.848135→0.849311. The result has both favorable and unfavorable timing
changes. Winner interval agreement does not establish winner accuracy.

| Other diagnostic measurement | Population | Mean px | Median px | P95 px |
|---|---:|---:|---:|---:|
| Player bottom-center disagreement | 57305 | 3.461802 | 1.572611 | 11.764085 |
| Fresh-detector bottom-center disagreement | 24129 | 1.678630 | 1.117645 | 4.366445 |
| Shuttle raw disagreement when both present | 20199 | 5.991200 | 1.488654 | 3.521448 |

The50 out-of-image legacy shuttle coordinates are retained and flagged, without
clipping; the maximum729.122px disagreement includes invalid legacy coordinates.
These values are not physical localization error or player detection AP/IoU.
Frame300 court singles-floor-corner disagreement is mean1.550521px,
maximum2.195053px against one declared manual candidate. This single-frame
comparison does not establish all-frame calibration or3D shuttle accuracy.

## Raw and semantically admitted racket coverage

Every emitted abstention was joined to its exact current raw frame/owner and
candidate payload. All4239 joins are unique and preserve the original candidate
geometry, confidence and source frame. The gate changes semantic copies while
raw perception/cache/export evidence remains available.

| Coverage population | Count | Interpretation |
|---|---:|---|
| All cached person rows | 58452 | Includes current detector matches and propagated boxes. |
| Current detector-matched person rows | 24591 | Denominator differs from all person rows. |
| Raw racket-candidate rows | 20568 | 35.1878% of all person rows; geometric candidates, not verified rackets. |
| Frames with any raw candidate | 12060 | 41.1660% of29296 source frames. |
| Uniquely matched withheld rows | 4239 | 20.6097% of raw candidate rows; anatomical ambiguity, not physical negatives. |
| Remaining semantic candidate rows | 16329 | 27.9357% of all person rows; candidates not withheld by this narrow policy. |
| Frames with any remaining candidate | 11568 | 39.4866% of29296 source frames. |

Remaining candidates are **not certified equipment**. Banner/body/torso contours
remain unresolved, and true equipment can overlap a face. Policy admission
coverage must not be called racket precision/recall or contact accuracy.
The raw track-export count20559 differs from the20568 full-cache row population;
those export and cache denominators must not be silently substituted. A zero
count of racket-on-propagated-box rows is a freshness contract, not accuracy.

## Other component coverage and unavailable accuracy

Raw shuttle observations occur on20,256 frames. Player detection executes on
12,315 frames, yielding24,591 current detector-matched rows and33,861 propagated
or unmatched rows. Pose is present/current on46,816 rows;22,227 of those poses
are computed on propagated boxes. No pose source is stale, but pose freshness
does not establish joint accuracy. Exported projected court positions comprise
56,597 anonymous rows;32,805 use propagated boxes.

All75 predicted rally winners remain unknown. There are zero canonical accepted
point events and708 broadcast-score observations. These counts are not a verified
0–0 score. The816 predicted strokes include586unknown outputs:71.8137%unknown,
28.1863%known prediction coverage. Stable athlete re-identification remains
degraded because OSNet is unavailable and the baseline re-ID provider is absent.
All58,440 exported player rows have no canonical player ID.765 OCR readouts
carry AXELSEN/ANTONSEN labels; observed strings do not independently establish
identity, score correctness or point alignment.

All ten unsupported physical-accuracy categories were independently checked for
`status=unavailable` and `value=null`:

| Metric family | Status | Reason |
|---|---|---|
| player_AP_mAP_IoU | unavailable | Independently reviewed boxes and complete positive/negative coverage; supplied generated points are not boxes. |
| tracking_IDF1_HOTA_ID_switches_fragmentation | unavailable | Reviewed persistent athlete identities, boxes and visibility; two generated detection slots are not persistent IDs. |
| pose_PCK_OKS | unavailable | Reviewed keypoints and joint visibility, skeleton convention and scale. |
| shuttle_physical_localization_PR | unavailable | Independent reviewed coordinates/visibility; filled model estimates do not identify interpolated frames. |
| racket_contact_PR_F1_temporal_error | unavailable | Reviewed contact/racket times and negative windows, not rally-level labels. |
| stroke_per_class_PR_F1_confusion | unavailable | Complete per-contact stroke taxonomy and labels; a single ball_types field per coarse rally is insufficient. |
| winner_outcome_accuracy_PR_F1_confusion | unavailable | Verified symbolic Player A/B identity and source-bound adjudicated outcomes; win_predictions is generated. |
| score_sequence_accuracy | unavailable | Reviewed broadcast identity, point alignment and score sequence, accounting for edited-video omissions. |
| highlight_quality | unavailable | Reviewed highlight relevance/boundaries; rally overlap and execution are not relevance accuracy. |
| player_analytics_accuracy | unavailable | Reviewed participant identities and metric-specific physical movement/event labels. |

Unavailable metrics are not scored zero. No new human ground truth, AP/mAP,
IDF1/HOTA, PCK/OKS, contact F1, stroke confusion matrix, winner accuracy or scoring
accuracy is inferred from successful execution or generated-reference agreement.

## Runtime, GPU use and model provenance

| Item | Actual fresh result |
|---|---:|
| Worker elapsed seconds | 3381.98716597585 |
| Parent elapsed seconds | 3393.230042782612 |
| Worker source fps | 8.6623628542206 |
| Parent source fps | 8.63366162347657 |
| Physical GPU index | 1 |
| Sampled worker GPU peak MiB | 2122 |
| Sampled worker-tree peak RSS bytes | 3162554368 |
| Worker maximum RSS bytes | 3194896384 |
| Worker final CPU seconds | 37556.78703 |
| Resource samples | 1638 |
| Sampling errors | 0 |
| Media ready seconds | 2.449088459368795 |
| Model staging seconds | 1.6798189408145845 |
| Component initialization including models seconds | 8.922011024784297 |

The fresh worker used physicalGPU1, **NVIDIA GeForce GTX1080Ti**. RFDETR-Small
and RTMPose executed via ONNX CUDA; TrackNetv3 executed via torch-CUDA FP16.
The receipts record no requested-to-actual backend fallback for these models.
Court geometry, scene continuity, association and OCR include CPU work. Thus GPU
use does not make every stage GPU-bound or make wall time pure neural latency.
The worker takes56.37minutes for16.28minutes of source footage, around3.46×
source duration. Pure neural-only throughput and isolated model-loading latency
are explicitly unavailable.

| Measured stage invocation scope | Calls | Accumulated seconds | P50 ms | P95 ms |
|---|---:|---:|---:|---:|
| court | 489 | 153.922 | 306.088 | 396.013 |
| content_continuity_and_players | 489 | 1441.222 | 3311.936 | 3617.652 |
| shuttle | 489 | 427.121 | 847.660 | 1099.133 |
| players | 489 | 128.370 | 242.848 | 542.680 |
| ocr | 489 | 451.860 | 936.343 | 1059.779 |

These are saved invocation wall-time scopes; some overlap. They must not be
summed into an invented pure-neural budget or compared as a controlled speedup.
GPU/RSS peaks are sampled and can miss short peaks; tree RSS may count shared
pages more than once. CPU resource competition from unrelated jobs is not
excluded by these receipts. Decode/perception/cache runner scope is2790.788s.

There is a **redundant reporting-field limitation**:
`bound_reference_diagnostics/component_reference_metrics.json.executed_models`
is null because that summary lookup uses `worker_info.loaded_models`, while the
worker receipt exposes `models`. This does not indicate missing or failed
inference. Actual, verified provenance is available in
`run/inference.json.models`, `run/inference.json.execution_backends`,
`analysis/technical_analysis.json.model_sets_from_actual_caches`, and
`analysis/technical_analysis.json.models_verified_during_analysis`.
Model identities and hashes are preserved in the independent JSON review too.
No immutable matrix/helper was edited to change this field during the active run.

RFDETR-Small1.4.2, RTMPose-M body7 and TrackNetv3 checkpoint hashes are verified.
OCR package detector/classifier/recognizer weights are separately hashed.
OSNet and RacketVision are explicitly unavailable, not claimed loaded; no
alternative model performance is invented. The source plan, profiles, applied
fix receipt and environment remain the authoritative implementation/configuration
provenance for the fresh run.

This review establishes actual fresh execution, unchanged raw observations,
reproduced semantic effects and explicit metric limitations. It does not replace
the enclosing final completion receipt, final consolidated matrix, or physical
ground-truth accuracy requirements.
