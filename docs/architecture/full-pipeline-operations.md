# Pipeline operation and evaluation notes

The active project is a modular engine plus a badminton plugin; see
[full-pipeline-architecture.md](full-pipeline-architecture.md). Select model
identifiers and device/backends through the YAML files under `config/profiles/`;
`models/manifest.yaml` describes artifacts and candidates. A configured model or
manifest entry is not proof that its adapter is active or the weights exist.
Check `BadmintonPerception` loaders and `BadmintonSession.degraded()` for actual
runtime support. Do not download or switch a model solely because it is newer.

For the configured GPU runtime, use the existing environment and `../gpu-env.sh` as
specified by the root `AGENTS.md`. Preserve existing sessions before reanalysis and
keep Cloudflare disabled. For the scoped evaluation-integrity regression when a
permitted test runtime is available:

```bash
source ../gpu-env.sh
.venv/bin/python -m pytest engine/tests/test_evaluation_manifest.py -q
.venv/bin/python -m pytest sports/badminton/tests/test_shuttle_post_segmentation.py \
  sports/badminton/tests/test_shuttle_scene_boundaries.py \
  sports/badminton/tests/test_contact_scene_boundaries.py -q
.venv/bin/python -m pytest sports/badminton/tests/test_tracknet_onnx_cache_integrity.py -q
```

This command has not been run as part of the local-only session. A synthetic or
mocked pass would verify logic only, not model, GPU, real-video or accuracy claims.

## Rally evaluation manifest

`research/evaluate_session.py` consumes a source-bound, exhaustive rally manifest
whose `media_sha256` matches the session. The `window_s` and all rally boundaries
use canonical analysis-proxy seconds; the window is half-open. Choose the event
population and split explicitly. A `draft` requires `--allow-draft` and is never
accuracy-claim eligible. A `reviewed` manifest must contain
`"review": {"human_verified": true}` as an explicit human-review attestation;
a mere `status` string is insufficient. `held_out` is a declaration of the split,
not proof that the recording was isolated from tuning. Neither attestation proves
annotation correctness, exhaustive review, or independence: record the reviewer,
method, uncertainty and provenance outside the tool as appropriate.

The evaluator matches rallies one-to-one, reports unmatched truth and predictions,
separates unresolved winners, and records media/annotation/event-log hashes. A
labelled rally evaluator does not validate contact events, shot classification,
player identity, shuttle accuracy or line calls. See
`research/shot-annotation-protocol.md` and
`research/tracking-annotation-protocol.md` for separately scoped evaluation.

## Known limitations

The current canonical frame index and derived presentation time are based on the
CFR analysis proxy. Source-level variable frame timestamps and duplicates are not
fully represented per frame. Court homography maps floor-plane points; it cannot
measure airborne shuttle coordinates in three dimensions. The external repository
report identifies transferable ideas and their limits, not proven performance on
this project's footage. Do not replace models or change cache versions without a
separate compatibility and baseline assessment.

Shuttle post-processing is segmented at changes of shot ID and replay state, so
its spike and gap-fill windows should not cross those boundaries. This change is
untested until the commands above run. The same boundaries are passed to contact
velocity and wrist windows, and the rally FSM is given unknown speed at a boundary;
these changes also need runtime validation. The rally FSM still uses the internal
`vis` mask, which includes reconstructed positions. Temporarily unusable camera
geometry may mix stabilized and raw image coordinates without a shot/replay change;
that case is not covered by these boundaries. Post-contact shot kinematics and a
next-contact flight duration may also use evidence across a cut; those consumers
have not yet been isolated. The rally FSM also retains stationary-history samples
across a non-replay shot cut; a cut may combine different scenes' evidence. Whether
an open rally should close or remain uncertain on such a cut needs separate design
and validation. Real-video and labelled before/after analysis is needed before
asserting improved rally, contact or classification accuracy.

TrackNet's newly keyed ONNX export does not solve every cache issue. It does not
independently verify an existing derived ONNX file's contents, fingerprint every
exporter dependency, or validate TensorRT engine caches against all model, driver,
runtime and hardware changes. The PyTorch checkpoint loader still requires a
trusted artifact. A missing or stale cache must not be treated as a model-quality
finding, and the new path has not been exercised with real checkpoints.

## ONNX cache deployment caveats

The candidate TrackNet change deliberately stops reusing legacy unkeyed ONNX files.
The first ONNX/TensorRT run for each new key therefore needs enough space for a
fresh export and a working PyTorch ONNX exporter, including the dependencies
appropriate to the installed PyTorch version. The configured server has not been
inspected in this local-only session. A missing export dependency or read-only
cache may degrade the shuttle stage at startup; verify it before deployment and
keep the existing environment and unrelated jobs intact. Do not delete legacy
files or historical session artifacts as part of this change.

The candidate exporter requests embedded ONNX weights and refuses unexpected
sidecar files before publishing. PyTorch's default exporter varies by version;
actual export success, graph semantics and numeric parity remain unverified on
the configured runtime. Exporter failures must remain visible as degradation.

The content digest records the checkpoint bytes used in naming the export; it is
not a signature, does not prove that a cached ONNX graph matches those weights, and
does not close the gap between registry verification of a path and reopening it.
Pinning a first fetch is not authentication. Provider-specific TensorRT caches and
hardware/runtime changes need their own tested invalidation policy.
