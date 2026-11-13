import { describe, expect, it } from "vitest";
import { TrackBuffer } from "./tracks";

function window(count = 2, version = 2) {
  return {
    v: version,
    from: 10,
    to: 10,
    shuttle: { f: [], x: [], y: [], c: [] },
    players: {},
    anonymous: Object.fromEntries(
      Array.from({ length: count }, (_, i) => [
        `episode:${i}`,
        {
          f: [10],
          t: [i],
          b: [0, 0, 10, 20],
          k: Array(51).fill(1),
          cx: [null],
          cy: [null],
          pf: [6 + i],
        },
      ]),
    ),
  };
}

describe("pose source-frame wire provenance", () => {
  it.each([2, 4])("retains all %i players' exact pose frames", (count) => {
    const buffer = new TrackBuffer();
    buffer.ingest(window(count));
    expect(buffer.playersAt(10).map((p) => p.poseObservedFrame)).toEqual(
      Array.from({ length: count }, (_, i) => 6 + i),
    );
  });
  it("backreads old data with unknown provenance while keeping its keypoints", () => {
    const buffer = new TrackBuffer();
    const legacy = window(2, 1);
    for (const p of Object.values(legacy.anonymous)) delete (p as { pf?: unknown }).pf;
    buffer.ingest(legacy);
    expect(buffer.playersAt(10).map((p) => p.poseObservedFrame)).toEqual([null, null]);
    expect(buffer.playersAt(10).every((p) => p.kps?.length === 51)).toBe(true);
    const person = buffer.playersAt(10)[0];
    const displayed = person ? buffer.displayPose(person, 10) : null;
    expect(displayed?.observedFrame).toBeNull();
    expect(displayed?.ageFrames).toBeNull();
  });
  it("never promotes a retained old pose to a current observation", () => {
    const buffer = new TrackBuffer();
    buffer.ingest(window());
    const person = buffer.playersAt(10)[0];
    expect(person?.kps?.length).toBe(51);
    expect(person ? buffer.displayPose(person, 10) : null).toBeNull();
  });
  it("breaks display-only pose continuity at a same-camera content epoch", () => {
    const buffer = new TrackBuffer();
    buffer.ingest({
      v: 2,
      from: 0,
      to: 1,
      shuttle: { f: [], x: [], y: [], c: [] },
      players: {},
      anonymous: {
        a: {
          f: [0, 1],
          t: [7, 7],
          obs: ["birth-a", "birth-a"],
          b: [0, 0, 10, 20, 0, 0, 10, 20],
          k: [...Array(51).fill(1), ...Array(51).fill(0)],
          cx: [0, 0],
          cy: [0, 0],
          pf: [0, null],
          ctx: ["shot0:content0", "shot0:content1"],
        },
      },
    });
    const person = buffer.playersAt(1)[0];
    expect(person?.contextId).toBe("shot0:content1");
    expect(person ? buffer.displayPose(person, 1) : null).toBeNull();
  });
  it.each([0, 3, Number.NaN])("rejects unsupported version %s before changing the buffer", (version) => {
    const buffer = new TrackBuffer();
    expect(() => buffer.ingest(window(2, version))).toThrow();
    expect(buffer.version).toBe(0);
  });
  it.each([-1, 11, 1.5, Number.NaN])("rejects invalid or future source %s atomically", (source) => {
    const buffer = new TrackBuffer();
    const invalid = window();
    const player = invalid.anonymous["episode:0"];
    if (!player) throw new Error("Missing controlled fixture player");
    player.pf = [source];
    expect(() => buffer.ingest(invalid)).toThrow();
    expect(buffer.playersAt(10)).toEqual([]);
    expect(buffer.version).toBe(0);
  });
  it("rejects a partial temporal-context column before replacing existing observations", () => {
    const buffer = new TrackBuffer();
    buffer.ingest(window());
    const invalid = { ...window(), cam: { f: [10], g: [1, 0, 0, 0, 1, 0, 0, 0, 1], ctx: [] } };
    expect(() => buffer.ingest(invalid)).toThrow("Misaligned camera temporal contexts");
    expect(buffer.playersAt(10)).toHaveLength(2);
    expect(buffer.version).toBe(1);
  });
});
