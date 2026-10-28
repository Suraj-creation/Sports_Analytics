import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { usePlayback } from "@/stores/playback";
import { ev, SESSION } from "@/test/fixtures";
import { VisualObservations } from "./VisualObservations";

function openView() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={client}>
      <VisualObservations session={SESSION} />
    </QueryClientProvider>,
  );
  fireEvent.click(screen.getByText("Visual track observations"));
}

afterEach(() => vi.restoreAllMocks());

it("shows unlinked track hypotheses and resets, and opens the actual event clip", async () => {
  const first = ev("participant_observation", 120, {
    event_id: "track-a",
    status: "provisional",
    payload: {
      kind: "PLAYER_ENTERED",
      participant_id: "participant-a1b2-000001",
      track_id: 7,
      side: "near",
      certainty: "hypothesis",
    },
  });
  const reset = ev("identity_ambiguity", 180, {
    event_id: "reset",
    status: "provisional",
    payload: { reason: "visual_tracker_reset", tracker_instance: "c3d4" },
  });
  const next = ev("participant_observation", 210, {
    event_id: "track-b",
    status: "provisional",
    payload: {
      kind: "PARTICIPANT_FIRST_OBSERVED",
      participant_id: "participant-c3d4-000001",
      track_id: 7,
      side: "far",
      certainty: "hypothesis",
    },
  });
  const query = vi
    .spyOn(globalThis, "fetch")
    .mockResolvedValue(
      new Response(JSON.stringify({ last_seq: 3, events: [first, reset, next] }), { status: 200 }),
    );
  usePlayback.setState({ selection: null, video: null });
  openView();
  expect(await screen.findByText(/Unlinked visual track observations/)).toBeInTheDocument();
  expect(query).toHaveBeenCalledWith(
    expect.stringContaining("/api/sessions/s1/events?types=participant_observation%2Cidentity_ambiguity"),
    expect.objectContaining({ signal: expect.any(AbortSignal) }),
  );
  expect(await screen.findByText(/Epoch a1b2/)).toBeInTheDocument();
  expect(screen.getByText(/Epoch c3d4/)).toBeInTheDocument();
  expect(screen.getByText(/Tracking continuity uncertain/)).toBeInTheDocument();
  expect(screen.getAllByText(/Track 7/)).toHaveLength(2);
  fireEvent.click(screen.getByRole("button", { name: /Watch observation at 0:04/ }));
  expect(usePlayback.getState().selection).toMatchObject({ start: 120, eventId: "track-a" });
});

it("does not turn missing evidence into a claim that no people were present", async () => {
  vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(JSON.stringify({ last_seq: 0, events: [] }), { status: 200 }),
  );
  openView();
  expect(await screen.findByText(/No visual track observations were recorded/)).toBeInTheDocument();
  expect(screen.getByText(/does not establish that nobody was present/)).toBeInTheDocument();
});

it("discloses when the visible list is truncated and reveals more on request", async () => {
  const events = Array.from({ length: 51 }, (_, index) =>
    ev("participant_observation", index, {
      status: "provisional",
      payload: { kind: "PLAYER_ENTERED", participant_id: `participant-a1-000${index}`, track_id: index },
    }),
  );
  vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(JSON.stringify({ last_seq: 51, events }), { status: 200 }),
  );
  openView();
  expect(await screen.findByText(/Showing the first 50 entries/)).toBeInTheDocument();
  expect(screen.getAllByRole("listitem")).toHaveLength(50);
  fireEvent.click(screen.getByRole("button", { name: "Show more observations" }));
  expect(screen.getAllByRole("listitem")).toHaveLength(51);
  expect(screen.queryByText(/Showing the first 50 entries/)).not.toBeInTheDocument();
});

it("cancels the old session request and does not show its data after switching sessions", async () => {
  let oldSignal: AbortSignal | undefined;
  const fetcher = vi
    .spyOn(globalThis, "fetch")
    .mockImplementationOnce((_input, init) => {
      oldSignal = init?.signal as AbortSignal;
      return new Promise((_resolve, reject) =>
        oldSignal?.addEventListener("abort", () => reject(new DOMException("Aborted", "AbortError"))),
      );
    })
    .mockResolvedValueOnce(new Response(JSON.stringify({ last_seq: 0, events: [] }), { status: 200 }));
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const view = render(
    <QueryClientProvider client={client}>
      <VisualObservations session={SESSION} />
    </QueryClientProvider>,
  );
  fireEvent.click(screen.getByText("Visual track observations"));
  await waitFor(() => expect(fetcher).toHaveBeenCalledTimes(1));
  view.rerender(
    <QueryClientProvider client={client}>
      <VisualObservations session={{ ...SESSION, session_id: "s2" }} />
    </QueryClientProvider>,
  );
  expect(await screen.findByText(/No visual track observations were recorded/)).toBeInTheDocument();
  expect(oldSignal?.aborted).toBe(true);
  expect(fetcher).toHaveBeenCalledTimes(2);
});
