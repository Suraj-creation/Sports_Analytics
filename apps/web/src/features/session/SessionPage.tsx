import * as Dialog from "@radix-ui/react-dialog";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams, useSearch } from "@tanstack/react-router";
import {
  ArrowLeft,
  Crosshair,
  Download,
  Keyboard,
  LayoutTemplate,
  Maximize2,
  PanelTopClose,
  RotateCcw,
  Video,
} from "lucide-react";
import { useEffect, useId, useRef, useState } from "react";
import { flushSync } from "react-dom";
import { ErrorNote, Spinner } from "@/components/ui";
import { type AnalysisSearch, SessionAnalytics } from "@/features/analytics/SessionAnalytics";
import { playEvidence } from "@/features/player/clip";
import { EvidenceDetails } from "@/features/player/EvidenceDetails";
import { VideoStage } from "@/features/player/VideoStage";
import { Timeline } from "@/features/timeline/Timeline";
import { api } from "@/lib/api";
import { clock, fps as fpsOf, STATUS_LABEL, shortName } from "@/lib/format";
import { frameClock } from "@/lib/frameClock";
import type { PlayerId, Session } from "@/lib/types";
import { usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";
import { EstimatedIndividualAnalytics } from "./EstimatedIndividualAnalytics";
import { IndividualAnalytics } from "./IndividualAnalytics";
import { LiveFeed } from "./LiveFeed";
import { ParticipantRoster } from "./ParticipantRoster";
import { PlayerSelector } from "./PlayerSelector";
import { ReanalysisFeedback } from "./ReanalysisFeedback";
import { ExportTab } from "./tabs/ExportTab";
import { VisualObservations } from "./VisualObservations";

const TABS = [
  ["overview", "Overview"],
  ["moments", "Moments"],
  ["rallies", "Rallies"],
  ["shots", "Shots"],
  ["tactics", "Tactics"],
  ["court", "Court"],
  ["movement", "Movement"],
  ["h2h", "Head to head"],
  ["pair", "Your pair"],
  ["ask", "Ask"],
] as const;

type VideoMode = "standard" | "focus" | "collapsed";

export function SessionPage() {
  const navigate = useNavigate();
  const params = useParams({ strict: false }) as { sessionId?: string; matchId?: string };
  const sessionId = params.matchId ?? params.sessionId ?? "";
  const search = useSearch({ strict: false }) as AnalysisSearch;
  const live = useSession((s) => s.session);
  const open = useSession((s) => s.open);
  const close = useSession((s) => s.close);
  const q = useQuery({
    queryKey: ["session", sessionId],
    queryFn: () => api.session(sessionId),
    enabled: Boolean(sessionId),
  });
  useEffect(() => {
    open(sessionId);
    return () => close();
  }, [sessionId, open, close]);
  const session = live?.session_id === sessionId ? live : q.data;
  const reused = session?.meta.reused_session_id;
  const reusedSessionId = typeof reused === "string" && reused.trim() !== sessionId ? reused.trim() : "";
  useEffect(() => {
    if (reusedSessionId)
      void navigate({
        to: "/matches/$matchId",
        params: { matchId: reusedSessionId },
        search,
        replace: true,
      });
  }, [reusedSessionId, navigate, search]);
  if (reusedSessionId)
    return (
      <div className="grid h-64 place-items-center" role="status">
        <p className="flex items-center gap-3 text-sm text-line-2">
          <Spinner className="size-5" /> Opening saved analysis…
        </p>
      </div>
    );
  if (q.error && !session)
    return (
      <div className="match-workspace">
        <h1 className="text-2xl font-bold mb-4">We couldn't open that match</h1>
        <ErrorNote error={q.error} />
        <Link to="/matches" className="rally-action mt-4">
          See your matches
        </Link>
      </div>
    );
  if (!session)
    return (
      <div className="grid h-64 place-items-center">
        <Spinner className="size-6" />
      </div>
    );
  return <SessionWorkspace key={sessionId} session={session} search={search} />;
}

function SessionWorkspace({ session, search }: { session: Session; search: AnalysisSearch }) {
  const navigate = useNavigate();
  const [showExports, setShowExports] = useState(false);
  const [showQuality, setShowQuality] = useState(false);
  const [shortcuts, setShortcuts] = useState(false);
  const [videoMode, setVideoMode] = useState<VideoMode>("standard");
  const videoBodyId = useId();
  const modeTransition = useRef<{ skipTransition: () => void } | null>(null);
  const restoreControl = useRef<HTMLButtonElement>(null);
  const standardControl = useRef<HTMLButtonElement>(null);
  const previousVideoMode = useRef<VideoMode>("standard");
  const connection = useSession((s) => s.connection);
  const status = useSession((s) => s.status);
  const video = usePlayback((s) => s.video);
  const frame = usePlayback((s) => s.frame);
  const applied = useRef<number | null>(null);
  const [editing, setEditing] = useState(false);
  const fps = fpsOf(session.media);
  const nFrames = session.media?.n_frames ?? 0;
  const availablePlayers = session.players.filter((p) => p.player_id === "P1" || p.player_id === "P2");
  const selected: PlayerId =
    search.who && availablePlayers.some((p) => p.player_id === search.who)
      ? search.who
      : (availablePlayers[0]?.player_id ?? "P1");
  const tab = TABS.some(([id]) => id === search.tab) ? search.tab : "overview";
  const reanalyse = useMutation({ mutationFn: () => api.control(session.session_id, "reanalyse") });
  const changeVideoMode = (mode: VideoMode, animate = false) => {
    // Collapse only changes the workspace. The media node, source and evidence remain attached.
    if (mode === "collapsed") usePlayback.getState().video?.pause();
    if (mode === videoMode) return;
    modeTransition.current?.skipTransition();
    if (
      animate &&
      document.startViewTransition &&
      document.documentElement.dataset.reducedMotion !== "true" &&
      !window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches
    ) {
      const transition = document.startViewTransition(() => flushSync(() => setVideoMode(mode)));
      // A second mode action may skip an in-flight snapshot without affecting media playback.
      void transition.ready.catch(() => {});
      modeTransition.current = transition;
      return;
    }
    setVideoMode(mode);
  };
  const patch = (change: Partial<AnalysisSearch>) =>
    void navigate({
      to: ".",
      search: ((old: Record<string, unknown>) => ({ ...old, ...change })) as never,
      replace: true,
      resetScroll: false,
    });

  useEffect(() => {
    if (videoMode === "collapsed") restoreControl.current?.focus({ preventScroll: true });
    else if (previousVideoMode.current === "collapsed")
      standardControl.current?.focus({ preventScroll: true });
    previousVideoMode.current = videoMode;
  }, [videoMode]);

  useEffect(() => {
    usePlayback.getState().resetMedia();
    frameClock.publish(0);
    return () => usePlayback.getState().resetMedia();
  }, []);

  useEffect(() => {
    // A source-linked evidence action should always bring its recording back into view.
    const revealEvidence = () => setVideoMode((mode) => (mode === "collapsed" ? "standard" : mode));
    window.addEventListener("bai:play-clip", revealEvidence);
    return () => window.removeEventListener("bai:play-clip", revealEvidence);
  }, []);

  useEffect(() => {
    if (search.f == null) return;
    const requested = Math.max(0, Math.min(nFrames - 1, search.f ?? 0));
    if (!video || !session.media || applied.current === requested) return;
    const cue = () => {
      // A more recent evidence click while media loaded takes precedence over the arrival URL.
      if (!usePlayback.getState().selection) usePlayback.getState().seekFrame(requested, fps);
      applied.current = requested;
    };
    if (video.readyState >= 1) cue();
    else video.addEventListener("loadedmetadata", cue, { once: true });
    return () => video.removeEventListener("loadedmetadata", cue);
  }, [video, session.media, search.f, fps, nFrames]);

  useEffect(() => {
    const key = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement;
      if (event.key === "Escape" && videoMode === "focus" && !target.closest("[role=dialog]")) {
        event.preventDefault();
        setVideoMode("standard");
        standardControl.current?.focus({ preventScroll: true });
        return;
      }
      if (target.closest("input, textarea, select, button, a, [contenteditable=true]")) return;
      if (event.key === "?") {
        event.preventDefault();
        setShortcuts(true);
        return;
      }
      const player = usePlayback.getState();
      if (!player.video) return;
      if (event.code === "Space" || event.key.toLowerCase() === "k") {
        event.preventDefault();
        if (videoMode === "collapsed") setVideoMode("standard");
        if (player.video.paused) void player.video.play().catch(() => {});
        else player.video.pause();
      }
      if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
        event.preventDefault();
        if (videoMode === "collapsed") setVideoMode("standard");
        player.video.pause();
        const next =
          player.frame + (event.key === "ArrowLeft" ? -1 : 1) * (event.shiftKey ? Math.round(fps) : 1);
        player.seekFrame(Math.min(nFrames - 1, Math.max(0, next)), fps);
      }
      if (event.key.toLowerCase() === "j" || event.key.toLowerCase() === "l") {
        const events = useSession.getState().events.ofType("rally_end");
        const rally =
          event.key.toLowerCase() === "l"
            ? events.find((r) => r.frame_start > player.frame + 1)
            : events.filter((r) => r.frame_start < player.frame - 1).at(-1);
        if (rally) playEvidence(rally.frame_start, rally.frame_end, `Rally ${rally.payload.rally_no}`);
      }
      if (event.key.toLowerCase() === "f") {
        if (videoMode === "collapsed") flushSync(() => setVideoMode("standard"));
        void document.querySelector<HTMLElement>("[data-testid=video-stage]")?.requestFullscreen?.();
      }
    };
    window.addEventListener("keydown", key);
    return () => window.removeEventListener("keydown", key);
  }, [fps, nFrames, videoMode]);

  const busy = ["created", "ingesting", "ready_to_play", "analysing"].includes(session.status);
  const progress =
    nFrames > 0 ? Math.min(100, Math.max(0, ((session.frontier_frame + 1) / nFrames) * 100)) : null;
  return (
    <div className="match-workspace" data-video-mode={videoMode}>
      <div className="match-context" hidden={videoMode === "focus"}>
        <div className="match-back">
          <Link to="/matches" className="inline-flex min-h-9 items-center gap-2 text-sm text-line-2">
            <ArrowLeft className="size-4" aria-hidden />
            Your matches
          </Link>
        </div>
        <header className="match-heading">
          <div>
            <h1>{session.title}</h1>
            <p className="match-subtitle">
              {new Date(session.created_at).toLocaleDateString(undefined, {
                day: "numeric",
                month: "long",
                year: "numeric",
              })}{" "}
              · {availablePlayers.map((p) => shortName(session, p.player_id)).join(" vs ")}
            </p>
            <p className="match-subtitle">
              {STATUS_LABEL[session.status] ?? session.status}
              {busy && progress !== null ? ` · ${progress.toFixed(0)}% of source frames reached` : ""}
              {connection !== "open" ? " · reconnecting to analysis" : ""}
            </p>
          </div>
          <div className="match-actions">
            <button type="button" className="rally-action" onClick={() => setEditing(true)}>
              Edit match details
            </button>
            <button
              type="button"
              className="rally-action"
              aria-expanded={showQuality}
              aria-controls="recording-quality"
              onClick={() => setShowQuality((v) => !v)}
            >
              Recording & quality
            </button>
            <button type="button" className="rally-action" onClick={() => setShowExports((v) => !v)}>
              <Download className="size-4" aria-hidden />
              Export
            </button>
            <Link
              to="/sessions/$sessionId/calibrate"
              params={{ sessionId: session.session_id }}
              className="rally-action"
            >
              <Crosshair className="size-4" aria-hidden />
              Court
            </Link>
          </div>
        </header>
      </div>
      <ReanalysisFeedback
        accepted={reanalyse.isSuccess && !busy}
        sessionDetail={session.status_detail}
        liveDetail={status?.detail}
      />
      {session.status === "failed" && (
        <div role="alert" className="analysis-notice mt-5">
          <p className="font-semibold text-alert">This analysis stopped before completion</p>
          <p>
            {session.status_detail ??
              "The server recorded a processing failure. Any available measurements remain partial."}
          </p>
          <button
            type="button"
            className="rally-action mt-3"
            disabled={reanalyse.isPending}
            onClick={() => reanalyse.mutate()}
          >
            <RotateCcw className="size-4" aria-hidden />
            Retry analysis
          </button>
          <ErrorNote error={reanalyse.error} />
        </div>
      )}
      {busy && (
        <p role="status" className="analysis-notice mt-5">
          The video is being prepared or analysed. Recorded results appear as they arrive; the figures below
          are partial.{status?.rate_x ? ` Processing at ${status.rate_x.toFixed(1)}× real time.` : ""}
        </p>
      )}
      <div hidden={videoMode === "focus"}>
        {showQuality && (
          <section
            id="recording-quality"
            className="analysis-panel mt-5"
            aria-labelledby="recording-quality-heading"
          >
            <h2 id="recording-quality-heading">What this recording can tell us</h2>
            <dl className="mt-4 grid grid-cols-2 gap-4 text-sm">
              <div>
                <dt className="text-line-2">Source frames</dt>
                <dd>{nFrames ? nFrames.toLocaleString() : "Media not prepared"}</dd>
              </div>
              <div>
                <dt className="text-line-2">Analysed frames</dt>
                <dd>{session.analysed_frames.toLocaleString()}</dd>
              </div>
              <div>
                <dt className="text-line-2">Frame rate</dt>
                <dd>{session.media ? `${fps.toFixed(3)} fps` : "Unavailable"}</dd>
              </div>
              <div>
                <dt className="text-line-2">Identity capability</dt>
                <dd>Two court-side identities</dd>
              </div>
            </dl>
            <p className="analysis-panel-hint mt-4">
              Frame processing is not rally coverage or labelled detection accuracy. Shot labels are
              heuristic; placement uses receiver positions; measured distance can contain tracking jitter.
              Four-player doubles attribution requires additional identity evidence.
            </p>
            {session.status === "analysed" && (
              <div className="mt-5 border-t border-seam pt-4">
                <h3 className="font-medium">Apply court or format changes</h3>
                <p className="analysis-panel-hint mt-2">
                  This backs up saved results, then reprocesses the video with your current court calibration
                  and match format.
                </p>
                <button
                  type="button"
                  className="rally-action mt-3"
                  disabled={reanalyse.isPending}
                  onClick={() => reanalyse.mutate()}
                >
                  <RotateCcw className="size-4" aria-hidden />
                  {reanalyse.isPending ? "Requesting reanalysis…" : "Analyse again"}
                </button>
                <ErrorNote error={reanalyse.error} />
              </div>
            )}
          </section>
        )}
        {showExports && (
          <section className="analysis-panel mt-5">
            <h2>Take your evidence with you</h2>
            <div className="mt-4">
              <ExportTab session={session} />
            </div>
          </section>
        )}
      </div>
      <section
        className="match-video video-theme"
        data-match-player
        data-theme="dark"
        aria-label="Source recording"
      >
        <header className="video-workspace-header">
          <div className="video-workspace-label">
            <Video className="size-4" aria-hidden />
            <h2>Source recording</h2>
            <span className="video-workspace-status">
              {videoMode === "collapsed"
                ? `Paused at ${clock(frame, session.media, true)}`
                : videoMode === "focus"
                  ? "Focus view"
                  : "Video & evidence"}
            </span>
          </div>
          <fieldset className="video-mode-controls" aria-label="Video workspace mode">
            {videoMode === "collapsed" ? (
              <button
                ref={restoreControl}
                type="button"
                onClick={(event) => changeVideoMode("standard", event.detail > 0)}
                aria-controls={videoBodyId}
                aria-expanded="false"
              >
                <Maximize2 className="size-4" aria-hidden /> Restore video
              </button>
            ) : (
              <>
                <button
                  ref={standardControl}
                  type="button"
                  aria-pressed={videoMode === "standard"}
                  aria-controls={videoBodyId}
                  onClick={(event) => changeVideoMode("standard", event.detail > 0)}
                >
                  <LayoutTemplate className="size-4" aria-hidden /> Standard view
                </button>
                <button
                  type="button"
                  aria-pressed={videoMode === "focus"}
                  aria-controls={videoBodyId}
                  onClick={(event) => changeVideoMode("focus", event.detail > 0)}
                >
                  <Maximize2 className="size-4" aria-hidden /> Focus video
                </button>
                <button
                  type="button"
                  aria-controls={videoBodyId}
                  aria-expanded="true"
                  onClick={(event) => changeVideoMode("collapsed", event.detail > 0)}
                >
                  <PanelTopClose className="size-4" aria-hidden /> Collapse video
                </button>
              </>
            )}
          </fieldset>
        </header>
        <div id={videoBodyId} className="video-workspace-body" hidden={videoMode === "collapsed"}>
          <div className="match-video-stage">
            <VideoStage
              session={session}
              controlsVisible={videoMode !== "collapsed"}
              suspended={videoMode === "collapsed"}
            />
          </div>
          <div className="video-workspace-timeline">
            <Timeline session={session} />
          </div>
          <footer className="video-workspace-footer">
            <p>
              Source frame <span className="tabular">{frame.toLocaleString()}</span> · Select a moment to
              inspect its evidence
            </p>
            <button type="button" onClick={() => setShortcuts(true)}>
              <Keyboard className="size-4" aria-hidden /> Keyboard shortcuts
            </button>
          </footer>
        </div>
      </section>
      <EvidenceDetails session={session} />
      <div className="match-secondary" hidden={videoMode === "focus"}>
        <PlayerSelector session={session} selected={selected} onSelect={(who) => patch({ who })} />
        <nav className="match-tabs" aria-label="Match analysis">
          {TABS.map(([id, label]) => (
            <button
              type="button"
              key={id}
              aria-current={tab === id ? "page" : undefined}
              onClick={() => patch({ tab: id })}
            >
              {label}
            </button>
          ))}
        </nav>
        <div className="match-analysis">
          <SessionAnalytics
            key={`${session.session_id}-${selected}-${tab}`}
            session={session}
            player={selected}
            search={{ ...search, tab }}
          />
        </div>
        <div className="match-support">
          <ParticipantRoster key={`roster-${session.session_id}`} session={session} />
          <IndividualAnalytics session={session} />
          <EstimatedIndividualAnalytics session={session} />
          <VisualObservations session={session} />
          <details className="analysis-panel mt-5">
            <summary className="cursor-pointer text-sm font-medium">Live event feed</summary>
            <div className="mt-4 max-h-64 overflow-y-auto">
              <LiveFeed session={session} />
            </div>
          </details>
        </div>
      </div>
      <MetadataDialog session={session} open={editing} onOpenChange={setEditing} />
      <Dialog.Root open={shortcuts} onOpenChange={setShortcuts}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 z-50 bg-black/40" />
          <Dialog.Content className="panel fixed left-1/2 top-1/2 z-50 w-[min(440px,90vw)] -translate-x-1/2 -translate-y-1/2 p-6">
            <Dialog.Title className="text-xl font-semibold">Keyboard shortcuts</Dialog.Title>
            <Dialog.Description className="mt-2 text-sm text-line-2">
              Control the source video while focus is outside a form control.
            </Dialog.Description>
            <dl className="mt-5 grid grid-cols-2 gap-3 text-sm">
              <dt>Space / K</dt>
              <dd>Play or pause</dd>
              <dt>← / →</dt>
              <dd>One frame</dd>
              <dt>Shift + ← / →</dt>
              <dd>One second</dd>
              <dt>J / L</dt>
              <dd>Previous / next rally</dd>
              <dt>F</dt>
              <dd>Fullscreen</dd>
              <dt>Escape</dt>
              <dd>Close help or leave Focus view</dd>
            </dl>
            <Dialog.Close className="rally-action mt-6">Close</Dialog.Close>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </div>
  );
}

