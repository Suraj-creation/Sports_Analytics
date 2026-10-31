import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import { SESSION } from "@/test/fixtures";
import { PairAnalytics } from "./PairAnalytics";

afterEach(() => vi.restoreAllMocks());

it("shows reviewed pair positions and individual contributions without inventing responsibility", async () => {
  vi.spyOn(api, "individualAnalytics").mockResolvedValue({
    available: true,
    match_format: "doubles",
    teams: {},
    participants: Object.fromEntries(
      ["Alice", "Bob", "Cara", "Dev"].map((name, index) => [
        String(index),
        {
          name,
          team_id: index < 2 ? "T1" : "T2",
          total_shots: index,
          shot_distribution: {},
          event_ids: [],
          events: [],
          rally_ids: [],
        },
      ]),
    ),
    accounting: { total_shots: 6, attributed_shots: 6, unattributed_shots: 0 },
    unattributed_event_ids: [],
    legacy_unlinked_shots: 0,
    counting_scope: "reviewed",
    pairs: {
      T1: {
        members: ["0", "1"],
        observed_frames: 30,
        front_back_frames: 20,
        side_by_side_frames: 10,
        front_seconds: { "0": 0.5, "1": 0.2 },
        rear_seconds: { "0": 0.2, "1": 0.5 },
        meaning: "positions",
      },
    },
  });
  render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <PairAnalytics session={SESSION} />
    </QueryClientProvider>,
  );
  expect(await screen.findByText("Alice & Bob")).toBeInTheDocument();
  expect(screen.getByText(/20 front\/back/)).toBeInTheDocument();
  expect(screen.getByText(/do not establish tactical responsibility/)).toBeInTheDocument();
});
