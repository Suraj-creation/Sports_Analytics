# Project instructions for Claude

Before every task, coding change, investigation, review or handoff, read
`AGENTS.md`, `CODEX.md` and `CLAUDE.md`. Follow the complete platform contract in
`AGENTS.md`; keep all three instruction files consistent.

- Build a reusable analytics platform: the whole pipeline is a configurable
  plugin, and detection, perception, tracking/identity, contacts, classification,
  segmentation, scoring and analytics have replaceable component contracts.
  Extend existing interfaces instead of creating a second monolithic engine.
- Keep the host in `engine/` domain-neutral. Badminton geometry, interpretation,
  rules and analytics belong in its sport plugin. Other sports or analytics
  pipelines must be incorporable without embedding badminton assumptions in the host.
- Declare typed stage inputs/outputs, configuration/version, capabilities,
  provenance, timeline/coordinates, state lifecycle, cache invalidation and
  failure/unknown behavior. Verify actual component and pipeline replacement.
- Design and evaluate every change for singles and four-player doubles. Infer
  unspecified format through evidence with an explicit uncertain state; respect
  user overrides. Do not silently truncate four people to two or equate a track,
  a person, a team and a scoring slot. Expose extra configuration when required.
- Diagnose real missing contacts, poor shot classes and absent point updates.
  Preserve unknowns, while providing reviewable visual evidence and truthful
  observed-versus-accepted scores. Never invent points to force a final score.
- Compare stage and end-to-end accuracy, coverage, confusion, timing and resources
  against source-bound reviewed labels and a preserved baseline. Runtime passes
  are not labelled accuracy; agent/model-produced labels remain diagnostic.
- Study external repositories outside this codebase and verify each code/model/
  data license before reuse, even for noncommercial work. Keep weights, generated
  data and credentials out of Git and retain required attribution.

The workspace was consolidated on 2026-11-04. Author and validate in the primary
`Sports_Analytics` checkout on `main`; obsolete task worktrees have been retired.
The user authorized consolidation and publication of useful recent improvements
and removal of obsolete worktrees and Cloudflare artifacts. Source ../gpu-env.sh
and use the existing .venv. Preserve application sessions, model assets, accepted
evidence and unrelated server jobs. Never commit credentials or generated data.
