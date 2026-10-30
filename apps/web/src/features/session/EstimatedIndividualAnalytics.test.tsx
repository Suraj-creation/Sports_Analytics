import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import type { EstimatedIndividualAnalyticsData } from "@/lib/types";
import { SESSION } from "@/test/fixtures";
import { EstimatedIndividualAnalytics } from "./EstimatedIndividualAnalytics";

it("shows estimated players separately from verified totals and unresolved candidates", async () => {
  const scope = {participants: {U1: {name: "Alice", team_id: "T1", estimated_shots: 3, shot_distribution: {unknown: 3}, events: []}},
    accounting: {total_linked_shots: 5, estimated_shots: 3, unresolved_shots: 2}, unresolved_event_ids: ["x", "y"], legacy_unlinked_shots: 1};
  const episodes = {episodes: [{observation_id: "obs1", participant_id: "episode1", track_id: 7, candidate_shots: 2, shot_distribution: {unknown: 2}, detector_run_counts: {ran: 1, not_run: 1, unknown: 0}, events: [], status: "anonymous_track_episode"}], accounting: {total_linked_shots: 5, episode_candidate_shots: 2, unresolved_shots: 3}, unresolved_event_ids: []};
  const data: EstimatedIndividualAnalyticsData & {episode_profiles: unknown} = {episode_profiles: {official: episodes, all_linked: episodes}, available: true, match_format: "doubles", official: scope, all_linked: scope, unlinked_stroke_events: 0, policy: {}};
  vi.spyOn(api, "estimatedIndividualAnalytics").mockResolvedValue(data);
  const client = new QueryClient({defaultOptions: {queries: {retry: false}}});
  render(<QueryClientProvider client={client}><EstimatedIndividualAnalytics session={{...SESSION, roster: {match_format: "doubles", teams: [], participants: []}}} /></QueryClientProvider>);
  expect(await screen.findByText("Alice")).toBeInTheDocument();
  expect(screen.getByText(/3 estimated shots/i)).toBeInTheDocument();
  expect(screen.getByText(/2 unresolved/i)).toBeInTheDocument();
  expect(screen.getByText(/not verified/i)).toBeInTheDocument();
  expect(screen.queryByText(/Track 7/)).not.toBeInTheDocument();
  expect(screen.queryByText(/Anonymous track episodes/i)).not.toBeInTheDocument();

  vi.restoreAllMocks();
});


it("hides anonymous candidates when no named estimates are available", () => {
  const scope = {participants: {}, accounting: {total_linked_shots: 1, estimated_shots: 0, unresolved_shots: 1}, unresolved_event_ids: ["x"], legacy_unlinked_shots: 0};
  const episodes = {episodes: [{observation_id: "obs2", participant_id: "episode2", track_id: 9, candidate_shots: 1, shot_distribution: {}, detector_run_counts: {ran: 0, not_run: 1, unknown: 0}, events: [], status: "anonymous_track_episode"}], accounting: {total_linked_shots: 1, episode_candidate_shots: 1, unresolved_shots: 0}, unresolved_event_ids: []};
  const data: EstimatedIndividualAnalyticsData & {episode_profiles: unknown} = {available: false, match_format: null, official: scope, all_linked: scope, episode_profiles: {official: episodes, all_linked: episodes}, unlinked_stroke_events: 0, policy: {}};
  vi.spyOn(api, "estimatedIndividualAnalytics").mockResolvedValue(data);
  const client = new QueryClient({defaultOptions: {queries: {retry: false, staleTime: Infinity}}});
  client.setQueryData(["estimated-individual-analytics", SESSION.session_id], data);
  render(<QueryClientProvider client={client}><EstimatedIndividualAnalytics session={{...SESSION, roster: null}} /></QueryClientProvider>);
  expect(screen.queryByText(/Track 9/)).not.toBeInTheDocument();
  expect(screen.queryByRole("heading", {name: "Automatic player estimates"})).not.toBeInTheDocument();
  vi.restoreAllMocks();
});
