/**
 * Fixture generator.
 *
 * Rallies and shots are generated first; every number anywhere else in the product is then
 * DERIVED from them — stats, heatmaps, highlights, momentum, pair chemistry, the score fold.
 * Nothing is hand-typed twice, so a figure on a card can always be traced to the rallies and
 * the shots that produced it. That is the point: the analytics have to be checkable.
 *
 * The derivations mirror what the engine does today (apps/web/src/features/session/tabs/*,
 * engine match analytics): the same stroke ontology, the same 3x3 court zones, the same
 * highlight reason decomposition with MMR diversity, the same EWMA momentum.
 */

import {
  type Heatmap,
  type HeatmapKind,
  type Highlight,
  type HighlightCategory,
  type Match,
  type MomentumPoint,
  type PairStats,
  type Player,
  type PlayerId,
  type PlayerStats,
  type Rally,
  type ScorePoint,
  type Shot,
  type Side,
  STROKE_FAMILY,
  type Stroke,
  ZONES,
  type Zone,
} from "./types";

export const FPS = 30;

function rng(seed: number) {
  let s = seed >>> 0;
  return () => {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 4294967296;
  };
}

function pick<T>(r: () => number, xs: readonly T[]): T {
  return xs[Math.floor(r() * xs.length) % xs.length] as T;
}

/* ───────────────────────── shot grammar ─────────────────────────
   What can follow what. This is why the shot sequences read like badminton
   rather than a random draw from the stroke list. */

const AFTER: Record<string, Stroke[]> = {
  serve: ["net_shot", "lift", "push", "rush", "drive"],
  attack: ["block", "lift", "net_shot", "drive"],
  defend: ["smash", "drop", "clear", "drive"],
  neutral: ["net_shot", "push", "drive", "smash", "drop", "lift", "cross_net"],
};

const ZONE_FOR: Record<Stroke, Zone[]> = {
  short_serve: ["front-centre", "front-left", "front-right"],
  long_serve: ["mid-centre", "front-centre"],
  smash: ["rear-centre", "rear-left", "rear-right", "mid-centre"],
  rush: ["front-centre", "front-left", "front-right"],
  drop: ["rear-centre", "rear-left", "rear-right"],
  clear: ["rear-centre", "rear-left", "rear-right", "mid-centre"],
  lift: ["front-left", "front-right", "mid-left", "mid-right", "front-centre"],
  drive: ["mid-left", "mid-right", "mid-centre"],
  push: ["front-centre", "mid-centre", "front-left", "front-right"],
  net_shot: ["front-left", "front-centre", "front-right"],
  cross_net: ["front-left", "front-right"],
  block: ["mid-left", "mid-right", "mid-centre", "front-centre"],
};

/** Where the shot puts the opponent — i.e. where they meet it. */
const SENDS_TO: Record<Stroke, Zone[]> = {
  short_serve: ["front-centre", "front-left", "front-right"],
  long_serve: ["rear-centre", "rear-left", "rear-right"],
  smash: ["mid-left", "mid-right", "mid-centre", "front-centre"],
  rush: ["front-centre", "mid-centre"],
  drop: ["front-left", "front-centre", "front-right"],
  clear: ["rear-left", "rear-centre", "rear-right"],
  lift: ["rear-left", "rear-centre", "rear-right"],
  drive: ["mid-left", "mid-right"],
  push: ["mid-centre", "front-centre", "mid-left", "mid-right"],
  net_shot: ["front-left", "front-centre", "front-right"],
  cross_net: ["front-left", "front-right"],
  block: ["front-centre", "mid-centre"],
};

const END_REASONS: Record<string, string> = {
  winner: "a clean winner",
  out: "the shuttle landed out",
  net: "the shuttle hit the net",
  unknown: "we couldn't tell",
};

interface Spec {
  id: string;
  title: string;
  date: string;
  venue: string;
  court: string;
  discipline: "singles" | "doubles";
  players: Player[];
  seed: number;
  /** Target games, e.g. [[21,17],[19,21],[21,18]] — the fold is generated to land on these. */
  games: [number, number][];
  coverageReason: string;
  /** Fraction of rallies the system could follow end to end. */
  followedRatio: number;
  durationMin: number;
}