function MetadataDialog({
  session,
  open,
  onOpenChange,
}: {
  session: Session;
  open: boolean;
  onOpenChange: (value: boolean) => void;
}) {
  const qc = useQueryClient();
  const [title, setTitle] = useState(session.title);
  const [p1, setP1] = useState(session.players.find((p) => p.player_id === "P1")?.name ?? "");
  const [p2, setP2] = useState(session.players.find((p) => p.player_id === "P2")?.name ?? "");
  const save = useMutation({
    mutationFn: () =>
      api.patchSession(session.session_id, { title: title.trim(), player1: p1.trim(), player2: p2.trim() }),
    onSuccess: (updated) => {
      useSession.setState({ session: updated });
      void qc.invalidateQueries();
      onOpenChange(false);
    },
  });
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-black/40" />
        <Dialog.Content className="panel fixed left-1/2 top-1/2 z-50 w-[min(480px,90vw)] -translate-x-1/2 -translate-y-1/2 p-6">
          <Dialog.Title className="text-xl font-semibold">Match details</Dialog.Title>
          <Dialog.Description className="mt-2 text-sm text-line-2">
            Names are labels you supply. The people view groups recordings by these names.
          </Dialog.Description>
          <form
            className="mt-5 space-y-4"
            onSubmit={(e) => {
              e.preventDefault();
              save.mutate();
            }}
          >
            <label className="block text-sm">
              Title
              <input
                value={title}
                required
                maxLength={200}
                onChange={(e) => setTitle(e.target.value)}
                className="mt-2 block min-h-11 w-full rounded-lg border border-seam bg-stand px-3"
              />
            </label>
            <label className="block text-sm">
              P1 name
              <input
                value={p1}
                maxLength={100}
                onChange={(e) => setP1(e.target.value)}
                className="mt-2 block min-h-11 w-full rounded-lg border border-seam bg-stand px-3"
              />
            </label>
            <label className="block text-sm">
              P2 name
              <input
                value={p2}
                maxLength={100}
                onChange={(e) => setP2(e.target.value)}
                className="mt-2 block min-h-11 w-full rounded-lg border border-seam bg-stand px-3"
              />
            </label>
            <ErrorNote error={save.error} />
            <div className="flex justify-end gap-3">
              <Dialog.Close className="rally-action" type="button">
                Cancel
              </Dialog.Close>
              <button
                type="submit"
                disabled={save.isPending || !title.trim()}
                className="rally-action rally-action-primary"
              >
                {save.isPending ? "Saving…" : "Save details"}
              </button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
