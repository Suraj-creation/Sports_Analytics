import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { Timeline } from "@/features/timeline/Timeline";
import { ExportTab } from "@/features/session/tabs/ExportTab";
import { EventLog } from "@/lib/events";
import type { Session } from "@/lib/types";
import { useSession } from "@/stores/session";
import { SESSION } from "@/test/fixtures";

vi.mock("@/features/library/Thumb", () => ({ useSprite: () => ({ data: null }), spriteStyle: () => null }));
const original = useSession.getState();
afterEach(() => { cleanup(); useSession.setState(original); vi.restoreAllMocks(); });

function timeline(session: Session, live = session) {
  const events = new EventLog();
  useSession.setState({ session: live, events, eventsVersion: events.version });
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(<QueryClientProvider client={client}><Timeline session={session} /></QueryClientProvider>);
}

it("shows unknown coverage for a failed source with no media instead of 100 percent", () => {
  timeline({ ...SESSION, media: null, status: "failed", frontier_frame: 0, analysed_frames: 0 });
  expect(screen.getByText("Analysis coverage unavailable")).toBeVisible();
  expect(screen.queryByText("100% of analysis proxy frames processed")).not.toBeInTheDocument();
});
it("does not count the default frontier frame as a processed frame", () => {
  timeline({ ...SESSION, status: "analysing", frontier_frame: 0, analysed_frames: 0,
    media: { ...SESSION.media!, n_frames: 1 } });
  expect(screen.getByText("0% of analysis proxy frames processed")).toBeVisible();
});
it("preserves partial coverage and does not convert failure into completion", () => {
  timeline({ ...SESSION, status: "failed", frontier_frame: 29, analysed_frames: 30,
    media: { ...SESSION.media!, n_frames: 60 } });
  expect(screen.getByText("50% of analysis proxy frames processed")).toBeVisible();
});
it("preserves completed coverage for all frames", () => {
  timeline({ ...SESSION, status: "analysed", frontier_frame: 66, analysed_frames: 67,
    media: { ...SESSION.media!, n_frames: 67 } });
  expect(screen.getByText("100% of analysis proxy frames processed")).toBeVisible();
});
it("does not borrow the progress of a different active session", () => {
  const own = { ...SESSION, status: "failed" as const, frontier_frame: 29, analysed_frames: 30,
    media: { ...SESSION.media!, n_frames: 60 } };
  timeline(own, { ...own, session_id: "foreign", status: "analysed", frontier_frame: 59, analysed_frames: 60 });
  expect(screen.getByText("50% of analysis proxy frames processed")).toBeVisible();
});
it("tells failed-export users that the results are partial", () => {
  render(<ExportTab session={{ ...SESSION, status: "failed" }} />);
  expect(screen.getByText("Analysis stopped before completion — exports contain partial results.")).toBeVisible();
  expect(screen.queryByText(/Analysis is still running/)).not.toBeInTheDocument();
  expect(screen.getByRole("link", { name: /Rallies table/ })).toHaveAttribute("href", "/api/sessions/s1/exports/rallies.csv");
});
it("preserves in-progress export wording", () => {
  render(<ExportTab session={SESSION} />);
  expect(screen.getByText("Analysis is still running — exports include everything analysed so far.")).toBeVisible();
});
it("does not label completed exports as partial", () => {
  render(<ExportTab session={{ ...SESSION, status: "analysed" }} />);
  expect(screen.queryByText(/partial results|still running/)).not.toBeInTheDocument();
});
