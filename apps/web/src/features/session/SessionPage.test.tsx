import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { PropsWithChildren } from "react";
import { afterEach, expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import { usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";
import { SESSION } from "@/test/fixtures";
import { SessionPage } from "./SessionPage";

const navigation = vi.hoisted(() => vi.fn());
vi.mock("@tanstack/react-router", () => ({
  Link: ({ children }: PropsWithChildren) => <a href="/matches">{children}</a>,
  useParams: () => ({ sessionId: "s1" }),
  useSearch: () => ({}),
  useNavigate: () => navigation,
}));
vi.mock("@/features/analytics/SessionAnalytics", () => ({ SessionAnalytics: () => null }));
vi.mock("@/features/player/EvidenceDetails", () => ({ EvidenceDetails: () => null }));
vi.mock("@/features/player/VideoStage", () => ({ VideoStage: () => null }));
vi.mock("@/features/timeline/Timeline", () => ({ Timeline: () => null }));
vi.mock("./LiveFeed", () => ({ LiveFeed: () => null }));
vi.mock("./PlayerSelector", () => ({ PlayerSelector: () => null }));
vi.mock("./VisualObservations", () => ({ VisualObservations: () => null }));
vi.mock("./IndividualAnalytics", () => ({ IndividualAnalytics: () => null }));
vi.mock("./EstimatedIndividualAnalytics", () => ({ EstimatedIndividualAnalytics: () => null }));
vi.mock("./ReanalysisFeedback", () => ({ ReanalysisFeedback: () => null }));
vi.mock("./tabs/ExportTab", () => ({ ExportTab: () => null }));

const original = useSession.getState();
afterEach(() => {
  cleanup();
  useSession.setState({ session: original.session, open: original.open, close: original.close });
  vi.restoreAllMocks();
  navigation.mockClear();
});

it("retains one working roster and removes player review panels across live updates", () => {
  const session = { ...SESSION, roster: null };
  const open = vi.fn();
  const close = vi.fn();
  useSession.setState({ session, open, close });
  vi.spyOn(api, "session").mockResolvedValue(session);
  const consoleError = vi.spyOn(console, "error").mockImplementation(() => {});
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const view = render(<QueryClientProvider client={client}><SessionPage /></QueryClientProvider>);

  fireEvent.click(screen.getByRole("button", { name: /set up participants/i }));
  fireEvent.change(screen.getByLabelText("Match format"), { target: { value: "doubles" } });
  fireEvent.change(screen.getByLabelText("Player 1 name"), { target: { value: "Alice" } });

  for (const frame of [10, 25, 40]) {
    act(() => {
      usePlayback.setState({ frame });
      useSession.setState({ session: { ...session, frontier_frame: 6000 + frame } });
    });
    expect(screen.getAllByRole("heading", { name: "Participants" })).toHaveLength(1);
    expect(screen.queryByText("Review player evidence")).not.toBeInTheDocument();
    expect(screen.getAllByLabelText("Player 1 name")).toHaveLength(1);
    expect(screen.getByLabelText("Player 1 name")).toHaveValue("Alice");
  }
  expect(consoleError.mock.calls.flat().join(" ")).not.toMatch(/same key|unique .key. prop/i);
  view.unmount();
});

it("keeps the viewport position when switching every analysis tab", () => {
  const session = { ...SESSION, roster: null };
  useSession.setState({ session, open: vi.fn(), close: vi.fn() });
  vi.spyOn(api, "session").mockResolvedValue(session);
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(<QueryClientProvider client={client}><SessionPage /></QueryClientProvider>);
  for (const name of ["Moments", "Rallies", "Shots", "Tactics", "Court", "Movement", "Head to head", "Your pair", "Ask"]) {
    fireEvent.click(screen.getByRole("button", { name }));
    expect(navigation).toHaveBeenLastCalledWith(expect.objectContaining({ resetScroll: false }));
  }
});

it("redirects a reused-source import to its saved match without mounting a new workspace", () => {
  const session = { ...SESSION, meta: { reused_session_id: "saved-match" } };
  useSession.setState({ session, open: vi.fn(), close: vi.fn() });
  vi.spyOn(api, "session").mockResolvedValue(session);
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(<QueryClientProvider client={client}><SessionPage /></QueryClientProvider>);
  expect(navigation).toHaveBeenCalledWith(expect.objectContaining({
    to: "/matches/$matchId", params: { matchId: "saved-match" }, replace: true,
  }));
  expect(screen.queryByRole("heading", { name: "Participants" })).not.toBeInTheDocument();
});

it("reanalyses a completed match only after the expanded manual action is clicked", async () => {
  const session = { ...SESSION, status: "analysed" as const };
  useSession.setState({ session, open: vi.fn(), close: vi.fn() });
  vi.spyOn(api, "session").mockResolvedValue(session);
  const control = vi.spyOn(api, "control").mockResolvedValue({ status: "accepted" } as never);
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(<QueryClientProvider client={client}><SessionPage /></QueryClientProvider>);
  expect(control).not.toHaveBeenCalled();
  expect(screen.queryByRole("button", { name: "Analyse again" })).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Recording & quality" }));
  expect(screen.getByText(/backs up saved results.*reprocesses the video/i)).toBeVisible();
  expect(control).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole("button", { name: "Analyse again" }));
  await waitFor(() => expect(control).toHaveBeenCalledExactlyOnceWith("s1", "reanalyse"));
});

it.each(["analysing", "failed"] as const)("keeps completed-match reanalysis hidden while %s", (status) => {
  const session = { ...SESSION, status };
  useSession.setState({ session, open: vi.fn(), close: vi.fn() });
  vi.spyOn(api, "session").mockResolvedValue(session);
  const control = vi.spyOn(api, "control").mockResolvedValue({ status: "accepted" } as never);
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(<QueryClientProvider client={client}><SessionPage /></QueryClientProvider>);
  fireEvent.click(screen.getByRole("button", { name: "Recording & quality" }));
  expect(screen.queryByRole("button", { name: "Analyse again" })).not.toBeInTheDocument();
  if (status === "failed") expect(screen.getByRole("button", { name: "Retry analysis" })).toBeEnabled();
  expect(control).not.toHaveBeenCalled();
});
