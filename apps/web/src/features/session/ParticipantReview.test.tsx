import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { frameClock } from "@/lib/frameClock";
import { usePlayback } from "@/stores/playback";
import { ev, SESSION } from "@/test/fixtures";
import { ParticipantReview } from "./ParticipantReview";

afterEach(() => { vi.unstubAllGlobals(); usePlayback.setState({video: null, reviewBox: null}); });

it("requires an explicit person and frame interval before saving a track review", async () => {
  const obs = ev("participant_observation", 40, {payload: {kind: "PLAYER_ENTERED", track_id: 7, participant_id: "participant-abc-000001"}});
  const fetcher = vi.fn(async (url: string, init?: RequestInit) => {
    const data = url.includes("/box?") ? {available: true, frame: 40, bbox: [1, 2, 30, 40]} : url.includes("events?") ? {events: [obs]} : url.endsWith("identity-reviews") && init?.method === "POST" ? {} : [];
    return new Response(JSON.stringify(data), {status: 200, headers: {"Content-Type": "application/json"}});
  });
  vi.stubGlobal("fetch", fetcher);
  const session = {...SESSION, roster: {match_format: "doubles" as const, teams: [], participants: [
    {participant_id: "U1", name: "Alice", team_id: null},
  ]}};
  const video = document.createElement("video");
  video.pause = vi.fn();
  usePlayback.setState({video});
  const client = new QueryClient({defaultOptions: {queries: {retry: false}}});
  render(<QueryClientProvider client={client}><ParticipantReview session={session}/></QueryClientProvider>);
  fireEvent.click(screen.getByText("Review player evidence"));
  await screen.findByRole("option", {name: /Track 7/});
  fireEvent.change(screen.getByLabelText("Track observation"), {target: {value: obs.event_id}});
  fireEvent.change(screen.getByLabelText("Person"), {target: {value: "U1"}});
  fireEvent.change(screen.getByLabelText("Reviewed frame"), {target: {value: "40"}});
  expect(screen.getByRole("button", {name: "Confirm reviewed frame"})).toBeDisabled();
  fireEvent.click(screen.getByRole("button", {name: "Show track box on video"}));
  await waitFor(() => expect(video.currentTime).toBeGreaterThan(1));
  frameClock.publish(40);
  fireEvent(video, new Event("seeked"));
  await waitFor(() => expect(screen.getByRole("button", {name: "Confirm reviewed frame"})).toBeEnabled());
  expect(usePlayback.getState().reviewBox?.trackId).toBe(7);
  fireEvent.click(screen.getByRole("button", {name: "Confirm reviewed frame"}));
  await waitFor(() => expect(fetcher.mock.calls.some(([url, init]) => url.endsWith("/identity-reviews") && init?.method === "POST")).toBe(true));
  const call = fetcher.mock.calls.find(([url, init]) => url.endsWith("/identity-reviews") && init?.method === "POST");
  expect(JSON.parse(String(call?.[1]?.body))).toEqual({observation_id: obs.event_id, player_id: "U1", frame_start: 40, frame_end: 40});
});

it("requires a separate watched shot and track preview before confirming its player", async () => {
  const obs = ev("participant_observation", 40, {payload: {kind: "PLAYER_ENTERED", track_id: 7, participant_id: "participant-abc-000001"}});
  const shot = ev("stroke", 40, {payload: {stroke: "unknown", participant_hypothesis: {participant_id: "participant-abc-000001", track_id: 7}}});
  const identity = {...ev("identity_review", 40, {payload: {observation_id: obs.event_id, participant_id: "participant-abc-000001"}}), actors: {player_id: "U1", track_id: 7, opponent_id: null}};
  vi.stubGlobal("fetch", vi.fn(async (url: string) => {
    const data = url.includes("/box?") ? {available: true, frame: 40, bbox: [1, 2, 30, 40]} : url.includes("events?") ? {events: [obs, shot]} : url.endsWith("/identity-reviews") ? [identity] : [];
    return new Response(JSON.stringify(data), {status: 200, headers: {"Content-Type": "application/json"}});
  }));
  const video = document.createElement("video");
  video.pause = vi.fn();
  usePlayback.setState({video});
  const session = {...SESSION, roster: {match_format: "doubles" as const, teams: [], participants: [{participant_id: "U1", name: "Alice", team_id: null}]}};
  const client = new QueryClient({defaultOptions: {queries: {retry: false}}});
  render(<QueryClientProvider client={client}><ParticipantReview session={session}/></QueryClientProvider>);
  fireEvent.click(screen.getByText("Review player evidence"));
  await screen.findByRole("option", {name: /Alice · track 7/});
  fireEvent.change(screen.getByLabelText("Reviewed interval"), {target: {value: identity.event_id}});
  fireEvent.change(screen.getByLabelText("Shot candidate"), {target: {value: shot.event_id}});
  expect(screen.getByRole("button", {name: "Confirm player for shot"})).toBeDisabled();
  expect(screen.getByRole("button", {name: "Show shot track box"})).toBeDisabled();
  Object.defineProperty(video, "paused", {value: false, configurable: true});
  fireEvent.click(screen.getByRole("button", {name: "Watch shot"}));
  expect(screen.getByRole("button", {name: "Show shot track box"})).toBeDisabled();
  act(() => { frameClock.publish(39); frameClock.publish(40); });
  await waitFor(() => expect(screen.getByRole("button", {name: "Show shot track box"})).toBeEnabled());
  fireEvent.click(screen.getByRole("button", {name: "Show shot track box"}));
  await waitFor(() => expect(video.currentTime).toBeGreaterThan(1));
  frameClock.publish(40);
  fireEvent(video, new Event("seeked"));
  await waitFor(() => expect(screen.getByRole("button", {name: "Confirm player for shot"})).toBeEnabled());
});
