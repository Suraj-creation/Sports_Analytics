# Future full-upload cache completion guard

The completed Test7-v2 neural worker did not record a perception-cache SHA
catalog at inference completion. Its later 179-file hashes and full semantic
parity remain useful post-hoc evidence, but cannot establish that completion-time
snapshot. That limitation remains unchanged; no old metadata/cache was rewritten,
and no neural inference was repeated for this repair.

`research/production_external_stress.py` now supplies public, self-contained
`perception_catalog`, `write_perception_catalog` and `verify_perception_catalog`
helpers for **future** generic full-upload workers. The worker exclusively
creates `perception_completion_catalog.json` before publishing `inference.json`.
The latter binds its relative path, SHA, version, file/frame counts and snapshot
stage under `perception_cache_catalog`. The parent verifies after the worker
process closes and before its completion receipt; absent/changed cache evidence
produces `failed_cache_catalog_guard`, never a completed receipt.

Schema `production-perception-completion-catalog:v1` binds session ID, original
source SHA, proxy SHA and canonical media dimensions/rate/frame count. Every row
records a relative cache path, bytes, SHA, codec version, header hash and complete
frame extent. Cache header ends are **inclusive zero-origin proxy frame indices**;
benchmark rally interval/export semantics are unchanged. Codec20 itself has no
source-hash field: source/proxy context is bound by the trusted worker receipt,
not inferred from shuttle coordinates. This is file/header/extent provenance,
not physical accuracy, model-origin attestation, confidence calibration or an
original-VFR exposure mapping.

The declared bounds are 10,000 cache files, 2,000,000 canonical source frames,
4,096 frames per cache, 16 MiB per cache, 8 GiB total and 8 MiB per catalog.
MessagePack array/map/string/bin decoding is bounded. Canonical segment names,
all frame IDs, contiguous complete coverage, codec20, image dimensions and FPS
must agree. Empty/missing populations, foreign paths, unexpected files and
symlinked files/directories/catalogs/output roots fail closed. Hash verification
also checks exact population and metadata; a forged replacement catalog digest
cannot turn a foreign path or mismatched context into valid evidence. Existing
output directories and catalog files cannot be silently reused or overwritten.

Focused producer/parent/constructor tests pass **43/43**, with Ruff clean.
Controls include altered/missing/extra/foreign caches, source/session/proxy/media
bindings, catalog tamper, symlink escapes, absent/zero caches, malformed frame
IDs/headers and byte bounds. A simulated worker mutates its cache only after
closing; the actual parent orchestration rejects completion. The existing
constructor-binding smoke now has an explicit synthetic header/frame cache for
its positive path and a no-cache negative path that cannot write a completed
inference receipt. Neither fixture represents neural perception accuracy.

Evidence is `prod_20261105_cache_catalog_guard_v1/`. An initial test-fixture
argument-name collision is retained in its failed log; the production helper was
not the cause. The corrected full focused log, exact source snapshots and narrow
future-executor diff are separate artifacts. The full-upload semantic reader
consumes the same real verifier when the field is present, includes the executor
helper in its source-proof map, and retains explicit legacy absence as unknown.
The root orchestrator owns final coupled research validation and promotion
decisions. No evaluator, production engine, provider, web source, deployed asset,
default profile, historical result or model weight changed in this workstream.
