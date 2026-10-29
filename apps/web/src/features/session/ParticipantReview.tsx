import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { ErrorNote } from "@/components/ui";
import { playEventEvidence } from "@/features/player/clip";
import { useAnalysisQueryKey, useAnalysisRevision } from "@/lib/analysisQuery";
import { req } from "@/lib/api";
import { clock, fps as fpsOf } from "@/lib/format";
import { frameClock, timeToFrame } from "@/lib/frameClock";
import type { BaiEvent, Session } from "@/lib/types";
import { usePlayback } from "@/stores/playback";

type ReviewEvent = Omit<BaiEvent, "actors"> & {
  actors: { player_id: string | null; track_id: number | null; opponent_id: string | null };
};

export function ParticipantReview({ session }: { session: Session }) {
  const revision = useAnalysisRevision(session);
  return <ParticipantReviewGeneration key={`${session.session_id}:${revision}`} session={session} />;
}

function ParticipantReviewGeneration({ session }: { session: Session }) {
  const [open, setOpen] = useState(false);
  const [observationId, setObservationId] = useState("");
  const [playerId, setPlayerId] = useState("");
  const [start, setStart] = useState("");
  const [shown, setShown] = useState<string[]>([]);
  const [watchedShots, setWatchedShots] = useState<string[]>([]);
  const [shownShots, setShownShots] = useState<string[]>([]);
  const [identityId, setIdentityId] = useState("");
  const [strokeId, setStrokeId] = useState("");
  const watchStop = useRef<(() => void) | null>(null);
  const active = useRef(true);
  const previewAbort = useRef<AbortController | null>(null);
  const cancelSeek = useRef<(() => void) | null>(null);
  useEffect(() => {
    active.current = true;
    return () => {
      active.current = false;
      watchStop.current?.();
      previewAbort.current?.abort();
      cancelSeek.current?.();
      if (usePlayback.getState().reviewBox?.sessionId === session.session_id)
        usePlayback.setState({ reviewBox: null });
    };
  }, [session.session_id]);
  const client = useQueryClient();
  const base = `/api/sessions/${encodeURIComponent(session.session_id)}`;
  const observations = useQuery({
    queryKey: useAnalysisQueryKey("review-observations", session),
    enabled: open,
    queryFn: () => req<{ events: BaiEvent[] }>(`${base}/events?types=participant_observation,stroke`),
  });
  const identities = useQuery({
    queryKey: useAnalysisQueryKey("identity-reviews", session),
    enabled: open,
    queryFn: () => req<ReviewEvent[]>(`${base}/identity-reviews`),
  });
  const shotReviews = useQuery({
    queryKey: useAnalysisQueryKey("stroke-participant-reviews", session),
    enabled: open,
    queryFn: () => req<ReviewEvent[]>(`${base}/stroke-participant-reviews`),
  });
  const refresh = () => {
    void client.invalidateQueries({ queryKey: ["identity-reviews", session.session_id] });
    void client.invalidateQueries({ queryKey: ["stroke-participant-reviews", session.session_id] });
    void client.invalidateQueries({ queryKey: ["individual-analytics", session.session_id] });
    void client.invalidateQueries({ queryKey: ["estimated-individual-analytics", session.session_id] });
  };
  const preview = useMutation({
    mutationFn: async ({
      observation,
      frame,
      track,
      shot,
    }: {
      observation: string;
      frame: number;
      track: number;
      shot?: string;
    }) => {
      previewAbort.current?.abort();
      const controller = new AbortController();
      previewAbort.current = controller;
      const currentVideo = usePlayback.getState().video;
      if (!currentVideo) throw new Error("The video player is not ready yet.");
      const video: HTMLVideoElement = currentVideo;
      const result = await req<{
        available: boolean;
        frame: number;
        bbox: [number, number, number, number] | null;
      }>(`${base}/participant-observations/${encodeURIComponent(observation)}/box?frame=${frame}`, {
        signal: controller.signal,
      });
      if (!active.current || controller.signal.aborted) throw new Error("This analysis was replaced.");
      if (!result.available || !result.bbox || result.frame !== frame)
        throw new Error(
          "No track box is available for this frame. Choose another frame or review new analysis.",
        );
      video.pause();
      usePlayback.setState({
        reviewBox: { sessionId: session.session_id, frame, trackId: track, bbox: result.bbox },
      });
      const fps = fpsOf(session.media);
      await new Promise<void>((resolve, reject) => {
        let sought = false;
        let unsubscribe = () => {};
        const timer = window.setTimeout(() => {
          cleanup();
          reject(new Error("The requested video frame did not appear. Try again."));
        }, 5000);
        function cleanup() {
          window.clearTimeout(timer);
          video.removeEventListener("seeked", onSeeked);
          unsubscribe();
          cancelSeek.current = null;
        }
        cancelSeek.current = () => {
          cleanup();
          reject(new Error("This analysis was replaced."));
        };
        function check() {
          if (
            sought &&
            usePlayback.getState().video === video &&
            !video.seeking &&
            timeToFrame(video.currentTime, fps) === frame &&
            frameClock.frame === frame
          ) {
            cleanup();
            resolve();
          }
        }
        function onSeeked() {
          sought = true;
          check();
        }
        video.addEventListener("seeked", onSeeked);
        unsubscribe = frameClock.subscribe(check);
        if (!video.seeking && timeToFrame(video.currentTime, fps) === frame && frameClock.frame === frame) {
          sought = true;
          check();
        } else usePlayback.getState().seekFrame(frame, fps);
      });
      await new Promise<void>((resolve) =>
        requestAnimationFrame(() => requestAnimationFrame(() => resolve())),
      );
      if (
        !active.current ||
        controller.signal.aborted ||
        usePlayback.getState().video !== video ||
        video.seeking ||
        frameClock.frame !== frame ||
        timeToFrame(video.currentTime, fps) !== frame
      )
        throw new Error("The selected video frame changed. Show the track box again.");
      frameClock.poke();
      document.querySelector("[data-match-player]")?.scrollIntoView({ behavior: "smooth", block: "center" });
      return { key: `${observation}:${frame}:${track}`, shot };
    },
    onSuccess: ({ key, shot }) => {
      if (!active.current) return;
      if (shot) setShownShots((items) => [...items, `${shot}:${key}`]);
      else setShown((items) => [...items, key]);
    },
  });
  const createIdentity = useMutation({
    mutationFn: () =>
      req(`${base}/identity-reviews`, {
        method: "POST",
        body: JSON.stringify({
          observation_id: observationId,
          player_id: playerId,
          frame_start: Number(start),
          frame_end: Number(start),
        }),
      }),
    onSuccess: () => {
      refresh();
      setObservationId("");
      setPlayerId("");
      setStart("");
    },
  });
  const removeIdentity = useMutation({
    mutationFn: (id: string) =>
      req(`${base}/identity-reviews/${encodeURIComponent(id)}`, { method: "DELETE" }),
    onSuccess: refresh,
  });
  const selectedIdentity = identities.data?.find((event) => event.event_id === identityId);
  const strokes = (observations.data?.events ?? []).filter((event) => {
    if (event.type !== "stroke" || !selectedIdentity) return false;
    const hypothesis = event.payload.participant_hypothesis;
    return (
      hypothesis &&
      typeof hypothesis === "object" &&
      hypothesis.participant_id === selectedIdentity.payload.participant_id &&
      hypothesis.track_id === selectedIdentity.actors.track_id &&
      event.frame_start >= selectedIdentity.frame_start &&
      event.frame_start <= selectedIdentity.frame_end
    );
  });
  const selectedStroke = strokes.find((event) => event.event_id === strokeId);
  const watchShot = (event: BaiEvent) => {
    const video = usePlayback.getState().video;
    const lead = Math.max(0, event.frame_start - Math.ceil(fpsOf(session.media)));
    if (!video || lead >= event.frame_start) return;
    watchStop.current?.();
    let sawLead = false;
    watchStop.current = frameClock.subscribe((frame) => {
      if (usePlayback.getState().video !== video || video.paused) return;
      if (frame >= lead && frame < event.frame_start) sawLead = true;
      if (sawLead && frame >= event.frame_start) {
        setWatchedShots((items) => [...items, event.event_id]);
        watchStop.current?.();
        watchStop.current = null;
      }
    });
    playEventEvidence({ ...event, frame_start: lead }, session.media);
  };
  const createShotReview = useMutation({
    mutationFn: () => {
      if (!selectedIdentity || !selectedStroke) throw new Error("Select a player association and shot.");
      return req(`${base}/strokes/${encodeURIComponent(selectedStroke.event_id)}/participant-review`, {
        method: "POST",
        body: JSON.stringify({
          identity_review_id: selectedIdentity.event_id,
          player_id: selectedIdentity.actors.player_id,
          participant_id: selectedIdentity.payload.participant_id,
          track_id: selectedIdentity.actors.track_id,
        }),
      });
    },
    onSuccess: () => {
      refresh();
      setStrokeId("");
    },
  });
  const removeShotReview = useMutation({
    mutationFn: (id: string) =>
      req(`${base}/stroke-participant-reviews/${encodeURIComponent(id)}`, { method: "DELETE" }),
    onSuccess: refresh,
  });
  const people = session.roster?.participants ?? [];
  const name = (id: string | null) =>
    people.find((person) => person.participant_id === id)?.name || id || "Unknown player";
  const starts = (observations.data?.events ?? []).filter(
    (event) =>
      event.type === "participant_observation" &&
      ["PARTICIPANT_FIRST_OBSERVED", "PLAYER_ENTERED"].includes(String(event.payload.kind)),
  );
  const chosenObservation = starts.find((event) => event.event_id === observationId);
  const selectedTrack = chosenObservation?.payload.track_id;
  const frameNumber = start !== "" ? Number(start) : NaN;
  const previewKey = `${observationId}:${frameNumber}:${selectedTrack}`;
  const shotPreviewKey = `${selectedIdentity?.payload.observation_id}:${selectedStroke?.frame_start}:${selectedIdentity?.actors.track_id}`;
  const labelClass = "block text-sm";
  const inputClass = "mt-2 block min-h-11 w-full rounded-lg border border-seam bg-stand px-3";
  return (
    <details className="analysis-panel mt-5" onToggle={(event) => setOpen(event.currentTarget.open)}>
      <summary className="cursor-pointer text-sm font-medium">Review player evidence</summary>
      {open && (
        <div className="mt-4 space-y-5">
          <p className="analysis-panel-hint">
            Show the track box on the video and confirm only a frame you can identify. Each review covers one
            frame because a track can switch people. Player review does not verify shot type.
          </p>
          {!people.length && <p className="text-sm">Set up participants before reviewing player evidence.</p>}
          {(observations.error || identities.error || shotReviews.error) && (
            <ErrorNote error={observations.error || identities.error || shotReviews.error} />
          )}
          {people.length > 0 && (
            <form
              className="space-y-3"
              onSubmit={(event) => {
                event.preventDefault();
                createIdentity.mutate();
              }}
            >
              <h3 className="font-medium">1. Link a track at one frame to a person</h3>
              <label className={labelClass}>
                Track observation
                <select
                  className={inputClass}
                  value={observationId}
                  onChange={(event) => setObservationId(event.target.value)}
                  required
                >
                  <option value="">Select an observation</option>
                  {starts.map((event) => (
                    <option key={event.event_id} value={event.event_id}>
                      Track {String(event.payload.track_id)} · frame {event.frame_start} ·{" "}
                      {clock(event.frame_start, session.media)}
                    </option>
                  ))}
                </select>
              </label>
              {observationId && (
                <button
                  className="analysis-watch"
                  type="button"
                  onClick={() => {
                    const event = starts.find((item) => item.event_id === observationId);
                    if (event) playEventEvidence(event, session.media);
                  }}
                >
                  Watch observation
                </button>
              )}
              <label className={labelClass}>
                Person
                <select
                  className={inputClass}
                  value={playerId}
                  onChange={(event) => setPlayerId(event.target.value)}
                  required
                >
                  <option value="">Select a person</option>
                  {people.map((person, index) => (
                    <option key={person.participant_id} value={person.participant_id}>
                      {person.name || `Player ${index + 1}`}
                    </option>
                  ))}
                </select>
              </label>
              <label className={labelClass}>
                Reviewed frame
                <input
                  className={inputClass}
                  type="number"
                  min="0"
                  step="1"
                  value={start}
                  onChange={(event) => setStart(event.target.value)}
                  required
                />
              </label>
              <button
                className="analysis-watch"
                type="button"
                disabled={
                  !observationId ||
                  !Number.isInteger(frameNumber) ||
                  frameNumber < 0 ||
                  typeof selectedTrack !== "number" ||
                  preview.isPending
                }
                onClick={() =>
                  preview.mutate({
                    observation: observationId,
                    frame: frameNumber,
                    track: selectedTrack as number,
                  })
                }
              >
                Show track box on video
              </button>
              {shown.includes(previewKey) && (
                <p className="text-xs text-line-2">
                  Track box shown for this frame. Inspect the highlighted person before confirming.
                </p>
              )}
              {preview.error && <ErrorNote error={preview.error} />}
              {createIdentity.error && <ErrorNote error={createIdentity.error} />}
              <button
                className="rally-action"
                type="submit"
                disabled={createIdentity.isPending || !shown.includes(previewKey)}
              >
                Confirm reviewed frame
              </button>
            </form>
          )}
          {(identities.data?.length ?? 0) > 0 && (
            <div>
              <h3 className="font-medium">Reviewed track intervals</h3>
              <ul className="mt-2 space-y-2 text-sm">
                {identities.data?.map((event) => (
                  <li key={event.event_id}>
                    {name(event.actors.player_id)} · track {event.actors.track_id} · frames{" "}
                    {event.frame_start}–{event.frame_end}{" "}
                    <button
                      className="analysis-watch"
                      type="button"
                      onClick={() => removeIdentity.mutate(event.event_id)}
                    >
                      Revoke
                    </button>
                  </li>
                ))}
              </ul>
              {removeIdentity.error && <ErrorNote error={removeIdentity.error} />}
            </div>
          )}
          {(identities.data?.length ?? 0) > 0 && (
            <form
              className="space-y-3"
              onSubmit={(event) => {
                event.preventDefault();
                createShotReview.mutate();
              }}
            >
              <h3 className="font-medium">2. Confirm the player for a shot</h3>
              <label className={labelClass}>
                Reviewed interval
                <select
                  className={inputClass}
                  value={identityId}
                  onChange={(event) => {
                    setIdentityId(event.target.value);
                    setStrokeId("");
                  }}
                  required
                >
                  <option value="">Select an interval</option>
                  {identities.data?.map((event) => (
                    <option key={event.event_id} value={event.event_id}>
                      {name(event.actors.player_id)} · track {event.actors.track_id} · {event.frame_start}–
                      {event.frame_end}
                    </option>
                  ))}
                </select>
              </label>
              <label className={labelClass}>
                Shot candidate
                <select
                  className={inputClass}
                  value={strokeId}
                  onChange={(event) => setStrokeId(event.target.value)}
                  required
                >
                  <option value="">Select a shot</option>
                  {strokes.map((event) => (
                    <option key={event.event_id} value={event.event_id}>
                      Frame {event.frame_start} · {String(event.payload.stroke ?? "unknown")}
                    </option>
                  ))}
                </select>
              </label>
              {selectedStroke && (
                <div className="flex flex-wrap gap-2">
                  <button className="analysis-watch" type="button" onClick={() => watchShot(selectedStroke)}>
                    Watch shot
                  </button>
                  <button
                    className="analysis-watch"
                    type="button"
                    disabled={
                      !selectedIdentity ||
                      preview.isPending ||
                      !watchedShots.includes(selectedStroke.event_id)
                    }
                    onClick={() => {
                      if (
                        selectedIdentity &&
                        typeof selectedIdentity.payload.observation_id === "string" &&
                        typeof selectedIdentity.actors.track_id === "number"
                      )
                        preview.mutate({
                          observation: selectedIdentity.payload.observation_id,
                          frame: selectedStroke.frame_start,
                          track: selectedIdentity.actors.track_id,
                          shot: selectedStroke.event_id,
                        });
                    }}
                  >
                    Show shot track box
                  </button>
                </div>
              )}
              {selectedStroke && !watchedShots.includes(selectedStroke.event_id) && (
                <p className="text-xs text-line-2">
                  Play the shot from before contact through the contact frame to enable track review.
                </p>
              )}
              {preview.error && <ErrorNote error={preview.error} />}
              {createShotReview.error && <ErrorNote error={createShotReview.error} />}
              <button
                className="rally-action"
                type="submit"
                disabled={
                  createShotReview.isPending ||
                  !selectedStroke ||
                  !shownShots.includes(`${selectedStroke.event_id}:${shotPreviewKey}`)
                }
              >
                Confirm player for shot
              </button>
            </form>
          )}
          {(shotReviews.data?.length ?? 0) > 0 && (
            <div>
              <h3 className="font-medium">Reviewed shot associations</h3>
              <ul className="mt-2 space-y-2 text-sm">
                {shotReviews.data?.map((event) => (
                  <li key={event.event_id}>
                    {name(event.actors.player_id)} · frame {event.frame_start}{" "}
                    <button
                      className="analysis-watch"
                      type="button"
                      onClick={() => removeShotReview.mutate(event.event_id)}
                    >
                      Revoke
                    </button>
                  </li>
                ))}
              </ul>
              {removeShotReview.error && <ErrorNote error={removeShotReview.error} />}
            </div>
          )}
        </div>
      )}
    </details>
  );
}
