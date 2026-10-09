import * as Dialog from "@radix-ui/react-dialog";
import * as Tabs from "@radix-ui/react-tabs";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Link, useParams, useSearch } from "@tanstack/react-router";
import { clsx } from "clsx";
import { ArrowLeft, CircleAlert, Crosshair, Keyboard, RotateCcw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Button, ErrorNote, IconButton, Kbd, Spinner } from "@/components/ui";
import { CourtMinimap } from "@/features/court/CourtMinimap";
import { VideoStage } from "@/features/player/VideoStage";
import { Timeline } from "@/features/timeline/Timeline";
import { api } from "@/lib/api";
import { fps as fpsOf, playerName, STATUS_LABEL, shortName } from "@/lib/format";
import { frameClock } from "@/lib/frameClock";
import type { Session } from "@/lib/types";
import { usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";
import { currentRally, isSmash, rallies, stateAt } from "./derive";
import { LiveFeed } from "./LiveFeed";
import { AskTab } from "./tabs/AskTab";
import { ExportTab } from "./tabs/ExportTab";
import { HeatmapsTab } from "./tabs/HeatmapsTab";
import { HighlightsTab } from "./tabs/HighlightsTab";
import { RalliesTab } from "./tabs/RalliesTab";
import { StatsTab } from "./tabs/StatsTab";

const TABS = [
  { id: "stats", label: "Stats" },
  { id: "heatmaps", label: "Heatmaps" },
  { id: "highlights", label: "Highlights" },
  { id: "rallies", label: "Rallies" },
  { id: "ask", label: "Ask" },
  { id: "export", label: "Export" },
] as const;

export function SessionPage() {
  const { sessionId } = useParams({ from: "/sessions/$sessionId" });
  const search = useSearch({ from: "/sessions/$sessionId" });
  const open = useSession((s) => s.open);
  const close = useSession((s) => s.close);
  const live = useSession((s) => s.session);
  const initial = useQuery({ queryKey: ["session", sessionId], queryFn: () => api.session(sessionId) });

  useEffect(() => {
    open(sessionId);
    return () => close();
  }, [sessionId, open, close]);

  const session = live?.session_id === sessionId ? live : initial.data;
  if (initial.error && !session) {
    return (
      <div className="mx-auto max-w-md space-y-4 px-4 py-16 text-center">
        <ErrorNote error={initial.error} />
        <Link to="/" className="text-sm text-signal hover:underline">
          Back to the library
        </Link>
      </div>
    );
  }
  if (!session) {
    return (
      <div className="grid h-full place-items-center">
        <Spinner className="size-6" />
      </div>
    );
  }
  return <SessionView session={session} deepLinkFrame={search.f} />;
}

function SessionView({ session, deepLinkFrame }: { session: Session; deepLinkFrame?: number }) {
  const [tab, setTab] = useState<string>("stats");
  const [help, setHelp] = useState(false);
  useShortcuts(session, () => setHelp((h) => !h));
  useDeepLink(session, deepLinkFrame);

  return (
    <div className="mx-auto max-w-[1680px] space-y-4 px-4 py-4 sm:px-6">
      <Header session={session} onHelp={() => setHelp(true)} />
      <Banners session={session} />
      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(300px,360px)]">
        <div className="min-w-0 space-y-3">
          <div className="aspect-video max-h-[68vh] w-full">
            <VideoStage session={session} />
          </div>
          <Timeline session={session} />
          <RallyBar session={session} />
        </div>
        <aside className="flex min-w-0 flex-col gap-4 lg:max-h-[calc(68vh+220px)]">
          <section className="panel p-3" aria-labelledby="court-h">
            <h2 id="court-h" className="mb-2 text-sm font-semibold">
              Court
            </h2>
            <CourtMinimap session={session} />
          </section>
          <section
            className="panel flex min-h-[220px] flex-1 flex-col overflow-hidden"
            aria-labelledby="feed-h"
          >
            <h2 id="feed-h" className="px-3 pt-3 pb-2 text-sm font-semibold">
              Live feed
            </h2>
            <div className="min-h-0 flex-1 overflow-y-auto px-1 pb-2">
              <LiveFeed session={session} />
            </div>
          </section>
        </aside>
      </div>

      <Tabs.Root value={tab} onValueChange={setTab} className="panel">
        <Tabs.List
          className="flex gap-1 overflow-x-auto border-b border-seam px-2"
          aria-label="Match analysis"
        >
          {TABS.map((t) => (
            <Tabs.Trigger
              key={t.id}
              value={t.id}
              className={clsx(
                "relative h-11 shrink-0 px-3 text-sm text-line-2 transition-colors hover:text-line",
                "data-[state=active]:text-line data-[state=active]:after:absolute data-[state=active]:after:inset-x-3",
                "data-[state=active]:after:bottom-0 data-[state=active]:after:h-0.5 data-[state=active]:after:rounded-full",
                "data-[state=active]:after:bg-line",
              )}
            >
              {t.label}
            </Tabs.Trigger>
          ))}
        </Tabs.List>
        <div className="p-4">
          <Tabs.Content value="stats">
            <StatsTab session={session} />
          </Tabs.Content>
          <Tabs.Content value="heatmaps">
            <HeatmapsTab session={session} />
          </Tabs.Content>
          <Tabs.Content value="highlights">
            <HighlightsTab session={session} />
          </Tabs.Content>
          <Tabs.Content value="rallies">
            <RalliesTab session={session} />
          </Tabs.Content>
          <Tabs.Content value="ask" className="h-[520px]">
            <AskTab session={session} />
          </Tabs.Content>
          <Tabs.Content value="export">
            <ExportTab session={session} />
          </Tabs.Content>
        </div>
      </Tabs.Root>
      <ShortcutHelp open={help} onOpenChange={setHelp} />
    </div>
  );
}

