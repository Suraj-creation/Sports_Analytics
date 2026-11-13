import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { PropsWithChildren } from "react";
import { afterEach, expect, it, vi } from "vitest";
import * as productApi from "@/features/product/api";
import type { MatchSummary, Overview } from "@/features/product/types";
import * as api from "@/lib/api";
import { SESSION } from "@/test/fixtures";
import { useCollection } from "./useCollection";

vi.mock("./providers", () => ({
  DEFAULT_EXAMPLE_SPORT: "badminton",
  highlightProvider: () => ({ fromRecording: () => null }),
}));
const clients: QueryClient[] = [];
afterEach(() => {
  for (const c of clients.splice(0)) c.clear();
  vi.restoreAllMocks();
});
const match = (id: string): MatchSummary => ({
  session: { ...SESSION, session_id: id },
  analytics: null,
  highlights: [],
  availability: { analytics: false, partial: false, reason: null },
  lineage: { event_seq: 0, source: "fixture", metric_version: 1 },
});
function show(sessionId: string) {
  vi.spyOn(productApi, "fetchOverview").mockResolvedValue({
    matches: [match("first"), match("second")],
    scope: { truncated: false },
  } as Overview);
  const request = vi.spyOn(api, "req").mockResolvedValue({});
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  clients.push(client);
  const wrapper = ({ children }: PropsWithChildren) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
  return { request, ...renderHook(() => useCollection("recordings", "doubles", sessionId, ""), { wrapper }) };
}
it("does not substitute another recording for an explicit unknown identifier", async () => {
  const { result, request } = show("missing");
  await waitFor(() => expect(result.current.loading).toBe(false));
  expect(result.current.error).toContain("selected recording is unavailable");
  expect(result.current.collection).toBeNull();
  expect(result.current.activeSessionId).toBe("missing");
  expect(request).not.toHaveBeenCalled();
});
it.each([
  ["", "first"],
  ["second", "second"],
])("resolves selection %s only to %s", async (selected, expected) => {
  const { result, request } = show(selected);
  await waitFor(() => expect(result.current.activeSessionId).toBe(expected));
  await waitFor(() =>
    expect(request).toHaveBeenCalledWith(`/api/sessions/${expected}/insights`, expect.any(Object)),
  );
  expect(result.current.missingSession).toBe(false);
});
