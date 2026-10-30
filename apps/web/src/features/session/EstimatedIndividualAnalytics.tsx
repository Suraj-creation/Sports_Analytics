import { useQuery } from "@tanstack/react-query";
import { ErrorNote } from "@/components/ui";
import { api } from "@/lib/api";
import type { Session } from "@/lib/types";

export function EstimatedIndividualAnalytics({ session }: {session: Session}) {
  const result = useQuery({
    queryKey: ["estimated-individual-analytics", session.session_id],
    queryFn: () => api.estimatedIndividualAnalytics(session.session_id),
    enabled: Boolean(session.media),
    refetchInterval: ["analysing", "ready_to_play"].includes(session.status) ? 30000 : false,
  });
  if (result.error) return <section className="analysis-panel mt-5"><h2>Automatic player estimates</h2><ErrorNote error={result.error} /></section>;
  if (!result.data) return null;
  const scope = result.data.all_linked;
  if (!result.data.available) return null;
  return <section className="analysis-panel mt-5" aria-labelledby="estimated-individual-heading">
    <h2 id="estimated-individual-heading" className="font-medium">Automatic player estimates</h2>
    <p className="analysis-panel-hint mt-2">These are not verified. Automatic estimates use available player evidence; track switches and shot labels can be wrong. Counts include linked shots in rallies whose match status is uncertain and may overlap reviewed totals; do not add them together. They do not represent official scores.</p>
    <ul className="mt-3 grid gap-3 sm:grid-cols-2">
      {Object.entries(scope.participants).map(([id, person], index) => <li key={id} className="rounded-lg border border-seam p-3">
        <p className="font-medium">{person.name || `Player ${index + 1}`}</p>
        <p className="mt-1 text-sm">{person.estimated_shots} estimated {person.estimated_shots === 1 ? "shot" : "shots"}</p>
        {Object.keys(person.shot_distribution).length > 0 && <p className="mt-1 text-xs text-line-2">{Object.entries(person.shot_distribution).map(([shot, count]) => `${shot}: ${count}`).join(" · ")}</p>}
      </li>)}
    </ul>
    <p className="mt-3 text-xs text-line-2">{scope.accounting.unresolved_shots} unresolved of {scope.accounting.total_linked_shots} linked shots.
      {scope.legacy_unlinked_shots > 0 && ` ${scope.legacy_unlinked_shots} older unlinked shots are excluded.`}
    </p>

  </section>;
}
