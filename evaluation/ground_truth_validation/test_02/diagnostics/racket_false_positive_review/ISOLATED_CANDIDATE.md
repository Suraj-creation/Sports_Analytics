# Isolated semantic admission candidate — not integrated

The candidate exists only under `candidate_source/bai_badminton/` and imports via
an explicit `PYTHONPATH` ahead of the unchanged main package. It copies66 Python
source files; only `engine.py` differs and `racket_admission.py` is added.
No models, videos, datasets or original run directories were copied or changed.

The main production package still matches every original source hash captured
before the candidate. See
[validation receipt](candidate_validation_receipt.json),
[original hashes](candidate_source_original_hashes.json), and
[reviewable patch](candidate.patch). **Do not apply the patch before root's
baseline/evidence gate and regression review.**

## Behavior

At engine ingress, a new semantic copy of every `PersonObs` is created in the raw
analysis-image basis before camera stabilization. A selected current geometric
racket enclosing three distinct confident, source-current facial landmarks is
ambiguous. Its semantic copy receives `racket=None` and
`racket_frame_idx=None`; lower-ranked contours are never promoted.

Only current, unique-track, detector-matched finite people with confidence≥0.5
can witness an alias. Face joint confidence must be finite and0.5–1; COCO nose,
eyes and ears are tested against the fitted ellipse rather than a fixed body or
head region. Missing, stale, low-confidence or collapsed facial evidence does
not invent an alias. Other participants' faces count, including doubles.

The engine appends a provisional `racket_observation_ambiguity` event containing
policy/version, raw candidate geometry/support, source frame, owner track,
source stamps, face-track/joint references, `semantic_admitted=false`, and the
no-reranking policy. `Event.type` accepts this string. No named actor, contact,
winner or point is invented.

Original `FramePerception`, persons, source stamps, pose arrays, candidate
objects and encoded cache bytes remain unchanged. Existing raw racket track
exports also remain unchanged as raw geometric observations. Both named player
buffers and anonymous participant snapshots receive the gated semantic copy,
so contact proximity, overlap and fresh equipment evidence cannot consume the
ambiguous head ellipse as equipment.

## RED/GREEN and regression evidence

The initial untouched source copy produced10 failures and14 passes on24 real
engine cases. Its candidate GREEN run passed24 cases. Tests were then expanded
with direct physical-evidence assertions, four-player doubles and retained raw
Test2 observations.

Final identical test file:

- **Untouched isolated baseline:**11 failed,14 passed,2 skipped. The optional new
  helper fixture checks skip because that helper does not exist before the fix;
  the real-engine contract failures independently establish RED.
- **Isolated candidate:**27 contract tests passed.
- **Candidate plus existing racket/contact/participant/provenance/geometry
  families:**199 passed.
- Lint passed for both candidate source files and the new contract tests.

[Final RED](candidate_RED_final.log),
[combined final GREEN/regressions](candidate_regressions_final.log),
[real engine tests](candidate_tests/test_engine_racket_admission.py).

Cases cover named singles and anonymous singles/doubles; four participants;
raw cache/input immutability; raw track preservation; provisional event/source
payloads; stale/missing/low-confidence/collapsed/duplicate face evidence; ordinary
overhead rackets; other-person head aliases; actual face-overlap ambiguity;
camera rotation and projective registration; and chunk partition invariance.
Retained Test2/300 removes only the near head from semantic admission;
Test2/1594 remains unchanged. These are contract predicates on frozen estimates,
not physical detection precision/recall or a full video rerun.

The first broader-suite command used two nonexistent test filenames and ran no
tests; its failure log remains preserved. The corrected explicit suite then
passed196 cases, and the expanded final suite passed199. No expectation was
weakened to resolve that command-selection error.

## Remaining scope and risks

This is an evidence-driven mitigation of one recurring anatomical alias class.
Far advertising/lettering and some torso candidates remain unresolved. A true
racket overlapping a confidently posed face is intentionally ambiguous and may
lose an impact cue. Erroneous poses can increase abstention. Missing anatomy
does not certify surviving equipment. Removed counts are not an accuracy gain.

Root must first preserve the full fresh Test2 baseline, then decide whether to
integrate. Exact own-cache baseline parity and a declared semantic source
intervention can isolate the candidate's downstream effect using unchanged
perception. Use the existing guarded replay mechanism; do not rewrite original
inference receipts or call the replay fresh neural inference. Test1 requires
the same before/after semantic regression.

The policy version is explicit in ambiguity events. Existing accepted analyses
are historical results: they must not silently be presented as using this policy
without recomputation. No raw cache codec change is required because perception
is unchanged. Reanalysis/version metadata and a fresh integration run remain
the orchestrator's responsibility.
