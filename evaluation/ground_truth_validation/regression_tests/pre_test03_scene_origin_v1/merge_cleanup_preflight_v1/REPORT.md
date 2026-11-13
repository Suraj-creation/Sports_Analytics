# Merge and auxiliary-worktree cleanup preflight

All five auxiliary worktrees are clean for tracked changes and nonignored untracked files. Every head, including all four earlier candidates, is an ancestor of `5ae614826e6f909defb02445386962ac13b4641a`. Main remains at `dacc05e9421db7a27782c524d4efffddf015e20a`, which is also an ancestor; a fast-forward history integration is possible after local path collisions are preserved and resolved. Cached `origin/main` is dacc05e and is ten commits behind5ae. This is a local tracking-ref observation, not a fresh remote check or proof that changes were pushed.

**This report authorizes no early cleanup.** The user's existing authorization covers merge, push and removal after Test1 and Test2 are accepted. At this preflight, broader numerical acceptance is still being finalized and the next Test2 validation gate remains separate. No Git mutation, source change, archive change, move or deletion was performed here.

| Auxiliary worktree | Head | Tracked/nonignored status | Ignored paths |
|---|---|---|---:|
| test03-pipeline-improvements-20261111 | `c7cf871c81cc` | Clean | 529 |
| test03-scene-acquisition-20261112 | `a14695372f0d` | Clean | 530 |
| test03-scene-continuity-20261112 | `c585e3507a2f` | Clean | 531 |
| test03-scene-evidence-contract-20261112 | `2418ab8cbe4c` | Clean | 536 |
| test03-scene-overlap-20261112 | `5ae614826e6f` | Clean | 259 |

The five directories occupy about1.12GiB combined using `du` without following symlinks. Most bytes are tracked repository copies (including legacy material and Part2 annotation copies). This size excludes the shared symlink targets and must not be represented as permission to delete main's data or legacy assets.

## What would be removed, and what must remain

Each worktree contains five protected shared links, for25links total: `.venv`, `apps/web/dist`, `artifacts`, `data/research/pluggable-pipeline-20261103`, and `models/cache`. Their resolved targets are inside the retained main checkout. The full mapping is in [worktree inventory](worktree_inventory.json). Remove only worktree entries/directories through Git's worktree mechanism; never recurse through resolved symlink targets. Keep main's environment, builds, artifacts, data, all original annotations and model caches intact. The shared Git object database also stays intact.

Every ignored nonsymlink item is Python bytecode or pytest/Hypothesis/Ruff cache state. No ignored executable source, report, annotation or independently modified model was found in any auxiliary tree. The Hypothesis material is constants/cache state, not a newly authored source implementation. Nothing from these ignored caches is needed to retain the committed engineering fixes; the retained validation logs and regression source remain separate evidence. Nonignored auxiliary status is empty, so there is currently no unique dirty/untracked source inside these five directories requiring rescue. Recheck immediately before removal because this is a point-in-time inventory.

## Archive completeness and historical reconstruction

Five representative actual fresh-run plans were checked: c7Test1, c585Test1,2418Test1,2418Test2 and5aeTest1. Their permanent `executed_source` trees contain every archived file with the correct recorded SHA256:128/288plan entries for the first run,129/289for each newer run. Each has160missing standalone archive entries, specifically100`.tsx` and60`.ts` frontend files. This is an archive-scope omission, not lost or dirty backend code. Every one of those160files matches its actual producer-head Git blob exactly. [Archive verification](executed_archive_verification.json) preserves the literal missing-file findings; [committed recovery verification](committed_archive_gap_resolution.json) resolves all of them against committed bytes without changing an original archive.

After a real merge and successful push, those historical commits and their full trees remain reachable from main, so no large recovery bundle is needed solely for already committed ancestors. For convenient self-contained recovery, a **new** supplementary archive of these160files plus source-path/commit/hash mapping can be created outside the disposable worktrees; do not add files to already sealed run archives. Existing external run directories, reports, predictions, logs, receipts, source copies and dirty patches must remain untouched. This audit checked the named five full-run source plans; it does not claim every historical experimental run has a standalone complete source tree.

