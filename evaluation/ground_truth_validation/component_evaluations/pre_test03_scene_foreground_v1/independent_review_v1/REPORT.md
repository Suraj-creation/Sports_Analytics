# Independent review of the isolated scene-foreground candidate

The revised source has no additional blocker identified in this review before the planned source-prefix controls. Fifteen independent synthetic contract checks pass against the exact eight production-file hashes in [probe_result_v1.json](probe_result_v1.json). This is a review of an unbenchmarked working candidate, not a source-freeze receipt, physical scene-accuracy result or acceptance of the pipeline for Test2/Test3.

The source inspected was `/home/administrator/Desktop/sport-analytics/test03-scene-continuity-20261112`, compared with the preserved c7cf871c control. This agent made no production edits, ran no neural inference, consumed no video or annotations in the contract probe, and changed no historical evaluation artifacts. Root owns the corrections and final source freeze; other agents own the focused tests and chronological source-prefix harness.

## Confirmed findings and revised behavior

| Finding during review | Consequence in the earlier draft | Revised behavior independently checked |
|---|---|---|
| Image layout used participant `admitted_indices` | Two identical raw current boxes, with one outside an expired court lease, produced a tracking barrier despite complete positive image correspondence | Version2 decisions record all raw `layout_indices` separately from unchanged participant admissions. Complete injective image correspondence vetoes a reset with all, one or zero court-admitted participants, in two- and four-region controls |
| `carry` accepted older frames and did not prune memory | An estimate expired at31 could reappear after `carry(1)` | Strictly increasing carry frames; expired observations are removed and cannot revive |
| Historical decision versions could be bound to new raw evidence | A legacy decision could bypass new supporting-key semantics | RawV3 requires decisionV2; historical rawV2 requires decisionV1 |
| Historical nonunknown region bound broadened | Old decisionV1 could acquire five-to-eight-region authority never supported by its original contract | Historical nonunknown decisionV1 retains2–4; new decisionV2 can bind2–8 qualified witnesses |
| Only the preferred channel cohort was retained | Complete layout correspondence on one independently qualified channel could hide another qualified channel's innovation | Each channel first qualifies independently; the supporting set retains the union of qualified cohorts. One appearance witness plus one correspondence witness still cannot manufacture a quorum |
| Background reliability overwrote missing regional evidence | With zero features in both regions, V3 incorrectly reported `measured` alongside `insufficient_region_features` | Unknown regional evidence remains `unknown` through observer and codec |

These are deterministic source-contract findings. Their correction does not measure a reduction in physical false cuts or establish optical-flow robustness on real footage.

## Data-flow and provenance review

- `CourtForegroundMemory` is separate from participant tracking authority. Fresh court-origin proposals seed image episodes; unique current raw IoU correspondence refreshes their image boxes. It does not add persons, pose observations, physical identities, court membership, contact actors or points.
- Empty fresh proposals are **not** physical negative labels. The agreed policy retains an unmatched scene-only estimate for at most the existing one-second missing-fresh allowance. Its `detector_observed=True` records the attempted detector observation, while `detector_matched=False` distinguishes the estimate. Subsequent carries remain unobserved, do not renew age, and expire at31 for30fps. The initially suggested immediate deletion was not adopted; treating an empty model output as confirmed absence would be an unsupported inference.
- Cuts reset foreground memory; excluded/replay views reset it separately; stale unscheduled carries clear it. Opaque image keys are not reset to old values, preventing old per-key adaptive history from inheriting a new episode after a reset. Detached snapshots retain their original frame and boxes.
- The pipeline stores current-frame foreground regions separately and passes only the immediately preceding frame's region inventory into content continuity. Provider fallback still uses the existing participant-based stream when the optional scene-only port is unavailable.
- V3 retains bounded region measurements and explicitly identifies qualifying supporting keys. The codec recomputes per-channel cohorts using recorded actual adaptive-ratio/intensity parameters, rejecting forged key/flag combinations. Plugin decoding additionally compares those parameters with the producer content configuration/defaults; this binding was confirmed in source.
- DecisionV2 preserves raw current boxes, scores, source-frame/image hash/model provenance, participant admission and separate image-layout candidates. Binding recomputes unique geometrical correspondence. Unknown decisions preserve an explicit experimental raw-hypothesis barrier fallback; they do not become verified edit truth.
- Relevant identities have changed: tracking contract/model version3; content provider version3 with V3 output declaration; serialized perception codec22; whole pipeline version6; foreground policy identity included with tracking metadata. Historical decision/raw parsing remains distinct. Root must record the final source hashes and run new output directories rather than reinterpret c7 caches with the new implementation.

## Independent smoke scope

The [probe](contract_probe.py) uses actual observer/provider/memory implementations with deterministic low-level flow measurements. Its15 passing controls cover:

- Complete raw current image correspondence, independently of all/one/no participant admissions, for two and four regions.
- Duplicate raw current proposals yielding explicit ambiguous correspondence and the documented experimental fallback.
- Strict decision/raw version pairing and forged witness-subset rejection.
- Unknown status with background features but no measurable foreground features.
- Bounded unmatched estimates after empty fresh proposals, carry expiry, rejected rewind and detached reset keys.

All eight inspected production-file hashes were unchanged across that probe. The receipt identifies the actual imported source root. The probe is intentionally not a neural pipeline run, image detector benchmark or substitute for the independently owned focused tests.

## Remaining acceptance requirements and risks

The separate stream may follow an official after an image-region handover. This must remain harmless to participant authority and visible in the source provenance. Two simultaneous occlusions or detector failures can still satisfy a raw scene hypothesis; ambiguous/missing layout evidence retains the explicit experimental reset fallback. Therefore there is no claim that all false cuts are fixed.

The source-prefix controls must recover Test1 edits7857/8106 and remove the7857–7859 stale box while preserving the court lease and immediate-birth improvements. Test2 controls must retain official rejection and both athletes around6492, true edit6307/11346, and no-reset controls7703/23639. Those controls use real source pixels and exact detector evidence and are owned separately; this review does not pre-empt their results. Complete fresh Test1/Test2 runs and unchanged annotation/evaluation methods remain required before a broader accuracy or acceptance claim.

No Test3 data was accessed. Root's final freeze and real-source regressions remain the next gates.
