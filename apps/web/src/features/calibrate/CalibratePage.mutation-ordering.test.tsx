import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, cleanup, fireEvent, render, waitFor } from "@testing-library/react";
import type { PropsWithChildren } from "react";
import { afterEach, expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import { useSession } from "@/stores/session";
import { SESSION } from "@/test/fixtures";
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
  near_left: [0, 0],
  near_right: [6, 0],
  far_right: [6, 13],
  far_left: [0, 13],
  net_left: [0, 6.5],
  net_right: [6, 6.5],
};
const detected = Object.fromEntries(
  Object.entries(reference).map(([id, [x, y]]) => [id, [x * 20 + 10, y * 20 + 10]]),
) as Record<string, [number, number]>;

it("ignores edits while a proposal is loading so initialization cannot erase a user's new history", async () => {
  vi.spyOn(HTMLMediaElement.prototype, "pause").mockImplementation(() => {});
  vi.spyOn(api, "session").mockResolvedValue(SESSION);
  let resolve!: (value: Awaited<ReturnType<typeof api.calibrationProposal>>) => void;
  vi.spyOn(api, "calibrationProposal").mockImplementation(
    () =>
      new Promise((done) => {
        resolve = done;
      }),
  );
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  clients.push(client);
  const view = render(
    <QueryClientProvider client={client}>
      <CalibratePage />
    </QueryClientProvider>,
  );
  await waitFor(() => expect(api.calibrationProposal).toHaveBeenCalled());
  const svg = view.container.querySelector('svg[preserveAspectRatio="none"]');
  const box = view.container.querySelector(".cursor-crosshair");
  if (!svg || !box) throw new Error("Missing image editor");
  vi.spyOn(svg, "getBoundingClientRect").mockReturnValue({
    left: 0,
    top: 0,
    width: 1000,
    height: 500,
  } as DOMRect);
  fireEvent(box, new MouseEvent("pointerdown", { bubbles: true, clientX: 250, clientY: 200 }));
  expect(svg.querySelectorAll("circle")).toHaveLength(0);
  await act(async () =>
    resolve({
      frame: 0,
      width: 320,
      height: 240,
      reference_points: reference,
      proposal: null,
      current: null,
    }),
  );
  await waitFor(() => expect(svg).toHaveAttribute("viewBox", "0 0 320 240"));
  fireEvent(box, new MouseEvent("pointerdown", { bubbles: true, clientX: 250, clientY: 200 }));
  expect(svg.querySelector("circle")).toHaveAttribute("cx", "80");
  expect(view.getByRole("button", { name: /^Undo$/ })).toBeEnabled();
  fireEvent.click(view.getByRole("button", { name: /^Undo$/ }));
  expect(svg.querySelectorAll("circle")).toHaveLength(0);
});

it("maps calibration clicks into raw pixels and ignores presentation letterboxes", async () => {
  vi.spyOn(HTMLMediaElement.prototype, "pause").mockImplementation(() => {});
  vi.spyOn(api, "session").mockResolvedValue(SESSION);
  vi.spyOn(api, "calibrationProposal").mockResolvedValue({
    frame: 0,
    width: 320,
    height: 240,
    reference_points: reference,
    proposal: null,
    current: null,
  });
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  clients.push(client);
  const view = render(
    <QueryClientProvider client={client}>
      <CalibratePage />
    </QueryClientProvider>,
  );
  await waitFor(() => expect(view.container.querySelector('svg[viewBox="0 0 320 240"]')).not.toBeNull());
  const video = view.container.querySelector("video");
  const box = view.container.querySelector(".cursor-crosshair");
  if (!video || !box) throw new Error("Missing real calibration elements");
  Object.defineProperty(video, "videoWidth", { value: 640, configurable: true });
  Object.defineProperty(video, "videoHeight", { value: 240, configurable: true });
  vi.spyOn(box, "getBoundingClientRect").mockReturnValue({
    left: 10,
    top: 20,
    width: 1000,
    height: 750,
  } as DOMRect);
  fireEvent.loadedMetadata(video);
  const svg = view.container.querySelector('svg[viewBox="0 0 320 240"]');
  if (!svg) throw new Error("Missing calibrated image coordinate surface");
  vi.spyOn(svg, "getBoundingClientRect").mockReturnValue({
    left: 10,
    top: 207.5,
    width: 1000,
    height: 375,
  } as DOMRect);
  expect(svg).toHaveStyle({ top: "25%", height: "50%" });
  fireEvent(box, new MouseEvent("pointerdown", { bubbles: true, clientX: 810, clientY: 100 }));
  expect(svg?.querySelectorAll("circle")).toHaveLength(0);
  fireEvent(box, new MouseEvent("pointerdown", { bubbles: true, clientX: 810, clientY: 520 }));
  expect(svg?.querySelector("circle")).toHaveAttribute("cx", "256");
  expect(svg?.querySelector("circle")).toHaveAttribute("cy", "200");
});

it.each([
  { revision: 0, refFrame: 0, expected: [50, 100] },
  { revision: 77, refFrame: 0, expected: [50, 100] },
  { revision: 0, refFrame: 500, expected: [10, 10] },
])(
  "saves rendered points at first enabled commit (revision $revision, reference $refFrame)",
  async ({ revision, refFrame, expected }) => {
    useSession.setState({ session: { ...SESSION, meta: { analysis_revision: revision } } });
    vi.spyOn(HTMLMediaElement.prototype, "pause").mockImplementation(() => {});
    vi.spyOn(api, "session").mockResolvedValue(SESSION);
    vi.spyOn(api, "calibrationProposal").mockResolvedValue({
      frame: 0,
      width: 1280,
      height: 720,
      reference_points: reference,
      proposal: { method: "court_lines_v1", score: 0.9, points: detected },
      current: {
        H: [
          [10, 0, 50],
          [0, 10, 100],
          [0, 0, 1],
        ],
        reprojection_error_px: 0,
        n_points: 6,
        source: "human",
        mode: "camera",
        ref_frame: refFrame,
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
    render(
      <QueryClientProvider client={client}>
        <CalibratePage />
      </QueryClientProvider>,
    );
    await waitFor(() => expect(save).toHaveBeenCalledTimes(1), { timeout: 3000 });
    expect(save.mock.calls[0]?.[0]).toBe("s1");
    expect(save.mock.calls[0]?.[1].near_left).toEqual(expected);
    expect(Object.keys(save.mock.calls[0]?.[1] ?? {})).toHaveLength(6);
    expect(save.mock.calls[0]?.[2]).toBe(0);
  },
);
