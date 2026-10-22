/**
 * Prototype domain model.
 *
 * Mirrors what the engine actually produces today (see apps/web/src/lib/types.ts and the
 * Stats / Heatmaps / Highlights / Rallies tabs), generalised from the engine's two-track
 * `PlayerId` to any number of players so doubles is a first-class discipline rather than
 * a thing bolted on later.
 */

export type PlayerId = string;
export type Side = "A" | "B";
export type Discipline = "singles" | "doubles";

/** The 12 strokes in the engine ontology, plus the jump-smash subtype. */
export type Stroke =
  | "short_serve"
  | "long_serve"
  | "smash"
  | "drop"
  | "clear"
  | "lift"
  | "drive"
  | "push"
  | "rush"
  | "net_shot"
  | "cross_net"
  | "block";

export const STROKES: Stroke[] = [
  "short_serve",
  "long_serve",
  "smash",
  "drop",
  "clear",
  "lift",
  "drive",
  "push",
  "rush",
  "net_shot",
  "cross_net",
  "block",
];

export const STROKE_LABEL: Record<string, string> = {
  short_serve: "Short serve",
  long_serve: "Long serve",
  smash: "Smash",
  drop: "Drop",
  clear: "Clear",
  lift: "Lift",
  drive: "Drive",
  push: "Push",
  rush: "Net kill",
  net_shot: "Net shot",
  cross_net: "Cross-court net",
  block: "Block",
  jump_smash: "Jump smash",
  unknown: "Shot",
};

/** Which family a stroke belongs to — drives the attack / neutral / defend split. */
export const STROKE_FAMILY: Record<Stroke, "attack" | "neutral" | "defend" | "serve"> = {
  short_serve: "serve",
  long_serve: "serve",
  smash: "attack",
  rush: "attack",
  drop: "attack",
  cross_net: "neutral",
  net_shot: "neutral",
  drive: "neutral",
  push: "neutral",
  clear: "defend",
  lift: "defend",
  block: "defend",
};

/** 3 depth x 3 width per half, the engine's `court_zones` ontology. */
export type Zone =
  | "front-left"
  | "front-centre"
  | "front-right"
  | "mid-left"
  | "mid-centre"
  | "mid-right"
  | "rear-left"
  | "rear-centre"
  | "rear-right";

export const ZONES: Zone[] = [
  "front-left",
  "front-centre",
  "front-right",
  "mid-left",
  "mid-centre",
  "mid-right",
  "rear-left",
  "rear-centre",
  "rear-right",
];

export interface Player {
  id: PlayerId;
  name: string;
  short: string;
  side: Side;
  /** Near the camera at the start of the match. */
  end: "near" | "far";
  isYou: boolean;
  /** Doubles only: who they played with. */
  partnerId?: PlayerId;
  colour: "you" | "partner" | "opponent-1" | "opponent-2";
}

export interface Shot {
  id: string;
  frame: number;
  player: PlayerId;
  stroke: Stroke;
  subtype?: "jump_smash";
  /** Where the hitter was standing. */
  from: Zone;
  /** Where the receiver met it — NOT where the shuttle landed (the engine has no flight model). */
  metAt: Zone;
  /** Shot index within the rally, 1-based. */
  n: number;
  /** Whether this shot ended the rally. */
  decisive: boolean;
}

export interface Rally {
  no: number;
  frames: [number, number];
  durationS: number;
  shots: Shot[];
  winner: Side | null;
  /** Who played the last shot. */
  lastHitter: PlayerId;
  outcome: "winner" | "out" | "net" | "unknown";
  endReason: string;
  /** false = warm-up / replay: on the timeline, not in the score. */
  official: boolean;
  /** Score after this rally, by side. */
  scoreAfter: { A: number; B: number };
  game: number;
  server: PlayerId;
  /** True when this rally was played at 20-all or beyond, or at game/match point. */
  pressure: boolean;
}

export interface PlayerStats {
  // ── exactly the engine's PlayerStats ──
  pointsWon: number;
  pointsLost: number;
  winners: number;
  errorsOut: number;
  errorsNet: number;
  strokes: Record<string, number>;
  smashes: number;
  jumpSmashes: number;
  smashPoints: number;
  serves: number;
  servePointsWon: number;
  distanceM: number;
  pointsWonUnderPressure: number;
  // ── derived for the recreational layer ──
  steps: number;
  activeS: number;
  ralliesPlayed: number;
  longestRally: number;
  shotsPlayed: number;
  /** Shots that kept the rally alive (did not end it as an error). */
  returnsMade: number;
  returnsAttempted: number;
  /** Defensive-family shots followed by at least one more shot from the same player. */
  defensiveSaves: number;
  netShots: number;
  /** Distinct stroke types observed. */
  repertoire: number;
  /** Share of this player's shots by family. */
  familySplit: { attack: number; neutral: number; defend: number; serve: number };
  /** Where this player hit from, by zone. */
  originZones: Record<Zone, number>;
  /** Where the opponent met this player's shots, by zone. */
  targetZones: Record<Zone, number>;
}

