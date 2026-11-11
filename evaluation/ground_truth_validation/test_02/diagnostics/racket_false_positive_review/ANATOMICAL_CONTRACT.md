# Diagnosis-local anatomical ambiguity contract

This prototype is separate from production. It establishes a conservative
evidence contract and records its effects on frozen observations. It does not
claim an implemented pipeline fix or a measured physical accuracy gain.

## Proposed rule

Run the existing geometric proposal/ownership selection first. For each selected
racket candidate, check all fresh detector-matched participants with a
same-frame COCO-17 pose. If its fitted ellipse encloses at least three distinct
facial keypoints among nose, eyes and ears with finite confidence0.5–1, the
equipment interpretation is ambiguous with anatomy.

Abstain for that owner on this frame. Preserve the selected candidate, implicated
participant/face landmarks and `racket_anatomical_alias` reason for diagnosis.
**Do not promote a lower-ranked proposal** after the selected candidate becomes
ambiguous. Other owners' unaliased candidates remain unchanged.

The rule makes no fixed body/head/bounding-box exclusion region, uses no player
name or frame-specific coordinates, and does not require a fixed camera or scale.
It is positive ambiguity evidence, not a physical classification that the
ellipse must depict a head. A real racket overlapping the face is also
ambiguous in a single frame and loses this equipment cue. Missing, stale,
collapsed or low-confidence face landmarks do not create an alias.

The diagnosis-local implementation is
[anatomical_abstention_prototype.py](anatomical_abstention_prototype.py).
It explicitly receives the source frame index. Production's current
`RacketPort.detect(image, persons)` does not receive that index, although the
pipeline has it and current pose observations are source-stamped before racket
inference. Any integration must preserve the component boundary and validate
current image/pose provenance rather than silently trusting stale arrays.

## Why whole-owner abstention matters

The selected Test2/300 head has support0.909. Removing only candidates containing
facial landmarks and reranking promotes a lower-ranked torso/jersey contour at
593.03,439.46. This does not repair the equipment interpretation.

| Frozen example | Existing selected owners | Whole-owner abstention | Candidate veto and rerank |
|---|---|---|---|
| Test2/300 | 0 and1 | Owner0 abstains; owner1 unchanged | Owner0 replaced by jersey contour; owner1 unchanged |
| Test2/1594 | 4 and5 | Both unchanged | Both unchanged |
| Test1/243 | None | None | No reranking comparison required |
| Test1/300 | 0 and2 | Owner0 head abstains; owner2 unchanged | Not recomputed for this control |
| Test1/9000 | 0 and1 | Owner0 head abstains; owner1 unchanged | Not recomputed for this control |

See [exact comparison](anatomical_policy_v1/policy_comparison.json).
The surviving banner/letter/torso candidates remain unresolved; this is a narrow
contract proposal, not a complete racket detector.

## RED/GREEN proof

The same diagnosis-local contract tests run in two modes:

- **RED:** baseline passthrough, with no proposed policy: **9 failed,8 passed**.
- **GREEN:** the diagnosis-local wrapper: **17 passed**.

[RED log](anatomical_policy_v1/RED.log),
[GREEN log](anatomical_policy_v1/GREEN.log),
[tests](test_anatomical_abstention_contract.py).

Controls cover selected-head ambiguity with preserved reason/candidate; rigid
rotations and scales; clear overhead rackets near a face without enclosing its
landmarks; true racket/partially occluded-face ambiguity; missing/low-confidence,
stale and collapsed face poses; another person's face in doubles; preservation
of unrelated owners; and prevention of lower-ranked jersey promotion.

Separately,12 image-component probe tests pass. The19 synthetic image controls
study actual geometric acquisition under blur, orientation, scale, partial
occlusion and background-like transverse edges. These controls are not human
physical racket labels and do not define sporting precision/recall.

## Stronger shaft evidence remains a separate investigation

The current sampler accepts unrelated dilated edges with no connected straight
shaft. Directional line evidence is promising on these examples, but fixed pixel
corridors lose scale2 positives; wider body-relative corridors can admit clutter,
and shaft occlusion reduces support. No production line threshold was selected.
Anatomical ambiguity does not imply that every surviving ellipse is equipment.

## Expected tradeoff and required regression

This policy can remove false equipment support while increasing abstention for
true face-overlapping rackets or mistaken poses. It does not improve perception
recall by itself. The preserved existing candidate may still be shown as an
ambiguous geometric proposal, but must not replace wrists or satisfy a specific
equipment-overlap cue as though verified.

Root must authorize any production integration after the fresh Test2 baseline
completes. A production change requires its own regression tests, cache/version
handling, fresh Test2 and Test1 runs, and before/after downstream contact,
classification, rally and identity/outcome coverage comparisons. Reduced racket
counts alone do not establish an accuracy improvement.
