import type { EventLog } from "./events";

/** A reviewed name applies only to this observed episode and finite interval. */
export function reviewedIdentity(
  events: EventLog,
  person: { track: number; observationId: string | null },
  frame: number,
  names: Record<string, string>,
): { id: string; name: string } | null {
  const birth = person.observationId ? events.get(person.observationId) : undefined;
  if (
    !birth ||
    birth.type !== "participant_observation" ||
    birth.provenance.model !== "participant_tracker_v1" ||
    birth.status !== "provisional" ||
    birth.payload.track_id !== person.track
  )
    return null;
  const epoch = /^participant-([A-Za-z0-9]+)-[0-9]{6}$/.exec(String(birth.payload.participant_id))?.[1];
  if (!epoch) return null;
  const candidates = events.ofType("identity_review").filter(
    (review) =>
      review.status === "human_verified" &&
      review.provenance.model === "human" &&
      review.actors.player_id &&
      names[review.actors.player_id] &&
      review.actors.track_id === person.track &&
      birth.frame_start <= review.frame_start &&
      review.frame_start <= frame &&
      frame <= review.frame_end &&
      review.payload.observation_id === birth.event_id &&
      review.payload.participant_id === birth.payload.participant_id &&
      !events
        .window(birth.frame_start, review.frame_end, ["identity_ambiguity", "participant_observation"])
        .some((boundary) => {
          if (boundary.event_id === birth.event_id || boundary.frame_start < birth.frame_start) return false;
          if (
            boundary.type === "participant_observation" &&
            ["PLAYER_ENTERED", "PARTICIPANT_FIRST_OBSERVED"].includes(boundary.payload.kind) &&
            boundary.payload.track_id === person.track &&
            boundary.payload.participant_id !== birth.payload.participant_id
          )
            return true;
          if (boundary.frame_start === birth.frame_start && (boundary.seq ?? 0) < (birth.seq ?? 0))
            return false;
          if (boundary.type === "identity_ambiguity")
            return (
              (boundary.payload.tracker_instance != null && boundary.payload.tracker_instance !== epoch) ||
              ["visual_tracker_reset", "calibration_changed", "prolonged_coverage_loss"].includes(
                boundary.payload.reason,
              )
            );
          return (
            boundary.payload.kind === "PLAYER_EXITED" &&
            boundary.payload.participant_id === birth.payload.participant_id
          );
        }),
  );
  const selected = candidates.length === 1 ? candidates[0] : undefined;
  const id = selected?.actors.player_id;
  return id ? { id, name: names[id] ?? id } : null;
}
