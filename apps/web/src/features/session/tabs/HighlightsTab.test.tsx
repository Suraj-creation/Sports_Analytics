import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { playEvidence } from "@/features/player/clip";
import { api } from "@/lib/api";
import type { Highlight } from "@/lib/types";
import { SESSION } from "@/test/fixtures";
import { HighlightsTab } from "./HighlightsTab";

vi.mock("@/features/player/clip", () => ({ playEvidence: vi.fn() }));
const clients: QueryClient[] = [];
afterEach(() => {
  for (const c of clients.splice(0)) c.clear();
  vi.restoreAllMocks();
});
function show(highlight: Highlight) {
  vi.spyOn(api, "highlights").mockResolvedValue({ highlights: [highlight] });
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  clients.push(client);
  render(
    <QueryClientProvider client={client}>
      <HighlightsTab session={SESSION} />
    </QueryClientProvider>,
  );
}
const base: Highlight = {
  rally_id: "rally-event",
  rally_no: 1,
  frame_start: 100,
  frame_end: 200,
  score: 4,
  categories: [],
  reasons: { length: 4 },
  player: null,
};
it("retains evidence qualification and navigates with the canonical source event", async () => {
  show({
    ...base,
    evidence_status: "estimated_events",
    score_semantics: "ranking_score_not_probability",
    evidence_ids: ["rally-event", "stroke-event"],
  });
  expect(await screen.findByText(/Evidence: estimated events · 2 linked source events/)).toBeVisible();
  expect(screen.getByText("Ranking score, not a probability")).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: "Play rally 1" }));
  expect(playEvidence).toHaveBeenCalledWith(100, 200, "Rally 1", "rally-event");
});
it("backreads legacy rankings without inventing evidence provenance", async () => {
  show(base);
  expect(await screen.findByText(/Evidence status unavailable for this saved ranking/)).toBeVisible();
  expect(screen.getByText(/Source event list unavailable/)).toBeVisible();
});
