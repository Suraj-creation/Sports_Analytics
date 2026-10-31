import { describe, expect, it, vi } from "vitest";
import { EventLog } from "@/lib/events";
import { TrackBuffer } from "@/lib/tracks";
import { drawOverlay } from "./overlay";

describe("player observation overlay", () => {
  it.each([
    [1280, 720, 1280, 720, 1, 0, 0],
    [1000, 1000, 1280, 720, 0.78125, 0, 218.75],
    [1080, 1920, 1920, 1080, 0.5625, 0, 656.25],
    [1280, 720, 720, 1280, 0.5625, 437.5, 0],
  ])("maps intrinsic pixels into a %sx%s letterboxed viewport", (cw, ch, vw, vh, scale, ox, oy) => {
    const context = { setTransform: vi.fn(), clearRect: vi.fn() };
    drawOverlay(
      {
        canvas: {
          clientWidth: cw,
          clientHeight: ch,
          width: cw,
          height: ch,
          getContext: () => context,
        } as unknown as HTMLCanvasElement,
        video: { videoWidth: vw, videoHeight: vh } as HTMLVideoElement,
        tracks: new TrackBuffer(),
        events: new EventLog(),
        calibration: null,
        layers: { court: false, players: false, pose: false, shuttle: false, labels: false, scoreBug: false },
        names: { P1: "Player 1", P2: "Player 2" },
        colors: { P1: "blue", P2: "red" },
      },
      0,
    );
    const dpr = window.devicePixelRatio || 1;
    expect(context.setTransform).toHaveBeenLastCalledWith(dpr * scale, 0, 0, dpr * scale, dpr * ox, dpr * oy);
  });

  it("draws four anonymous doubles tracks without inventing participant names", () => {
    const tracks = new TrackBuffer();
    tracks.ingest({
      v: 1,
      from: 0,
      to: 0,
      shuttle: { f: [], x: [], y: [], c: [] },
      players: {},
      anonymous: Object.fromEntries(
        [1, 2, 3, 4].map((track) => [
          String(track),
          {
            f: [0],
            t: [track],
            b: [10, 20, 30, 80],
            k: new Array(51).fill(0),
            cx: [null],
            cy: [null],
            m: [track !== 4],
          },
        ]),
      ),
    });
    const context = {
      setTransform: vi.fn(),
      clearRect: vi.fn(),
      setLineDash: vi.fn(),
      beginPath: vi.fn(),
      moveTo: vi.fn(),
      lineTo: vi.fn(),
      stroke: vi.fn(),
      fill: vi.fn(),
      fillRect: vi.fn(),
      arcTo: vi.fn(),
      closePath: vi.fn(),
      fillText: vi.fn(),
      measureText: () => ({ width: 80 }),
    };
    drawOverlay(
      {
        canvas: {
          clientWidth: 1280,
          clientHeight: 720,
          width: 1280,
          height: 720,
          getContext: () => context,
        } as unknown as HTMLCanvasElement,
        video: { videoWidth: 1280, videoHeight: 720 } as HTMLVideoElement,
        tracks,
        events: new EventLog(),
        calibration: null,
        layers: { court: false, players: true, pose: false, shuttle: false, labels: true, scoreBug: false },
        names: { P1: "Player 1", P2: "Player 2" },
        colors: { P1: "blue", P2: "red" },
      },
      0,
    );
    expect(context.stroke).toHaveBeenCalledTimes(4);
    expect(context.fillText.mock.calls.map((call) => call[0])).toEqual([
      "Track 1 · identity unassigned",
      "Track 2 · identity unassigned",
      "Track 3 · identity unassigned",
      "Track 4 · identity unassigned · tracked estimate",
    ]);
  });
});
