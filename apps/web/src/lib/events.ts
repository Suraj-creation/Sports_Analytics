import type { BaiEvent } from "./types";

/**
 * Client-side fold of the append-only event log — the same rule as the backend's
 * `current_view`: an event that supersedes another replaces it; retracted events vanish.
 */
export class EventLog {
  private live = new Map<string, BaiEvent>();
  private superseded = new Set<string>();
  lastSeq = 0;
  version = 0;
  /** ids of events whose replacement arrived in the latest batch (for "corrected" animations) */
  readonly recentlyCorrected = new Set<string>();

  apply(events: BaiEvent[]): void {
    this.recentlyCorrected.clear();
    for (const e of events) {
      if (e.seq != null) this.lastSeq = Math.max(this.lastSeq, e.seq);
      if (e.supersedes) {
        this.superseded.add(e.supersedes);
        if (this.live.delete(e.supersedes) && e.status !== "retracted")
          this.recentlyCorrected.add(e.event_id);
      }
      if (e.status === "retracted" || this.superseded.has(e.event_id)) continue;
      this.live.set(e.event_id, e);
    }
    this.version++;
  }

  get(id: string): BaiEvent | undefined {
    return this.live.get(id);
  }

  /** Live events of the given types, ordered by frame. */
  ofType(...types: string[]): BaiEvent[] {
    const set = new Set(types);
    const out: BaiEvent[] = [];
    for (const e of this.live.values()) if (set.has(e.type)) out.push(e);
    return out.sort((a, b) => a.frame_start - b.frame_start || (a.seq ?? 0) - (b.seq ?? 0));
  }

  /** Latest live event of `type` that started at or before `frame`. */
  latestBefore(type: string, frame: number): BaiEvent | undefined {
    let best: BaiEvent | undefined;
    for (const e of this.live.values()) {
      if (e.type === type && e.frame_start <= frame && (!best || e.frame_start > best.frame_start)) best = e;
    }
    return best;
  }

  /** Live events overlapping [a, b]. */
  window(a: number, b: number, types?: string[]): BaiEvent[] {
    const set = types ? new Set(types) : null;
    const out: BaiEvent[] = [];
    for (const e of this.live.values()) {
      if (e.frame_end >= a && e.frame_start <= b && (!set || set.has(e.type))) out.push(e);
    }
    return out.sort((x, y) => x.frame_start - y.frame_start);
  }

  get size(): number {
    return this.live.size;
  }

  clear(): void {
    this.live.clear();
    this.superseded.clear();
    this.lastSeq = 0;
    this.version++;
  }
}
