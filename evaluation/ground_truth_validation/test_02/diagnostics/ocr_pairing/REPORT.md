# Test 2 OCR pairing: inherited repair already present

No new production fix is required for the historical branding/score-field
association example. This review found the relevant repair already included in
the actual current source, beyond the three narrow correctness repairs described
in the Test 1 status summary. It was published with commit `b124f42` and is covered
by existing spatial-parser regressions.

## Reproduction and provenance

The historical fixed-crop model diagnostic used canonical Test 2 frame 22924,
764.133333 seconds, original source SHA256
`4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a`.
Its retained image visibly contains AXELSEN / ANTONSEN and a separate SXFI / LIVE
logo. Recorded OCR tokens omit the top row's current digit: `AXELSEN`, `16 21`,
`ANTONSEN`, `21 5 12`, plus the branding and unrelated corner text. The visible
image is diagnostic evidence; it is not a newly adjudicated full score sequence.

The committed existing fixture in
`sports/badminton/tests/test_scoreboard_spatial_board.py` retains these tokens and
their axis-aligned bounding rectangles. `reproduce_parser_history.py` applies
the same observations to read-only historical parser snapshots and current code.
No OCR network, video decoding, label table or production source edit is involved.
Original OCR quadrilaterals were not retained in the probe JSON; the geometry
scope is explicitly the existing committed bounding-rectangle regression fixture.

| Implementation | Source SHA256 | Deterministic result |
|---|---|---|
| Historical `caa9176` and `b124f42^` | `541009a669fdfa62a4267162caabdf6233fce1d95c9d0024248cbb4d42e7e588` | `SXFI:21 / LIVE:12`, confidence 0.929; incorrectly associates athlete score fields with branding |
| Current `nearest-name-current-column-v2` | Recorded in `parser_history_evidence.json` | Abstains; no reading or crop lock |

The historical source hash exactly matches the parser hash recorded by the old
model probe. The historical reproduction matches its saved bad reading. Current
source assigns numeric fields to the nearest eligible name to their left, which
prevents a distant logo from borrowing the athlete's numbers. With the upper
current digit absent, the two true current-score columns do not align; abstention
is appropriate. Reading 21 as the current upper score or inventing the absent
digit from this fixture would not be a justified correction.

The existing complete-current-column control reads `AXELSEN:9 / ANTONSEN:12`
when its upper numeric token explicitly contains `16 21 9`; its ROI excludes the
logo. That is a deterministic parser control, not a new inference or a ground
truth sporting-accuracy result.

## Regression result and Test 1 safety

`current_parser_regression.log` records **37 passed, one deselected**. The command
uses the original GPU runtime environment and existing `.venv`; the deselected
case performs a fresh OCR model call and was intentionally outside this
deterministic review task:

```bash
source ../gpu-env.sh
PYTHONPATH="$PWD/engine/src:$PWD/sports/badminton/src:$PWD/agents/src:$PWD/apps/api/src:$PWD" \
  .venv/bin/python -m pytest \
  sports/badminton/tests/test_scoreboard_spatial_board.py \
  sports/badminton/tests/test_scoreboard.py \
  sports/badminton/tests/test_score_mapping_vote_provenance.py \
  -k 'not real_ocr_reads_a_rendered_scoreboard' -q
```

Controls cover unrelated sponsor text, absent boards, multiple plausible boards,
three aligned rows, invalid/current missing values, singles and doubles names,
numeric fields left of names, clocks, reversed token order, scale changes,
nearest-name association, crop locking and source-transition vote provenance.

No Test 1 source or output was changed. Its completed latest-pipeline run already
included this inherited parser implementation, so no new Test 1 inference is
needed solely for this read-only check. The current fresh Test 2 baseline will
establish actual full-video OCR coverage under the already-improved parser.
Do not infer a full-video score gain from this one deterministic fixture.

## Artifacts and disposition

- `parser_history_evidence.json`: token fixture, source hashes and old/current
  outputs, with explicit geometry and accuracy limitations.
- `historical_parser_caa9176.py`, `historical_parser_b124f42_parent.py`: exact
  historical source snapshots, not executable production replacements.
- `parser_history_execution.log`: deterministic comparison output.
- `current_parser_regression.log`: current tests.
- `reproduce_parser_history.py`: reproducible comparison script; uses exclusive
  output creation to avoid silently overwriting evidence.

No additional failing test or patch was manufactured. Continue investigating
current scene continuity, perception dropout and supported annotation comparisons;
do not repeat this already-resolved historical OCR fix.
