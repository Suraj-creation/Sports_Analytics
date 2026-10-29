// A hand-authored, synthetic record shared by the catalogue and guided investigation.
// These labels are illustration data, not measured events or a model accuracy result.
const sequences = [
  ['clear', 'drop', 'lift', 'smash', 'net', 'unknown'],
  ['clear', 'lift', 'clear', 'drop', 'smash', 'drive', 'lift', 'smash', 'net', 'unknown'],
  ['clear', 'drop', 'lift', 'unknown'],
  ['clear', 'lift', 'clear', 'drop', 'drive', 'smash', 'lift', 'clear', 'drop', 'smash', 'drive', 'net', 'unknown', 'unknown'],
  ['clear', 'drop', 'lift', 'drive', 'smash', 'clear', 'unknown', 'unknown'],
  ['clear', 'lift', 'clear', 'drop', 'drive', 'smash', 'lift', 'clear', 'drop', 'drive', 'net', 'unknown'],
];
const durations = [8, 12, 6, 18, 10, 16];
const shotLabels = { clear: 'Clear', drop: 'Drop', smash: 'Smash', lift: 'Lift', drive: 'Drive', net: 'Net shot', unknown: 'Unknown' };
let strokeId = 0;

function freezeRecord(record) {
  for (const value of Object.values(record)) {
    if (value && typeof value === 'object') freezeRecord(value);
  }
  return Object.freeze(record);
}

export const sample = freezeRecord({
  title: 'An illustrative six-rally record',
  source: 'Synthetic fixture — not measured match footage',
  rallies: sequences.map((types, index) => ({
    id: `R${index + 1}`,
    duration: durations[index],
    official: true,
    shots: types.map((type, shotIndex) => ({ id: `E${++strokeId}`, type, player: shotIndex % 2 === 0 ? 'P1' : 'P2' })),
  })),
  excludedExchanges: [
    { id: 'W1', official: false, duration: 11, reason: 'Warm-up', shots: [
      { id: 'W1E1', type: 'clear', player: 'P1' }, { id: 'W1E2', type: 'lift', player: 'P2' },
    ] },
    { id: 'W2', official: false, duration: 7, reason: 'Warm-up', shots: [
      { id: 'W2E1', type: 'drive', player: 'P1' }, { id: 'W2E2', type: 'drive', player: 'P2' },
    ] },
  ],
});

const officialRallies = () => sample.rallies.filter((rally) => rally.official);
const officialIds = () => officialRallies().map((rally) => rally.id);

export function getSummary() {
  const rallies = officialRallies();
  const shots = rallies.flatMap((rally) => rally.shots);
  const unknownStrokes = shots.filter((shot) => shot.type === 'unknown').length;
  const longest = [...rallies].sort((a, b) => b.shots.length - a.shots.length || b.duration - a.duration)[0];
  return {
    officialRallies: rallies.length,
    strokeCount: shots.length,
    activePlaySeconds: rallies.reduce((total, rally) => total + rally.duration, 0),
    meanShots: rallies.length ? shots.length / rallies.length : null,
    longestRallyId: longest?.id ?? null,
    unknownStrokes,
    classifiedStrokes: shots.length - unknownStrokes,
    classificationCoverage: shots.length ? (shots.length - unknownStrokes) / shots.length : null,
  };
}

export function getShotMix() {
  const shots = officialRallies().flatMap((rally) => rally.shots);
  return Object.entries(shotLabels).map(([type, label]) => {
    const count = shots.filter((shot) => shot.type === type).length;
    return { type, label, count, share: shots.length ? count / shots.length : 0 };
  });
}

export function getPatterns() {
  const pairs = new Map();
  let denominator = 0;
  for (const rally of officialRallies()) {
    for (let index = 0; index < rally.shots.length - 1; index++) {
      const from = rally.shots[index].type;
      const to = rally.shots[index + 1].type;
      const key = `${from}:${to}`;
      const pattern = pairs.get(key) ?? { from, to, count: 0, evidence: [] };
      pattern.count++;
      if (!pattern.evidence.includes(rally.id)) pattern.evidence.push(rally.id);
      pairs.set(key, pattern);
      denominator++;
    }
  }
  // Unknown is retained: each official adjacent observation contributes to the denominator.
  return [...pairs.values()]
    .sort((a, b) => b.count - a.count || a.from.localeCompare(b.from) || a.to.localeCompare(b.to))
    .map((pattern) => ({ ...pattern, denominator }));
}