function zoneOf(r: () => number, stroke: Stroke): Zone {
  return pick(r, ZONE_FOR[stroke]);
}

function emptyZones(): Record<Zone, number> {
  return Object.fromEntries(ZONES.map((z) => [z, 0])) as Record<Zone, number>;
}

/* ───────────────────────── the generator ───────────────────────── */

export function buildMatch(spec: Spec): Match {
  const r = rng(spec.seed);
  const sideOf = new Map(spec.players.map((p) => [p.id, p.side] as const));
  const bySide: Record<Side, PlayerId[]> = {
    A: spec.players.filter((p) => p.side === "A").map((p) => p.id),
    B: spec.players.filter((p) => p.side === "B").map((p) => p.id),
  };

  const rallies: Rally[] = [];
  let frame = 20 * FPS;
  let rallyNo = 0;
  let shotId = 0;

  // Warm-up rallies first: on the timeline, never in the score.
  for (let w = 0; w < 2; w += 1) {
    rallyNo += 1;
    rallies.push(makeRally(rallyNo, false, 1, { A: 0, B: 0 }, r.call(null) < 0.5 ? "A" : "B"));
  }

  // The real match: play each game until it reaches the target score.
  spec.games.forEach(([ta, tb], gi) => {
    const score = { A: 0, B: 0 };
    const targetWinner: Side = ta > tb ? "A" : "B";
    let guard = 0;
    while ((score.A < ta || score.B < tb) && guard < 90) {
      guard += 1;
      const aNeeds = ta - score.A;
      const bNeeds = tb - score.B;
      // Bias the winner so the game lands exactly on the target scoreline.
      const pA = aNeeds / Math.max(1, aNeeds + bNeeds);
      let winner: Side = r() < pA ? "A" : "B";
      if (score.A >= ta) winner = "B";
      if (score.B >= tb) winner = "A";
      rallyNo += 1;
      const server = winner === targetWinner || rallyNo % 2 === 0 ? winner : winner === "A" ? "B" : "A";
      const rally = makeRally(rallyNo, true, gi + 1, score, server, winner);
      score[winner] += 1;
      rally.scoreAfter = { ...score };
      rallies.push(rally);
    }
  });

  function makeRally(
    no: number,
    official: boolean,
    game: number,
    scoreBefore: { A: number; B: number },
    serveSide: Side,
    forcedWinner?: Side,
  ): Rally {
    // Amateur rally lengths cluster short with a long tail.
    const u = r();
    const nShots = Math.max(2, Math.round(2 + u * u * 20));
    const serverId = pick(r, bySide[serveSide]);
    const shots: Shot[] = [];
    let side: Side = serveSide;
    let prevFamily = "serve";
    let prevStroke: Stroke = r() < 0.75 ? "short_serve" : "long_serve";
    let hitter = serverId;
    const start = frame;

    for (let n = 1; n <= nShots; n += 1) {
      let stroke: Stroke;
      if (n === 1) {
        stroke = prevStroke;
      } else {
        const options = AFTER[prevFamily] ?? AFTER.neutral;
        stroke = pick(r, options as Stroke[]);
      }
      const from = zoneOf(r, stroke);
      const metAt = pick(r, SENDS_TO[stroke]);
      const isJump = stroke === "smash" && r() < 0.28;
      shotId += 1;
      shots.push({
        id: `s${shotId}`,
        frame: start + Math.round((n - 1) * (0.9 + r() * 0.7) * FPS),
        player: hitter,
        stroke,
        ...(isJump ? { subtype: "jump_smash" as const } : {}),
        from,
        metAt,
        n,
        decisive: n === nShots,
      });
      prevStroke = stroke;
      prevFamily = STROKE_FAMILY[stroke];
      side = side === "A" ? "B" : "A";
      // In doubles the pair splits front and rear, and who takes which rotates as the
      // serve changes hands — so both partners serve, receive and attack across a match.
      const candidates = bySide[side];
      if (candidates.length === 1) {
        hitter = candidates[0] as PlayerId;
      } else {
        const rear = (no + (side === "A" ? 0 : 1)) % 2;
        const wantsRear = prevFamily === "attack" || prevFamily === "defend";
        hitter = candidates[wantsRear ? rear : 1 - rear] as PlayerId;
      }
    }

    const last = shots[shots.length - 1] as Shot;
    const lastSide = sideOf.get(last.player) as Side;
    // The rally ends either with a winner from the last hitter or an error by them.
    const outcomeRoll = r();
    let outcome: Rally["outcome"];
    let winner: Side;
    if (forcedWinner) {
      winner = forcedWinner;
      outcome = lastSide === winner ? "winner" : outcomeRoll < 0.55 ? "out" : "net";
    } else {
      outcome = outcomeRoll < 0.42 ? "winner" : outcomeRoll < 0.78 ? "out" : "net";
      winner = outcome === "winner" ? lastSide : lastSide === "A" ? "B" : "A";
    }

    const durationS = Math.max(3, Math.round(nShots * 1.25 + r() * 3));
    const end = start + durationS * FPS;
    frame = end + Math.round((7 + r() * 13) * FPS);
    const tight =
      Math.min(scoreBefore.A, scoreBefore.B) >= 19 || Math.max(scoreBefore.A, scoreBefore.B) >= 20;

    return {
      no,
      frames: [start, end],
      durationS,
      shots,
      winner: official ? winner : null,
      lastHitter: last.player,
      outcome,
      endReason: END_REASONS[outcome] ?? "we couldn't tell",
      official,
      scoreAfter: { ...scoreBefore },
      game,
      server: serverId,
      pressure: official && tight,
    };
  }

  /* ── coverage: which rallies could be followed end to end ── */
  const followedCount = Math.round(rallies.length * spec.followedRatio);
  const order = rallies.map((_, i) => i).sort((a, b) => ((a * 7919) % 97) - ((b * 7919) % 97));
  const followed = new Set(order.slice(0, followedCount));

  /* ── derive per-player stats from the shots and rally outcomes ── */
  const stats: Record<PlayerId, PlayerStats> = {};
  for (const p of spec.players) {
    stats[p.id] = {
      pointsWon: 0,
      pointsLost: 0,
      winners: 0,
      errorsOut: 0,
      errorsNet: 0,
      strokes: {},
      smashes: 0,
      jumpSmashes: 0,
      smashPoints: 0,
      serves: 0,
      servePointsWon: 0,
      distanceM: 0,
      pointsWonUnderPressure: 0,
      steps: 0,
      activeS: 0,
      ralliesPlayed: 0,
      longestRally: 0,
      shotsPlayed: 0,
      returnsMade: 0,
      returnsAttempted: 0,
      defensiveSaves: 0,
      netShots: 0,
      repertoire: 0,
      familySplit: { attack: 0, neutral: 0, defend: 0, serve: 0 },
      originZones: emptyZones(),
      targetZones: emptyZones(),
    };
  }

  const movement = rng(spec.seed + 101);
  for (const rally of rallies) {
    if (!rally.official) continue;
    const touched = new Set(rally.shots.map((s) => s.player));
    for (const id of touched) {
      const st = stats[id] as PlayerStats;
      st.ralliesPlayed += 1;
      st.longestRally = Math.max(st.longestRally, rally.shots.length);
      st.activeS += rally.durationS;
      // Distance scales with rally length; ~0.78 m per step is a typical court stride.
      const metres = rally.shots.length * (1.5 + movement() * 1.6);
      st.distanceM += metres;
      st.steps += Math.round(metres / 0.78);
    }
    for (const s of rally.shots) {
      const st = stats[s.player] as PlayerStats;
      const key = s.subtype === "jump_smash" ? "jump_smash" : s.stroke;
      st.strokes[key] = (st.strokes[key] ?? 0) + 1;
      st.shotsPlayed += 1;
      st.familySplit[STROKE_FAMILY[s.stroke]] += 1;
      st.originZones[s.from] += 1;
      st.targetZones[s.metAt] += 1;
      if (s.stroke === "smash") st.smashes += 1;
      if (s.subtype === "jump_smash") st.jumpSmashes += 1;
      if (s.n === 1) st.serves += 1;
      if (s.stroke === "net_shot" || s.stroke === "cross_net" || s.stroke === "rush") st.netShots += 1;
      if (s.n > 1) {
        st.returnsAttempted += 1;
        if (!s.decisive || rally.outcome === "winner") st.returnsMade += 1;
      }
    }
    // Defensive save: a defend-family shot that the same player followed with another shot.
    for (let i = 0; i < rally.shots.length - 2; i += 1) {
      const s = rally.shots[i] as Shot;
      if (STROKE_FAMILY[s.stroke] !== "defend") continue;
      const next = rally.shots.slice(i + 1).find((x) => x.player === s.player);
      if (next) (stats[s.player] as PlayerStats).defensiveSaves += 1;
    }

    const w = rally.winner;
    if (!w) continue;
    for (const p of spec.players) {
      const st = stats[p.id] as PlayerStats;
      if (p.side === w) {
        st.pointsWon += 1;
        if (rally.pressure) st.pointsWonUnderPressure += 1;
        if (sideOf.get(rally.server) === w && rally.server === p.id) st.servePointsWon += 1;
      } else {
        st.pointsLost += 1;
      }
    }
    const last = rally.shots[rally.shots.length - 1] as Shot;
    const lastSt = stats[last.player] as PlayerStats;
    if (rally.outcome === "winner") {
      lastSt.winners += 1;
      if (last.stroke === "smash") lastSt.smashPoints += 1;
    } else if (rally.outcome === "out") lastSt.errorsOut += 1;
    else if (rally.outcome === "net") lastSt.errorsNet += 1;
  }
  for (const p of spec.players) {
    const st = stats[p.id] as PlayerStats;
    st.repertoire = Object.keys(st.strokes).filter((k) => k !== "jump_smash").length;
    st.distanceM = Math.round(st.distanceM);
  }

  /* ── score timeline and EWMA momentum (the engine's method) ── */
  const scoreTimeline: ScorePoint[] = [];
  const momentum: MomentumPoint[] = [];
  const momentumShifts: number[] = [];
  let ewma = 0;
  let run: { side: Side; length: number } = { side: "A", length: 0 };
  let prevLeader: Side | null = null;
  for (const rally of rallies) {
    if (!rally.official || !rally.winner) continue;
    scoreTimeline.push({
      rallyNo: rally.no,
      game: rally.game,
      score: rally.scoreAfter,
      winner: rally.winner,
      frame: rally.frames[0],
    });
    const v = rally.winner === "A" ? 1 : -1;
    ewma = ewma * 0.78 + v * 0.22;
    run =
      run.side === rally.winner
        ? { side: run.side, length: run.length + 1 }
        : { side: rally.winner, length: 1 };
    const leader: Side = ewma >= 0 ? "A" : "B";
    if (prevLeader && leader !== prevLeader) momentumShifts.push(rally.no);
    prevLeader = leader;
    momentum.push({ rallyNo: rally.no, value: Math.max(-1, Math.min(1, ewma * 2.2)), run });
  }

  /* ── heatmaps: expand the 3x3 zone counts onto a 14x7 floor grid ── */
  const heatmaps: Heatmap[] = [];
  const jitter = rng(spec.seed + 7);
  for (const p of spec.players) {
    for (const kind of ["presence", "movement", "origin", "landing", "targeting"] as HeatmapKind[]) {
      heatmaps.push(buildHeatmap(p, kind, stats[p.id] as PlayerStats, jitter));
    }
  }

  /* ── highlights: the engine's reason decomposition, then MMR for variety ── */
  const highlights = rankHighlights(rallies, spec, sideOf, followed);

  /* ── doubles: pair chemistry ── */
  let pairs: Record<Side, PairStats> | undefined;
  if (spec.discipline === "doubles") {
    pairs = { A: pairStats("A", bySide.A, rallies, sideOf), B: pairStats("B", bySide.B, rallies, sideOf) };
  }

  const activePlayS = rallies.filter((x) => x.official).reduce((a, x) => a + x.durationS, 0);

  return {
    id: spec.id,
    title: spec.title,
    date: spec.date,
    venue: spec.venue,
    court: spec.court,
    discipline: spec.discipline,
    status: "ready",
    players: spec.players,
    sides: {
      A: { label: bySide.A.map((id) => short(spec, id)).join(" & "), players: bySide.A },
      B: { label: bySide.B.map((id) => short(spec, id)).join(" & "), players: bySide.B },
    },
    games: spec.games,
    durationMin: spec.durationMin,
    activePlayS,
    rallies,
    highlights,
    stats,
    pairs,
    momentum,
    momentumShifts,
    scoreTimeline,
    heatmaps,
    coverage: {
      followed: followedCount,
      total: rallies.length,
      reason: spec.coverageReason,
    },
    fps: FPS,
    nFrames: frame + 10 * FPS,
  };
}

