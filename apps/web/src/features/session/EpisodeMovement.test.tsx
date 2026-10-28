import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import { SESSION } from "@/test/fixtures";
import { EpisodeMovement } from "./EpisodeMovement";

it("shows calibrated movement only for a requested anonymous track window", async () => {
  const spy = vi.spyOn(api, "episodeMovement").mockResolvedValue({available: true, reason: null, scope: "anonymous_track_episodes_not_people", window: {from: 0, to: 900, fps: 30}, episodes: [{observation_id: "obs1", participant_id: "episode1", track_id: 7, status: "estimated", distance_m: 2.4, valid_frames: 10, detector_observed_frames: 4, carried_frames: 6, unknown_source_frames: 0, coverage_fraction: 0.1, observed_seconds: 1, segments: 1, positions_m: []}], warning: "Provisional"});
  const client = new QueryClient({defaultOptions: {queries: {retry: false}}});
  render(<QueryClientProvider client={client}><EpisodeMovement session={SESSION} /></QueryClientProvider>);
  expect(spy).not.toHaveBeenCalled();
  fireEvent.click(screen.getByText("Court movement by track"));
  fireEvent.click(screen.getByRole("button", {name: "Inspect movement near this frame"}));
  expect(await screen.findByText(/Track 7/)).toBeInTheDocument();
  expect(screen.getByText(/2.4 m/)).toBeInTheDocument();
  expect(screen.getByText(/4 detector-run, 6 carried/)).toBeInTheDocument();
  expect(screen.getByText(/not a full-match distance/i)).toBeInTheDocument();
  vi.restoreAllMocks();
});
