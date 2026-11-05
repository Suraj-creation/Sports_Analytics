import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, render, waitFor } from "@testing-library/react";
import type { PropsWithChildren } from "react";
import { afterEach, expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import { SESSION } from "@/test/fixtures";
import { useSession } from "@/stores/session";
import { CalibratePage } from "./CalibratePage";

vi.mock("@tanstack/react-router", () => ({
  Link: ({ children }: PropsWithChildren) => <a href="/sessions/s1">{children}</a>,
  useParams: () => ({ sessionId: "s1" }),
  useNavigate: () => vi.fn(),
}));
vi.mock("@/features/player/useHls", () => ({ useHls: () => "ready" }));

const initialStore = useSession.getState();
const clients: QueryClient[] = [];
const observers: MutationObserver[] = [];
afterEach(() => {
  for (const observer of observers.splice(0)) observer.disconnect();
  cleanup();
  for (const client of clients.splice(0)) client.clear();
  useSession.setState(initialStore);
  vi.restoreAllMocks();
});

const reference: Record<string, [number, number]> = {
  near_left: [0, 0], near_right: [6, 0], far_right: [6, 13],
  far_left: [0, 13], net_left: [0, 6.5], net_right: [6, 6.5],
};
const detected = Object.fromEntries(Object.entries(reference).map(([id, [x, y]]) =>
  [id, [x * 20 + 10, y * 20 + 10]],
)) as Record<string, [number, number]>;

it.each([
  { revision: 0, refFrame: 0, expected: [50, 100] },
  { revision: 77, refFrame: 0, expected: [50, 100] },
  { revision: 0, refFrame: 500, expected: [10, 10] },
])("saves rendered points at first enabled commit (revision $revision, reference $refFrame)", async ({ revision, refFrame, expected }) => {
  useSession.setState({ session: { ...SESSION, meta: { analysis_revision: revision } } });
  vi.spyOn(HTMLMediaElement.prototype, "pause").mockImplementation(() => {});
  vi.spyOn(api, "session").mockResolvedValue(SESSION);
  vi.spyOn(api, "calibrationProposal").mockResolvedValue({
    frame: 0, width: 1280, height: 720, reference_points: reference,
    proposal: { method: "court_lines_v1", score: 0.9, points: detected },
    current: {
      H: [[10, 0, 50], [0, 10, 100], [0, 0, 1]], reprojection_error_px: 0,
      n_points: 6, source: "human", mode: "camera", ref_frame: refFrame,
    },
  });
  const save = vi.spyOn(api, "calibrate").mockResolvedValue({ reprojection_error_px: 0, n_points: 6 });
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  clients.push(client);
  let clicked = false;
  // Exercise a commit-to-passive-effect ordering with the actual DOM and mutation hook.
  // The click must use coordinates from the rendered enabled button, regardless of
  // when TanStack's mutation observer receives its next effect-based options.
  const observer = new MutationObserver(() => {
    const button = document.querySelector<HTMLButtonElement>("button.ui-button-primary");
    if (button && !button.disabled && !clicked) {
      clicked = true;
      button.click();
    }
  });
  observers.push(observer);
  observer.observe(document.body, { subtree: true, childList: true, attributes: true });
  render(<QueryClientProvider client={client}><CalibratePage /></QueryClientProvider>);
  await waitFor(() => expect(save).toHaveBeenCalledTimes(1), { timeout: 3000 });
  expect(save.mock.calls[0]?.[0]).toBe("s1");
  expect(save.mock.calls[0]?.[1].near_left).toEqual(expected);
  expect(Object.keys(save.mock.calls[0]?.[1] ?? {})).toHaveLength(6);
  expect(save.mock.calls[0]?.[2]).toBe(0);
});
