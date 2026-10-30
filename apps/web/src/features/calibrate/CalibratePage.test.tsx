import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { PropsWithChildren } from "react";
import { afterEach, expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import { SESSION } from "@/test/fixtures";
import { CalibratePage } from "./CalibratePage";
vi.mock("@tanstack/react-router", () => ({
  Link: ({ children }: PropsWithChildren) => <a href="/sessions/s1">{children}</a>,
  useParams: () => ({ sessionId: "s1" }), useNavigate: () => vi.fn(),
}));
vi.mock("@/features/player/useHls", () => ({ useHls: () => "ready" }));
afterEach(() => vi.restoreAllMocks());
const reference: Record<string, [number, number]> = { near_left: [0, 0], near_right: [6, 0], far_right: [6, 13], far_left: [0, 13], net_left: [0, 6.5], net_right: [6, 6.5] };
const detected = Object.fromEntries(Object.entries(reference).map(([id, [x, y]]) => [id, [x * 20 + 10, y * 20 + 10]])) as Record<string, [number, number]>;
async function show(refFrame = 0) {
  vi.spyOn(HTMLMediaElement.prototype, "pause").mockImplementation(() => {});
  vi.spyOn(api, "session").mockResolvedValue(SESSION);
  vi.spyOn(api, "calibrationProposal").mockResolvedValue({
    frame: 0, width: 1280, height: 720, reference_points: reference,
    proposal: { method: "court_lines_v1", score: 0.9, points: detected },
    current: { H: [[10, 0, 50], [0, 10, 100], [0, 0, 1]], reprojection_error_px: 0, n_points: 6, source: "human", mode: "camera", ref_frame: refFrame },
  });
  const save = vi.spyOn(api, "calibrate").mockResolvedValue({ reprojection_error_px: 0, n_points: 6 });
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(<QueryClientProvider client={client}><CalibratePage /></QueryClientProvider>);
  await waitFor(() => expect(screen.getByRole("button", { name: "Save calibration" })).toBeEnabled(), { timeout: 5000 });
  return save;
}
it("restores saved manual points on their reference frame before a new detector proposal", async () => {
  const save = await show();
  fireEvent.click(screen.getByRole("button", { name: "Save calibration" }));
  await waitFor(() => expect(save).toHaveBeenCalled());
  expect(save.mock.calls[0]?.[1].near_left).toEqual([50, 100]);
  expect(save.mock.calls[0]?.[1].far_right).toEqual([110, 230]);
});
it("uses a fresh proposal for a different camera frame and keeps Use detected available", async () => {
  const save = await show(500);
  expect(screen.getByRole("button", { name: "Use detected" })).toBeEnabled();
  fireEvent.click(screen.getByRole("button", { name: "Save calibration" }));
  await waitFor(() => expect(save).toHaveBeenCalled());
  expect(save.mock.calls[0]?.[1]).toEqual(detected);
});

it("replaces restored saved points with detected points only after Use detected is chosen", async () => {
  const save = await show();
  fireEvent.click(screen.getByRole("button", { name: "Use detected" }));
  fireEvent.click(screen.getByRole("button", { name: "Save calibration" }));
  await waitFor(() => expect(save).toHaveBeenCalled());
  expect(save.mock.calls[0]?.[1]).toEqual(detected);
});
