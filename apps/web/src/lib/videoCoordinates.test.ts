import { describe, expect, it } from "vitest";
import { analysisPoint, videoViewport } from "./videoCoordinates";

describe("raw-analysis coordinates in a sample-aspect-corrected video", () => {
  it("maps the actual762-pixel analysis edge onto the763-pixel browser presentation", () => {
    const view = videoViewport(1280, 720, 763, 720, 762, 720);
    expect(view).not.toBeNull();
    if (!view) throw new Error("Missing viewport");
    expect(view.left).toBe(258.5);
    expect(view.left + 762 * view.scaleX).toBeCloseTo(1021.5, 10);
    expect(view.top + 720 * view.scaleY).toBe(720);
    const edge = analysisPoint(1021.5, 720, view);
    expect(edge?.[0]).toBeCloseTo(762, 10);
    expect(edge?.[1]).toBe(720);
    expect(analysisPoint(200, 300, view)).toBeNull();
  });
  it("inverts an anamorphic presentation without treating letterbox bars as image points", () => {
    const view = videoViewport(1000, 1000, 640, 240, 320, 240);
    if (!view) throw new Error("Missing viewport");
    expect(view.width).toBe(1000);
    expect(view.height).toBe(375);
    expect(analysisPoint(500, 500, view)).toEqual([160, 120]);
    expect(analysisPoint(100, 100, view)).toBeNull();
    expect(analysisPoint(900, 900, view)).toBeNull();
  });
  it.each([0, -1, Number.NaN, Number.POSITIVE_INFINITY])("withholds invalid dimensions %s", (width) => {
    expect(videoViewport(width, 720, 1280, 720, 1280, 720)).toBeNull();
  });
});
