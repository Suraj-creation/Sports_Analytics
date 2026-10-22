import * as Popover from "@radix-ui/react-popover";
import { clsx } from "clsx";
import {
  ChevronLeft,
  ChevronRight,
  Layers as LayersIcon,
  Maximize,
  Pause,
  Play,
  Repeat,
  RotateCcw,
  SkipBack,
  SkipForward,
  Volume2,
  VolumeX,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { Match, PlayerId, Rally } from "../data/types";
import { STROKE_LABEL } from "../data/types";
import { IconButton } from "../ui/primitives";
import { sceneAt } from "./scene";
import { type Layers, usePlayer } from "./store";

/* ─────────────────────────────────────────────────────────────────────────────
   The match player.

   Not a modal and not an overlay: it is the top of the match page and it stays there
   while you read. Every "watch" anywhere in the product seeks THIS player and plays —
   you never lose your place, and you never lose the controls.

   It carries the same control set as the production VideoStage (play/pause, frame step,
   speed, mute, overlay layers, fullscreen) plus a scrubber over the whole match with
   rally segments, game breaks and highlight markers.
   ───────────────────────────────────────────────────────────────────────────── */

// Camera geometry: a trapezoid, as seen from behind the near baseline.
const TOP_W = 0.3;
const BOT_W = 0.84;
const Y_TOP = 0.15;
const Y_BOT = 0.95;
const VB_W = 1000;
const VB_H = 562;

function proj(x: number, y: number): [number, number] {
  const w = TOP_W + (BOT_W - TOP_W) * y;
  return [(0.5 + (x - 0.5) * w) * VB_W, (Y_TOP + (Y_BOT - Y_TOP) * y) * VB_H];
}

function path(points: [number, number][]) {
  return `${points.map(([x, y], i) => `${i ? "L" : "M"}${x.toFixed(1)},${y.toFixed(1)}`).join("")}Z`;
}

const MARK_COLOUR: Record<string, string> = {
  you: "#4fd6c4",
  partner: "#e27bf2",
  "opponent-1": "#9aa7b2",
  "opponent-2": "#d7dee3",
};

export function MatchPlayer({ match, compact }: { match: Match; compact?: boolean }) {
  const { frame, playing, rate, muted, layers, cue, clip } = usePlayer();
  const setFrame = usePlayer((s) => s.setFrame);
  const toggle = usePlayer((s) => s.toggle);
  const pause = usePlayer((s) => s.pause);
  const seek = usePlayer((s) => s.seek);
  const stageRef = useRef<HTMLDivElement>(null);
  const raf = useRef(0);
  const last = useRef(0);

  const nFrames = match.nFrames;

  // ── the clock ──
  useEffect(() => {
    if (!playing) {
      last.current = 0;
      return;
    }
    const tick = (now: number) => {
      if (last.current) {
        const dt = (now - last.current) / 1000;
        const st = usePlayer.getState();
        const next = st.frame + dt * match.fps * rate;
        // A clip is bounded: it stops at its end, or starts again if looping.
        const stop = st.clip ? Math.min(st.clip.to, nFrames) : nFrames;
        if (next >= stop) {
          if (st.clip && st.loop) {
            st.setFrame(st.clip.from);
          } else {
            st.pause();
            st.setFrame(stop);
          }
        } else {
          st.setFrame(next);
        }
      }
      last.current = now;
      raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(raf.current);
      last.current = 0;
    };
  }, [playing, rate, match.fps, nFrames]);

  const scene = useMemo(() => sceneAt(match, frame), [match, frame]);

  const step = useCallback(
    (d: number) => {
      pause();
      setFrame(Math.max(0, Math.min(nFrames, frame + d)));
    },
    [frame, nFrames, pause, setFrame],
  );

  const jumpRally = useCallback(
    (dir: 1 | -1) => {
      const list = match.rallies;
      const idx = list.findIndex((r) => frame >= r.frames[0] && frame <= r.frames[1]);
      let target: Rally | undefined;
      if (dir === 1) {
        target = idx >= 0 ? list[idx + 1] : list.find((r) => r.frames[0] > frame);
      } else {
        const before = list.filter((r) => r.frames[0] < frame - 15);
        target = before[before.length - 1];
      }
      if (target) seek(target.frames[0], `Rally ${target.no}`);
    },
    [frame, match.rallies, seek],
  );

  // ── keyboard, the same map the production player uses ──
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const el = e.target as HTMLElement | null;
      if (el && /^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName)) return;
      if (el?.isContentEditable || e.metaKey || e.ctrlKey || e.altKey) return;
      switch (e.key) {
        case " ":
        case "k":
          e.preventDefault();
          toggle();
          break;
        case "ArrowLeft":
          e.preventDefault();
          step(e.shiftKey ? -match.fps : -1);
          break;
        case "ArrowRight":
          e.preventDefault();
          step(e.shiftKey ? match.fps : 1);
          break;
        case "j":
          jumpRally(-1);
          break;
        case "l":
          jumpRally(1);
          break;
        case "f":
          void stageRef.current?.requestFullscreen?.();
          break;
        default:
          break;
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [toggle, step, jumpRally, match.fps]);

  const nameOf = (id: PlayerId) => match.players.find((p) => p.id === id)?.short ?? id;
  const colourOf = (id: PlayerId) =>
    MARK_COLOUR[match.players.find((p) => p.id === id)?.colour ?? "opponent-1"] ?? "#9aa7b2";

  return (
    <div data-theme="dark" className="overflow-hidden rounded-[14px] border border-edge bg-well text-ink">
      {/* ── stage ── */}
      <div
        ref={stageRef}
        className="relative bg-black"
        style={{ aspectRatio: "16 / 9", maxHeight: compact ? "34vh" : "56vh" }}
      >
        <button
          type="button"
          onClick={toggle}
          onDoubleClick={() => void stageRef.current?.requestFullscreen?.()}
          aria-label={playing ? "Pause" : "Play"}
          className="absolute inset-0 size-full"
        >
          <svg viewBox={`0 0 ${VB_W} ${VB_H}`} className="size-full" aria-hidden>
            <rect width={VB_W} height={VB_H} fill="#05100d" />
            {/* floor */}
            <path d={path([proj(0, 0), proj(1, 0), proj(1, 1), proj(0, 1)])} fill="#14382f" />
            <path
              d={path([proj(-0.14, 0), proj(1.14, 0), proj(1.24, 1), proj(-0.24, 1)])}
              fill="#0f2b24"
              opacity="0.9"
            />
            <path d={path([proj(0, 0), proj(1, 0), proj(1, 1), proj(0, 1)])} fill="#14382f" />

            {layers.court && <CourtLines doubles={match.discipline === "doubles"} />}
            {layers.zones && <ZoneGrid />}

            {/* net */}
            <g>
              {(() => {
                const [lx, ly] = proj(-0.035, 0.5);
                const [rx] = proj(1.035, 0.5);
                const h = 46;
                return (
                  <>
                    {/* netting: a dark wash so the court behind still reads, then the mesh */}
                    <rect x={lx} y={ly - h} width={rx - lx} height={h} fill="#06120f" opacity="0.45" />
                    <rect x={lx} y={ly - h} width={rx - lx} height={h} fill="url(#netmesh)" />
                    {/* the white tape along the top, and the posts */}
                    <rect x={lx} y={ly - h - 3} width={rx - lx} height={4} fill="#e8efea" />
                    <line
                      x1={lx}
                      y1={ly + 2}
                      x2={rx}
                      y2={ly + 2}
                      stroke="#cfd8d4"
                      strokeWidth="1.5"
                      opacity="0.8"
                    />
                    <rect x={lx - 3} y={ly - h - 6} width={5} height={h + 8} fill="#cfd8d4" rx="1.5" />
                    <rect x={rx - 2} y={ly - h - 6} width={5} height={h + 8} fill="#cfd8d4" rx="1.5" />
                  </>
                );
              })()}
            </g>
            <defs>
              <pattern id="netmesh" width="6" height="6" patternUnits="userSpaceOnUse">
                <path d="M0 0H6M0 0V6" stroke="#e8efea" strokeWidth="0.6" opacity="0.38" />
              </pattern>
            </defs>

            {/* shuttle trail */}
            {layers.trail &&
              scene.shuttle &&
              scene.trail.map((t, i) => {
                const [x, y] = proj(t.x, t.y);
                return (
                  <circle
                    // biome-ignore lint/suspicious/noArrayIndexKey: the slot number is the trail point's identity
                    key={`trail-${i}`}
                    cx={x}
                    cy={y - 14}
                    r={3.2 - i * 0.3}
                    fill="#ffffff"
                    opacity={0.34 - i * 0.045}
                  />
                );
              })}

            {/* players */}
            {scene.marks.map((m) => {
              const [x, y] = proj(m.x, m.y);
              const scale = 0.52 + m.y * 0.85;
              const c = colourOf(m.id);
              const role = match.players.find((p) => p.id === m.id)?.colour ?? "opponent-1";
              return (
                <g key={m.id}>
                  <ellipse cx={x} cy={y + 4} rx={17 * scale} ry={5 * scale} fill="#000" opacity="0.4" />
                  {/* body */}
                  <rect
                    x={x - 7 * scale}
                    y={y - 42 * scale}
                    width={14 * scale}
                    height={38 * scale}
                    rx={7 * scale}
                    fill={c}
                    opacity="0.92"
                  />
                  <circle cx={x} cy={y - 48 * scale} r={7.5 * scale} fill={c} />
                  {/* identity: colour AND shape, on the name chip rather than floating */}
                  {layers.labels && (
                    <g>
                      <rect
                        x={x - 34}
                        y={y + 8 * scale}
                        width={68}
                        height={18}
                        rx={9}
                        fill="#05100d"
                        opacity="0.78"
                      />
                      <RoleMark role={role} x={x - 23} y={y + 17 * scale} s={0.78} c={c} />
                      <text x={x + 6} y={y + 21 * scale} textAnchor="middle" fontSize={12} fill="#e8efea">
                        {nameOf(m.id)}
                      </text>
                    </g>
                  )}
                  {layers.players && (
                    <circle
                      cx={x}
                      cy={y + 4}
                      r={20 * scale}
                      fill="none"
                      stroke={c}
                      strokeWidth="1.5"
                      strokeDasharray="3 4"
                      opacity="0.55"
                    />
                  )}
                </g>
              );
            })}

            {/* shuttle */}
            {layers.shuttle && scene.shuttle && (
              <g>
                {(() => {
                  const [x, y] = proj(scene.shuttle.x, scene.shuttle.y);
                  const lift = 16 + scene.shuttle.height * 90;
                  return (
                    <>
                      <ellipse cx={x} cy={y} rx="5" ry="2" fill="#000" opacity="0.35" />
                      <circle cx={x} cy={y - lift} r="5" fill="#fff" />
                      <path
                        d={`M${x - 4} ${y - lift - 2} L${x} ${y - lift - 12} L${x + 4} ${y - lift - 2} Z`}
                        fill="#fff"
                        opacity="0.85"
                      />
                    </>
                  );
                })()}
              </g>
            )}
          </svg>
        </button>

        {/* score bug */}
        {layers.scoreBug && (
          <div className="pointer-events-none absolute left-3 top-3 flex overflow-hidden rounded-[10px] border border-white/15 bg-black/70 text-sm backdrop-blur">
            {(["A", "B"] as const).map((side) => (
              <div key={side} className="flex items-center gap-2 px-3 py-1.5">
                <span className="max-w-[140px] truncate text-[#cfd8d4]">{match.sides[side].label}</span>
                <span className="numerals text-lg text-white">{scene.score[side]}</span>
              </div>
            ))}
            <div className="border-l border-white/15 px-3 py-1.5 text-xs text-[#9aa7b2]">
              Game {scene.score.game}
            </div>
          </div>
        )}

        {/* what you are looking at */}
        <div className="pointer-events-none absolute right-3 top-3 flex max-w-[52%] flex-col items-end gap-1.5 text-right">
          <span className="rounded bg-black/70 px-2 py-1 text-[11px] text-[#9aa7b2] backdrop-blur">
            <span className="hidden sm:inline">Reconstructed from the match data — </span>no footage in this
            prototype
          </span>
          {scene.rally && (
            <span className="rounded bg-black/70 px-2 py-1 text-xs text-[#e8efea] backdrop-blur">
              Rally {scene.rally.no}
              {!scene.rally.official && " · warm-up, not counted"}
              {scene.lastShot && (
                <>
                  {" · "}
                  {STROKE_LABEL[scene.lastShot.subtype ?? scene.lastShot.stroke]} by{" "}
                  {nameOf(scene.lastShot.player)}
                </>
              )}
            </span>
          )}
        </div>

        {cue && (
          <div className="pointer-events-none absolute inset-x-0 bottom-3 flex justify-center">
            <span className="rounded-full bg-black/80 px-3 py-1.5 text-xs text-[#e8efea] backdrop-blur">
              {cue}
            </span>
          </div>
        )}

        {!playing && (
          <span aria-hidden className="pointer-events-none absolute inset-0 flex items-center justify-center">
            <span className="flex size-16 items-center justify-center rounded-full bg-white/90">
              <Play className="size-7 translate-x-0.5 fill-[#05100d] text-[#05100d]" />
            </span>
          </span>
        )}
      </div>

      {clip && <ClipBar match={match} />}
      <Scrubber match={match} />
      <Controls
        match={match}
        onStep={step}
        onJumpRally={jumpRally}
        onFullscreen={() => void stageRef.current?.requestFullscreen?.()}
        playing={playing}
        muted={muted}
        rate={rate}
      />
    </div>
  );
}

