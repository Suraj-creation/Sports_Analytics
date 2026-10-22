import type { Analytics, Highlight, PlayerId, PlayerStats, Session } from "@/lib/types";

export interface MatchSummary {
  session: Session;
  analytics:
    | (Omit<Analytics, "players"> & {
        active_play_s?: number;
        players: Partial<Record<PlayerId, Omit<PlayerStats, "distance_m"> & { distance_m: number | null }>>;
      })
    | null;
  availability: { analytics: boolean; partial: boolean; reason: string | null };
  highlights: Highlight[];
  lineage: { event_seq: number; source: string; metric_version: number };
}
export interface PersonHistory {
  session_id: string;
  title: string;
  created_at: string;
  player_id: string;
  points_won: number | null;
  points_lost: number | null;
  win_rate: number | null;
  rallies: number | null;
  strokes: Record<string, number> | null;
  distance_m: number | null;
}
export interface Person {
  person_id: string;
  name: string;
  matches: number;
  session_ids: string[];
  points_won: number | null;
  points_lost: number | null;
  win_rate: number | null;
  strokes: Record<string, number> | null;
  distance_m: number | null;
  history: PersonHistory[];
}
export interface Overview {
  schema_version: number;
  generated_at: string;
  scope: { limit: number; returned_matches: number; truncated: boolean };
  matches: MatchSummary[];
  people: Person[];
  progress: {
    named_players: number;
    analysed_matches: number;
    total_rallies: number;
    active_play_s: number;
    history: {
      session_id: string;
      created_at: string;
      rallies: number;
      active_play_s: number;
      avg_rally_shots: number | null;
    }[];
    records?: {
      key: string;
      label: string;
      value: number;
      unit: string;
      session_id: string;
      frame?: number | null;
    }[];
  };
  capabilities: {
    doubles_individual_tracking: boolean;
    shot_speed: boolean;
    player_identity: string;
  };
}