Recorded absolute producer paths will stop existing after worktree removal. That does not invalidate preserved hashes, but source links/native tools that require those exact paths will need reconstruction. Preserve a navigation index mapping each old ROOT and commit to permanent archive paths and the retained Git tree. Future strict replay should restore the recorded checkout/byte snapshot when needed; do not rebase ROOT, rewrite old receipts or claim a relocated copy passed a guard requiring a different physical root. Newer native postprocessing additionally archives executable dependency sources, which helps preserve the actual auditor/adapter implementation.

## Main merge collisions and exact resolution plan

Main has six modified tracked files plus552nonignored untracked paths at inventory time (excluding this new preflight directory). This count covers reviewable source/reports; it excludes ignored generated evidence, which must also stay in place. The incoming48tracked-path delta overlaps15local paths. Four are byte-identical: `normal_timestamp_audit.py`, `evaluate_manifest_components.py`, its usage Markdown, and `test_render_validation_evidence_guards.py`. Eleven differ; exact old/current/incoming SHA256s and complete diffs are preserved in [merge overlap manifest](main_merge_overlap.json). The differences are:

- The native adapter adds executable dependency archiving and updates structural provenance.
- The renderer, normal completed-cache validator and producer catalogue extend normal codec support to24; historical strict21recovery is retained.
- The scene auditor advances fromV3 toV4 with actual prior-foreground/camera/format proof and explicit overlap-dependent abstention.
- The regression runner adds native codec24 dispatch and source archival/provenance; its incoming usage document is shorter than main's149-line version.
- Four research fixtures/tests add the reviewed24metadata/structural expectations and negative guards.

No new main-only runtime fix was identified in these overlapping diffs that should replace the tested incoming implementation. Preserve all current versions first, then adopt the accepted5aeversions for these15paths together, since selectively retaining old helpers would omit codec24/native-proof support. In particular, preserve the longer current regression usage document as historical documentation rather than silently losing it; migrate still-applicable explanatory material later without reviving stale runtime claims.

Main's modified `evaluation/ground_truth_validation/.gitignore` is the sole modified path outside the incoming delta. Keep it: it excludes generated CSV/snapshots from publication, without deleting their actual local files. Main-only continuation/download/export helpers, reports, failure cases and diagnostic packages are also outside the incoming delta and must stay.

Concrete integration sequence, to be executed by the orchestrator **only after both acceptance gates**:

1. Stop edits to the affected source paths, refresh this inventory, and preserve main's actual working diff plus exact bytes of all15overlap paths in a NEW permanent pre-merge source snapshot. Hash-check that copy. Preserve the other main-only source/reports and ignored evidence in place; do not use blanket `clean`, ignored-file stashing or reset commands.
2. Resolve only the listed incoming collisions after snapshot verification. Restore only the five overlapping modified tracked paths to their base and move only the nine untracked incoming-addition paths into the verified snapshot as needed. The independent `.gitignore` change and every unrelated main-only path remain. Counts describe this manifest; re-evaluate any newly changed path first.
3. Fast-forward main to5ae, verify the expected48-path delta and previously accepted source hashes, then commit any separately reviewed main-only canonical tools/reports/docs. Verify the retained source/config/model/annotation identities and run appropriate post-integration checks.
4. Push main and verify the published commit/history contains all five auxiliary heads. Local cached `origin/main` alone is insufficient proof. Preserve historical standalone source gaps via Git history and optionally the new supplement described above.
5. Recheck all five worktrees remain clean and all active runs are finished. Remove the five worktrees by their exact recorded names through Git worktree removal, then delete only their now-merged temporary branches. If a removal refuses, inspect its reason; do not use force until any newly reported content is inventoried and retained. Never delete the main repo, shared links' targets, external benchmark directories or original datasets.

This is a preservation/resolution plan; none of these integration steps was executed by this preflight. The point-in-time [inventory script](inventory_preflight.py), complete ignored/source/symlink lists and exact per-file diffs make the proposed actions reviewable.
