import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, cleanup, render, renderHook } from "@testing-library/react";
import type { PropsWithChildren } from "react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { useMeasuredMovement } from "@/features/analytics/useInsights";
import { useAnalytics } from "@/features/session/tabs/StatsTab";
import { useSession } from "@/stores/session";
import { SESSION } from "@/test/fixtures";
import { api } from "./api";
import type { Analytics, Heatmap } from "./types";

const original = useSession.getState();
const clients: QueryClient[] = [];
const live = { ...SESSION, status: "analysing" as const, meta: { analysis_revision: 1 } };
const counts = (rallies: number) => ({ rallies }) as Analytics;
const heatmap = {
  player: "P1",
  kind: "presence",
  cell_m: 1,
  origin_m: [0, 0],
  shape: [1, 1],
  total: 1,
  values: [[1]],
} as Heatmap;
beforeEach(() => {
  vi.useFakeTimers();
  useSession.setState({
    session: live,
    analyticsVersion: 0,
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
});
afterEach(() => {
  cleanup();
  for (const client of clients.splice(0)) client.clear();
  useSession.setState(original);
  vi.restoreAllMocks();
  vi.useRealTimers();
});
async function advance(ms = 0) {
  await act(async () => {
    await vi.advanceTimersByTimeAsync(ms);
  });
}
function show(multiple = false) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  clients.push(client);
  const wrapper = ({ children }: PropsWithChildren) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
  const useOne = () => {
    const a = useAnalytics(SESSION.session_id);
    return { a };
  };
  const useMultiple = () => {
    const a = useAnalytics(SESSION.session_id);
    return {
      a,
      b: useAnalytics(SESSION.session_id),
      movement: useMeasuredMovement(live, "P1"),
      duplicate: useMeasuredMovement(live, "P1"),
    };
  };
  return renderHook(multiple ? useMultiple : useOne, { wrapper });
}
function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((done) => {
    resolve = done;
  });
  return { promise, resolve };
}

it("coalesces bursts across duplicate observers and stops work after the last observer leaves", async () => {
  const analytics = vi.spyOn(api, "analytics").mockResolvedValue(counts(1));
  const positions = vi.spyOn(api, "heatmap").mockResolvedValue(heatmap);
  const view = show(true);
  await advance(1);
  expect(analytics).toHaveBeenCalledTimes(1);
  expect(positions).toHaveBeenCalledTimes(1);
  act(() => {
    for (let version = 1; version <= 100; version++) useSession.setState({ analyticsVersion: version });
  });
  await advance(1998);
  expect(analytics).toHaveBeenCalledTimes(1);
  await advance(2);
  expect(analytics).toHaveBeenCalledTimes(2);
  expect(positions).toHaveBeenCalledTimes(2);
  view.unmount();
  act(() => useSession.setState({ analyticsVersion: 101 }));
  await advance(10000);
  expect(analytics).toHaveBeenCalledTimes(2);
  expect(positions).toHaveBeenCalledTimes(2);
});

it("reuses a just-fetched snapshot when a nested observer mounts after the first response", async () => {
  const request = vi.spyOn(api, "analytics").mockResolvedValue(counts(1));
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  clients.push(client);
  function Observer() {
    useAnalytics(SESSION.session_id);
    return null;
  }
  const view = render(
    <QueryClientProvider client={client}>
      <Observer />
    </QueryClientProvider>,
  );
  await advance(1);
  expect(request).toHaveBeenCalledTimes(1);
  view.rerender(
    <QueryClientProvider client={client}>
      <Observer />
      <Observer />
    </QueryClientProvider>,
  );
  await advance(1);
  expect(request).toHaveBeenCalledTimes(1);
});

