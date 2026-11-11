# Test1 scoring and identity diagnosis, plus a separately reproduced safety defect

## Source observations: a disagreement is not automatically a pipeline defect

The fresh baseline's actual source frame8634 (287.8s) visibly shows **AN S.Y.20 / INTANON20**. The associated agent source-panel inspection is diagnostic evidence; it is not a newly independently reviewed sporting label. The cached OCR readings at8522,8552,8582,8612,8642,8672 all report exactly those names and20:20 with confidences approximately0.967–0.972. Corroborated `broadcast_score` events preserve the same observation.

The supplied `Test1_Full.csv` CSV line20 covers4:30–4:48 and lists PlayerA winning, score10:9, HookShot/net outcome. Therefore that CSV's score is not established as the source image's absolute scoreboard. Changing OCR20:20 to match10:9 would corrupt source evidence. Raw supplied tables and current observations must remain separate.

Frame panel: `../annotation_visual_review/frame_08634_source_resized.png`. Exact image hash, cached readouts, original score-event payloads and the unchanged supplied row are recorded in `scoring_identity_evidence.json`.

The actual live36 rally results have **36 unknown winners**: winner-source categories27geometry,3ocr_ambiguous,6ocr_unmapped; source transition statuses30unavailable/6candidate. Empty configured player names and no independently established PlayerA/B→named-athlete/score-row mapping mean source score changes cannot safely become named official winners. The baseline's unavailable OSNet identity and ReID remain explicit degradation.

`BadmintonMatchEngine._multi_person_identity_ambiguous` starts true and all later assignments in current source also set it true (engine.py around341,542,1025,1184,3139). Consequently legacy near/far→P1/P2 assignment and geometric winner inference are gated off. This is a conservative identity contract, not proof that an individual is absent. Simply forcing it false would revive unverified side-as-identity assumptions and is not a supported fix. Accurate OCR acquisition does not by itself solve athlete/track/row identity or official point acceptance.

## Confirmed current code defect: repeated queries manufacture independent mapping votes

`score_ocr.py::ScoreReconciler.winner_from_ocr` previously incremented `_votes[(winning_row, geometry_winner)]` on every call. `_maybe_fix_map` accepted a dominant hypothesis at3votes. Reconciliation and refolding query existing source transitions repeatedly, so three requests about **one** corroborated source increment could establish a row mapping as though three independent points had agreed.

The original-source failing regression `test_repeated_score_transition_votes.py` constructs one generic10:10→11:10 change, observed twice before and twice after a rally. All three calls resolve the identical canonical `ScoreTransitionRef` ID `11246892473b6ff50b94ba3a90a889ccaaeebfda8d8f6d854d254bf6822508f0`. Actual before-fix results:

- Votes become `{(0,'P1'):3}`.
- `row_map` becomes `{0:'P1',1:'P2'}` despite only one source point.
- Returned provenance changes from `ocr_unmapped` to `ocr` on the third query.

`repeated_vote_red.log` preserves this failure on untouched primary source. This is a real provenance/retry-safety defect in current code, **not the demonstrated cause of Test1's unknown winners**: Test1 currently supplies no geometric winner to this voting path, and has no configured names. It must not be presented as a measured baseline accuracy improvement.

## Focused isolated correction

After root authorization, the only production module edited for this task is:

`/home/administrator/Desktop/sport-analytics/test01-pipeline-fixes-20261110/sports/badminton/src/bai_badminton/score_ocr.py`

The primary `Sports_Analytics` implementation remains untouched. The patch adds a source-transition mapping-vote ledger. A vote requires a canonical independently corroborated transition and each transition ID contributes at most once, regardless of query count, changed geometry answer or accepted-point ownership refolding. The existing3-vote/2×dominance thresholds and all numerical OCR/geometry settings remain unchanged. Vote provenance resets with the existing competitor-name epoch reset. Existing deep-copy scoring transaction checkpoints naturally include the new reconciler field; no engine source change is needed.

A new worktree-only test module `sports/badminton/tests/test_score_mapping_vote_provenance.py` covers seven meaningful behaviors: repeated queries, three independent points, contradictory repeated geometry, late same-value confirmations, accepted-point claim refolding, name-epoch reset and checkpoint-copy independence.

Before the patch,6new tests failed and1passed (`worktree_vote_red.log`). After the patch, the full score-test glob passed **193 tests** (`worktree_score_unique_green.log`). The collection-only log (`score_collection.log`) independently records distinct node IDs; the earlier combined selection also passed193 tests and must not be added as separate coverage. No new neural inference was run by this task. Root controls fresh end-to-end baseline/regression and any model/version promotion.

## Limits and next evidence

- Keep correct source20:20 acquisition and anonymous/unknown identity behavior unchanged during the fresh regression.
- Do not infer physical accuracy from unit success; compare actual fresh rally/score/event outputs against the preserved baseline.
- The safety patch has a demonstrated code-level effect for repeated queries. It is expected to leave the current anonymous Test1 baseline's winner coverage unchanged.
- Verified athlete/track/row binding, source-cut score continuity, accepted rally-point association, and independently reviewed outcome/score labels remain separate work. No annotation-specific row, name blacklist, fitted score offset, synthetic winner or point padding was introduced.
