# Project workspace

Author code in the current local Windows checkout/worktree, following the user's
request to keep editing fast. Preserve unrelated local changes and untracked
folders, including `Part2/` and `SportsVideoAnalysis/`. Use Git to transfer tested
changes to an isolated checkout on the Remote GPU Server for inference and
end-to-end application testing. The server runtime and existing environment are
under `/home/administrator/Desktop/sport-analytics/Sports_Analytics`.
Do not store SSH passwords or application secrets in this repository.

## Runtime

On the GPU server, source `../gpu-env.sh` before inference, media processing or
tests and use the existing `.venv`. Run all tests, model inference and media
processing on the GPU server; the space-constrained Windows device is for
editing, Git and browser access only. The server's Pascal GPUs require its configured
CUDA/FFmpeg environment; do not replace that environment during routine work.
Do not stop unrelated GPU training jobs. Keep Cloudflare disabled during testing;
use localhost or an SSH local port forward for browser access.
Preserve existing untracked user files, including `apps/web/dist.old/`.

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