it("retains a dirty version arriving while a live snapshot is in flight", async () => {
  const pending = deferred<Analytics>();
  const request = vi
    .spyOn(api, "analytics")
    .mockResolvedValueOnce(counts(0))
    .mockImplementationOnce(() => pending.promise)
    .mockResolvedValue(counts(2));
  const { result } = show();
  await advance(1);
  act(() => useSession.setState({ analyticsVersion: 1 }));
  await advance(2000);
  expect(request).toHaveBeenCalledTimes(2);
  act(() => useSession.setState({ analyticsVersion: 2 }));
  await advance(10000);
  expect(request).toHaveBeenCalledTimes(2);
  await act(async () => pending.resolve(counts(1)));
  await advance(1);
  expect(request).toHaveBeenCalledTimes(3);
  await advance(1);
  expect(result.current.a.data?.rallies).toBe(2);
});

it("immediately supersedes a pre-completion request and ignores its late result", async () => {
  const pending = deferred<Analytics>();
  const request = vi
    .spyOn(api, "analytics")
    .mockResolvedValueOnce(counts(0))
    .mockImplementationOnce(() => pending.promise)
    .mockResolvedValue(counts(8));
  const { result } = show();
  await advance(1);
  act(() => useSession.setState({ analyticsVersion: 1 }));
  await advance(2000);
  expect(request).toHaveBeenCalledTimes(2);
  act(() => useSession.setState({ session: { ...live, status: "analysed" }, analyticsVersion: 2 }));
  await advance(1);
  expect(request).toHaveBeenCalledTimes(3);
  await act(async () => pending.resolve(counts(1)));
  await advance(1);
  expect(result.current.a.data?.rallies).toBe(8);
});

it("follows an inherited initial request once instead of leaving a dirty snapshot stale", async () => {
  const pending = deferred<Analytics>();
  const request = vi
    .spyOn(api, "analytics")
    .mockImplementationOnce(() => pending.promise)
    .mockResolvedValue(counts(3));
  const { result } = show();
  act(() => useSession.setState({ analyticsVersion: 1 }));
  await advance(2000);
  expect(request).toHaveBeenCalledTimes(1);
  await act(async () => pending.resolve(counts(0)));
  await advance(2001);
  expect(request).toHaveBeenCalledTimes(2);
  expect(result.current.a.data?.rallies).toBe(3);
});

it("supersedes an initial request with no cached data when processing completes", async () => {
  const pending = deferred<Analytics>();
  const request = vi
    .spyOn(api, "analytics")
    .mockImplementationOnce(() => pending.promise)
    .mockResolvedValue(counts(7));
  const { result } = show();
  expect(request).toHaveBeenCalledTimes(1);
  act(() => useSession.setState({ session: { ...live, status: "analysed" }, analyticsVersion: 1 }));
  await advance(1);
  expect(request).toHaveBeenCalledTimes(2);
  await act(async () => pending.resolve(counts(0)));
  await advance(1);
  expect(result.current.a.data?.rallies).toBe(7);
});

it("isolates a generation reset and cancels its old pending refresh timer", async () => {
  const old = deferred<Analytics>();
  const request = vi
    .spyOn(api, "analytics")
    .mockImplementationOnce(() => old.promise)
    .mockResolvedValue(counts(4));
  const { result } = show();
  act(() => useSession.setState({ analyticsVersion: 1 }));
  await advance(1000);
  act(() =>
    useSession.setState({ session: { ...live, meta: { analysis_revision: 2 } }, analyticsVersion: 2 }),
  );
  await advance(1);
  expect(request).toHaveBeenCalledTimes(2);
  await act(async () => old.resolve(counts(99)));
  await advance(5000);
  expect(request).toHaveBeenCalledTimes(2);
  expect(result.current.a.data?.rallies).toBe(4);
});

it("refreshes same-generation corrections promptly after completion", async () => {
  useSession.setState({ session: { ...live, status: "analysed" } });
  const request = vi.spyOn(api, "analytics").mockResolvedValueOnce(counts(0)).mockResolvedValue(counts(5));
  vi.spyOn(api, "heatmap").mockResolvedValue(heatmap);
  const { result } = show(true);
  await advance(1);
  act(() => useSession.setState({ analyticsVersion: 1 }));
  await advance(1);
  expect(request).toHaveBeenCalledTimes(2);
  await advance(1);
  expect(result.current.a.data?.rallies).toBe(5);
});
