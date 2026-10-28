# Task 2 continuation: identity safeguards and source-bound measurement

The implementation now refuses named propagation through substantial competing
player-box overlap. Anonymous candidates remain available. New tracking and
shot evaluators expose identity fragmentation, missed observations, abstention,
spurious attributed events and joint contact/family/hitter errors. This is a
verified incremental improvement, **not completion of high-accuracy Task 2**.

## Implementation

`analytics/automatic_individual.py` previously filtered out every competing track
before checking a seed-to-shot interval. Smooth box motion therefore passed even
when partners overlapped and a tracker could have exchanged their identities.
The named-estimate continuity check now retains competing same-frame observations
and abstains at box IoU >= 0.3 for visible, confident, valid competing tracks.
It checks the inclusive interval, so separation cannot erase an earlier overlap.
A separate seed reviewed after separation can establish a new supported interval.
The guard applies only to named propagation; it preserves anonymous candidates,
reviewed counts, event reconciliation and unrelated players. The threshold is an
uncalibrated abstention heuristic. Missing competitors, low-confidence boxes and
unseen crossings remain limitations. This does not relink fragmented episodes or
prove that any numeric tracker ID denotes a particular person.

`research/tracking_benchmark.py` adds sampled localization P/R, four-player
coverage, global identity assignment/IDF1, sampled switches/fragments and explicit
missing/ambiguous support. Matching identity names once over the complete window
penalizes fragmentation; per-episode manual rebinding cannot conceal it. Identity
overlap counts are independent of local localization tie-breaking. Switches are
counted only for uniquely localizable samples. The extractor hashes source/proxy
bytes, event bodies and latest player chunks, namespaces IDs by generation/live
birth, invalidates exits/reset/reuse/retraction boundaries, and rejects concurrent
chunk revisions. It never writes sessions or reviews. See the
[tracking protocol](../../../../research/tracking-annotation-protocol.md).

`shot_benchmark.py` and `participant_benchmark.py` version 2 validate ontology
keys, expose known-family support/F1 separately from legacy unknown-as-class
metrics, and report per-person event P/R plus joint contact/family/hitter P/R/F1.
An all-unknown label set cannot support known-family classification. Extra shots
credited to a person lower precision. Existing conditional metrics remain for
comparison, with property-specific eligibility and explicit uncertainty.

## Source-video review and annotation quality

The reviewed input is the existing ten-second doubles clip from parent 60–70 s,
250 frames at 25 fps, 1280x720. Source SHA-256:
`e50e00223bf41468ac4c913ff5a7647d909563326d256be8037fe79fedace640`.
Canonical proxy SHA-256:
`316120c31b96e17aeebc4d8b3977affbdbb46c00637069cd4147b51d928d6b4c`.

Sixteen source frames (0,15,...,225) contain four visible people each. An initial
AI draft was frozen before reading model boxes. A mismatch audit identified
coordinate-reading errors in several draft boxes. A separate AI reviewer then
annotated single source frames without seeing model outputs or previous boxes;
frame 150 was additionally checked at full height. **Both revisions are retained**.
The independent revision is used below. The coordinator had already seen model
outputs when requesting that second pass; this is disclosed in its metadata.
The revised labels are still AI-only diagnostic annotations, never human ground
truth or held-out evidence. Differences between annotation revisions are not
code improvements. Initial-draft reports are retained for audit, not conclusions.

The reviewer followed anonymous people seeded once by initial appearance and
position, rather than renaming partners at each position. Body boxes are manually
read to roughly 10px, with uncertain blurred/occluded extremities and overlap at
frame 180. Every fifteenth frame cannot validate intervening continuity. Source,
proxy and HLS each contain 250 frames; sampled source/proxy matching selected the
same frame index at all 16 samples, and sampled proxy/HLS pixels agreed exactly
in the checked court crop. See `timeline-verification.json`.

An independent source-only review of every frame 50–99 found two internal
motion/return candidates and two boundary actions. Exact contact and fine family
were blurred or unresolved. That partial review is saved in
`../annotations/doubles-62-64-blind-motion-ai-draft.json`; it deliberately declares
`exhaustive: false`. It cannot supply shot precision, recall, family F1, or hitter
accuracy. No partial review was promoted to ground truth to make a score possible.

## Matched GPU experiment

