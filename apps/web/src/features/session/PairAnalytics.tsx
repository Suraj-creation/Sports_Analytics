import { useQuery } from "@tanstack/react-query";
import { useAnalysisQueryKey } from "@/lib/analysisQuery";
import { api } from "@/lib/api";
import type { Session } from "@/lib/types";
import { DoublesService } from "./DoublesService";

export function PairAnalytics({ session }: { session: Session }) {
  const query = useQuery({
    queryKey: useAnalysisQueryKey("individual-analytics", session),
    queryFn: () => api.individualAnalytics(session.session_id),
    enabled: Boolean(session.media),
  });
  const data = query.data;
  return (
    <section className="analysis-panel" aria-label="Reviewed pair positions">
      <h2 className="font-medium">Your pair</h2>
      <p className="analysis-panel-hint mt-2">
        Link all four players in Visual track observations below, then review hitters. Pair measurements use
        reviewed intervals and validated court positions during official rallies.
      </p>
      {!data?.pairs || !Object.values(data.pairs).some((pair) => pair.observed_frames > 0) ? (
        <p className="mt-4 text-sm">No pair positions have sufficient reviewed evidence yet.</p>
      ) : (
        Object.entries(data.pairs).map(([team, pair]) => (
          <div className="mt-4 rounded border border-seam p-3" key={team}>
            <h3 className="font-medium">
              {pair.members.map((id) => data.participants[id]?.name || "Unnamed player").join(" & ")}
            </h3>
            <p className="mt-2 text-sm">
              {pair.observed_frames} frames with both players · {pair.front_back_frames} front/back ·{" "}
              {pair.side_by_side_frames} side by side
            </p>
            {pair.members.map((id) => (
              <p className="mt-1 text-sm" key={id}>
                {data.participants[id]?.name || "Unnamed player"}: {data.participants[id]?.total_shots ?? 0}{" "}
                reviewed shots · {pair.front_seconds[id] ?? 0}s nearer the net · {pair.rear_seconds[id] ?? 0}s
                farther from the net
              </p>
            ))}
            <p className="mt-2 text-xs text-line-2">
              Position measurements describe court location; they do not establish tactical responsibility.
            </p>
          </div>
        ))
      )}
      {session.roster?.match_format === "doubles" && (
        <DoublesService
          key={`${session.session_id}:${session.meta.analysis_revision ?? 0}`}
          session={session}
        />
      )}
    </section>
  );
}
