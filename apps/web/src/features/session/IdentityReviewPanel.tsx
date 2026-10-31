import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { ErrorNote, Field, inputClass } from "@/components/ui";
import { useAnalysisQueryKey, useAnalysisRevision } from "@/lib/analysisQuery";
import { req } from "@/lib/api";
import type { BaiEvent, Session } from "@/lib/types";

interface ReviewData {
  analysis_revision: number;
  events: BaiEvent[];
  stroke_reviews: (BaiEvent & { current_stroke_event_id?: string | null })[];
}

export function IdentityReviewPanel({
  session,
  observations,
}: {
  session: Session;
  observations: BaiEvent[];
}) {
  const revision = useAnalysisRevision(session);
  const client = useQueryClient();
  const base = `/api/sessions/${encodeURIComponent(session.session_id)}`;
  const reviews = useQuery({
    queryKey: useAnalysisQueryKey("identity-reviews", session),
    queryFn: ({ signal }) => req<ReviewData>(`${base}/identity-reviews`, { signal }),
  });
  const strokes = useQuery({
    queryKey: useAnalysisQueryKey("identity-review-strokes", session),
    queryFn: ({ signal }) => req<{ events: BaiEvent[] }>(`${base}/events?types=stroke`, { signal }),
  });
  const births = observations.filter(
    (event) =>
      event.type === "participant_observation" &&
      ["PARTICIPANT_FIRST_OBSERVED", "PLAYER_ENTERED"].includes(String(event.payload.kind)),
  );
  const [observationId, setObservation] = useState("");
  const selected = births.find((event) => event.event_id === observationId) ?? births[0];
  const [participant, setParticipant] = useState("");
  const [start, setStart] = useState<number | null>(null);
  const [end, setEnd] = useState<number | null>(null);
  const people = session.roster?.participants ?? [];
  const ready = session.status === "analysed" && reviews.data?.analysis_revision === revision;
  const mutation = useMutation({
    mutationFn: ({ path, body, method = "POST" }: { path: string; body?: unknown; method?: string }) =>
      req<BaiEvent>(`${base}/${path}`, { method, body: body ? JSON.stringify(body) : undefined }),
    onSuccess: () =>
      client.invalidateQueries({ predicate: (query) => query.queryKey[1] === session.session_id }),
  });
  const name = (id: string | null) =>
    people.find((person) => person.participant_id === id)?.name || id || "Unnamed participant";
  return (
    <section className="mt-5 space-y-3" aria-label="Player identity review">
      <h3 className="font-medium">Link observed tracks to players</h3>
      <p className="text-sm text-line-2">
        Review the video, choose the person and a finite interval. A link ends at a track exit or tracking
        reset. Hitter review confirms the person only; contact and shot type keep their own evidence.
      </p>
      {!ready && (
        <p className="text-sm text-line-2">
          Wait for completed analysis and current observations before saving a review.
        </p>
      )}
      <form
        className="grid gap-3 sm:grid-cols-2"
        onSubmit={(event) => {
          event.preventDefault();
          if (!ready || !selected) return;
          mutation.mutate({
            path: "identity-reviews",
            body: {
              observation_id: selected.event_id,
              participant_id: participant || people[0]?.participant_id,
              start: start ?? selected.frame_start,
              end: end ?? selected.frame_start,
              analysis_revision: revision,
            },
          });
        }}
      >
        <Field label="Observed track">
          <select
            className={inputClass}
            value={selected?.event_id ?? ""}
            onChange={(event) => {
              setObservation(event.target.value);
              setStart(null);
              setEnd(null);
            }}
          >
            {births.map((event) => (
              <option key={event.event_id} value={event.event_id}>
                Track {event.payload.track_id} · frame {event.frame_start}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Roster participant">
          <select
            className={inputClass}
            value={participant || people[0]?.participant_id || ""}
            onChange={(event) => setParticipant(event.target.value)}
          >
            {people.map((person, index) => (
              <option key={person.participant_id} value={person.participant_id}>
                {person.name || `Player ${index + 1}`}
              </option>
            ))}
          </select>
        </Field>
        <Field label="From frame">
          <input
            className={inputClass}
            type="number"
            required
            min={selected?.frame_start ?? 0}
            max={(session.media?.n_frames ?? 1) - 1}
            value={start ?? selected?.frame_start ?? 0}
            onChange={(event) => setStart(event.target.valueAsNumber)}
          />
        </Field>
        <Field label="Through frame">
          <input
            className={inputClass}
            type="number"
            required
            min={start ?? selected?.frame_start ?? 0}
            max={(session.media?.n_frames ?? 1) - 1}
            value={end ?? selected?.frame_start ?? 0}
            onChange={(event) => setEnd(event.target.valueAsNumber)}
          />
        </Field>
        <button
          className="rally-action"
          type="submit"
          disabled={!ready || !selected || !people.length || mutation.isPending}
        >
          Confirm player interval
        </button>
      </form>
      <ErrorNote error={reviews.error || strokes.error || mutation.error} />
      {reviews.data?.events.map((review) => (
        <div key={review.event_id} className="rounded border border-seam p-3 text-sm">
          <p>
            {name(review.actors.player_id)} · track {review.actors.track_id} · frames {review.frame_start}–
            {review.frame_end}
          </p>
          <button
            type="button"
            className="rally-action mt-2"
            disabled={!ready || mutation.isPending}
            onClick={() =>
              mutation.mutate({
                path: `identity-reviews/${review.event_id}?analysis_revision=${revision}`,
                method: "DELETE",
              })
            }
          >
            Revoke player interval
          </button>
          {(strokes.data?.events ?? [])
            .filter(
              (stroke) =>
                stroke.frame_start >= review.frame_start &&
                stroke.frame_start <= review.frame_end &&
                stroke.payload.participant_hypothesis?.observation_id === review.payload.observation_id,
            )
            .map((stroke) => {
              const checked = reviews.data?.stroke_reviews.find(
                (event) =>
                  (event.current_stroke_event_id ?? event.payload.stroke_event_id) === stroke.event_id &&
                  event.payload.identity_review_id === review.event_id,
              );
              return (
                <div key={stroke.event_id} className="mt-2">
                  <span>
                    Frame {stroke.frame_start} · {String(stroke.payload.stroke || "unknown")}
                  </span>{" "}
                  <button
                    type="button"
                    className="rally-action"
                    disabled={!ready || mutation.isPending}
                    onClick={() =>
                      mutation.mutate(
                        checked
                          ? {
                              path: `stroke-participant-reviews/${checked.event_id}?analysis_revision=${revision}`,
                              method: "DELETE",
                            }
                          : {
                              path: "stroke-participant-reviews",
                              body: {
                                stroke_event_id: stroke.event_id,
                                identity_review_id: review.event_id,
                                analysis_revision: revision,
                              },
                            },
                      )
                    }
                  >
                    {checked ? "Revoke hitter review" : `Confirm hitter at frame ${stroke.frame_start}`}
                  </button>
                </div>
              );
            })}
        </div>
      ))}
    </section>
  );
}