function short(spec: Spec, id: PlayerId) {
  return spec.players.find((p) => p.id === id)?.short ?? id;
}

/* ───────────────────────── heatmaps ───────────────────────── */

const ROWS = 14;
const COLS = 7;

/** Zone -> the block of grid cells it covers on a player's own half. */
function cellsFor(zone: Zone, near: boolean): [number, number][] {
  const [depth, width] = zone.split("-") as [string, string];
  const rowBand = depth === "front" ? 0 : depth === "mid" ? 1 : 2;
  // Near player owns rows 7-13 with front closest to the net (row 7).
  const rows = near
    ? [
        [7, 8],
        [9, 10],
        [11, 13],
      ][rowBand]
    : [
        [5, 6],
        [3, 4],
        [0, 2],
      ][rowBand];
  const cols = width === "left" ? [0, 1] : width === "centre" ? [2, 4] : [5, 6];
  const out: [number, number][] = [];
  for (let y = (rows as number[])[0] as number; y <= ((rows as number[])[1] as number); y += 1) {
    for (let x = (cols as number[])[0] as number; x <= ((cols as number[])[1] as number); x += 1) {
      out.push([y, x]);
    }
  }
  return out;
}

function buildHeatmap(p: Player, kind: HeatmapKind, st: PlayerStats, jit: () => number): Heatmap {
  const values = Array.from({ length: ROWS }, () => Array.from({ length: COLS }, () => 0));
  const near = p.end === "near";
  // `targeting` and `landing` describe the OPPONENT's half.
  const ownHalf = kind !== "targeting" && kind !== "landing";
  const source = kind === "targeting" || kind === "landing" ? st.targetZones : st.originZones;

  let total = 0;
  for (const zone of ZONES) {
    const base = source[zone];
    if (base === 0) continue;
    // Presence and movement spread wider than the shot origins they are built from.
    const spread = kind === "presence" || kind === "movement" ? 1.25 : 1;
    for (const [y, x] of cellsFor(zone, ownHalf ? near : !near)) {
      const v = base * spread * (0.6 + jit() * 0.8);
      (values[y] as number[])[x] = ((values[y] as number[])[x] as number) + v;
      total += v;
    }
  }
  // Movement is busiest in the middle — that is where a player returns to between shots.
  if (kind === "movement" || kind === "presence") {
    const midRow = near ? 10 : 4;
    for (let x = 0; x < COLS; x += 1) {
      const boost = (3 - Math.abs(x - 3)) * 1.4;
      (values[midRow] as number[])[x] = ((values[midRow] as number[])[x] as number) + boost;
      total += boost;
    }
  }
  const max = Math.max(1e-6, ...values.flat());
  return {
    player: p.id,
    kind,
    values: values.map((row) => row.map((v) => v / max)),
    total: Math.round(total),
  };
}