function RoleMark({ role, x, y, s, c }: { role: string; x: number; y: number; s: number; c: string }) {
  const r = 6 * s;
  if (role === "you") return <circle cx={x} cy={y} r={r} fill={c} stroke="#05100d" strokeWidth={1.5} />;
  if (role === "partner")
    return (
      <path
        d={`M${x} ${y - r} L${x + r} ${y} L${x} ${y + r} L${x - r} ${y} Z`}
        fill={c}
        stroke="#05100d"
        strokeWidth={1.5}
      />
    );
  if (role === "opponent-2")
    return (
      <path
        d={`M${x} ${y - r} L${x + r} ${y + r} L${x - r} ${y + r} Z`}
        fill={c}
        stroke="#05100d"
        strokeWidth={1.5}
      />
    );
  return (
    <rect x={x - r} y={y - r} width={r * 2} height={r * 2} fill={c} stroke="#05100d" strokeWidth={1.5} />
  );
}

function CourtLines({ doubles }: { doubles: boolean }) {
  const L = "rgb(232 239 234 / 0.62)";
  const line = (x1: number, y1: number, x2: number, y2: number, w = 1.6, o = 1) => {
    const [ax, ay] = proj(x1, y1);
    const [bx, by] = proj(x2, y2);
    return <line x1={ax} y1={ay} x2={bx} y2={by} stroke={L} strokeWidth={w} opacity={o} />;
  };
  // 5.18 m singles inside 6.1 m doubles → sideline inset of 0.0755 either side.
  const si = 0.0755;
  return (
    <g>
      {/* outer (doubles) court */}
      <path
        d={path([proj(0, 0), proj(1, 0), proj(1, 1), proj(0, 1)])}
        fill="none"
        stroke={L}
        strokeWidth="2"
      />
      {/* singles sidelines */}
      {line(si, 0, si, 1, 1.4, doubles ? 0.55 : 1)}
      {line(1 - si, 0, 1 - si, 1, 1.4, doubles ? 0.55 : 1)}
      {/* short service lines (1.98 m from net) */}
      {line(0, 0.352, 1, 0.352)}
      {line(0, 0.648, 1, 0.648)}
      {/* long service line for doubles (0.76 m in from the baseline) */}
      {line(0, 0.057, 1, 0.057, 1.4, doubles ? 1 : 0.4)}
      {line(0, 0.943, 1, 0.943, 1.4, doubles ? 1 : 0.4)}
      {/* centre lines */}
      {line(0.5, 0, 0.5, 0.352)}
      {line(0.5, 0.648, 0.5, 1)}
    </g>
  );
}

