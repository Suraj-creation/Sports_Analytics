import { useEffect, useMemo, useRef, useState } from "react";
import { prepareCanvas } from "@/features/court/geometry";
import { spriteStyle, useSprite } from "@/features/library/Thumb";
import { isJumpSmash, isSmash, rallies } from "@/features/session/derive";
import { clock, fps as fpsOf, PLAYER_HEX, shortName, strokeLabel } from "@/lib/format";
import { frameClock } from "@/lib/frameClock";
import type { PlayerId, Session } from "@/lib/types";
import { usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";

const DETAIL_S = 60;
const DETAIL_LEAD = 1 / 3; // playhead sits a third of the way into the detail window
const LABEL_W = 84;

const windowStartOf = (f: number, span: number) => Math.max(0, f - Math.round(span * DETAIL_LEAD));

function useWidth<T extends HTMLElement>() {
  const ref = useRef<T>(null);
  const [w, setW] = useState(600);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const ro = new ResizeObserver(([e]) => e && setW(Math.max(200, Math.floor(e.contentRect.width))));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  return [ref, w] as const;
}

/** Whole-match overview (rallies, games, analysis frontier) above a 60-second shot lane. */
export function Timeline({ session }: { session: Session }) {
  return (
    <div className="panel space-y-2 p-3">
      <Overview session={session} />
      <Detail session={session} />
    </div>
  );
}

function Overview({ session }: { session: Session }) {
  const [ref, width] = useWidth<HTMLDivElement>();
  const events = useSession((s) => s.events);
  const eventsVersion = useSession((s) => s.eventsVersion);
  const frontier = useSession((s) => s.session?.frontier_frame ?? 0);
  const status = useSession((s) => s.session?.status ?? session.status);
  const seekFrame = usePlayback((s) => s.seekFrame);
  const uiFrame = usePlayback((s) => s.frame);
  const n = Math.max(1, session.media?.n_frames ?? 1);
  const fps = fpsOf(session.media);
  const x = (f: number) => (f / n) * width;
  const playhead = useRef<SVGLineElement>(null);
  const [hover, setHover] = useState<number | null>(null);
  const dragging = useRef(false);
  const sprite = useSprite(session.session_id, status !== "ingesting" && status !== "created");

  // biome-ignore lint/correctness/useExhaustiveDependencies: eventsVersion signals mutation of the log
  const data = useMemo(
    () => ({
      rallies: rallies(events),
      games: events.ofType("game_end"),
      highlights: events.ofType("highlight"),
    }),
    [events, eventsVersion],
  );

  useEffect(
    () =>
      frameClock.subscribe((f) => {
        const el = playhead.current;
        if (el) {
          const px = String((f / n) * width);
          el.setAttribute("x1", px);
          el.setAttribute("x2", px);
        }
      }),
    [n, width],
  );

  const marks = useMemo(() => {
    const x = (f: number) => (f / n) * width;
    return (
      <>
        {data.rallies.map((r) => {
          const c = r.winner ? PLAYER_HEX[r.winner] : "#74877f";
          const band = r.end.band;
          return (
            <rect
              key={r.end.event_id}
              x={x(r.start)}
              y={12}
              width={Math.max(1.5, x(r.stop) - x(r.start))}
              height={14}
              rx={1.5}
              fill={band === "uncertain" || band === "unknown" ? "transparent" : c}
              fillOpacity={band === "confirmed" ? 0.9 : 0.45}
              stroke={band === "confirmed" ? "none" : c}
              strokeDasharray={band === "uncertain" || band === "unknown" ? "2 2" : undefined}
              strokeWidth={1}
            />
          );
        })}
        {data.games.map((g) => (
          <g key={g.event_id}>
            <line
              x1={x(g.frame_start)}
              x2={x(g.frame_start)}
              y1={6}
              y2={30}
              stroke="var(--color-line)"
              strokeWidth={1.5}
            />
          </g>
        ))}
        {data.highlights.map((h) => (
          <circle key={h.event_id} cx={x(h.frame_start)} cy={5} r={2.5} fill="var(--color-line)" />
        ))}
      </>
    );
  }, [data, width, n]);
  const frameAt = (clientX: number, el: Element) => {
    const r = el.getBoundingClientRect();
    return Math.max(0, Math.min(n - 1, Math.round(((clientX - r.left) / r.width) * n)));
  };
  const hoverRally =
    hover != null ? data.rallies.find((r) => hover >= r.start && hover <= r.stop) : undefined;
  const analysedTo = status === "analysed" ? n : frontier;

  return (
    <div ref={ref} className="relative">
      <div
        className="cursor-pointer touch-none select-none"
        role="slider"
        tabIndex={0}
        aria-label="Match timeline"
        aria-valuemin={0}
        aria-valuemax={n}
        aria-valuenow={uiFrame}
        aria-valuetext={clock(uiFrame, session.media)}
        onPointerDown={(e) => {
          dragging.current = true;
          (e.currentTarget as Element).setPointerCapture(e.pointerId);
          seekFrame(frameAt(e.clientX, e.currentTarget), fps);
        }}
        onPointerMove={(e) => {
          const f = frameAt(e.clientX, e.currentTarget);
          setHover(f);
          if (dragging.current) seekFrame(f, fps);
        }}
        onPointerUp={() => {
          dragging.current = false;
        }}
        onPointerLeave={() => setHover(null)}
        onKeyDown={(e) => {
          const d = e.key === "ArrowRight" ? 5 : e.key === "ArrowLeft" ? -5 : 0;
          if (d) {
            e.preventDefault();
            e.stopPropagation();
            seekFrame(Math.max(0, Math.min(n - 1, frameClock.frame + Math.round(d * fps))), fps);
          }
        }}
      >
        <svg width={width} height={34} className="block" aria-hidden>
          <rect x={0} y={10} width={width} height={18} rx={4} fill="var(--color-mat-deep)" />
          {/* analysed so far */}
          <rect
            x={0}
            y={30}
            width={x(analysedTo)}
            height={3}
            rx={1.5}
            fill="var(--color-signal)"
            opacity={0.85}
          />
          {marks}
          <line ref={playhead} x1={0} x2={0} y1={2} y2={34} stroke="var(--color-shuttle)" strokeWidth={2} />
        </svg>
      </div>

      {hover != null && (
        <div
          className="pointer-events-none absolute bottom-full z-20 mb-2 -translate-x-1/2 overflow-hidden rounded-lg border border-seam bg-stand shadow-xl shadow-black/40"
          style={{ left: Math.max(90, Math.min(width - 90, x(hover))) }}
        >
          {sprite.data && (
            <div
              className="h-[90px] w-[160px] bg-mat-deep"
              style={spriteStyle(session.session_id, sprite.data, hover / fps) ?? undefined}
            />
          )}
          <div className="space-y-0.5 px-2 py-1.5 text-xs">
            <p className="tabular font-medium">{clock(hover, session.media)}</p>
            {hoverRally && (
              <p className="text-line-2">
                Rally {hoverRally.no} · {hoverRally.end.payload.n_shots ?? 0} shots
                {hoverRally.winner && ` · ${shortName(session, hoverRally.winner)}`}
              </p>
            )}
            {hover > analysedTo && <p className="text-line-3">Not analysed yet</p>}
          </div>
        </div>
      )}
    </div>
  );
}

/** 60 s around the playhead: each player's shots on their own lane, smashes emphasised. */
function Detail({ session }: { session: Session }) {
  const [ref, width] = useWidth<HTMLDivElement>();
  const canvas = useRef<HTMLCanvasElement>(null);
  const events = useSession((s) => s.events);
  const frontier = useSession((s) => s.session?.frontier_frame ?? 0);
  const status = useSession((s) => s.session?.status ?? session.status);
  const seekFrame = usePlayback((s) => s.seekFrame);
  const fps = fpsOf(session.media);
  const n = session.media?.n_frames ?? 0;
  const span = Math.round(DETAIL_S * fps);
  const H = 72;
  const name1 = shortName(session, "P1");
  const name2 = shortName(session, "P2");
  const [tip, setTip] = useState<{ x: number; text: string } | null>(null);

  useEffect(() => {
    const c = canvas.current;
    if (!c) return;
    const plotW = width - LABEL_W;
    const lane: Record<PlayerId, number> = { P1: 22, P2: 46 };
    return frameClock.subscribe((f) => {
      const g = prepareCanvas(c, width, H);
      if (!g) return;
      const a = windowStartOf(f, span);
      const X = (fr: number) => LABEL_W + ((fr - a) / span) * plotW;
      g.font = '500 11px "Archivo Variable", system-ui, sans-serif';
      // lane labels
      const names: Record<PlayerId, string> = { P1: name1, P2: name2 };
      for (const pid of ["P1", "P2"] as PlayerId[]) {
        g.fillStyle = PLAYER_HEX[pid];
        g.fillRect(0, lane[pid] - 5, 3, 10);
        g.fillStyle = "#a9bab2";
        g.fillText(names[pid].slice(0, 11), 8, lane[pid] + 4);
        g.strokeStyle = "rgba(42,56,51,1)";
        g.beginPath();
        g.moveTo(LABEL_W, lane[pid] + 0.5);
        g.lineTo(Math.min(width, X(n)), lane[pid] + 0.5);
        g.stroke();
      }
      // time ticks every 5 s
      g.fillStyle = "#74877f";
      const step = Math.round(5 * fps);
      for (let t = Math.ceil(a / step) * step; t < Math.min(a + span, n); t += step) {
        const px = X(t);
        g.fillRect(px, 56, 1, 4);
        if ((t / step) % 2 === 0) g.fillText(clock(t, session.media), Math.max(LABEL_W, px - 10), 70);
      }
      // not-yet-analysed region
      const analysedTo = status === "analysed" ? n : frontier;
      if (analysedTo < a + span) {
        const px = Math.max(LABEL_W, X(analysedTo));
        g.fillStyle = "rgba(12,38,32,0.7)";
        g.fillRect(px, 8, width - px, 48);
      }
      // rallies as faint spans
      for (const r of events.window(a, a + span, ["rally_end"])) {
        const x0 = Math.max(LABEL_W, X(r.frame_start));
        const x1 = X(r.frame_end);
        g.fillStyle = "rgba(232,239,234,0.05)";
        g.fillRect(x0, 10, Math.max(1, x1 - x0), 44);
      }
      // shots
      for (const e of events.window(a, a + span, ["stroke"])) {
        const pid = e.actors.player_id as PlayerId | null;
        if (!pid) continue;
        const px = X(e.frame_start);
        if (px < LABEL_W) continue;
        const y = lane[pid];
        g.fillStyle = PLAYER_HEX[pid];
        g.globalAlpha = e.band === "confirmed" ? 1 : e.band === "probable" ? 0.75 : 0.45;
        if (isJumpSmash(e)) {
          g.beginPath();
          g.moveTo(px, y - 8);
          g.lineTo(px + 6, y);
          g.lineTo(px, y + 8);
          g.lineTo(px - 6, y);
          g.closePath();
          g.fill();
        } else if (isSmash(e)) {
          g.fillRect(px - 2, y - 8, 4, 16);
        } else {
          g.fillRect(px - 1, y - 5, 2, 10);
        }
        g.globalAlpha = 1;
      }
      // playhead
      g.fillStyle = "#ffffff";
      g.fillRect(X(f) - 1, 4, 2, 52);
    });
  }, [width, events, frontier, status, fps, span, n, session.media, name1, name2]);

  const frameAtX = (clientX: number, el: Element) => {
    const r = el.getBoundingClientRect();
    const px = clientX - r.left;
    if (px < LABEL_W) return null;
    return Math.max(
      0,
      Math.round(windowStartOf(frameClock.frame, span) + ((px - LABEL_W) / (r.width - LABEL_W)) * span),
    );
  };

  return (
    <div ref={ref} className="relative">
      <canvas
        ref={canvas}
        style={{ width, height: H }}
        className="block cursor-pointer"
        aria-label="Shots in the last minute, one lane per player"
        role="img"
        onClick={(e) => {
          const f = frameAtX(e.clientX, e.currentTarget);
          if (f != null) seekFrame(Math.min(n - 1, f), fps);
        }}
        onMouseMove={(e) => {
          const f = frameAtX(e.clientX, e.currentTarget);
          if (f == null) return setTip(null);
          const near = events.window(f - 6, f + 6, ["stroke"])[0];
          const r = e.currentTarget.getBoundingClientRect();
          setTip({
            x: e.clientX - r.left,
            text: near
              ? `${strokeLabel(near.payload)} · ${shortName(session, near.actors.player_id)} · ${clock(near.frame_start, session.media)}`
              : clock(f, session.media),
          });
        }}
        onMouseLeave={() => setTip(null)}
      />
      {tip && (
        <div
          className="pointer-events-none absolute bottom-full z-20 mb-1 -translate-x-1/2 rounded-md border border-seam bg-stand px-2 py-1 text-xs whitespace-nowrap shadow-lg"
          style={{ left: Math.max(80, Math.min(width - 80, tip.x)) }}
        >
          {tip.text}
        </div>
      )}
      <div className="mt-1 flex gap-4 pl-[84px] text-[11px] text-line-3">
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-0.5 bg-line-2" aria-hidden /> shot
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-3 w-1 bg-line-2" aria-hidden /> smash
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block size-2 rotate-45 bg-line-2" aria-hidden /> jump smash
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2 w-3 rounded-sm bg-mat-deep ring-1 ring-seam" aria-hidden /> not
          analysed yet
        </span>
      </div>
    </div>
  );
}
