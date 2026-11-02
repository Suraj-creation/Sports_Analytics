# Full pipeline: engineering report

Date: 2 November 2026. Working branch `full_pipeline` begins at
`32a8295d9645d81bd1586a777541bb2f72c08bed`. This is a partial implementation
and static review, not a completed or production-validated full-pipeline upgrade.
The earlier unrelated tracked modifications/deletions and untracked folders were
left in the working tree; no commit, reset, dependency install or deployment was
performed.

## Changes made

1. Extended `AGENTS.md` with architecture and evidence principles, and added
   `CLAUDE.md` / `CODEX.md` pointing to the same project instructions. Added the
   architecture/ownership map and operation notes under `docs/architecture/`.
2. Revisited the pinned external implementations and compared them to this
   checkout in `docs/research/external-repository-analysis.md`. Researched models,
   rights, tensor contracts and evidence gaps in
   `docs/research/model-and-algorithm-evaluation.md`. Corrected the prior report's
   description of D's missing-InpaintNet-checkpoint fallback.
3. `research/evaluate_session.py` now requires an explicit
   `review.human_verified=true` attestation before accepting reviewed rally labels
   and rejects unknown annotation statuses, even in draft mode. Matching still
   requires source binding and exhaustive labels. This is an annotator assertion,
   not proof of review quality or held-out independence. Added regression cases in
   `engine/tests/test_evaluation_manifest.py`.
4. `shuttle_post.process` supports segment boundaries. The match engine supplies
   shot/replay transitions; `WindowObs` carries them into participant/contact
   windows; shuttle and wrist velocity fitting and candidate suppression are scoped
   to a segment. The engine treats speed at a transition as unknown and resets the
   streaming same-player contact suppression. Focused tests cover postprocessing,
   participant propagation, contact context and the camera-jump scenario. These
   are static implementations with unexecuted regression tests.
5. TrackNet ONNX exports now use a cache key derived from checkpoint bytes, source,
   executing exporter/builder code, dimensions, interpreter/PyTorch versions and
   export contract. Atomic publication avoids exposing a partially written graph.
   This intentionally ignores old unkeyed exports and requires an export on first
   use. Focused regression tests are written but unexecuted. See operational notes
   for exporter, cache, supply-chain and TensorRT caveats.

## Evidence and verification status

- **Source and static checks:** the documents use pinned source links and local
  code references. Source parsing, document-link and scoped Git whitespace checks
  are recorded in the handoff. They do not execute the application.
- **Unit, integration, regression:** authored tests have not been run. The user
  requested local work without SSH; the project instructions reserve tests,
  inference and media processing for the remote GPU environment. Both constraints
  prevent executing those checks here.
- **Baseline and accuracy:** no new before/after metrics. No independent, exhaustive
  held-out labels for the target changes were assessed in this session. Existing
  historical reports are context only; geometric exclusion and synthetic tests are
  not shuttle/contact/identity accuracy.
- **Hardware:** local read-only inventory reports Python 3.12.10 and Intel UHD
  Graphics, with no NVIDIA GPU reported by Windows. The remote runtime and current
  GPU resources were not inspected. No model or video was run.
- **Models and rights:** no model choice, manifest, weights or dependencies were
  changed. External code, weights, datasets and videos have independent terms;
  J's MIT source does not grant blanket rights to all its dependencies, D had no
  license file in the inspected snapshot, and V restricts redistribution and
  commercial use. Candidate checkpoint trust must be verified independently.

## Remaining work before integration or deployment

- Run the targeted tests listed in `full-pipeline-operations.md` on the permitted
  environment, then the related badminton, engine, API and evaluation suites.
  Verify real ONNX export and inference with the existing server environment,
  checkpoint, providers and representative input; check first-export dependencies,
  disk usage, numerical parity, concurrency and failure behavior.
- The rally FSM retains stationary history across a non-replay cut and consumes
  interpolated positions as internally visible. Open-rally behavior at a cut is
  unresolved. Post-contact flight/receiver context can cross cuts, and camera
  stabilization loss can mix coordinate frames without a shot change.
- Existing keyed ONNX files are not independently authenticated; registry checking
  and later checkpoint reopening are separate operations. TensorRT engine cache
  invalidation across weights, versions and hardware is not yet established.
- Create reviewed, exhaustive, source-bound and match-disjoint singles/doubles
  labels for detection, identities, shuttle, contacts, rallies and scores. Freeze
  baseline settings; evaluate the unchanged and candidate implementations on the
  same footage, including false positives, misses, timing, abstention and resource
  use. Do not infer improvement from these code changes alone.
- Additional interface, scoring, reporting, device and full-video requirements in
  the supplied brief remain partial or unverified. The architecture document maps
  existing interfaces and is not a claim that every proposed component is independently
  replaceable. No end-to-end or production-readiness claim is warranted.
