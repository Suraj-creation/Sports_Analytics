import { describe, expect, it } from "vitest";
import { project } from "./court";
import { fitHomography, reprojectionError } from "./homography";

const TRUE_H = [
  [62.0, 9.5, 640.0],
  [-1.5, -28.0, 420.0],
  [0.0005, 0.031, 1.0],
];
const COURT: [number, number][] = [
  [-3.05, -6.7],
  [3.05, -6.7],
  [3.05, 6.7],
  [-3.05, 6.7],
  [-3.05, 0],
  [3.05, 0],
];

describe("fitHomography", () => {
  it("recovers a broadcast-like homography from exact correspondences", () => {
    const img = COURT.map((p) => project(TRUE_H, p));
    const H = fitHomography(COURT, img);
    expect(H).not.toBeNull();
    expect(reprojectionError(H as number[][], COURT, img)).toBeLessThan(1e-6);
    // a point that wasn't used for the fit lands where the true homography puts it
    const [u, v] = project(H as number[][], [0, 1.98]);
    const [tu, tv] = project(TRUE_H, [0, 1.98]);
    expect(Math.hypot(u - tu, v - tv)).toBeLessThan(1e-6);
  });

  it("needs at least four points", () => {
    expect(fitHomography(COURT.slice(0, 3), COURT.slice(0, 3))).toBeNull();
  });

  it("rejects degenerate (collinear) input", () => {
    const line: [number, number][] = [
      [0, 0],
      [1, 0],
      [2, 0],
      [3, 0],
    ];
    expect(fitHomography(line, line)).toBeNull();
  });
});
