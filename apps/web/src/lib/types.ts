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

export interface RosterTeam {
  team_id: string;
  score_slot: "P1" | "P2" | null;
}

export interface RosterParticipant {
  participant_id: string;
  name: string | null;
  team_id: string | null;
}

export interface SessionRoster {
  match_format: "singles" | "doubles";
  teams: RosterTeam[];
  participants: RosterParticipant[];
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
  roster?: SessionRoster | null;
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
  analysed_frames?: number;
  analysis_revision?: number;
  playhead: number;
  rate_x?: number;
  lead_ms?: number;
  degraded?: { stage: string; reason: string }[];
  capabilities?: Record<
    string,
    {
      status: string;
      requested_model: string | null;
      active_model: string | null;
      required: boolean;
      reason: string | null;
    }
  >;
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
  distance_m: number | null;
  distance_quality?: {
    status: "estimate" | "unavailable";
    method: string;
    observed_s: number;
    coverage: number;
    reason?: string | null;
  };
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
  /** reference view the camera is tracked against (null: the calibration is taken to hold for the whole shot) */
  cam_ref?: number | null;
  ref_frame?: number | null;
  source?: string;
  /** lines: the court is measured from its painted lines in every frame; camera: tracked from the reference
   *  frame by the background; static: one homography for the whole video */
  mode?: "lines" | "camera" | "static";
  method?: string;
  validity?: string;
  calibration_id?: string | null;
  quality?: { precision: number; support: number; lines: [number, number]; area: number; rms_px: number };
  camera?: { focal_px: number; centre_m: [number, number, number] } | null;
  coverage?: number;
  adjusted_px?: number;
  lines_check?: string;
}

/** Scene segment (a `scene` event's payload): which camera shot that stretch of video */
export interface ScenePayload {
  view: "main" | "alt" | "none";
  camera: number | null;
  analysed: boolean;
  court_quality: number | null;
  duration_s: number;
}

export interface AskAnswer {
  text: string;
  citations: { kind: "ev" | "kb"; ref: string; frame?: number; type?: string }[];
  grounded: boolean;
  issues: string[];
  provider: string;
  model: string;
}

export interface IndividualAnalyticsData {
  available: boolean;
  match_format: "singles" | "doubles" | null;
  participants: Record<
    string,
    {
      name: string | null;
      team_id: string | null;
      total_shots: number;
      shot_distribution: Record<string, number>;
      event_ids: string[];
      events: Array<{
        event_id: string;
        frame: number;
        stroke: string;
        track_id: number;
        review_id: string;
        rally_id: string;
      }>;
      rally_ids: string[];
    }
  >;
  teams: Record<string, { score_slot: "P1" | "P2" | null; attributed_shots: number }>;
  accounting: { total_shots: number; attributed_shots: number; unattributed_shots: number };
  unattributed_event_ids: string[];
  legacy_unlinked_shots: number;
  counting_scope: string;
}

export interface EstimatedIndividualAnalyticsData {
  available: boolean;
  match_format: "singles" | "doubles" | null;
  official: EstimatedShotScope;
  all_linked: EstimatedShotScope;
  episode_profiles: { official: AnonymousEpisodeScope; all_linked: AnonymousEpisodeScope };
  unlinked_stroke_events: number;
  policy: Record<string, unknown>;
}
export interface EstimatedShotScope {
  participants: Record<
    string,
    {
      name: string | null;
      team_id: string | null;
      estimated_shots: number;
      shot_distribution: Record<string, number>;
      events?: unknown[];
    }
  >;
  accounting: {
    total_linked_shots: number;
    estimated_shots: number;
    unresolved_shots: number;
    verified_shots?: number;
  };
  unresolved_event_ids: string[];
  legacy_unlinked_shots: number;
}

export interface AnonymousEpisodeScope {
  episodes: Array<{
    observation_id: string;
    participant_id: string;
    track_id: number;
    candidate_shots: number;
    shot_distribution: Record<string, number>;
    detector_run_counts: { ran: number; not_run: number; unknown: number };
    events?: unknown[];
    status: string;
  }>;
  accounting: { total_linked_shots: number; episode_candidate_shots: number; unresolved_shots: number };
  unresolved_event_ids: string[];
}

export interface EpisodeMovementData {
  available: boolean;
  reason: string | null;
  scope: string;
  window: { from: number; to: number; fps: number };
  episodes: Array<{
    observation_id: string;
    participant_id: string;
    track_id: number;
    status: string;
    distance_m: number | null;
    valid_frames: number;
    detector_observed_frames: number;
    carried_frames: number;
    unknown_source_frames: number;
    coverage_fraction: number;
    observed_seconds: number;
    segments: number;
    positions_m: number[][];
  }>;
  warning: string;
}
