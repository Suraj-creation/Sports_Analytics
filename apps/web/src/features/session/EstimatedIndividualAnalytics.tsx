import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { ErrorNote } from "@/components/ui";
import { useAnalysisQueryKey } from "@/lib/analysisQuery";
import { api } from "@/lib/api";
import type { Session } from "@/lib/types";

export function EstimatedIndividualAnalytics({ session }: { session: Session }) {
  const [limit, setLimit] = useState(8);
  const result = useQuery({
    queryKey: useAnalysisQueryKey("estimated-individual-analytics", session),
    queryFn: () => api.estimatedIndividualAnalytics(session.session_id),
    enabled: Boolean(session.media),
    refetchInterval: ["analysing", "ready_to_play"].includes(session.status) ? 30000 : false,
  });
  if (result.error)
    return (
      <section className="analysis-panel mt-5">
        <h2>Automatic player estimates</h2>
        <ErrorNote error={result.error} />
      </section>
    );
  if (!result.data) return null;
  const scope = result.data.all_linked;
  const episodes = result.data.episode_profiles.all_linked;
  if (!result.data.available && episodes.episodes.length === 0) return null;
  return (
    <section className="analysis-panel mt-5" aria-labelledby="estimated-individual-heading">
      <h2 id="estimated-individual-heading" className="font-medium">
        Automatic player estimates
      </h2>
      <p className="analysis-panel-hint mt-2">
        These are not verified. A reviewed track frame seeds nearby automatic player estimates; track switches
        and shot labels can be wrong. Counts include linked shots in rallies whose match status is uncertain
        and may overlap reviewed totals; do not add them together. They do not represent official scores.
      </p>
      {!result.data.available && (
        <p className="mt-3 text-sm text-line-2">
          Set up participants and review a track frame to associate estimates with named people.
        </p>
      )}
      <ul className="mt-3 grid gap-3 sm:grid-cols-2">
        {Object.entries(scope.participants).map(([id, person], index) => (
          <li key={id} className="rounded-lg border border-seam p-3">
            <p className="font-medium">{person.name || `Player ${index + 1}`}</p>
            <p className="mt-1 text-sm">
              {person.estimated_shots} estimated {person.estimated_shots === 1 ? "shot" : "shots"}
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
        {scope.accounting.unresolved_shots} unresolved of {scope.accounting.total_linked_shots} linked shots.
        {scope.legacy_unlinked_shots > 0 &&
          ` ${scope.legacy_unlinked_shots} older unlinked shots are excluded.`}
      </p>
      <div className="mt-5 border-t border-seam pt-4">
        <h3 className="font-medium">Anonymous track episodes</h3>
        <p className="analysis-panel-hint mt-2">
          Candidate shots are grouped automatically by a temporary visual track. A track can switch people or
          restart; these are not durable player identities and cannot be added to named totals. Detector-run
          counts indicate the detector ran on the frame, not that it matched a particular person.
        </p>
        {episodes.episodes.length === 0 ? (
          <p className="mt-2 text-sm text-line-2">No supported track candidates are available yet.</p>
        ) : (
          <ul className="mt-3 space-y-2 text-sm">
            {episodes.episodes.slice(0, limit).map((episode) => (
              <li key={`${episode.observation_id}:${episode.track_id}`}>
                Track {episode.track_id} · episode {episode.observation_id.slice(-6)} ·{" "}
                {episode.candidate_shots} candidate {episode.candidate_shots === 1 ? "shot" : "shots"} ·{" "}
                {episode.detector_run_counts.ran} detector-run, {episode.detector_run_counts.not_run} carried,{" "}
                {episode.detector_run_counts.unknown} source unknown
              </li>
            ))}
          </ul>
        )}
        {episodes.episodes.length > limit && (
          <button className="rally-action mt-3" type="button" onClick={() => setLimit((n) => n + 8)}>
            Show more tracks
          </button>
        )}
        <p className="mt-2 text-xs text-line-2">
          {episodes.accounting.unresolved_shots} linked shots have no supported track candidate.
        </p>
      </div>
    </section>
  );
}
