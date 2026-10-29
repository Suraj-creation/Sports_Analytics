import type { PlayerId } from "./types";

/** Decoded columnar track window (see engine/src/bai_engine/wire.py). */
interface WirePlayer {
  f: number[];
  t: number[];
  b: number[];
  k: number[];
  cx: (number | null)[];
  cy: (number | null)[];
  c?: number[];
  obs?: (string | null)[];
  d?: (boolean | null)[];
  m?: (boolean | null)[];
  raw?: (number | null)[];
  method?: (string | null)[];
}

interface WireWindow {
  v: number;
  from: number;
  to: number;
  shuttle: { f: number[]; x: number[]; y: number[]; c: number[] };
  players: Record<string, WirePlayer>;
  anonymous?: Record<string, WirePlayer>;
  /** camera pose per frame: 3×3 row-major, reference px → frame px; all zeros = court not in view.
   *  `h`: physical camera (0 = main, analysed; -1 = no court); `q`: court-line fit precision */
  cam?: { f: number[]; g: number[]; h?: number[]; q?: (number | null)[] };
}

/** What the camera shows at a frame. */
export interface CameraView {
  /** main: the analysed camera; alt: another camera (court drawn, not analysed); none: no court in view */
  view: "main" | "alt" | "none";
  camera: number;
  quality: number | null;
}

export interface ShuttlePoint {
  x: number;
  y: number;
  c: number;
}

export interface PlayerFrame {
  bbox: [number, number, number, number];
  kps: Float32Array | null; // 17 × (x, y, score)
  court: [number, number] | null;
  track: number;
  playerId: PlayerId | null;
  observationId: string | null;
  confidence: number | null;
  detectorObserved: boolean | null;
  detectorMatched: boolean | null;
  rawTrack: number | null;
  identityMethod: string | null;
}

export interface DisplayPose {
  keypoints: Float32Array;
  observedFrame: number;
  ageFrames: number;
}

function playerFrame(p: WirePlayer, i: number, playerId: PlayerId | null): PlayerFrame {
  const k = p.k.slice(i * 51, i * 51 + 51);
  const cx = p.cx[i];
  const cy = p.cy[i];
  return {
    bbox: p.b.slice(i * 4, i * 4 + 4) as PlayerFrame["bbox"],
    kps: k.length === 51 && k.some((v) => v !== 0) ? Float32Array.from(k) : null,
    court: cx != null && cy != null ? [cx, cy] : null,
    track: p.t[i] as number,
    playerId,
    observationId: p.obs?.[i] ?? null,
    confidence: p.c?.[i] ?? null,
    detectorObserved: p.d?.[i] ?? null,
    detectorMatched: p.m?.[i] ?? null,
    rawTrack: p.raw?.[i] ?? null,
    identityMethod: p.method?.[i] ?? null,
  };
}

/**
 * Frame-indexed store of everything the overlay draws. Mutable on purpose: the canvas reads
 * it every video frame, React never re-renders on track arrival (only `version` bumps).
 */
export class TrackBuffer {
  readonly shuttle = new Map<number, ShuttlePoint>();
  readonly players: Record<PlayerId, Map<number, PlayerFrame>> = { P1: new Map(), P2: new Map() };
  readonly anonymous = new Map<string, Map<number, PlayerFrame>>();
  /** per-frame camera pose (null: tracked, but the court is not in view); empty when the camera is untracked */
  private readonly cams = new Map<number, number[][] | null>();
  private readonly views = new Map<number, CameraView>();
  /** true once any camera pose has arrived: the overlay then follows the camera instead of a fixed court */
  tracksCamera = false;
  /** frame ranges known to be analysed (so "no shuttle" means invisible, not "not yet analysed") */
  private covered: [number, number][] = [];
  version = 0;

  ingest(win: WireWindow): void {
    // a window replaces whatever we had for its range (refinement revisions arrive this way)
    for (let f = win.from; f <= win.to; f++) {
      this.shuttle.delete(f);
    }
    const s = win.shuttle;
    for (let i = 0; i < s.f.length; i++) {
      const f = s.f[i] as number;
      this.shuttle.set(f, { x: s.x[i] as number, y: s.y[i] as number, c: s.c[i] as number });
    }
    for (const pid of ["P1", "P2"] as PlayerId[]) {
      const p = win.players[pid];
      const map = this.players[pid];
      for (let f = win.from; f <= win.to; f++) map.delete(f);
      if (!p) continue;
      for (let i = 0; i < p.f.length; i++) {
        map.set(p.f[i] as number, playerFrame(p, i, pid));
      }
    }
    for (const [key, map] of this.anonymous) {
      for (let f = win.from; f <= win.to; f++) map.delete(f);
      if (!map.size) this.anonymous.delete(key);
    }
    for (const [key, p] of Object.entries(win.anonymous ?? {})) {
      const map = this.anonymous.get(key) ?? new Map<number, PlayerFrame>();
      for (let i = 0; i < p.f.length; i++) map.set(p.f[i] as number, playerFrame(p, i, null));
      this.anonymous.set(key, map);
    }
    for (let f = win.from; f <= win.to; f++) {
      this.cams.delete(f);
      this.views.delete(f);
    }
    const c = win.cam;
    if (c) {
      this.tracksCamera = true;
      for (let i = 0; i < c.f.length; i++) {
        const f = c.f[i] as number;
        const g = c.g.slice(i * 9, i * 9 + 9);
        this.cams.set(f, g[8] ? [g.slice(0, 3), g.slice(3, 6), g.slice(6, 9)] : null);
        if (c.h) {
          const cam = c.h[i] ?? -1;
          // a pose without a camera id comes from an analysis made before cameras were identified: main
          const view = !g[8] ? "none" : cam <= 0 ? "main" : "alt";
          this.views.set(f, { view, camera: cam, quality: c.q?.[i] ?? null });
        }
      }
    }
    this.cover(win.from, win.to);
    this.version++;
  }

