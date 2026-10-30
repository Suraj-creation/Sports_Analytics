import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import type { PropsWithChildren } from "react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { api, hlsUrl } from "@/lib/api";
import { frameClock } from "@/lib/frameClock";
import type { Session } from "@/lib/types";
import { usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";
import { SESSION } from "@/test/fixtures";
import { SessionPage } from "./SessionPage";

vi.mock("@tanstack/react-router", () => ({
  Link: ({ children }: PropsWithChildren) => <a href="/matches">{children}</a>,
  useParams: () => ({ sessionId: "s1" }),
  useSearch: () => ({}),
  useNavigate: () => vi.fn(),
}));
// Exercise the native HLS attachment and real VideoStage; the browser media decoder is external.
vi.mock("hls.js/light", () => ({ default: { isSupported: () => false } }));
vi.mock("@/features/analytics/SessionAnalytics", () => ({ SessionAnalytics: () => null }));
vi.mock("@/features/timeline/Timeline", () => ({ Timeline: () => null }));
vi.mock("./LiveFeed", () => ({ LiveFeed: () => null }));
vi.mock("./PlayerSelector", () => ({ PlayerSelector: () => null }));
vi.mock("./VisualObservations", () => ({ VisualObservations: () => null }));
vi.mock("./IndividualAnalytics", () => ({ IndividualAnalytics: () => null }));
vi.mock("./EstimatedIndividualAnalytics", () => ({ EstimatedIndividualAnalytics: () => null }));
vi.mock("./tabs/ExportTab", () => ({ ExportTab: () => null }));

const originalSession = useSession.getState();
const originalPlayback = usePlayback.getState();
const originalTransition = Object.getOwnPropertyDescriptor(document, "startViewTransition");
const originalReducedMotion = document.documentElement.dataset.reducedMotion;

beforeEach(() => {
  vi.spyOn(HTMLMediaElement.prototype, "canPlayType").mockReturnValue("probably");
  vi.spyOn(HTMLMediaElement.prototype, "pause").mockImplementation(() => {});
  vi.spyOn(HTMLMediaElement.prototype, "play").mockResolvedValue();
  vi.spyOn(HTMLMediaElement.prototype, "load").mockImplementation(() => {});
});

afterEach(() => {
  cleanup();
  useSession.setState(originalSession);
  usePlayback.setState(originalPlayback);
  if (originalTransition) Object.defineProperty(document, "startViewTransition", originalTransition);
  else Reflect.deleteProperty(document, "startViewTransition");
  if (originalReducedMotion == null) delete document.documentElement.dataset.reducedMotion;
  else document.documentElement.dataset.reducedMotion = originalReducedMotion;
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

function show(overrides: Partial<Session> = {}) {
  const session = { ...SESSION, status: "analysed" as const, roster: null, ...overrides };
  useSession.setState({ session, open: vi.fn(), close: vi.fn() });
  vi.spyOn(api, "session").mockResolvedValue(session);
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <SessionPage />
    </QueryClientProvider>,
  );
}

it("keeps the same source and selected evidence through focus, collapse and restore", () => {
  const source = vi.spyOn(HTMLMediaElement.prototype, "src", "set");
  const view = show();
  const video = view.container.querySelector("video");
  if (!video) throw new Error("The source video should be mounted");
  expect(source).toHaveBeenCalledExactlyOnceWith(hlsUrl("s1"));
  video.currentTime = 42.5;
  const selection = { start: 1275, end: 1300, label: "Selected rally" };
  act(() => usePlayback.setState({ frame: 1275, selection }));

  fireEvent.click(screen.getByRole("button", { name: "Focus video" }));
  expect(screen.getByRole("button", { name: "Standard view" })).toHaveAttribute("aria-pressed", "false");
  expect(screen.getByRole("button", { name: "Focus video" })).toHaveAttribute("aria-pressed", "true");
  expect(screen.getByRole("button", { name: "Standard view" })).toBeVisible();
  expect(view.container.querySelector("video")).toBe(video);
  expect(screen.getByRole("heading", { name: "Selected rally" })).toBeVisible();

  fireEvent.click(screen.getByRole("button", { name: "Collapse video" }));
  expect(video.pause).toHaveBeenCalledTimes(1);
  expect(screen.getByRole("button", { name: "Restore video" })).toBeVisible();
  expect(screen.queryByLabelText("Playback speed")).not.toBeInTheDocument();
  expect(view.container.querySelector("video")).toBe(video);
  expect(video.currentTime).toBe(42.5);
  expect(usePlayback.getState().selection).toEqual(selection);

  fireEvent.click(screen.getByRole("button", { name: "Restore video" }));
  expect(screen.getByRole("button", { name: "Standard view" })).toHaveAttribute("aria-pressed", "true");
  expect(screen.getByLabelText("Playback speed")).toBeVisible();
  expect(view.container.querySelector("video")).toBe(video);
  expect(video.currentTime).toBe(42.5);
  expect(source).toHaveBeenCalledTimes(1);
  expect(usePlayback.getState().selection).toEqual(selection);
});

it("reveals a collapsed recording when a source-linked moment is selected", () => {
  const view = show();
  const video = view.container.querySelector("video");
  fireEvent.click(screen.getByRole("button", { name: "Collapse video" }));
  expect(screen.getByRole("button", { name: "Restore video" })).toHaveFocus();

  const selection = { start: 100, end: 130, label: "Source moment" };
  act(() => window.dispatchEvent(new CustomEvent("bai:play-clip", { detail: selection })));

  expect(screen.getByRole("button", { name: "Standard view" })).toHaveAttribute("aria-pressed", "true");
  expect(screen.getByLabelText("Playback speed")).toBeVisible();
  expect(view.container.querySelector("video")).toBe(video);
  expect(usePlayback.getState().selection).toEqual(selection);
});

it("preserves participant drafts while focus hides supplementary analysis", () => {
  show();
  fireEvent.click(screen.getByRole("button", { name: "Set up participants" }));
  fireEvent.change(screen.getByLabelText("Match format"), { target: { value: "doubles" } });
  fireEvent.change(screen.getByLabelText("Player 1 name"), { target: { value: "Alice" } });

  fireEvent.click(screen.getByRole("button", { name: "Focus video" }));
  expect(screen.getByLabelText("Player 1 name")).not.toBeVisible();
  expect(screen.queryByRole("navigation", { name: "Match analysis" })).not.toBeInTheDocument();

  fireEvent.click(screen.getByRole("button", { name: "Standard view" }));
  expect(screen.getByLabelText("Player 1 name")).toBeVisible();
  expect(screen.getByLabelText("Player 1 name")).toHaveValue("Alice");
  expect(screen.getByRole("navigation", { name: "Match analysis" })).toBeVisible();
});

it("leaves focus with Escape without replacing the source video", () => {
  const view = show();
  const video = view.container.querySelector("video");
  fireEvent.click(screen.getByRole("button", { name: "Focus video" }));
  fireEvent.keyDown(screen.getByRole("button", { name: "Focus video" }), { key: "Escape" });
  expect(screen.getByRole("button", { name: "Standard view" })).toHaveAttribute("aria-pressed", "true");
  expect(screen.getByRole("button", { name: "Standard view" })).toHaveFocus();
  expect(view.container.querySelector("video")).toBe(video);
  expect(screen.getByRole("navigation", { name: "Match analysis" })).toBeVisible();
});

it("keeps collapsed playback paused after the analysis frontier catches up", () => {
  const view = show({ status: "analysing", frontier_frame: 60 });
  const video = view.container.querySelector("video");
  if (!video) throw new Error("The source video should be mounted");
  let paused = false;
  Object.defineProperty(video, "paused", { configurable: true, get: () => paused });
  vi.mocked(video.pause).mockImplementation(() => {
    paused = true;
    video.dispatchEvent(new Event("pause"));
  });
  vi.mocked(video.play).mockImplementation(async () => {
    paused = false;
    video.dispatchEvent(new Event("play"));
  });
  video.currentTime = 1;
  act(() => frameClock.publish(30));
  expect(screen.getByText(/Analysis is catching up/)).toBeVisible();
  expect(video.paused).toBe(true);

  fireEvent.click(screen.getByRole("button", { name: "Collapse video" }));
  act(() =>
    useSession.setState((state) => ({
      session: state.session ? { ...state.session, frontier_frame: 600 } : null,
    })),
  );
  expect(video.paused).toBe(true);
  expect(video.play).not.toHaveBeenCalled();

  fireEvent.click(screen.getByRole("button", { name: "Restore video" }));
  expect(video.paused).toBe(true);
  expect(video.play).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole("button", { name: "Play (Space)" }));
  expect(video.paused).toBe(false);
});

it("skips native mode transitions when the app Reduce motion setting is enabled", () => {
  const startTransition = vi.fn((update: () => void) => {
    update();
    return { ready: Promise.resolve(), skipTransition: vi.fn() };
  });
  Object.defineProperty(document, "startViewTransition", { configurable: true, value: startTransition });
  vi.stubGlobal("matchMedia", vi.fn().mockReturnValue({ matches: false }));
  document.documentElement.dataset.reducedMotion = "true";
  show();

  fireEvent.click(screen.getByRole("button", { name: "Focus video" }), { detail: 1 });
  expect(startTransition).not.toHaveBeenCalled();
  expect(screen.getByRole("button", { name: "Focus video" })).toHaveAttribute("aria-pressed", "true");
});

it("keeps a pending moment paused when metadata arrives after the source was collapsed", () => {
  const view = show();
  const video = view.container.querySelector("video");
  if (!video) throw new Error("The source video should be mounted");
  const selection = { start: 100, end: 130, label: "Pending source moment" };
  act(() => window.dispatchEvent(new CustomEvent("bai:play-clip", { detail: selection })));
  fireEvent.click(screen.getByRole("button", { name: "Collapse video" }));
  Object.defineProperty(video, "readyState", { configurable: true, value: 1 });
  fireEvent.loadedMetadata(video);

  expect(video.play).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole("button", { name: "Restore video" }));
  expect(video.play).not.toHaveBeenCalled();
  expect(usePlayback.getState().selection).toEqual(selection);
});

it("plays a newly selected moment after revealing a collapsed ready source", () => {
  const view = show();
  const video = view.container.querySelector("video");
  if (!video) throw new Error("The source video should be mounted");
  Object.defineProperty(video, "readyState", { configurable: true, value: 1 });
  fireEvent.loadedMetadata(video);
  fireEvent.click(screen.getByRole("button", { name: "Collapse video" }));
  const selection = { start: 100, end: 130, label: "New source moment" };
  act(() => window.dispatchEvent(new CustomEvent("bai:play-clip", { detail: selection })));

  expect(screen.getByRole("button", { name: "Standard view" })).toHaveAttribute("aria-pressed", "true");
  expect(view.container.querySelector("video")).toBe(video);
  expect(video.currentTime).toBeCloseTo(100.5 / 30);
  expect(video.play).toHaveBeenCalledTimes(1);
  expect(usePlayback.getState().selection).toEqual(selection);
});
