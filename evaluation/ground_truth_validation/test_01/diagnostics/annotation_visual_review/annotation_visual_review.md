# Test1 source-frame annotation alignment review

This is a qualitative diagnostic review of13 source frames. It is not fresh model inference, exhaustive visual review, independently adjudicated physical ground truth, or a certification of winner/contact/court accuracy. Original video and annotation files are unchanged.

Source: `/home/administrator/Desktop/sport-analytics/Sports_Analytics/data/benchmarking/test1/Test1_Full_rev.mp4`. SHA256 `877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6`.

## Exact media/time/coordinate handling

Frames were decoded sequentially from the retained original with PyAV and2 CPU decoder threads. Every captured source PTS/time base was saved in [frame_metadata.json](frame_metadata.json); all selected times exactly equal zero-origin source-frame/30. Original1920×1080 BGR frames were resized to1280×720 with OpenCV INTER_AREA. Legacy court/player/shuttle coordinates were drawn unchanged in that declared1280×720 space. No original time shift or fitted coordinate transformation was applied. Source pixel hashes and rendered PNG hashes are preserved.

Green: legacy manual court corners. Magenta: legacy net cable/post points. Yellow: legacy player slot1. Cyan: legacy player slot2. Red: legacy shuttle only when its table says Visibility1. Missing player coordinates remain missing; no points are fabricated. Static court geometry is intentionally shown outside its one declared frame only as a reference overlay, with that limitation printed on the panels.

## Findings

### 1. Court geometry is plausible as a singles rectangle at the declared frame

[Declared-frame overlay](frame_08634_legacy_overlay.png), sourceframe8634/287.8s, shows TL(448.204,303.934),TR(825.664,300.246),BR(930.173,653.115),BL(344.925,655.574) near the visible inner singles sidelines/baselines. The outer doubles near-baseline corners extend farther left/right. The cable endpoints aroundy306 and post-floor bases aroundy430 are plausible for this camera. This supports the hypothesis that the manual reference describes singles boundaries, not a generic doubles rectangle. It does not quantify point error or certify every corner; exact click adjudication and component-specific coordinate binding remain separate work.

![Declared court frame8634](frame_08634_legacy_overlay.png)

### 2. Legacy player slots are not persistent athlete identities

[Frame0](frame_00000_legacy_overlay.png) shows slot1 near the navy athlete’s feet and slot2 near the far white athlete. At [frame8634](frame_08634_legacy_overlay.png), slot1 is near the far white athlete and slot2 near the near navy athlete. At [frame9000](frame_09000_legacy_overlay.png), slot1 is again near the near navy athlete. These positive examples support coordinate plausibility while directly contradicting a fixed slot1=physical personA/slot2=physical personB assumption. The near navy jersey visibly contains INTANON/THAILAND text; no face-based identity identification was used. Neither slots nor this text alone certify the annotation’s symbolic PlayerA/B convention.

The source implementation explicitly calls these bottom-center detector points: `legacy/pipeline/analysis/player_detection.py:201`. Point positions alone do not supply bounding-box GT for AP/mAP or stable identity GT for IDF1/HOTA.

### 3. Supplied running scores are not literal broadcast score observations

At [frame8106](frame_08106_source_resized.png), [8628](frame_08628_source_resized.png), [8634](frame_08634_source_resized.png), [8640](frame_08640_source_resized.png), and [8683](frame_08683_source_resized.png), the visible broadcast graphic reads `AN S.Y.20 / INTANON20`. Yet coarse Test1 row19 (270–288s) reports terminal10:9; partial Full2 row19 (270.2–287.6s) reports9:10. Thus those CSV score fields cannot be used directly as synchronized displayed-score GT at that interval. Selected-rally cumulative scoring, edited-out points and label conventions are hypotheses requiring provenance review; this panel review does not choose one.

At [frame9000](frame_09000_source_resized.png) and [9967](frame_09967_source_resized.png), the visible display is `AN S.Y.21 / INTANON20`. This is observed text change across sampled views, not a certified assignment of an intervening rally’s winner. Continuous clip review must establish every action and transition before adjudicating the primary-vs-Full2 winner conflict. No label was rewritten.

