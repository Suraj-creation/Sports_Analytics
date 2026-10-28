import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, fireEvent, render, screen } from "@testing-library/react";
import type { PropsWithChildren } from "react";
import { afterEach, expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import { usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";
import { SESSION } from "@/test/fixtures";
import { SessionPage } from "./SessionPage";

vi.mock("@tanstack/react-router", () => ({
  Link: ({ children }: PropsWithChildren) => <a href="#">{children}</a>,
  useParams: () => ({ sessionId: "s1" }),
  useSearch: () => ({}),
  useNavigate: () => vi.fn(),
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
vi.mock("./EpisodeMovement", () => ({ EpisodeMovement: () => null }));
vi.mock("./ReanalysisFeedback", () => ({ ReanalysisFeedback: () => null }));
vi.mock("./tabs/ExportTab", () => ({ ExportTab: () => null }));

const original = useSession.getState();
afterEach(() => {
  useSession.setState({ session: original.session, open: original.open, close: original.close });
  vi.restoreAllMocks();
});

it("retains exactly one roster and one review panel across playback and session updates", () => {
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
    expect(screen.getAllByText("Review player evidence")).toHaveLength(1);
    expect(screen.getAllByLabelText("Player 1 name")).toHaveLength(1);
    expect(screen.getByLabelText("Player 1 name")).toHaveValue("Alice");
  }
  expect(consoleError.mock.calls.flat().join(" ")).not.toMatch(/same key|unique .key. prop/i);
  view.unmount();
});
