import test from 'node:test';
import assert from 'node:assert/strict';
import { getAnswer, getPhase } from '../src/demo-data.js';
import { buildBrief } from '../src/brief-model.js';

test('an unavailable measurement never supplies fabricated speed or source evidence', () => {
  const answer = getAnswer('speed');
  assert.equal(answer.status, 'Insufficient evidence');
  assert.equal(answer.phase, null);
  assert.match(answer.body, /cannot establish/i);
  assert.doesNotMatch(answer.body, /\d+\s*(km|mph|m\/s)/);
});

test('an evidence citation resolves to the source phase it describes', () => {
  const answer = getAnswer('recovery');
  const phase = getPhase(answer.phase);
  assert.equal(phase.title, 'Recovery');
  assert.match(phase.image, /recovery/);
});

test('brief generation preserves user content as plain text without claiming delivery', () => {
  const brief = buildBrief({ role: 'coach', source: 'phone', goal: '  Review <script>my weekly sessions</script>.  ' });
  assert.match(brief, /Coach/);
  assert.match(brief, /Phone recording/);
  assert.match(brief, /<script>my weekly sessions<\/script>/);
  assert.match(brief, /not been sent/i);
});

test('an unusable goal or unknown role cannot create a misleading brief', () => {
  assert.throws(() => buildBrief({ role: 'coach', source: 'fixed', goal: '   ' }), /10/);
  assert.throws(() => buildBrief({ role: 'admin', source: 'fixed', goal: 'Review the recorded match' }), /role/i);
  assert.throws(() => buildBrief({ role: 'player', source: 'fixed', goal: 'x'.repeat(1201) }), /1200/);
});
