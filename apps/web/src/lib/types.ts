// Mirrors the backend pydantic contracts (engine/src/bai_engine/schema). Keep in sync with
// GET /api/openapi.json; frames are the canonical time unit everywhere.

export type PlayerId = "P1" | "P2";
export type SessionStatus = "created" | "ingesting" | "ready_to_play" | "analysing" | "analysed" | "failed";
export type Band = "confirmed" | "probable" | "uncertain" | "unknown";
export type EventStatus = "provisional" | "confirmed" | "corrected" | "retracted" | "human_verified";

export interface MediaInfo {
  fps_num: number;
  fps_den: number;
  n_frames: number;
  width: number;
  height: number;
  duration_us: number;
  has_audio: boolean;
}

export interface PlayerInfo {
  player_id: PlayerId;
  name: string | null;
}

export interface Session {
  session_id: string;
  title: string;
  sport: string;
  source: {
    kind: "upload" | "youtube" | string;
    uri: string;
    original_name: string | null;
    sha256: string | null;
  };
  media: MediaInfo | null;
  players: PlayerInfo[];
  profile: string;
  status: SessionStatus;
  status_detail: string | null;
  frontier_frame: number;
  analysed_frames: number;
  created_at: string;
  meta: Record<string, unknown>;
}

export interface Evidence {
  kind: string;
  frames?: [number, number] | null;
  event_id?: string | null;
  scores?: Record<string, number> | null;
  note?: string | null;
}

export interface BaiEvent {
  event_id: string;
  session_id: string;
  type: string;
  frame_start: number;
  frame_end: number;
  pts_us: number;
  actors: { player_id: PlayerId | null; track_id: number | null; opponent_id: PlayerId | null };
  payload: Record<string, any>;
  confidence: number | null;
  band: Band;
  status: EventStatus;
  evidence: Evidence[];
  provenance: { model: string; profile?: string | null };
  supersedes: string | null;
  parent_id: string | null;
  seq: number | null;
}

export interface MatchState {
  game_no: number;
  score: Record<PlayerId, number>;
  games_won: Record<PlayerId, number>;
  completed_games: [number, number][];
  server: PlayerId;
  receiver: PlayerId;
  service_court: "left" | "right";
  ends: Record<PlayerId, "near" | "far">;
  rally_no: number;
  winner: PlayerId | null;
  game_point: PlayerId | null;
  match_point: PlayerId | null;
  deuce: boolean;
  deciding_game: boolean;
}

export interface StatusMsg {
  type: "status";
  status: SessionStatus;
  detail: string | null;
  n_frames: number;
  frontier_frame: number;
  playhead: number;
  rate_x?: number;
  lead_ms?: number;
  degraded?: { stage: string; reason: string }[];
}

export interface PlayerStats {
  points_won: number;
  points_lost: number;
  win_rate: number | null;
  winners: number;
  errors_out: number;
  errors_net: number;
  strokes: Record<string, number>;
  smashes: number;
  jump_smashes: number;
  smash_points: number;
  serves: number;
  serve_points_won: number;
  distance_m: number;
  points_won_under_pressure: number;
}

export interface Highlight {
  rally_id: string;
  rally_no: number;
  frame_start: number;
  frame_end: number;
  score: number;
  categories: string[];
  reasons: Record<string, number>;
  player: PlayerId | null;
}

export interface Analytics {
  rallies: number;
  players: Partial<Record<PlayerId, PlayerStats>>;
  momentum: {
    rally_no: number;
    value: number;
    leader: PlayerId;
    run: { player: PlayerId; length: number };
  }[];
  momentum_shifts: { rally_no: number; to: PlayerId; rally_id: string }[];
  score_timeline: {
    rally_no: number;
    game_no: number;
    score: Record<PlayerId, number>;
    winner: PlayerId;
    frame: number;
    rally_id: string;
  }[];
  avg_rally_shots: number | null;
  longest_rally_shots: number;
}

export interface Heatmap {
  player: PlayerId;
  kind: string;
  cell_m: number;
  origin_m: [number, number];
  shape: [number, number];
  total: number;
  values: number[][];
}

export interface Calibration {
  H: number[][];
  reprojection_error_px: number;
  n_points: number;
  net_ground_y?: number;
  net_top_y?: number;
}

export interface AskAnswer {
  text: string;
  citations: { kind: "ev" | "kb"; ref: string; frame?: number; type?: string }[];
  grounded: boolean;
  issues: string[];
  provider: string;
  model: string;
}