/* ───────────────────────── highlight ranking ───────────────────────── */

function rankHighlights(
  rallies: Rally[],
  spec: Spec,
  sideOf: Map<PlayerId, Side>,
  followed: Set<number>,
): Highlight[] {
  const longest = Math.max(...rallies.map((x) => x.shots.length));
  const candidates: Highlight[] = [];

  rallies.forEach((rally, idx) => {
    if (!rally.official || !followed.has(idx)) return;
    const reasons: Record<string, number> = {};
    const categories: HighlightCategory[] = [];
    const shots = rally.shots;

    // length
    const lengthScore = Math.min(3, (shots.length / longest) * 3);
    if (shots.length >= 8) {
      reasons.length = round1(lengthScore);
      if (shots.length === longest) categories.push("longest_rally");
      else if (shots.length >= 10) categories.push("rally_craft");
    }
    // smash / jump smash finishes
    const last = shots[shots.length - 1] as Shot;
    if (last.stroke === "smash" && rally.outcome === "winner") {
      reasons.smash_winner = 1.5;
      categories.push("smash_winner");
      if (last.subtype === "jump_smash") {
        reasons.jump_smash = 1.2;
        categories.push("jump_smash");
      }
    }
    // defence
    const defendRuns = new Map<PlayerId, number>();
    for (const s of shots) {
      if (STROKE_FAMILY[s.stroke] === "defend") defendRuns.set(s.player, (defendRuns.get(s.player) ?? 0) + 1);
    }
    const bestDefender = [...defendRuns.entries()].sort((a, b) => b[1] - a[1])[0];
    if (bestDefender && bestDefender[1] >= 4) {
      reasons.defence = Math.min(1.5, bestDefender[1] * 0.35);
      categories.push("best_defence");
    }
    // net battle
    let netRun = 0;
    let bestNetRun = 0;
    for (const s of shots) {
      if (s.stroke === "net_shot" || s.stroke === "cross_net" || s.stroke === "rush") netRun += 1;
      else netRun = 0;
      bestNetRun = Math.max(bestNetRun, netRun);
    }
    if (bestNetRun >= 3) {
      reasons.net_play = Math.min(1.2, bestNetRun * 0.35);
      categories.push("net_battle");
    }
    // variety
    const distinct = new Set(shots.map((s) => s.stroke)).size;
    if (distinct >= 5) reasons.variety = Math.min(1.5, distinct * 0.25);
    // pressure / deuce / game point
    if (rally.pressure) {
      reasons.pressure = 1.4;
      const hi = Math.max(rally.scoreAfter.A, rally.scoreAfter.B);
      const lo = Math.min(rally.scoreAfter.A, rally.scoreAfter.B);
      if (hi >= 20 && lo >= 20) categories.push("deuce");
      else if (hi >= 20) categories.push("game_point");
      else categories.push("clutch");
    }
    // doubles: both partners contributed
    if (spec.discipline === "doubles" && rally.winner) {
      const winnersShots = shots.filter((s) => sideOf.get(s.player) === rally.winner);
      if (new Set(winnersShots.map((s) => s.player)).size === 2 && shots.length >= 8) {
        reasons.partner_play = 1.1;
        categories.push("partner_play");
      }
    }

    const score = Math.min(10, Object.values(reasons).reduce((a, b) => a + b, 0) * 1.9);
    if (score < 1.2 || categories.length === 0) return;

    // Credit: the player whose play earned it, or both on a shared rally.
    let credits: PlayerId[];
    if (categories.includes("best_defence") && bestDefender) credits = [bestDefender[0]];
    else if (categories.includes("smash_winner")) credits = [last.player];
    else if (categories.includes("partner_play") && rally.winner) {
      credits = spec.players.filter((p) => p.side === rally.winner).map((p) => p.id);
    } else credits = [...new Set(shots.map((s) => s.player))];

    candidates.push({
      id: `h-${spec.id}-${rally.no}`,
      rallyNo: rally.no,
      frames: rally.frames,
      durationS: rally.durationS,
      score: round1(score),
      categories,
      reasons,
      credits,
      title: titleFor(categories, shots.length),
      why: whyFor(categories, shots.length, bestDefender?.[1] ?? 0, bestNetRun, distinct),
    });
  });

  // MMR: maximal marginal relevance over category sets, so the reel stays varied.
  candidates.sort((a, b) => b.score - a.score);
  const chosen: Highlight[] = [];
  const used = new Set<string>();
  while (chosen.length < 12 && candidates.length) {
    let bestIdx = 0;
    let best = -Infinity;
    candidates.forEach((c, i) => {
      const overlap = c.categories.some((x) => used.has(x)) ? 1 : 0;
      const mmr = 0.65 * (c.score / 10) - 0.35 * overlap;
      if (mmr > best) {
        best = mmr;
        bestIdx = i;
      }
    });
    const [taken] = candidates.splice(bestIdx, 1);
    if (!taken) break;
    for (const c of taken.categories) used.add(c);
    chosen.push(taken);
  }
  return chosen.sort((a, b) => b.score - a.score);
}

