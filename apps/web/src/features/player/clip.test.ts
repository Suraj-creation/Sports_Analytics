import { describe, expect, it } from "vitest";
import { rallyLabel } from "@/lib/format";
import { usePlayback } from "@/stores/playback";
import { ev, SESSION } from "@/test/fixtures";
import { normalizeClip, playEventEvidence } from "./clip";

it("keeps two unofficial zero-number exchanges distinct by source event and frame", () => {
  const first = ev("rally_end", 10, {
    event_id: "exchange-a",
    frame_end: 30,
    payload: { rally_no: 0, official: false },
  });
  const second = ev("rally_end", 100, {
    event_id: "exchange-b",
    frame_end: 120,
    payload: { rally_no: 0, official: false },
  });
  playEventEvidence(first, SESSION.media, 1);
  expect(usePlayback.getState().selection).toMatchObject({
    eventId: "exchange-a",
    start: 10,
    end: 30,
    label: "Candidate 1",
  });
  playEventEvidence(second, SESSION.media, 2);
  expect(usePlayback.getState().selection).toMatchObject({
    eventId: "exchange-b",
    start: 100,
    end: 120,
    label: "Candidate 2",
  });
  expect(rallyLabel(0)).toBe("Rally candidate");
  expect(rallyLabel(9, false, 2)).toBe("Candidate 2");
  expect(rallyLabel(9, true, 2)).toBe("Rally 9");
  usePlayback.setState({ selection: null, clip: null });
});

describe("bounded evidence clips", () => {
  it("clamps the lead in and end to the real media frame range", () => {
    expect(normalizeClip(10, 400, 30, 300)).toEqual({ from: 0, to: 299 });
    expect(normalizeClip(100, 200, 30, 300)).toEqual({ from: 70, to: 200 });
  });
  it("rejects missing or inverted clip evidence", () => {
    expect(normalizeClip(30, 20, 30, 300)).toBeNull();
    expect(normalizeClip(Number.NaN, 200, 30, 300)).toBeNull();
    expect(normalizeClip(0, 20, 0, 300)).toBeNull();
  });
});
