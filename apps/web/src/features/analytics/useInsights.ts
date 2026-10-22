import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
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
  const version = useSession((s) => s.analyticsVersion);
  const qc = useQueryClient();
  useEffect(() => {
    if (version > 0) void qc.invalidateQueries({ queryKey: ["insights", id] });
  }, [id, qc, version]);
  return useQuery({
    queryKey: ["insights", id],
    queryFn: () => req<SessionInsights>(`/api/sessions/${encodeURIComponent(id)}/insights`),
  });
}

/** A zero default distance is not a measurement unless court-position samples exist. */
export function useMeasuredMovement(session: Session, player: PlayerId) {
  const calibrated = useSession((s) => s.calibration !== null);
  return useQuery({
    queryKey: ["movement-evidence", session.session_id, player],
    queryFn: () => api.heatmap(session.session_id, player, "presence"),
    enabled: calibrated,
    refetchInterval: session.status === "analysing" ? 5000 : false,
  });
}
