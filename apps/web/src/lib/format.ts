import type { MediaInfo, PlayerId, Session } from "./types";

export const fps = (m: MediaInfo | null | undefined) => (m ? m.fps_num / m.fps_den : 30);

/** Display clock for a frame — the only place frames become human time in the UI. */
export function clock(frame: number, m: MediaInfo | null | undefined, millis = false): string {
  const t = Math.max(0, frame) / fps(m);
  const h = Math.floor(t / 3600);
  const mm = Math.floor((t % 3600) / 60);
  const ss = Math.floor(t % 60);
  const base = h
    ? `${h}:${String(mm).padStart(2, "0")}:${String(ss).padStart(2, "0")}`
    : `${mm}:${String(ss).padStart(2, "0")}`;
  return millis ? `${base}.${String(Math.floor((t % 1) * 1000)).padStart(3, "0")}` : base;
}

export function playerName(s: Session | null | undefined, pid: PlayerId | null | undefined): string {
  if (!pid) return "—";
  const p = s?.players.find((x) => x.player_id === pid);
  return p?.name || (pid === "P1" ? "Player 1" : "Player 2");
}

export function shortName(s: Session | null | undefined, pid: PlayerId | null | undefined): string {
  const n = playerName(s, pid);
  const parts = n.split(/\s+/);
  return parts.length > 1 ? (parts[parts.length - 1] as string) : n;
}

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
  cross_net: "Cross-court net shot",
  block: "Block",
  unknown: "Shot",
  jump_smash: "Jump smash",
};

export const OUTCOME_LABEL: Record<string, string> = {
  out: "landed out",
  net: "into the net",
  winner: "landed in",
  unknown: "outcome unclear",
};

export const CATEGORY_LABEL: Record<string, string> = {
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
};

export const STATUS_LABEL: Record<string, string> = {
  created: "Queued",
  ingesting: "Preparing video",
  ready_to_play: "Ready to play",
  analysing: "Analysing",
  analysed: "Analysed",
  failed: "Failed",
};

export const pct = (v: number | null | undefined) => (v == null ? "—" : `${Math.round(v * 100)}%`);

export function strokeLabel(payload: Record<string, any>): string {
  return STROKE_LABEL[payload.subtype ?? ""] ?? STROKE_LABEL[payload.stroke ?? "unknown"] ?? "Shot";
}

export function playerColor(pid: PlayerId | null | undefined): string {
  return pid === "P1" ? "var(--color-p1)" : pid === "P2" ? "var(--color-p2)" : "var(--color-line-2)";
}

/** Canvas needs literal colours (CSS variables don't resolve there). Mirrors styles.css. */
export const PLAYER_HEX: Record<PlayerId, string> = { P1: "#4290e0", P2: "#e2701f" };

export function otherPlayer(pid: PlayerId): PlayerId {
  return pid === "P1" ? "P2" : "P1";
}
