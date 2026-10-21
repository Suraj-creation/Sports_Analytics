import * as Popover from "@radix-ui/react-popover";
import { clsx } from "clsx";
import {
  ChevronLeft,
  ChevronRight,
  Layers as LayersIcon,
  Maximize,
  Pause,
  Play,
  Volume2,
  VolumeX,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { IconButton, Spinner } from "@/components/ui";
import { clock, fps as fpsOf, PLAYER_HEX, shortName } from "@/lib/format";
import { frameClock, timeToFrame } from "@/lib/frameClock";
import type { Session } from "@/lib/types";
import { type Layers, usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";
import { drawOverlay, type OverlayCtx } from "./overlay";
import { ScoreBug } from "./ScoreBug";
import { StrokeToast } from "./StrokeToast";
import { useHls } from "./useHls";

/** Semantic events are final this far behind the analysis frontier (look-ahead + settle). */
export const SEMANTIC_LEAD_S = 3;
const RESUME_MARGIN_S = 2;

const LAYER_LABEL: Record<keyof Layers, string> = {
  shuttle: "Shuttle trail",
  players: "Player boxes",
  pose: "Pose skeletons",
  court: "Court lines",
  labels: "Name labels",
  scoreBug: "Score",
};

export function VideoStage({ session }: { session: Session }) {
  const [video, setVideo] = useState<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const stageRef = useRef<HTMLDivElement>(null);
  const fps = fpsOf(session.media);
  const nFrames = session.media?.n_frames ?? 0;
  const hls = useHls(video, session.session_id, session.media != null);

  const tracks = useSession((s) => s.tracks);
  const events = useSession((s) => s.events);
  const calibration = useSession((s) => s.calibration);
  const connection = useSession((s) => s.connection);
  const tracksVersion = useSession((s) => s.tracksVersion);
  const eventsVersion = useSession((s) => s.eventsVersion);
  const frontier = useSession((s) => s.session?.frontier_frame ?? 0);
  const status = useSession((s) => s.session?.status ?? session.status);

  const layers = usePlayback((s) => s.layers);
  const waitForAnalysis = usePlayback((s) => s.waitForAnalysis);
  const bindVideo = usePlayback((s) => s.bindVideo);
  const setPlaying = usePlayback((s) => s.setPlaying);
  const setFrame = usePlayback((s) => s.setFrame);
  const [hidden, setHidden] = useState(false);
  const [gated, setGated] = useState(false);
  const [muted, setMuted] = useState(true);
  const [rate, setRate] = useState(1);

  useEffect(() => {
    bindVideo(video);
    return () => bindVideo(null);
  }, [video, bindVideo]);

  // ---- presented-frame clock (requestVideoFrameCallback = the exact frame on screen)
  useEffect(() => {
    if (!video) return;
    let id = 0;
    let raf = 0;
    const publish = (t: number) => frameClock.publish(timeToFrame(t, fps));
    if ("requestVideoFrameCallback" in video) {
      const cb: VideoFrameRequestCallback = (_now, meta) => {
        publish(meta.mediaTime);
        id = video.requestVideoFrameCallback(cb);
      };
      id = video.requestVideoFrameCallback(cb);
    } else {
      const loop = () => {
        publish((video as HTMLVideoElement).currentTime);
        raf = requestAnimationFrame(loop);
      };
      raf = requestAnimationFrame(loop);
    }
    const onSeeked = () => publish(video.currentTime);
    video.addEventListener("seeked", onSeeked);
    return () => {
      if (id && "cancelVideoFrameCallback" in video) video.cancelVideoFrameCallback(id);
      cancelAnimationFrame(raf);
      video.removeEventListener("seeked", onSeeked);
    };
  }, [video, fps]);

  // ---- overlay: drawn for exactly the presented frame, outside React
  const overlay = useRef<OverlayCtx | null>(null);
  // biome-ignore lint/correctness/useExhaustiveDependencies: the versions signal buffer mutation → redraw
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!video || !canvas) return;
    const off = hidden
      ? { shuttle: false, players: false, pose: false, court: false, labels: false, scoreBug: false }
      : layers;
    overlay.current = {
      canvas,
      video,
      tracks,
      events,
      calibration,
      layers: off,
      colors: PLAYER_HEX,
      names: { P1: shortName(session, "P1"), P2: shortName(session, "P2") },
    };
    frameClock.poke();
  }, [video, tracks, events, calibration, layers, hidden, session, tracksVersion, eventsVersion]);

  useEffect(
    () =>
      frameClock.subscribe((f) => {
        if (overlay.current) drawOverlay(overlay.current, f);
      }),
    [],
  );

  useEffect(() => {
    const el = stageRef.current;
    if (!el) return;
    const ro = new ResizeObserver(() => frameClock.poke());
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // ---- throttled frame for React panels, playhead to the engine, track prefetch, gating
  useEffect(() => {
    if (!video) return;
    let lastUi = 0;
    let lastReq = 0;
    return frameClock.subscribe((f) => {
      const now = performance.now();
      if (now - lastUi > 120 || video.paused) {
        setFrame(f);
        lastUi = now;
      }
      const st = useSession.getState();
      st.socket?.playhead(f, !video.paused);
      const front = st.session?.frontier_frame ?? 0;
      const analysing = st.session?.status === "analysing";
      // keep ~4 s of analysed tracks ahead of the playhead in the buffer
      const ahead = f + Math.round(4 * fps);
      const need = !st.tracks.isCovered(f) ? f : !st.tracks.isCovered(ahead) ? ahead : -1;
      if (need >= 0 && need <= front && now - lastReq > 800) {
        st.socket?.requestTracks(
          Math.max(0, need - Math.round(fps)),
          Math.min(nFrames - 1, need + Math.round(20 * fps)),
        );
        lastReq = now;
      }
      // hold playback at the frontier so labels appear at their real moment
      if (usePlayback.getState().waitForAnalysis && analysing && !video.paused) {
        if (f > front - SEMANTIC_LEAD_S * fps) {
          video.pause();
          setGated(true);
        }
      }
    });
  }, [video, fps, nFrames, setFrame]);

  useEffect(() => {
    if (!gated || !video) return;
    const ready =
      status !== "analysing" || frontier - SEMANTIC_LEAD_S * fps >= frameClock.frame + RESUME_MARGIN_S * fps;
    if (ready || !waitForAnalysis) {
      setGated(false);
      void video.play().catch(() => {});
    }
  }, [gated, frontier, status, fps, video, waitForAnalysis]);

  // ---- (re)connect → ask for the window around the playhead
  useEffect(() => {
    if (connection === "open") useSession.getState().socket?.seek(frameClock.frame);
  }, [connection]);

  useEffect(() => {
    if (!video) return;
    const onSeeking = () => useSession.getState().socket?.seek(timeToFrame(video.currentTime, fps));
    const onPlay = () => setPlaying(true);
    const onPause = () => {
      setPlaying(false);
      // the last presented frame may have been throttled away from the UI copy
      setFrame(frameClock.frame);
      useSession.getState().socket?.flushPlayhead();
    };
    video.addEventListener("seeking", onSeeking);
    video.addEventListener("play", onPlay);
    video.addEventListener("pause", onPause);
    return () => {
      video.removeEventListener("seeking", onSeeking);
      video.removeEventListener("play", onPlay);
      video.removeEventListener("pause", onPause);
    };
  }, [video, fps, setPlaying, setFrame]);

  useEffect(() => {
    if (video) video.playbackRate = rate;
  }, [video, rate]);

  // "." toggles every overlay (keyboard map lives in SessionPage)
  useEffect(() => {
    const onToggle = () => setHidden((h) => !h);
    window.addEventListener("bai:toggle-overlays", onToggle);
    return () => window.removeEventListener("bai:toggle-overlays", onToggle);
  }, []);

  const playing = usePlayback((s) => s.playing);
  const togglePlay = () => {
    if (!video) return;
    if (video.paused) {
      setGated(false);
      void video.play().catch(() => {});
    } else {
      video.pause();
      setGated(false);
    }
  };

  const noTracksYet = status === "analysing" && frontier < 1;

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden rounded-[var(--radius-card)] border border-seam bg-mat-deep">
      <div ref={stageRef} className="relative min-h-0 flex-1 bg-black" data-testid="video-stage">
        <video
          ref={setVideo}
          className="absolute inset-0 size-full object-contain"
          playsInline
          muted={muted}
          preload="auto"
          onClick={togglePlay}
          onDoubleClick={() => void stageRef.current?.requestFullscreen?.()}
        />
        <canvas ref={canvasRef} className="pointer-events-none absolute inset-0 size-full" aria-hidden />
        {layers.scoreBug && !hidden && <ScoreBug session={session} />}
        {!hidden && <StrokeToast session={session} />}

        {(hls === "loading" || hls === "waiting" || hls === "idle") && (
          <div className="absolute inset-0 grid place-items-center bg-mat-deep/80">
            <div className="flex flex-col items-center gap-3 text-center">
              <Spinner className="size-6" />
              <p className="text-sm text-line-2">
                {status === "ingesting" || status === "created"
                  ? "Preparing the video — playback starts with the first seconds"
                  : "Loading video"}
              </p>
            </div>
          </div>
        )}
        {hls === "error" && (
          <div className="absolute inset-0 grid place-items-center bg-mat-deep/90 px-6 text-center">
            <p className="text-sm text-line-2">
              This browser can't play the stream. Try a current Chrome, Edge or Firefox.
            </p>
          </div>
        )}
        {gated && (
          <div className="absolute inset-x-0 bottom-4 flex justify-center">
            <div className="flex items-center gap-2 rounded-full border border-seam bg-mat-deep/90 px-4 py-2 text-sm backdrop-blur">
              <span className="size-2 animate-pulse rounded-full bg-signal" aria-hidden />
              Analysis is catching up — playback resumes on its own
            </div>
          </div>
        )}
        {noTracksYet && hls === "ready" && !gated && (
          <div className="absolute top-3 right-3 rounded-full bg-mat-deep/85 px-3 py-1 text-xs text-line-2">
            Warming up the models…
          </div>
        )}
      </div>

      <Controls
        playing={playing}
        onToggle={togglePlay}
        fps={fps}
        session={session}
        muted={muted}
        onMute={() => setMuted((m) => !m)}
        rate={rate}
        onRate={setRate}
        onFullscreen={() => void stageRef.current?.requestFullscreen?.()}
        hasAudio={Boolean(session.media?.has_audio)}
      />
    </div>
  );
}

