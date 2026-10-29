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

  it("does not turn an analysed missing observation into a carried pose", () => {
    const t = new TrackBuffer();
    t.ingest(win(0, 20, []));
    expect(t.player("P1", 3)).toBeUndefined();
    expect(t.player("P1", 4)).toBeUndefined();
  });

  it("preserves four anonymous players and their observation provenance", () => {
    const t = new TrackBuffer();
    const anonymous = Object.fromEntries(
      [1, 2, 3, 4].map((track) => [
        `episode:${track}`,
        {
          f: [0],
          t: [track],
          b: [10, 20, 30, 80],
          k: new Array(51).fill(0.7),
          cx: [1],
          cy: [2],
          obs: [`episode-${track}`],
          c: [0.9],
          d: [true],
          m: [track !== 4],
        },
      ]),
    );
    t.ingest({ ...win(0, 9, []), players: {}, anonymous });
    expect(t.playersAt(0)).toHaveLength(4);
    expect(t.playersAt(0).every((p) => p.playerId === null && p.kps?.length === 51)).toBe(true);
    expect(t.playersAt(0)[3]?.detectorMatched).toBe(false);
    expect(t.playersAt(1)).toEqual([]);
    t.ingest({ ...win(0, 9, []), players: {} });
    expect(t.playersAt(0)).toEqual([]);
  });

  const sampledPoses = (frames: number[], ids = frames.map(() => "episode-a")) => ({
    ...win(0, 6, []),
    players: {},
    anonymous: {
      a: {
        f: frames,
        t: frames.map(() => 7),
        obs: ids,
        b: frames.flatMap((f) => [10 + f, 20, 30 + f, 80]),
        k: frames.flatMap((f) => (f === 0 ? [15, 25, 0.9, ...new Array(48).fill(0)] : new Array(51).fill(0))),
        cx: frames.map(() => 0),
        cy: frames.map(() => 0),
      },
    },
  });

  it("holds a pose for display between samples without changing observed keypoints", () => {
    const t = new TrackBuffer();
    t.ingest(sampledPoses([0, 1, 2]));
    const current = t.playersAt(2)[0];
    expect(current?.kps).toBeNull();
    const display = current ? t.displayPose(current, 2) : null;
    expect(display?.observedFrame).toBe(0);
    expect(display?.ageFrames).toBe(2);
    expect(display?.keypoints[0]).toBe(17); // bbox translated +2; pose is an estimate
    expect(current?.kps).toBeNull();
    expect(t.playersAt(0)[0]?.kps?.[0]).toBe(15);
  });

  it("never holds a pose across a missing body, changed episode or expired age", () => {
    for (const window of [
      sampledPoses([0, 2]),
      sampledPoses([0, 1], ["old", "new"]),
      sampledPoses([0, 1, 2, 3, 4, 5, 6]),
    ]) {
      const t = new TrackBuffer();
      t.ingest(window);
      const frame = window.anonymous.a.f.at(-1) as number;
      const current = t.playersAt(frame)[0];
      expect(current ? t.displayPose(current, frame) : null).toBeNull();
    }
  });

  it("never holds a pose from another camera or an unknown episode", () => {
    const eye = [1, 0, 0, 0, 1, 0, 0, 0, 1];
    const t = new TrackBuffer();
    t.ingest({ ...sampledPoses([0, 1]), cam: { f: [0, 1], g: [...eye, ...eye], h: [0, 2] } });
    const current = t.playersAt(1)[0];
    expect(current ? t.displayPose(current, 1) : null).toBeNull();
    const unknown = new TrackBuffer();
    unknown.ingest(sampledPoses([0, 1], ["", ""]));
    const person = unknown.playersAt(1)[0];
    expect(person ? unknown.displayPose(person, 1) : null).toBeNull();
  });

  it("does not estimate through an abrupt bbox jump or a stricter age limit", () => {
    const t = new TrackBuffer();
    const window = sampledPoses([0, 1, 2]);
    window.anonymous.a.b.splice(8, 4, 500, 20, 520, 80);
    t.ingest(window);
    const jumped = t.playersAt(2)[0];
    expect(jumped ? t.displayPose(jumped, 2) : null).toBeNull();
    const previous = t.playersAt(1)[0];
    expect(previous ? t.displayPose(previous, 1, 0) : null).toBeNull();
  });
});

describe("TrackBuffer camera poses", () => {
  const eye = [1, 0, 0, 0, 1, 0, 0, 0, 1];
  const withCam = (from: number, to: number, frames: number[], g: number[][]) => ({
    ...win(from, to, []),
    cam: { f: frames, g: g.flat() },
  });

  it("is untracked until a pose arrives (the overlay then keeps the fixed court)", () => {
    const tb = new TrackBuffer();
    tb.ingest(win(0, 9, [1, 2]));
    expect(tb.tracksCamera).toBe(false);
  });

  it("stores the pose per frame; an all-zero pose means the court is not in view", () => {
    const tb = new TrackBuffer();
    tb.ingest(withCam(0, 9, [3, 4], [eye, new Array(9).fill(0)]));
    expect(tb.tracksCamera).toBe(true);
    expect(tb.camera(3)).toEqual([
      [1, 0, 0],
      [0, 1, 0],
      [0, 0, 1],
    ]);
    expect(tb.camera(4)).toBeNull();
    expect(tb.camera(5)).toBeNull(); // frames without a pose never draw a stale court
  });

  it("a refreshed window replaces the poses it covers", () => {
    const tb = new TrackBuffer();
    tb.ingest(withCam(0, 9, [3], [eye]));
    tb.ingest(withCam(0, 9, [4], [eye]));
    expect(tb.camera(3)).toBeNull();
    expect(tb.camera(4)).not.toBeNull();
  });

  it("knows which camera shot each frame: main (analysed), another camera, or no court", () => {
    const tb = new TrackBuffer();
    const zero = new Array(9).fill(0);
    tb.ingest({
      ...win(0, 9, []),
      cam: { f: [1, 2, 3], g: [eye, eye, zero].flat(), h: [0, 2, -1], q: [0.93, 0.7, 0] },
    });
    expect(tb.view(1)).toEqual({ view: "main", camera: 0, quality: 0.93 });
    expect(tb.view(2)?.view).toBe("alt");
    expect(tb.view(3)?.view).toBe("none");
    expect(tb.view(4)).toBeUndefined();
  });

  it("a pose from an analysis made before cameras were identified counts as the main camera", () => {
    const tb = new TrackBuffer();
    tb.ingest({ ...win(0, 9, []), cam: { f: [1], g: eye, h: [-1], q: [0] } });
    expect(tb.view(1)?.view).toBe("main");
  });
});
