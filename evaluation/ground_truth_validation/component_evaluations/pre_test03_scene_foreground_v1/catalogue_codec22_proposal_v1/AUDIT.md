# Codec22 completion and diagnostic compatibility audit

This is schema/tool validation, **not physical pipeline validation**. No Test3 data, inference, metric recomputation, matching change, score rule, confidence threshold or original annotation change was performed here.

The initial patch was preserved as an unapplied proposal with original/proposed source hashes. The root agent subsequently approved and applied its exact three-file contents to MAIN and the new scene candidate after the prefix run completed. [applied_receipt.json](applied_receipt.json) records that separate authorization and byte binding; [proposal_source_bindings.json](proposal_source_bindings.json) remains the original proposal-time record. The original c7 checkout and published evaluation outputs remain unchanged.

## Required schema compatibility

1. `production_external_stress.py` previously allowed only codecs20/21. New catalogues can include22, and both21/22 invoke the native production diagnostic decoder for model/profile/source-observation validation. All catalogue size/frame/byte limits and source/header/hash/extent checks remain unchanged.
2. Published catalogues retain their original `[20]` or `[20,21]` accepted-codec metadata only when every actual file fits that historical population. This normalizes one in-memory metadata field; it never rewrites a published catalogue or normalizes other limits. A22 population cannot claim either old policy. Unsupported23 and malformed source observations still fail.
3. Normal timestamp audit previously called a deliberately strict historical `validate_cache21`. One shared private context validator now serves two explicit public wrappers: historical recovery stays21-only; ordinary completed-run validation accepts21/22 and uses the native decoder. No header is rewritten to pass a validator.
4. `normal_timestamp_audit.py` changes only that validator selection. AST controls retain the complete timestamp-audit method after normalizing its renamed validator import/call; `decode_source_pts`, `verify_proxy` and historical recovery catalogue functions remain unchanged.

The three helpers must stay byte-identical between MAIN and the new candidate for the existing orchestration COMMON/admission checks. Their exact root-applied contents are pinned in the application receipt. No additional production or canonical-helper edits were made after the root agent's source freeze.

## Guard results and preserved failures

- The unapplied pure-function proposal tests passed 16 cases against the candidate-native codec22 parser, with bytecode writing disabled. These AST unit wrappers never assign or rebase a module ROOT and are not full-run completion proof. Initial malformed fixture failures are preserved in `initial_fixture_red.log` and `focused_green.log`; the fixture was corrected to use actual loaded model references and an explicit effective weightless stroke implementation, while source validators stayed strict. [focused_green_v2.log](focused_green_v2.log) records the 16 passing controls.
- The portable canonical test is `research/tests/test_catalog_codec22.py`, copied identically to MAIN and the candidate. It uses canonical imports and has no dependency on this proposal directory. Its 15 cases passed.
- The first legacy subset exposed schema-age assertions: the synthetic21 test fixture assumed the latest writer still emitted21, and one recovery test assumed normal catalogue policy excluded22. The actual RED run, old test sources and hashes are retained in [legacy_subset_initial_red.log](legacy_subset_initial_red.log) and `original_test_sources/`.
- With explicit authorization, only synthetic-fixture/current-policy expectations were updated. The historical21 fixture omits codec22 foreground/new witness/new decision fields. It is clearly labelled controlled test data, never a rewritten real run. Historical recovery still rejects22, and normal policy rejects unsupported23. Old provenance, field, time, geometry, hash and population checks remain intact. The combined portable/legacy subset passed 111 tests: [canonical_legacy_subset_green.log](canonical_legacy_subset_green.log), [receipt](canonical_legacy_subset_receipt.json).

## Renderer compatibility

The MAIN-only reusable renderer accepts20/21/22 while keeping complete worker/parent/plan/cache/source/PTS guards. Every codec22 frame requires typed bounded scene-only `fg` data. These regions render blue as **IMAGE CONTEXT ONLY**; they are not athlete admission, physical identities or GT. Raw V3 witness parameters/keys and decision layout indices remain preserved; the renderer does not rerun the scene policy. Legacy20/21 context stays explicitly unknown.

Its 45 synthetic guards pass, including four-player preservation, actual source/proxy PTS, typed foreground on unselected frames, separate context authority, unchanged raw witness/layout payloads, historical20/21 support and artifact preservation. The renderer is absent from the inspected preserved Test1/Test2/c7 worker-plan source maps, so this update does not alter their frozen inputs. Existing renderer v1/v2 executed source snapshots and artifacts remain unchanged. This audit does not claim a completed real codec22 video render or improved scene/contact/tracking accuracy.

Further full-suite, fresh Test1/2 inference and before/after evaluation are the root orchestrator's separate acceptance gates. No candidate is accepted or advanced to Test3 by these schema tests alone.
