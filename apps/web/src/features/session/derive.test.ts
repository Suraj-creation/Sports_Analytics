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

  it("does not turn a provisional point into a known score or opening state", () => {
    const pending = new EventLog();
    pending.apply([
      ev("point", 100, {
        status: "provisional",
        payload: { winner: "P1", state_before: state(0, 0), state_after: state(1, 0) },
      }),
    ]);
    expect(stateAt(pending, 99).known).toBe(false);
    expect(stateAt(pending, 100).known).toBe(false);
  });

  it("keeps the latest accepted score when a later point is still provisional", () => {
    const pending = new EventLog();
    pending.apply([
      point(100, "P1", state(0, 0), state(1, 0)),
      ev("point", 200, {
        status: "provisional",
        payload: { winner: "P2", state_before: state(1, 0), state_after: state(1, 1) },
      }),
    ]);
    expect(stateAt(pending, 200).state.score).toEqual({ P1: 1, P2: 0 });
  });

  it("drops an overturned point even when its original arrives again later", () => {
    const corrected = new EventLog();
    const original = ev("point", 100, {
      event_id: "overturned-point",
      seq: 1,
      payload: { state_before: state(0, 0), state_after: state(1, 0) },
    });
    corrected.apply([original]);
    corrected.apply([ev("point", 100, { seq: 2, supersedes: original.event_id, status: "retracted" })]);
    corrected.apply([original]);
    expect(stateAt(corrected, 100).known).toBe(false);
  });

  it("shows an accepted starting-score seed at its frame even without a resolved point", () => {
    const seeded = new EventLog();
    seeded.apply([
      ev("match_phase", 100, {
        payload: {
          basis: "scoreboard",
          base_state: { score: { P1: 8, P2: 3 }, server_known: false },
          state_after: state(8, 3, { server_known: false }),
        },
      }),
    ]);
    expect(stateAt(seeded, 99).known).toBe(false);
    expect(stateAt(seeded, 100).known).toBe(true);
    expect(stateAt(seeded, 100).state.score).toEqual({ P1: 8, P2: 3 });
    expect(stateAt(seeded, 100).state.server_known).toBe(false);
  });

  it("does not expose a seeded opening score before the seed when later points exist", () => {
    const seeded = new EventLog();
    seeded.apply([
      ev("match_phase", 100, {
        payload: { basis: "scoreboard", base_state: {}, state_after: state(8, 3, { server_known: false }) },
      }),
      point(200, "P1", state(8, 3, { server_known: false }), state(9, 3)),
    ]);
    expect(stateAt(seeded, 99).known).toBe(false);
    expect(stateAt(seeded, 150).state.score).toEqual({ P1: 8, P2: 3 });
    expect(stateAt(seeded, 200).state.score).toEqual({ P1: 9, P2: 3 });
  });

  it("does not treat a provisional starting-score seed as accepted evidence", () => {
    const seeded = new EventLog();
    seeded.apply([
      ev("match_phase", 100, {
        status: "provisional",
        payload: { basis: "scoreboard", base_state: {}, state_after: state(8, 3) },
      }),
    ]);
    expect(stateAt(seeded, 100).known).toBe(false);
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