  /** Camera pose at `frame` (reference px → frame px), or null when the court is not (known to be) in view. */
  camera(frame: number): number[][] | null {
    return this.cams.get(frame) ?? null;
  }

  /** Which camera shot `frame` (undefined: not analysed yet, or analysed before cameras were identified). */
  view(frame: number): CameraView | undefined {
    return this.views.get(frame);
  }

  private cover(a: number, b: number): void {
    const merged: [number, number][] = [];
    for (const r of [...this.covered, [a, b] as [number, number]].sort((x, y) => x[0] - y[0])) {
      const last = merged[merged.length - 1];
      if (last && r[0] <= last[1] + 1) last[1] = Math.max(last[1], r[1]);
      else merged.push([r[0], r[1]]);
    }
    this.covered = merged;
  }

  isCovered(frame: number): boolean {
    return this.covered.some(([a, b]) => frame >= a && frame <= b);
  }

  coveredRanges(): readonly [number, number][] {
    return this.covered;
  }

  /** Shuttle points for frames (frame - n, frame], oldest first, with their frame index. */
  trail(frame: number, n: number): { f: number; p: ShuttlePoint }[] {
    const out: { f: number; p: ShuttlePoint }[] = [];
    for (let f = frame - n + 1; f <= frame; f++) {
      const p = this.shuttle.get(f);
      if (p) out.push({ f, p });
    }
    return out;
  }

  player(pid: PlayerId, frame: number, maxGap = 0): PlayerFrame | undefined {
    const m = this.players[pid];
    for (let d = 0; d <= maxGap; d++) {
      if (d && (this.isCovered(frame) || this.view(frame)?.camera !== this.view(frame - d)?.camera)) break;
      const v = m.get(frame - d);
      if (v) return v;
    }
    return undefined;
  }

  /** Exact-frame observations, including all anonymous doubles players. No identity is invented. */
  playersAt(frame: number): PlayerFrame[] {
    return [...Object.values(this.players), ...this.anonymous.values()].flatMap((map) => {
      const p = map.get(frame);
      return p ? [p] : [];
    });
  }

  /** Display-only pose hold between scheduled samples. Stored observations stay unchanged.
   * Requires a current body box and continuous evidence for the same episode;
   * never bridges a missing person, camera change, or unassigned episode.
   */
  displayPose(person: PlayerFrame, frame: number, maxAge = 5): DisplayPose | null {
    if (person.kps) return { keypoints: person.kps, observedFrame: frame, ageFrames: 0 };
    if (!person.observationId || this.view(frame)?.view === "none") return null;
    const map = person.playerId
      ? this.players[person.playerId]
      : [...this.anonymous.values()].find((values) => values.get(frame) === person);
    if (!map || map.get(frame) !== person) return null;
    for (let age = 1; age <= maxAge; age++) {
      const previous = map.get(frame - age);
      if (
        !previous ||
        previous.track !== person.track ||
        previous.observationId !== person.observationId ||
        this.view(frame - age)?.camera !== this.view(frame)?.camera ||
        this.view(frame - age)?.view === "none"
      )
        return null;
      if (!previous.kps) continue;
      const [sx, sy, ex, ey] = previous.bbox;
      const [x, y, right, bottom] = person.bbox;
      if (![sx, sy, ex, ey, x, y, right, bottom].every(Number.isFinite) || ex <= sx || ey <= sy) return null;
      const widthRatio = (right - x) / (ex - sx);
      const heightRatio = (bottom - y) / (ey - sy);
      const displacement = Math.hypot((x + right - sx - ex) / 2, (y + bottom - sy - ey) / 2);
      if (
        widthRatio < 0.5 ||
        widthRatio > 2 ||
        heightRatio < 0.5 ||
        heightRatio > 2 ||
        displacement > ey - sy
      )
        return null;
      const keys = Float32Array.from(previous.kps);
      for (let i = 0; i < 17; i++) {
        keys[i * 3] = x + (((keys[i * 3] as number) - sx) * (right - x)) / (ex - sx);
        keys[i * 3 + 1] = y + (((keys[i * 3 + 1] as number) - sy) * (bottom - y)) / (ey - sy);
      }
      return { keypoints: keys, observedFrame: frame - age, ageFrames: age };
    }
    return null;
  }

  playerCourtTrail(pid: PlayerId, frame: number, n: number, step = 3): [number, number][] {
    const out: [number, number][] = [];
    let previous: PlayerFrame | undefined;
    for (let f = Math.max(0, frame - n); f <= frame; f++) {
      const v = this.players[pid].get(f);
      if (
        !v?.court ||
        (previous && (previous.track !== v.track || previous.observationId !== v.observationId))
      )
        out.length = 0;
      if (v?.court && (frame - f) % step === 0) out.push(v.court);
      previous = v;
    }
    return out;
  }

  clear(): void {
    this.shuttle.clear();
    this.players.P1.clear();
    this.players.P2.clear();
    this.anonymous.clear();
    this.cams.clear();
    this.views.clear();
    this.tracksCamera = false;
    this.covered = [];
    this.version++;
  }
}