/** The 3x3 analysis zones, off by default — this is the analyst's layer. */
function ZoneGrid() {
  const L = "rgb(79 214 196 / 0.35)";
  const seg = (x1: number, y1: number, x2: number, y2: number) => {
    const [ax, ay] = proj(x1, y1);
    const [bx, by] = proj(x2, y2);
    return <line x1={ax} y1={ay} x2={bx} y2={by} stroke={L} strokeWidth="1" strokeDasharray="5 5" />;
  };
  return (
    <g>
      {[0.145, 0.275, 0.725, 0.855].map((y) => (
        <g key={y}>{seg(0, y, 1, y)}</g>
      ))}
      {[0.333, 0.667].map((x) => (
        <g key={x}>{seg(x, 0, x, 1)}</g>
      ))}
    </g>
  );
}

/* ───────────────────────── scrubber ─────────────────────────
   The whole match on one track: rally segments, game breaks and the moments
   we picked out. Click anywhere to seek. */

function Scrubber({ match }: { match: Match }) {
  const frame = usePlayer((s) => s.frame);
  const seek = usePlayer((s) => s.seek);
  const clip = usePlayer((s) => s.clip);
  const [hover, setHover] = useState<{ x: number; rally: Rally | null } | null>(null);
  const ref = useRef<HTMLDivElement>(null);
  const n = match.nFrames;

  const pos = (f: number) => `${(f / n) * 100}%`;

  const fromEvent = (clientX: number) => {
    const r = ref.current?.getBoundingClientRect();
    if (!r) return 0;
    return Math.max(0, Math.min(n, ((clientX - r.left) / r.width) * n));
  };

  return (
    <div className="border-t border-edge px-3 pb-1.5 pt-2.5">
      <div
        ref={ref}
        className="relative h-9 cursor-pointer"
        onMouseMove={(e) => {
          const f = fromEvent(e.clientX);
          const rally = match.rallies.find((r) => f >= r.frames[0] && f <= r.frames[1]) ?? null;
          setHover({ x: (f / n) * 100, rally });
        }}
        onMouseLeave={() => setHover(null)}
        onClick={(e) => seek(fromEvent(e.clientX))}
        onKeyDown={(e) => {
          if (e.key === "Home") seek(0);
          if (e.key === "End") seek(n);
        }}
        role="slider"
        tabIndex={0}
        aria-label="Match position"
        aria-valuemin={0}
        aria-valuemax={Math.round(n)}
        aria-valuenow={Math.round(frame)}
      >
        {/* the bounded clip, if one is playing */}
        {clip && (
          <span
            aria-hidden
            className="absolute top-[14px] h-6 rounded-[3px] border border-[#f0b454] bg-[#f0b454]/20"
            style={{ left: pos(clip.from), width: `${((clip.to - clip.from) / n) * 100}%` }}
          />
        )}
        {/* game bands */}
        <div className="absolute inset-x-0 top-[18px] h-2.5 overflow-hidden rounded-full bg-[#0c2620]">
          {match.rallies.map((r) => (
            <span
              key={r.no}
              className={clsx("absolute top-0 h-full", r.official ? "bg-[#4fd6c4]" : "bg-[#5d6d68]")}
              style={{
                left: pos(r.frames[0]),
                width: `${((r.frames[1] - r.frames[0]) / n) * 100}%`,
                opacity: r.official ? 0.55 + Math.min(0.45, r.shots.length / 24) : 0.4,
              }}
            />
          ))}
        </div>
        {/* highlight markers */}
        {match.highlights.map((h) => (
          <button
            key={h.id}
            type="button"
            aria-label={`Jump to ${h.title}`}
            title={h.title}
            onClick={(e) => {
              e.stopPropagation();
              usePlayer.getState().playClip(h.frames[0], h.frames[1], h.title);
            }}
            className="absolute top-0 size-3 -translate-x-1/2 rotate-45 rounded-[2px] border border-[#05100d] bg-[#f0b454] transition-transform hover:scale-125"
            style={{ left: pos(h.frames[0]) }}
          />
        ))}
        {/* game dividers */}
        {match.scoreTimeline
          .filter((s, i, arr) => i > 0 && s.game !== arr[i - 1]?.game)
          .map((s) => (
            <span
              key={s.rallyNo}
              aria-hidden
              className="absolute top-[14px] h-5 w-px bg-[#e8efea]/60"
              style={{ left: pos(s.frame) }}
            />
          ))}
        {/* playhead */}
        <span
          aria-hidden
          className="absolute top-[12px] h-6 w-0.5 -translate-x-1/2 rounded-full bg-white"
          style={{ left: pos(frame) }}
        />
        {hover && (
          <span
            className="pointer-events-none absolute -top-7 z-10 -translate-x-1/2 whitespace-nowrap rounded border border-edge bg-surface px-2 py-0.5 text-[11px] text-ink"
            style={{ left: `${hover.x}%` }}
          >
            {hover.rally ? `Rally ${hover.rally.no} · ${hover.rally.shots.length} shots` : "Between rallies"}
          </span>
        )}
      </div>
      <div className="flex items-center gap-3 text-[11px] text-faint">
        <span className="flex items-center gap-1.5">
          <span aria-hidden className="h-2 w-4 rounded-full bg-[#4fd6c4]/70" /> rally (taller bar = longer)
        </span>
        <span className="flex items-center gap-1.5">
          <span aria-hidden className="size-2 rotate-45 rounded-[1px] bg-[#f0b454]" /> moment
        </span>
        <span className="flex items-center gap-1.5">
          <span aria-hidden className="h-3 w-px bg-[#e8efea]/60" /> game break
        </span>
      </div>
    </div>
  );
}

