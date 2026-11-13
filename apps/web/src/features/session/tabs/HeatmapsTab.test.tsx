import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import { useSession } from "@/stores/session";
import { SESSION } from "@/test/fixtures";
import { HeatmapsTab } from "./HeatmapsTab";

const original = useSession.getState();
const clients: QueryClient[] = [];
afterEach(() => {
  act(() => useSession.setState(original));
  for (const c of clients.splice(0)) c.clear();
  vi.restoreAllMocks();
});
function show(kind: string, total: number) {
  useSession.setState({
    calibration: {
      H: [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
      ],
      reprojection_error_px: 0,
      n_points: 4,
    },
  });
  vi.spyOn(api, "heatmap").mockResolvedValue({
    player: "P1",
    kind,
    cell_m: 1,
    origin_m: [0, 0],
    shape: [1, 1],
    total,
    values: [[1]],
  });
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  clients.push(client);
  render(
    <QueryClientProvider client={client}>
      <HeatmapsTab session={SESSION} selectedPlayer="P1" initialKind={kind} />
    </QueryClientProvider>,
  );
}
it("labels distance-weighted movement in metres rather than as a detection count", async () => {
  show("movement", 12.5);
  expect(await screen.findByText("12.5 m of estimated travel")).toBeVisible();
  expect(screen.queryByText("13 samples")).not.toBeInTheDocument();
});
it("labels sampled presence without claiming dwell time", async () => {
  show("presence", 3);
  expect(await screen.findByText("3 samples")).toBeVisible();
  expect(screen.getByText("Sampled feet positions during qualified rally intervals")).toBeVisible();
  expect(screen.queryByText(/Time spent/)).not.toBeInTheDocument();
});
