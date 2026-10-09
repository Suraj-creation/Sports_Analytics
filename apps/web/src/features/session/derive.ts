import type { EventLog } from "@/lib/events";
import type { BaiEvent, MatchState, PlayerId } from "@/lib/types";

export const INITIAL_STATE: MatchState = {
  game_no: 1,
  score: { P1: 0, P2: 0 },
  games_won: { P1: 0, P2: 0 },
  completed_games: [],
  server: "P1",
  receiver: "P2",
  service_court: "right",
  ends: { P1: "near", P2: "far" },
  rally_no: 0,
  winner: null,
  game_point: null,
  match_point: null,
  deuce: false,
  deciding_game: false,
};

/**
 * Match state as of `frame` — derived from the point events so the score bug never spoils
 * what hasn't happened yet on screen. Before the first point, the first point's
 * `state_before` carries the real opening server and ends.
 */
export function stateAt(events: EventLog, frame: number): { state: MatchState; known: boolean } {
  const last = events.latestBefore("point", frame);
  if (last?.payload.state_after) return { state: last.payload.state_after as MatchState, known: true };
  const first = events.ofType("point")[0];
  if (first?.payload.state_before) return { state: first.payload.state_before as MatchState, known: true };
  return { state: INITIAL_STATE, known: false };
}

export interface RallyView {
  end: BaiEvent; // the rally_end event (carries winner, outcome, shots)
  no: number;
  start: number;
  stop: number;
  winner: PlayerId | null;
}

export function rallies(events: EventLog): RallyView[] {
  return events.ofType("rally_end").map((e) => ({
    end: e,
    no: (e.payload.rally_no as number) ?? 0,
    start: e.frame_start,
    stop: e.frame_end,
    winner: (e.payload.winner as PlayerId | null) ?? null,
  }));
}

/** Rally containing `frame`, or the one in progress (rally_start without an end yet). */
export function currentRally(
  events: EventLog,
  frame: number,
): { start: number; end: BaiEvent | null } | null {
  const end = events.window(frame, frame, ["rally_end"])[0];
  if (end) return { start: end.frame_start, end };
  const start = events.latestBefore("rally_start", frame);
  if (!start) return null;
  const lastEnd = events.latestBefore("rally_end", frame);
  if (lastEnd && lastEnd.frame_end >= start.frame_start) return null; // between rallies
  return { start: start.frame_start, end: null };
}

export const isSmash = (e: BaiEvent) => e.type === "stroke" && e.payload.stroke === "smash";
export const isJumpSmash = (e: BaiEvent) => isSmash(e) && e.payload.subtype === "jump_smash";