/* ───────────────────────── the clip bar ─────────────────────────
   When you click a moment you get a bounded passage, not the rest of the match.
   This bar says what you are watching, how long it is, and gives you the three
   things you actually want: again, on a loop, or carry on into the match. */

function ClipBar({ match }: { match: Match }) {
  const clip = usePlayer((s) => s.clip);
  const frame = usePlayer((s) => s.frame);
  const loop = usePlayer((s) => s.loop);
  const replay = usePlayer((s) => s.replayClip);
  const toggleLoop = usePlayer((s) => s.toggleLoop);
  const exitClip = usePlayer((s) => s.exitClip);
  if (!clip) return null;
  const len = (clip.to - clip.from) / match.fps;
  const done = Math.max(0, Math.min(1, (frame - clip.from) / Math.max(1, clip.to - clip.from)));

  return (
    <div className="flex flex-wrap items-center gap-2 border-t border-edge bg-[#f0b454]/10 px-3 py-2">
      <span className="flex min-w-0 items-center gap-2">
        <span aria-hidden className="size-2 shrink-0 rotate-45 rounded-[1px] bg-[#f0b454]" />
        <span className="truncate text-sm font-[600] text-ink">{clip.label}</span>
        <span className="tabular shrink-0 text-xs text-muted">{Math.round(len)}s clip</span>
      </span>
      <span aria-hidden className="h-1 min-w-[60px] flex-1 overflow-hidden rounded-full bg-[#0c2620]">
        <span className="block h-full bg-[#f0b454]" style={{ width: `${done * 100}%` }} />
      </span>
      <span className="flex shrink-0 items-center gap-1">
        <button
          type="button"
          onClick={replay}
          className="h-9 rounded-[10px] px-2.5 text-sm text-ink hover:bg-surface-raised"
        >
          <RotateCcw className="mr-1 inline size-3.5" aria-hidden />
          Again
        </button>
        <button
          type="button"
          onClick={toggleLoop}
          aria-pressed={loop}
          className={clsx(
            "h-9 rounded-[10px] px-2.5 text-sm",
            loop ? "bg-ink/15 text-ink" : "text-muted hover:bg-surface-raised hover:text-ink",
          )}
        >
          <Repeat className="mr-1 inline size-3.5" aria-hidden />
          Loop
        </button>
        <button
          type="button"
          onClick={exitClip}
          className="h-9 rounded-[10px] px-2.5 text-sm text-muted hover:bg-surface-raised hover:text-ink"
        >
          Watch on ›
        </button>
      </span>
    </div>
  );
}

