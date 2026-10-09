import type { PlayerId } from "./types";

/** Decoded columnar track window (see engine/src/bai_engine/wire.py). */
interface WireWindow {
  v: number;
  from: number;
  to: number;
  shuttle: { f: number[]; x: number[]; y: number[]; c: number[] };
  players: Record<
    string,
    { f: number[]; t: number[]; b: number[]; k: number[]; cx: (number | null)[]; cy: (number | null)[] }
  >;
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
}

/**
 * Frame-indexed store of everything the overlay draws. Mutable on purpose: the canvas reads
 * it every video frame, React never re-renders on track arrival (only `version` bumps).
 */
export class TrackBuffer {
  readonly shuttle = new Map<number, ShuttlePoint>();
  readonly players: Record<PlayerId, Map<number, PlayerFrame>> = { P1: new Map(), P2: new Map() };
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
        const k = p.k.slice(i * 51, i * 51 + 51);
        const hasKps = k.some((v) => v !== 0);
        const cx = p.cx[i];
        const cy = p.cy[i];
        map.set(p.f[i] as number, {
          bbox: [
            p.b[i * 4] as number,
            p.b[i * 4 + 1] as number,
            p.b[i * 4 + 2] as number,
            p.b[i * 4 + 3] as number,
          ],
          kps: hasKps ? Float32Array.from(k) : null,
          court: cx != null && cy != null ? [cx, cy] : null,
          track: p.t[i] as number,
        });
      }
    }
    this.cover(win.from, win.to);
    this.version++;
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

  player(pid: PlayerId, frame: number, maxGap = 3): PlayerFrame | undefined {
    const m = this.players[pid];
    for (let d = 0; d <= maxGap; d++) {
      const v = m.get(frame - d);
      if (v) return v;
    }
    return undefined;
  }

  playerCourtTrail(pid: PlayerId, frame: number, n: number, step = 3): [number, number][] {
    const out: [number, number][] = [];
    for (let f = frame - n; f <= frame; f += step) {
      const v = this.players[pid].get(f);
      if (v?.court) out.push(v.court);
    }
    return out;
  }

  clear(): void {
    this.shuttle.clear();
    this.players.P1.clear();
    this.players.P2.clear();
    this.covered = [];
    this.version++;
  }
}
