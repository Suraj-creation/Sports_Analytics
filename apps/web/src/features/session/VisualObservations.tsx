import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { ErrorNote, Spinner } from "@/components/ui";
import { playEventEvidence } from "@/features/player/clip";
import { useAnalysisQueryKey } from "@/lib/analysisQuery";
import { req } from "@/lib/api";
import { clock } from "@/lib/format";
import type { BaiEvent, Session } from "@/lib/types";

const EVENT_TYPES = "participant_observation,identity_ambiguity";
const PAGE_SIZE = 50;

function observationLabel(event: BaiEvent): string {
  if (event.type === "identity_ambiguity") return "Tracking continuity uncertain";
  switch (event.payload.kind) {
    case "PARTICIPANT_FIRST_OBSERVED":
    case "PLAYER_ENTERED":
      return "Visual track observed";
    case "PLAYER_EXITED":
      return "Visual track no longer observed";
    case "PLAYER_REIDENTIFICATION_UNCERTAIN":
    case "PLAYER_SUBSTITUTION_OR_IDENTITY_UNCERTAIN":
      return "Possible track connection, unconfirmed";
    default:
      return "Visual track observation";
  }
}

function epochOf(event: BaiEvent): string | null {
  if (event.type === "identity_ambiguity") {
    return typeof event.payload.tracker_instance === "string" ? event.payload.tracker_instance : null;
  }
  const id = event.payload.participant_id;
  return typeof id === "string" ? (/^participant-([a-zA-Z0-9]+)-\d+$/.exec(id)?.[1] ?? null) : null;
}

export function VisualObservations({ session }: { session: Session }) {
  const [open, setOpen] = useState(false);
  const [limit, setLimit] = useState(PAGE_SIZE);
  const observations = useQuery({
    queryKey: useAnalysisQueryKey("visual-track-observations", session),
    queryFn: ({ signal }) =>
      req<{ last_seq: number; events: BaiEvent[] }>(
        `/api/sessions/${encodeURIComponent(session.session_id)}/events?${new URLSearchParams({ types: EVENT_TYPES })}`,
        { signal },
      ),
    enabled: open,
    refetchInterval: open && session.status === "analysing" ? 10_000 : false,
  });
  const events = (observations.data?.events ?? [])
    .filter((event) => event.type === "participant_observation" || event.type === "identity_ambiguity")
    .slice()
    .sort((a, b) => a.frame_start - b.frame_start || (a.seq ?? 0) - (b.seq ?? 0));

  return (
    <details className="analysis-panel mt-5" onToggle={(event) => setOpen(event.currentTarget.open)}>
      <summary className="cursor-pointer text-sm font-medium">Visual track observations</summary>
      {open && (
        <div className="mt-4">
          <p className="font-medium">Unlinked visual track observations</p>
          <p className="analysis-panel-hint mt-2">
            These are provisional observations, not verified people or a player roster. A track can change or
            be lost; separate epochs are not linked to the same person. Side estimates and connections can be
            wrong. Coverage may be unavailable, and missing observations do not prove absence.
          </p>
          {observations.isPending && (
            <p className="mt-4 flex items-center gap-2 text-sm text-line-2">
              <Spinner />
              Loading observations
            </p>
          )}
          {observations.error && (
            <div className="mt-4">
              <ErrorNote error={observations.error} />
            </div>
          )}
          {observations.data && events.length === 0 && (
            <p className="mt-4 text-sm text-line-2">
              No visual track observations were recorded. This does not establish that nobody was present.
            </p>
          )}
          {events.length > 0 && (
            <ol className="mt-4 max-h-96 space-y-2 overflow-y-auto" aria-label="Visual track evidence">
              {events.slice(0, limit).map((event) => {
                const epoch = epochOf(event);
                const track = event.payload.track_id;
                const side = event.payload.side;
                const time = clock(event.frame_start, session.media);
                return (
                  <li
                    key={event.event_id}
                    className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2 border-b border-seam py-2 text-sm"
                  >
                    <div>
                      <p className="font-medium">{observationLabel(event)} · provisional</p>
                      <p className="text-xs text-line-2">
                        {event.type === "participant_observation" && Number.isInteger(track) && track >= 0
                          ? `Track ${track} · `
                          : ""}
                        {event.type === "participant_observation"
                          ? `Epoch ${epoch ?? "unavailable"} · `
                          : epoch
                            ? `New epoch ${epoch} · `
                            : ""}
                        {side === "near" || side === "far" ? `Side estimate: ${side} · ` : ""}
                        {time} · frame {event.frame_start.toLocaleString()}
                      </p>
                    </div>
                    <button
                      type="button"
                      className="analysis-watch"
                      onClick={() => playEventEvidence(event, session.media)}
                      aria-label={`Watch observation at ${time}`}
                    >
                      Watch
                    </button>
                  </li>
                );
              })}
            </ol>
          )}
          {events.length > limit && (
            <div className="mt-4">
              <p className="text-xs text-line-2">Showing the first {limit} entries; more are available.</p>
              <button
                type="button"
                className="rally-action mt-2"
                onClick={() => setLimit((value) => value + PAGE_SIZE)}
              >
                Show more observations
              </button>
            </div>
          )}
        </div>
      )}
    </details>
  );
}
