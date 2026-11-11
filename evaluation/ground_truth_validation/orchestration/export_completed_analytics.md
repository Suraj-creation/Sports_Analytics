# Completed-session analytics export

`export_completed_analytics.py` exports the current canonical analytics fold from an already completed and strictly verified upload, without neural inference, semantic observation replay, a web server or provider calls.

```bash
source ../gpu-env.sh
.venv/bin/python evaluation/ground_truth_validation/orchestration/export_completed_analytics.py \
  --run /absolute/path/to/completed_run \
  --output /absolute/path/to/new_external/analytics_export
```

Only the two arguments above are needed for a new ordinary successful baseline. The optional `--completion-recovery` is solely for a historical run with the existing explicit independent completion proof; it never changes that original failed receipt. An incomplete/failed new run without such a proof is rejected. The existing strict `load_finished_input` verifier must pass before the helper creates its output.

## Isolation and provenance

The helper reads the source JSONL ledger and session, recreates a new detached SQLite event store, and copies observation-track Parquet files into the new external output. It never constructs an EventStore or SQLite connection on an original database. Original event IDs, payloads, correction ancestry and original sequence order are retained. If original sequence integers have gaps, detached integers may be dense; any such remapping is recorded explicitly. Original source/session/receipt/track/SQLite/WAL/SHM files are hash-bound and checked unchanged after export.

It uses the same actual functions as the current pipeline/API: `analytics.rebuild.build`, `rally_records`, `build_individual_analytics`, and `build_estimated_individual_analytics`. Derived outputs remain estimates; the helper does not inject CSV labels or force reference winners/scores.

## Outputs

- `analytics.json`: actual public canonical match fold plus the pipeline's `highlights(k=12)` output.
- `highlights.json`: ranked canonical highlights and evidence/bounds checks; no rendered clip or relevance accuracy claimed.
- `rally_outcome_records.json`: complete canonical rally records, including official/unknown statuses and event references. `score_after` is exported as null whenever `score_available` is false, avoiding interpretation of an internal zero placeholder as verified0–0.
- `individual_analytics.json`: actual reviewed player/participant fold.
- `estimated_individual_analytics.json`: separately labelled actual automatic estimates, preserving anonymous/unresolved coverage.
- `scoring_outcome_evidence.json`: original live point, score observation/correction, broadcast score, phase, rally and identity ambiguity evidence, with full original payloads and event IDs.
- `live_events.jsonl`: all current live events, including types beyond those grouped in the scoring summary.
- `unavailable_and_limits.json`: degradation and missing ground-truth/identity/relevance certification; no invented accuracy.
- `detached/`: copied session, recreated event store and copied track files used for reproducibility.
- `export_receipt.json`: completion binding, input and output hashes, original preservation, counts, provenance and any sequence remapping.

The verified completion helper also checks the original source video. A historical run whose source was removed is not silently rebound to a different file. Use a source-retained historical baseline for the validation check. The fresh current baseline retains its original source and uses the normal strict completion route.

## Validation

The offline check **passed** against the genuine complete historical Test1 neural run, using its explicit independently verified finalization proof. Validation output is separate from all historical results:

`../ground-truth-validation-artifacts-20261110/helper_validation/test01_analytics_export_v1/`

Command/output log: `export_completed_analytics_validation.log` next to this document. The historical proof rechecks original caches, source/proxy PTS and model bindings, so that validation can take several CPU minutes before the detached export begins. This is not a neural run. The final outcome and invariant checks are recorded in the receipt and subsequent validation log.

Validated outcome: 17,268 frames, 2,416 original append-only events, 1,796 current live events, 36 canonical rallies (20 official / 16 unofficial), and 12 ranked highlights. All highlight IDs and bounds passed; unavailable scores stayed null; no sequence remapping was needed; original input hashes and all exported JSON/JSONL hashes passed. The helper opened no original SQLite database and ran no neural inference. Machine-readable assertions are in `export_completed_analytics_validation.json`.
