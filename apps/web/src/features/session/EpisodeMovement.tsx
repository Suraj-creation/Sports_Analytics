import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { ErrorNote } from "@/components/ui";
import { api } from "@/lib/api";
import { fps as fpsOf } from "@/lib/format";
import type { Session } from "@/lib/types";
import { usePlayback } from "@/stores/playback";

export function EpisodeMovement({ session }: {session: Session}) {
  const frame = usePlayback((state) => state.frame);
  const [window, setWindow] = useState<{from: number; to: number} | null>(null);
  const result = useQuery({queryKey: ["episode-movement", session.session_id, window], enabled: Boolean(window),
    queryFn: () => api.episodeMovement(session.session_id, window!.from, window!.to), retry: false});
  if (!session.media || session.media.n_frames <= 0) return null;
  const inspect = () => {
    const half = Math.round(30 * fpsOf(session.media));
    const target = Math.max(0, Math.min(frame, session.media!.n_frames - 1));
    setWindow({from: Math.max(0, target - half), to: Math.min(session.media!.n_frames - 1, target + half)});
  };
  return <details className="analysis-panel mt-5">
    <summary className="cursor-pointer text-sm font-medium">Court movement by track</summary>
    <div className="mt-4 space-y-3">
      <p className="analysis-panel-hint">Estimated movement uses only supported, calibrated track segments. It is not a full-match distance or a confirmed person; tracking gaps and jitter can affect it. A detector-run frame does not prove that a specific player was detected.</p>
      <button className="rally-action" type="button" onClick={inspect} disabled={result.isFetching}>Inspect movement near this frame</button>
      {result.isFetching && <p className="text-sm text-line-2">Checking track coverage…</p>}
      {result.error && <ErrorNote error={result.error} />}
      {result.data && !result.data.available && <p className="text-sm text-line-2">Calibrated movement is unavailable for this window.</p>}
      {result.data?.available && <div>
        <p className="text-xs text-line-2">Frames {result.data.window.from}–{result.data.window.to}. {result.data.warning}</p>
        <ul className="mt-3 space-y-2 text-sm">{result.data.episodes.map((episode) => <li key={`${episode.observation_id}:${episode.track_id}`}>
          Track {episode.track_id} · episode {episode.observation_id.slice(-6)} · {episode.distance_m === null ? "distance unavailable" : `${episode.distance_m.toFixed(1)} m estimated`} · {Math.round(episode.coverage_fraction * 100)}% track-frame coverage · {episode.detector_observed_frames} detector-run, {episode.carried_frames} carried, {episode.unknown_source_frames} source unknown
        </li>)}</ul>
      </div>}
    </div>
  </details>;
}
