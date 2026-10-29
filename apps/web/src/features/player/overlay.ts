import { COURT_LINES, mul3, NET, project } from "@/lib/court";
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
  fps?: number;
  reviewBox?: { frame: number; trackId: number; bbox: [number, number, number, number] } | null;
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

  const view = tracks.view(frame);
  if (layers.court && o.calibration?.H) {
    // The calibration holds for one camera pose; the engine measures the court in every frame, so it is
    // drawn where it is *in this frame* — in other cameras' views too (dimmer: shown, not analysed) — and not
    // at all where no court is in view (close-ups, crowd).  Sessions analysed without camera tracking keep
    // the fixed court.
    const pose = tracks.tracksCamera ? tracks.camera(frame) : undefined;
    if (pose === undefined) drawCourt(g, o.calibration.H, px);
    else if (pose) drawCourt(g, mul3(pose, o.calibration.H), px, view?.view === "alt");
  }
  if (layers.labels && view) drawSceneChip(g, view.view, px, video.videoHeight || 720);

  if (layers.players || layers.pose) {
    for (const p of tracks.playersAt(frame)) {
      const color = p.playerId ? o.colors[p.playerId] : "#e8c46b";
      const carried = p.detectorMatched === false;
      g.globalAlpha = carried ? 0.65 : 1;
      if (carried) g.setLineDash([4 * px, 3 * px]);
      if (layers.players) drawBrackets(g, p.bbox, color, px);
      g.setLineDash([]);
      g.globalAlpha = 1;
      const pose = layers.pose
        ? tracks.displayPose(p, frame, Math.min(5, Math.floor((o.fps ?? 30) * 0.2)))
        : null;
      if (pose) drawSkeleton(g, pose.keypoints, color, px, pose.ageFrames > 0);
      const name = p.playerId ? o.names[p.playerId] : `Track ${p.track} · identity unassigned`;
      const qualification = `${carried ? " · tracked estimate" : ""}${pose?.ageFrames ? " · pose estimate" : ""}`;
      if (layers.labels) drawLabel(g, p.bbox, `${name}${qualification}`, color, px);
    }
  }

  if (o.reviewBox && o.reviewBox.frame === frame) {
    drawBrackets(g, o.reviewBox.bbox, "#ffdf51", px);
    drawLabel(g, o.reviewBox.bbox, `Review track ${o.reviewBox.trackId}`, "#ffdf51", px);
  }
  if (layers.shuttle) drawShuttle(g, tracks, frame, px);

  // contact flash: a ring at the contact point for ~6 frames after a hit
  for (const c of layers.shuttle ? o.events.window(frame - 6, frame, ["contact"]) : []) {
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

const SCENE_LABEL: Record<"main" | "alt" | "none", string> = {
  main: "Main camera · analysed",
  alt: "Other camera · not analysed",
  none: "No usable court view",
};

/** Which camera this frame comes from, so a gap in the overlays reads as "not this view", not as a failure. */
function drawSceneChip(g: CanvasRenderingContext2D, view: "main" | "alt" | "none", px: number, vh: number) {
  if (view === "main") return; // the normal case needs no label
  const fs = 11 * px;
  g.font = `600 ${fs}px "Archivo Variable", system-ui, sans-serif`;
  const text = SCENE_LABEL[view];
  const tw = g.measureText(text).width;
  const x = 12 * px;
  const y = vh - fs - 22 * px;
  g.fillStyle = "rgba(12,38,32,0.78)";
  roundRect(g, x, y, tw + 14 * px, fs + 10 * px, 6 * px);
  g.fill();
  g.fillStyle = view === "alt" ? "#e8c46b" : "#9fb3aa";
  g.fillText(text, x + 7 * px, y + fs + 3 * px);
}

function drawCourt(g: CanvasRenderingContext2D, H: number[][], px: number, other = false): void {
  g.strokeStyle = other ? "rgba(232,196,107,0.32)" : "rgba(232,239,234,0.38)";
  g.lineWidth = 1.25 * px;
  if (other) g.setLineDash([4 * px, 4 * px]);
  g.beginPath();
  for (const [a, b] of COURT_LINES) {
    const pa = project(H, a);
    const pb = project(H, b);
    g.moveTo(pa[0], pa[1]);
    g.lineTo(pb[0], pb[1]);
  }
  g.stroke();
  g.setLineDash([]);
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

function drawSkeleton(
  g: CanvasRenderingContext2D,
  k: Float32Array,
  color: string,
  px: number,
  estimated = false,
) {
  g.strokeStyle = color;
  g.globalAlpha = estimated ? 0.55 : 0.85;
  if (estimated) g.setLineDash([3 * px, 2 * px]);
  g.lineWidth = 1.75 * px;
  g.lineCap = "round";
  g.beginPath();
  for (const [a, b] of SKELETON) {
    if ((k[a * 3 + 2] ?? 0) < 0.3 || (k[b * 3 + 2] ?? 0) < 0.3) continue;
    g.moveTo(k[a * 3] as number, k[a * 3 + 1] as number);
    g.lineTo(k[b * 3] as number, k[b * 3 + 1] as number);
  }
  g.stroke();
  g.setLineDash([]);
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
    if (tracks.view(a.f)?.camera !== tracks.view(b.f)?.camera) continue;
    const t = i / trail.length;
    const confidence = Math.max(0.15, Math.min(1, Math.min(a.p.c, b.p.c)));
    g.strokeStyle = `rgba(255,255,255,${(0.12 + 0.75 * t) * confidence})`;
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
    if (head.p.c < 0.5) {
      g.strokeStyle = "#e8c46b";
      g.lineWidth = 1.5 * px;
      g.setLineDash([3 * px, 3 * px]);
      g.beginPath();
      g.arc(head.p.x, head.p.y, 9 * px, 0, Math.PI * 2);
      g.stroke();
      g.setLineDash([]);
    }
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
