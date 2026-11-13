# Independent codec23 and schema-helper validation

**Passed:** 119 source-guarded native synthetic tests, including36 new codec23 cases,45 acquisition cases and38 historical codec/decision cases. The new test file is `sports/badminton/tests/test_scene_acquisition_codec_v23.py`. Only that candidate test file was authored for this task; production corrections were made by the root owner. No neural inference, video decoding, real-data evaluation or Test3 access occurred.

The tests use a synthetic25FPS Session/media context and explicitly constructed court/camera observations. They exercise the actual native `BadmintonSession` encoder/decoder. Synthetic detector/image identities are fixtures, not evidence of real-video accuracy. [Execution receipt](execution_receipt.json) binds the command, native candidate imports, seven source/test hashes before and after execution, and [119-pass log](guarded_tests.log). Candidate commit after execution: `9992f87fc24c51da28ada77c07d15e9e18338232`.

The36 new cases verify:

- Singles/two and doubles/four complete weak scene proofs at chunk start and with an adjacent cached camera frame, without manufacturing any player identity.
- The calibrated court reference fingerprint, exact float32 projected polygon, current camera, serialized previous camera, derived relative transform, detector/model/frame/image dimensions, calibration/view/replay state, and receiver-bound isolation policy.
- A camera-explained pan cannot authorize a weak reset even when the raw old/current boxes are disjoint, all current detections remain inside the source court, and the serialized camera pair is internally consistent.
- The mandatory acquisition decision remains required when the strong image hypothesis is false.
- New rawV4/decisionV3 families cannot be relabelled codec21/22. Actual historical rawV2/decisionV1 records still decode under21/22, and existing rawV3/decisionV2 tests remain valid.
- Weak expected participant count binds to the immutable format context known at chunk start. Unknown, unconfirmed or conflicting contexts reject the proof; a legitimate later inferred-format transition does not invalidate that earlier context.

Two independent review findings were reported before production edits: the missing codec-family downgrade guard and the missing confirmed-format/count binding. Root added both; the final tests exercise their rejected cases. The first test attempt failed because the new fixture supplied NumPy scalar values to an intentionally strict built-in-number contract. The fixture was corrected to Python floats; no production relaxation was needed. Initial and intermediate logs are preserved separately.

At a chunk’s first frame, serialized previous-camera geometry is a producer claim checked against the current-camera/relative-transform arithmetic. When the previous frame is present in the same chunk, its actual recorded camera must also match. This decoder alone cannot independently observe an omitted prior chunk; completed-run provenance and any cross-chunk audit remain necessary. Court/reference identity is also checked against the receiving isolation policy rather than treating a self-consistent forged header as trusted source evidence.

## Independent evaluator/helper review

[Helper review receipt](helper_review.json) verifies all **seven original evaluator/guard modules** remain byte-identical and AST-identical to the prior sealed independent review and equal between MAIN and this native candidate. Therefore their scalar scoring thresholds, interval/point matching and numeric aggregation are unchanged.

The three schema helpers are also byte-identical between MAIN and candidate. Compared with the previously sealed codec22 proposal, `normal_timestamp_audit.py` is entirely unchanged. The only other changes are:

1. Normal completed-cache validation accepts23 alongside21/22 and updates its descriptive error label; historical `validate_cache21` remains strictly21.
2. The catalogue accepts23 and invokes the same native decoder for it.
3. Historical acceptance-policy normalization additionally recognizes a published20/21/22 catalogue only when every observed file actually fits that policy. Hashes, population/source bindings and other limits remain exact.

The audit normalizes only these declared schema-list/label edits and requires full remaining source text and AST equality. PTS decoding, proxy verification, timing/alignment arithmetic and scoring/matching code were not changed. No annotation contents or metrics were reopened for this review. The audit script and exact input hashes are preserved with the receipt.

These are contract and reproducibility checks, not acceptance of the candidate on real footage or a claim of physical accuracy improvement. Full source-bound regression and visual review remain the root orchestrator’s next gate.
