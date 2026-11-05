import { act, cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import type { Session } from "@/lib/types";
import { usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";
import { SESSION } from "@/test/fixtures";
import { VideoStage } from "./VideoStage";
import type { HlsState } from "./useHls";

const transport = vi.hoisted(() => ({ state: "idle" as HlsState }));
vi.mock("./useHls", () => ({ useHls: () => transport.state }));
vi.mock("./ScoreBug", () => ({ ScoreBug: () => null }));
vi.mock("./StrokeToast", () => ({ StrokeToast: () => null }));
const originalSession = useSession.getState();
const originalPlayback = usePlayback.getState();
afterEach(() => {
  cleanup();
  useSession.setState(originalSession);
  usePlayback.setState(originalPlayback);
  vi.restoreAllMocks();
});

function show(state: HlsState, session: Session = { ...SESSION, status: "failed", media: null }, live = session) {
  transport.state = state;
  useSession.setState({ session: live });
  return render(<VideoStage session={session} controlsVisible={false} />);
}

it.each(["idle", "loading", "waiting", "error"] as const)(
  "explains unavailable failed playback in %s state without claiming it is loading",
  (state) => {
    show(state);
    expect(screen.getByText("Video unavailable")).toBeVisible();
    expect(screen.getByText(/Analysis stopped. Retry analysis or add another recording/)).toBeVisible();
    expect(screen.queryByText("Loading video")).not.toBeInTheDocument();
    expect(screen.queryByText(/Preparing the video/)).not.toBeInTheDocument();
    expect(screen.queryByText(/This browser can't play/)).not.toBeInTheDocument();
  },
);

it("does not turn a different session's status into failed-media progress", () => {
  const failed = { ...SESSION, status: "failed" as const, media: null };
  show("idle", failed, { ...SESSION, session_id: "other", status: "analysed" });
  expect(screen.getByText("Video unavailable")).toBeVisible();
});

it.each(["created", "ingesting"] as const)("preserves %s preparation before media exists", (status) => {
  show("idle", { ...SESSION, status, media: null });
  expect(screen.getByText("Preparing the video — playback starts with the first seconds")).toBeVisible();
  expect(screen.queryByText("Video unavailable")).not.toBeInTheDocument();
});

it.each(["loading", "waiting"] as const)("preserves normal %s playback loading", (state) => {
  show(state, { ...SESSION, status: "analysing" });
  expect(screen.getByText("Loading video")).toBeVisible();
  expect(screen.queryByText("Video unavailable")).not.toBeInTheDocument();
});

it("preserves completed-stream browser error information", () => {
  show("error", { ...SESSION, status: "analysed" });
  expect(screen.getByText(/This browser can't play the stream/)).toBeVisible();
});

it("keeps ready media visible after a later analysis failure", () => {
  show("ready", { ...SESSION, status: "failed" });
  expect(screen.queryByText("Video unavailable")).not.toBeInTheDocument();
  expect(screen.queryByText("Loading video")).not.toBeInTheDocument();
  expect(screen.getByLabelText(`Source recording: ${SESSION.title}`)).toBeInTheDocument();
});

it("preserves stream recovery when failed analysis already has media", () => {
  show("waiting", { ...SESSION, status: "failed" });
  expect(screen.getByText("Loading video")).toBeVisible();
  expect(screen.queryByText("Video unavailable")).not.toBeInTheDocument();
});

it("returns to normal preparation when the same failed recording is retried", () => {
  const failed = { ...SESSION, status: "failed" as const, media: null };
  const view = show("idle", failed);
  const video = view.container.querySelector("video");
  const retrying = { ...failed, status: "ingesting" as const };
  act(() => useSession.setState({ session: retrying }));
  view.rerender(<VideoStage session={retrying} controlsVisible={false} />);
  expect(screen.getByText(/Preparing the video/)).toBeVisible();
  expect(screen.queryByText("Video unavailable")).not.toBeInTheDocument();
  expect(view.container.querySelector("video")).toBe(video);
});
