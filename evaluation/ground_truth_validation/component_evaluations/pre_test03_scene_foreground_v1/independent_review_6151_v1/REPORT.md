# Independent source review: Test2 frame6151

**The additional6151 barrier corresponds to a genuine same-camera edited jump in the supplied video. It is not a newly observed false barrier.** This is an agent visual diagnosis tied to exact source pixels and recorded decisions; it is not an independently labelled scene-accuracy dataset or a false-positive/recall measurement.

At frame6150 the blue athlete walks near the far baseline and the red athlete stands near the bottom-left edge. At6151 both athletes jump to an active exchange near the centre/net. The broadcast changes10:13→10:14 at that same boundary. Neighbouring6148–6150 frames show continuity before the transition, and6151–6154 retain the new exchange afterwards. These visible scoreboard values do not bind anonymous track episodes to names, reconstruct a point decision or manufacture winner ground truth.

| Canonical frame | Time(s) | Exact proxy PTS / timebase | Visual state |
|---:|---:|---|---|
| 6150 | 205.000000 | 3148800 / (1/15360) | Far blue athlete and bottom-left red athlete; displayed10:13 |
| 6151 | 205.033333 | 3149312 / (1/15360) | Central active exchange; displayed10:14 |

Source images: [6150](frame_06150_source.png), [6151](frame_06151_source.png), [6148](frame_06148_source.png), [6149](frame_06149_source.png), [6152](frame_06152_source.png), [6153](frame_06153_source.png), [6154](frame_06154_source.png).

## Source and execution binding

- Original source SHA256: `4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a`.
- Retained canonical proxy SHA256: `2841ee54fb0b6d28c2a57e89293ba4530173980635c21aa8d08f60f52931b6cd`;1280×720,30/1fps,29,296frames.
- This review rehashed that proxy and verified its association with the completed original Test2 worker, original completed parent/worker hash binding and cache catalogue. The original large source was not downloaded or rehashed again. Every extracted frame's exact PTS, timebase and BGR pixel hash matches its closed prefix row. PNG hashes and consumed input hashes are preserved in [source_extraction_receipt.json](source_extraction_receipt.json).
- The reviewed prefix is the closed `prefix_v1` candidate`7ed2f731e2d58273e381710226500f30d47e00bb`. Its recorded candidate files are verified against immutable Git objects, rather than importing its now-changing checkout or pretending a current ROOT is the old runtime.
- The prefix uses RF-DETR, ROI, ByteTrack and content continuity with the preserved original geometry/rate schedule. It omits pose, shuttle, engine/FSM feedback and end-to-end inference. The5505–6510case reports374 seeded detector observations,375 unique observations and one fresh neural detector call. This read-only review performs no model inference.

## Why the three arms differ

| Arm at6151 | Prior image context | Scene result | Detector / participant result |
|---|---|---|---|
| Original bounded control | Two athlete regions plus a static official | Unknown: official has only4features; old conjunction requires measurements from every region | No forced detector call;3carried participant boxes |
| c7 bounded control | Only one court-admitted participant remains | Unknown: fewer than two prior regions | No forced detector call;1carried participant box |
| New foreground bounded control | Three separate image contexts retained | Two independent athlete regions qualify; static low-feature official is not a supporting witness | Source-bound current detector probe; barrier and two fresh athlete births |

The independently verified original **full-NN** cache also misses the edit: content epoch stays8, detector execution isfalse at6151, raw status is`unknown/insufficient_region_features`, and no layout decision is recorded. This confirms that the original bounded control's missing barrier is consistent with the preserved actual run; it does not make the bounded c7/new arms full-pipeline runs.

The new raw hypothesis retains80background features with0.9625consistent fraction. Its two supporting athlete regions have47/31features, correspondence discontinuities39.953480/17.815670 and appearance ratios4.225510/4.443779. Both independently meet the unchanged recorded ratio3/intensity15 policy. The static official has4features and does not qualify. All ten entries in the two-support-region × five-current-raw-box IoU matrix are exactlyzero. The recorded current layout barrier therefore agrees with the independently observed layout jump.

At6151 all variants identify the same source image/PTS. No hard camera cut is flagged: this is an edit within the same camera view. The new policy forces current perception on a frame that otherwise follows the preserved two-frame detector cadence. The new prefix's local content epoch0→1 is local to this bounded window; it must not be equated with the original full-run epoch8.

Complete source-bound rows, supporting region measurements, raw detector boxes, all variant decisions and the original cache records are in [decision_evidence.json](decision_evidence.json). No earlier report, annotation, prefix or evaluation matrix was modified.

## Separate unresolved Test1 ambiguity and bounded-memory proposal

The same prefix still misses Test1 edit7857. Its far image key is removed at7806 when two raw proposals overlap the last unambiguous7800region. Recomputing the existing0.3IoU gate gives:

| Frame | Age from last unambiguous7800 observation | Qualifying overlaps |
|---:|---:|---|
| 7806 | 6frames | Two raw proposals:0.636083 and0.360303 |
| 7812 | 12frames | One raw proposal:0.558191; second candidate0.216148 is below the existing gate |

A bounded quarantine is a reasonable **candidate contract to test**, rather than immediate destruction of image context: retain the prior box and its last unambiguous observation timestamp through ambiguous current proposals, mark it unmatched, and renew neither image age nor participant authority. Do not select an ambiguous proposal or seed overlapping duplicate scene keys from those same proposals. If the original unique correspondence reappears before expiry, it can provide a new fresh image observation; persistent ambiguity must still expire after the existing one-second missing-fresh allowance, including carried frames. Resets must clear it and avoid reusing adaptive-history keys.

This would bridge the observed6frame ambiguity without extending the participant court lease. It remains a scene-only estimate and could be visually wrong during occlusion or an edit. V3 must keep independent-region checks, raw source-pixel measurements and current-layout corroboration; no confidence, time or IoU threshold should be tuned to7806. The quarantine behavior and complete7857source prefix must be verified in a separately preserved candidate arm. This review applies no production change and does not claim that the proposal already recovers7857.

## Disposition

Retain6151 as a newly recovered **source-reviewed true edit control**, alongside6307. Do not count it as a false barrier, and do not extrapolate this review into aggregate scene precision/recall. The remaining missed7857edit and all required source/full-NN regressions still control candidate acceptance. No Test3 data was accessed.
