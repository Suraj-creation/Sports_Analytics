import test from 'node:test';
import assert from 'node:assert/strict';
import * as catalogue from '../src/catalogue-data.js';

test('the catalogue exposes the shared analytics model', () => {
  assert.ok(catalogue, 'The shared catalogue data module must exist');
  for (const name of ['getSummary', 'getShotMix', 'getPatterns', 'getHighlights', 'investigate']) {
    assert.equal(typeof catalogue[name], 'function', `${name} must be available to the UI`);
  }
});

test('official totals exclude both warm-up exchanges', () => {
  assert.ok(catalogue);
  const summary = catalogue.getSummary();
  assert.deepEqual(summary, {
    officialRallies: 6,
    strokeCount: 54,
    activePlaySeconds: 70,
    meanShots: 9,
    longestRallyId: 'R4',
    unknownStrokes: 8,
    classifiedStrokes: 46,
    classificationCoverage: 46 / 54,
  });
  assert.equal(catalogue.sample.excludedExchanges.length, 2);
  assert.ok(catalogue.sample.excludedExchanges.every((rally) => !rally.official));
  assert.ok(catalogue.sample.excludedExchanges.every((rally) => rally.shots.length > 0 && rally.duration > 0));
});

test('the same fixture supplies every official rally and unique stroke identity', () => {
  assert.ok(catalogue);
  const rallies = catalogue.sample.rallies;
  assert.deepEqual(rallies.map((rally) => [rally.id, rally.duration, rally.shots.length, rally.official]), [
    ['R1', 8, 6, true], ['R2', 12, 10, true], ['R3', 6, 4, true],
    ['R4', 18, 14, true], ['R5', 10, 8, true], ['R6', 16, 12, true],
  ]);
  const ids = rallies.flatMap((rally) => rally.shots.map((shot) => shot.id));
  assert.equal(new Set(ids).size, 54);
  assert.ok(rallies.every((rally) => rally.shots.every((shot) => ['P1', 'P2'].includes(shot.player))));
});

test('shot shares retain Unknown in their denominator', () => {
  assert.ok(catalogue);
  const mix = catalogue.getShotMix();
  const counts = Object.fromEntries(mix.map(({ type, count }) => [type, count]));
  assert.deepEqual(counts, { clear: 12, drop: 8, smash: 7, lift: 9, drive: 6, net: 4, unknown: 8 });
  assert.equal(mix.find((row) => row.type === 'smash').share, 7 / 54);
  assert.equal(mix.find((row) => row.type === 'unknown').share, 8 / 54);
  assert.ok(mix.every((row) => row.label.length > 0));
  assert.ok(Math.abs(mix.reduce((sum, row) => sum + row.share, 0) - 1) < 1e-12);
});

