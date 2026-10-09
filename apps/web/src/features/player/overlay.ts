import { COURT_LINES, NET, project } from "@/lib/court";
import type { EventLog } from "@/lib/events";
import type { TrackBuffer } from "@/lib/tracks";
import type { Calibration, PlayerId } from "@/lib/types";
import type { Layers } from "@/stores/playback";

const SKELETON: [number, number][] = [
  [5, 6],
  [5, 7],
  [7, 9],
  [6, 8],
  [8, 10],
  [5, 11],
  [6, 12],
  [11, 12],
  [11, 13],
  [13, 15],
  [12, 14],
  [14, 16],
];
const TRAIL = 14;

export interface OverlayCtx {
  canvas: HTMLCanvasElement;
  video: HTMLVideoElement;
  tracks: TrackBuffer;
  events: EventLog;
  calibration: Calibration | null;
  layers: Layers;
  colors: Record<PlayerId, string>;
  names: Record<PlayerId, string>;
}

/** Map video intrinsic pixels → canvas pixels for an object-fit: contain video. */
function viewport(video: HTMLVideoElement, canvas: HTMLCanvasElement) {
  const vw = video.videoWidth || 1280;
  const vh = video.videoHeight || 720;
  const cw = canvas.clientWidth;
  const ch = canvas.clientHeight;
  const s = Math.min(cw / vw, ch / vh);
  return { s, ox: (cw - vw * s) / 2, oy: (ch - vh * s) / 2 };
}

/** Draw every overlay layer for exactly `frame` (called from requestVideoFrameCallback). */
export function drawOverlay(o: OverlayCtx, frame: number): void {
  const { canvas, video, tracks, layers } = o;
  const dpr = window.devicePixelRatio || 1;
  const w = Math.round(canvas.clientWidth * dpr);
  const h = Math.round(canvas.clientHeight * dpr);
  if (canvas.width !== w || canvas.height !== h) {
    canvas.width = w;
    canvas.height = h;
  }
  const g = canvas.getContext("2d");
  if (!g) return;
  g.setTransform(1, 0, 0, 1, 0, 0);
  g.clearRect(0, 0, w, h);
  const { s, ox, oy } = viewport(video, canvas);
  g.setTransform(dpr * s, 0, 0, dpr * s, dpr * ox, dpr * oy);
  const px = 1 / s; // one CSS pixel in video units

  if (layers.court && o.calibration?.H) drawCourt(g, o.calibration.H, px);

  if (layers.players) {
    for (const pid of ["P1", "P2"] as PlayerId[]) {
      const p = tracks.player(pid, frame);
      if (!p) continue;
      const color = o.colors[pid];
      drawBrackets(g, p.bbox, color, px);
      if (layers.pose && p.kps) drawSkeleton(g, p.kps, color, px);
      if (layers.labels) drawLabel(g, p.bbox, o.names[pid], color, px);
    }
  }

  if (layers.shuttle) drawShuttle(g, tracks, frame, px);

  // contact flash: a ring at the contact point for ~6 frames after a hit
  for (const c of o.events.window(frame - 6, frame, ["contact"])) {
    const xy = c.payload.shuttle_xy as [number, number] | null;
    if (!xy) continue;
    const age = frame - c.frame_start;
    if (age < 0) continue;
    const color = c.actors.player_id ? o.colors[c.actors.player_id] : "#ffffff";
    g.strokeStyle = color;
    g.globalAlpha = Math.max(0, 1 - age / 7);
    g.lineWidth = 2.5 * px;
    g.beginPath();
    g.arc(xy[0], xy[1], (10 + age * 4) * px, 0, Math.PI * 2);
    g.stroke();
    g.globalAlpha = 1;
  }
}

function drawCourt(g: CanvasRenderingContext2D, H: number[][], px: number): void {
  g.strokeStyle = "rgba(232,239,234,0.38)";
  g.lineWidth = 1.25 * px;
  g.beginPath();
  for (const [a, b] of COURT_LINES) {
    const pa = project(H, a);
    const pb = project(H, b);
    g.moveTo(pa[0], pa[1]);
    g.lineTo(pb[0], pb[1]);
  }
  g.stroke();
  const [na, nb] = [project(H, NET[0]), project(H, NET[1])];
  g.strokeStyle = "rgba(232,239,234,0.6)";
  g.setLineDash([6 * px, 5 * px]);
  g.beginPath();
  g.moveTo(na[0], na[1]);
  g.lineTo(nb[0], nb[1]);
  g.stroke();
  g.setLineDash([]);
}

