import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { AskTab } from "@/features/session/tabs/AskTab";
import { useAnalytics } from "@/features/session/tabs/StatsTab";
import { api } from "@/lib/api";
import type { Analytics, AskAnswer } from "@/lib/types";
import { useSession } from "@/stores/session";
import { SESSION } from "@/test/fixtures";
import { analysisQueryKey } from "./analysisQuery";

afterEach(() => {
  vi.restoreAllMocks();
  useSession.setState({ session: null, analyticsVersion: 0 });
});

it("clears prior AI answers and rejects a delayed answer when reanalysis replaces the evidence", async () => {
  const pending = deferred<AskAnswer>();
  const answer: AskAnswer = {
    text: "Old rally totals",
    citations: [],
    grounded: false,
    issues: [],
    provider: "test",
    model: "test",
  };
  vi.spyOn(api, "askProvider").mockResolvedValue({ available: true, provider: "test", model: "test" });
  const ask = vi
    .spyOn(api, "ask")
    .mockResolvedValueOnce(answer)
    .mockImplementationOnce(() => pending.promise);
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const oldSession = { ...SESSION, meta: { analysis_revision: 1 } };
  const view = render(
    <QueryClientProvider client={client}>
      <AskTab session={oldSession} />
    </QueryClientProvider>,
  );
  fireEvent.change(screen.getByLabelText("Question"), { target: { value: "Count rallies" } });
  fireEvent.click(screen.getByRole("button", { name: "Ask" }));
  expect(await screen.findByText("Old rally totals")).toBeVisible();
  fireEvent.change(screen.getByLabelText("Question"), { target: { value: "Explain those rallies" } });
  fireEvent.click(screen.getByRole("button", { name: "Ask" }));
  await waitFor(() => expect(ask).toHaveBeenCalledTimes(2));

  view.rerender(
    <QueryClientProvider client={client}>
      <AskTab session={{ ...oldSession, meta: { analysis_revision: 2 } }} />
    </QueryClientProvider>,
  );
  expect(screen.queryByText("Old rally totals")).not.toBeInTheDocument();
  await act(async () => pending.resolve({ ...answer, text: "Delayed old rally explanation" }));
  expect(screen.queryByText("Delayed old rally explanation")).not.toBeInTheDocument();
  expect(screen.getByText("Ask about this match")).toBeVisible();
  view.unmount();
  client.clear();
});

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((done) => {
    resolve = done;
  });
  return { promise, resolve };
}

function Counts() {
  const result = useAnalytics(SESSION.session_id);
  return <p>{result.data ? `Rallies: ${result.data.rallies}` : "Waiting for current analysis"}</p>;
}

it("hides old cached counts and isolates a late old-generation response after reanalysis", async () => {
  const oldRequest = deferred<Analytics>();
  const newRequest = deferred<Analytics>();
  const request = vi
    .spyOn(api, "analytics")
    .mockImplementationOnce(() => oldRequest.promise)
    .mockImplementationOnce(() => newRequest.promise)
    .mockResolvedValue({ rallies: 2 } as Analytics);
  useSession.setState({ session: { ...SESSION, meta: { analysis_revision: 1 } }, analyticsVersion: 0 });
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  client.setQueryData(analysisQueryKey("analytics", SESSION.session_id, 1), { rallies: 77 });
  const view = render(
    <QueryClientProvider client={client}>
      <Counts />
    </QueryClientProvider>,
  );
  expect(screen.getByText("Rallies: 77")).toBeVisible();
  await waitFor(() => expect(request).toHaveBeenCalledTimes(1));

  act(() => useSession.setState({ session: { ...SESSION, meta: { analysis_revision: 2 } } }));
  await waitFor(() => expect(request).toHaveBeenCalledTimes(2));
  expect(screen.getByText("Waiting for current analysis")).toBeVisible();
  expect(screen.queryByText("Rallies: 77")).not.toBeInTheDocument();

  await act(async () => oldRequest.resolve({ rallies: 99 } as Analytics));
  await waitFor(() =>
    expect(client.getQueryData(analysisQueryKey("analytics", SESSION.session_id, 1))).toEqual({
      rallies: 99,
    }),
  );
  expect(screen.getByText("Waiting for current analysis")).toBeVisible();
  expect(screen.queryByText("Rallies: 99")).not.toBeInTheDocument();

  await act(async () => newRequest.resolve({ rallies: 2 } as Analytics));
  expect(await screen.findByText("Rallies: 2")).toBeVisible();
  await act(async () => client.invalidateQueries({ queryKey: ["analytics", SESSION.session_id] }));
  expect(request).toHaveBeenCalledTimes(3);
  view.unmount();
  client.clear();
});
