import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { EventLog } from "@/lib/events";
import { useSession } from "@/stores/session";
import { ev, SESSION } from "@/test/fixtures";
import { RalliesTab } from "./RalliesTab";

const original = useSession.getState();
afterEach(() => {
  useSession.setState(original);
  vi.unstubAllGlobals();
});

it("confirms a known winner through the score correction API and shows request feedback", async () => {
  const events = new EventLog();
  events.apply([
    ev("rally_end", 100, {
      event_id: "reviewed-rally",
      frame_end: 200,
      payload: { rally_no: 1, official: true, winner: "P1", outcome: "winner", shots: [] },
    }),
  ]);
  useSession.setState({ session: SESSION, events, eventsVersion: events.version });
  const requests: unknown[] = [];
  vi.stubGlobal("fetch", async (_url: string, init: RequestInit) => {
    const body = JSON.parse(String(init.body));
    requests.push(body);
    const accepted =
      body.kind === "winner" && body.rally_event_id === "reviewed-rally" && body.winner === "P1";
    return new Response(
      JSON.stringify(accepted ? { status: "accepted" } : { detail: "Use the score correction flow" }),
      {
        status: accepted ? 202 : 422,
      },
    );
  });
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={client}>
      <RalliesTab session={SESSION} selectedRally={1} />
    </QueryClientProvider>,
  );
  fireEvent.click(screen.getByRole("button", { name: "Confirm winner" }));
  await waitFor(() =>
    expect(requests).toEqual([{ kind: "winner", rally_event_id: "reviewed-rally", winner: "P1" }]),
  );
  expect(await screen.findByText(/Correction requested/)).toBeVisible();
  expect(screen.queryByText(/Correction saved/)).not.toBeInTheDocument();
});

it("uses stable candidate ordinals for unnumbered exchanges without inventing official rally numbers", () => {
  const events = new EventLog();
  events.apply([
    ev("rally_end", 100, {
      event_id: "candidate-a",
      frame_end: 200,
      payload: { rally_no: 0, official: false, shots: [] },
    }),
    ev("rally_end", 300, {
      event_id: "candidate-b",
      frame_end: 400,
      payload: { rally_no: 0, official: false, shots: [] },
    }),
    ev("rally_end", 500, {
      event_id: "official",
      frame_end: 600,
      payload: { rally_no: 5, official: true, shots: [] },
    }),
  ]);
  useSession.setState({ session: SESSION, events, eventsVersion: events.version });
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={client}>
      <RalliesTab session={SESSION} selectedRally={0} />
    </QueryClientProvider>,
  );
  expect(screen.getByText("Candidate 1").closest("details")).not.toHaveAttribute("open");
  expect(screen.getByText("Candidate 2").closest("details")).not.toHaveAttribute("open");
  expect(screen.getByText("Rally 5")).toBeInTheDocument();
  expect(screen.queryByText("Rally 0")).not.toBeInTheDocument();
  expect(screen.getByText("Recorded rally candidates")).toBeVisible();
  expect(screen.getByText(/3 recorded rally candidates/)).toBeVisible();
  expect(screen.queryByText(/3 observed rallies/)).not.toBeInTheDocument();
  fireEvent.change(screen.getByLabelText("Outcome"), { target: { value: "excluded" } });
  expect(screen.getByText("Candidate 1")).toBeInTheDocument();
  expect(screen.getByText("Candidate 2")).toBeInTheDocument();
});