function round1(n: number) {
  return Math.round(n * 10) / 10;
}

function titleFor(cats: HighlightCategory[], shots: number): string {
  if (cats.includes("longest_rally")) return `The longest rally — ${shots} shots`;
  if (cats.includes("jump_smash")) return "A jump smash to finish";
  if (cats.includes("smash_winner")) return "Smash winner";
  if (cats.includes("best_defence")) return "A long defensive stand";
  if (cats.includes("net_battle")) return "A net battle";
  if (cats.includes("partner_play")) return "Both of you built this one";
  if (cats.includes("deuce")) return "A point at deuce";
  if (cats.includes("game_point")) return "Game point";
  if (cats.includes("clutch")) return "A point under pressure";
  return `A ${shots}-shot rally`;
}

function whyFor(
  cats: HighlightCategory[],
  shots: number,
  defence: number,
  netRun: number,
  distinct: number,
): string {
  const bits: string[] = [];
  if (shots >= 8) bits.push(`${shots} shots`);
  if (defence >= 4) bits.push(`${defence} shots played from under the shuttle`);
  if (netRun >= 3) bits.push(`${netRun} net shots in a row`);
  if (distinct >= 5) bits.push(`${distinct} different shots`);
  if (cats.includes("smash_winner")) bits.push("finished with a smash");
  if (cats.includes("partner_play")) bits.push("both partners hit in the build-up");
  if (cats.includes("deuce")) bits.push("played at deuce");
  return bits.length ? `Picked for: ${bits.join(", ")}.` : "Picked for the way the rally was built.";
}

