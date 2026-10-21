import type { BaiEvent, MatchState, PlayerId, Session } from "@/lib/types";

let seq = 0;

export function ev(type: string, frame: number, over: Partial<BaiEvent> = {}): BaiEvent {
  seq += 1;
  return {
    event_id: over.event_id ?? `${type}-${frame}-${seq}`,
    session_id: "s1",
    type,
    frame_start: frame,
    frame_end: over.frame_end ?? frame,
    pts_us: Math.round((frame / 30) * 1e6),
    actors: { player_id: null, track_id: null, opponent_id: null, ...(over.actors ?? {}) },
    payload: over.payload ?? {},
    confidence: over.confidence ?? 0.9,
    band: over.band ?? "confirmed",
    status: over.status ?? "confirmed",
    evidence: [],
    provenance: { model: "test" },
    supersedes: over.supersedes ?? null,
    parent_id: over.parent_id ?? null,
    seq: over.seq ?? seq,
  };
}

export function state(p1: number, p2: number, over: Partial<MatchState> = {}): MatchState {
  return {
    game_no: 1,
    score: { P1: p1, P2: p2 },
    games_won: { P1: 0, P2: 0 },
    completed_games: [],
    server: "P1",
    receiver: "P2",
    service_court: (p1 + p2) % 2 ? "left" : "right",
    ends: { P1: "near", P2: "far" },
    rally_no: p1 + p2,
    winner: null,
    game_point: null,
    match_point: null,
    deuce: false,
    deciding_game: false,
    ...over,
  };
}

/** A point event at `frame` won by `winner`, taking the score from `before` to `after`. */
export function point(frame: number, winner: PlayerId, before: MatchState, after: MatchState): BaiEvent {
  return ev("point", frame, {
    actors: { player_id: winner, track_id: null, opponent_id: winner === "P1" ? "P2" : "P1" },
    payload: { winner, state_before: before, state_after: after },
  });
}

export const SESSION: Session = {
  session_id: "s1",
  title: "Final",
  sport: "badminton",
  source: { kind: "upload", uri: "x", original_name: "final.mp4", sha256: "abc" },
  media: {
    fps_num: 30,
    fps_den: 1,
    n_frames: 9000,
    width: 1280,
    height: 720,
    duration_us: 300e6,
    has_audio: true,
  },
  players: [
    { player_id: "P1", name: "Viktor Axelsen" },
    { player_id: "P2", name: "Kento Momota" },
  ],
  profile: "cpu-dev",
  status: "analysing",
  status_detail: null,
  frontier_frame: 6000,
  analysed_frames: 6001,
  created_at: "2026-10-01T10:00:00Z",
  meta: {},
};