function drawBrackets(
  g: CanvasRenderingContext2D,
  b: [number, number, number, number],
  color: string,
  px: number,
) {
  const [x1, y1, x2, y2] = b;
  const L = Math.min(18 * px, (x2 - x1) / 3, (y2 - y1) / 4);
  g.strokeStyle = color;
  g.lineWidth = 2.25 * px;
  g.lineCap = "round";
  g.beginPath();
  for (const [cx, cy, dx, dy] of [
    [x1, y1, 1, 1],
    [x2, y1, -1, 1],
    [x1, y2, 1, -1],
    [x2, y2, -1, -1],
  ] as const) {
    g.moveTo(cx + dx * L, cy);
    g.lineTo(cx, cy);
    g.lineTo(cx, cy + dy * L);
  }
  g.stroke();
}

function drawSkeleton(g: CanvasRenderingContext2D, k: Float32Array, color: string, px: number) {
  g.strokeStyle = color;
  g.globalAlpha = 0.85;
  g.lineWidth = 1.75 * px;
  g.lineCap = "round";
  g.beginPath();
  for (const [a, b] of SKELETON) {
    if ((k[a * 3 + 2] ?? 0) < 0.3 || (k[b * 3 + 2] ?? 0) < 0.3) continue;
    g.moveTo(k[a * 3] as number, k[a * 3 + 1] as number);
    g.lineTo(k[b * 3] as number, k[b * 3 + 1] as number);
  }
  g.stroke();
  g.globalAlpha = 1;
}

function drawLabel(
  g: CanvasRenderingContext2D,
  b: [number, number, number, number],
  name: string,
  color: string,
  px: number,
) {
  const fs = 12 * px;
  g.font = `600 ${fs}px "Archivo Variable", system-ui, sans-serif`;
  const tw = g.measureText(name).width;
  const x = (b[0] + b[2]) / 2 - tw / 2 - 6 * px;
  const y = b[1] - 22 * px;
  g.fillStyle = "rgba(12,38,32,0.82)";
  roundRect(g, x, y, tw + 12 * px, fs + 8 * px, 5 * px);
  g.fill();
  g.fillStyle = color;
  g.fillRect(x, y + 3 * px, 2.5 * px, fs + 2 * px);
  g.fillStyle = "#e8efea";
  g.fillText(name, x + 7 * px, y + fs + 2 * px);
}

function drawShuttle(g: CanvasRenderingContext2D, tracks: TrackBuffer, frame: number, px: number) {
  const trail = tracks.trail(frame, TRAIL);
  if (!trail.length) return;
  // comet: tapered, fading segments; only connect consecutive frames (gaps stay gaps)
  for (let i = 1; i < trail.length; i++) {
    const a = trail[i - 1];
    const b = trail[i];
    if (!a || !b || b.f - a.f > 2) continue;
    const t = i / trail.length;
    g.strokeStyle = `rgba(255,255,255,${0.12 + 0.75 * t})`;
    g.lineWidth = (1 + 4 * t) * px;
    g.lineCap = "round";
    g.beginPath();
    g.moveTo(a.p.x, a.p.y);
    g.lineTo(b.p.x, b.p.y);
    g.stroke();
  }
  const head = trail[trail.length - 1];
  if (head && head.f >= frame - 1) {
    g.shadowColor = "rgba(255,255,255,0.9)";
    g.shadowBlur = 10 * px;
    g.fillStyle = "#ffffff";
    g.beginPath();
    g.arc(head.p.x, head.p.y, 4.5 * px, 0, Math.PI * 2);
    g.fill();
    g.shadowBlur = 0;
  }
}

function roundRect(g: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
  g.beginPath();
  g.moveTo(x + r, y);
  g.arcTo(x + w, y, x + w, y + h, r);
  g.arcTo(x + w, y + h, x, y + h, r);
  g.arcTo(x, y + h, x, y, r);
  g.arcTo(x, y, x + w, y, r);
  g.closePath();
}
