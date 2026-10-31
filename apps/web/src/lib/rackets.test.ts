import { expect, it } from "vitest";
import { TrackBuffer } from "./tracks";

it("displays exact-frame racket observations and removes them when a window is replaced", () => {
  const tracks = new TrackBuffer();
  const window = { v: 1, from: 0, to: 10, shuttle: { f: [], x: [], y: [], c: [] }, players: {} };
  tracks.ingest({
    ...window,
    rackets: { f: [3], t: [4], x: [100], y: [50], b: [80, 30, 120, 70], c: [0.9], obs: ["birth"] },
  });
  expect(tracks.racketsAt(3)).toEqual([
    { track: 4, x: 100, y: 50, bbox: [80, 30, 120, 70], confidence: 0.9, observationId: "birth" },
  ]);
  expect(tracks.racketsAt(4)).toEqual([]);
  tracks.ingest(window);
  expect(tracks.racketsAt(3)).toEqual([]);
  tracks.ingest({
    ...window,
    rackets: { f: [3], t: [4], x: [40], y: [20], b: [50, 10, 40, 20], c: [0.9], obs: ["birth"] },
  });
  expect(tracks.racketsAt(3)).toEqual([]);
});
