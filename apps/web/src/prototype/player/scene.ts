/**
 * The scene at a frame.
 *
 * There is no footage in this prototype, so the stage renders the match from the rally and
 * shot data instead: every player's position, the shuttle, the trail and the score are
 * computed for the exact frame the playhead is on. It is a reconstruction, labelled as one —
 * but it is driven by the same events the overlays would be drawn from over real video,
 * so every control and every overlay behaves the way it would on the real player.
 */

import type { Match, PlayerId, Rally, Shot, Side, Zone } from "../data/types";

export interface Mark {
  id: PlayerId;
  /** 0..1 across the court (0 = left from the near baseline), 0..1 along it (0 = far, 1 = near). */
  x: number;
  y: number;
  near: boolean;
}

export interface Scene {
  rally: Rally | null;
  /** Index of the shot that has just been played, -1 before the first. */
  shotIndex: number;
  marks: Mark[];
  shuttle: { x: number; y: number; height: number } | null;
  trail: { x: number; y: number }[];
  score: { A: number; B: number; game: number };
  /** True while the shuttle is dead between rallies. */
  between: boolean;
  lastShot: Shot | null;
}

const DEPTH: Record<string, number> = { front: 0.335, mid: 0.21, rear: 0.075 };
const WIDTH: Record<string, number> = { left: 0.26, centre: 0.5, right: 0.74 };

/** Zone to a point on the floor, for a player at the near or far end. */
export function zonePos(zone: Zone, near: boolean): { x: number; y: number } {
  const [depth, width] = zone.split("-") as [string, string];
  const d = DEPTH[depth] ?? 0.21;
  return { x: WIDTH[width] ?? 0.5, y: near ? 1 - d : d };
}

/** Where a player waits between shots — just behind the middle of their half. */
function basePos(near: boolean): { x: number; y: number } {
  return { x: 0.5, y: near ? 0.72 : 0.28 };
}

function lerp(a: number, b: number, t: number) {
  return a + (b - a) * t;
}

function ease(t: number) {
  return t < 0.5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2;
}

export function sceneAt(match: Match, frame: number): Scene {
  const nearIds = new Set(match.players.filter((p) => p.end === "near").map((p) => p.id));
  const rally = match.rallies.find((r) => frame >= r.frames[0] && frame <= r.frames[1]) ?? null;

  // Score shown is the score as of the last completed rally — never ahead of the picture.
  let score = { A: 0, B: 0 };
  let game = 1;
  for (const r of match.rallies) {
    if (!r.official || r.frames[1] > frame) continue;
    score = r.scoreAfter;
    game = r.game;
  }

  if (!rally) {
    return {
      rally: null,
      shotIndex: -1,
      marks: match.players.map((p) => {
        const near = nearIds.has(p.id);
        const b = basePos(near);
        // Doubles partners stand apart while waiting.
        const offset = match.discipline === "doubles" ? (p.id < (p.partnerId ?? "") ? -0.14 : 0.14) : 0;
        return { id: p.id, x: b.x + offset, y: b.y, near };
      }),
      shuttle: null,
      trail: [],
      score: { ...score, game },
      between: true,
      lastShot: null,
    };
  }

  const shots = rally.shots;
  let shotIndex = -1;
  for (let i = 0; i < shots.length; i += 1) {
    if ((shots[i] as Shot).frame <= frame) shotIndex = i;
  }
  const current = shots[Math.max(0, shotIndex)] as Shot;
  const next = shots[shotIndex + 1];
  const span = next ? next.frame - current.frame : 24;
  const t = next ? Math.max(0, Math.min(1, (frame - current.frame) / Math.max(1, span))) : 1;

  // Each player moves toward where their next shot will be played from.
  const marks: Mark[] = match.players.map((p) => {
    const near = nearIds.has(p.id);
    const prevShot = [...shots.slice(0, shotIndex + 1)].reverse().find((s) => s.player === p.id);
    const nextShot = shots.slice(shotIndex + 1).find((s) => s.player === p.id);
    const from = prevShot ? zonePos(prevShot.from, near) : basePos(near);
    const to = nextShot ? zonePos(nextShot.from, near) : basePos(near);
    const k = ease(t);
    return { id: p.id, x: lerp(from.x, to.x, k), y: lerp(from.y, to.y, k), near };
  });

  // The shuttle flies from the hitter to wherever the receiver meets it.
  const hitterNear = nearIds.has(current.player);
  const origin = zonePos(current.from, hitterNear);
  const target = zonePos(current.metAt, !hitterNear);
  const shuttle = {
    x: lerp(origin.x, target.x, t),
    y: lerp(origin.y, target.y, t),
    height: Math.sin(t * Math.PI) * (current.stroke === "smash" ? 0.25 : 1),
  };

  // A short trail of where the shuttle has just been.
  const trail: { x: number; y: number }[] = [];
  for (let k = 1; k <= 7; k += 1) {
    const tt = Math.max(0, t - k * 0.06);
    trail.push({ x: lerp(origin.x, target.x, tt), y: lerp(origin.y, target.y, tt) });
  }

  return {
    rally,
    shotIndex,
    marks,
    shuttle,
    trail,
    score: { ...score, game },
    between: false,
    lastShot: current,
  };
}

/** Side a player belongs to, for the score bug. */
export function sideOf(match: Match, id: PlayerId): Side {
  return match.players.find((p) => p.id === id)?.side ?? "A";
}