test('adjacent patterns use 48 within-rally pairs and never bridge rally boundaries', () => {
  assert.ok(catalogue);
  const patterns = catalogue.getPatterns();
  assert.equal(patterns.reduce((sum, pattern) => sum + pattern.count, 0), 48);
  assert.ok(patterns.every((pattern) => pattern.denominator === 48));
  // Every rally ends Unknown and the next starts Clear. A flattened implementation
  // would invent this transition five times.
  assert.equal(patterns.find((pattern) => pattern.from === 'unknown' && pattern.to === 'clear'), undefined);
  const clearDrop = patterns.find((pattern) => pattern.from === 'clear' && pattern.to === 'drop');
  assert.equal(clearDrop.count, 8);
  assert.deepEqual(clearDrop.evidence, ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']);
  const unknownPair = patterns.find((pattern) => pattern.from === 'unknown' && pattern.to === 'unknown');
  assert.equal(unknownPair.count, 2);
  assert.deepEqual(unknownPair.evidence, ['R4', 'R5']);
});

test('pattern citations resolve to a rally containing the described adjacent pair', () => {
  assert.ok(catalogue);
  for (const pattern of catalogue.getPatterns()) {
    for (const id of pattern.evidence) {
      const rally = catalogue.sample.rallies.find((row) => row.id === id);
      assert.ok(rally?.official, `Pattern cites an official rally: ${id}`);
      assert.ok(rally.shots.some((shot, index) => shot.type === pattern.from && rally.shots[index + 1]?.type === pattern.to));
    }
  }
});

test('highlights rank reproducibly by observed stroke count and retain source values', () => {
  assert.ok(catalogue);
  const highlights = catalogue.getHighlights();
  assert.deepEqual(highlights.map(({ id, shots, duration }) => [id, shots, duration]), [
    ['R4', 14, 18], ['R6', 12, 16], ['R2', 10, 12],
  ]);
  for (const highlight of highlights) {
    assert.deepEqual(highlight.evidence, [highlight.id]);
    assert.match(highlight.reason, /stroke count/i);
    assert.doesNotMatch(highlight.reason, /winner|accuracy|best technique/i);
  }
  assert.deepEqual(catalogue.getHighlights(), highlights);
});

test('definitions explain the denominator and cite eligible records', () => {
  assert.ok(catalogue);
  for (const key of ['activePlay', 'meanShots', 'classificationCoverage']) {
    const metric = catalogue.metricDefinitions[key];
    for (const field of ['title', 'question', 'formula', 'scope', 'exclusions', 'limitation']) {
      assert.equal(typeof metric[field], 'string');
      assert.ok(metric[field].length > 0);
    }
    assert.deepEqual(metric.evidence, ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']);
    assert.match(metric.exclusions, /warm.up/i);
  }
  assert.match(catalogue.metricDefinitions.classificationCoverage.formula, /46\s*\/\s*54/);
  assert.match(catalogue.metricDefinitions.classificationCoverage.limitation, /not accuracy/i);
});

test('a threshold investigation returns exactly the matching official evidence', () => {
  assert.ok(catalogue);
  for (const question of ['Show rallies with at least 10 shots', 'Which rallies have >=10 strokes?', 'Find rallies with 10+ shots']) {
    const result = catalogue.investigate(question);
    assert.equal(result.supported, true);
    assert.equal(result.kind, 'rallies');
    assert.deepEqual(result.evidence, ['R2', 'R4', 'R6']);
    assert.match(result.text, /3/);
    assert.match(result.text, /sample/i);
    assert.deepEqual(result.steps.filter((step) => step.tool).map((step) => step.tool), [
      'match_overview', 'list_rallies', 'get_rally',
    ]);
    assert.equal(result.steps.at(-1).tool, null);
    assert.match(result.steps.at(-1).title, /local.*grounding/i);
  }
});

test('threshold boundaries never add warm-up exchanges or fabricate missing matches', () => {
  assert.ok(catalogue);
  assert.deepEqual(catalogue.investigate('Show rallies with at least 0 shots').evidence, ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']);
  const empty = catalogue.investigate('Show rallies with at least 15 shots');
  assert.equal(empty.supported, true);
  assert.deepEqual(empty.evidence, []);
  assert.match(empty.text, /0|no official/i);
  assert.ok(empty.steps.every((step) => step.tool !== 'get_rally'));
});

test('active-play investigation uses 70 seconds and all six official records', () => {
  assert.ok(catalogue);
  const result = catalogue.investigate('How much active play is in this sample?');
  assert.equal(result.supported, true);
  assert.equal(result.kind, 'active-play');
  assert.match(result.text, /70 seconds/);
  assert.deepEqual(result.evidence, ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']);
  assert.match(result.text, /warm.up/i);
});

test('speed and biomechanics requests abstain without fabricated measurements or citations', () => {
  assert.ok(catalogue);
  for (const question of ['What was the top smash speed?', 'How fast was my recovery?', 'What are my knee angles?', 'Explain my injury risk', 'Show joint torque and biomechanics']) {
    const result = catalogue.investigate(question);
    assert.equal(result.supported, false);
    assert.equal(result.kind, 'unsupported');
    assert.deepEqual(result.evidence, []);
    assert.doesNotMatch(result.text, /\d+\s*(?:km|mph|m\/s|degrees|newtons)/i);
    assert.match(result.text, /cannot|not support/i);
  }
});

test('unsupported player, comparison and external scopes cannot reuse a whole-sample answer', () => {
  assert.ok(catalogue);
  for (const question of [
    'Show P1 rallies with at least 10 shots',
    'Show winning rallies with at least 10 shots',
    'Compare my active play with last week',
    'What is active play across all sessions?',
    'How much active play is in R1?',
    'Predict tomorrow active play',
    'Show rallies with at least 10 shots for Alex',
    'Show rallies with at least 10 shots and under 12 seconds',
    'Show rallies with at least 10 shots but not R4',
    'Who won this match?',
    'Show rallies with at least 10.5 shots',
    '', null, { question: 'active play' }, 'x'.repeat(1001),
  ]) {
    const result = catalogue.investigate(question);
    assert.equal(result.supported, false);
    assert.deepEqual(result.evidence, []);
    assert.ok(result.steps.length <= 4);
  }
});
test('the visible initial question resolves to the same three official rallies', () => {
  const result = catalogue.investigate('Which rallies had at least 10 shots?');
  assert.equal(result.supported, true);
  assert.deepEqual(result.evidence, ['R2', 'R4', 'R6']);
});
