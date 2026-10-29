import { useQuery } from "@tanstack/react-query";
import { useAnalysisQueryKey } from "@/lib/analysisQuery";
import { api } from "@/lib/api";
import type { Session } from "@/lib/types";

export function IndividualAnalytics({ session }: { session: Session }) {
  const query = useQuery({
    queryKey: useAnalysisQueryKey("individual-analytics", session),
    queryFn: () => api.individualAnalytics(session.session_id),
    enabled: Boolean(session.media),
    refetchInterval: 15000,
  });
  if (!session.media || !query.data?.available) return null;
  const data = query.data;
  return (
    <section className="analysis-panel mt-5" aria-labelledby="individual-heading">
      <h2 id="individual-heading" className="font-medium">
        Individual player analytics
      </h2>
      <p className="analysis-panel-hint mt-2">
        Counts include official-rally shots with a reviewed player association. Shot types remain estimates
        unless separately reviewed.
      </p>
      <ul className="mt-3 grid gap-3 sm:grid-cols-2">
        {Object.entries(data.participants).map(([id, person], index) => (
          <li key={id} className="rounded-lg border border-seam p-3">
            <p className="font-medium">{person.name || `Player ${index + 1}`}</p>
            <p className="mt-1 text-sm">
              {person.total_shots} reviewed player {person.total_shots === 1 ? "shot" : "shots"}
            </p>
            {Object.keys(person.shot_distribution).length > 0 && (
              <p className="mt-1 text-xs text-line-2">
                {Object.entries(person.shot_distribution)
                  .map(([shot, count]) => `${shot}: ${count}`)
                  .join(" · ")}
              </p>
            )}
          </li>
        ))}
      </ul>
      <p className="mt-3 text-xs text-line-2">
        {data.accounting.unattributed_shots} unassigned of {data.accounting.total_shots} linked shots.
        {data.legacy_unlinked_shots > 0 &&
          ` ${data.legacy_unlinked_shots} older shots have no linked event and are excluded.`}
      </p>
    </section>
  );
}