function Header({ session, onHelp }: { session: Session; onHelp: () => void }) {
  const status = useSession((s) => s.status);
  const connection = useSession((s) => s.connection);
  const progress = useSession((s) => s.ingestProgress);
  const reanalyse = useMutation({ mutationFn: () => api.control(session.session_id, "reanalyse") });
  const n = session.media?.n_frames ?? 0;
  const pct = n ? Math.min(100, Math.round(((session.frontier_frame + 1) / n) * 100)) : 0;
  const busy = ["created", "ingesting", "analysing", "ready_to_play"].includes(session.status);

  return (
    <div className="flex flex-wrap items-center gap-3">
      <Link
        to="/"
        aria-label="Back to the library"
        className="grid size-9 place-items-center rounded-lg text-line-2 hover:bg-stand-raised hover:text-line"
      >
        <ArrowLeft className="size-5" />
      </Link>
      <div className="min-w-0">
        <h1 className="truncate text-lg font-semibold tracking-tight">{session.title}</h1>
        <p className="text-sm text-line-2">
          <span className="text-p1">●</span> {playerName(session, "P1")}{" "}
          <span className="text-line-3">vs</span> <span className="text-p2">●</span>{" "}
          {playerName(session, "P2")}
        </p>
      </div>
      <div className="ml-auto flex flex-wrap items-center gap-2">
        <span
          className={clsx(
            "inline-flex h-8 items-center gap-2 rounded-full border px-3 text-sm",
            session.status === "failed" ? "border-alert/50 text-alert" : "border-seam",
          )}
          role="status"
        >
          {busy && <span className="size-2 animate-pulse rounded-full bg-signal" aria-hidden />}
          {STATUS_LABEL[session.status] ?? session.status}
          {session.status === "ingesting" && progress != null && (
            <span className="tabular text-line-2">{Math.round(progress * 100)}%</span>
          )}
          {session.status === "analysing" && (
            <span className="tabular text-line-2">
              {pct}%{status?.rate_x ? ` · ${status.rate_x.toFixed(1)}× real time` : ""}
            </span>
          )}
        </span>
        {connection !== "open" && (
          <span className="inline-flex h-8 items-center gap-2 rounded-full border border-caution/50 px-3 text-sm text-caution">
            <Spinner className="size-3.5 text-caution" /> Reconnecting
          </span>
        )}
        <Link
          to="/sessions/$sessionId/calibrate"
          params={{ sessionId: session.session_id }}
          className="inline-flex h-8 items-center gap-2 rounded-lg border border-seam bg-stand-raised px-3 text-[13px] hover:border-line-3"
        >
          <Crosshair className="size-4" aria-hidden /> Calibrate court
        </Link>
        {(session.status === "analysed" || session.status === "failed") && (
          <Button size="sm" busy={reanalyse.isPending} onClick={() => reanalyse.mutate()}>
            <RotateCcw className="size-4" aria-hidden /> Analyse again
          </Button>
        )}
        <IconButton label="Keyboard shortcuts (?)" onClick={onHelp}>
          <Keyboard className="size-5" />
        </IconButton>
      </div>
    </div>
  );
}

