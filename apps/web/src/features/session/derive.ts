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
 * Match state as of `frame`, using accepted score evidence in the effective log.
 * A seed has an explicit frame; otherwise the first accepted point's `state_before`
 * supplies the opening state for older logs that do not contain a seed event.
 */
export function stateAt(
  events: EventLog,
  frame: number,
): { state: MatchState; known: boolean; evidence?: BaiEvent } {
  const accepted = events
    .ofType("point", "match_phase")
    .filter(
      (event) =>
        (event.status === "confirmed" || event.status === "corrected" || event.status === "human_verified") &&
        event.payload.state_after &&
        (event.type === "point" || event.payload.base_state),
    );
  const last = accepted.filter((event) => event.frame_start <= frame).at(-1);
  if (last) return { state: last.payload.state_after as MatchState, known: true, evidence: last };
  // The seed constrains when this opening state is known. A future point's
  // state_before must not move that observation earlier in the recording.
  if (accepted.some((event) => event.type === "match_phase")) return { state: INITIAL_STATE, known: false };
  const first = accepted[0];
  if (first?.payload.state_before) return { state: first.payload.state_before as MatchState, known: true };
  return { state: INITIAL_STATE, known: false };
}

export interface RallyView {
  end: BaiEvent; // the rally_end event (carries winner, outcome, shots)
  no: number;
  start: number;
  stop: number;
  winner: PlayerId | null;
  /** false: warm-up / practice / replayed exchange — on the timeline, not in the score */
  official: boolean;
}

export function rallies(events: EventLog): RallyView[] {
  return events.ofType("rally_end").map((e) => ({
    end: e,
    no: (e.payload.rally_no as number) ?? 0,
    start: e.frame_start,
    stop: e.frame_end,
    winner: (e.payload.winner as PlayerId | null) ?? null,
    official: e.payload.official !== false,
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
