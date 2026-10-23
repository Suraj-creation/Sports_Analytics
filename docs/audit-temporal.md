# Temporal and event integrity audit — 23 October 2026

## Scope and flow

Baseline: `d661bc5`; implementation: `codex/production-audit-20261023` working tree.
The existing engine consumes ordered perception chunks, stabilizes geometry,
post-processes shuttle samples, detects contact hypotheses, segments exchanges,
waits for scoreboard evidence, decides official-play eligibility, infers outcomes,
folds accepted winners through BWF rules, and aggregates accepted evidence.
This audit improves that implementation without changing its perception models.

## Demonstrated defects and changes

1. **Observation end became a point.** Closing a live exchange at EOF or a camera
   cut still ran landing/extrapolation heuristics. A truncated synthetic flight
   produced a confirmed P2 point (`c1_crossed_out`). Cut/EOF outcomes now return
   `unknown` with `rule_check=incomplete_rally`. Explicit OCR or reviewer evidence
   can resolve them; segmentation alone cannot award the point.
2. **Missing evidence admitted official play.** Uncalibrated initial activity was
   assumed official, and a serve formation with unknown stationarity established
   match play. Both now abstain with `phase_basis=insufficient`. Existing explicit
   reviewer and scoreboard authority remains intact.
3. **Candidate strokes leaked into live statistics.** Before a containing rally
   was accepted, an open warm-up exchange exposed five strokes as match statistics.
   Aggregation now waits for official rally acceptance; canceled and unofficial
   exchanges retain evidence without affecting accepted shot counts.
4. **Correction IDs bypassed warm-up exclusion.** Replacing a warm-up stroke
   created a new event ID that escaped an exclusion list of old IDs. Rebuilding
   now resolves canonical shot revisions and includes only official rally-owned
   stroke IDs. The regression previously added one unsupported drive.
5. **Receiver feet masqueraded as a shuttle landing.** Classification now emits
   `receiver_court_xy` plus `landing_source=receiver_position`. The legacy coordinate
   alias remains for compatibility; analytics can explicitly withhold landing maps.

`score_available` is set only where a canonical accepted point exists, so missing
outcomes do not fabricate zero-score timeline observations. Refolds and canonical
analytics rebuilds refresh this availability along with corrected shot references.

## Regression evidence

Six added parameterized engine/phase cases cover these defects; regression failures
were reproduced before their fixes. The focused engine/phase suite passed 26
tests. Independent evaluator and analytics-integrity suites passed 29 tests.
Ruff and `git diff --check` passed. Consult the integrated audit for final full-suite
counts after all specialist changes.

## Full cached-observation comparison

| Recording | Decoded frames | Exchanges before/after | Official before/after | Points before → after |
| --- | ---: | ---: | ---: | ---: |
| SampleRally | 480 | 1 / 1 | 0 / 0 | 0 → 0 |
| Singles broadcast | 12,075 | 25 / 25 | 24 / 24 | 24 → 23 |
| Doubles broadcast | 12,148 | 28 / 28 | 24 / 24 | 24 → 21 |
| Multi-court incident | 22,802 | 64 / 64 | 50 / 50 | 50 → 49 |

The five changed outcomes all terminate at camera cuts. Their winners now remain
unresolved. Every segmented start/end and official-play decision was unchanged.
Source media hashes and cached-observation hashes match across runs. Results are
in [before](testing/audit-20261023/cache-replay-before.json) and
[after](testing/audit-20261023/cache-replay-after.json), including per-rally intervals.

This is **cached perception / semantic regression**, not fresh GPU inference or
labelled accuracy. Historical codecs 1, 3 and 5 are decoded explicitly by the
research harness; production codec-6 invalidation remains enforced. Replay uses
the initial recorded calibration, camera reference, source metadata, model
observations and OCR. It excludes padded frames beyond decoded media length and
does not apply historical reviewer corrections. The doubles recording exercises
the incumbent two-identity implementation; it does not validate four-player play.

Abstaining on a cut is conservative: one incident cut had a stationary-landing
hypothesis. Without independent labels, withholding that point does not establish
that the former winner was wrong. Serve-formation heuristics and normally ended
rally outcomes still require annotated official-play, contact and outcome labels.

## Reproduce safely

Run on the authoritative GPU server from the repository root. Output directories
must be fresh and outside source session directories. Source SQLite connections
are read-only; original session events, tracks and caches are not replaced.
Each output contains fresh SQLite stores, a status manifest and a JSON summary.
Failed replay retains `status=failed` and any completed session summaries.

```bash
source ../gpu-env.sh
source .venv/bin/activate
replay_work=$(mktemp -d /tmp/bai-replay.XXXXXX)
mkdir "$replay_work/baseline"
git archive d661bc5 sports/badminton/src engine/src | tar -x -C "$replay_work/baseline"
PYTHONPATH="$replay_work/baseline/sports/badminton/src:$replay_work/baseline/engine/src" \
  python research/replay_cached_observations.py --data-dir data \
  --output-dir "$replay_work/before" --implementation-label d661bc5
PYTHONPATH="$PWD/sports/badminton/src:$PWD/engine/src" \
  python research/replay_cached_observations.py --data-dir data \
  --output-dir "$replay_work/after" --implementation-label production-audit-working-tree
pytest -q sports/badminton/tests/test_engine.py sports/badminton/tests/test_match_phase.py
```

The JSON provenance records the loaded engine source path/hash, implementation
label, cache hashes, coverage, calibration policy and `accuracy_claim=false`.
Reported runtimes measure CPU semantic replay of stored observations only.
