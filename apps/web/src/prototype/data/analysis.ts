/**
 * Derived tactical views.
 *
 * These come from the source blueprints in `Design/`, which warn about two specific
 * traps this file is built to avoid:
 *
 *   1. "Sequence view, not terminal-shot view" (Front-End Blueprint §7.9). Crediting only
 *      the last stroke misleads — one badminton study found net shots produced many positive
 *      perturbations even where smashes dominated direct winners. So we show what LED to the
 *      point, not only what finished it.
 *
 *   2. "Counts AND rates with opportunity denominators; frequency ≠ effectiveness"
 *      (Blueprint §7.10). A shot played 60 times and a shot played 4 times cannot be compared
 *      on raw counts, so every rate here carries its denominator.
 *
 * Everything is computed from the rallies and shots, so every figure can be opened in the
 * player and checked.
 */

import type { Match, PlayerId, Side, Stroke } from "./types";
import { STROKE_FAMILY, STROKE_LABEL } from "./types";

function sideOf(match: Match, id: PlayerId): Side {
  return match.players.find((p) => p.id === id)?.side ?? "A";
}

function counted(match: Match) {
  return match.rallies.filter((r) => r.official && r.winner);
}

/* ───────────────────────── shot effectiveness ─────────────────────────
   Frequency is not effectiveness. Each row carries what it was measured over. */

export interface ShotEffect {
  stroke: string;
  label: string;
  played: number;
  /** Rallies this player's side went on to win, among rallies where they played this shot. */
  ralliesWon: number;
  ralliesWith: number;
  /** Times this shot was the last of the rally and won it. */
  finishedWin: number;
  /** Times this shot was the last of the rally and lost it. */
  finishedLoss: number;
  /** Times it was played and the rally carried on. */
  continued: number;
  exampleFrame: number | null;
}

export function shotEffectiveness(match: Match, pid: PlayerId): ShotEffect[] {
  const mySide = sideOf(match, pid);
  const rows = new Map<string, ShotEffect>();
  const ralliesByStroke = new Map<string, Set<number>>();
  const wonByStroke = new Map<string, Set<number>>();

  for (const rally of counted(match)) {
    const won = rally.winner === mySide;
    for (const s of rally.shots) {
      if (s.player !== pid) continue;
      const key = s.subtype ?? s.stroke;
      const row =
        rows.get(key) ??
        ({
          stroke: key,
          label: STROKE_LABEL[key] ?? key,
          played: 0,
          ralliesWon: 0,
          ralliesWith: 0,
          finishedWin: 0,
          finishedLoss: 0,
          continued: 0,
          exampleFrame: null,
        } satisfies ShotEffect);
      row.played += 1;
      if (row.exampleFrame === null) row.exampleFrame = Math.max(0, s.frame - match.fps);
      if (s.decisive) {
        if (rally.outcome === "winner") row.finishedWin += 1;
        else row.finishedLoss += 1;
      } else {
        row.continued += 1;
      }
      rows.set(key, row);

      const seen = ralliesByStroke.get(key) ?? new Set<number>();
      seen.add(rally.no);
      ralliesByStroke.set(key, seen);
      if (won) {
        const w = wonByStroke.get(key) ?? new Set<number>();
        w.add(rally.no);
        wonByStroke.set(key, w);
      }
    }
  }

  for (const [key, row] of rows) {
    row.ralliesWith = ralliesByStroke.get(key)?.size ?? 0;
    row.ralliesWon = wonByStroke.get(key)?.size ?? 0;
  }
  return [...rows.values()].sort((a, b) => b.played - a.played);
}

/* ───────────────────────── build-up, not just the ending ─────────────────────────
   The two shots before the rally ended, for points won and points lost. */

export interface Sequence {
  key: string;
  label: string;
  n: number;
  exampleFrame: number;
}

