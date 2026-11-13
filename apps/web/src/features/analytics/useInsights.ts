import { useQuery } from "@tanstack/react-query";
import { ANALYSIS_REFRESH_MS, useLiveAnalysisQueryKey } from "@/lib/analysisRefresh";
import { api, req } from "@/lib/api";
import type { PlayerId, Session } from "@/lib/types";
import { useSession } from "@/stores/session";

export interface PlayerTactics {
  serves: number;
  serve_rallies: number;
  serve_points_won: number;
  serve_win_rate: number | null;
  returns: number;
  return_rallies: number;
  return_points_won: number;
  return_win_rate: number | null;
  shot_distribution: { stroke: string; count: number; share: number }[];
  rally_length: { label: string; rallies: number; points_won: number; win_rate: number | null }[];
}

interface SessionInsights {
  schema_version: number;
  session_id: string;
  availability: { analytics: boolean; partial: boolean; reason: string | null };
  lineage: { event_seq: number; source: string; metric_version: number };
  tactics: Partial<Record<PlayerId, PlayerTactics>> | null;
  definitions: Record<string, string>;
}

export function useInsights(id: string) {
  return useQuery({
    queryKey: useLiveAnalysisQueryKey("insights", id),
    queryFn: ({ signal }) =>
      req<SessionInsights>(`/api/sessions/${encodeURIComponent(id)}/insights`, { signal }),
    staleTime: ANALYSIS_REFRESH_MS,
  });
}

/** A zero default distance is not a measurement unless court-position samples exist. */
export function useMeasuredMovement(session: Session, player: PlayerId) {
  const calibrated = useSession((s) => s.calibration !== null);
  return useQuery({
    queryKey: useLiveAnalysisQueryKey("movement-evidence", session, player),
    queryFn: ({ signal }) => api.heatmap(session.session_id, player, "presence", signal),
    staleTime: ANALYSIS_REFRESH_MS,
    enabled: calibrated,
  });
}
