import { describe, expect, it } from "vitest";
import { normalizeClip } from "./clip";

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
