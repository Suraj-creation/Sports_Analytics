import test from 'node:test';
import assert from 'node:assert/strict';
import { buildBrief } from '../src/brief-model.js';

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
