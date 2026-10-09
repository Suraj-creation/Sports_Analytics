import { describe, expect, it } from "vitest";
import { ev } from "@/test/fixtures";
import { EventLog } from "./events";
import { TrackBuffer } from "./tracks";

describe("EventLog", () => {
  it("replaces superseded events and drops retracted ones, like the backend current_view", () => {
    const log = new EventLog();
    const a = ev("stroke", 100, { event_id: "a", payload: { stroke: "clear" } });
    const b = ev("stroke", 140, { event_id: "b" });
    log.apply([a, b]);
    const a2 = ev("stroke", 100, {
      event_id: "a2",
      supersedes: "a",
      payload: { stroke: "smash" },
      status: "corrected",
    });
    const bGone = ev("stroke", 140, { event_id: "b-r", supersedes: "b", status: "retracted" });
    log.apply([a2, bGone]);
    expect(log.ofType("stroke").map((e) => e.event_id)).toEqual(["a2"]);
    expect(log.get("a2")?.payload.stroke).toBe("smash");
    expect(log.recentlyCorrected.has("a2")).toBe(true);
    expect(log.recentlyCorrected.has("b-r")).toBe(false);
  });

  it("ignores a late original after its correction (out-of-order backlog)", () => {
    const log = new EventLog();
    log.apply([ev("stroke", 10, { event_id: "x2", supersedes: "x" })]);
    log.apply([ev("stroke", 10, { event_id: "x" })]);
    expect(log.ofType("stroke").map((e) => e.event_id)).toEqual(["x2"]);
  });

  it("tracks the highest seq for lossless resume", () => {
    const log = new EventLog();
    log.apply([ev("contact", 1, { seq: 7 }), ev("contact", 2, { seq: 3 })]);
    expect(log.lastSeq).toBe(7);
  });

  it("latestBefore and window respect frame order", () => {
    const log = new EventLog();
    log.apply([ev("point", 300), ev("point", 100), ev("rally_end", 50, { frame_end: 120 })]);
    expect(log.latestBefore("point", 299)?.frame_start).toBe(100);
    expect(log.latestBefore("point", 99)).toBeUndefined();
    expect(log.window(110, 115).map((e) => e.type)).toEqual(["rally_end"]);
  });
});

const win = (from: number, to: number, shuttleFrames: number[]) => ({
  v: 1,
  from,
  to,
  shuttle: {
    f: shuttleFrames,
    x: shuttleFrames.map((f) => f * 2),
    y: shuttleFrames.map(() => 100),
    c: shuttleFrames.map(() => 0.9),
  },
  players: {
    P1: { f: [from], t: [1], b: [10, 20, 30, 80], k: new Array(51).fill(0), cx: [0.5], cy: [-3] },
  },
});

describe("TrackBuffer", () => {
  it("a window replaces its whole range (refinement revisions remove stale points)", () => {
    const t = new TrackBuffer();
    t.ingest(win(0, 9, [0, 1, 2, 3, 4]));
    t.ingest(win(0, 9, [2]));
    expect([...t.shuttle.keys()]).toEqual([2]);
    expect(t.player("P1", 0)?.court).toEqual([0.5, -3]);
    expect(t.player("P1", 0)?.kps).toBeNull(); // all-zero keypoints mean "no pose"
  });

  it("merges covered ranges so gaps mean invisible, not unanalysed", () => {
    const t = new TrackBuffer();
    t.ingest(win(0, 9, []));
    t.ingest(win(10, 19, []));
    t.ingest(win(40, 49, []));
    expect(t.coveredRanges()).toEqual([
      [0, 19],
      [40, 49],
    ]);
    expect(t.isCovered(15)).toBe(true);
    expect(t.isCovered(30)).toBe(false);
  });

  it("trail returns only frames up to the playhead, oldest first", () => {
    const t = new TrackBuffer();
    t.ingest(win(0, 20, [5, 6, 8, 12]));
    expect(t.trail(8, 4).map((p) => p.f)).toEqual([5, 6, 8]);
  });

  it("player() bridges short detection gaps only", () => {
    const t = new TrackBuffer();
    t.ingest(win(0, 20, []));
    expect(t.player("P1", 3)).toBeDefined();
    expect(t.player("P1", 4)).toBeUndefined();
  });
});