/* ───────────────────────── controls ───────────────────────── */

const LAYER_LABEL: Record<keyof Layers, string> = {
  shuttle: "Shuttle",
  trail: "Shuttle trail",
  players: "Player markers",
  labels: "Name labels",
  court: "Court lines",
  scoreBug: "Score",
  zones: "Analysis zones",
};

function Controls({
  match,
  onStep,
  onJumpRally,
  onFullscreen,
  playing,
  muted,
  rate,
}: {
  match: Match;
  onStep: (d: number) => void;
  onJumpRally: (d: 1 | -1) => void;
  onFullscreen: () => void;
  playing: boolean;
  muted: boolean;
  rate: number;
}) {
  const frame = usePlayer((s) => s.frame);
  const toggle = usePlayer((s) => s.toggle);
  const setRate = usePlayer((s) => s.setRate);
  const toggleMute = usePlayer((s) => s.toggleMute);
  const layers = usePlayer((s) => s.layers);
  const toggleLayer = usePlayer((s) => s.toggleLayer);

  return (
    <div className="flex h-14 items-center gap-0.5 border-t border-edge px-2">
      <IconButton label={playing ? "Pause (Space)" : "Play (Space)"} onClick={toggle}>
        {playing ? <Pause className="size-5 fill-current" /> : <Play className="size-5 fill-current" />}
      </IconButton>
      <IconButton label="Previous rally (J)" onClick={() => onJumpRally(-1)}>
        <SkipBack className="size-4 fill-current" />
      </IconButton>
      <IconButton label="Previous frame (←)" onClick={() => onStep(-1)}>
        <ChevronLeft className="size-5" />
      </IconButton>
      <IconButton label="Next frame (→)" onClick={() => onStep(1)}>
        <ChevronRight className="size-5" />
      </IconButton>
      <IconButton label="Next rally (L)" onClick={() => onJumpRally(1)}>
        <SkipForward className="size-4 fill-current" />
      </IconButton>
      <span className="tabular ml-2 shrink-0 text-sm text-ink">
        {hms(frame, match.fps)}
        <span className="text-faint"> / {hms(match.nFrames, match.fps)}</span>
      </span>
      <span className="tabular ml-2 hidden shrink-0 text-xs text-faint lg:inline">
        frame {Math.round(frame).toLocaleString()}
      </span>

      <div className="ml-auto flex shrink-0 items-center gap-0.5">
        <label className="sr-only" htmlFor="rate">
          Playback speed
        </label>
        <select
          id="rate"
          value={rate}
          onChange={(e) => setRate(Number(e.target.value))}
          className="tabular h-10 rounded-[10px] border border-edge bg-surface px-2 text-sm text-ink"
        >
          {[0.25, 0.5, 1, 1.5, 2, 4].map((r) => (
            <option key={r} value={r}>
              {r}×
            </option>
          ))}
        </select>
        <IconButton label={muted ? "Unmute" : "Mute"} onClick={toggleMute}>
          {muted ? <VolumeX className="size-5" /> : <Volume2 className="size-5" />}
        </IconButton>
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
              data-theme="dark"
              className="z-50 w-64 rounded-[14px] border border-edge bg-surface p-2 text-ink shadow-[var(--shadow-pop)]"
            >
              <p className="px-2 pb-2 pt-1 text-xs text-faint">Show on the stage</p>
              {(Object.keys(LAYER_LABEL) as (keyof Layers)[]).map((k) => (
                <button
                  key={k}
                  type="button"
                  role="switch"
                  aria-checked={layers[k]}
                  onClick={() => toggleLayer(k)}
                  className="flex w-full items-center gap-3 rounded-[10px] px-2 py-2 text-left text-sm hover:bg-surface-raised"
                >
                  <span
                    aria-hidden
                    className={clsx(
                      "relative h-4 w-7 shrink-0 rounded-full transition-colors",
                      layers[k] ? "bg-live" : "bg-edge",
                    )}
                  >
                    <span
                      className={clsx(
                        "absolute top-0.5 size-3 rounded-full bg-well transition-transform",
                        layers[k] ? "translate-x-3.5" : "translate-x-0.5",
                      )}
                    />
                  </span>
                  {LAYER_LABEL[k]}
                </button>
              ))}
            </Popover.Content>
          </Popover.Portal>
        </Popover.Root>
        <IconButton label="Full screen (F)" onClick={onFullscreen}>
          <Maximize className="size-5" />
        </IconButton>
      </div>
    </div>
  );
}

export function hms(frame: number, fps: number): string {
  const t = Math.max(0, frame) / fps;
  const m = Math.floor(t / 60);
  const s = Math.floor(t % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}
