import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import type { IndividualAnalyticsData } from "@/lib/types";
import { SESSION } from "@/test/fixtures";
import { IndividualAnalytics } from "./IndividualAnalytics";

it("shows four separate verified player totals and unresolved strokes", async () => {
  const result: IndividualAnalyticsData = {
    available: true, match_format: "doubles", teams: {},
    participants: Object.fromEntries(["Alice", "Bob", "Cara", "Dev"].map((name, i) => [`U${i}`, {
      name, team_id: null, total_shots: i, shot_distribution: {}, event_ids: [], events: [], rally_ids: [],
    }])),
    accounting: {total_shots: 9, attributed_shots: 6, unattributed_shots: 3},
    unattributed_event_ids: ["a", "b", "c"], legacy_unlinked_shots: 2, counting_scope: "test",
  };
  vi.spyOn(api, "individualAnalytics").mockResolvedValue(result);
  const queryClient = new QueryClient({defaultOptions: {queries: {retry: false}}});
  render(<QueryClientProvider client={queryClient}><IndividualAnalytics session={SESSION} /></QueryClientProvider>);
  expect(await screen.findByText("Alice")).toBeInTheDocument();
  expect(screen.getByText("Dev")).toBeInTheDocument();
  expect(screen.getByText(/3 unassigned/i)).toBeInTheDocument();
  expect(screen.getByText(/2 older shots/i)).toBeInTheDocument();
  vi.restoreAllMocks();
});
