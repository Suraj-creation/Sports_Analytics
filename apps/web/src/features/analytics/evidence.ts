import type { EventLog } from "@/lib/events";
import type { BaiEvent, PlayerId } from "@/lib/types";

/** A presentation projection of persisted events. Server analytics remain authoritative. */
export interface EvidenceRally {
  id: string;
  no: number;
  start: number;
  end: number;
  official: boolean;
  winner: PlayerId | null;
  outcome: string;
  shots: BaiEvent[];
  shotCount: number | null;
  event: BaiEvent;
}

export function evidenceRallies(events: EventLog): EvidenceRally[] {
  const strokes = events.ofType("stroke");
  return events.ofType("rally_end").map((event) => {
    const logged = strokes.filter(
      (s) => s.frame_start >= event.frame_start && s.frame_start <= event.frame_end,
    );
    const hasReferences =
      Array.isArray(event.payload.shots) &&
      event.payload.shots.some((s: Record<string, unknown>) => typeof s.event_id === "string");
    const shots =
      hasReferences || (!logged.length && Array.isArray(event.payload.shots))
        ? event.payload.shots.flatMap((s: Record<string, unknown>) => {
            if (typeof s.event_id === "string") {
              const current = events.resolve(s.event_id);
              return current?.type === "stroke" ? [current] : [];
            }
            if (typeof s.frame !== "number") return [];
            return [
              {
                ...event,
                event_id: typeof s.event_id === "string" ? s.event_id : `${event.event_id}:frame:${s.frame}`,
                type: "stroke",
                frame_start: s.frame,
                frame_end: s.frame,
                actors: {
                  player_id: s.player_id === "P1" || s.player_id === "P2" ? s.player_id : null,
                  track_id: null,
                  opponent_id: null,
                },
                payload: { stroke: s.stroke, subtype: s.subtype },
              } as BaiEvent,
            ];
          })
        : logged;
    const uniqueShots = [...new Map(shots.map((s: BaiEvent) => [s.event_id, s])).values()] as BaiEvent[];
    return {
      id: event.event_id,
      no: Number(event.payload.rally_no ?? 0),
      start: event.frame_start,
      end: event.frame_end,
      official: event.payload.official !== false,
      winner: event.payload.winner === "P1" || event.payload.winner === "P2" ? event.payload.winner : null,
      outcome: String(event.payload.outcome ?? "unknown"),
      shots: uniqueShots,
      shotCount: hasReferences
        ? uniqueShots.length
        : typeof event.payload.n_shots === "number"
          ? event.payload.n_shots
          : uniqueShots.length || null,
      event,
    };
  });
}

export interface RallyFilter {
  winner?: PlayerId | "all";
  minimumShots?: number;
  outcome?: "all" | "counted" | "excluded";
}

export function filterRallies(rows: EvidenceRally[], filter: RallyFilter): EvidenceRally[] {
  return rows.filter(
    (r) =>
      (!filter.winner || filter.winner === "all" || r.winner === filter.winner) &&
      (!filter.minimumShots || (r.shotCount !== null && r.shotCount >= filter.minimumShots)) &&
      (!filter.outcome ||
        filter.outcome === "all" ||
        (filter.outcome === "counted" ? r.official : !r.official)),
  );
}

export function shotRows(rows: EvidenceRally[], player: PlayerId) {
  const result = new Map<
    string,
    { stroke: string; count: number; rallies: number; won: number; frame: number }
  >();
  for (const r of rows) {
    if (!r.official) continue;
    const seen = new Set<string>();
    for (const shot of r.shots) {
      if (shot.actors.player_id !== player) continue;
      const stroke = String(
        shot.payload.subtype === "jump_smash" ? "jump_smash" : (shot.payload.stroke ?? "unknown"),
      );
      const row = result.get(stroke) ?? { stroke, count: 0, rallies: 0, won: 0, frame: shot.frame_start };
      row.count++;
      if (!seen.has(stroke)) {
        row.rallies++;
        if (r.winner === player) row.won++;
        seen.add(stroke);
      }
      result.set(stroke, row);
    }
  }
  return [...result.values()].sort((a, b) => b.count - a.count);
}

export function activeSeconds(rows: EvidenceRally[], fps: number): number | null {
  if (!Number.isFinite(fps) || fps <= 0 || !rows.some((r) => r.official)) return null;
  return rows.filter((r) => r.official).reduce((sum, r) => sum + Math.max(0, r.end - r.start + 1) / fps, 0);
}
