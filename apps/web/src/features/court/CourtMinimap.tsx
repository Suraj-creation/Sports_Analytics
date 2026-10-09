import { useEffect, useRef, useState } from "react";
import { currentRally } from "@/features/session/derive";
import { fps as fpsOf, PLAYER_HEX, shortName } from "@/lib/format";
import { frameClock } from "@/lib/frameClock";
import type { BaiEvent, PlayerId, Session } from "@/lib/types";
import { useSession } from "@/stores/session";
import { CourtView, prepareCanvas } from "./geometry";

const TRAIL_S = 1.6;

/**
 * The bold element: a live top-down court, frame-synced to the video. Player dots carry a
 * short movement trail; the rally's shots are drawn hitter → hitter, and the shot in flight is
 * an arrow to where the receiver plays it. (The airborne shuttle itself is not projected:
 * a single camera can't place it on the floor until it lands.)
 */
export function CourtMinimap({ session }: { session: Session }) {
  const wrap = useRef<HTMLDivElement>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  const [width, setWidth] = useState(320);
  const tracks = useSession((s) => s.tracks);
  const events = useSession((s) => s.events);
  const calibrated = useSession((s) => s.calibration != null);
  const fps = fpsOf(session.media);

  useEffect(() => {
    const el = wrap.current;
    if (!el) return;
    const ro = new ResizeObserver(([e]) => e && setWidth(Math.max(200, Math.floor(e.contentRect.width))));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    const c = canvas.current;
    if (!c) return;
    const view = new CourtView(width);
    return frameClock.subscribe((frame) => {
      const g = prepareCanvas(c, view.width, view.height);
      if (!g) return;
      view.drawCourt(g);

      // shots of the current rally up to this frame
      const rally = currentRally(events, frame);
      if (rally) {
        const shots = events
          .window(rally.start, frame, ["stroke"])
          .filter((e) => e.frame_start <= frame && e.payload.hitter_court_xy);
        drawShots(g, view, shots);
      }

      // players: trail + dot
      for (const pid of ["P1", "P2"] as PlayerId[]) {
        const trail = tracks.playerCourtTrail(pid, frame, Math.round(TRAIL_S * fps), 3);
        const color = PLAYER_HEX[pid];
        if (trail.length > 1) {
          for (let i = 1; i < trail.length; i++) {
            const a = trail[i - 1] as [number, number];
            const b = trail[i] as [number, number];
            const pa = view.map(a[0], a[1]);
            const pb = view.map(b[0], b[1]);
            g.strokeStyle = color;
            g.globalAlpha = 0.1 + (0.5 * i) / trail.length;
            g.lineWidth = 2;
            g.lineCap = "round";
            g.beginPath();
            g.moveTo(pa[0], pa[1]);
            g.lineTo(pb[0], pb[1]);
            g.stroke();
          }
          g.globalAlpha = 1;
        }
        const now = tracks.player(pid, frame, 6)?.court;
        if (now) {
          const [x, y] = view.map(now[0], now[1]);
          g.fillStyle = "#0c2620";
          g.beginPath();
          g.arc(x, y, 8, 0, Math.PI * 2);
          g.fill();
          g.fillStyle = color;
          g.beginPath();
          g.arc(x, y, 6, 0, Math.PI * 2);
          g.fill();
        }
      }
    });
  }, [width, tracks, events, fps]);

  return (
    <div ref={wrap} className="space-y-2">
      <div className="flex items-baseline justify-between text-xs text-line-3">
        <span className="flex items-center gap-1.5">
          <span className="size-2 rounded-full bg-p1" aria-hidden />
          {shortName(session, "P1")}
          <span className="ml-2 size-2 rounded-full bg-p2" aria-hidden />
          {shortName(session, "P2")}
        </span>
        <span>near end ← → far end</span>
      </div>
      <canvas
        ref={canvas}
        style={{ width, height: new CourtView(width).height }}
        className="block rounded-lg"
        role="img"
        aria-label="Top-down court with player positions and the shots of the current rally"
      />
      {!calibrated && <p className="text-xs text-line-3">Positions appear once the court is calibrated.</p>}
    </div>
  );
}

function drawShots(g: CanvasRenderingContext2D, view: CourtView, shots: BaiEvent[]) {
  // the rally's path: hitter to hitter, fading toward older shots
  for (let i = 0; i < shots.length; i++) {
    const s = shots[i] as BaiEvent;
    const [x, y] = view.map(...(s.payload.hitter_court_xy as [number, number]));
    const pid = s.actors.player_id as PlayerId | null;
    const color = pid ? PLAYER_HEX[pid] : "#a9bab2";
    const age = shots.length - 1 - i;
    g.globalAlpha = Math.max(0.25, 1 - age * 0.15);
    const next = shots[i + 1];
    if (next) {
      const [nx, ny] = view.map(...(next.payload.hitter_court_xy as [number, number]));
      g.strokeStyle = "rgba(255,255,255,0.35)";
      g.lineWidth = 1;
      g.setLineDash([3, 3]);
      g.beginPath();
      g.moveTo(x, y);
      g.lineTo(nx, ny);
      g.stroke();
      g.setLineDash([]);
    }
    g.fillStyle = color;
    g.beginPath();
    g.arc(x, y, s.payload.stroke === "smash" ? 3.5 : 2.5, 0, Math.PI * 2);
    g.fill();
  }
  g.globalAlpha = 1;
  // the shot in flight: arrow from the latest hitter to where it's played back / lands
  const last = shots[shots.length - 1];
  const land = last?.payload.landing_court_xy as [number, number] | null | undefined;
  if (last && land) {
    const [x0, y0] = view.map(...(last.payload.hitter_court_xy as [number, number]));
    const [x1, y1] = view.map(land[0], land[1]);
    arrow(g, x0, y0, x1, y1, "#ffffff");
  }
}

function arrow(g: CanvasRenderingContext2D, x0: number, y0: number, x1: number, y1: number, color: string) {
  const a = Math.atan2(y1 - y0, x1 - x0);
  const L = Math.hypot(x1 - x0, y1 - y0);
  if (L < 4) return;
  g.strokeStyle = color;
  g.fillStyle = color;
  g.lineWidth = 2;
  g.beginPath();
  g.moveTo(x0, y0);
  g.lineTo(x1 - 6 * Math.cos(a), y1 - 6 * Math.sin(a));
  g.stroke();
  g.beginPath();
  g.moveTo(x1, y1);
  g.lineTo(x1 - 8 * Math.cos(a - 0.45), y1 - 8 * Math.sin(a - 0.45));
  g.lineTo(x1 - 8 * Math.cos(a + 0.45), y1 - 8 * Math.sin(a + 0.45));
  g.closePath();
  g.fill();
}
