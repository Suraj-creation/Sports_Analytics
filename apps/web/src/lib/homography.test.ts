import { describe, expect, it } from "vitest";
import { mul3, project } from "./court";
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

describe("camera pose composition", () => {
  it("court → image under a panned/zoomed camera is G·H, not H", () => {
    // the camera zooms 1.3× about the frame centre and pans 90 px right
    const G = [
      [1.3, 0, 90 + (1 - 1.3) * 640],
      [0, 1.3, (1 - 1.3) * 360],
      [0, 0, 1],
    ];
    const GH = mul3(G, TRUE_H);
    for (const c of COURT) {
      const [u, v] = project(TRUE_H, c);
      const [gu, gv] = project(GH, c);
      expect(gu).toBeCloseTo(1.3 * u + 90 + (1 - 1.3) * 640, 6);
      expect(gv).toBeCloseTo(1.3 * v + (1 - 1.3) * 360, 6);
    }
    // …so a court drawn with the fixed H would sit hundreds of px off the one the camera sees
    const [u0] = project(TRUE_H, [3.05, 6.7]);
    const [u1] = project(GH, [3.05, 6.7]);
    expect(Math.abs(u1 - u0)).toBeGreaterThan(50);
  });
});