export function getHighlights() {
  return [...officialRallies()]
    .sort((a, b) => b.shots.length - a.shots.length || b.duration - a.duration || a.id.localeCompare(b.id))
    .slice(0, 3)
    .map((rally) => ({
      id: rally.id,
      title: `Rally ${rally.id.slice(1)} · ${rally.shots.length} candidate strokes`,
      reason: 'Ranked by candidate stroke count, then duration. An illustrative selection rule, not a performance score.',
      shots: rally.shots.length,
      duration: rally.duration,
      evidence: [rally.id],
    }));
}

const summary = getSummary();
const metricScope = 'The six official rallies in this synthetic sample; these are not measurements from the displayed imagery.';
const metricExclusions = 'The two warm-up exchanges are excluded from official totals.';

export const metricDefinitions = freezeRecord({
  activePlay: {
    title: 'Active rally play',
    question: 'How much of the sample is marked as rally play?',
    formula: `Sum of official rally durations = ${summary.activePlaySeconds} seconds`,
    scope: metricScope,
    exclusions: metricExclusions,
    limitation: 'Segmented rally time is not total video duration, exercise time or time on court.',
    evidence: officialIds(),
  },
  meanShots: {
    title: 'Mean candidate strokes per rally',
    question: 'How many candidate strokes does the average official sample rally contain?',
    formula: `${summary.strokeCount} candidate strokes / ${summary.officialRallies} official rallies = ${summary.meanShots}`,
    scope: metricScope,
    exclusions: `${metricExclusions} Unknown stroke labels remain in the count.`,
    limitation: 'Candidate event counts depend on event detection; a label does not establish a verified contact.',
    evidence: officialIds(),
  },
  classificationCoverage: {
    title: 'Classification coverage',
    question: 'What proportion of candidate strokes has a known label?',
    formula: `${summary.classifiedStrokes} labelled candidates / ${summary.strokeCount} total candidates = ${summary.classifiedStrokes} / ${summary.strokeCount}`,
    scope: metricScope,
    exclusions: `${metricExclusions} Unknown labels are excluded from the numerator and retained in the denominator.`,
    limitation: 'Coverage is not accuracy. Rule-based shot names are a preview; assigning a label does not establish that it is correct.',
    evidence: officialIds(),
  },
});

function overviewStep() {
  return {
    tool: 'match_overview',
    title: 'Check the sample scope',
    detail: `${summary.officialRallies} official sample rallies; ${sample.excludedExchanges.length} warm-up exchanges excluded. No live video or model is queried.`,
  };
}

function groundingStep(detail) {
  return { tool: null, title: 'Local grounding check', detail };
}

function unsupported(text) {
  return {
    supported: false,
    kind: 'unsupported',
    text,
    evidence: [],
    steps: [overviewStep(), groundingStep('The sample has no eligible evidence for this request. No measurement or source citation is invented.')],
  };
}

function hasOnlyScopeWords(text, allowed) {
  const words = text.replace(/[?!.,:]/g, ' ').trim().split(/\s+/).filter(Boolean);
  return words.every((word) => allowed.includes(word));
}