function Banners({ session }: { session: Session }) {
  const status = useSession((s) => s.status);
  const calibrated = useSession((s) => s.calibration != null);
  const degraded = status?.degraded ?? [];
  const analysingLong = session.status === "analysing" && session.frontier_frame > 30 * fpsOf(session.media);
  return (
    <>
      {session.status === "failed" && session.status_detail && (
        <Banner tone="alert">
          {session.status_detail}. Fix the cause (see the server log), then choose “Analyse again”.
        </Banner>
      )}
      {!calibrated && analysingLong && (
        <Banner tone="caution">
          The court wasn't found automatically, so positions, heatmaps and in/out calls are off.{" "}
          <Link
            to="/sessions/$sessionId/calibrate"
            params={{ sessionId: session.session_id }}
            className="font-medium underline underline-offset-4"
          >
            Calibrate the court
          </Link>{" "}
          — it takes about a minute.
        </Banner>
      )}
      {degraded.length > 0 && (
        <Banner tone="caution">
          Running with reduced analysis: {degraded.map((d) => `${d.stage} (${d.reason})`).join("; ")}.
        </Banner>
      )}
    </>
  );
}

function Banner({ tone, children }: { tone: "alert" | "caution"; children: React.ReactNode }) {
  return (
    <p
      role={tone === "alert" ? "alert" : "status"}
      className={clsx(
        "flex gap-2 rounded-lg border px-3 py-2 text-sm",
        tone === "alert" ? "border-alert/40 bg-alert/10" : "border-caution/40 bg-caution/10",
      )}
    >
      <CircleAlert
        className={clsx("mt-0.5 size-4 shrink-0", tone === "alert" ? "text-alert" : "text-caution")}
        aria-hidden
      />
      <span>{children}</span>
    </p>
  );
}

/** "Rally 47 · 9 shots · P1 serving from the right" — the context line under the timeline. */
function RallyBar({ session }: { session: Session }) {
  const frame = usePlayback((s) => s.frame);
  const events = useSession((s) => s.events);
  const v = useSession((s) => s.eventsVersion);
  // biome-ignore lint/correctness/useExhaustiveDependencies: v signals mutation of the log
  const info = useMemo(() => {
    const r = currentRally(events, frame);
    const { state, known } = stateAt(events, frame);
    const shots = r
      ? events.window(r.start, frame, ["stroke"]).filter((e) => e.frame_start <= frame).length
      : 0;
    return { r, state, known, shots };
  }, [events, v, frame]);
  const { r, state, known, shots } = info;
  return (
    <p className="flex flex-wrap items-center gap-x-3 gap-y-1 px-1 text-sm text-line-2" aria-live="off">
      {r ? (
        <span className="font-medium text-line">
          {r.end ? `Rally ${r.end.payload.rally_no}` : `Rally ${state.rally_no + 1} in play`} · {shots} shot
          {shots === 1 ? "" : "s"}
        </span>
      ) : (
        <span>Between rallies</span>
      )}
      {known && (
        <span>
          {shortName(session, state.server)} serving from the {state.service_court}
        </span>
      )}
      {known && (
        <span className="tabular">
          Game {state.game_no} · {state.score.P1}–{state.score.P2}
        </span>
      )}
    </p>
  );
}

