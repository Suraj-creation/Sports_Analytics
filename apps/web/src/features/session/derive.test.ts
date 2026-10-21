import { describe, expect, it } from "vitest";
import { EventLog } from "@/lib/events";
import { ev, point, state } from "@/test/fixtures";
import { currentRally, stateAt } from "./derive";

describe("stateAt", () => {
  const log = new EventLog();
  const s0 = state(0, 0, { server: "P2", receiver: "P1" });
  const s1 = state(0, 1, { server: "P2", receiver: "P1" });
  const s2 = state(1, 1);
  log.apply([point(300, "P2", s0, s1), point(600, "P1", s1, s2)]);

  it("never shows a point before the video reaches it", () => {
    expect(stateAt(log, 299).state.score).toEqual({ P1: 0, P2: 0 });
    expect(stateAt(log, 300).state.score).toEqual({ P1: 0, P2: 1 });
    expect(stateAt(log, 599).state.score).toEqual({ P1: 0, P2: 1 });
    expect(stateAt(log, 600).state.score).toEqual({ P1: 1, P2: 1 });
  });

  it("before the first point uses that point's opening state (real first server)", () => {
    const r = stateAt(log, 10);
    expect(r.known).toBe(true);
    expect(r.state.server).toBe("P2");
  });

  it("with no points at all the state is unknown", () => {
    expect(stateAt(new EventLog(), 10).known).toBe(false);
  });
});

describe("currentRally", () => {
  const log = new EventLog();
  log.apply([
    ev("rally_start", 100),
    ev("rally_end", 100, { frame_end: 400, payload: { rally_no: 1 } }),
    ev("rally_start", 600),
  ]);

  it("finds the finished rally containing the frame", () => {
    expect(currentRally(log, 250)?.end?.payload.rally_no).toBe(1);
  });

  it("reports no rally between rallies", () => {
    expect(currentRally(log, 500)).toBeNull();
  });

  it("reports the rally in play when it has started but not ended", () => {
    const r = currentRally(log, 700);
    expect(r?.start).toBe(600);
    expect(r?.end).toBeNull();
  });
});
