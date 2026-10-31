import { describe, expect, it } from "vitest";
import { EventLog } from "@/lib/events";
import { ev } from "@/test/fixtures";
import { evidenceRallies, filterRallies, shotRows } from "./evidence";

describe("session evidence", () => {
  it("follows canonical corrections and never resurrects a retracted embedded shot", () => {
    const log = new EventLog();
    log.apply([
      ev("stroke", 110, { event_id: "shot", payload: { stroke: "smash" } }),
      ev("rally_end", 100, {
        frame_end: 150,
        payload: { n_shots: 1, shots: [{ event_id: "shot", frame: 110, stroke: "smash" }] },
      }),
      ev("stroke", 110, { event_id: "corrected", supersedes: "shot", payload: { stroke: "unknown" } }),
    ]);
    expect(evidenceRallies(log)[0]?.shots[0]?.payload.stroke).toBe("unknown");
    log.apply([ev("stroke", 110, { event_id: "removed", supersedes: "corrected", status: "retracted" })]);
    expect(evidenceRallies(log)[0]?.shots).toEqual([]);
    expect(evidenceRallies(log)[0]?.shotCount).toBe(0);
  });
  it("keeps excluded rallies visible but out of counted shot summaries", () => {
    const log = new EventLog();
    log.apply([
      ev("stroke", 110, {
        actors: { player_id: "P1", track_id: null, opponent_id: "P2" },
        payload: { stroke: "smash" },
      }),
      ev("rally_end", 100, {
        frame_end: 150,
        payload: { rally_no: 1, official: true, winner: "P1", n_shots: 1 },
      }),
      ev("stroke", 210, {
        actors: { player_id: "P1", track_id: null, opponent_id: "P2" },
        payload: { stroke: "clear" },
      }),
      ev("rally_end", 200, {
        frame_end: 250,
        payload: { rally_no: 2, official: false, winner: "P2", n_shots: 1 },
      }),
    ]);
    const rallies = evidenceRallies(log);
    expect(rallies).toHaveLength(2);
    expect(shotRows(rallies, "P1")).toEqual([{ stroke: "smash", count: 1, rallies: 1, won: 1, frame: 110 }]);
    expect(filterRallies(rallies, { outcome: "excluded" })).toHaveLength(1);
  });

  it("filters winner and minimum shot count together without inventing unknown actors", () => {
    const log = new EventLog();
    log.apply([
      ev("rally_end", 100, { frame_end: 300, payload: { rally_no: 1, winner: "P1", n_shots: 9 } }),
      ev("rally_end", 400, { frame_end: 500, payload: { rally_no: 2, winner: null, n_shots: 2 } }),
    ]);
    const rows = evidenceRallies(log);
    expect(filterRallies(rows, { winner: "P1", minimumShots: 8 }).map((r) => r.no)).toEqual([1]);
    expect(shotRows(rows, "P2")).toEqual([]);
  });
});
