import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { ev, SESSION } from "@/test/fixtures";
import { IdentityReviewPanel } from "./IdentityReviewPanel";

afterEach(() => vi.restoreAllMocks());

it("associates any of four named roster people with an explicit track interval and revision", async () => {
  const birth = ev("participant_observation", 10, {
    event_id: "birth",
    payload: {
      kind: "PLAYER_ENTERED",
      participant_id: "participant-abcd-000001",
      track_id: 7,
    },
  });
  const requests: { path: string; body: unknown }[] = [];
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input, init) => {
    const path = String(input);
    if (init?.method === "POST") {
      requests.push({ path, body: JSON.parse(String(init.body)) });
      return new Response(JSON.stringify(ev("identity_review", 10)), { status: 201 });
    }
    return new Response(
      JSON.stringify(
        path.includes("/events?") ? { events: [] } : { analysis_revision: 2, events: [], stroke_reviews: [] },
      ),
      { status: 200 },
    );
  });
  const session = {
    ...SESSION,
    status: "analysed" as const,
    meta: { analysis_revision: 2 },
    roster: {
      match_format: "doubles" as const,
      teams: [],
      participants: ["Alice", "Bob", "Cara", "Dev"].map((name, i) => ({
        participant_id: `person-${i}`,
        name,
        team_id: null,
      })),
    },
  };
  render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <IdentityReviewPanel session={session} observations={[birth]} />
    </QueryClientProvider>,
  );
  await screen.findByRole("option", { name: "Dev" });
  fireEvent.change(screen.getByLabelText("Roster participant"), { target: { value: "person-3" } });
  fireEvent.change(screen.getByLabelText("Through frame"), { target: { value: "80" } });
  fireEvent.click(screen.getByRole("button", { name: "Confirm player interval" }));
  await waitFor(() => expect(requests).toHaveLength(1));
  expect(requests[0]).toEqual({
    path: "/api/sessions/s1/identity-reviews",
    body: {
      observation_id: "birth",
      participant_id: "person-3",
      start: 10,
      end: 80,
      analysis_revision: 2,
    },
  });
});

it("keeps the revoke control when a reviewed shot is corrected", async () => {
  const birth = ev("participant_observation", 1, {
    event_id: "birth",
    payload: { kind: "PLAYER_ENTERED", track_id: 7 },
  });
  const review = ev("identity_review", 1, {
    event_id: "identity",
    frame_end: 50,
    actors: { player_id: "person-a", track_id: 7, opponent_id: null },
    payload: { observation_id: "birth" },
  });
  const corrected = ev("stroke", 10, {
    event_id: "corrected",
    supersedes: "original",
    status: "corrected",
    payload: { stroke: "clear", participant_hypothesis: { observation_id: "birth" } },
  });
  vi.spyOn(globalThis, "fetch").mockImplementation(
    async (input) =>
      new Response(
        JSON.stringify(
          String(input).includes("/events?")
            ? { events: [corrected] }
            : {
                analysis_revision: 2,
                events: [review],
                stroke_reviews: [
                  {
                    ...ev("stroke_participant_review", 10, {
                      payload: { stroke_event_id: "original", identity_review_id: "identity" },
                    }),
                    current_stroke_event_id: "corrected",
                  },
                ],
              },
        ),
        { status: 200 },
      ),
  );
  render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <IdentityReviewPanel
        session={{
          ...SESSION,
          status: "analysed",
          meta: { analysis_revision: 2 },
          roster: {
            match_format: "doubles",
            teams: [],
            participants: [{ participant_id: "person-a", name: "Alice", team_id: null }],
          },
        }}
        observations={[birth]}
      />
    </QueryClientProvider>,
  );
  expect(await screen.findByRole("button", { name: "Revoke hitter review" })).toBeInTheDocument();
});
