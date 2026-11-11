# OCR acquisition: demonstrated crop hazard and bounded causal limits

Production code and the active baseline are unchanged. This review separates a
generic engineering defect from an unproven explanation for Test 2's actual
missing readings. Original annotations are not inputs to either probe.

## Generic contract reproduction

`test_roi_expansion_contract.py` records **one failing case and two passing
controls** on current source. The deterministic OCR stub returns only fields
inside its supplied crop. A valid two-row21:19 board first locks a narrow ROI.
The next board retains that completed-game column and adds the current1:0
column to the right, still within the original acquisition corner. The reader
keeps returning21:19, resets its miss counter on each successful parse and never
sees the new column. Full-corner parser input correctly returns1:0. These are
synthetic engineering observations, not manufactured Part2 sporting labels.

The missing guarantee is acquisition completeness: the parser's “rightmost
current column” can only be rightmost among supplied pixels. A valid historical
column inside a permanently cropped ROI is indistinguishable from the current
column without additional context. Existing miss-based unlock cannot recover
when the wrong old column remains parseable. Existing committed spatial-parser
tests cover missing/invalid fields in supplied boxes, but not this ROI growth
and successful-stale-reading loop.

## Real source-pixel demonstration

`probe_real_reader_roi.py` ran the actual unchanged CPU OCR reader with two
explicit threads on the current baseline's proxy. It records actual raw text
boxes, confidences, pixel hashes, crops and ROI overlays under `real_roi_probe/`.
The sparse sequence is deliberately not called a replay of the full worker.

| Actual proxy frame | Retained narrow ROI result | Full top-left acquisition result |
|---|---|---|
|720|AXELSEN0 /ANTONSEN2; initial lock`[274,36,439,92]`|Same0:2|
|8794|16:20|16:20|
|11346|16:21, confidence0.99993|Abstains; raw numeric tokens are`165` and`211`|
|12604|16:21, confidence0.99993|13:2, confidence0.90548; tokens`16 13` and`21 2`|
|22924|16:21, confidence0.99994|Abstains; top current digit is absent from recorded OCR tokens|

The720 standalone reading/confidence matches the first actual cached successful
readout. The8794 narrow reading likewise matches cache. At12604 the source crop
actually contains only the old16:21 game column; the complete corner visibly
contains current13:2 to its right. Thus the acquisition hazard is demonstrated
on real pixels in addition to a synthetic contract.

**This sparse path is not proof of the full worker's ROI history.** The actual
cached reader continues16:20 through9484, then has no reading until12604, where
it returns the current13:2. Therefore the sparse probe's retained stale16:21
cannot be attributed to the active worker without replaying the missing source
calls and view eligibility. The first compact exploratory scan printed only
value changes; the corrected actual missing-read interval is after9484 through
before12604, not after8794. This distinction is preserved explicitly.

At11346 complete pixels still do not solve recognition: the OCR merges adjacent
game fields into three-digit tokens`165` and`211`. Those cannot be silently split
into sporting scores without a verified column/game layout; alternative partitions
exist. The current parser appropriately abstains. Full-corner22924 similarly
does not invent the missing top current digit or attach scores to branding.

## Isolated candidate and tradeoffs

`full_corner_candidate.py` preserves the original successful acquisition corner
instead of narrowing permanently to the detected board bounds. It retains the
existing read cadence, one OCR call per eligible frame, four-corner discovery and
max-miss unlock count. It introduces no numeric threshold, model change, logo
blacklist, video identity or frame exception. This class is not registered or
installed in production.

Three deterministic candidate controls pass: expanded current column is retained
with no extra call, unchanged board remains readable, and exactly the existing
miss budget unlocks and resumes corner search. This addresses the generic
synthetic hazard, without establishing full-video accuracy or an acceptable
performance tradeoff.

The real successful initial board's crop grows from165x56 to576x180 pixels,
approximately11.2times the area. Larger crops can increase OCR runtime, add
unrelated text and create more parser abstention. Full-corner acquisition alone
does not fix fused numeric tokens. A narrower untruncated horizontal-context
policy would be a separate experiment requiring its own positive/negative
controls; no such policy was adopted or silently substituted.

