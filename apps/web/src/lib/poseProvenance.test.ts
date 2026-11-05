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
});
