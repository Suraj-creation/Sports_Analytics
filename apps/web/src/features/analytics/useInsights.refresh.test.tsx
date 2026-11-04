import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, cleanup, renderHook, waitFor } from "@testing-library/react";
import type { PropsWithChildren } from "react";
import { afterEach, expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import type { Heatmap } from "@/lib/types";
import { useSession } from "@/stores/session";
import { SESSION } from "@/test/fixtures";
import { useMeasuredMovement } from "./useInsights";

const original = useSession.getState();
const clients: QueryClient[] = [];
afterEach(() => {
  cleanup();
  for (const client of clients) client.clear();
  clients.length = 0;
  useSession.setState(original);
  vi.restoreAllMocks();
});

function heatmap(total: number): Heatmap {
  return { player: "P1", kind: "presence", cell_m: 1, origin_m: [0, 0], shape: [1, 1], total, values: [[1]] };
}

it.each([[10, 0], [0, 10]])(
  "refreshes movement support from %s to %s after a same-generation rally correction",
  async (before, after) => {
    const session = { ...SESSION, status: "analysed" as const };
    useSession.setState({
      session,
      analyticsVersion: 0,
      calibration: {
        H: [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        reprojection_error_px: 0,
        n_points: 4,
      },
    });
    vi.spyOn(api, "heatmap").mockResolvedValueOnce(heatmap(before)).mockResolvedValueOnce(heatmap(after));
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false, staleTime: Infinity, gcTime: 0 } },
    });
    clients.push(client);
    const wrapper = ({ children }: PropsWithChildren) => (
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    );
    const { result } = renderHook(() => useMeasuredMovement(session, "P1"), { wrapper });
    await waitFor(() => expect(result.current.data?.total).toBe(before));
    // A committed correction changes available rally support without changing analysis_revision.
    act(() => useSession.setState({ analyticsVersion: 1 }));
    await waitFor(() => expect(result.current.data?.total).toBe(after));
  },
);