`replay_scheduled_ocr_gap.py` compares current and full-corner readers on every
actual cached main-camera-eligible source frame after9484 through12634, seeded
from successful720/8794/9484 observations. It records every call, ROI/miss/corner
state, readouts and call timing. The result belongs to
`scheduled_gap_replay/report.json` when complete. CPU weights are shared, current
arm runs first, and the GPU baseline shares the host: timings describe this
diagnostic workload, not a controlled production speed benchmark. Intermediate
pre9484 ROI state was not directly logged by the worker and remains a seed-state
limitation even if the later replay matches its cached output.

Do not deploy this candidate merely because its synthetic regression passes.
Use the completed replay, current baseline/all-reference findings and measured
resource tradeoff to decide whether a separate fix is justified. No current
Test 2 score/outcome gain or Test 1 preservation is claimed from these probes.

## Completed scheduled replay: ROI retention is not this gap's cause

The bounded actual-pixel replay is complete. It processes **105 eligible calls**
after9484 through12634 in each arm. Current-source output reproduces the actual
cached reading frames and rows exactly: only12604 and12634 return13:2; there are
no missing/extra readout frames or row mismatches. At12604 confidence0.90548 and
at12634 confidence0.99991 also match the observed current run.

The current reader fails9514,9544,9574 and9604, then **unlocks at9604**. It rotates
the four full acquisition corners and fails to produce a board until12604, where
it locks the now-wider`[274,34,474,95]` ROI. Thus it is not stuck indefinitely on
the initial narrow ROI in this actual gap. The successful seed state and later
output sequence are observationally consistent with the worker, while the
unrecorded intermediate pre9484 state remains an explicit reconstruction limit.

The full-corner candidate follows the same105 calls, unlocks at9604 and returns
the same two13:2 readings at12604/12634. It produces **no additional source
readouts and no measured gap-coverage improvement**. Its12634 confidence differs
(0.91399) because it uses the full corner rather than the successful smaller crop;
neither confidence is calibrated score accuracy.

| Bounded diagnostic measurement | Current reader | Full-corner candidate |
|---|---:|---:|
|Eligible OCR calls|105|105|
|Returned readings|2|2|
|First successful frame after gap|12604|12604|
|Wrong/extra/missing cached row comparisons|0|0|
|Sum of instrumented call time|238.466s|236.087s|

These sums include mostly identical unlocked-corner work, current-first order,
warm shared recognizer state and concurrent host activity. The small difference
does not establish a production speedup or estimate the extra cost of keeping
every successful board at full-corner size.

**Disposition:** retain the generic ROI-expansion hazard and its RED engineering
contract as a future issue, but do not promote the candidate as a Test 2 fix.
The observed Test 2 gap is not explained by persistent narrow-ROI lock. Actual
full-corner11346 shows one concrete token-fusion/parsing limitation; the entire
gap must not be assigned to that single sampled cause. Better acquisition/token
layout research needs source-bound examples and ambiguity controls rather than
invented score partitions. Production remains unchanged.

## Actual22924 positive countercontrol: reject candidate promotion

When the new prefix reached22924, its actual cache recorded `AXELSEN9 /
ANTONSEN12` with confidence0.96547, matching the selected source image. The
standalone full-corner call on that same proxy frame abstains because the upper
current digit was not recognized. Actual current ROI acquisition therefore has
a positive recognition result that the proposed full-corner-only path loses.
The generic stale-ROI synthetic contract does not outweigh this observed
countercontrol and the zero benefit in scheduled gap replay. **Reject adopting
the isolated alternative for Test 2.**

The later actual9:14 read at22954 was independently checked against original
source22945/22946/22954. The display jumps9:12→9:14 at the visible edit22946,
coincident with an actual cached scene barrier and epoch26→27. It is a legitimate
source-text observation across edited footage; treating it as one observed
scoring increment or inventing missing winners would be unsupported.