Two fresh isolated runs used archived main `449ec48`, the same source/proxy,
calibration and existing models/environment on GPU 1 (GTX 1080 Ti). The first
uses the existing profile, detector stride 2 in play/6 idle. The second changes
only detector cadence to every frame in play/idle, leaving replay disabled.
The experiment copies the profile outside production and reuses existing model
files. Source session results and production profile are not changed.

Agreement against the **same revised AI draft** at IoU >= 0.5:

| Measurement | Main 449ec48 | Denser detector experiment |
| --- | ---: | ---: |
| Visible labelled person boxes | 64 | 64 |
| Delivered track boxes | 60 | 60 |
| Matched / spurious / missed boxes | 59 / 1 / 5 | 60 / 0 / 4 |
| Sampled box precision / recall | 98.33% / 92.19% | 100% / 93.75% |
| Sampled global IDF1 | 91.94% | 93.55% |
| Samples localizing all four | 14 / 16 | 15 / 16 |
| Sampled uniquely-localizable switches | 0 | 2 |
| Truth boxes with ambiguous localization assignment | 2 | 0 |
| Fresh detector-run frames | 109 / 250 | 250 / 250 |
| End-to-end wall time | 21.149 s | 23.843 s |
| Sampled process GPU memory peak | 2126 MiB | 2124 MiB |

These are **draft agreement and single-run resource diagnostics**, not verified
tracking/shot accuracy or a controlled speed study. Zero sampled switches is not
proof of uninterrupted identity; main excludes two ambiguously localizable boxes
from switch counting. Compatible identity keys are candidate keys, not a measured
fragment count. Dense detection improves this draft's box score
slightly but creates two sampled identity switches and costs ~12.7% more wall
time. It is **not promoted to the production default**. The new overlap safeguard
does not change these anonymous inference outputs: it protects subsequent named
estimates and is validated by the separate crossing/re-seeding regression.

## Verification and preservation

The full engine, badminton, API and research regression suite passed 769 tests
with 27 existing FastAPI/Starlette deprecation warnings. Focused fixtures cover
swaps despite identical localization, per-frame fragmentation, missing frames,
unknown identities, duplicate predictions, source binding, local matching ties,
reused/retracted birth references, concurrent track revisions, overlap at seed
and shot boundaries, selective abstention, and re-seeding after separation.
Additional targeted score-accounting fixtures and Ruff checks accompany the
final source. No frontend component or API route was redesigned.

All five original event ledgers are checked against the previously saved hashes.
Inference writes only new isolated output directories under
`/home/administrator/Desktop/sport-analytics/task2-validation-20261028/`.
The backend and Cloudflare tunnel remain stopped. Existing primary-checkout
changes and `apps/web/dist.old/` are preserved.

## Reproduction

On the configured GPU host, source the existing environment and use its `.venv`.
Set `PYTHONPATH` to the checked-out `engine/src:sports/badminton/src:apps/api/src:.`
when working from an isolated source checkout.

```sh
source /home/administrator/Desktop/sport-analytics/gpu-env.sh
python -m research.tracking_benchmark \
  --annotations docs/testing/task2/annotations/doubles-tracking-60-70-independent-ai-draft.json \
  --session 01M60K38M17QTHTE7QFC1RDG0N \
  --data-dir /home/administrator/Desktop/sport-analytics/task2-validation-20261028/fresh-main/data \
  --allow-draft
```

Repeat against `fresh-dense/data` using the identical annotations. Reports include
annotation/prediction hashes, media binding, event-log hashes and selected track
chunk hashes. Fresh inference uses the existing
`docs/testing/task2/continuation/fresh_session_benchmark.py`, with `--runtime-root`
pointing to the existing model/config directory when input data is a backup.
Its output must be a new directory outside the source data. The dense profile's
sole edit and before/after hashes are in `detector-cadence-manifest.json`.
Preserve both run folders; do not reset application sessions to reproduce it.

## Remaining Task 2 requirements

Persistent four-person identity through complete crossings/occlusions is still
unvalidated, and automatic episode stitching is not supplied by this safeguard.
The few AI-labelled samples cannot resolve full-match identity. Independently
reviewed exhaustive physical-contact times, known shot families and hitter
identities on recording-separated evaluation windows are still absent. The
existing Part2 rows label rallies, and this new motion draft is intentionally
partial. Consequently no honest measured per-class shot improvement, full-match
hitter accuracy, or trained temporal/pretrained-model comparison is available.
The new evaluators, source-bound review artifacts and reproducible GPU trial make
those remaining requirements testable without inventing labels or rewriting
historical analytics.