export function buildUp(
  match: Match,
  pid: PlayerId,
): { won: Sequence[]; lost: Sequence[]; sampleWon: number; sampleLost: number } {
  const mySide = sideOf(match, pid);
  const won = new Map<string, Sequence>();
  const lost = new Map<string, Sequence>();
  let sampleWon = 0;
  let sampleLost = 0;

  for (const rally of counted(match)) {
    const shots = rally.shots;
    if (shots.length < 3) continue;
    const a = shots[shots.length - 3];
    const b = shots[shots.length - 2];
    const c = shots[shots.length - 1];
    if (!a || !b || !c) continue;
    // Only rallies this player was actually involved in at the end.
    if (a.player !== pid && b.player !== pid && c.player !== pid) continue;

    const key = `${a.stroke}>${b.stroke}>${c.stroke}`;
    const label = `${STROKE_LABEL[a.stroke]} → ${STROKE_LABEL[b.stroke]} → ${STROKE_LABEL[c.stroke]}`;
    const bucket = rally.winner === mySide ? won : lost;
    if (rally.winner === mySide) sampleWon += 1;
    else sampleLost += 1;
    const row = bucket.get(key) ?? { key, label, n: 0, exampleFrame: Math.max(0, a.frame - match.fps) };
    row.n += 1;
    bucket.set(key, row);
  }

  const top = (m: Map<string, Sequence>) => [...m.values()].sort((x, y) => y.n - x.n).slice(0, 6);
  return { won: top(won), lost: top(lost), sampleWon, sampleLost };
}

/* ───────────────────────── serve and receive ───────────────────────── */

export interface ServeRow {
  stroke: string;
  label: string;
  served: number;
  won: number;
  exampleFrame: number | null;
}

export interface ReceiveRow {
  /** What the opponent served. */
  against: string;
  againstLabel: string;
  /** What this player did with it. */
  replies: { stroke: string; label: string; n: number }[];
  received: number;
  won: number;
  exampleFrame: number | null;
}

export function serveAndReceive(
  match: Match,
  pid: PlayerId,
): { serving: ServeRow[]; receiving: ReceiveRow[] } {
  const mySide = sideOf(match, pid);
  const serving = new Map<string, ServeRow>();
  const receiving = new Map<string, ReceiveRow>();

  for (const rally of counted(match)) {
    const first = rally.shots[0];
    const reply = rally.shots[1];
    if (!first) continue;
    const won = rally.winner === mySide;

    if (first.player === pid) {
      const key = first.stroke;
      const row =
        serving.get(key) ??
        ({
          stroke: key,
          label: STROKE_LABEL[key] ?? key,
          served: 0,
          won: 0,
          exampleFrame: Math.max(0, first.frame - match.fps),
        } satisfies ServeRow);
      row.served += 1;
      if (won) row.won += 1;
      serving.set(key, row);
    } else if (reply?.player === pid) {
      const key = first.stroke;
      const row =
        receiving.get(key) ??
        ({
          against: key,
          againstLabel: STROKE_LABEL[key] ?? key,
          replies: [],
          received: 0,
          won: 0,
          exampleFrame: Math.max(0, reply.frame - match.fps),
        } satisfies ReceiveRow);
      row.received += 1;
      if (won) row.won += 1;
      const existing = row.replies.find((x) => x.stroke === reply.stroke);
      if (existing) existing.n += 1;
      else
        row.replies.push({
          stroke: reply.stroke,
          label: STROKE_LABEL[reply.stroke] ?? reply.stroke,
          n: 1,
        });
      receiving.set(key, row);
    }
  }

  for (const r of receiving.values()) r.replies.sort((a, b) => b.n - a.n);
  return {
    serving: [...serving.values()].sort((a, b) => b.served - a.served),
    receiving: [...receiving.values()].sort((a, b) => b.received - a.received),
  };
}

/* ───────────────────────── attack / defence transitions ───────────────────────── */

