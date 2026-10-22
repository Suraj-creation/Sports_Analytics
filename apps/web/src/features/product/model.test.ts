import { describe, expect, it } from "vitest";
import { filterMatches, processingPercent } from "./model";
import type { MatchSummary } from "./types";

const row = (title: string, status: string) =>
  ({ session: { title, status, players: [{ name: "Sam" }] } }) as MatchSummary;
describe("match library selection", () => {
  it("applies text and processing filters together", () => {
    const matches = [
      row("Club night", "analysed"),
      row("Club finals", "analysing"),
      row("Training", "analysed"),
    ];
    expect(filterMatches(matches, "club", "analysed").map((m) => m.session.title)).toEqual(["Club night"]);
    expect(filterMatches(matches, "sam", "all")).toHaveLength(3);
  });
  it("clamps padded segment frontiers and preserves unknown duration", () => {
    expect(processingPercent(22_860, 22_802)).toBe(100);
    expect(processingPercent(-1, 100)).toBe(0);
    expect(processingPercent(5, 0)).toBeNull();
    expect(processingPercent(25, 100)).toBe(25);
  });
});
