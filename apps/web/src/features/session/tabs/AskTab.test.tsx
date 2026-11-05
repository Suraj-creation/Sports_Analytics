import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import { EventLog } from "@/lib/events";
import { useSession } from "@/stores/session";
import { ev, SESSION } from "@/test/fixtures";
import { AskTab } from "./AskTab";

afterEach(() => vi.restoreAllMocks());

it.each([
  ["confirmed", "Estimated event"],
  ["human_verified", "Human reviewed event"],
] as const)("describes %s citation provenance separately from support band", async (status, label) => {
  const event = ev("stroke", 120, { status, band: "confirmed", payload: { stroke: "smash" } });
  const events = new EventLog();
  events.apply([event]);
  useSession.setState({ events, eventsVersion: events.version });
  vi.spyOn(api, "askProvider").mockResolvedValue({ available: false, provider: null, model: null });
  vi.spyOn(api, "ask").mockResolvedValue({
    text: `An estimated shot [[ev:${event.event_id}]].`,
    citations: [{ kind: "ev", ref: event.event_id, frame: 120, type: "stroke" }],
    grounded: true,
    issues: [],
    provider: "scripted",
    model: "contract",
  });
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={client}>
      <AskTab session={SESSION} />
    </QueryClientProvider>,
  );
  fireEvent.change(screen.getByLabelText("Question"), { target: { value: "What happened?" } });
  fireEvent.click(screen.getByRole("button", { name: "Ask" }));
  expect(await screen.findByTitle(`${label} at 0:04 · support band: confirmed`)).toBeInTheDocument();
  expect(screen.queryByTitle(/confirmed evidence/)).not.toBeInTheDocument();
});