export interface Transitions {
  /** Rallies where the player went from a defending shot to an attacking one. */
  defenceToAttack: number;
  /** ...and then went on to win the rally. */
  defenceToAttackWon: number;
  /** Rallies where they were attacking and ended up defending. */
  attackToDefence: number;
  attackToDefenceWon: number;
  examples: { label: string; frame: number }[];
  sample: number;
}

export function transitions(match: Match, pid: PlayerId): Transitions {
  const mySide = sideOf(match, pid);
  const out: Transitions = {
    defenceToAttack: 0,
    defenceToAttackWon: 0,
    attackToDefence: 0,
    attackToDefenceWon: 0,
    examples: [],
    sample: 0,
  };

  for (const rally of counted(match)) {
    const mine = rally.shots.filter((s) => s.player === pid);
    if (mine.length < 2) continue;
    out.sample += 1;
    const won = rally.winner === mySide;
    let sawDefence = false;
    let sawAttackAfterDefence = false;
    let sawAttack = false;
    let sawDefenceAfterAttack = false;
    for (const s of mine) {
      const fam = STROKE_FAMILY[s.stroke as Stroke];
      if (fam === "defend") {
        sawDefence = true;
        if (sawAttack) sawDefenceAfterAttack = true;
      }
      if (fam === "attack") {
        sawAttack = true;
        if (sawDefence) sawAttackAfterDefence = true;
      }
    }
    if (sawAttackAfterDefence) {
      out.defenceToAttack += 1;
      if (won) out.defenceToAttackWon += 1;
      if (out.examples.length < 4) {
        out.examples.push({
          label: `Rally ${rally.no} — turned defence into attack`,
          frame: rally.frames[0],
        });
      }
    }
    if (sawDefenceAfterAttack) {
      out.attackToDefence += 1;
      if (won) out.attackToDefenceWon += 1;
    }
  }
  return out;
}

/* ───────────────────────── score state ─────────────────────────
   Blueprint §7.9 asks for score-state filtering: a rally at 19-19 is not the
   same rally as one at 11-4, and lumping them hides the thing people care about. */

export type ScoreState = "level" | "ahead" | "behind" | "tight";

export function scoreStateOf(match: Match, rallyNo: number, pid: PlayerId): ScoreState {
  const mySide = sideOf(match, pid);
  const idx = match.rallies.findIndex((r) => r.no === rallyNo);
  const prev = match.rallies
    .slice(0, Math.max(0, idx))
    .filter((r) => r.official)
    .pop();
  const before = prev?.scoreAfter ?? { A: 0, B: 0 };
  const mine = mySide === "A" ? before.A : before.B;
  const theirs = mySide === "A" ? before.B : before.A;
  if (Math.min(mine, theirs) >= 19) return "tight";
  if (mine === theirs) return "level";
  return mine > theirs ? "ahead" : "behind";
}

export const SCORE_STATE_LABEL: Record<ScoreState, string> = {
  level: "Level",
  ahead: "Ahead",
  behind: "Behind",
  tight: "19-all or beyond",
};

/** Doubles role at the moment of a shot: front or rear court. */
export function roleAt(zone: string): "front" | "rear" | "mid" {
  const depth = zone.split("-")[0];
  return depth === "front" ? "front" : depth === "rear" ? "rear" : "mid";
}

/* ───────────────────────── counterexamples ─────────────────────────
   Blueprint §7.13: "Include counterexamples in analytical reports to avoid highlight bias."
   The moments reel is selected for being good. This finds the rallies that went the
   other way, so the picture is not only the flattering half. */

export function counterexamples(match: Match, pid: PlayerId, n = 4) {
  const mySide = sideOf(match, pid);
  return counted(match)
    .filter((r) => r.winner !== mySide && r.shots.length >= 6)
    .filter((r) => r.shots[r.shots.length - 1]?.player === pid)
    .sort((a, b) => b.shots.length - a.shots.length)
    .slice(0, n)
    .map((r) => ({
      rallyNo: r.no,
      frame: r.frames[0],
      shots: r.shots.length,
      reason: `${r.shots.length} shots, ended because ${r.endReason}`,
    }));
}
