# Full pipeline implementation ledger

- 2026-11-02: Started at `32a8295d9645d81bd1586a777541bb2f72c08bed` on `main`;
  created `full_pipeline` at the same commit. Existing unrelated modifications and
  untracked paths are recorded in `docs/architecture/full-pipeline-architecture.md`.
- The pre-existing external analysis is an untracked user-requested deliverable and
  is preserved. Review evidence in it before adopting external ideas.
- Validation constraint: local-only request plus project server-only test rule means
  tests, inference and media processing cannot be run in this session. Static
  checks do not establish runtime correctness or labelled accuracy.
- Initial architecture and disjoint file ownership published before delegation.
- No trained model, weight, dependency, application secret or dataset changed.
- Audited existing source-bound rally evaluator. Unlike the shot evaluator it
  accepted `status=reviewed` without a human attestation and allowed arbitrary
  statuses when draft mode was enabled. Added a strict reviewed/draft status gate,
  explicit `review.human_verified is True` requirement for reviewed labels, and
  focused regression cases. Existing draft evaluation remains opt-in. These
  changes are source-reviewed but the regression tests have not been executed.
- External comparison and current-model research completed as static source reviews;
  see `docs/research/` for pinned links, rights caveats and proposed experiments.
- Implemented shot/replay-bounded shuttle post-processing and propagated the
  boundary to participant/contact windows. The rally FSM receives unknown speed at
  a cut, and streaming same-player contact suppression resets. An independent review
  identified additional unaddressed context risks below. None of these changes has
  been exercised by tests or real footage in this session.
- Implemented content-aware, atomically published TrackNet ONNX export caching;
  existing legacy exports are ignored, requiring a one-time new export. The exact
  exporter dependencies, remaining TensorRT cache, existing graph integrity and
  registry-verification/reopen trust boundary require separate validation.
- Outstanding: a non-replay shot cut does not clear the rally FSM's stationary
  history or decide whether an open rally persists; reconstructed shuttle points
  still count in its internal visibility. Post-contact shot motion and next-contact
  flight/receiver context can cross a cut. A temporary camera pose/calibration
  loss can mix stabilized and raw coordinates without changing shot/replay IDs.
- No tests, media processing, inference, GPU measurement or held-out evaluation
  performed. No model weights, manifest, dependencies, secret, existing session
  or user data were changed. Static source review and checks cannot substitute for
  the tests or labelled evaluation.
- Independent static reviews identified and prompted guards for cross-shot contact
  context and unexpected ONNX sidecars. Final scoped review found no additional
  actionable issue in those changes, while preserving the unresolved items above.
- ONNX export now requests embedded weights, uses an isolated temporary directory,
  rejects unexpected sidecars and publishes only a nonempty graph. Exporter behavior
  and numeric parity remain untested. Python source parsing, scoped whitespace and
  document/link checks are static checks only; no passing tests are claimed.