/** A bounded, offline example router. This is deterministic demo logic, not an LLM. */
export function investigate(question) {
  if (typeof question !== 'string' || !question.trim() || question.length > 1000) {
    return unsupported('This offline sample supports rally-count thresholds and total active play. Ask one of those questions to inspect its evidence.');
  }
  const query = question.trim().toLowerCase().replace(/\bwhat's\b/g, 'what is');
  if (/\b(?:speed|fast|biomechanics?|joints?|knees?|angles?|injur\w*|torque|forces?|muscles?)\b|km\/?h|mph|m\/s|jump height/.test(query)) {
    return unsupported('This synthetic sample cannot establish speed or biomechanics. Such measurements need validated temporal, trajectory, calibration or instrumentation evidence appropriate to the question.');
  }
  if (/\bp\d+\b|\b(?:players?|winning|winners?|won|lost|scores?|compare|comparison|previous|sessions|yesterday|weeks?|teams?|doubles|matches)\b/.test(query)) {
    return unsupported('This offline example does not support player filters, outcomes or comparisons across sessions. Its answers cover the official rallies in this sample only.');
  }

  const threshold = query.match(/(?:at least|>=|≥|minimum(?: of)?|no fewer than)\s*(\d+)(?![\d.])\s*(?:candidate\s+)?(?:shots?|strokes?)\b/)
    ?? query.match(/\b(\d+)\s*\+\s*(?:candidate\s+)?(?:shots?|strokes?)\b/);
  const rallyScopeWords = ['show', 'find', 'list', 'get', 'which', 'what', 'how', 'many', 'me', 'all', 'the', 'official', 'sample', 'rallies', 'rally', 'have', 'has', 'had', 'with', 'contain', 'contains', 'having', 'in', 'this', 'are', 'there', 'please'];
  if (/\brall(?:y|ies)\b/.test(query) && threshold && hasOnlyScopeWords(query.replace(threshold[0], ''), rallyScopeWords)) {
    const minimum = Number(threshold[1]);
    if (!Number.isSafeInteger(minimum)) return unsupported('Use a whole-number stroke threshold for the official rallies in this sample.');
    const rallies = officialRallies().filter((rally) => rally.shots.length >= minimum);
    const evidence = rallies.map((rally) => rally.id);
    const steps = [overviewStep(), {
      tool: 'list_rallies',
      title: 'Retrieve eligible rallies',
      detail: `Filter: at least ${minimum} candidate strokes. ${rallies.length} official sample rallies match.`,
    }];
    if (rallies.length) steps.push({
      tool: 'get_rally',
      title: 'Inspect the supporting records',
      detail: rallies.map((rally) => `${rally.id}: ${rally.shots.length} candidate strokes, ${rally.duration} seconds`).join('; '),
    });
    steps.push(groundingStep('The count and each citation resolve to the same eligible sample records. Unknown stroke labels remain in the stroke count.'));
    return {
      supported: true,
      kind: 'rallies',
      text: `${rallies.length} official sample ${rallies.length === 1 ? 'rally has' : 'rallies have'} at least ${minimum} candidate strokes.${rallies.length ? ` Evidence: ${evidence.join(', ')}.` : ' No matching rally is present.'} The two warm-up exchanges are excluded.`,
      evidence,
      steps,
    };
  }
  const activeScopeWords = ['how', 'much', 'long', 'what', 'is', 'was', 'the', 'total', 'active', 'rally', 'play', 'time', 'duration', 'in', 'this', 'sample', 'calculate', 'show', 'me', 'find', 'give', 'please', 'seconds', 'of', 'amount', 'does', 'contain', 'shuttle'];
  if ((/\bactive\s+(?:rally\s+)?play\b|\brally play\b|\bshuttle in play\b/.test(query)) && hasOnlyScopeWords(query, activeScopeWords)) {
    return {
      supported: true,
      kind: 'active-play',
      text: `The sample contains ${summary.activePlaySeconds} seconds of active rally play: the sum of ${summary.officialRallies} official rally durations. The two warm-up exchanges are excluded. This is not total video duration or exercise time.`,
      evidence: officialIds(),
      steps: [overviewStep(), {
        tool: 'list_rallies',
        title: 'Retrieve official rally durations',
        detail: officialRallies().map((rally) => `${rally.id}: ${rally.duration}s`).join('; '),
      }, groundingStep(`Local calculation: ${officialRallies().map((rally) => rally.duration).join(' + ')} = ${summary.activePlaySeconds} seconds. Every contributing rally is cited.`)],
    };
  }
  return unsupported('This offline sample supports questions such as “Show rallies with at least 10 shots” and “How much active play is in this sample?” It cannot answer other match questions.');
}
