import { beforeEach, describe, expect, it } from "vitest";
import { usePlayback } from "./playback";

describe("evidence playback lifecycle", () => {
  beforeEach(() => {
    usePlayback.getState().resetMedia();
    usePlayback.getState().bindVideo(null);
  });
  it("releases an active bounded clip on a manual seek, including same-frame seeks", () => {
    const video = document.createElement("video");
    Object.defineProperty(video, "duration", { value: 10 });
    usePlayback.getState().bindVideo(video);
    usePlayback.getState().selectEvidence({ start: 90, end: 120, label: "Smash" }, { from: 60, to: 120 });
    usePlayback.getState().seekFrame(90, 30);
    expect(video.currentTime).toBeCloseTo(90.5 / 30);
    expect(usePlayback.getState()).toMatchObject({ frame: 90, clip: null, selection: null });
  });
  it("clamps to available media and rejects invalid timebases", () => {
    const video = document.createElement("video");
    Object.defineProperty(video, "duration", { value: 10 });
    usePlayback.getState().bindVideo(video);
    usePlayback.getState().seekFrame(99999, 30);
    expect(usePlayback.getState().frame).toBe(299);
    usePlayback.getState().seekFrame(90, 0);
    usePlayback.getState().seekFrame(Number.NaN, 30);
    expect(usePlayback.getState().frame).toBe(299);
  });
  it("clears prior-session evidence, play state and frame when a recording changes", () => {
    usePlayback
      .getState()
      .selectEvidence({ start: 900, end: 1200, label: "Old recording" }, { from: 870, to: 1200 });
    usePlayback.getState().setPlaying(true);
    usePlayback.getState().setFrame(999);
    usePlayback.getState().resetMedia();
    expect(usePlayback.getState()).toMatchObject({ frame: 0, playing: false, clip: null, selection: null });
  });
});
