# Codebase cleanup review — Video2 scope

No files were deleted. This is a read-only inventory, not an authorization to purge datasets or evidence. Sizes are allocated disk bytes, shown in decimal MB/GB. The checkout occupies38.79GB; the current task's separate experiment directory occupies12.69GB outside the checkout.

The active application starts through `start-app.sh` → `.venv/bin/bai serve`, with `engine/`, `sports/badminton/`, `agents/`, `apps/api/` and built `apps/web/dist/`. Workspace packages are declared in `pyproject.toml`. The separate client website is deliberately retained in the existing workspace-consolidation notes.

| Candidate | Measured size | Disposition | Consequence |
|---|---:|---|---|
| `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, source `__pycache__/`, `apps/web/test-results/` |27.5MB total|Regenerable caches/results after processes stop|First checks/imports recreate caches; retain any test failure evidence needed elsewhere|
| `.hypothesis/` |1.02MB|Optional test cache; preserve useful failure examples first|Previously cached examples are lost; source regression fixtures remain|
| `models/cache/.hf/` |602.6MB|Duplicate downloader cache candidate|All6large blobs (602.44MB) have verified independent canonical copies; no canonical symlinks point into`.hf`. Keep every canonical model, manifest and lock. Future downloads may use the network|
| `apps/web/node_modules/` |331.6MB|Reinstallable dependency tree, not dead code|Development, builds and web tests need reinstalling from the lockfile; keep current built`apps/web/dist/` for startup|
| `data/recovery/` |4.15GB|Archive/review old recovery snapshots|Not the default active data directory; recovery/session history must be backed up and references reviewed before removal|
| `artifacts/benchmarking/` |6.48GB|Archive older generated evidence, not blanket deletion|Contains frozen Test1/Test2 benchmarks, hashes, replays and release evidence required for comparisons|
| `../pipeline-repair-runs-20261105/` |12.69GB|Archive selected generated runs/probes after evidence retention|The inventory identifies5.17GB of optional additional-run/reference/source-clone candidates. Some are linked by reports; preserve a verified archive and update links before deleting originals|
| `legacy/` |175.3MB|Inactive-runtime archive candidate|Project lint explicitly bans imports from`legacy`; it includes163.35MB of court data, so preserve that dataset independently before retiring it|
| `client-website/` |1.34MB|Separate deliverable, owner decision|Not the active analytics app; existing project notes explicitly retain it. Removing it retires that website source|

Keep `.venv/` (10.99GB: the working Pascal-compatible GPU environment), canonical `models/cache/` weights and pins, `.git/`, `.env`, active configuration, core application source, tests, original videos and annotation CSVs. `Part2/` is mostly the original Video2 and must not be treated as disposable legacy code. `data/media/` (4.72GB) mixes source video and generated playback assets; use a session-aware retention review rather than deleting the directory. `outputs/benchmarking/test1/` remains a frozen baseline.

No production module is certified dead merely because a text search finds no direct import: this application uses dynamic component registries, plugins and CLI entry points. Research/prototype code is mostly small; removing it saves little compared with generated media and dependency caches. Consolidation should preserve tested runner/evaluator contracts and exact benchmark provenance.

The extra amateur run was interrupted after the user clarified Video2-only scope. Its partial output is retained and is not a completed benchmark. The attempted additional Video2 repetition did not launch neural inference: its frame-count preparation timed out at300seconds. Existing Video2 evaluation remains complete. No testing of every Google Drive video was performed.

Evidence: [disk inventory](../../pipeline-repair-runs-20261105/cleanup_inventory_v1.json), [duplicate model-download audit](../../pipeline-repair-runs-20261105/hf_duplicate_cache_audit_v1.json), [runtime entry](../start-app.sh), [workspace configuration](../pyproject.toml), [prior preservation policy](../docs/workspace-consolidation-20261104.md).