![Broadcast20:20 at287.6s](frame_08628_source_resized.png)

![Broadcast21:20 at300s](frame_09000_source_resized.png)

### 4. Court-frame validity cannot persist blindly through camera cuts

[Frame8640](frame_08640_source_resized.png) is the main court view. [Frame8683](frame_08683_source_resized.png) is a closeup of the navy athlete; the camera has cut somewhere between those samples. The Full2 next candidate interval begins at8683/289.433s, already in a closeup. A static court polygon applied there would have no physical floor meaning. This diagnoses an annotation/context alignment requirement; it does not prove that the current pipeline failed to invalidate geometry. Missing legacy player coordinates at8683 remain explicit in the metadata.

![Closeup at8683](frame_08683_source_resized.png)

### 5. Opening preparation versus rally start needs temporal review

Frames0 and150 show preparation. At [frame243/8.1s](frame_00243_legacy_overlay.png), the near player’s racket/arms are raised and the legacy visibility/shuttle output is present. At [frame300/10s](frame_00300_legacy_overlay.png), the far player is in an overhead posture. This is insufficient to certify first serve/contact or the exact physical start of play from isolated stills. Legacy generated start243 and the coarse8s boundary are references, not newly confirmed impact frames.

## All sampled frames

| Frame | Seconds | Raw resized source | Legacy overlay |
|---|---|---|---|
| 0 | 0.000000 | [Raw](frame_00000_source_resized.png) | [Overlay](frame_00000_legacy_overlay.png) |
| 150 | 5.000000 | [Raw](frame_00150_source_resized.png) | [Overlay](frame_00150_legacy_overlay.png) |
| 243 | 8.100000 | [Raw](frame_00243_source_resized.png) | [Overlay](frame_00243_legacy_overlay.png) |
| 300 | 10.000000 | [Raw](frame_00300_source_resized.png) | [Overlay](frame_00300_legacy_overlay.png) |
| 715 | 23.833333 | [Raw](frame_00715_source_resized.png) | [Overlay](frame_00715_legacy_overlay.png) |
| 8106 | 270.200000 | [Raw](frame_08106_source_resized.png) | [Overlay](frame_08106_legacy_overlay.png) |
| 8460 | 282.000000 | [Raw](frame_08460_source_resized.png) | [Overlay](frame_08460_legacy_overlay.png) |
| 8628 | 287.600000 | [Raw](frame_08628_source_resized.png) | [Overlay](frame_08628_legacy_overlay.png) |
| 8634 | 287.800000 | [Raw](frame_08634_source_resized.png) | [Overlay](frame_08634_legacy_overlay.png) |
| 8640 | 288.000000 | [Raw](frame_08640_source_resized.png) | [Overlay](frame_08640_legacy_overlay.png) |
| 8683 | 289.433333 | [Raw](frame_08683_source_resized.png) | [Overlay](frame_08683_legacy_overlay.png) |
| 9000 | 300.000000 | [Raw](frame_09000_source_resized.png) | [Overlay](frame_09000_legacy_overlay.png) |
| 9967 | 332.233333 | [Raw](frame_09967_source_resized.png) | [Overlay](frame_09967_legacy_overlay.png) |

## Next bounded investigations

1. Review continuous source clip roughly260–305s with exact PTS, including all score updates/cuts, to establish whether coarse row19 and Full2 row19 denote the same physical point and what symbolicA/B mapping applies.
2. Review initial0–15s temporal sequence to distinguish setup/practice racket motions from first serve/contact; do not backdate a physical rally solely to a generated-table start.
3. Bind legacy court/player/shuttle coordinate semantics independently. Treat singles/doubles correspondence as a declared hypothesis; do not force the wrong rectangle to obtain an error metric.
4. Use player-slot reassignments as diagnostic regression examples for adapters that might equate slot indices with physical participants.
5. Keep this agent inspection separate from newly reviewed human GT and preserve all conflicting original labels.

The extraction’s initial diagnostic attempt encountered empty player coordinates at8683; its error log is retained. The successful renderer explicitly skips drawing missing points, retaining their raw empty fields in metadata. This was an overlay-tool handling correction, not a pipeline or annotation change.