function useDeepLink(session: Session, f?: number) {
  const video = usePlayback((s) => s.video);
  const seekFrame = usePlayback((s) => s.seekFrame);
  useEffect(() => {
    if (!video || f == null) return;
    const go = () => seekFrame(f, fpsOf(session.media));
    if (video.readyState >= 1) go();
    else video.addEventListener("loadedmetadata", go, { once: true });
    return () => video.removeEventListener("loadedmetadata", go);
  }, [video, f, seekFrame, session.media]);
}

function useShortcuts(session: Session, toggleHelp: () => void) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement | null;
      if (t && (t.isContentEditable || ["INPUT", "TEXTAREA", "SELECT"].includes(t.tagName))) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      const { video, seekFrame } = usePlayback.getState();
      const { events } = useSession.getState();
      const fps = fpsOf(session.media);
      const n = session.media?.n_frames ?? 0;
      const f = frameClock.frame;
      const clamp = (x: number) => Math.max(0, Math.min(n - 1, x));
      const seek = (x: number) => seekFrame(clamp(x), fps);
      const k = e.key;
      let handled = true;
      if (k === " " || k === "k" || k === "K") {
        if (!video) return;
        if (video.paused) void video.play().catch(() => {});
        else video.pause();
      } else if (k === "ArrowLeft" || k === "ArrowRight") {
        const d = k === "ArrowLeft" ? -1 : 1;
        if (e.shiftKey) seek(f + d * Math.round(5 * fps));
        else {
          video?.pause();
          seek(f + d);
        }
      } else if (k === "j" || k === "J") seek(f - Math.round(10 * fps));
      else if (k === "l" || k === "L") seek(f + Math.round(10 * fps));
      else if (k === "[" || k === "]") {
        const rs = rallies(events);
        const target =
          k === "]"
            ? rs.find((r) => r.start > f + 2)
            : [...rs].reverse().find((r) => r.start < f - Math.round(fps));
        if (target) seek(target.start - Math.round(fps));
      } else if (k === "s" || k === "S") {
        const next = events.ofType("stroke").find((ev) => isSmash(ev) && ev.frame_start > f + 2);
        if (next) seek(next.frame_start - Math.round(1.5 * fps));
      } else if (k === ".") window.dispatchEvent(new Event("bai:toggle-overlays"));
      else if (k === "?") toggleHelp();
      else handled = false;
      if (handled) e.preventDefault();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [session.media, toggleHelp]);
}

const SHORTCUTS: [string[], string][] = [
  [["Space"], "Play / pause"],
  [["←", "→"], "Previous / next frame"],
  [["Shift", "← →"], "Back / forward 5 seconds"],
  [["J", "L"], "Back / forward 10 seconds"],
  [["[", "]"], "Previous / next rally"],
  [["S"], "Next smash"],
  [["."], "Hide or show all overlays"],
  [["?"], "This list"],
];

function ShortcutHelp({ open, onOpenChange }: { open: boolean; onOpenChange: (o: boolean) => void }) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-black/60" />
        <Dialog.Content className="panel fixed top-1/2 left-1/2 z-50 w-[min(92vw,380px)] -translate-x-1/2 -translate-y-1/2 p-5">
          <Dialog.Title className="mb-3 font-semibold">Keyboard shortcuts</Dialog.Title>
          <Dialog.Description className="sr-only">
            Keys for controlling playback and navigation
          </Dialog.Description>
          <dl className="space-y-2 text-sm">
            {SHORTCUTS.map(([keys, what]) => (
              <div key={what} className="flex items-center justify-between gap-4">
                <dt className="flex gap-1">
                  {keys.map((x) => (
                    <Kbd key={x}>{x}</Kbd>
                  ))}
                </dt>
                <dd className="text-line-2">{what}</dd>
              </div>
            ))}
          </dl>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