function Controls(props: {
  playing: boolean;
  onToggle: () => void;
  fps: number;
  session: Session;
  muted: boolean;
  onMute: () => void;
  rate: number;
  onRate: (r: number) => void;
  onFullscreen: () => void;
  hasAudio: boolean;
}) {
  const frame = usePlayback((s) => s.frame);
  const seekFrame = usePlayback((s) => s.seekFrame);
  const video = usePlayback((s) => s.video);
  const layers = usePlayback((s) => s.layers);
  const toggleLayer = usePlayback((s) => s.toggleLayer);
  const waitForAnalysis = usePlayback((s) => s.waitForAnalysis);
  const setWait = usePlayback((s) => s.setWaitForAnalysis);
  const n = props.session.media?.n_frames ?? 0;
  const step = (d: number) => {
    video?.pause();
    seekFrame(Math.max(0, Math.min(n - 1, frameClock.frame + d)), props.fps);
  };

  return (
    <div className="flex h-12 shrink-0 items-center gap-1 border-t border-seam px-2">
      <IconButton label={props.playing ? "Pause (Space)" : "Play (Space)"} onClick={props.onToggle}>
        {props.playing ? <Pause className="size-5" /> : <Play className="size-5" />}
      </IconButton>
      <IconButton label="Previous frame (←)" onClick={() => step(-1)}>
        <ChevronLeft className="size-5" />
      </IconButton>
      <IconButton label="Next frame (→)" onClick={() => step(1)}>
        <ChevronRight className="size-5" />
      </IconButton>
      <span className="tabular ml-2 text-sm">
        {clock(frame, props.session.media, true)}
        <span className="text-line-3"> / {clock(n, props.session.media)}</span>
      </span>
      <span className="tabular ml-2 hidden text-xs text-line-3 md:inline">
        frame {frame.toLocaleString()}
      </span>

      <div className="ml-auto flex items-center gap-1">
        <label className="sr-only" htmlFor="rate">
          Playback speed
        </label>
        <select
          id="rate"
          value={props.rate}
          onChange={(e) => props.onRate(Number(e.target.value))}
          className="tabular h-8 rounded-lg border border-seam bg-stand px-2 text-sm text-line"
        >
          {[0.25, 0.5, 1, 1.5, 2].map((r) => (
            <option key={r} value={r}>
              {r}×
            </option>
          ))}
        </select>
        {props.hasAudio && (
          <IconButton label={props.muted ? "Unmute" : "Mute"} onClick={props.onMute}>
            {props.muted ? <VolumeX className="size-5" /> : <Volume2 className="size-5" />}
          </IconButton>
        )}
        <Popover.Root>
          <Popover.Trigger asChild>
            <IconButton label="Overlay layers">
              <LayersIcon className="size-5" />
            </IconButton>
          </Popover.Trigger>
          <Popover.Portal>
            <Popover.Content
              side="top"
              align="end"
              sideOffset={8}
              className="panel z-50 w-64 space-y-1 p-2 shadow-xl shadow-black/40"
            >
              <p className="px-2 pt-1 pb-2 text-xs text-line-3">
                Show on video · press <span className="text-line-2">.</span> to hide all
              </p>
              {(Object.keys(LAYER_LABEL) as (keyof Layers)[]).map((k) => (
                <Toggle key={k} label={LAYER_LABEL[k]} checked={layers[k]} onChange={() => toggleLayer(k)} />
              ))}
              <div className="my-1 border-t border-seam" />
              <Toggle
                label="Wait for analysis"
                hint="Pause at the analysis frontier so shots and points appear at their moment"
                checked={waitForAnalysis}
                onChange={() => setWait(!waitForAnalysis)}
              />
            </Popover.Content>
          </Popover.Portal>
        </Popover.Root>
        <IconButton label="Full screen" onClick={props.onFullscreen}>
          <Maximize className="size-5" />
        </IconButton>
      </div>
    </div>
  );
}

function Toggle({
  label,
  hint,
  checked,
  onChange,
}: {
  label: string;
  hint?: string;
  checked: boolean;
  onChange: () => void;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={onChange}
      className="flex w-full items-start gap-3 rounded-lg px-2 py-1.5 text-left hover:bg-stand-raised"
    >
      <span
        className={clsx(
          "relative mt-0.5 h-4 w-7 shrink-0 rounded-full transition-colors",
          checked ? "bg-signal" : "bg-seam",
        )}
        aria-hidden
      >
        <span
          className={clsx(
            "absolute top-0.5 size-3 rounded-full bg-mat-deep transition-transform",
            checked ? "translate-x-3.5" : "translate-x-0.5",
          )}
        />
      </span>
      <span className="text-sm">
        {label}
        {hint && <span className="block text-xs text-line-3">{hint}</span>}
      </span>
    </button>
  );
}
