import { useMemo } from "react";
import { evidenceRallies } from "@/features/analytics/evidence";
import { clock, fps as fpsOf, shortName, strokeLabel } from "@/lib/format";
import type { Session } from "@/lib/types";
import { usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";
import { playEvidence } from "./clip";

/** Selected evidence and the picture share the same canonical media frame coordinates. */
export function EvidenceDetails({ session }: { session: Session }) {
  const events = useSession((s) => s.events);
  const version = useSession((s) => s.eventsVersion);
  const frame = usePlayback((s) => s.frame);
  const selection = usePlayback((s) => s.selection);
  const clip = usePlayback((s) => s.clip);
  const video = usePlayback((s) => s.video);
  // biome-ignore lint/correctness/useExhaustiveDependencies: version signals mutation of the event log.
  const rows = useMemo(() => evidenceRallies(events), [events, version]);
  const shots = rows.flatMap((r) => r.shots).sort((a, b) => a.frame_start - b.frame_start);
  const rally = rows.find((r) => frame >= r.start && frame <= r.end);
  const current = rally?.shots.filter((s) => s.frame_start <= frame).at(-1);
  const selected = selection
    ? shots.find((s) =>
        selection.eventId ? s.event_id === selection.eventId : s.frame_start === selection.start,
      )
    : current;
  const selectedEvent = (selection?.eventId ? events.resolve(selection.eventId) : undefined) ?? selected;
  const selectedRally = selection
    ? rows.find((r) => selection.start >= r.start && selection.start <= r.end)
    : rally;
  const index = selected ? shots.findIndex((s) => s.event_id === selected.event_id) : -1;
  const jump = (i: number) => {
    const shot = shots[i];
    if (!shot) return;
    const context = rows.find((r) => shot.frame_start >= r.start && shot.frame_start <= r.end);
    playEvidence(
      shot.frame_start,
      Math.min(context?.end ?? shot.frame_end, shot.frame_start + Math.round(fpsOf(session.media) * 1.5)),
      strokeLabel(shot.payload),
      shot.event_id,
    );
  };
  return (
    <section className="evidence-details" aria-label="Video evidence" data-testid="evidence-details">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h2 className="text-base font-semibold" aria-live="polite" aria-atomic="true">
            {selection?.label ?? (current ? strokeLabel(current.payload) : "Explore the match")}
          </h2>
          <p className="mt-1 text-sm text-line-2">
            {selection ? (
              <>
                Selected moment · {clock(selection.start, session.media, true)} · source frame{" "}
                {selection.start.toLocaleString()}
              </>
            ) : (
              "Choose a shot, rally or moment to watch its source evidence here."
            )}
            {selectedEvent?.actors.player_id && ` · ${shortName(session, selectedEvent.actors.player_id)}`}
          </p>
          {selectedRally && (
            <p className="mt-1 text-sm text-line-2">
              Rally {selectedRally.no} · {selectedRally.official ? "Counted" : "Not counted"} ·{" "}
              {selectedRally.winner ? `${shortName(session, selectedRally.winner)} won` : "Winner unresolved"}
            </p>
          )}
          {clip && (
            <p className="mt-1 text-xs text-line-2">
              Clip {clock(clip.from, session.media, true)}–{clock(clip.to, session.media, true)} · frames{" "}
              {clip.from.toLocaleString()}–{clip.to.toLocaleString()} · one-second lead-in on replay
            </p>
          )}
          {selection && !clip && (
            <p className="mt-1 text-xs text-line-2" role="status">
              {video && video.readyState >= 1
                ? "This event is outside the available video range. Choose another moment."
                : "Waiting for video. This moment will open when the recording is ready."}
            </p>
          )}
          {selectedEvent && (
            <p className="mt-2 text-xs text-line-2">
              {selectedEvent.status === "human_verified"
                ? "Human-reviewed event"
                : ["stroke", "contact"].includes(selectedEvent.type)
                  ? "Estimated hit / shot"
                  : "Recorded event"}
              {` · confidence band: ${selectedEvent.band}`}
              {selectedEvent.provenance?.model ? ` · ${selectedEvent.provenance.model}` : ""}
            </p>
          )}
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className="rally-action"
            disabled={index <= 0}
            onClick={() => jump(index - 1)}
          >
            Previous shot
          </button>
          <button
            type="button"
            className="rally-action"
            disabled={index < 0 || index >= shots.length - 1}
            onClick={() => jump(index + 1)}
          >
            Next shot
          </button>
        </div>
      </div>
      {rally && (
        <p className="mt-3 border-t border-seam pt-3 text-xs text-line-2">
          Now showing · Rally {rally.no}
          {current ? ` · ${strokeLabel(current.payload)}` : " · before the first recorded shot"}
          {current?.actors.player_id ? ` · ${shortName(session, current.actors.player_id)}` : ""}
        </p>
      )}
    </section>
  );
}