export type HeatmapKind = "presence" | "movement" | "origin" | "landing" | "targeting";

export const HEATMAP_KINDS: { id: HeatmapKind; label: string; hint: string; preview?: boolean }[] = [
  {
    id: "presence",
    label: "Where they stand",
    hint: "Time spent in each part of their half while the shuttle was in play.",
  },
  {
    id: "movement",
    label: "Movement",
    hint: "Distance covered, by area — the busier the floor, the more ground covered there.",
  },
  { id: "origin", label: "Where they hit from", hint: "Their position at the moment of each shot." },
  {
    id: "landing",
    label: "Where their shots go",
    hint: "Where the opponent met the shuttle. This is the receiver's position, not the landing point.",
    preview: true,
  },
  {
    id: "targeting",
    label: "Targeting",
    hint: "Which areas of the opponent's half this player attacks most.",
  },
];

export interface Heatmap {
  player: PlayerId;
  kind: HeatmapKind;
  /** rows (along the court) x cols (across it), normalised 0-1. */
  values: number[][];
  total: number;
}

export type HighlightCategory =
  | "longest_rally"
  | "smash_winner"
  | "jump_smash"
  | "best_defence"
  | "net_battle"
  | "comeback"
  | "momentum_shift"
  | "deuce"
  | "game_point"
  | "match_point"
  | "clutch"
  | "partner_play"
  | "rally_craft";

export const CATEGORY_LABEL: Record<HighlightCategory, string> = {
  longest_rally: "Longest rally",
  smash_winner: "Smash winner",
  jump_smash: "Jump smash",
  best_defence: "Best defence",
  net_battle: "Net battle",
  comeback: "Comeback",
  momentum_shift: "Momentum shift",
  deuce: "Deuce",
  game_point: "Game point",
  match_point: "Match point",
  clutch: "Clutch point",
  partner_play: "Partner play",
  rally_craft: "Rally craft",
};

export interface Highlight {
  id: string;
  rallyNo: number;
  frames: [number, number];
  durationS: number;
  /** The engine's 0-10 excitement score. Shown only in the analyst view. */
  score: number;
  categories: HighlightCategory[];
  /** The reasons decomposition the ranker produced. */
  reasons: Record<string, number>;
  /** Who it credits. Doubles moments can credit two. */
  credits: PlayerId[];
  title: string;
  why: string;
}

export interface MomentumPoint {
  rallyNo: number;
  /** -1 (side B fully ahead) .. +1 (side A fully ahead) */
  value: number;
  run: { side: Side; length: number };
}

export interface ScorePoint {
  rallyNo: number;
  game: number;
  score: { A: number; B: number };
  winner: Side;
  frame: number;
}

/** Doubles only: how a pair worked together. */
export interface PairStats {
  side: Side;
  players: [PlayerId, PlayerId];
  /** Rallies in which both partners hit at least once. */
  bothContributed: number;
  /** Rally won immediately after a partner's defensive shot. */
  rescues: number;
  /** Rear-court attack followed by a front-court interception by the partner. */
  attackCombos: number;
  /** Shot share front vs rear, per player. */
  frontRear: Record<PlayerId, { front: number; rear: number }>;
  longestSharedRally: number;
  pointsWon: number;
}

export interface Match {
  id: string;
  title: string;
  date: string;
  venue: string;
  court: string;
  discipline: Discipline;
  status: "ready" | "analysing" | "failed";
  progress?: number;
  players: Player[];
  sides: Record<Side, { label: string; players: PlayerId[] }>;
  /** Games won by each side, e.g. [[21,17],[19,21],[21,15]] */
  games: [number, number][];
  durationMin: number;
  /** Time the shuttle was actually in play. */
  activePlayS: number;
  rallies: Rally[];
  highlights: Highlight[];
  stats: Record<PlayerId, PlayerStats>;
  pairs?: Record<Side, PairStats>;
  momentum: MomentumPoint[];
  momentumShifts: number[];
  scoreTimeline: ScorePoint[];
  heatmaps: Heatmap[];
  /** How much of the match the system could follow. */
  coverage: { followed: number; total: number; reason: string };
  fps: number;
  nFrames: number;
}

/** A deterministic, evidence-linked sentence written under a chart. */
export interface Insight {
  text: string;
  /** Jump the player here to see it. */
  frame?: number;
  tone: "neutral" | "strength" | "watch";
}