/* ───────────────────────── pair chemistry ───────────────────────── */

function pairStats(side: Side, ids: PlayerId[], rallies: Rally[], sideOf: Map<PlayerId, Side>): PairStats {
  const [a, b] = ids as [PlayerId, PlayerId];
  const frontRear: Record<PlayerId, { front: number; rear: number }> = {
    [a]: { front: 0, rear: 0 },
    [b]: { front: 0, rear: 0 },
  };
  let bothContributed = 0;
  let rescues = 0;
  let attackCombos = 0;
  let longestSharedRally = 0;
  let pointsWon = 0;

  for (const rally of rallies) {
    if (!rally.official) continue;
    if (rally.winner === side) pointsWon += 1;
    const ours = rally.shots.filter((s) => sideOf.get(s.player) === side);
    if (ours.length === 0) continue;
    for (const s of ours) {
      const depth = s.from.split("-")[0];
      const slot = depth === "rear" ? "rear" : depth === "front" ? "front" : null;
      if (slot) (frontRear[s.player] as { front: number; rear: number })[slot] += 1;
    }
    const distinct = new Set(ours.map((s) => s.player));
    if (distinct.size === 2) {
      bothContributed += 1;
      longestSharedRally = Math.max(longestSharedRally, rally.shots.length);
    }
    // A rescue: one partner plays a defensive shot, the other plays the next shot for the side.
    for (let i = 0; i < ours.length - 1; i += 1) {
      const s = ours[i] as Shot;
      const next = ours[i + 1] as Shot;
      if (STROKE_FAMILY[s.stroke] === "defend" && next.player !== s.player) rescues += 1;
      // An attack combo: rear-court attack, then the partner intercepts at the net.
      if (
        STROKE_FAMILY[s.stroke] === "attack" &&
        s.from.startsWith("rear") &&
        next.player !== s.player &&
        next.from.startsWith("front")
      ) {
        attackCombos += 1;
      }
    }
  }

  return {
    side,
    players: [a, b],
    bothContributed,
    rescues,
    attackCombos,
    frontRear,
    longestSharedRally,
    pointsWon,
  };
}
