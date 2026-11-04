import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { api, ApiError } from "@/lib/api";
import type { IndividualAnalyticsData } from "@/lib/types";
import { SESSION } from "@/test/fixtures";
import { IndividualAnalytics } from "./IndividualAnalytics";
import { PairAnalytics } from "./PairAnalytics";

const clients: QueryClient[] = [];
afterEach(() => {
  cleanup();
  for (const client of clients) client.clear();
  clients.length = 0;
  vi.restoreAllMocks();
});

const empty: IndividualAnalyticsData = {
  available: false,
  match_format: "singles",
  teams: {},
  participants: {},
  accounting: { total_shots: 0, attributed_shots: 0, unattributed_shots: 0 },
  unattributed_event_ids: [],
  legacy_unlinked_shots: 0,
  counting_scope: "reviewed",
};

function mount(component: "individual" | "pair") {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: 0 } } });
  clients.push(client);
  const view = render(
    <QueryClientProvider client={client}>
      {component === "individual" ? (
        <IndividualAnalytics session={SESSION} />
      ) : (
        <PairAnalytics session={SESSION} />
      )}
    </QueryClientProvider>,
  );
  return { ...view, client };
}

it.each(["individual", "pair"] as const)(
  "shows a failed %s analytics request instead of hiding it as missing evidence",
  async (component) => {
    vi.spyOn(api, "individualAnalytics").mockRejectedValue(
      new ApiError(503, "Reviewed analytics temporarily unavailable"),
    );
    mount(component);
    expect(await screen.findByText("Reviewed analytics temporarily unavailable")).toBeInTheDocument();
    expect(screen.queryByText("No pair positions have sufficient reviewed evidence yet.")).not.toBeInTheDocument();
  },
);

it.each(["individual", "pair"] as const)(
  "keeps a successful empty %s response distinct from a request failure",
  async (component) => {
    vi.spyOn(api, "individualAnalytics").mockResolvedValue(empty);
    const view = mount(component);
    await waitFor(() => expect(view.client.isFetching()).toBe(0));
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    if (component === "pair")
      expect(screen.getByText("No pair positions have sufficient reviewed evidence yet.")).toBeInTheDocument();
    else expect(view.container).toBeEmptyDOMElement();
  },
);
