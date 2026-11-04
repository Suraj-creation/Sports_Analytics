# Required reading and platform contract

Before every task, implementation, debugging session, review or handoff, read
`AGENTS.md`, `CODEX.md` and `CLAUDE.md`. Treat the architecture and evidence rules
below as requirements for all code, tests, configuration and product behavior.
Keep the three instruction files consistent when these requirements change.

We are building a reusable analytics platform. Badminton is the current domain,
not the platform's architectural limit. Whole analysis pipelines and their
individual components must be replaceable through explicit plugin contracts.
Support future sports and other analytics without putting domain assumptions
into the generic host or creating a parallel engine for each use case.

## Pluggable pipelines and components

- Extend the existing engine/sport-plugin interfaces as the entry point. A
  pipeline plugin declares the stages it composes, their order/dependencies,
  configuration, capabilities and lifecycle. The host selects a pipeline by
  configuration/registration, not by hard-coded badminton imports or UI branches.
- Keep acquisition, media/timebases, scheduling, generic model execution,
  persistence, transport, generic evidence and observability in `engine/`.
  Domain plugins own court/field geometry, format-specific interpretation,
  contacts, action/shot semantics, rules, scoring and domain analytics.
- Detection, perception, tracking/identity, contact inference, classification,
  activity/rally segmentation, outcome/scoring and analytics must have explicit
  replaceable component boundaries. A domain may compose, omit or replace stages;
  do not assume every future pipeline has badminton's stages or event taxonomy.
- Each component declares typed inputs/outputs, timeline/coordinate conventions,
  configuration and artifact versions, supported formats/devices, required and
  optional evidence, provenance, failure/unknown behavior and state reset/restore.
  Resolve implementations through registries/factories and dependency injection.
  Avoid global singletons, hidden model selection and speculative abstractions.
- Cache identity includes relevant input/media, model, stage/pipeline version,
  configuration, calibration and format decisions. Invalidate dependent results
  when these change; preserve/back up accepted evidence and existing baselines.
- Test the host boundary with an independent non-badminton test plugin and test
  component replacement. A registry entry alone is not proof of pluggability.

## Singles, doubles and format adaptation

- Singles and four-player doubles are first-class requirements throughout the
  pipeline, storage, evaluation and UI. Design every change against both. A
  singles-only research component must declare that limitation and remain behind
  an explicit capability gate; do not present its fallback as doubles support.
- When format is unspecified, a replaceable format-understanding layer should
  infer singles/doubles from sustained target-court observations and expose its
  evidence and uncertainty. Respect explicit user format/roster configuration.
  Occlusion, spectators, adjacent courts or two currently visible players must
  not silently force singles or overwrite a confirmed doubles roster.
- Propagate confirmed or uncertain format through stage configuration. Keep
  physical participants, track episodes, team membership and the two scoring
  slots distinct. Doubles contact attribution considers all four participants;
  team scoring must not pretend a near/far track is a permanent named player.
- If additional calibration, roster binding or service configuration is needed,
  expose the missing requirement or a review action. Preserve unknown identity,
  format, contact, shot and winner rather than inventing a result.
- Format changes must reset incompatible temporal state and invalidate dependent
  caches explicitly, with reproducibility metadata and compatible schema handling.

## Accuracy, scoring and reviewable evidence

- Useful end-to-end behavior is required; passing unit/runtime checks does not
  establish contact, classification or scoring quality. Trace empty or poor
  output through the actual perception-to-decision gates on real footage.
- Distinguish observed scoreboard values, identity/row hypotheses, reconstructed
  score transitions and accepted point decisions. Reconcile evidence with legal
  rules, but never invent rally winners or pad a match to a plausible final score.
  Do not present an unknown score as a verified 0–0 match score.
- Make contact candidates, racket/shuttle observations, shot labels, rally
  boundaries and point decisions visually reviewable with canonical-frame
  evidence, provenance, uncertainty and rejection/abstention reasons. A visible
  point/score update must identify its player/team and supporting evidence.
- Maintain an evaluation matrix for shuttle visibility/location, contact timing,
  hitter/team attribution, shot classes, rally boundaries, point decisions and
  score sequences, plus latency/resources. Include singles, doubles, identity
  uncertainty, cuts/replays, occlusion and multi-court scenes.
- Report stage-conditional and end-to-end metrics, coverage/abstention, matching
  tolerances, per-class confusion and errors. Use source-bound reviewed labels
  and match-disjoint tuning/evaluation; preserve a comparable baseline. Agent
  visual checks and model-generated outputs remain diagnostic/draft evidence.
- Study external implementations outside this repository. Verify code, model,
  dataset and dependency licenses separately, including noncommercial use;
  preserve required notices and record pinned sources/artifact hashes. Adopt a
  model or method only on comparable evidence, not README scores or novelty.

# Project workspace

The workspace was consolidated on 2026-11-04. Author code and run validation in
`/home/administrator/Desktop/sport-analytics/Sports_Analytics` on `main`.
The user authorized consolidation and publication of useful recent improvements,
removal of obsolete worktrees and cleanup of Cloudflare and temporary artifacts.
Preserve original application sessions, model assets, accepted evidence and
unrelated server jobs. Recovery snapshots are recorded in the cleanup report.
Never store SSH passwords or application secrets in this repository.

## Runtime

On the GPU server, source `../gpu-env.sh` before inference, media processing or
tests and use the existing `.venv`. Run all tests, model inference and media
processing on the GPU server; the space-constrained Windows device is for
editing, Git and browser access only. The server's Pascal GPUs require its configured
CUDA/FFmpeg environment; do not replace that environment during routine work.
Do not stop unrelated GPU training jobs. Keep Cloudflare disabled during testing;
use localhost or an SSH local port forward for browser access.
Keep generated builds, caches and local secrets out of Git.

## Validation

The application is started with `../start-server.sh` on port 8010.
Court-isolation design and evaluation instructions are in
`docs/multi-court-isolation.md`. Back up session results before reanalysis.
Geometric exclusion metrics are not labelled shuttle/event accuracy.

## Engineering principles

- Extend the existing engine and sport plugin boundaries. Keep video, scheduling,
  storage, generic evidence and model execution in `engine/`; keep badminton
  geometry, perception, rules, contacts and analytics in `sports/badminton/`.
- Give replaceable components explicit configuration, input/output contracts,
  version and failure behavior. Prefer existing interfaces to speculative abstractions.
- Preserve evidence provenance: distinguish model observations, tracker estimates,
  reconstructed points, derived events, identity hypotheses, review and unknowns.
  Do not describe heuristic scores as calibrated probabilities or ground truth.
- Use the canonical CFR proxy timeline for analysis while distinguishing it from
  source timestamps and duplicated observations. A floor homography is not a 3D
  measurement of airborne shuttle position, speed, contact or landing.
- Invalidate dependent caches for changed inputs, models, configuration and
  calibration; maintain schema compatibility and record reproducibility metadata.
- Preserve existing baselines and model artifacts. Adopt alternatives only on
  comparable evidence; document missing labels, unavailable models and failures.
- Keep singles, four-player doubles, uncertain identity and multi-court scenes in
  scope. Do not force an identity, shot class, point or line call without evidence.
- Add focused regression coverage for behavior changes. Validate in the runtime
  specified above; report any tests or real-video checks that could not be run.
- External source, datasets, model weights and dependencies have separate licenses;
  verify each before reuse. Never commit credentials, large weights or generated data.
- During parallel work, assign exclusive production-file ownership and coordinate
  shared schemas, registries and configuration with the integration owner.
