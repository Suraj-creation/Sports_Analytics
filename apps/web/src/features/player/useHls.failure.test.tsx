import { act, cleanup, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { useHls } from "./useHls";

const hls = vi.hoisted(() => ({
  handlers: new Map<string, (...args: unknown[]) => void>(),
  loadSource: vi.fn(),
  startLoad: vi.fn(),
  stopLoad: vi.fn(),
  destroy: vi.fn(),
}));

vi.mock("hls.js/light", () => ({
  default: class {
    static isSupported = () => true;
    static Events = { MANIFEST_PARSED: "manifestParsed", ERROR: "error" };
    static ErrorTypes = { NETWORK_ERROR: "networkError", MEDIA_ERROR: "mediaError" };
    on = (name: string, callback: (...args: unknown[]) => void) => hls.handlers.set(name, callback);
    loadSource = hls.loadSource;
    startLoad = hls.startLoad;
    stopLoad = hls.stopLoad;
    destroy = hls.destroy;
    attachMedia = vi.fn();
    recoverMediaError = vi.fn();
  },
}));

beforeEach(() => {
  vi.useFakeTimers();
  vi.clearAllMocks();
  hls.handlers.clear();
});

afterEach(() => {
  cleanup();
  vi.useRealTimers();
});

function networkError(code: number) {
  act(() => {
    hls.handlers.get("error")?.("error", {
      fatal: true,
      type: "networkError",
      details: "manifestLoadError",
      response: { code, text: "fixture response" },
    });
  });
}

it.each([401, 403])("treats HTTP %s as a terminal authorization failure, not media preparation", (code) => {
  const video = document.createElement("video");
  const { result } = renderHook(() => useHls(video, "S1", true));
  networkError(code);
  expect(result.current).toBe("error");
  act(() => vi.advanceTimersByTime(6000));
  expect(hls.loadSource).toHaveBeenCalledTimes(1);
});

it("keeps retrying an initial 404 while media segments are being prepared", () => {
  const video = document.createElement("video");
  const { result } = renderHook(() => useHls(video, "S1", true));
  networkError(404);
  expect(result.current).toBe("waiting");
  act(() => vi.advanceTimersByTime(2000));
  expect(hls.loadSource).toHaveBeenCalledTimes(2);
  expect(hls.startLoad).toHaveBeenCalledWith(0);
});

it("cancels a pending transient retry when authorization is subsequently rejected", () => {
  const video = document.createElement("video");
  const { result } = renderHook(() => useHls(video, "S1", true));
  networkError(404);
  networkError(401);
  expect(result.current).toBe("error");
  act(() => vi.advanceTimersByTime(6000));
  expect(hls.loadSource).toHaveBeenCalledTimes(1);
});
